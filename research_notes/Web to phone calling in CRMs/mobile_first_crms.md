# Mobile-first and SMB/emerging-market CRMs: placing a web click-to-call on the rep's own Android phone (SIM calling)

Research date: 2026-11-08. Sources are mostly vendor help docs and marketing pages. Third-party review sites (G2/Capterra) and Play Store "Data safety" pages were not fetched in depth because of budget, so the reliability evidence is thin (see Gaps). Two hosts failed to fetch: devweb.telecrm.in (blocked by the session network) and support.monday.com (403).

## 1. Which products actually do "click in web, SIM call on own phone," and the feature names

### Takeaway
LeadSquared, Kylas and TeleCRM clearly document the exact pattern: an Android app plus the phone's SIM, triggered from the web. NeoDove ("GSM calling triggered to mobile"), Callyzer (Chrome extension "Quick Call" plus the Android app) and monday Smart Call (desktop app triggers a call on the phone, but on a monday-bought business number) are close variants. Bitrix24, Odoo, Salesmate, Zoho Bigin and Privyr do not appear to offer a native web-to-own-SIM flow. They use SIP/VoIP, callbacks, or calling inside the mobile app only.

### Cited Findings
- **LeadSquared** (feature in place since Oct 2016): "You can initiate calls to leads from web application and the call will be place thru your mobile." Requirements: "an android phone with working SIM, internet access and LeadSquared Mobile App." "After the call, activity will be recorded in LeadSquared." — [LeadSquared news 19-Oct-16](https://help.leadsquared.com/news/19-oct-16-new-feature-use-leadsquared-to-initiate-track-call-to-leads-via-your-mobile-phone/)
- LeadSquared's current article is "Make Calls on Your Phone Using the Web Platform." It is "only supported on Android mobile phones." — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- LeadSquared also offers a separate cloud-telephony path (for example Exotel), where calls go out through the provider rather than the SIM. The admin can allow cloud calls only, or cloud calls plus carrier calls. — [Exotel LeadSquared Mobile docs](https://developer.exotel.com/docs/integrations/leadsquared-mobile); [LeadSquared telephony tag](https://help.leadsquared.com/tag/telephony/)
- **Kylas**: help article "How to make outbound call from Kylas web application via your mobile phone." Clicking the call icon on a Lead or Contact means "A call to the Lead's or Contact's number will be placed from your mobile phone." Available on all plans. — [Kylas KB](https://support.kylas.io/portal/en/kb/articles/how-to-make-outbound-call-from-kylas-web-application-via-your-mobile-phone)
- Kylas has two Android apps: "Kylas Sales CRM" and "Kylas Dialer" (package `io.kylas.dialer`). The Dialer handles call log sync and recordings. — [Kylas call-log sync KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- **TeleCRM**: "Click any lead's number in the browser — dials on mobile instantly." — [TeleCRM features (search snippet)](https://devweb.telecrm.in/features/call-management). Also: "The CRM mobile app initiates the call through the phone's native dialler, then tracks it via app permissions," and "The caller ID is the rep's mobile number unless masking is configured." — [TeleCRM blog: Click-to-Call CRM 2026](https://telecrm.in/blog/click-to-call-crm/)
- **NeoDove**: its web dialer places calls from the browser "using Voice over Internet Protocol (VOIP) or GSM calling triggered to mobile." — [NeoDove Web FAQ](https://docs.neodove.com/neodove-web-application/faqs-web-application)
- **Callyzer**: the Chrome extension "Quick Call by Callyzer" ("Make calls directly from your Chrome browser") is linked to the Callyzer Biz Android app from the app's "More" section. Users can right-click a number and choose "Call with Quick Call." Roughly 4–5k users. — [ExtensionAuditor scan](https://extensionauditor.com/scan/quick-call-by-callyzer-lpggagjnphkfelodjnhbhkkpbgmkpiop). The Bitrix24 marketplace app says the extension turns phone numbers in the browser into links that call through your mobile and syncs the log and recording to Bitrix24. — [Bitrix24 Market: Callyzer by SarasUk](https://www.bitrix24.com/apps/app/sarasuk_tech_pvt_ltd.callyzer_by_sarasuk/)
- **monday sales CRM, "monday Smart Call"**: native calling on a business number bought inside monday. Browser calling is not supported. A call triggered from the desktop app starts on the phone (monday mobile app). Calls to numbers outside the monday line are not recorded or logged. — [monday support: Get started with Smart Call (search-result summary; page returned 403 to fetch)](https://support.monday.com/hc/en-us/articles/35893698534674-Get-started-with-monday-Smart-Call). Note: this rings the monday app over VoIP on a virtual number, not the SIM. Inferred from "business number bought inside the platform."
- **Bitrix24**: "If you are calling from a browser or the Bitrix24 Messenger application, the call goes through the phone by default." Blue button means the call goes from the phone; green means browser or Messenger. The page links to SIP-phone and Zoiper setup, so "phone" here means a connected SIP/desk phone, not the mobile SIM. — [Bitrix24 Helpdesk 18537686](https://helpdesk.bitrix24.com/open/18537686). The mobile app offers "Call" (mobile operator) versus "Call using Bitrix24" (telephony), started on the phone itself. — [Bitrix24 Helpdesk 17590798](https://helpdesk.bitrix24.com/open/17590798)
- **Odoo VoIP**: on mobile, Odoo asks "VOIP or Phone" when placing a call, with a "remember" checkbox. That is a choice made on the device, not a push from the web. The 17.4 docs say the Odoo Android and iOS apps "are no longer being maintained" and recommend a SIP app such as Zoiper for mobile users. — [Odoo 17.4 docs: Devices and integrations](https://www.odoo.com/documentation/saas-17.4/applications/productivity/voip/devices_integrations.html); [Odoo 18.4 docs](https://www.odoo.com/documentation/saas-18.4/applications/productivity/voip/devices_integrations.html)
- **Salesmate**: the Android app logs outgoing calls only when they are made from the Salesmate mobile app. Built-in calling uses virtual numbers bought in the web app. No web-to-SIM push was found. — [Salesmate blog: call tracking on iOS/Android](https://www.salesmate.io/blog/seamless-call-tracking-now-available-ios-android-apps); [Salesmate mobile calling prerequisites](https://support.salesmate.io/hc/en-us/articles/360015321472-Pre-requisites-of-calling-in-the-Salesmate-Mobile-App)
- **Zoho Bigin**: the Android app (v2.0.0+) supports built-in telephony, RingCentral and Zoho Voice for calls from the app. Web click-to-call goes through Zoho Voice or other telephony. No web-to-SIM push was found. — [Zoho community: Make and receive calls from Bigin's Android app](https://help.zoho.com/portal/en/community/topic/make-and-receive-calls-from-bigins-android-app); [Zoho Voice integrations](https://help.zoho.com/portal/en/kb/zoho-voice/integrations/articles/integrations-zoho-telephony)
- **Privyr**: mobile-first, with one-tap calls from the phone. Bulk calling starts with "Open your Privyr mobile app." No evidence of web-triggered phone calls. — [Privyr blog](https://www.privyr.com/blog/?p=9086)
- **Runo**: a SIM-based call-management CRM on Android, iOS and web, with "Auto dial & Click to Dial" in the app. Web-to-mobile triggering was not confirmed. — [Runo](https://runo.in/call-management-crm); [G2 Runo](https://g2.com/products/runo-call-management-crm/discuss)
- **Salestrail**: a call-tracking overlay that logs SIM and WhatsApp calls into CRMs such as HubSpot. It is not a web-to-phone dialer. — [HubSpot marketplace: Salestrail](https://ecosystem.hubspot.com/marketplace/apps/salestrail-for-hubspot-273060)

### Inferences
- In this market, the web-to-own-SIM pattern is basically an Indian SMB-CRM feature (LeadSquared, Kylas, TeleCRM, NeoDove, Callyzer). Global SMB CRMs (Salesmate, Bigin, monday, Odoo, Bitrix24) route web clicks to VoIP, SIP or virtual numbers instead.
- LeadSquared's implementation looks like a generic notification mechanism ("Nudges") reused for call routing rather than a purpose-built call channel. That explains its admin-heavy setup (see section 2).

### Gaps
- Freshsales (India) "call via phone": not researched. Freshworks' "call via phone" is generally a telephony callback to a forwarded number. Unverified here.
- Interakt (a WhatsApp tool) appears irrelevant to SIM calling. Not researched.
- monday Smart Call details could not be fetched directly (403).

## 2. Delivery mechanism (push/FCM, persistent connection, polling) and device pairing

### Takeaway
LeadSquared is the only vendor that documents the mechanism. The web action calls an API that sends a silent push notification ("nudge") to a server-registered target device. The device is registered at mobile-app login, and re-logging in re-registers it. Kylas pairs implicitly by logging into the same account on web and mobile and uses a system-overlay pop-up, which also implies push. No vendor documents how it chooses between multiple devices, which suggests a "last registered device wins" model (inference).

### Cited Findings
- LeadSquared: the web action "sends a call nudge (a mobile notification) to the user's phone through the Nudges Connector." "The notification that the call is being placed is silent." — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- LeadSquared setup is admin-built. It needs the Custom Lead and List Actions, Call and SMS Tracker, and Nudges connectors. It also needs an x-auth-token from support, and a nudge template with action type "Call Routing." The admin then creates a Lead Grid Row Action of type "Call an API" (POST) whose URL includes the template ID, ProspectID and UserId. — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- LeadSquared error: "No Target Device Retrieved.Cannot Call" appears when the device is not registered. The fix is to log out and back into the mobile app, which re-registers the device so it can receive the silent push. — [LeadSquared help ?p=8755 (user comments / staff replies)](https://help.leadsquared.com/?p=8755)
- Kylas pairing: "Keep the Kylas sales CRM mobile app installed" and log in to the same Kylas account on both web and mobile. No other pairing step. — [Kylas KB](https://support.kylas.io/portal/en/kb/articles/how-to-make-outbound-call-from-kylas-web-application-via-your-mobile-phone)
- Callyzer pairing: the Chrome extension is linked from the Android app's "More" section, which may be a code or QR link. The exact method is unconfirmed. — [ExtensionAuditor](https://extensionauditor.com/scan/quick-call-by-callyzer-lpggagjnphkfelodjnhbhkkpbgmkpiop)

### Inferences
- LeadSquared ties routing to a UserId, so the server keeps one target device per user, refreshed at login. A second device logging in probably replaces the first. The error text says "Target Device" in the singular. This is inference.
- Kylas's statement that the pop-up works "even when the app is killed" implies a high-priority FCM data message that wakes the app and draws an overlay. Kylas does not document this. It is inferred.
- No vendor documents a persistent socket or polling. On Android, FCM is the only practical way to wake a killed app, so it is almost certainly FCM in all cases (inference).

### Gaps
- Multi-device routing rules, QR pairing and per-device registration UIs: not documented for any vendor found.

## 3. Web feedback when the phone is offline, locked, killed or logged out

### Takeaway
The vendors give very little feedback. LeadSquared shows an error only when no device is registered, plus a reference ID for support. None documents an online/heartbeat indicator, a delivery receipt or a "phone ringing" state in the web UI. Instead, they push the burden onto OEM battery and autostart settings.

### Cited Findings
- LeadSquared shows "No Target Device Retrieved.Cannot Call" when there is no registered device. If a call is not placed, the user should send the on-screen reference ID to support@leadsquared.com. You "must be logged into your LeadSquared Mobile Application while the call is being placed," and Autostart must be enabled. — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- Kylas: enable "Display over other apps" or "Show on top," and on Xiaomi also "Display pop up window while running in background." With these, "you will start receiving the call pop up even when the app is killed or running in background." — [Kylas KB](https://support.kylas.io/portal/en/kb/articles/how-to-make-outbound-call-from-kylas-web-application-via-your-mobile-phone)
- Salestrail, the closest documented evidence of reliability failure modes: battery optimization is "the most common cause" of missed logs, and "Samsung, Xiaomi, Huawei, and OPPO in particular have additional battery management layers." Android may pause the app after about 6–8 hours, and "When Salestrail is paused by Android, call logging will stop until the app is reopened." On dual-SIM phones, "If no SIM is selected, no calls will be tracked." Truecaller as the default dialer is incompatible. Sync over mobile data can lag "a short delay." The admin dashboard shows per-user "App installed" and "Permissions" status in green. — [Salestrail KB: calls not logged](https://www.salestrail.io/knowledge-base/calls-not-logged-in-the-salestrail-app-causes-and-solutions)
- Kylas Dialer shows the sync status with date and time in the app's "Call history." — [Kylas call-log sync KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)

### Inferences
- Salestrail's admin view of "App installed" and "Permissions" health per user is the closest thing to a device-health indicator. It suggests the app reports permission state to the server periodically.
- Our product could stand out by adding a delivery ACK, a "phone ringing / dialing" state, and a last-seen heartbeat, since the documented competitors lack them.

### Gaps
- No vendor documentation was found on lock-screen behavior, offline queuing or delivery timeouts.

## 4. Taps on the phone, and auto-dial (CALL_PHONE) versus opening the dialer, plus the default-dialer role

### Takeaway
LeadSquared needs one tap: the notification opens the dialer pre-filled, and the user taps Call. Kylas shows an overlay pop-up and requests CALL_PHONE ("make and receive calls"), and its Dialer app offers to become the default phone app (user can decline). TeleCRM says it uses "the phone's native dialler." Fully automatic dialing without a tap is not documented by anyone.

### Cited Findings
- LeadSquared: tapping the nudge opens the phone's dialer with the number filled in. "You must tap the call button to place the call." Device permissions needed: "Make a Call, Read Contact and Read Call History." — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- Kylas Dialer: at first launch it shows a prompt to become the default phone app (accept or decline). It requests permissions for reading call logs, making and receiving calls, and file access. — [Kylas call-log sync KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- TeleCRM: "initiates the call through the phone's native dialler." — [TeleCRM blog](https://telecrm.in/blog/click-to-call-crm/)
- The TeleCRM blog warns that a real click-to-call CRM should not rely on "just a tel: link." — [TeleCRM blog](https://telecrm.in/blog/click-to-call-crm/)

### Inferences
- Since Android 10, apps cannot start activities from the background, so a silent push cannot directly start a call. A tap on a notification or an overlay (SYSTEM_ALERT_WINDOW, which Kylas requests) is the standard workaround. This likely explains LeadSquared's notification tap and Kylas's "display over other apps" requirement. This is inference from Android platform rules, not stated by the vendors.
- Kylas offering the default-dialer role (optional) is consistent with using it to get reliable call state and call-log access without a Play exception. That rationale is inferred.

### Gaps
- Exact tap count for Kylas, TeleCRM and Callyzer: not documented.

## 5. Detecting call status and duration, and the recording approach

### Takeaway
The vendors detect calls by reading the call log after the call, plus phone-state events for in-call pop-ups. Recording is not done by the app. Apps pick up the OEM's built-in call-recorder files from a folder the user configures, so recording only works on devices with native recording (Samsung and Xiaomi mentioned). "Connected" status comes from the call log's duration being greater than 0, so it inherits the call log's inaccuracies (inference).

### Cited Findings
- Kylas: the Dialer reads call logs from the device and syncs calls made to Leads and Contacts. "Kylas caller will start fetching call recording after each call." The user sets "set recording path" to the OEM recording folder. It "works best on Samsung and Xiaomi devices," and devices without built-in recording "may face issues." During a call, a pop-up shows the matching Lead or Contact with "View Lead" and "Add Lead" actions. — [Kylas call-log sync KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- Salestrail: "does not record audio — it only detects and attaches system-generated recordings." It needs File Storage/Read Media. Android 8+ is required for tracking and Android 9+ for recording. — [Salestrail Play listing via search; Salestrail install KB](https://www.salestrail.io/knowledge-base/installing-the-salestrail-app-on-android). It also needs the Phone, Call Logs and Contacts permissions: "Without these three permissions, the app cannot detect or log any calls." — [Salestrail KB](https://www.salestrail.io/knowledge-base/calls-not-logged-in-the-salestrail-app-causes-and-solutions)
- LeadSquared: recording is Android-only and "device dependent." It needs a separate "Call and SMS tracker" app. Admin per-role settings for Track Calls, Track SMS and Record Calls can be "No Calls" or "All Calls," with an "Override settings on device" option. Recordings are stored as mp4 on the lead's activity. — [LeadSquared help ?p=9296](https://help.leadsquared.com/?p=9296)
- LeadSquared on iOS (contrast): the app must be in the foreground for the whole call, or the duration will be wrong ("a one-minute call can show as six minutes"). Dial-pad and inbound calls cannot be tracked. — [LeadSquared help ?p=9296](https://help.leadsquared.com/?p=9296)
- TeleCRM: "All calls are auto-logged with time, call duration and status" (connected, unanswered or missed). "Recording and logging depend on the device and Android version." — [TeleCRM blog](https://telecrm.in/blog/click-to-call-crm/)
- NeoDove: "not possible to record calls because of Google's guidelines." Recording is available only with NeoDove IVR (cloud). — [NeoDove Web FAQ](https://docs.neodove.com/neodove-web-application/faqs-web-application)

### Inferences
- The iOS limitation shows that iOS has no call-log access. Only Android supports the "call log after the call" model.
- A separate "Call and SMS tracker" app (LeadSquared) and a separate "Dialer" app (Kylas) suggest vendors keep the sensitive-permission app apart from the main CRM app. That is plausibly to limit the Play policy review scope (inferred).

### Gaps
- No vendor documents how it tells "answered" from "ringing, no answer" beyond the call-log duration. Accuracy figures were not found.

## 6. Google Play SMS & Call Log policy handling

### Takeaway
Google Play currently has an explicit permitted exception, "Enterprise archive, CRM, and/or enterprise device management." For CRM it allows READ_CALL_LOG and PROCESS_OUTGOING_CALLS, but not WRITE_CALL_LOG. Vendors appear to rely on it, since Kylas Dialer and Salestrail ship on Play with call-log access. Kylas additionally offers the default-dialer role. "Call recorder" is explicitly an invalid use case, which is why apps attach OEM recordings instead of recording themselves.

### Cited Findings
- Google Play Help, "Use of SMS or Call Log permission groups," lists the exception "Enterprise archive, CRM, and/or enterprise device management." For CRM, only the asterisked permissions READ_CALL_LOG and PROCESS_OUTGOING_CALLS are allowed. Exceptions are "Subject to Google Play review and approval" and apply only if "there's currently no alternative method." "Call recorder" is listed as an invalid use case. Other relevant exceptions are "Cross-device synchronization" (READ_CALL_LOG) and "Connected device companion apps." The page also says account verification via phone call will no longer be permitted from January 27, 2027. — [Google Play Console Help 10208820](https://support.google.com/googleplay/android-developer/answer/10208820)
- Kylas Dialer is distributed via Google Play or QR code, with no APK mentioned, and requests call-log read permission. — [Kylas call-log sync KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- Salestrail is distributed on Play as "Salestrail - Call log & analysis." A separate "Salestrail Recorder APK" exists that is "used only for recording — it cannot track calls on its own." — [Salestrail KB](https://www.salestrail.io/knowledge-base/calls-not-logged-in-the-salestrail-app-causes-and-solutions)
- NeoDove attributes not recording calls to "Google's guidelines." — [NeoDove FAQ](https://docs.neodove.com/neodove-web-application/faqs-web-application)

### Inferences
- Salestrail's off-Play "Recorder APK" is a direct example of the side-load strategy for features Play forbids (recording). Tracking stays on Play under the CRM exception.
- Our app should declare the CRM exception for READ_CALL_LOG only, avoid WRITE_CALL_LOG and in-app recording on the Play build, and consider an optional default-dialer mode like Kylas.

### Gaps
- Play Store "Data safety" sections for LeadSquared, Kylas, TeleCRM and Callyzer were not fetched.

## 7. Web UI during and after the call, and privacy/compliance

### Takeaway
The web side is minimal in the documented flows: an activity is posted after the call. The rich UI (lead pop-up, add lead, disposition) is on the phone. Privacy controls are mostly admin toggles for tracking and recording scope, plus office-hours and SIM-selection limits on what gets tracked (Salestrail).

### Cited Findings
- LeadSquared: after the call, an activity is posted to the lead. No in-call web panel is described. — [LeadSquared help ?p=8755](https://help.leadsquared.com/?p=8755)
- Kylas: the in-call pop-up on the phone shows the matched Lead or Contact, with "View Lead" and "Add Lead/Add Contact." — [Kylas KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- LeadSquared's recording access is limited to the lead owner, the reporting or sales-group manager, and users the lead is shared with. Admins can force tracking settings over device settings. — [LeadSquared help ?p=9296](https://help.leadsquared.com/?p=9296)
- Salestrail: calls outside the configured office hours are not tracked and go to an "Untracked" tab. SIM selection limits tracking to the chosen SIM (work versus personal). — [Salestrail KB](https://www.salestrail.io/knowledge-base/calls-not-logged-in-the-salestrail-app-causes-and-solutions)
- Kylas logs only calls to numbers that match a Lead or Contact. — [Kylas KB](https://support.kylas.io/portal/en/kb/articles/how-to-sync-the-mobile-phone-call-logs-with-kylas)
- monday Smart Call uses a business number so the rep's personal number is not exposed. — [monday support (search summary)](https://support.monday.com/hc/en-us/articles/35893698534674-Get-started-with-monday-Smart-Call)

### Inferences
- Privacy patterns worth copying: log only CRM-matched numbers, work-hours windows, per-SIM selection on dual-SIM phones, and admin-enforced policy with visible user status.

### Gaps
- No documented live web call widget, call-state indicator or auto-opened post-call form was found for LeadSquared, Kylas or TeleCRM web. They may exist, but are undocumented in the sources reached.
- G2/Capterra reliability reviews were not collected.
