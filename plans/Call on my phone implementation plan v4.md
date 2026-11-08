# Call on my phone: implementation plan (v4, implementation-ready)

**Status:** Final draft for owner sign-off · 2026-11-08
**Replaces:** v3. Same simplified architecture, with the production-critical corrections applied.
**Constraints kept:**
- existing Platform/DPoP authentication;
- existing native call tracking (`FollowedCallsController`, `CallSessionTracker`,
  `CallMonitorService` `specialUse`);
- the two-tap `ACTION_DIAL` flow (MOB-040).

There is no generic device-command platform and no telephony provider.

---

## 0. Feature and boundaries

A consultant clicks **Call on my phone** on a Lead in the web CRM.
1. The chosen phone (signed in to the CRM app) shows a notification.
2. A tap opens the **phone's own dialer** with the number.
3. The consultant taps Call, and the call goes out on their SIM.

The web shows a small call card with status it can prove, and the call is logged **at most once**.

| Part | Owns |
|---|---|
| **Business Platform** | The push token on the phone's **existing native session**; push delivery as a new channel of the **existing Notification Delivery Service** (D209/D211) |
| **CRM backend** | The call request: authorization, number, Do Not Call, state, expiry, Activity link. **The only state machine** |
| **CRM app** | Notification handling, single-use open, dialer launch through the existing call flow, event reporting |
| **CRM web** | Action, phone and number choice, call card, log prompt |

**Verified against code (develop, 2026-11-08):**
- Platform: `sessions/application/devices.py` (device id = the correlation id the CRM token's
  `session_id` claim carries); `notifications/` (the email delivery service:
  `X-Platform-Service-Token`, idempotency ledger, membership check, closed outcomes).
- CRM backend:
  - `kernel/idempotency.py`;
  - `telephony/application/calls.py::do_not_call_within`;
  - `activity_calls` (no external-id column today);
  - `notification/infrastructure/platform_delivery.py` (the client template).
- CRM app:
  - `call_recording_controller.dart` (`place()`, `_placing` guard, `recover()`);
  - `CallIntegration.kt` (`DIALER_UNAVAILABLE`, `canOpenDialer`);
  - `CallSessionMachine.kt` (`NOT_PLACED` after 2 min, `OTHER_CALL`, `INTERRUPTED`, `STOPPED`);
  - manifest (`POST_NOTIFICATIONS` declared).

---

## 1. Platform

### 1.1 Push token on the native session
- `PUT /api/v1/native/session/push-registration`, with a DPoP-bound native token (existing auth).
  Body:
  - `fcm_token`
  - `app_version`
  - `readiness`: `{notifications_allowed, call_channel_enabled, can_open_dialer,
    phone_state_allowed}`
- The user and session come **from the token only**.
- Storage: new table `native_push_registrations`, one row per native session.
  - Columns: `session_id` (PK, FK to `platform_sessions`, `ON DELETE CASCADE`), `token_ciphertext`,
    `token_fingerprint` (HMAC-SHA256 with a Platform key), `app_version`, `readiness` (jsonb),
    `reported_at`, `last_error`.
  - A **unique index on `token_fingerprint`**: registering the same token from another session
    deletes the old row in the same transaction.
- **Lifecycle:**
  - Revocation, logout or "end this device" makes the session not live, and the row is ignored and
    pruned.
  - FCM `UNREGISTERED` or `SENDER_ID_MISMATCH` deletes the row.
  - The app re-sends on token refresh and **on every app foreground** (readiness changes). This
    needs no background work and no change to the token rules.
- The **device list** (`GET /api/v1/session/devices` and `/native/session/devices`, already
  built) gains `push: {ready: bool, readiness, reported_at}` for native rows. `ready` means: live
  session, token present, `app_version >= minimum`, and
  `notifications_allowed && call_channel_enabled && can_open_dialer`.

### 1.2 Push delivery: the existing Notification Delivery Service gains a push channel
`POST /api/v1/notifications/push-deliveries`, copying `deliver_email` step for step.

- **Service-to-service authorization:**
  - `X-Platform-Service-Token`, compared in constant time.
  - A **new credential of its own**, `PLATFORM_PUSH_SERVICE_TOKEN` (CRM side
    `CRM_PUSH_GATEWAY_SERVICE_TOKEN`). Settings refuse it if it equals any other Platform service
    token (the D209 rule already enforced in `config.py`).
  - A leak lets the holder send a **fixed, generic** notification to a member's own phone, and
    nothing else.
- **Body:** `{idempotency_key, organization_id, recipient_platform_user_id, target_device_id,
  purpose, reference_id, ttl_seconds}`.
  - `purpose` is a **closed set**, at first only `crm.call_request`.
  - **The Platform owns the text** for each purpose and locale ("Call request from CRM web"). A
    product cannot send free text, a name or a number.
- **Checks, in order** (same as email):
  1. The idempotency ledger, so a known key answers without sending.
  2. A per-organization rate cap → 429 + `Retry-After`. No row is written.
  3. `recipient` holds an active membership of an active `organization_id`.
  4. `target_device_id` is a live native session **of that user**, with a registration.
  5. The claim commits as `sending`.
  6. FCM HTTP v1, outside the transaction.
  7. The outcome commits.
- **FCM message:**
  - `notification` + `data{purpose, reference_id}`.
  - `android.notification.channel_id = "crm_call_requests"`, `android.priority = HIGH`.
  - `ttl = ttl_seconds`, `collapse_key = reference_id`.
- **Outcomes** (closed, mirroring email):
  - `accepted`: FCM returned a message id. This proves the provider accepted it, **not** that
    the phone received it.
  - `rejected`: reason `recipient_unknown`, `device_not_found`, `device_not_ready`,
    `token_unregistered`, `rejected_by_provider`, or `organization_suspended`.
  - `deferred`: FCM 429/5xx, with `Retry-After`.
  - `ambiguous`: the conversation broke after the request was sent.
- **One Firebase project per environment** (dev/staging/prod). Its service account lives in the
  Platform secret store.

---

## 2. CRM backend: `capabilities/phone_call/`

### 2.1 Table `phone_call_requests`

| Column | Notes |
|---|---|
| `organization_id, id` | Primary key, with row-level security |
| `member_id, lead_id, contact_point_id` | `contact_point_id` is chosen explicitly when a Lead has several numbers |
| `target_device_id` | The Platform device id. Equals the phone's token `session_id` claim |
| `state` | See 2.2. Forward-only |
| `failure_code` | Closed set, see 2.2 |
| `dispatch_attempts, next_dispatch_at` | Bounded retry |
| `expires_at` | `created_at + 120 s` |
| `opened_at, open_attempt_id` | Single-use open fence |
| `dial_started_at, ended_at, observed_seconds, tracking` | `tracking` is `followed`, `untracked` or `interrupted` |
| `activity_id` | Set when logged |
| `revision` | ETag for `If-Match` |

**Active-request boundary:** a partial unique index on `(organization_id, member_id)` where
`state IN ('requested','sent','opened','dialing')`.
- So there is **one live request per member per organization**.
- `needs_log`, `outcome_unknown` and the final states are **not** active, so a pending log never
  blocks the next call.
- The phone adds a device-wide guard (§3.4) for a person who belongs to two organizations.

### 2.2 States and transitions (only the transitions listed exist)

| From | Event | To |
|---|---|---|
| — | web create, authorized | `requested` |
| `requested` | Platform `accepted` or `ambiguous` | `sent` (`ambiguous` stores `delivery_unconfirmed = true`) |
| `requested` | Platform `rejected` | `failed` (`device_not_ready`, `device_not_found`, `token_unregistered`, `push_rejected`) |
| `requested` | retries exhausted, or `expires_at` reached while still `requested` | `failed` (`push_unavailable`) |
| `requested`/`sent` | web cancel | `cancelled` |
| `requested`/`sent` | sweep after `expires_at` | `expired` |
| `sent` | open accepted (§2.4) | `opened` |
| `sent`/`opened` | open refused at dial time (record access, Do Not Call, number changed, membership) | `refused` (`do_not_call`, `record_unavailable`, `number_changed`, `not_permitted`) |
| `opened` | phone `dialer_failed` | `failed` (`dialer_unavailable`) |
| `opened` | phone `not_placed` (tracker `NOT_PLACED`) | `not_placed` |
| `opened` | phone `started` | `dialing` |
| `opened` | phone `untracked` (tracking unavailable, or `OTHER_CALL`/`STOPPED`) | `needs_log` (`tracking = untracked`) |
| `dialing` | phone `ended` (`observed_seconds`) | `needs_log` |
| `opened` | sweep: no event for 5 min | `outcome_unknown` |
| `dialing` | sweep: no event for 4 h | `outcome_unknown` |
| `outcome_unknown` | late phone `started` / `ended` / `untracked` | `needs_log` (late events are kept, never lost) |
| `outcome_unknown` | late phone `not_placed` / `dialer_failed` | `not_placed` / `failed` |
| `opened`, `dialing`, `needs_log`, `outcome_unknown` | `logCall` with this request (§2.6) | `logged` |

Final states: `logged`, `cancelled`, `expired`, `failed`, `refused`, `not_placed`.
- Phone events for a final state are acknowledged (204) and ignored.
- `needs_log` and `outcome_unknown` stay **loggable**: a person can log a call the tracker missed.
- **No state means "answered".** `observed_seconds` is shown as "includes ringing". The outcome
  comes only from the consultant in the existing Log Call form.

### 2.3 Create and dispatch
`POST /leads/{id}/actions/call-on-my-phone {contact_point_id, device_id}`, with `Idempotency-Key`
(the existing kernel), returns 202 `{id, state, revision}`.
1. **Authorize:**
   - the tenant setting is on;
   - the member holds `call.log`;
   - the Lead is visible;
   - the contact point belongs to the Lead and is a phone;
   - `do_not_call_within` (the existing telephony policy) passes;
   - no active request exists, else 409 `call_already_active` with the active id.
2. In one unit of work, insert `requested`, enqueue a D388 intent and emit a stream hint.
3. **The DBOS workflow `phone_call.dispatch`** calls the Platform with
   `idempotency_key = "pcr:{id}"`. The key is the same on every attempt, so the Platform ledger
   stops a second push.
   - `accepted`/`ambiguous` → `sent`.
   - `rejected` → `failed(reason)`.
   - `deferred` or unreachable → retry at **1 s, 3 s, 8 s**, at most 4 attempts, never after
     `expires_at`, then `failed(push_unavailable)`.
   - A `401` from the Platform is logged as a deployment fault and ends as `push_unavailable`.
   - Every attempt is a guarded update `WHERE state='requested'`, so a cancel that wins the race
     stops further sends.
4. The web knows only what this proves:

   | State | Card text |
   |---|---|
   | `requested` | "Sending to *Pixel 8*…" |
   | `sent` | "Sent to *Pixel 8*. Tap the notification on your phone" (with `delivery_unconfirmed`: "Sending to your phone may not have completed") |
   | `sent` + 30 s | "Your phone hasn't responded yet" (a warning, still cancellable) |
   | `failed(device_not_ready)` | "This phone isn't ready: notifications are off (last reported 10:42)" |

### 2.4 Single-use, retry-safe open (phone)
`POST /phone-call-requests/{id}/actions/open {attempt_id}`, with `Idempotency-Key = attempt_id`.
The phone creates `attempt_id` and **saves it before sending** (§3.4).

In one transaction, with `SELECT … FOR UPDATE`:
1. Check the caller's organization and token `session_id` equal the request's organization and
   `target_device_id`. Otherwise 404, as if hidden.
2. **Re-authorize at dial time:** membership, `call.log`, Lead visibility, the contact point is
   unchanged and still a phone, `do_not_call_within` passes, and the tenant setting is on. A
   failure → `refused(code)`, 409 with that code.
3. If `state = sent` and `now < expires_at`: set `opened`, `open_attempt_id`, `opened_at`, and
   return `{number, lead_label, revision}`.
4. **A lost-response retry:** if `state = opened`, `open_attempt_id = attempt_id`,
   `now < opened_at + 60 s` and no phone event has arrived, return the **same** answer again,
   after re-running step 2. This domain-level replay covers the kernel's
   `idempotency_replay_unavailable` case, where the work committed but the response was lost.
5. Anything else returns 409 `call_request_not_open`, with the current state:
   - another attempt id;
   - an expired request;
   - a cancelled request;
   - a retry after 60 s or after an event.

   The phone **does not dial**.

The number is returned **only** here, and only to the targeted phone. The phone never stores it
past the dialer launch.

### 2.5 Phone events
`POST /phone-call-requests/{id}/events`:
- Body: `{event_id, kind, occurred_at, observed_seconds?, tracking?}`, where `kind` is one of
  `started`, `ended`, `not_placed`, `dialer_failed` or `untracked`.
- Authorization: the same session and organization check as open.
- `event_id` is unique per request, so a re-sent event is acknowledged without effect.
- Only transitions in §2.2 apply. Anything else is acknowledged as 204 and ignored. That is what
  makes late, duplicate and out-of-order events safe.
- `If-Match` is **not** required: events are commutative facts, and a 412 loop would lose them on
  a flaky network.

### 2.6 Logging exactly once (concurrency-safe)
- **Schema:**
  - `activity_calls` gains `phone_call_request_id uuid NULL`.
  - `UNIQUE (organization_id, phone_call_request_id)` (NULLs are not compared).
  - A foreign key to `phone_call_requests`.
  - `phone_call_requests.activity_id` gains `UNIQUE (organization_id, activity_id)`.
- **`logCall` with `phone_call_request_id`:** one unit of work.
  1. `SELECT … FOR UPDATE` the request.
  2. Require the same member, and the state to be loggable (`opened`, `dialing`, `needs_log` or
     `outcome_unknown`).
  3. Insert the Activity and its `activity_calls` row.
  4. Set the request to `logged` with its `activity_id`.
- A concurrent second submission waits on the row lock, then finds `logged`. It gets 409
  `call_already_logged` with `activity_id`, and the client opens that Activity.
- The unique index is the backstop if the lock is ever bypassed: a unique violation maps to the
  same 409, and the transaction, including the second Activity, rolls back.
- The client's own retry with the same `Idempotency-Key` replays as today.
- `CallCreate` gains an optional `phone_call_request_id`, added to the contract and `schema.sql` in
  the same merge request. `started_at` and `ended_at` are pre-filled from the request; the
  outcome is always chosen by the person.

### 2.7 Other endpoints, sweep and hints
- `GET /phone-call-requests/{id}` (requester or target phone) and `GET /me/phone-call-requests/active`
  (card recovery).
- `POST /phone-call-requests/{id}/actions/cancel`, with `If-Match`. It applies only in `requested`
  or `sent`, and otherwise returns 409 `call_request_not_cancellable`. It never claims to hang up
  a call.
- **Sweep** (a DBOS periodic job, every 15 s):
  - `requested`/`sent` past `expires_at` → `expired`;
  - `opened` with no event for 5 min → `outcome_unknown`;
  - `dialing` with no event for 4 h → `outcome_unknown`.
- **Live web updates:** each state change commits a hint of a new kind `phone_call` on the
  **existing** notifications stream (`kernel/listen.py`, the D390 precedent). It carries no
  content; the web refetches.
- **Audit:** `crm.phone_call.requested`, `.opened`, `.ended` and `.logged` record the member,
  record, device id and outcome codes, **never the number**.

### 2.8 Copy number (Do Not Call safe)
- The request read model includes `copy_allowed`, computed by the server from the request's
  **current** state:
  - **true only if** the member can still see the contact point **and** `do_not_call_within`
    passes now;
  - always **false** for `refused(do_not_call)`, `refused(record_unavailable)` and
    `refused(not_permitted)`.
- **Copy** is offered on `failed`, `expired`, `cancelled` and `not_placed`, and only when
  `copy_allowed`. The number copied is the one the member already sees on the Lead. Copy never
  bypasses Do Not Call.

### 2.9 Tenant switch and permission
- A tenant setting "Allow calling from web through members' phones": **off by default**, with an
  admin disclosure that customers see the consultant's own SIM number.
- Permission: the existing `call.log`.

---

## 3. CRM app (Android)

### 3.1 Readiness and permissions (foreground only)
- A one-time **"Receive calls from web"** setup screen in Settings, also prompted the first time a
  request arrives:
  - On Android 13+, request `POST_NOTIFICATIONS` (already declared) with a rationale, through
    the existing permission plumbing in `CallRecordingIntegration`.
  - Create the notification channel `crm_call_requests` at **app start**, before any push can
    arrive, with high importance and lock-screen visibility `PRIVATE`.
  - Check `READ_PHONE_STATE` as the existing tracker already does. If it's denied, calls still
    work but are `untracked`.
- **Readiness is computed and sent with the registration** on sign-in, token refresh and every
  foreground:
  - `areNotificationsEnabled()`;
  - the channel's importance is not `NONE`;
  - `canOpenDialer` (the existing `getCapabilities`);
  - `READ_PHONE_STATE` granted.

  The web shows readiness as "last reported", never as live.

### 3.2 FCM handling: all three app states
`firebase_messaging` is added. No `flutter_local_notifications` and no background Dart code.

| App state | What happens | Code path |
|---|---|---|
| **Background** (process alive) | The system shows the notification (message type `notification`). A tap brings the app forward | `FirebaseMessaging.onMessageOpenedApp` |
| **Terminated** (swiped away, not force-stopped) | The system shows the notification. A tap cold-starts the app | `FirebaseMessaging.instance.getInitialMessage()`, read once at start-up |
| **Foreground** | FCM does **not** display it. `onMessage` fires, and the app shows an in-app **call request sheet** (lead label fetched on open) with **Open dialer** / **Dismiss** | `FirebaseMessaging.onMessage` |
| **Force-stopped** | Android drops it. The web shows "hasn't responded yet", then `expired` | — |

- **Cold start ordering:** the request id from `getInitialMessage()` is held in memory until the
  session is restored and the active organization is known. Only then is open called.
  - If the phone is signed out, show "Sign in to continue". The request expires on the server.
  - The organization check is on the server: open for a request from another organization
    returns 404, and the app says "This request is for another organization".
- **Dismiss / swipe:** nothing is sent. The request expires on the server. No background code.

### 3.3 Dial path (two taps, the existing flow)
1. Tap the notification, or **Open dialer** on the sheet. This is tap 1.
2. Run open (§2.4) with a saved `attempt_id`. If it's refused, show the server's reason and stop.
3. Call the **existing** `FollowedCallsController.place(phoneNumber: number, lead: …)`. That arms
   `CallSessionTracker`, starts `CallMonitorService` (`specialUse`, **unchanged**) and opens the
   dialer with `ACTION_DIAL`.
4. The user taps Call in the dialer. This is tap 2.
5. Map the existing native outcomes to phone events:

| Native outcome | Event sent |
|---|---|
| `openDialer` → `DIALER_UNAVAILABLE` (place returns false) | `dialer_failed` |
| `place()` returns `notFollowed` (no `READ_PHONE_STATE`) but the dialer opened | `untracked` |
| Tracker `started` | `started` |
| Tracker `ended(durationSeconds)` | `ended`, `observed_seconds` |
| Tracker cancelled `NOT_PLACED` (2 min arm timeout) | `not_placed` |
| Tracker cancelled `OTHER_CALL` / `STOPPED` | `untracked` |
| Tracker cancelled `INTERRUPTED` | nothing yet. The existing `recover()` resolves it to `ended` or `untracked` |

6. After `ended` or `untracked`, the existing Log Call sheet opens pre-filled, with
   `phone_call_request_id`.

### 3.4 No duplicate dialer launches
A small file-backed store `web_call_requests.json` lives in the partition folder, alongside the
existing `call_sessions.json`. It holds one entry per request id:

`{attempt_id, phase: opening | dialer_launched | done, pending_events[]}`

- **Before calling open:** if an entry exists in `dialer_launched` or `done`, **do not open or
  dial again**. Show "You already opened the dialer for this call".
- If the entry is in `opening`, reuse its `attempt_id`, so a retry after a lost response replays
  (§2.4). This covers a double tap, a duplicate push, a tap on the sheet plus the notification,
  and a process restart.
- **The phase moves to `dialer_launched` before `place()` is called.** If the app dies between
  the two steps, the dialer is not opened again. The request then reaches `outcome_unknown` and
  can still be logged by hand. Under-dialing is preferred to double-dialing.
- **Device-wide guard:** while any entry is `opening` or `dialer_launched`, or the existing
  tracker has an active session, a new request shows "Finish your current call first" and is not
  opened.
- **Clean-up:** entries are pruned 24 h after `done`. Sign-out deletes the partition, as today.

### 3.5 Event delivery and eventual reconciliation
- Events are added to `pending_events` (with `event_id`) **before** they are sent. They are
  removed on 2xx or on a 4xx that is final.
- Sending is retried on the existing **foreground, session and network triggers** of
  `sync_executor`. There is no background work and no change to the token rules.
- On every foreground, the existing `recover()` runs first, so killed-process sessions resolve to
  `ended` or `untracked`, then pending events are flushed.
- The server accepts late events from `outcome_unknown` (§2.2), so a phone that comes back hours
  later still completes the record.
- Recording stays withheld (MOB-112). **No new permissions** beyond `POST_NOTIFICATIONS` (already
  declared) and the FCM service.

---

## 4. CRM web

1. **Action:** "Call on my phone" in the Lead's Contact menu and quick actions, loaded lazily (the
   lead route is near its 140 KB budget).
   - The **number** is chosen when the Lead has several (the existing contact resolver).
   - The **phone** list comes from the existing device list, now with `push.ready`.
     - One ready phone is used directly.
     - Several ready phones → a picker, defaulting to the last one used in this browser (local
       storage).
     - Not-ready phones are shown disabled, with the readiness reason and "last reported".
   - The action is greyed out with a reason when there's no ready phone, no number, Do Not Call,
     the feature is off, or the member lacks `call.log`.
2. **Call card:** in the CRM shell, minimizable, and kept across navigation.
   - Draggable, with arrow-key moves (WCAG 2.5.7) and `aria-live` status, reusing the sticky-notes
     code.
   - After a refresh it is restored from `GET /me/phone-call-requests/active`, and from the
     last request id in session storage for a final state.
   - It shows the texts in §2.3, plus:
     - `dialing`: "Call in progress on your phone · 00:42 (includes ringing)";
     - `needs_log`: "Call finished. Log the outcome";
     - `outcome_unknown`: "We didn't hear back from your phone. Log the call if you made it";
     - `refused` / `not_placed` / `failed` / `expired` / `cancelled`, each in its own words.
   - Actions: **Cancel** (only in `requested`/`sent`), **Copy number** (only when
     `copy_allowed`), **Log outcome** (loggable states), **Close**.
3. **Live status:** the `phone_call` stream hint triggers a refetch. Polling every 2 s is the
   fallback while the request is active. Status is never copied into a client store.
4. **Multi-tab:**
   - Every tab shows the card.
   - **Only the tab that started the request** (marked with the request id in session storage)
     opens the log form automatically. Other tabs show a **Log outcome** button.
   - A 409 `call_already_logged` opens the existing Activity.
5. English and Arabic strings, in their own lazily loaded catalogue. Logical CSS only.

---

## 5. Delivery (one merge request per repo, in order)

| # | Repo | Merge request | Gate (automated unless noted) |
|---|---|---|---|
| 0 | — | Owner decisions (§7); CRM D-number + MOB entry + Platform ADR; Firebase project per environment | Signed off |
| 1 | Platform | Push registration on the native session + readiness in the device list + the `push-deliveries` channel with its own service token | Token moves between sessions; cascade on session end; cross-user, cross-organization and not-ready targets rejected; ledger replay sends once; constant-time token check; 429 writes nothing |
| 2 | crm-backend | `phone_call` package + `phone_call_request_id` on `logCall` + sweep + hint + tenant setting | Every transition in §2.2; concurrent `logCall` gives one Activity (a two-connection test); open replay, wrong attempt, expiry and wrong session; Do Not Call and access re-checked at open; bounded retry and cancel race; late events from `outcome_unknown` |
| 3 | crm-app | FCM in three states, readiness, the `web_call_requests` store, the event outbox | Unit tests for the store and mapping; the **real-device checklist** (§6) |
| 4 | crm-frontend | Action, pickers, call card, log prompt | Multi-tab, refresh recovery, keyboard-only use, Arabic layout, bundle budgets |

Merge requests 3 and 4 can start once #2's contract is merged. Rollout:
- The tenant switch stays off until the new app version is live.
- Old app versions never register a token, so they are never eligible.
- Turning the switch off hides the action. Existing calling and logging are untouched.

## 6. Real-device checklist (gate for #3)

All on a Samsung phone and a Xiaomi/HyperOS phone:
- **App states:** foreground (sheet), background, terminated (cold start), and force-stopped
  (expires).
- **Notifications:** locked then unlocked; notification permission denied, and the channel turned
  off (the web shows not ready).
- **Duplicates:** a double tap, two pushes with the same request id, and the app killed between
  open and dialer → **one dialer launch at most**.
- **Lost connection:** an open response lost (airplane mode right after the tap) → the replay works,
  with one dialer.
- **Phone failures:** no dialer app (emulator) → `dialer_failed`; the dialer closed without
  calling → `not_placed` after 2 min; `READ_PHONE_STATE` denied → `untracked`.
- **Long calls:** a call longer than 3 minutes with the app killed during it → `recover()` →
  `ended`.
- **Offline:** offline during the call, back online an hour later → the events land and the
  request reaches `needs_log`.
- **Access changes:** Do Not Call set, or Lead access removed, between push and tap → refused and
  no dial; the organization switched on the phone → refused.

## 7. Owner decisions (unchanged from v3)
1. Firebase push, one project per environment.
2. Two taps (`ACTION_DIAL`).
3. A picker when there are several ready phones; never switch phones automatically.
4. Personal SIM use only behind the tenant switch, with the disclosure.
