# Call on my phone: implementation plan (v2)

**Status:** Draft for owner review · 2026-11-08
**Scope:** Business Platform (`business-platform-backend`), `crm-backend`, `crm-frontend`, `crm-app`
**Research behind it:** `reports/Web to phone calling in CRMs.md` (17 vendors, Android/iOS rules, platform patterns)

---

## 1. The feature in one paragraph

A member clicks **Call** on a Lead in the web CRM. Their own phone, signed in to the CRM app, gets
the call within a second or two and places it on its SIM. A floating, draggable call card on the web
shows each step as it happens: *sent → phone received it → waiting for you on the phone → calling →
ended (3:12)*. If the phone is locked, has notifications off, is offline or is signed out, the card
says which, within about 10 seconds, and offers another way to call. When the call ends, the call
log form opens already filled in.

## 2. What we learned from other CRMs

| Who | How a web click reaches the phone | What the web is told |
|---|---|---|
| **Pipedrive** "Web-to-mobile calling" | Push to the app, tap, native dialer | Error only if the app isn't installed; call-log prompt afterwards |
| **HubSpot** "Call from HubSpot app" | Push to the app | Log dialog after the call |
| **LeadSquared** | Silent push to the device registered at login | "No Target Device Retrieved. Cannot Call", and nothing else |
| **Kylas, TeleCRM, NeoDove** | Push to the app, phone's own dialer, call log read afterwards | Activity appears after the call |
| **HubSpot "Call from phone", RingCentral RingOut** | The server rings your phone first, then the customer (bridge) | Full status, because the server owns the call |
| **Salesforce, Dynamics, Close, Aircall, Dialpad** | Browser softphone (VoIP), so the SIM is never used | Full status |

**Conclusions:**
1. Every vendor that uses the member's own phone does it the same way: **push → one tap → dialer**.
   Our design is the industry pattern, not an experiment.
2. **None of them shows live status, delivery confirmation or a clear "phone locked/offline" message
   on the web.** That is where we can be better than all of them.
3. Pairing is simply "signed in to the same account on both". Nobody makes users scan QR codes.
4. Nobody documents which phone rings when there are several. We should decide this and show it.
5. The reliable fallback when the phone can't be reached is a **server bridge call**. We already
   have Twilio/Exotel connections (D408) to build that on later.

## 3. Correction: we *do* know it's the same person

The person signed in on the web and on the phone is the **same Platform user and the same CRM
member**. That is already built:

- Both sign-ins are rows in the same Platform `platform_sessions` table: `channel = 'browser'` for
  the web and `channel = 'native'` for the app (D316 §2, Platform migration `0013_native_sessions`).
- The Platform already lists a person's devices: `GET /api/v1/native/session/devices`
  (`sessions/application/devices.py`) returns `id, channel, client, device_label, last_active_at`.
- Every CRM token carries a `session_id` claim that equals that device `id`, so every CRM request
  can be traced to the exact web or phone session it came from.

**What is missing is a way to reach the phone, not a way to know who it belongs to:**
- no push address (an FCM/APNs token) stored against the phone's session;
- no way to send that session a command and follow it to completion;
- no reachability signal ("last seen 2 min ago", "notifications off").

## 4. Architecture: build it once in the Platform, use it from every product

The ecosystem has several products with mobile apps (CRM, ERP mobile, others to come). "Send a command
to the user's phone and track it" is needed far beyond calling: approvals, sign-in confirmations,
task reminders, document signing. So the hard parts go in the **Platform**, and the CRM only adds the
calling-specific part.

```
                        ┌──────────────── Business Platform ────────────────┐
 crm-frontend ──REST──▶ │  Device Registry   (push address per native session)│
      ▲                 │  Push Service      (one FCM/APNs identity, quotas)  │
      │                 │  Device Commands   (send → ack → expire, generic)   │
      │                 └───────────▲───────────────────────┬───────────────┘
      │                             │ issue command          │ push {type, id}
      │ live hint (SSE)             │                        ▼
 crm-backend: Call Requests ◀──── phone reports status ── crm-app (Android)
   (lead, number, state, call log link)
```

### 4.1 Platform: Device Registry
- New table **`device_push_registrations`**:
  - `installation_id`: a UUID the app generates once per install.
  - `session_id`: the FK to the `platform_sessions` native row. This binds the phone to the person.
  - `client_id`, `platform` (android/ios), `push_handle` (encrypted, **unique**).
  - `app_version`, `os_version`.
  - `capabilities`: `has_telephony`, `can_place_call`, `notifications_enabled`, `full_screen_allowed`.
  - `status`, `last_seen_at`, `last_push_error`.
- `PUT /api/v1/native/session/push-registration`: the phone registers or updates itself with its
  DPoP-bound token. The Platform takes user and session from the token, **never from the request**.
- Lifecycle:
  - **Ending a session deletes the registration.** Logout, revocation, a credential reset and "end
    this device" all already end the session (D316 §2), so a signed-out phone can never be rung.
  - The same push token arriving for another user moves the row (the unique constraint).
  - FCM `UNREGISTERED` deletes it. A daily job prunes rows not seen in 30 days.
- Extend the existing device list with `reachability` (`push_ready`, `last_seen_at`, `capabilities`)
  so Settings → Signed-in devices shows it too.

### 4.2 Platform: Push Service
- **One platform-owned Firebase project and APNs key for the first-party apps.** The tenant is a
  routing attribute, not a credential. Per-tenant credentials are only needed if we ever ship
  white-label apps, and would then live in the per-tenant secret store.
- Payloads carry **only `{type, command_id}`**. There is no name, number or tenant data in the push,
  because it passes through Google/Apple (PDPL cross-border concerns; SECURITY §27 lock-screen rule).
  The app fetches details over the authenticated API.
- Push class: a **visible, time-sensitive notification**, never silent. FCM downgrades silent
  high-priority messages, and silent wake-ups are what make LeadSquared-style setups unreliable.
- Short TTL (60 s). A stale "call now" must never ring the phone minutes later.
- Quotas per tenant and per product, plus an audit of every push sent.

### 4.3 Platform: Device Commands (generic)
- A table **`device_commands`**: `id, product, type, user, target session, state, expires_at,
  acked_at, reason, created_at`.
- States: `created → pushed → acknowledged → accepted → completed`, with side exits `declined`,
  `failed(reason)` and `expired`.
- **The app acknowledges every push it receives**: `POST /api/v1/native/commands/{id}/ack` with
  `{locked, notifications_enabled}`. This is how the web learns "locked" in seconds instead of
  guessing. FCM gives no delivery receipts, so the app's own ack is the only truth.
- **This needs an amendment to the "no background token refresh" rule** (NATIVE-INTEGRATION.md
  L213): allow one ack call from a push handler. It uses the DPoP key, which works while locked
  because the key is not `setUnlockedDeviceRequired`. **Decision needed: D-A below.**
- Products subscribe to state changes. Each product registers its command types, much as Salesforce
  apps subscribe to notification types.

### 4.4 CRM backend: Call Requests (the calling-specific part)
New package `capabilities/phone_call/`, no descriptor, like `telephony`.
- Table **`phone_call_requests`**: `org, member, lead_id, contact_point_id, device_command_id,
  state, started_at, ended_at, duration_seconds, failure_code, activity_id, revision`.
  Row-level security, forward-only states (the `voice_calls` model).
- CRM states shown to the user:

  | State | Web card says |
  |---|---|
  | `sending` | Sending to your phone… |
  | `delivered` | Your phone got it. Tap the notification |
  | `phone_locked` | Unlock your phone to place the call |
  | `dialer_open` | Tap Call on your phone |
  | `in_call` | Calling · 00:42 |
  | `ended` | Call ended · 3:12. Log the outcome |
  | `no_response` | Your phone didn't respond. Open the CRM app, or call another way |
  | `notifications_off` | Notifications are off for the CRM app on your phone |
  | `declined` | Declined on your phone |
  | `cancelled` | Cancelled |
  | `expired` | Expired |

  **Honest limit:** Android does not tell an ordinary app when the other person answers (MOB-102),
  so the card says "Calling", never "Connected". iOS can report a connection later.
- Endpoints:
  - `GET /me/call-devices`: calling-capable phones, read from the Platform. The web uses this to
    show "Pixel 8 · seen 2 min ago" before you click, or to grey the button out.
  - `POST /leads/{id}/actions/call-on-my-phone` with `{device_id?}` and `Idempotency-Key` → 202.
    Refusals use Problem Details codes: `no_call_device`, `do_not_call`, `no_phone_number`,
    `call_request_in_progress`, `feature_disabled`.
  - `GET /phone-call-requests/{id}` and `POST .../actions/cancel` (`If-Match`).
  - The phone uses `GET /phone-call-requests/{id}` (the only place the number appears) and
    `POST .../events` for `dialer_open`, `in_call`, `ended`, `declined`.
- The flow follows D388: commit the request and an intent, then a DBOS workflow asks the Platform to
  issue the command. A sweep moves the request to `no_response` after about 10 s without an ack, and
  to `expired` after 2 min.
- Live web updates: a new SSE hint kind `phone_call` on the existing notifications stream (the D390
  precedent). It carries only "this request changed"; the web refetches.
- **Call log:** `ended` opens the existing `logCall` form on both web and phone, pre-filled and
  linked by `phone_call_request_id`, which stops duplicate logs (FR-A10-C01). One call = one
  Activity.
- New permission key `call.place_on_device`, granted with `call.log`, plus a backfill.

### 4.5 Mobile app (crm-app, Android first)
1. Add `firebase_messaging`. After sign-in, register via the Platform endpoint, re-register on token
   refresh, and drop the registration on sign-out.
2. On push:
   - Ack immediately, sending lock state and notification state.
   - Show a high-importance **CallStyle-like notification** with generic text, "Call requested from
     CRM web", and a **Call** action.
3. On tap:
   - Open the app, fetch the request and send `dialer_open`.
   - Reuse `FollowedCallsController.place()`. The existing `CallSessionTracker` and foreground
     service then report `in_call` and `ended` with the duration.
4. The tap itself is required by Android: since Android 10 apps can't open screens from the
   background, and since 14 full-screen pop-ups are only for incoming-call apps.
   - **Option 1 (current rule MOB-040):** tap the notification, then tap Call in the dialer. 2 taps.
   - **Option 2:** the notification's Call action dials straight away with `CALL_PHONE`. 1 tap.
     This reverses MOB-040. **Decision D-B.**
5. An in-app health check: notifications on, battery unrestricted, autostart on Xiaomi/Oppo/Vivo.
   Show it on first use and report it as capabilities, so the web can warn early. Battery killers
   are the top failure cause for every Android-first CRM we studied.
6. iOS later: time-sensitive push → open app → `tel:` (iOS always asks to confirm) → `CXCallObserver`.

### 4.6 Web (crm-frontend)
1. **Call button:** in the Contact menu and quick actions, "Call on my phone (Pixel 8)" next to the
   existing `tel:` call.
   - Shows the target device and its last-seen time before you click.
   - Greyed out with a reason when there's no phone, no number, Do Not Call, or the feature is off.
   - Loaded lazily, because the lead route is at 137.2 of its 140 KB budget.
2. **Floating call card:** app-shell level, so it survives navigation and works in any product. It
   follows the sticky-notes pattern:
   - portal, pointer drag, **arrow-key moves** (WCAG 2.5.7 needs a non-drag way to move it),
     clamped to the viewport;
   - minimize to a pill;
   - `aria-live` status announcements;
   - restored after reload from the request id;
   - kept out of the toast and assistant corners.
3. **Live status:** the SSE hint triggers a refetch, with 2-second polling as the fallback while a
   call is live. Tabs share one stream through the existing Web Locks / BroadcastChannel, so every
   tab shows the same card. The request is never copied into a client store.
4. **Card actions:** Cancel · Retry · Open lead · Log outcome · Close.
   - When the phone doesn't respond: **"Call another way"**, using the `tel:` link, and later a
     bridge call.
   - Strings in English and Arabic.

### 4.7 Tenant controls and governance
Layered enablement, as in the platforms we studied:
1. **Platform entitlement:** the tenant's plan includes it.
2. **Tenant admin:** "Allow calls from web to members' phones" is on.
3. **Role:** the member holds `call.place_on_device`.
4. **Member:** has a registered phone with notifications on.

Admin settings (later):
- the maximum number of phones per member;
- the minimum app version;
- a **default target phone or a chooser**;
- an audit of who sent which call to which device for which record.

Rate limit: one live request per member, and N per minute per tenant.

## 5. Delivery order

Each merge request must be independently mergeable into `develop`.

| # | Repo | Merge request | Depends on |
|---|---|---|---|
| 0 | all | Decisions D-A…D-F recorded (CRM D-number, MOB entries, Platform ADR); Firebase project; privacy review of the payload | — |
| 1 | Platform | Device Registry + push-registration endpoint + reachability in the device list | 0 |
| 2 | Platform | Push Service (FCM adapter behind a port, fake for tests) + Device Commands + ack endpoint | 1 |
| 3 | crm-backend | `phone_call` package: requests, endpoints, SSE hint, sweep, permission + backfill | 2 (contract) |
| 4 | crm-app | FCM registration, push handling + ack, notification, status events, health check | 2, 3 |
| 5 | crm-frontend | Call-on-my-phone action + floating call card | 3 |
| 6 | all | End-to-end on real phones: locked, killed, battery saver, offline, two phones, Xiaomi + Samsung | 1–5 |
| 7 | later | Bridge-call fallback via Twilio/Exotel; iOS; Contacts/Accounts; admin console | 6 |

Merge requests 4 and 5 can be built in parallel once #3's contract is merged.

## 6. Decisions needed before code

The backend rules say a gap in the spec means stop and ask, so these need an owner:

- **D-A Background ack:** allow the app one authenticated call from a push handler (an exception to
  "no background refresh"). *Recommended: yes.* Without it, "locked" can't be told apart from
  "offline".
- **D-B Taps:** 2 taps (keep MOB-040) or 1 tap (`CALL_PHONE`, reverses MOB-040). *Recommended: start
  with 2 and offer 1 as a tenant setting later.*
- **D-C Several phones:** ring the most recently active phone, or let the member pick a default?
  *Recommended: most recent by default, a chooser when ambiguous, never ring them all.*
- **D-D Push:** promote MOB-022/MOB-047 and D316 §13. FCM on a platform-owned Firebase project.
  This needs Firebase credentials.
- **D-E Scope:** Leads only first, or Contacts/Accounts too? *Recommended: Leads first.*
- **D-F Fallback:** is the bridge call (server calls your phone, then the customer) wanted as a
  later phase?

## 7. Risks

- **Phone battery killers (Xiaomi/Oppo/Vivo):** mitigated by the in-app health check plus the
  ack timeout, which gives a clear "didn't respond" instead of silence.
- **FCM downgrades:** always show a visible notification, never silent pushes.
- **Google Play review:** avoid `READ_CALL_LOG` (not needed); the existing `specialUse` foreground
  service is already declared.
- **Bundle budgets:** the lead route and shell are near their limits, so everything is lazy.
- **Privacy:** no personal data in pushes; the number is fetched only by the request's own phone,
  over the authenticated API.
