# Platform-level architecture: device registry, push, presence, cross-device commands, and the floating call widget

Scope: patterns for running "device registry + push + presence + device command (e.g. place a call)" as shared platform services in a multi-tenant, multi-product ecosystem where CRM is one product among several. Research date: 2026-11-08. Several vendor docs (developer.salesforce.com atlas pages, parts of Apple and HubSpot docs) returned 403 or the wrong page when fetched. Claims from those sources are marked as search-snippet or unverified.

---

## 1. How large platforms structure push and device registration

### Takeaway
Every major vendor splits the work the same way. A **platform-level registration object** (Azure "installation", SNS "platform endpoint", FCM registration/FID, Salesforce connected-app registration) binds a vendor push handle to an app and to routing metadata such as tags or user. Products then **send to users or tags**, not to raw tokens. Salesforce scopes push per connected app with per-app daily quotas. Zoho appears to do push per app, and I found no public evidence of a shared push bus across apps.

### Cited Findings
- **Azure Notification Hubs:** an *installation* is "an enhanced registration". Create/update is "fully idempotent". It supports a special tag `$InstallationId:{id}` for targeting a single device, and partial updates via JSON-Patch. — [MS Learn: Registration management](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-registration-management)
- Azure: a maximum of **60 tags per device**. "By default, registrations and installations do not expire." When a push hits a handle the PNS has expired, ANH "automatically cleans up the associated installation/registration". — [same](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-registration-management)
- Azure documents two patterns, register from the device or register through the backend. Backend registration lets you "modify tags... even when the corresponding app on the device is inactive" and "authenticate the client app before adding a tag". Example: the backend adds `"username:" + username` itself rather than trusting client-supplied tags. Device-side registration needs only *Listen* rights, but "apps can be hacked", so securing tags "requires extra care". ETag optimistic concurrency applies to registration updates. — [same](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-registration-management)
- **AWS SNS mobile push:** a *platform application* holds credentials and a *platform endpoint* is one device token. `CreatePlatformEndpoint` is idempotent for the same token and settings, and throws if the same token has different settings. AWS warns against calling create on every app start because a reinstalled app's endpoint may exist but be **disabled**. — [AWS SNS docs](https://docs.aws.amazon.com/sns/latest/dg/mobile-platform-endpoint.html)
- **Salesforce:** mobile push is configured per connected app. There are two flavours, Apex push ("send, fire, and forget") and Notification Builder push (richer). A Notification Builder push needs the connected app **subscribed to each custom notification type**. — search snippets of [Salesforce Mobile Notifications Overview / limits](https://developer.salesforce.com/docs/atlas.en-us.pushImplGuide.meta/pns_limits.htm) (direct fetch returned 403)
- Salesforce daily push limits are **per app per day**. Salesforce-provided apps get 50,000. Older doc versions list 35,000 for company-built internal apps and 5,000 for AppExchange apps. Test pushes count toward the limit. — [pns_limits (v200)](https://developer.salesforce.com/docs/atlas.en-us.200.0.pushImplGuide.meta/pushImplGuide/pns_limits.htm), [current](https://developer.salesforce.com/docs/atlas.en-us.pushImplGuide.meta/pns_limits.htm) (search snippets; verify against the current release)
- **Microsoft Teams/Graph presence:** presence is aggregated across per-client and per-app *sessions* (covered in section 4). — [Graph: manage presence state](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)
- **Odoo:** mobile push uses "Odoo Cloud Notification (OCN)". It is switched on under Settings > General Settings > OCN > Push Notifications. Odoo 12 used an `ocn_client` module. — [Viindoo docs](https://viindoo.com/docs/13.0/d/mobile-329), [Odoo forum](https://www.odoo.com/forum/help-1/push-notification-on-odoo-mobile-application-v12-219934) (secondary sources; I found no official OCN architecture doc). Users report the checkbox alone sometimes fails to deliver. Third-party FCM modules for Odoo 17–19 exist and depend on `firebase-admin`. — [apps.odoo.com alwin_firebase_push_notification](https://apps.odoo.com/apps/modules/18.0/alwin_firebase_push_notification)
- **Zoho:** Zoho Creator push is configured **per application** and needs the customer's own FCM credentials and APNs certificates. — [Zoho Creator help](https://www.zoho.com.cn/creator/help/application/push-notifications.html). Cross-app aggregation exists in the Zoho Workplace dashboard, which lets users "view all your app notifications in one place" and toggle per app. — [Zoho Workplace](https://www.zoho.com/workplace/collaboration-dashboard.html). A Zoho One-wide announcement layer is still a community *feature request*. — [Zoho community](https://help.zoho.com/portal/es/community/topic/organization-wide-announcement-banner-across-all-zoho-one-applications)
- **Slack** rebuilt notifications into "a unified notifications model across desktop and mobile". It replaced four legacy preference systems with three options: all messages, mentions, or mute. — [InfoQ, Apr 2026](https://www.infoq.com/news/2026/04/slack-new-notification-system/), [slack.engineering push tag](https://slack.engineering/tags/push-notification/). An earlier Slack post covers quiet "informational" pushes that replace earlier ones. — [Into the Clouds](https://slack.engineering/into-the-clouds/)

### Inferences
- The common shape for a multi-product platform is a **platform Device Registry service** that owns (tenant, user, session, installation, push handle, app/product channel) and a **Notification service** that products call with "user X, category Y, payload ref Z". Products should never hold raw tokens. This mirrors Azure's backend-managed tags, SNS endpoints, and Salesforce's "custom notification type subscribed by connected app".
- Salesforce's per-app quotas and per-type subscriptions suggest a model for per-product **notification types**. The platform owns delivery, and each product registers types that admins can enable or disable.
- Zoho is per-app at the push-credential level, which shows the fragmented end state a unified ecosystem should avoid. This is an inference from limited public evidence.

### Gaps
- No primary source on Atlassian's mobile device-token architecture or on Slack's multi-workspace token handling. Searches turned up only general posts.
- I could not fetch Salesforce's current pushImplGuide body (403), so the Apex `Messaging.PushNotification` payload limits are unverified.
- I did not verify AWS Pinpoint's deprecation status or the "End User Messaging" rename in this pass.
- No official Odoo OCN internals. From training knowledge only, unverified: Odoo 16+ replaced longpolling with a websocket bus shared across tabs through a SharedWorker (`bus` module). Check this in the odoo/odoo source before citing it.

---

## 2. Device registry design: binding, token lifecycle, pruning

### Takeaway
Store one row per app installation, keyed by a stable client-generated installation ID. Bind it to user, tenant and session, and give it a `last_seen/updated` timestamp. Upsert idempotently on every app start. Delete or disable the row on the vendor's invalid-token signal (FCM `UNREGISTERED`/404, or `INVALID_ARGUMENT`/400 only when the payload is known to be valid). Run a scheduled prune of stale rows, around 30 days per Firebase's default. Logout or session revocation must also remove the binding.

### Cited Findings
- FCM recommends storing the registration "keyed by user ID, with an `installationId` field and a `timestamp` field", and updating the timestamp on every upload. — [Firebase: manage tokens](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- "By default, FCM considers a registration to be stale if its app instance hasn't connected for a month." Android registrations expire after **270 days** inactive. Choose your own window: "one month may be too short or too long". The example prune job uses 30 days and runs daily. — [same](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- With HTTP v1, delete on `UNREGISTERED` (404) or `INVALID_ARGUMENT` (400). The caveat: "INVALID_ARGUMENT can also be returned in cases of issues in the message payload." — [same](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- Legacy token refresh: "once per month strikes a good balance", and there is "no benefit to doing the refresh more frequently than weekly". The newer FID APIs auto-refresh via `onRegistered()`. Resubscribe topics when the FID changes, and remove topic mappings for stale instances. — [same](https://firebase.google.com/docs/cloud-messaging/manage-tokens)
- SNS recommended registration routine: if no ARN is stored, create one. Then always call `GetEndpointAttributes`. If not found, recreate. If the token differs or `Enabled=false`, call `SetEndpointAttributes` with the latest token and enable. The routine "is safe to call it multiple times". — [AWS SNS](https://docs.aws.amazon.com/sns/latest/dg/mobile-platform-endpoint.html)
- SNS disables endpoints when APNs or FCM report an invalid token. Re-enabling without a new token "will not work". There is a quota on endpoints created from the same token, and the error is "This endpoint is already registered with a different token". — [same](https://docs.aws.amazon.com/sns/latest/dg/mobile-platform-endpoint.html)
- Azure installations use a client-generated GUID stored on the device (`__NHInstallationId`) as the stable key, with the push channel updated on each start. — [MS Learn](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-registration-management)

### Inferences
Suggested data model, synthesized from the patterns above:
- `device_installation(id PK = client UUID, tenant_id, user_id, platform_session_id, product_scope[], platform{ios,android,web}, push_provider, push_handle (encrypted), app_id/bundle, app_version, os_version, device_label, capabilities{can_place_call, ...}, status{active,disabled,revoked}, created_at, last_registered_at, last_seen_at, last_push_error, disabled_reason)`.
- Unique on `push_handle` per provider so one handle is never bound to two users after a shared-device re-login. On upsert, reassign or delete any previous row with the same handle. This follows from the SNS duplicate-token warning.
- Session binding: when platform SSO revokes a session or the user logs out, set status to `revoked` and stop targeting. The app should also call delete on logout. The registry is user- and tenant-scoped, but credentials and app are global or platform-scoped (section 3).
- Prune triggers: provider error codes (immediate), the staleness job (daily, 30–60 days), user or admin removal, and tenant offboarding.

### Gaps
- No vendor doc I fetched explicitly specifies session-revocation-driven token unbinding. This is an inference and a best practice, not sourced.

---

## 3. Push credentials in multi-tenant SaaS, isolation, and payload minimization

### Takeaway
Use one platform-owned FCM/APNs app identity for the vendor's own mobile app, so the tenant is a routing attribute and not a credential boundary. Per-tenant credentials are needed only for white-label or tenant-built apps, which is the Zoho Creator and Salesforce Mobile Publisher model. Keep payloads data-only and minimal (IDs plus a type), and have the app fetch details over its authenticated session. The 4 KB cap and privacy rules (GDPR, Saudi PDPL cross-border transfer rules) both favour this.

### Cited Findings
- FCM: "Maximum payload for both message types is 4096 bytes." Data messages carry only custom key-value pairs and are handled by the client. Notification messages go to the tray when the app is in the background. — [Firebase: message types](https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type)
- The tenant-built app model needs tenant-supplied FCM credentials and APNs certificates (Zoho Creator). — [Zoho Creator](https://www.zoho.com.cn/creator/help/application/push-notifications.html)
- Azure ANH supports templates per installation, which allow per-device payload transformation, and tag expressions for routing. — [MS Learn](https://learn.microsoft.com/en-us/azure/notification-hubs/notification-hubs-push-notification-registration-management)
- Saudi PDPL: SDAIA published the amended *Regulation on Personal Data Transfer Outside the Kingdom* on **1 Sep 2024**, detailing Article 29. The March 2023 amendments (Royal Decree M/148) introduced adequacy. Commentators describe a pre-transfer risk assessment for sensitive or continuous transfers. — [Clyde & Co 2024](https://www.clydeco.com/en/insights/2024/09/saudi-arabia-s-personal-data-protection-law-become), [Clyde & Co 2025](https://clydeco.com/en/insights/2025/02/10-legal-updates-ksa-tech-and-data-laws), [Baker McKenzie](https://insightplus.bakermckenzie.com/bm/data-technology/saudi-arabia-new-amendments-have-been-introduced-to-the-personal-data-protection-law), [Digital Policy Alert](https://digitalpolicyalert.org/event/22351-implemented-regulation-on-personal-data-transfer-outside-the-kingdom). These are law-firm commentary, not the primary SDAIA text.
- SDAIA opened a public consultation on amendments to the PDPL Implementing Regulation (reported 9 Oct 2026). — [Al Tamimi](https://www.tamimi.com/news/sdaia-opens-public-consultation-on-proposed-amendments-to-the-pdpl-implementing-regulation/)

### Inferences
- Push payloads transit Google and Apple infrastructure outside KSA and UAE. Putting the callee phone number or customer name in the push is therefore plausibly a cross-border transfer of personal data. Sending `{type:"call_request", request_id, tenant_hint}` and fetching details over TLS from the in-region API reduces the exposure. This is an inference, not legal advice.
- Tenant isolation: the payload should not be enough to act on its own. The app must re-authenticate and the server must check that the request belongs to the device's current user and tenant. This guards against a token re-bound to another user receiving a stale push.
- Use a single vendor FCM project for the first-party app, and add per-tenant credentials only for white-label builds. This keeps quota and abuse monitoring centralized. Salesforce's per-app quotas show that limits attach to the app identity.

### Gaps
- No primary source on UAE PDPL (Federal Decree-Law 45/2021) executive regulations in this pass.
- No authoritative source on FCM per-project quotas for multi-tenant senders.

---

## 4. Presence, reachability, ACKs and command lifecycle

### Takeaway
Presence should be **session-based with expiry**: each client or app holds a session that must be refreshed or it decays, and the user's presence is an aggregate (the Graph model). For device commands, use the MDM pattern. Queue a command with an ID and an expiry, send a content-free wake push, have the device fetch and execute it, and have the device report a terminal status. A command left unacknowledged at expiry becomes "expired" or "unreachable".

### Cited Findings
- Graph: "Each Teams client has an independent presence session and the user's presence is an aggregated state from all the sessions." Precedence is user-preferred > session states, and DoNotDisturb > Busy > Available > Away. — [Graph: manage presence state](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)
- Graph timeouts: an `Available` session times out in **5 minutes** and decays to `AvailableInactive`, then to `Away` after another 5 minutes. `expirationDuration` defaults to 5 minutes, with a valid range of **5 min to 4 h**, after which the session becomes `Offline`. Apps must call `setPresence` before the timeout to keep the state. — [same](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)
- Graph presence values include `InACall`, `Busy` and `PresenceUnknown`. It has a `sequenceNumber` for versioning and supports change-notification subscriptions. — [Graph presence resource](https://learn.microsoft.com/en-us/graph/api/resources/presence)
- Cross-tenant presence in Teams requires mutual trust via External Access allow-lists. — [Graph: manage presence state](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)
- **Android Management API** `issueCommand` returns a long-running `Operation`. `Command.duration`: "The command will expire if not executed by the device during this time… The default duration if unspecified is ten minutes." The command carries an `errorCode` (`UNKNOWN`, `API_LEVEL`, `MANAGEMENT_MODE`, `INVALID_VALUE`, `UNSUPPORTED`), and status is tracked via get operation. — [AMAPI issueCommand](https://developers.google.com/android/management/reference/rest/v1/enterprises.devices/issueCommand)
- **Apple MDM** (the page fetch failed; this description comes from widely documented protocol behaviour and needs checking against Apple's reference). The server queues commands per device by `CommandUUID` and sends an APNs push using the `PushMagic` with **no command payload**. The device checks in to the `ServerURL` and receives the next command. It replies `Acknowledged`, `Error` (with `ErrorChain`), `NotNow` (retry later), or `Idle` (nothing to report). — [Apple: Sending MDM commands](https://developer.apple.com/documentation/devicemanagement/sending-mdm-commands-to-a-device) (not verified in this session)

### Inferences
Proposed "place call on phone" state machine, modelled on AMAPI and MDM:
- `created → pushed` (wake sent; record the provider message ID or error) `→ delivered` (app ACKs on receipt, before user action) `→ accepted/dialing` (user tapped, or auto-dial where policy allows) `→ completed | failed(reason) | declined`. A side exit to `expired` happens when `now > expires_at`. The TTL is short for calls (around 30–60 s) versus AMAPI's 10-minute default.
- Treat "push send succeeded" as distinct from "delivered". Only an app ACK proves reachability. No ACK within N seconds should show the web user "phone not reachable" and offer a fallback.
- Presence for "is the phone available for calls" should be a device-scoped session with a TTL (heartbeat on foreground or periodic background). Graph's 5-minute decay is a reasonable reference. Show "last seen" when the session has expired rather than claiming offline.
- Commands must be idempotent by command ID, because pushes can be duplicated and the device may fetch more than once.

### Gaps
- iOS background execution limits for data-only (content-available) pushes were not retrieved. This matters because iOS may throttle silent pushes, and VoIP/PushKit or CallKit rules are relevant if the phone must ring. Another researcher may cover it.

---

## 5. Per-tenant enablement, admin policy, entitlements

### Takeaway
Platforms gate push or device features at several layers: app identity (connected app), notification type subscription, admin enablement, and user preference. External or cross-tenant reach requires explicit admin allow-lists.

### Cited Findings
- Salesforce Notification Builder requires each custom notification type to be enabled for, or subscribed by, a connected app before it pushes. — [Salesforce pns_limits (snippet)](https://developer.salesforce.com/docs/atlas.en-us.pushImplGuide.meta/pns_limits.htm)
- Odoo: push is a tenant-level setting in General Settings (OCN). — [Viindoo docs](https://viindoo.com/docs/13.0/d/mobile-329)
- Teams: cross-tenant presence visibility is controlled by admin External Access allow-lists, and mutual trust is required. — [Graph](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)
- Slack: user-level preferences consolidated into three modes. — [InfoQ](https://www.infoq.com/news/2026/04/slack-new-notification-system/)
- Zoho Workplace: users can toggle notifications for all apps or selected ones. — [Zoho Workplace](https://www.zoho.com/workplace/collaboration-dashboard.html)

### Inferences
Suggested policy layers for the platform:
1. Platform entitlement: the licence includes "Device calling".
2. Tenant admin enable, plus policy: allowed platforms or app versions, max devices per user, whether managed devices are required, retention period for command and audit logs.
3. Role or permission: which roles may "call via my phone".
4. User device opt-in, plus product-level notification-type preferences.
5. Every command written to an audit log (who, which device, target record, outcome).

### Gaps
- No vendor doc retrieved on per-tenant retention policies for push or command logs.

---

## 6. Real-time to web: transport, hint-then-refetch, multi-tab fan-out

### Takeaway
For browser updates on call-request status, push small "hints" (event type plus ID) over a platform real-time channel and refetch the state over REST. This is the same minimization logic as mobile push. Fan out across tabs with a single connection per browser, shared via SharedWorker or BroadcastChannel, so N tabs don't open N sockets and only one tab acts on each event.

### Cited Findings
- BroadcastChannel allows communication between "windows, tabs, frames, or iframes and workers on the same origin". Contexts subscribe by channel name. Communication is scoped by storage partition (top-level site), not just origin. MDN's example use case is detecting login and logout in other tabs. — [MDN Broadcast Channel API](https://developer.mozilla.org/en-US/docs/Web/API/Broadcast_Channel_API)
- Graph presence uses change-notification subscriptions plus a `sequenceNumber` for ordering, which is the hint-and-version pattern. — [Graph presence](https://learn.microsoft.com/en-us/graph/api/resources/presence)
- Teams clients poll, so Graph presence changes "take a few minutes" to show. — [Graph](https://learn.microsoft.com/en-us/graph/cloud-communications-manage-presence-state)

### Inferences
- SSE is enough for server-to-browser status updates and works over plain HTTP/2 with auth cookies. WebSocket is warranted if the browser must send frequent messages. Managed pub/sub (Ably, Pusher, Centrifugo) offloads connection scaling but adds a data processor, which raises residency questions under PDPL. I did not fetch vendor docs to source this comparison.
- Use a version or sequence number on the call-request resource so a late hint never overwrites newer state.
- Use leader election across tabs (e.g. via the Web Locks API or BroadcastChannel) so only one tab plays a ring or toast. All tabs still update their UI.

### Gaps
- I did not fetch primary docs for Ably, Pusher or Centrifugo, or the SSE versus WebSocket specs. The report writer should treat that comparison as unsourced.
- Odoo's websocket and SharedWorker bus is unverified (see section 1 gaps).

---

## 7. Web UI: floating or docked live call widget

### Takeaway
CRMs host the softphone in a **persistent shell-level container** that survives in-app navigation: the Salesforce Lightning utility bar, HubSpot's calling iframe, and Aircall's detachable always-on-top window. The container supports minimize, restore and popout. On mobile the pattern collapses to a persistent top "live call bar". Accessibility requires that any drag-to-move also has a non-drag alternative (WCAG 2.2 SC 2.5.7, AA).

### Cited Findings
- Salesforce Open CTI for Lightning: `sforce.opencti.setSoftphonePanelVisibility({visible, callback})` shows the panel with `true`, and with false "the panel is minimized" (API 38.0+). Sibling methods set the panel height, width, label and icon in the utility bar. — [setSoftphonePanelVisibility](https://developer.salesforce.com/docs/service/api-cti/guide/sforce-api-cti-setsoftphonepanelvisibility-lex.md), [setSoftphonePanelHeight](https://developer.salesforce.com/docs/service/api-cti/guide/sforce-api-cti-setsoftphonepanelheight-lex.md), [setSoftphonePanelWidth](https://developer.salesforce.com/docs/service/api-cti/guide/sforce-api-cti-setsoftphonepanelwidth-lex.md), [setSoftphonePanelIcon](https://developer.salesforce.com/docs/service/api-cti/guide/sforce-api-cti-setsoftphonepanelicon-lex.md)
- Aircall mobile, iOS only: an active call can be minimized. A live call bar stays at the top and remains visible across screens and modals. — [Aircall support](https://support.aircall.io/en-gb/articles/34768865195933)
- Aircall desktop app: the in-call toolbar detaches into an always-on-top floating window. This is desktop-app only, and it opens on the main display. — [Aircall support](https://support.aircall.io/en-gb/articles/21534383206685), [Aircall support](https://support.aircall.io/en-gb/articles/31498999444253)
- WCAG 2.2 SC 2.5.7 Dragging Movements (AA): functionality that uses dragging must be achievable "by a single pointer without dragging" unless dragging is essential. Examples include directional buttons and selecting an item and then a destination. — [W3C Understanding 2.5.7](https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html)
- HubSpot calling-extension docs: the page I fetched covered help-desk channel connection (webhook returning `phoneNumbers`, `isReady` flag), not the widget's popout behaviour. — [HubSpot calling extensions guide](https://developers.hubspot.com/docs/api-reference/crm-calling-extensions-v3/guide)

### Inferences
Widget design guidance for the web side of "call via my phone":
- Mount the widget in the platform app shell, outside the product router, so it persists across CRM pages and across products in the ecosystem. It should be a platform UI service, with the state in a store keyed by `request_id` and rehydrated after a reload from the server.
- Provide three states: docked (in a utility bar or corner), expanded, and minimized pill. Add a "dock left/right" or "move" button set as the non-drag alternative required by 2.5.7. Allow arrow-key movement when the move handle is focused. Persist the position per user in localStorage.
- Semantics: if it is non-modal, use `role="region"` or `role="dialog"` without `aria-modal`, with an `aria-label` such as "Call in progress". Announce status changes ("Ringing on your phone", "Phone unreachable") through a polite `aria-live` region. Never trap focus in a non-modal widget. Provide a skip shortcut to focus it.
- At narrow widths, switch from a floating box to a full-width top or bottom bar (the Aircall iOS pattern). Respect safe-area insets, and avoid covering primary actions.
- Multi-tab: show the active widget in every tab via BroadcastChannel, but let only the leader tab produce sound or notifications.

### Gaps
- I could not retrieve primary docs on Twilio Flex, Zendesk Talk, or HubSpot calling-window popout behaviour (`usesCallingWindow`) in this pass. The Salesforce Open CTI popout behaviour is also unconfirmed.
- No WAI-ARIA APG pattern specifically for floating non-modal panels was retrieved. The ARIA guidance above is inference from general practice.
