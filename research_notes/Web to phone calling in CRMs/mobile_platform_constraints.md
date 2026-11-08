# Mobile platform constraints for a "remote place-this-SIM-call" companion app (Android 15/16/17, iOS 18/26) — researched 2026-11-08

Scope: an app that receives a "place this call" request (web app -> server -> push), places a cellular/SIM call, and reports call status back. All URLs fetched 2026-11-08 unless noted.

## Android: FCM delivery (priority, Doze, standby buckets, force-stop, TTL, collapse, delivery visibility)

### Takeaway
High-priority FCM can wake a Dozing device and grants a brief exemption to start a foreground service or expedited job, but only if the message really is high priority at receipt (FCM deprioritizes apps whose high-priority messages do not produce visible notifications) and only if the app is not force-stopped. The server gets no real-time per-message delivery receipt from FCM, so the app must send its own acknowledgement to the server.

### Cited Findings
- Normal-priority messages "may be delayed to conserve battery until the device exits doze". High-priority messages let FCM "wake a sleeping device when necessary" and allow limited processing, including very limited network access. They should generally lead to user interaction — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority)
- Deprioritization: if high-priority messages do not produce user-facing notifications, FCM may lower them to normal priority. FCM evaluates 7 days of behaviour per app instance. Detect it by comparing `RemoteMessage.getPriority()` with `getOriginalPriority()`, or with the Aggregate Delivery Data API. Disabled notifications also lead to deprioritization, so check that notifications are enabled before sending high-priority messages — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority)
- `onMessageReceived` gets "several seconds" (slightly more for high priority), "only expected to be long enough to immediately render a notification". Avoid extra async network calls inside the handler. For more work, use WorkManager or a foreground service. "Scheduling one [expedited job] right after a high priority onMessageReceived is covered by a brief exemption from expedited job quotas" — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority)
- New API (2026): FCM recommends migrating to `AndroidConfigV2` (`message.android_v2`), where urgency is set by message type: `RemoteNotification` for user-visible time-sensitive notifications and `BackgroundSync` for non-urgent work. "v1 of FCM used high priority messages whereas v2 uses RemoteNotification ... We strongly recommended migrating to v2 as v1 is deprecated" — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority); [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- App Standby Buckets page: "the only intended use for RemoteNotification is to push a notification to the user ... There is a policy enforcement for usage of these message types: a 20-second execution window that falls back to the original notification. There is no enforcement if the app is in foreground or user permits background runs." If the app shows no notification, the user cannot interact with it to promote it to the active bucket — [App Standby Buckets](https://developer.android.com/topic/performance/appstandby)
- Doze checklist: use FCM for downstream messaging, and put enough information in the initial payload that no further network access is needed. Exemption from battery optimization via `ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` is acceptable only if Doze or App Standby breaks core function, or FCM RemoteNotification cannot be used. "Instant messaging, chat, or calling app" appears in the use-case table — [Doze & App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- Google Play services may proxy (display) eligible high-priority notification messages on the app's behalf without launching the app. This is the default on Android Q+ for HTTP v1 messages. It can be opted out per message (`proxy: DENY`) or via manifest — [FCM message priority](https://firebase.google.com/docs/cloud-messaging/android/message-priority)
- Force-stopped apps: "Messages were dropped due to the application being force-stopped on the device at the time of delivery, and retries were unsuccessful ... FCM can't deliver the message. Unfortunately, you likely can't do much about this." Inactive devices: messages dropped, and on reconnect the SDK calls `onDeletedMessages()` — [Firebase blog, Understanding FCM delivery rates (Jul 2024)](https://firebase.blog/posts/2024/07/understand-fcm-delivery-rates/). Firebase maintainers explain that FCM follows the Android rule that stopped apps are not started without user action — [firebase/quickstart-android#368](https://github.com/firebase/quickstart-android/issues/368) (forum source). Some OEMs treat swipe-from-recents as a force-stop or "restrict launch" (anecdotal GitHub reports).
- TTL: 0 to 2,419,200 s (28 days), default four weeks. FCM does not apply collapsible-message throttling to TTL=0 messages. "a ttl value of 0 means messages that can't be delivered immediately are discarded ... this provides the best latency" — [Set message lifespan](https://firebase.google.com/docs/cloud-messaging/customize-messages/setting-message-lifespan)
- Collapse keys: at most 4 different collapse keys stored per device or registration token. Non-collapsible messages: up to 100 stored on Android, after which all stored messages are discarded and the app is told the limit was reached (full sync needed). FCM doesn't guarantee delivery order — [Collapsible message types](https://firebase.google.com/docs/cloud-messaging/customize-messages/collapsible-message-types)
- What the server can know: (a) Aggregated Delivery Data API: Android only, aggregated (not per-message), 7 days of history, delayed up to 5 days. (b) BigQuery export: per-message events such as `MESSAGE_ACCEPTED` and `MESSAGE_DELIVERED` ("delivered to the app's FCM SDK on the device", not on by default; enable with `setDeliveryMetricsExportToBigQuery(true)` or manifest meta-data). It requires Google Analytics. Initial propagation takes up to 48 h, with a daily sync starting 4:00 AM PT. No real-time per-message receipt to your server is documented — [Understand message delivery](https://firebase.google.com/docs/cloud-messaging/understand-delivery)
- FCM delivery statuses (blog) include delivered, device offline, Doze delay (normal priority), throttled, pending, TTL expired, force-stopped, and inactive device — [Firebase blog](https://firebase.blog/posts/2024/07/understand-fcm-delivery-rates/)

### Inferences
- Send the "place call" command as a time-sensitive, user-visible message (v1 `priority: high`, or v2 `RemoteNotification`) and always post a visible notification. Otherwise FCM deprioritizes the app and the foreground-service and expedited-job exemptions are lost.
- Use a short TTL (for example 30–120 s) or TTL=0, so a stale "call now" command is never delivered hours later. Use non-collapsible messages with a per-request ID, or one collapse key per user, so a newer request replaces an older one.
- The app must POST its own ack ("received", "notification shown", "call placed", "ended") to the server. FCM telemetry is too delayed for live CRM UX.

### Gaps
- Maximum FCM payload size (traditionally 4096 bytes for data messages) was not re-verified this session, because the concept-options page returned 404 (moved).
- Exact quotas for expedited jobs and the per-device high-priority rate were not found as numbers.
- The exact semantics of the 2026 "20-second execution window that falls back to the original notification" for RemoteNotification are not fully documented on the pages read.

## Android: background activity launch (BAL) restrictions and full-screen intents

### Takeaway
Since Android 10 an app cannot open an activity (including a dialer UI) from an FCM handler unless an exemption applies. The intended path is a notification the user taps, or a full-screen intent. Since Android 14, `USE_FULL_SCREEN_INTENT` is auto-granted only to apps whose core function is calling or alarms, with a Play Console declaration. An outbound "click-to-call" CRM companion is unlikely to qualify, so it should expect to ask the user for the permission or fall back to a heads-up notification.

### Cited Findings
- BAL restrictions apply since Android 10 (API 29). Exemptions: the app has a visible window; the app is the current IME; the activity is started from a `PendingIntent` sent by the system (for example a notification tap); the app has `SYSTEM_ALERT_WINDOW` granted by the user; `START_ACTIVITIES_FROM_BACKGROUND` (privileged); the app is bound by a service with that grant; the launcher or widget initiates; or a core OS component starts it (for example Telephony starting the incoming-call screen) — [Restrictions on starting activities from the background](https://developer.android.com/guide/components/activities/background-starts)
- PendingIntent hardening:
  - Targeting Android 14 (API 34): senders no longer grant BAL privileges by default and must opt in via `ActivityOptions.setPendingIntentBackgroundActivityStartMode()`. The recommended mode is `MODE_BACKGROUND_ACTIVITY_START_ALLOW_IF_VISIBLE` (SDK 36).
  - Targeting Android 15 (API 35): creators must opt in via `setPendingIntentCreatorBackgroundActivityStartMode()`.
  - `Context.startIntentSender()` needs a sender opt-in from API 34. `IntentSender.sendIntent()` needs one from API 37.
  - Blocked launches fail silently, with "Background activity launch blocked!" in logcat. Android 16 adds StrictMode `detectBlockedBackgroundActivityLaunch()`.
  - In-task hijacking protections are opt-in for apps targeting API 37 (`android:allowCrossUidActivitySwitchFromBelow`).
  - Source: [Background starts](https://developer.android.com/guide/components/activities/background-starts)
- Android 14 behaviour change: "For apps targeting Android 14 (API level 34) or higher, apps that are allowed to use this permission are limited to those that provide calling and alarms only. The Google Play Store revokes default USE_FULL_SCREEN_INTENT permissions for any apps that don't fit this profile". The deadline was May 31, 2024. Use `NotificationManager.canUseFullScreenIntent()` and `Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT` — [Android 14 behavior changes](https://developer.android.com/about/versions/14/behavior-changes-14)
- `canUseFullScreenIntent()`: "If permission is denied, notification will show up as an expanded heads up notification on lockscreen" — [NotificationManager reference](https://developer.android.com/reference/android/app/NotificationManager)
- Play policy FAQ: auto-grant applies to apps whose core functionality is "setting alarms or receiving phone or video calls". The Play Console declaration (App content page) started May 31, 2024, and only calling or alarm apps have the permission enabled by default from January 22, 2025 (targeting Android 14+). Other apps must "prompt users to grant permission ... and gracefully degrade the experience if denied" — [Play Console Help: Understanding foreground service and full-screen intent requirements](https://support.google.com/googleplay/android-developer/answer/13392821)

### Inferences
- The Play wording ("receiving phone or video calls") targets incoming-call UX. A CRM app that triggers outbound SIM calls should not count on the auto-grant. Design for: a high-priority push, then a heads-up notification with a "Call now" action (a notification tap is a system-sent PendingIntent, so it is BAL-exempt), with an optional user-granted FSI for lock-screen prominence.
- A notification action can directly fire a broadcast or service that calls `TelecomManager.placeCall` (no activity needed). That keeps a human tap in the loop, which also matches Play's intent for `CALL_PHONE`.
- `SYSTEM_ALERT_WINDOW` ("display over other apps") is a technical BAL exemption, but it needs a special-access grant. Play reviews it, and it does not help on a secure lock screen.

### Gaps
- No primary source was found on whether `CATEGORY_CALL` or `Notification.CallStyle` without a ConnectionService call gets special lock-screen treatment. CallStyle docs were not fetched, apart from the TelecomManager note below.
- The exact Play policy paragraph defining "calling" core functionality was not fetched (the policy hub page lists permissions; the FAQ was read).

## Android: placing the call (ACTION_DIAL / ACTION_CALL / placeCall, dialer role, ConnectionService)

### Takeaway
With the runtime `CALL_PHONE` permission, `TelecomManager.placeCall()` or `ACTION_CALL` places a SIM call without dialer confirmation. `ACTION_DIAL` needs no permission but only pre-fills the dialer. Calls go through the system Telecom stack (a managed ConnectionService). A self-managed ConnectionService is for VoIP only and cannot place SIM calls.

### Cited Findings
- `ACTION_CALL`: "there will be restrictions on which applications can initiate a call; most applications should use the ACTION_DIAL". It cannot call emergency numbers (use ACTION_DIAL). If the app targets M+ and declares `CALL_PHONE` but it is not granted, the action throws `SecurityException`. A `ROLE_DIALER` holder should use `TelecomManager.placeCall` instead. Call-forwarding MMI codes need the default or system dialer — [Intent reference](https://developer.android.com/reference/android/content/Intent)
- `TelecomManager.placeCall(Uri, Bundle)`:
  - It is "equivalent to placing an outgoing call using Intent.ACTION_CALL, except that the outgoing call will always be sent via the system telecom service".
  - "Placing a call via a managed ConnectionService requires permission: Manifest.permission.CALL_PHONE".
  - Emergency calls are allowed only for the default dialer or preloaded system dialer.
  - Self-managed ConnectionServices use it with `EXTRA_PHONE_ACCOUNT_HANDLE` and `MANAGE_OWN_CALLS`.
  - Extras include `EXTRA_PHONE_ACCOUNT_HANDLE` (pick a SIM) and `EXTRA_START_CALL_WITH_SPEAKERPHONE`.
  - "Notification.CallStyle notifications should be posted after the call is placed in order for the notification to be non-dismissible."
  - Source: [TelecomManager reference](https://developer.android.com/reference/android/telecom/TelecomManager)
- `ACTION_CHANGE_DEFAULT_DIALER` is "no longer supported since Q". Use `RoleManager.createRequestRoleIntent(ROLE_DIALER)` instead — [TelecomManager reference](https://developer.android.com/reference/android/telecom/TelecomManager)
- `TelecomManager.isInCall()` reports dialing, ringing, active or holding calls and requires `READ_PHONE_STATE`. `isInExternalCall()` was added in API 37 — [TelecomManager reference](https://developer.android.com/reference/android/telecom/TelecomManager)
- The `phoneCall` FGS type requires `FOREGROUND_SERVICE_PHONE_CALL` plus either `MANAGE_OWN_CALLS` in the manifest or the `ROLE_DIALER` role. Its stated purpose is to "Continue an ongoing call using the ConnectionService APIs". Apps targeting 15+ cannot launch it from `BOOT_COMPLETED` — [FGS types](https://developer.android.com/develop/background-work/services/fgs/service-types)

### Inferences
- Technically, an app with `CALL_PHONE` granted can call `placeCall()` from a background component (FCM handler, FGS, notification action) because no activity launch is needed. The in-call UI is shown by the system dialer (an OS-component exemption). I found no doc statement that it is blocked from the background or on the lock screen. Behaviour on a secure lock screen (the dialer may show over keyguard) should be device-tested. Fully unattended remote dialing is a policy and abuse risk (toll fraud); a user-tap confirmation is the safer pattern.
- Becoming the default dialer (`ROLE_DIALER` + `InCallService`) would give full call-state visibility and call-log rights, but means replacing the user's phone app. That is unrealistic for a CRM companion.

### Gaps
- No official doc found that explicitly states whether `placeCall`/`ACTION_CALL` from a background service is permitted or restricted on Android 15/16. This needs empirical testing.

## Android: observing call state and duration (READ_PHONE_STATE, precise state, call log and Play policy)

### Takeaway
A non-dialer app with `READ_PHONE_STATE` sees only IDLE, RINGING and OFFHOOK. OFFHOOK covers dialing, active and on-hold alike, so the app cannot tell when the far end answered. Precise call state needs `READ_PRECISE_PHONE_STATE` (privileged or carrier). Reading actual duration from the call log needs `READ_CALL_LOG`, which Play limits to default handlers plus listed exceptions. "Enterprise/CRM" is an exception only for the asterisked permissions in that row.

### Cited Findings
- `CALL_STATE_OFFHOOK`: "At least one call exists that is dialing, active, or on hold, and no calls are ringing or waiting." `CALL_STATE_RINGING` means a new incoming call is ringing or waiting — [TelephonyManager reference](https://developer.android.com/reference/android/telephony/TelephonyManager)
- `getCallState()` was deprecated in API 31 in favour of `getCallStateForSubscription()` (requires `READ_PHONE_STATE` or carrier privileges, plus `FEATURE_TELEPHONY_CALLING`), `TelephonyCallback.CallStateListener`, or `TelecomManager.isInCall()`. `PhoneStateListener.listen()` was deprecated in API 31 — [TelephonyManager reference](https://developer.android.com/reference/android/telephony/TelephonyManager)
- `TelephonyCallback.CallStateListener.onCallStateChanged(int)` (API 31) "Reports the state of Telephony (mobile) calls on the device for the registered subscription" (default subscription unless created with `createForSubscriptionId`). It "Requires Manifest.permission.READ_PHONE_STATE" and delivers IDLE, RINGING or OFFHOOK — [CallStateListener reference](https://developer.android.com/reference/android/telephony/TelephonyCallback.CallStateListener)
- Precise or radio-level telephony APIs in TelephonyManager require `READ_PRECISE_PHONE_STATE` or carrier privileges — [TelephonyManager reference](https://developer.android.com/reference/android/telephony/TelephonyManager) (seen on network-selection methods. The PreciseCallStateListener page did not render, so its permission is inferred to be the same.)
- Play SMS and Call Log policy:
  - The rule is "Only access Call Log or SMS permissions when your app falls within permitted uses", and only for critical core functionality.
  - Permitted uses are default SMS, Phone or Assistant handler.
  - The exceptions list includes:
    - Caller ID, spam detection or blocking (SMS, READ_CALL_LOG, PROCESS_OUTGOING_CALLS)
    - Connected device companions
    - Cross-device sync
    - Device automation
    - Backup and restore
    - **Enterprise/CRM/device management** — "For CRM use: only permissions marked with * are allowed"; corporate login is required for enterprise device management
    - Proxy calls
    - In-vehicle use
    - Call-based banking authentication
    - Government QoS reporting
    - Account verification via phone call, which will "no longer [be] permit[ted]" under READ_CALL_LOG effective January 27, 2027
  - Invalid uses include call recorders and remote device control.
  - Apps must submit the Permissions Declaration Form in Play Console, or "may be removed from Google Play".
  - Source: [Play Console Help: Use of SMS or Call Log permission groups](https://support.google.com/googleplay/android-developer/answer/10208820)

### Inferences
- Practical status reporting for a non-dialer CRM app: "dispatched" (the app called placeCall), "dialing/connected" (OFFHOOK seen), and "ended" (back to IDLE), with an elapsed time between OFFHOOK and IDLE that includes ring time. That time is not true talk time, and it cannot distinguish answered from unanswered or busy calls.
- Getting true answered/duration data requires `READ_CALL_LOG` (Play declaration under the Enterprise/CRM exception, if `READ_CALL_LOG` is asterisked for CRM) or distribution outside Play (managed Google Play private app or MDM). Alternatively, ask the user for an outcome.

### Gaps
- The fetched summary did not show which specific permissions carry the "*" in the Enterprise/CRM row (whether `READ_CALL_LOG` is included). The report writer should flag this as needing a direct check of the policy table.
- The PreciseCallStateListener permission was not directly confirmed (page rendered empty).

## Android: foreground services from FCM, lock state, Direct Boot, OEM killers

### Takeaway
A genuinely high-priority FCM message is an exemption that allows starting a foreground service from the background (Android 12+). Since Android 14 every FGS needs a declared type and Play declaration. For a CRM dialer helper, `shortService` (~3 min) or `specialUse` (Play-reviewed) fits better than `phoneCall`, which needs `MANAGE_OWN_CALLS` or the dialer role. OEM battery managers (Huawei, Xiaomi, OnePlus, Samsung rated worst) remain a major real-world failure source.

### Cited Findings
- Apps targeting Android 12 (API 31)+ can't start an FGS from the background except via exemptions. These include receiving a high-priority FCM message, but "If the message's priority is downgraded, your app cannot start a foreground service and attempting to start one results in a ForegroundServiceStartNotAllowedException". Check `RemoteMessage.getPriority() == PRIORITY_HIGH` first. Other exemptions:
  - user interaction with a notification
  - exact alarm
  - battery optimizations turned off
  - `SYSTEM_ALERT_WINDOW`, which for apps targeting 15+ also requires a currently visible overlay window
  - companion device
  - device or profile owner
  - Source: [Restrictions on starting FGS from background](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start)
- Since Android 14 (API 34) each FGS must declare a type, with the matching `FOREGROUND_SERVICE_*` permission.
  - `shortService`: no type permission, about 3 minutes, `onTimeout()` then ANR.
  - `specialUse`: `FOREGROUND_SERVICE_SPECIAL_USE`, with a `PROPERTY_SPECIAL_USE_FGS_SUBTYPE` justification reviewed in Play Console.
  - `dataSync`: cannot launch from `BOOT_COMPLETED` when targeting 15+.
  - Play Console requires an FGS-type declaration (App content page) for apps targeting 14+.
  - Source: [FGS types](https://developer.android.com/develop/background-work/services/fgs/service-types)
- `KeyguardManager.isDeviceLocked()`: the device is locked "when the user's apps are currently inaccessible and some form of lock screen authentication is required". "Swipe" does not count. `isKeyguardLocked()` returns true when the lock screen is showing, even if occluded (for example by the phone app during a call) — [KeyguardManager reference](https://developer.android.com/reference/android/app/KeyguardManager)
- OEM severity ranking (dontkillmyapp.com, undated): Huawei 5, Xiaomi 5, OnePlus 5, Samsung 5 ("especially after Android P update"), Oppo 4, Meizu 4, Asus 4, Vivo 3, realme 3, Motorola 3, Sony 2, AOSP/Pixel/Nokia 0 — [dontkillmyapp.com](https://dontkillmyapp.com/)

### Inferences
- Recommended Android flow:
  1. A high-priority FCM message arrives, and the app checks `getPriority()`.
  2. Post a heads-up notification "Call +1… for <CRM contact>" with a Call action. Optionally use FSI if permitted, and `CATEGORY_CALL`.
  3. Optionally enqueue an expedited WorkManager job to ACK the server.
  4. On user tap, call `placeCall` and start a `shortService` or `specialUse` FGS that registers a `TelephonyCallback`.
  5. Report OFFHOOK and IDLE timestamps to the server.
  6. Stop the FGS.
- After a reboot before first unlock, credential-encrypted storage (auth tokens) is unavailable. A non-Direct-Boot-aware app cannot run its normal code. Store the ack token in device-protected storage if acks are needed pre-unlock (not sourced this session).
- Onboarding should guide users to exempt the app from OEM battery optimization (per the dontkillmyapp vendor pages) and should detect a force-stop or missed push via server-side ack timeouts.

### Gaps
- Direct Boot / FCM-before-first-unlock behaviour and `setUnlockedDeviceRequired` Keystore semantics were not fetched (budget). Treat them as unverified.
- dontkillmyapp gives no date and no FCM-specific quantification.

## iOS: placing cellular calls, push options, call observation

### Takeaway
iOS gives third-party apps no way to place a cellular call without user confirmation. Opening a `tel:` URL always shows a system confirmation alert (iOS 10.3+), and only from a foreground app. PushKit VoIP pushes are only for VoIP calls reported to CallKit, and misuse gets the app terminated. CallKit features are blocked for China-storefront apps. The workable pattern is a regular APNs push, a time-sensitive notification, user tap, `tel:` confirmation, and `CXCallObserver` (which sees system calls, with connected/ended flags but no number) for coarse status.

### Cited Findings
- "When a user opens a URL with the tel scheme in a native app, iOS 10.3 and later displays an alert and requires user confirmation before dialing." URLs containing `*` or `#` are not dialed — [Apple URL Scheme Reference: Phone Links (archived)](https://developer.apple.com/library/archive/featuredarticles/iPhoneURLScheme_Reference/PhoneLinks/PhoneLinks.html)
- PushKit: "When linking against the iOS 13 SDK or later, your implementation of this method must report notifications of type voIP to the CallKit framework by calling the reportNewIncomingCall... method". "On iOS 13.0 and later, if you fail to report a call to CallKit, the system will terminate your app. Repeatedly failing to report calls may cause the system to stop delivering any more VoIP push notifications to your app. If you want to initiate a VoIP call without using CallKit, register for push notifications using the User Notifications framework instead of PushKit." — [pushRegistry(_:didReceiveIncomingPushWith:for:completion:)](https://developer.apple.com/documentation/pushkit/pkpushregistrydelegate/pushregistry(_:didreceiveincomingpushwith:for:completion:))
- Time Sensitive interruption level: "presents the notification immediately, lights up the screen, can play a sound, and breaks through system notification controls" such as Notification Summary and Focus. The user can turn it off — [UNNotificationInterruptionLevel.timeSensitive](https://developer.apple.com/documentation/usernotifications/unnotificationinterruptionlevel/timesensitive)
- `CXCallObserver`: "any app can create a new CXCallObserver object to be notified of any calls activity on the system" — [CXCallObserver](https://developer.apple.com/documentation/callkit/cxcallobserver). `CXCall` objects "are created by the telephony provider when an incoming call is received or an outgoing call is initiated", identified by UUID — [CXCall](https://developer.apple.com/documentation/callkit/cxcall). `hasConnected`: "A call is considered connected when both caller and callee can start communicating" — [CXCall.hasConnected](https://developer.apple.com/documentation/callkit/cxcall/hasconnected). CXCall properties are `uuid`, `isOutgoing`, `isOnHold`, `hasConnected` and `hasEnded`; no phone number is exposed (property list from the CXCall page structure; the page rendered via JSON abstract only).
- China: in May 2018 Apple told developers that, per MIIT, "This app cannot be approved with CallKit functionality active in China". Developers had to disable CallKit for the China storefront or withdraw — [9to5Mac (2018-05-19)](https://9to5mac.com/2018/05/19/apple-cracking-down-on-callkit-apps-in-china-app-store-due-to-government-regulation/); [TechCrunch (2018-05-25)](https://techcrunch.com/2018/05/25/googles-duo-and-ciscos-webex-teams-among-the-voip-apps-pulled-from-the-china-app-store); [Apple Developer Forums thread 103083](https://developer.apple.com/forums/thread/103083). No newer source confirms or lifts it.

### Inferences
- Recommended iOS flow:
  1. APNs alert push (time-sensitive, `thread-id`/category with a "Call" action, `apns-expiration` short).
  2. On tap, the app opens in the foreground and calls `UIApplication.open(tel:)`.
  3. The system confirmation alert appears and the user confirms.
  4. A `CXCallObserver` registered while the app is alive sees the outgoing call: `isOutgoing`, then `hasConnected` (answered), then `hasEnded`. The app computes approximate talk time from the connected-to-ended timestamps.
  5. Report to the server when the app is back in the foreground or via a background task. Background execution while the Phone app is frontmost is not guaranteed.
- `hasConnected` gives iOS a better "answered" signal than Android's non-privileged OFFHOOK. It cannot be tied to a number, so correlate by timing ("first outgoing CXCall after we opened tel:").
- Notification actions cannot open a `tel:` URL from the lock screen without the app coming to the foreground. Using a PushKit VoIP push for a SIM-call request is disallowed (it must report a CallKit VoIP call) and risks termination or push cut-off.
- There is no iOS API for the call history log.

### Gaps
- Whether `CXCallObserver` callbacks are delivered while the app is suspended during a cellular call was not confirmed from an Apple primary source.
- iOS 26-specific changes to tel: handling, CallKit, or the Phone app were not found.
- The App Review Guideline numbers relevant to VoIP/CallKit misuse were not fetched.
