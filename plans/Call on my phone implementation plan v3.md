# Call on my phone: implementation plan (v3, simplified)

**Status:** Draft for owner review · 2026-11-08
**Replaces:** v2. v3 removes everything that was not needed to ship the feature, and fixes the
review's P0 findings.

---

## 1. What we are building, and what we are not

**Building:** a consultant clicks **Call** on a Lead in the web CRM. Their phone, signed in to the
CRM app, shows a notification. They tap it, the **phone's own dialer** opens with the number, and
they tap Call. The call goes out on **their own SIM**, exactly as calls from the app do today. The
web shows a small call card with honest status, and the call is logged once.

**Not building:**

| Removed | Why |
|---|---|
| Any telephony provider, bridge or "call me back" (Twilio/Exotel) | Not needed: the phone's own SIM places the call |
| Generic Platform "device commands", presence or reachability service | Over-scoped. The CRM owns its own call request |
| Background acknowledgement from the phone (and changing the token-refresh rule) | Can't be made reliable, and weakens a security rule |
| "Phone locked / offline / notifications off" diagnoses | Can't be known reliably (review P0-2). We say only what we know |
| One-tap direct dialing (`CALL_PHONE`) | Keeps MOB-040: the dialer opens and the user confirms |
| Universal cross-product call widget | A small CRM call card. Reuse the pattern later if ERP needs it |
| iOS, Contacts/Accounts, call recording | Later, separately |

## 2. Who owns what

| Part | Owns | Size |
|---|---|---|
| **Business Platform** | Storing the phone's push token **on its existing native session**, and sending a push to it | Small |
| **CRM backend** | The call request: authorization, number, Do Not Call, expiry, state, Activity link | Main piece |
| **CRM app (Android)** | Showing the notification, re-checking the request, opening the dialer with the **existing** call tracker | Small–medium |
| **CRM web** | Call action, phone choice, call card, log prompt | Small–medium |

There is **one state machine, in the CRM**. The Platform only delivers a push; it holds no call
state. That removes the two-backend consistency problem (review P1-1).

## 3. Platform (small change)

The same person is already the same user on web and phone. Every phone sign-in is a
`platform_sessions` row with `channel='native'`, and every CRM token carries its `session_id`.
We add only:

1. **`PUT /api/v1/native/session/push-token`**: the app (new version only) saves its FCM token
   on **its own** native session. Storage:
   - an encrypted token;
   - a keyed-hash fingerprint with a unique index, so the same token re-registered by another
     session moves instead of duplicating (review P1-2).
2. **The token dies with the session.** Logout, revocation and "end this device" already end the
   session, so a signed-out phone can never be pushed to. FCM `UNREGISTERED` clears it.
3. **The device list** (`GET .../session/devices`, already built) gains `can_receive_calls: true`
   when a push token is present.
4. **An internal, service-to-service `send push`**: `{platform_user_id, session_id, title, data}`.
   - It checks the session belongs to that user and is live, then calls FCM.
   - No business data. Data is only `{type: "crm.call_request", id}`.
5. **One Firebase project per environment** (dev / staging / prod). The credentials sit in the
   Platform's secret store.

That's all. There is no command table, ack endpoint or presence.

## 4. CRM backend

New small package `capabilities/phone_call/` (no descriptor, like `telephony`).

**Table `phone_call_requests`:**
- `id, org, member, lead_id, contact_point_id, target_session_id`
- `state, expires_at, opened_at, dial_started_at, ended_at, observed_seconds`
- `activity_id UNIQUE`, `revision`
- Row-level security, forward-only states.

**States (fewer and truthful):**

| State | Meaning | Web card says |
|---|---|---|
| `sent` | Authorized, saved, push handed to Firebase | "Sent to *Pixel 8*. Tap the notification on your phone" |
| `sent` + 30 s | (still `sent`, only the card's text changes) | "Your phone hasn't responded yet" (a warning, still cancellable) |
| `opened` | The phone fetched it and **the server re-checked everything** | "Opening the dialer on your phone…" |
| `dialing` | The existing tracker saw the call start | "Call in progress on your phone · 00:42" (time includes ringing) |
| `needs_log` | The call finished. Outcome not yet recorded | "Call finished. Log the outcome" |
| `logged` | Exactly one Activity linked | "Logged" |
| `cancelled` / `expired` / `refused` | Final | Says which, with **Copy number** |

No state claims "answered" or "connected". The outcome comes from the consultant in the existing
Log Call form (P0-8).

**Endpoints:**
- `GET /me/call-phones`: the member's phones that can receive calls, read from the Platform
  device list.
- `POST /leads/{id}/actions/call-on-my-phone {contact_point_id, session_id}` → 202, with
  `Idempotency-Key`.
  - Refusals: `no_call_phone`, `do_not_call` (**reuses the existing telephony suppression
    policy**), `no_phone_number`, `call_already_active`, `feature_disabled`.
- `POST /phone-call-requests/{id}/actions/open`. **The phone calls this when the notification is
  tapped.** In one transaction it:
  1. checks `state = sent` and `now < expires_at` (2 min);
  2. checks the caller's token `session_id` equals `target_session_id`, so only the targeted phone
     can open it;
  3. re-checks membership, Lead visibility, the calling permission, Do Not Call and that the
     contact point is unchanged (P0-5);
  4. moves the request to `opened` and returns the number, **once**.

  A second open, an expired request or a cancelled one returns 409. The phone shows "This call
  request is no longer valid" and **does not dial** (P0-3, P0-4). The phone never caches the
  number.
- `POST /phone-call-requests/{id}/events {dialing | ended, observed_seconds}`: from the phone,
  with `If-Match`. Late or duplicate events are ignored (forward-only).
- `POST /phone-call-requests/{id}/actions/cancel`: from the web. Valid only before `opened`.
  It cancels the request; it cannot hang up a SIM call.

**Rules:**
- **One active request per member**, enforced with a partial unique index.
- The push is sent after commit via the existing DBOS intent pattern (D388). A retry reuses the
  same request id, so it never creates a second request. A duplicate push is harmless because
  `open` is single-use.
- Live web updates come from a new hint kind on the **existing** notifications stream; the web
  refetches. Polling is the fallback.
- Logging reuses `logCall`, with `phone_call_request_id` added to `CallCreate`.
  `activity_id UNIQUE` plus the idempotency key means there is only ever one Activity, even if web
  and phone both submit (P0-9).
- Permission: reuse **`call.log`**. A tenant setting "Allow calling from web via members' phones"
  is **off by default**, with an admin disclosure: *"customers will see the consultant's own SIM
  number"* (P1-6).

## 5. CRM app (Android)

1. Add `firebase_messaging`. After sign-in, send the token to the Platform. Sending it again on
   token refresh is enough.
2. **The push is a notification message displayed by the system.**
   - Generic text: "Call request from CRM web". No name or number.
   - No background code runs, so there's no background authentication (D-A dropped).
   - A tap opens the app with the request id.
   - Before writing the code, check on a real device that backgrounded and terminated apps behave
     as expected (P0-1).
3. **On tap:**
   - Call `open`. If the server refuses, show why and stop.
   - Otherwise call the **existing `FollowedCallsController.place()`**, which arms
     `CallSessionTracker`, starts the **existing `specialUse` `CallMonitorService` unchanged**
     (MOB-103) and opens the dialer with `ACTION_DIAL` (MOB-040).
4. Pass the tracker's existing `started` and `ended` events to `/events`. The tracker already
   cancels when another call is going on (`OTHER_CALL`), so an unrelated call is not attributed
   to the Lead (P0-8).
5. The existing Log Call sheet opens after the call, pre-filled and linked to the request.
6. Recording stays withheld, as today (MOB-112). No new permissions are added.

## 6. CRM web

1. **"Call on my phone"** in the Lead's Contact menu and quick actions, loaded lazily.
   - If the Lead has several numbers, pick the number (the existing contact resolver).
   - If the member has several phones, pick the phone; one phone is used directly.
   - Greyed out with a reason when there's no phone, no number, Do Not Call, or the feature is off.
2. **Call card:** small and minimizable, and it stays across page navigation inside the CRM.
   - Draggable, with arrow-key moves for accessibility, reusing the sticky-notes code.
   - Restored after a refresh.
   - Shows the states in §4, plus **Cancel** (before `opened`), **Copy number** and **Log
     outcome**.
3. **The log prompt only in the tab that started the call.** Other tabs show the status only.

## 7. Delivery

Each merge request is small and independently mergeable.

| # | Repo | Merge request | Gate |
|---|---|---|---|
| 0 | — | Owner decisions (§8) recorded; Firebase projects per environment | — |
| 1 | Platform | Push token on native session + internal send-push + `can_receive_calls` | Token moves, dies on logout/revoke, cross-user send refused |
| 2 | crm-backend | `phone_call` package + `phone_call_request_id` on `logCall` + tenant setting | Single-use open, expiry, re-authorization, one Activity, Do Not Call |
| 3 | crm-app | FCM token, notification tap → open → existing call flow | Real-device checklist (§9) |
| 4 | crm-frontend | Action, phone/number pick, call card | Multi-tab, refresh, a11y, English and Arabic |
| 5 | — | Tenant pilot behind the setting, old app versions not eligible (they have no token) | Rollback leaves existing calling untouched |

Merge requests 3 and 4 can be built in parallel once #2's contract is merged.

## 8. Owner decisions (reduced to four)

1. **Firebase push**, one project per environment. *Recommended: approve.*
2. **Two taps on the phone** (notification, then dialer). *Recommended: approve for v1.*
3. **Several phones:** pick when there's more than one, and never switch automatically.
   *Recommended: approve.*
4. **Personal SIM use:** allowed only when the tenant admin turns it on, with the disclosure
   above. *Owner decision.*

## 9. Must pass before the pilot

- **App states:** foreground, background, terminated; locked then unlocked; notifications off;
  battery saver.
- **Phones:** Samsung and Xiaomi; a call longer than 3 minutes; the app killed during a call.
- **Request validity:** an expired or cancelled request can't dial; a double tap or duplicate push
  dials once.
- **Access changes:** Lead access removed, Do Not Call set or the number changed before the tap,
  so it is refused.
- **Devices:** the phone logged out or switched organization; another user's or tenant's request
  is refused.
- **Logging:** web and phone both log, and exactly one Activity exists.
- **Web:** two tabs, a browser refresh, Arabic layout and keyboard-only use.
