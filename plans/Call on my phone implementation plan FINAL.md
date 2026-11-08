# Call on my phone: final implementation plan

**Status:** Implementation-ready, pending the owner decisions in §7 · 2026-11-08
**Replaces:** v4, with every Critical/Major finding of the independent code review fixed (§8).
**Kept as before:**
- the simplified architecture;
- existing Platform/DPoP authentication, with no background token refresh;
- existing native call tracking;
- the two-tap `ACTION_DIAL` flow (MOB-040).

There is **no** generic device-command platform, **no** telephony provider and **no** extra phases.
Nothing here is implemented, merged or deployed.

---

## 0. Feature and boundaries

A consultant clicks **Call on my phone** on a Lead in the web CRM.
1. Their chosen phone (signed in to the CRM app) shows a notification.
2. A tap opens the **phone's own dialer** with the number.
3. They tap Call, and the call goes out on their SIM.

The web shows a small call card with status it can prove, and the call is logged **at most once**.

| Part | Owns |
|---|---|
| **Business Platform** | The push token on the phone's **existing native session**; push as a new channel of the **existing Notification Delivery Service** (D209/D211) |
| **CRM backend** | The call request: authorization, number, Do Not Call, state, expiry, Activity link. **The only state machine** |
| **CRM app** | Notification handling, single-use open, dialer launch through the existing call flow, event reporting |
| **CRM web** | Action, phone and number choice, call card, log prompt |

**Checked against `develop` (2026-11-08):**
- **Platform:**
  - `sessions/application/devices.py`;
  - `sessions/infrastructure/broker.py` (the token's `session_id` = `correlation_id(session.id)`
    = the device-list id, and it stays the same across refresh);
  - `notifications/*` (email delivery: service token, ledger, closed outcomes, `deferred` →
    new attempt).
- **CRM backend:**
  - `kernel/idempotency.py`;
  - `kernel/listen.py`;
  - `durable/periodic.py` (the D208 15-minute tick only);
  - `telephony/application/calls.py::do_not_call_within`;
  - `activity/application/commands/log_call.py` (a single unit of work);
  - `platform_gateway/jwt_resolver.py` (does **not** read `session_id` yet);
  - `notification/application/delivery.py` (attempt-numbered keys).
- **CRM app:**
  - `call_recording_controller.dart` (`place()` → `bool`, its own `sessionId`, `recover()`);
  - `CallIntegration.kt`;
  - `CallSessionTracker.kt` (also emits `ringing`);
  - `CallSessionMachine.kt` (cancel reasons `NOT_PLACED` after 2 min, `OTHER_CALL`,
    `INTERRUPTED`, `STOPPED` = Dart cancel after a dialer failure);
  - `call_recording_composition.dart` (the lead call strip's Log call);
  - `sync_executor.dart`.

---

## 1. Platform

### 1.1 Push token on the native session
- `PUT /api/v1/native/session/push-registration`, with the existing DPoP-bound native token.
  - Body: `{fcm_token, app_version, readiness{notifications_allowed, call_channel_enabled,
    can_open_dialer, phone_state_allowed}}`.
  - The user and session come **from the token only**.
- New table `native_push_registrations`:
  - Columns: `session_id` (PK, FK to `platform_sessions`, `ON DELETE CASCADE`), `token_ciphertext`,
    `token_fingerprint` (HMAC-SHA256 under a Platform key), `app_version`, `readiness` (jsonb),
    `reported_at`, `last_error`.
  - A **unique index on `token_fingerprint`**: the same token registered from another session
    deletes the old row in the same transaction.
- **Lifecycle:**
  - A session that is no longer live (revoked, logged out, "end this device") is ignored when
    sending, and pruned.
  - FCM `UNREGISTERED` or `SENDER_ID_MISMATCH` deletes the row.
  - The app re-registers on sign-in, on token refresh and on **every foreground**. No background
    work.
- **The device list** (`/api/v1/session/devices`, `/native/session/devices`) gains, for native
  rows, `push: {ready, readiness, reported_at}`. `ready` means:
  - a live session with a token;
  - `app_version >= minimum`;
  - `notifications_allowed`, `call_channel_enabled` and `can_open_dialer`.

### 1.2 Push channel in the existing Notification Delivery Service
`POST /api/v1/notifications/push-deliveries`, copying `deliver_email` step for step.

- **Service-to-service authorization:**
  - `X-Platform-Service-Token`, compared in constant time.
  - A **new credential of its own**: `PLATFORM_PUSH_SERVICE_TOKEN` (CRM side
    `CRM_PUSH_GATEWAY_SERVICE_TOKEN`).
  - It is added to **every existing equal-token cross-check in both repos** (Platform `config.py`
    and CRM `config.py`, D209/D469).
  - A leak lets the holder send only a fixed, generic notification to a member's own phone.
- **Body:** `{idempotency_key, organization_id, recipient_platform_user_id, target_device_id,
  purpose, reference_id, ttl_seconds}`.
  - `purpose` is a closed set: `crm.call_request`.
  - The Platform owns the text, in the recipient's Platform profile locale. A product cannot send
    free text, a name or a number.
- **Checks, in order:**
  1. The ledger: a known key replays its answer and sends nothing.
  2. The per-organization rate cap → 429 + `Retry-After`. No row is written.
  3. An active membership in an active organization.
  4. `target_device_id` is a live native session of that user with a registration that is `ready`.
  5. The claim commits as `sending`.
  6. FCM HTTP v1, outside the transaction.
  7. The outcome commits.
- **FCM message:**
  - `notification` + `data{purpose, reference_id, organization_id}`.
  - Android `channel_id = "crm_call_requests"`, `priority = HIGH`.
  - `ttl = ttl_seconds`, `collapse_key = reference_id`.
- **Outcomes**, the same closed set as email:
  - `accepted`: FCM returned a message id. This proves the provider took it, not that the phone
    received it.
  - `rejected`: reason `recipient_unknown`, `device_not_found`, `device_not_ready`,
    `token_unregistered`, `rejected_by_provider` or `organization_suspended`.
  - `deferred`: FCM 429/5xx **before** it accepted. This **may be retried under a new key**, as
    email's are.
  - `ambiguous`: the conversation broke after sending.
  - `in_progress`: another request holds the key.
- **One Firebase project per environment** (dev/staging/prod). Its service account lives in the
  Platform secret store.

---

## 2. CRM backend: `capabilities/phone_call/`

### 2.0 Prerequisite: read the session claim
- Add `session_id` to `PlatformSession`, `jwt_resolver._session_from` and the dev resolver.
- Open and events refuse when it is absent: 401 if it was never presented, 404 if it doesn't match.
- This is part of merge request #2.

### 2.1 Table `phone_call_requests`

| Column | Notes |
|---|---|
| `organization_id, id` | Primary key, with row-level security |
| `member_id, lead_id, contact_point_id` | Explicit number choice when a Lead has several |
| `number_fingerprint` | HMAC of the dialable number at create. Detects `number_changed` at open |
| `target_device_id` | The Platform device id. Equals the phone's token `session_id` |
| `state, failure_code` | §2.2. Forward-only |
| `dispatch_attempt, ttl_seconds` | `ttl_seconds` is frozen once at create (120) |
| `expires_at` | `created_at + 120 s` |
| `opened_at, open_attempt_id` | Single-use open fence |
| `dial_started_at, ended_at, observed_seconds, tracking` | `tracking` is `followed`, `untracked` or `interrupted` |
| `activity_id` | `UNIQUE (organization_id, activity_id)` |
| `revision` | ETag |

**Active-request boundary:** a partial unique index on `(organization_id, member_id)` where
`state IN ('requested','sent','opened','dialing')`.
- One live request per member per organization.
- `needs_log`, `outcome_unknown` and the final states never block the next call.
- The requester can always free the slot (§2.7 *close*), so a dead phone can't hold it.

### 2.2 State machine (only these transitions exist)

| From | Event | To |
|---|---|---|
| — | web create, authorized | `requested` |
| `requested` | Platform `accepted` | `sent` |
| `requested` | Platform `ambiguous` | `sent` (`delivery_unconfirmed = true`) |
| `requested` | Platform `rejected` | `failed` (`device_not_ready`, `device_not_found`, `token_unregistered`, `push_rejected`) |
| `requested` | retry budget used up (§2.3) | `failed` (`push_unavailable`) |
| `requested`/`sent` | web cancel | `cancelled` |
| `sent` | `expires_at` reached (timer or backstop) | `expired` |
| `sent` | open accepted (§2.4) | `opened` |
| `sent` | open re-check fails | `refused` (`do_not_call`, `record_unavailable`, `number_changed`, `not_permitted`) |
| `opened` | phone `started` | `dialing` |
| `opened` | phone `ended` (a recovered call whose `started` was lost) | `needs_log` |
| `opened` | phone `untracked` | `needs_log` (`tracking = untracked`) |
| `opened` | phone `not_placed` | `not_placed` |
| `opened` | phone `dialer_failed` | `failed` (`dialer_unavailable`) |
| `dialing` | phone `ended` | `needs_log` |
| `dialing` | phone `untracked` (interrupted, no data) | `needs_log` (`tracking = interrupted`) |
| `opened`/`dialing` | timer: no event for 5 min / 90 min | `outcome_unknown` |
| `opened`/`dialing` | requester **close** (web) | `outcome_unknown` |
| `outcome_unknown` | late `started` / `ended` / `untracked` | `needs_log` |
| `outcome_unknown` | late `not_placed` / `dialer_failed` | `not_placed` / `failed` |
| `needs_log` | late `ended` | `needs_log` (fills in `observed_seconds` only) |
| `opened`, `dialing`, `needs_log`, `outcome_unknown` | `logCall` with this request (§2.6) | `logged` |
| `needs_log`/`outcome_unknown` | backstop: not logged for 14 days | `abandoned` |

- **Final states:** `logged`, `cancelled`, `expired`, `failed`, `refused`, `not_placed`,
  `abandoned`.
- An event that is not listed is acknowledged with 204 and has no effect, so late, duplicate and
  out-of-order events are safe.
- **No state means "answered".** `observed_seconds` is labelled "includes ringing". The outcome
  comes only from the consultant in the Log Call form.

### 2.3 Create and dispatch
`POST /leads/{id}/actions/call-on-my-phone {contact_point_id, device_id}` with `Idempotency-Key`
(the existing kernel; this is a create) → 202 `{id, state, revision}`.
1. **Authorize:**
   - the tenant setting is on;
   - the member holds `call.log`;
   - the Lead is visible;
   - the contact point belongs to the Lead and is a phone;
   - the **Do Not Call check** (§2.8) passes;
   - no active request exists, else 409 `call_already_active` with the active id.
2. **One unit of work:**
   - insert `requested` with `number_fingerprint`;
   - enqueue a D388 intent that starts the durable workflow `phone_call.lifecycle:{id}`;
   - emit a member-scoped stream hint.
3. **Dispatch inside the workflow:**
   - Key: `idempotency_key = "pcr:{id}:{dispatch_attempt}"`, the email client's attempt pattern.
   - **Move to the next attempt only after a definite `deferred` or a 429.** Platform unreachable,
     5xx or `in_progress` → retry **the same key**, so the ledger answers instead of sending again.
   - Back-off 1 s, 3 s, 8 s, up to **4 attempts in total**, and never after `expires_at`. Then
     `failed(push_unavailable)`.
   - A `401` from the Platform is logged as a deployment fault.
   - `ttl_seconds` and the body are frozen, so a retry never gets a content-mismatch 409.
   - Each result is a guarded update `WHERE state='requested'`, so a cancel that wins the race
     stops further sends.
4. **Timers, in the same workflow** (D388 §5 delayed-workflow precedent, not a scheduler):
   - sleep until `expires_at` → a guarded `sent → expired`;
   - after `opened`, sleep 5 min → a guarded `opened → outcome_unknown`;
   - after `dialing`, sleep 90 min → a guarded `dialing → outcome_unknown`.
5. **Backstop:** a D208 periodic organization job (the existing 15-minute tick) applies the same
   guarded transitions to any row whose workflow died, plus `abandoned` after 14 days.
   **Reads also report a `sent` request past `expires_at` as `expired`**, so the card never waits
   on a sweep.

### 2.4 Single-use, retry-safe open (phone)
`POST /phone-call-requests/{id}/actions/open {attempt_id}`. **There is no kernel
`Idempotency-Key` on this route.** `attempt_id` is the fence, which is the only way a lost
response can be replayed: the kernel would answer `idempotency_replay_unavailable` before the
domain code runs. This is recorded as a CRM-API-001 §6.1 matrix row (§2.9).

In one transaction, `SELECT … FOR UPDATE`:
1. Check the token's organization and `session_id` equal the request's organization and
   `target_device_id`. Otherwise 404, as if hidden.
2. **Re-authorize at dial time:**
   - membership, `call.log` and the tenant setting;
   - Lead visibility;
   - the contact point is unchanged (`number_fingerprint` matches);
   - the Do Not Call check (§2.8) passes.

   A failure from `sent` → `refused(code)`, and the code is returned (409).
3. If `state = sent` and `now < expires_at`: set `opened`, `open_attempt_id` and `opened_at`, and
   return `{number, lead_label, organization_id, revision}`.
4. **A lost-response retry:** if `state = opened`, `open_attempt_id = attempt_id`,
   `now < opened_at + 60 s` and no phone event has arrived, re-run step 2 and return the
   **same** answer.
5. Otherwise 409 `call_request_not_open` with the current state:
   - another attempt id;
   - an expired request;
   - a cancelled request;
   - a refused request;
   - a retry after 60 s or after an event.

   The phone **does not dial**.

The number is returned only here, only to the targeted phone, and is not kept after the dialer
launch.

### 2.5 Phone events
`POST /phone-call-requests/{id}/events {event_id, kind, occurred_at, observed_seconds?, tracking?}`
- `kind` is one of `started`, `ended`, `not_placed`, `dialer_failed` or `untracked`.
- The same session and organization check as open.
- `event_id` is unique per request. A repeat is acknowledged with no effect.
- No `If-Match`, because events are facts (§2.9).

### 2.6 Logging exactly once (concurrency-safe)
- **Schema:**
  - `activity_calls.phone_call_request_id uuid NULL`;
  - `UNIQUE (organization_id, phone_call_request_id)`;
  - a composite FK `(organization_id, phone_call_request_id)` to `phone_call_requests`;
  - `phone_call_requests.activity_id` is unique;
  - `ON DELETE SET NULL` from the Activity, with the request going back to `needs_log` through
    the same command if an Activity is ever removed.
- **`logCall` with `phone_call_request_id`:** inside the existing single unit of work of
  `log_call.py`.
  1. `SELECT … FOR UPDATE` the request.
  2. Require the **same member**, a loggable state (`opened`, `dialing`, `needs_log`,
     `outcome_unknown`), and that the Activity's contexts **include `request.lead_id`**.
  3. Insert the Activity.
  4. Set `logged` and `activity_id`.
- **A concurrent second submission** waits on the lock, then finds `logged` → 409
  `call_already_logged` with `activity_id`. The client opens it.
- **The unique index is the backstop:** a violation maps to the same 409 and rolls back the
  second Activity.
- **A client's own retry** with the same `Idempotency-Key` replays as today.
- **On the phone, every Log call path carries the request id** (§3.3), including the existing lead
  call strip, so a phone-side log can never be a second, unlinked Activity.
- `CallCreate` gains an optional `phone_call_request_id`. The contract and `schema.sql` change in
  the same merge request.

### 2.7 Other endpoints, hints and audit
- **Reads:**
  - `GET /phone-call-requests/{id}`, for the requester or the target phone;
  - `GET /me/phone-call-requests/active`, for card recovery.
- **`POST …/actions/cancel`** (`If-Match`, `Idempotency-Key`): only in `requested`/`sent`.
  Otherwise 409 `call_request_not_cancellable`. It never claims to hang up a call.
- **`POST …/actions/close`** (`If-Match`, `Idempotency-Key`): the requester moves `opened`/`dialing`
  → `outcome_unknown` ("I'm done; my phone didn't report"). This frees the active slot. Late phone
  events still land.
- **Live web updates:** each state change commits a **member-scoped** hint, using the D334 payload
  pattern `<org>:<member>:phone_call` in `kernel/listen.py`, so only that member's streams wake.
  The web refetches.
- **Audit:** `crm.phone_call.requested`, `.opened`, `.ended` and `.logged` record the member,
  record, device id and codes, **never the number**.

### 2.8 Do Not Call, and a safe Copy number
- **One check, used at create, at open and for Copy.** It reuses the consent and suppression
  lookup behind `do_not_call_within`, against the contact point's **E.164 form when one exists**:
  - `opted_out` / `suppressed` → `do_not_call` (blocks);
  - `address_not_e164` does **not** mean Do Not Call for a SIM call. It is handled by owner
    decision 5 (§7). The default blocks with a distinct code, `number_not_international`, never
    labelled "Do Not Call".
- **`copy_allowed`**, from the current state, in the request read model: true only if the member
  can still see the contact point and the check passes **now**.
  - It is always false for `refused(do_not_call|record_unavailable|not_permitted)`.
  - **Copy** is offered only on `failed`, `expired`, `cancelled`, `not_placed` and `abandoned`.
  - It copies the number the member already sees on the Lead.

### 2.9 Contract rules (CRM-API-001 §6.1 matrix, with a D-number)

| Operation | Idempotency-Key | If-Match | Why |
|---|---|---|---|
| call-on-my-phone (create) | required | — | Standard create |
| cancel, close (lifecycle) | required | required | Standard lifecycle |
| **open** | **not used** | **not used** | `attempt_id` fence; kernel replay cannot cover a lost response |
| **events** | **not used** | **not used** | `event_id` dedup; facts must not be lost to 412 loops |

### 2.10 Tenant switch and permission
- The tenant setting "Allow calling from web through members' phones" is **off by default**, with a
  disclosure that customers see the consultant's own SIM number.
- Permission: the existing `call.log`.

---

## 3. CRM app (Android)

### 3.1 Readiness and permissions (foreground only)
- **Channel:** `crm_call_requests` is created **in Kotlin at app start**, with high importance and
  lock-screen visibility `PRIVATE`. There is no `flutter_local_notifications`.
- **"Receive calls from web" setup** in Settings, also shown when a request first arrives:
  - On Android 13+, request `POST_NOTIFICATIONS` (already declared) through the existing
    permission plumbing.
  - `READ_PHONE_STATE` is checked as the tracker already does. If it's denied, calls work but are
    `untracked`.
- **Readiness is sent with the registration** on sign-in, token refresh and every foreground:
  - `areNotificationsEnabled()`;
  - the channel importance is not `NONE`;
  - the existing `canOpenDialer`;
  - `READ_PHONE_STATE`.

  The web shows it as "last reported".

### 3.2 FCM handling (`firebase_messaging`, no background Dart code)

| App state | Behaviour | Path |
|---|---|---|
| Background | The system shows the notification; a tap brings the app forward | `onMessageOpenedApp` |
| Terminated (not force-stopped) | The system shows it; a tap cold-starts | `getInitialMessage()`, read once |
| Foreground | Nothing is shown by the system → an in-app **call request sheet** with **Open dialer** / **Dismiss** | `onMessage` |
| Force-stopped | Dropped by Android → the web shows "hasn't responded yet", then `expired` | — |

- **Cold start:**
  - Hold `{reference_id, organization_id}` until the session is restored.
  - If the active organization differs, offer **Switch to *Org B* and continue** while the request
    is still valid.
  - If signed out, show "Sign in to continue".
- **A tray notification left over** after expiry or cancel can't be removed without background
  code. A tap shows "This call request has ended" and never dials.
- **Dismiss / swipe:** nothing is sent. The server expires the request.

### 3.3 Dial path: two taps, the existing flow
1. **Tap 1:** the notification, or **Open dialer** on the sheet.
2. Under the per-request mutex (§3.4): call open (§2.4). If it's refused, show the reason and stop.
3. **A small, additive change to `FollowedCallsController.place()`:**
   - It accepts an optional caller-supplied `sessionId` and **a `phoneCallRequestId`**, stored on
     the `FollowedCall` binding.
   - The tracking behaviour is otherwise unchanged.
   - The phone creates `sessionId`, **saves it in the `web_call_requests` entry**, then calls
     `place(contextKind: 'lead', contextId: leadId, phoneNumber, sessionId, phoneCallRequestId,
     openDialer)`.
   - That arms `CallSessionTracker`, starts `CallMonitorService` (`specialUse`, **unchanged**) and
     opens `ACTION_DIAL`.
4. **Tap 2:** Call, in the dialer.
5. **Native outcome → event**, keyed by the saved `sessionId`:

| Native outcome | Event |
|---|---|
| `place()` returns false (`DIALER_UNAVAILABLE`) | `dialer_failed` |
| `place()` true, and `state[sessionId].phase == notFollowed` (no `READ_PHONE_STATE`) | `untracked` |
| tracker `started` | `started` |
| tracker `ringing` (call waiting only) | **ignored** |
| tracker `ended(durationSeconds)` | `ended`, `observed_seconds` |
| tracker cancelled `NOT_PLACED` (2 min arm timeout) | `not_placed` |
| tracker cancelled `OTHER_CALL` | `untracked` |
| tracker cancelled `STOPPED` | **nothing**. It only follows Dart's own cancel after a dialer failure, which already sent `dialer_failed` |
| tracker cancelled `INTERRUPTED` | nothing yet. `recover()` decides |
| `recover()` → ended, with `startedAt` | `ended` (with `observed_seconds` if known) |
| `recover()` → ended, `interrupted` with no `startedAt` | `untracked` |
| binding dropped by `recover()` (no native record) | `untracked` |

6. **Every Log call entry point passes `phoneCallRequestId`** to `showLogCallSheet`. That covers
   the post-call sheet, the lead **call strip** (`call_recording_composition.dart`) and cold-start
   restore. Logging a request already logged from the web returns 409 `call_already_logged`, and
   the app opens that Activity.

### 3.4 No duplicate dialer launches
A file-backed store `web_call_requests.json` lives in the partition folder, next to
`call_sessions.json`. One entry per request id:

`{attempt_id, session_id, phase: opening | dialer_launched | done, created_at, pending_events[]}`

- **An in-process mutex per request id** wraps *read entry → open → CAS phase*. A notification tap,
  a sheet tap and a duplicate push are therefore serialized.
- **Phase rules:**
  - `dialer_launched` or `done` → never open or dial again. Show "You already opened the dialer
    for this call".
  - `opening` → reuse `attempt_id`, so a lost response replays (§2.4).
- **Compare-and-set `opening → dialer_launched`** (written to disk) **before** `place()` runs, and
  `place()` runs only if the CAS succeeded.
  - If the app dies between the CAS and `place()`, it does not dial again. The request then
    reaches `outcome_unknown` and can be logged by hand. Under-dialing is preferred to
    double-dialing.
- **Guard:** while an entry is `opening`/`dialer_launched`, or the native tracker has an active
  session (the only truly device-wide signal), a new request shows "Finish your current call
  first".
- **Stuck-entry recovery,** on every foreground after `recover()`:
  - an entry with no live tracker session for its `session_id`, older than the 2-minute arm
    window, is marked `done` once its pending events are queued;
  - an `opening` entry older than 2 minutes is marked `done` (the server will have expired it);
  - entries are pruned 24 h after `done`;
  - sign-out deletes the partition, as today.

### 3.5 Event delivery and eventual reconciliation
- **Events are a new `SyncHandler` kind on the existing `SyncQueue`.** It brings the existing
  retry and halt behaviour and the foreground, session and network triggers. No separate outbox
  and no background work.
  - Each event is queued with its `event_id` **before** the send.
  - A 2xx or a final 4xx removes it.
- **On every foreground:**
  1. `recover()` runs.
  2. The §3.3 mapping queues any recovered outcome.
  3. The queue flushes.
- **Late events are accepted** from `outcome_unknown` and `needs_log` (§2.2), so a phone that
  comes back hours later still completes the record.
- **Permissions:** recording stays withheld (MOB-112). No new permissions beyond
  `POST_NOTIFICATIONS` (already declared) and the FCM service.

---

## 4. CRM web
1. **Action:** "Call on my phone" in the Lead's Contact menu and quick actions, loaded lazily (the
   lead route is near its 140 KB budget).
   - **Number picker** when the Lead has several numbers.
   - **Phone list** from the existing device list with `push.ready`:
     - one ready phone is used directly;
     - several → a picker, defaulting to the last used in this browser;
     - not-ready phones are disabled, with their reason and "last reported".
   - The action is greyed out with a reason when there's no ready phone, no number, Do Not Call,
     a non-international number (decision 5), the feature is off, or the member lacks `call.log`.
2. **Call card:** in the CRM shell, minimizable, kept across navigation.
   - Draggable, with arrow-key moves (WCAG 2.5.7) and `aria-live` status, reusing the sticky-notes
     code.
   - Restored after a refresh from `/me/phone-call-requests/active`, and from session storage for
     a final state.

   | State | Card text |
   |---|---|
   | `requested` | "Sending to *Pixel 8*…" |
   | `sent` | "Sent to *Pixel 8*. Tap the notification on your phone" (with `delivery_unconfirmed`: "Sending may not have completed") |
   | `sent` + 30 s | "Your phone hasn't responded yet" |
   | `opened` | "Opening the dialer on your phone…" |
   | `dialing` | "Call in progress on your phone · 00:42 (includes ringing)" |
   | `needs_log` | "Call finished. Log the outcome" |
   | `outcome_unknown` | "We didn't hear back from your phone. Log the call if you made it" |
   | `failed(device_not_ready)` | "This phone isn't ready: notifications are off (last reported 10:42)" |
   | other final states | Their own plain words |

   - **Actions:**
     - **Cancel** (`requested`/`sent`);
     - **I'm done** = close (`opened`/`dialing`);
     - **Copy number** (only if `copy_allowed`);
     - **Log outcome** (loggable states);
     - **Close card**.
3. **Live status:** the member-scoped `phone_call` hint triggers a refetch, with 2-second polling
   as the fallback while active. Status is never copied into a client store.
4. **Multi-tab:** every tab shows the card. **Only the tab that started the request** (session
   storage) opens the log form automatically; the others show a **Log outcome** button. A 409
   `call_already_logged` opens the existing Activity.
5. English and Arabic in their own lazily loaded catalogue. Logical CSS only.

---

## 5. Delivery: one merge request per repo, in order

| # | Repo | Merge request | Gate |
|---|---|---|---|
| 0 | — | Owner decisions (§7). **CRM D-number** (incl. the §2.9 matrix rows), **MOB entry superseding MOB-022**, Platform ADR for the push channel. Firebase project per environment | Signed off |
| 1 | Platform | Push registration + readiness in the device list + the `push-deliveries` channel + its own token in every cross-check | Token moves between sessions; cascade on session end; cross-user, cross-organization and not-ready targets rejected; the ledger replays; `deferred` → a new key sends once; constant-time token check; 429 writes nothing |
| 2 | crm-backend | `session_id` claim + `phone_call` package + `phone_call_request_id` on `logCall` + lifecycle workflow and backstop + member hint + tenant setting + matrix rows | Every §2.2 transition; **two-connection concurrent `logCall` → one Activity**; open replay, wrong attempt, expiry, wrong session and missing claim; Do Not Call, access and number change re-checked at open; retry key rules and cancel race; the timers and backstop; late events |
| 3 | crm-app | Channel + readiness + FCM in three states + additive `place()` params + `web_call_requests` store and mutex + `SyncHandler` events + request id on every Log call path | Unit tests for the store, CAS, mutex and mapping; the **real-device checklist** (§6) |
| 4 | crm-frontend | Action, pickers, call card, log prompt | Multi-tab, refresh recovery, keyboard-only use, Arabic layout, bundle budgets |

Merge requests 3 and 4 can start once #2's contract is merged. **Rollout:**
- The tenant switch stays off until the new app is live.
- Old apps never register, so they are never eligible.
- Switching it off hides the action. Existing calling and logging are untouched.

## 6. Real-device checklist (gate for #3)

All on a Samsung phone and a Xiaomi/HyperOS phone:
- **App states:** foreground (sheet), background, cold start, force-stopped (expires).
- **Lock screen:** locked then unlocked.
- **Readiness:** notification permission denied, and the channel off → the web shows not ready.
- **Duplicates:**
  - a double tap, a sheet tap plus a notification tap, and two pushes for one request → **one
    dialer at most**;
  - the app killed between the CAS and the dialer → no second dialer.
- **Lost connection:** an open response lost (airplane mode right after the tap) → the replay works,
  with one dialer.
- **Dialer and tracker outcomes:**
  - no dialer app → `dialer_failed`, never `untracked`;
  - the dialer closed without calling → `not_placed` after 2 min;
  - `READ_PHONE_STATE` denied → `untracked`.
- **Interrupted calls:** a call longer than 3 minutes with the app killed during it → `recover()` →
  `ended`. The app killed while armed → `untracked`.
- **Offline:** offline for the whole call, back an hour later → the events land and the request
  reaches `needs_log`.
- **Access changes:** Do Not Call set, Lead access removed or the number changed between push and
  tap → refused, no dial.
- **Wrong organization:** a request for another organization → the switch offer.
- **Logging:**
  - logged on the phone from the call strip and on the web → one Activity;
  - the phone gone dead in `dialing` → the web's "I'm done" frees the slot.

## 7. Owner decisions
1. Firebase push, one project per environment.
2. Two taps (`ACTION_DIAL`).
3. A picker when there are several ready phones; never switch phones automatically.
4. Personal SIM use only behind the tenant switch, with the disclosure.
5. **New:** numbers stored without an international prefix (tenants with no dialling plan). Should
   they be callable from the phone (the SIM dials national numbers) while still checked against
   suppression, or blocked as `number_not_international` until the tenant sets a dialling plan?
   *Recommended:* allow, with suppression checked on the stored value, because the phone app's own
   Call button already dials them.

## 8. Review findings and how they were resolved

| Finding | Resolution |
|---|---|
| M1 one push key for all attempts: a `deferred` answer was replayed, never resent | Keys `pcr:{id}:{attempt}`, a new attempt only after `deferred`/429, `in_progress` handled, TTL frozen (§1.2, §2.3) |
| M2 the kernel idempotency blocked the open replay | No kernel key on open; an `attempt_id` fence; a matrix row (§2.4, §2.9) |
| M3 tracker events couldn't be matched to a request | An additive `sessionId` / `phoneCallRequestId` on `place()`, stored before the call (§3.3) |
| M4 wrong native mapping (`STOPPED`, `recover()`, `ringing`) | The mapping was rewritten from the code; `opened --ended-->` and the `needs_log` absorb added (§2.2, §3.3) |
| M5 the lead call strip could log a second, unlinked Activity | The request id is on every Log call path (§2.6, §3.3) |
| M6 a 15-second sweep breaks D203/D208 | Per-request durable timers + the D208 backstop + expiry on read (§2.3) |
| M7 stuck `dialing` / stuck phone entries | The requester's **close**, 90 min instead of 4 h, foreground stuck-entry recovery (§2.7, §3.4) |
| M8 two opens with the same attempt id could both dial | A per-request mutex + a CAS before `place()` (§3.4) |
| M9 `address_not_e164` counted as Do Not Call | Block only `opted_out`/`suppressed`; a distinct code + owner decision 5; `number_fingerprint` (§2.8, §7) |
| M10 no CRM-API-001 §6.1 rows | Explicit matrix rows under the D-number (§2.9) |
| M11 the CRM doesn't read `session_id` | The claim is added in #2; refused when absent (§2.0) |
| Minors | Activity context must include the Lead; composite FK; member-scoped hint; one expiry path; `abandoned` final state; locale from the profile; `organization_id` in the push data with a switch offer; tracker-based device-wide guard; `SyncHandler` instead of an outbox; MOB-022 superseded; leftover-notification copy |
