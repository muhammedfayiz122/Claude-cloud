# Web-to-own-phone calling in major enterprise CRMs (state as of Nov 2026)

Scope note: about 20 tool calls (searches and fetches). The primary sources fetched in full were the Pipedrive web-to-mobile article, the HubSpot calling-tool and mobile-calling KB articles, the Close web-calling and mobile-app articles, and the Microsoft Learn Teams dialer article. Salesforce, Zoho, Freshworks and Zendesk Sell came only from search snippets, secondary sources and training knowledge, and are marked that way. Items marked "[training knowledge, unverified]" were NOT confirmed by a source in this session.

## Q1. Is there a true "click in web → my phone dials via the vendor mobile app" feature? (exact name and docs)

### Takeaway
Two of the eight products have a documented, first-party "web click → push to my phone → call on phone" feature:
- **Pipedrive "Web-to-mobile calling"**: the clearest reference implementation.
- **HubSpot "Call from HubSpot app"**: a device option in the calling tool.

HubSpot also offers **"Call from phone"**, a telephony bridge to your registered number. Microsoft Dynamics 365 (Teams dialer), Close, Freshworks and Zoho rely on a browser softphone or a provider/bridge model. Salesforce Sales Dialer is reported as retiring.

### Cited Findings
**Pipedrive (strongest match)**
- Feature name: "Web-to-mobile calling" — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling). The old blog URL `pipedrive.com/en/blog/web-to-mobile-calling` now 301-redirects to this KB article. The blog's original title was "You're Only a Few Clicks from a Cellphone Call Thanks to Pipedrive's New Web to Mobile Calling Feature" — [Pipedrive blog (search listing)](https://www.pipedrive.com/en/blog/web-to-mobile-calling).
- Flow on the web: click a contact's phone number in list or detail view. In the window that opens, keep the **Phone** tab selected, choose **"Start the call from Pipedrive mobile app"**, then click **"Start call"** — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- Flow on the phone: the mobile app shows a notification saying a call was started from the web app. Tapping it gives the option to continue the call on the phone — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- Requirements:
  - Mobile app installed and up to date.
  - Android 11+ or iOS 18+.
  - Mobile notifications enabled.
  - On Android, "calling must be enabled on the device".
  - Calls are billed to the user's normal phone bill because the phone's carrier line places them.
  - Source: [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- Plan availability is inconsistent: the original blog said all plans, while a later help snippet tied it to Advanced and higher plans. The fetched current article does not state a plan — [search summary of Pipedrive KB/blog](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- Related: Pipedrive "Caller" is a separate VoIP calling product — [Pipedrive KB: Caller](https://support.pipedrive.com/en/article/caller). [Pipedrive KB: How can I make calls](https://support.pipedrive.com/en/article/how-can-i-make-calls-in-pipedrive) lists the calling options.

**HubSpot**
- The calling tool's **Device** menu (in the call pop-up or the "Open call options" dialog) has three options — [HubSpot KB: Use the calling tool](https://knowledge.hubspot.com/calling/use-the-calling-tool):
  - **Call from browser**: uses the computer's audio.
  - **Call from phone**: "calls your registered phone number"; it "uses twice as many calling minutes" because it places two separate calls (a bridge).
  - **Call from HubSpot app**: "sends a push notification to your phone so you can start the call in the HubSpot mobile app".
- HubSpot's "Make calls from the HubSpot mobile app" article covers calls started on the phone, not the web-to-app handoff — [HubSpot KB: Make calls from the HubSpot mobile app](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app). It describes two methods:
  - Carrier: the phone's own line, with no recording.
  - HubSpot Calling: VoIP over data or Wi-Fi from a registered HubSpot number, with recording.
- HubSpot Calling requires a Sales Hub or Service Hub Starter, Professional or Enterprise subscription plus an assigned Sales or Service seat. Carrier calls work on any subscription — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- Registering a phone number for the "Call from phone" bridge: [HubSpot KB: register your phone number](https://knowledge.hubspot.com/calling-user-guide/how-to-register-your-phone-number-for-calling).

**Microsoft Dynamics 365 Sales**
- First-party calling is the **Microsoft Teams dialer**, opened from the phone icon in the upper-right **Calls** pane — [Microsoft Learn: Make and receive Teams calls in Dynamics 365](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams). The article is dated 2025-06-30 and was updated 2025-11-26.
- How a call starts and where it can come from — [Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams):
  - Clicking the phone icon on a phone field establishes the call in the dialer pane.
  - Calls can also start from list views (needs the admin setting "Call from view"), from Sales accelerator work items, and from the "Up next" widget.
- Limits — [Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams):
  - The dialer fails if third-party cookies are blocked.
  - It is not supported on custom entities.
- The article never mentions starting a call on the user's mobile or Teams mobile. It does note that a call answered "from another app, such as Teams desktop" is not counted as missed — [Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams).
- An older Microsoft page on the "Sales Hub dialer" was labelled preview — [Microsoft Learn: Sales Hub dialer](https://learn.microsoft.com/dynamics365/sales/make-receive-calls-sales-hub-dialer). The URL now resolves to the Teams dialer article.

**Close**
- Calling paths: built-in calling (desktop app, mobile app or web browser), or "Use another calling app", which hands a tel: link to another app on the computer — [Close: Initiating calls from the web app](https://help.close.com/docs/initiating-calls-from-the-web-app.md). The page documents no web-to-mobile handoff.
- The mobile app's call settings let the user:
  - pick which number to dial from, "including your cell phone number";
  - turn recording on or off;
  - turn on "Receive Calls on this Device".
  - Source: [Close: Close Mobile App](https://help.close.com/docs/close-mobile-app).
- With "Receive Calls on this Device" on, inbound calls to the user's Close number ring the cell phone and the desktop app (if active) — [Close: Close Mobile App](https://help.close.com/docs/close-mobile-app).
- The Power and Predictive dialers are not available on mobile — [Close: Close Mobile App](https://help.close.com/docs/close-mobile-app).
- Call forwarding sends missed calls, or calls that arrive while Close isn't open, to a cell phone. It works only for Internal (Close-provided) and BYOC numbers — [Close: Calling setup (mirror)](https://guide.close.io/docs/setting-up-calling). Mirrored doc versions disagree on the forwarding delay (~20 s vs ~25 s) — [Close calling setup mirror](https://close.helpscoutdocs.com/article/311-setup).

**Freshworks (Freshsales / Freshcaller, now Freshdesk Contact Center)**
- Freshcaller web calling uses a browser phone widget in the bottom-right corner. Agents must be online and the account needs credits — [Freshcaller support](https://support.freshcaller.com/support/solutions/articles/50000002981).
- The Freshcaller mobile app has a "mobile availability" switch for inbound and outbound calling with no browser login needed. Status in the app is only online or offline — [Freshworks: Freshcaller mobile app](https://freshworks.com/freshcaller-cloud-pbx/call-center-performance/freshcaller-mobile-app-library).
- In the Freshsales mobile app, tapping a number shows a choice between the phone dialer and the Freshcaller app. This requires the web Freshsales–Freshcaller integration — [Freshsales support 239340](https://support.freshsales.io/support/solutions/articles/239340-how-to-make-calls-using-freshcaller-from-within-the-freshsales-mobile-app-).
- Incoming calls can be forwarded to the agent's mobile phone — [Freshworks marketplace listing](https://www.freshworks.com/apps/freshdesk_contact_center_-_cloud_telephony_for_crm).
- No documented web-click-to-own-mobile handoff was found.

**Zoho CRM**
- PhoneBridge is Zoho's telephony framework for third-party providers. Outgoing calls use its click-to-call button, and incoming calls appear in PhoneBridge call pop-ups — [Zoho Voice: Integrations - Zoho Telephony](https://help.zoho.com/portal/en/kb/zoho-voice/integrations/articles/integrations-zoho-telephony).
- With Zoho Voice as the native provider, click-to-call and pop-ups need the **ZDialer** browser extension, and a ZDialer mobile app exists — [Zoho Voice: Zoho CRM telephony integration](https://www.zoho.com/voice/help/zoho-crm-telephony-integration.html); [Zoho Voice: native integration](https://www.zoho.com/voice/help/zoho-crm-native-integration.html).
- Some PhoneBridge providers implement a callback bridge. One provider describes its flow as "first try to reach the person you called and once he answers it will connect the call to you" — [Telebroad: Zoho PhoneBridge](https://helpdesk.telebroad.com/support/solutions/articles/4000171309-zoho-phonebridge). This is provider-specific behaviour.
- Zoho CRM mobile app push notifications cover activity reminders, emails, @mentions, meeting invites and Signals. No "call started on web" push is documented — [Zoho CRM iOS: Signals](https://help.zoho.com/portal/en/kb/crm/crm-mobile/apple/collaboration-and-communication/articles/signals-in-zoho-crm-ios-app).
- A long-running community thread asks for a click-to-call that rings the user's Android phone from Chrome, which suggests no native feature — [Zoho community thread](https://help.zoho.com/portal/en/community/topic/seeking-click-to-call-solution-for-zoho-crm-in-chrome-when-i-use-my-android-phone-and-bluetooth-ear-buds).

**Salesforce**
- Sales Dialer (formerly Lightning Dialer) is click-to-dial from phone fields in Lightning Experience, with a Dialer utility-bar item and WebRTC in the browser — [Trailhead: Get started with Lightning Dialer](https://trailhead.salesforce.com/content/learn/modules/lightning-dialer-basics/get-started-with-lightning-dialer).
- One secondary source says Salesforce Help marks Sales Dialer as scheduled for retirement, with no new features, and recommends moving to Salesforce Voice — [Aloware blog (secondary)](https://aloware.com/blog/what-salesforce-dialer-is-and-how-to-choose-one). This was not verified on help.salesforce.com in this session.
- No help.salesforce.com page on a "call from my phone" bridge or a web-to-Salesforce-mobile-app handoff was found in this session.

**Zendesk Sell**
- The searches surfaced only third-party CTI integrations (Aircall, ZIWO, CloudTalk) for click-to-call and auto-logging — [Aircall for Sell](https://www.zendesk.com/marketplace/apps/sell/237375/); [CloudTalk for Sell](https://www.zendesk.com/marketplace/apps/sell/280695/).
- CloudTalk logs answered calls as closed activities with direction, duration, agent and recording link — [CloudTalk for Sell](https://www.zendesk.com/marketplace/apps/sell/280695/).
- ZIWO for Sell works only in Chrome — [ZIWO for Sell](https://www.zendesk.com/marketplace/apps/sell/256437/).

### Inferences
- Two first-party patterns exist across the market:
  - **App push → native/carrier dial on the phone**: Pipedrive, and HubSpot's "Call from HubSpot app".
  - **Server-side bridge ("call-me")**: the server rings the user's registered phone, then the customer. Examples are HubSpot "Call from phone" (twice the minutes) and some Zoho PhoneBridge providers.
- Everyone else runs the call in a browser softphone, and the mobile app is a separate VoIP endpoint that rings together with the desktop app (Close, Freshcaller).
- [training knowledge, unverified] Salesforce Sales Dialer historically offered a personal setting to place calls using a phone number instead of the computer: Dialer rings your phone first, then connects the customer. This is a bridge, not a mobile-app push. Service Cloud Voice is an Amazon Connect- or partner-based softphone in the Lightning utility bar. Neither pushes a call to the Salesforce Mobile app.
- [training knowledge, unverified] Zendesk Sell's mobile app historically had built-in "call tracking": after a call from the app it prompts for an outcome, and on Android it can detect calls with known contacts. Zendesk has been de-emphasising Sell, so check whether it is still sold in late 2026.

### Gaps
- Salesforce: no help.salesforce.com confirmation of a "call from my phone" or bridge option, of Sales Dialer's retirement date, or of whether Service Cloud Voice works on the Salesforce Mobile app.
- Zendesk Sell: no first-party doc on mobile call tracking was retrieved; its current lifecycle status is also unknown.
- Dynamics 365: no doc found on handing a Dynamics web call to Teams mobile. Microsoft's separate "Digital Contact Center" / Customer Service voice channel was not researched.
- HubSpot: no dedicated KB page describing the "Call from HubSpot app" push flow end to end (taps, logging, failure handling).

## Q2. Delivery mechanism (push vs socket vs telephony bridge) and device pairing

### Takeaway
- Pipedrive and HubSpot ("Call from HubSpot app") use a mobile push notification to the vendor app, tied to the same user login.
- HubSpot "Call from phone" (and some Zoho PhoneBridge providers) use a server telephony bridge to a pre-registered phone number.
- No vendor documents which device rings when several devices are logged in.

### Cited Findings
- Pipedrive: "The mobile app sends a notification saying the call was started from the web app." Mobile notifications must be enabled — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- HubSpot "Call from HubSpot app" "sends a push notification to your phone" — [HubSpot KB](https://knowledge.hubspot.com/calling/use-the-calling-tool).
- HubSpot "Call from phone" "calls your registered phone number" and places two separate calls, using double minutes — [HubSpot KB](https://knowledge.hubspot.com/calling/use-the-calling-tool). Users must register the number first — [HubSpot KB: register number](https://knowledge.hubspot.com/calling-user-guide/how-to-register-your-phone-number-for-calling).
- Close and Freshcaller ring the mobile app as a VoIP endpoint at the same time as desktop. In Close, inbound calls go to the cell phone and to the desktop app "if it's active", and Group Number calls ring both — [Close Mobile App](https://help.close.com/docs/close-mobile-app). In Freshcaller, the "mobile availability" toggle makes the app an endpoint — [Freshcaller mobile app](https://freshworks.com/freshcaller-cloud-pbx/call-center-performance/freshcaller-mobile-app-library).

### Inferences
- Pipedrive's and HubSpot's push almost certainly uses FCM on Android and APNs on iOS. Neither vendor says so, but any native-app "push notification" works this way. Pairing is implicit: any device where the user is logged into the mobile app with notifications enabled.
- Pipedrive asks for the Android "calling" (CALL_PHONE) permission, and the call is billed to the user's carrier. Together these indicate the app hands off to the native/carrier dialer rather than VoIP.
- Pipedrive's iOS 18+ requirement suggests a recent iOS API (perhaps notification/CallKit or App Intents behaviour). This is speculative.
- With several devices logged in, the push probably goes to all registered devices, and the first tap wins. This is unconfirmed for any vendor.

### Gaps
- No vendor documents socket vs push, device selection with several phones, push payload contents, or expiry and timeout of the request.

## Q3. Failure states (locked phone, offline, app missing or logged out) and how the web informs the user

### Takeaway
Only Pipedrive documents a failure state. If the app isn't installed, calls can't be made through the feature and an error prompts the user to download the app. Nothing is documented for locked, offline or ignored-notification cases.

### Cited Findings
- Pipedrive: without the mobile app, calls can't be made via this feature, and the error prompts you to download the app — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- A third-party troubleshooting guide for a failed handoff suggests: confirm the mobile app is logged in, allow push notifications, and update both the web and mobile apps — [Noota guide (secondary)](https://www.noota.io/en/pipedrive-calling-guide).

### Inferences
- Pipedrive's "download the app" error implies the server knows whether the user has any registered mobile device (push token). Web can therefore detect "no device" up front, but not "device offline" or "notification ignored".
- A locked phone presumably shows the notification on the lock screen, with the dial step needing an unlock. Not documented.

### Gaps
- No vendor docs on timeout, retry, or web-UI status while waiting for the phone.

## Q4. Taps on the phone; auto-dial vs opening the dialer

### Takeaway
Pipedrive needs about two taps on the phone (the notification, then "continue the call") and three web actions. HubSpot mobile needs Call icon → choose method → Call when started on the phone. Neither documents fully automatic dialing.

### Cited Findings
- Pipedrive web: click the number → choose "Start the call from Pipedrive mobile app" → "Start call". Phone: tap the notification → choose to continue the call on the phone — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- HubSpot mobile (phone-initiated): tap the Call icon → choose carrier or HubSpot Calling (with a from-number for the latter) → tap Call. It warns if the contact opted out of communications — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- A HubSpot home-screen widget offers one-tap Call next to contacts or call tasks — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- Zoho community workaround: the phone icon puts the number on the phone's call screen, and the user presses SEND — [Zoho community](https://help.zoho.com/portal/en/community/topic/seeking-click-to-call-solution-for-zoho-crm-in-chrome-when-i-use-my-android-phone-and-bluetooth-ear-buds).

### Inferences
- The explicit confirmation tap on the phone is consistent with OS rules: iOS does not let an app place a carrier call without user confirmation (tel: prompts). Android CALL_PHONE allows direct dial, but vendors keep a confirmation step for safety and parity.

### Gaps
- Whether Pipedrive's "continue" tap opens the native dialer pre-filled or dials directly.

## Q5. Logging outcome and duration; answered detection; call-log permission

### Takeaway
- **Pipedrive**: shows a post-call logging prompt in the web app, so call status is reflected back in the web UI.
- **HubSpot mobile**: shows a Log Call dialog with auto-filled duration and an outcome picker. Android can optionally log calls made outside the app.
- **Dynamics 365**: auto-creates a phone-call activity; unanswered calls are skipped by default.
- **Close**: tel: link calls are logged without duration.

### Cited Findings
- Pipedrive: after the call ends, a call-log prompt appears automatically **in the web app**. The user can mark an existing not-done activity done (owner kept), or create a new done call activity owned by the caller, and can schedule a follow-up. No automatic duration or outcome field is mentioned — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- HubSpot mobile: after hang-up, a Log Call dialog shows the contact or company, date, time and **duration**. It also offers notes, call type, call outcome, associations and a follow-up task — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- HubSpot on Android only: a setting logs calls made outside the HubSpot app — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- HubSpot recording is not possible on carrier calls; HubSpot Calling mobile calls can be recorded — [HubSpot KB](https://knowledge.hubspot.com/calling/make-calls-from-the-hubspot-mobile-app).
- Dynamics 365 Teams dialer:
  - After the call, a phone-call activity is created on the record timeline and the Activities page.
  - Inbound calls auto-fill Call From and Regarding when the number resolves.
  - By default unanswered calls aren't recorded; the admin can enable "documenting call attempts".
  - Missed calls appear in the in-app notification bell.
  - Source: [Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams).
- Close: tel: link calls are logged automatically, but duration isn't captured and can be typed in manually — [Close](https://help.close.com/docs/initiating-calls-from-the-web-app.md).
- Third-party pattern (Salestrail): Android SIM call tracking reads the native call log to capture inbound and outbound calls automatically. On iOS, only calls made inside the vendor app are tracked — [Salestrail](https://www.salestrail.io/knowledge-base/how-can-sales-teams-track-mobile-call-activity).

### Inferences
- HubSpot's Android-only "log calls made outside the app" almost certainly relies on the READ_CALL_LOG / phone-state permissions, which iOS doesn't offer. That explains the platform split; the KB doesn't name the permission. Google Play restricts READ_CALL_LOG to approved use cases (default dialer, or exception categories such as CRM call logging), so vendors must declare it.
- Pipedrive's prompt appearing on the web "after the call ends" implies the mobile app reports call-end to the server, so the web sees the event. The doc doesn't say how end of call is detected: Android call state, or iOS CallKit's CXCallObserver.

### Gaps
- Pipedrive: whether duration or answered status is captured. HubSpot "Call from HubSpot app": whether the log prompt appears on web, phone or both.

## Q6. Web UI pattern

### Takeaway
- **Pipedrive**: a modal call-options window (Phone tab plus a start-from-mobile option), then a post-call logging prompt on the web.
- **HubSpot**: a call pop-up box / "calling remote" with a Device selector.
- **Dynamics 365**: a docked Calls pane (dial pad) opened from the top-right phone icon, with top-right incoming-call notifications.
- **Freshcaller**: a bottom-right phone widget.
- **Salesforce**: a Dialer utility-bar panel.

### Cited Findings
- Pipedrive: a window opens on number click, with a Phone tab and the "Start the call from Pipedrive mobile app" option — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- HubSpot: the Device menu sits in the call pop-up box or the "Open call options" dialog. The call window must stay open for browser calls from the calling remote — [HubSpot KB](https://knowledge.hubspot.com/calling/use-the-calling-tool).
- Dynamics 365: phone icon top-right → Calls pane with dial pad. Incoming calls show a top-right notification with up to 3 matching records — [Microsoft Learn](https://learn.microsoft.com/en-us/dynamics365/sales/call-using-microsoft-teams).
- Freshcaller: phone widget in the bottom-right corner of the browser — [Freshcaller support](https://support.freshcaller.com/support/solutions/articles/50000002981).
- Salesforce Sales Dialer: a Dialer item on the Utility Bar — [Trailhead](https://trailhead.salesforce.com/content/learn/modules/lightning-dialer-basics/get-started-with-lightning-dialer).

### Inferences
- Dock or utility-bar softphones (Salesforce, Dynamics, Freshcaller) are the norm for browser-audio calling. For a phone handoff, vendors use a lightweight modal plus a post-call logging prompt instead of a live in-call panel.

### Gaps
- No vendor documents a live "ringing on your phone… / in call 02:13" status panel on the web during a phone-handoff call.

## Q7. Privacy: what's shown in the notification and on the lock screen

### Takeaway
Not documented by any vendor. Close documents caller-ID content for calls ringing on mobile: the Close lead and contact name plus an indication that the call comes from Close.

### Cited Findings
- Pipedrive's notification says the call "was started from the web app"; the exact text and the contact details shown aren't documented — [Pipedrive KB](https://support.pipedrive.com/en/article/web-to-mobile-calling).
- Close inbound calls on mobile show the Lead Name and Contact Name from Close, with an indication that the call is from Close — [Close Mobile App](https://help.close.com/docs/close-mobile-app).

### Inferences
- Push notifications for a handoff likely include the contact name and/or number so the user can confirm. That content would be visible on the lock screen unless the OS hides previews.

### Gaps
- No vendor documents the notification payload or lock-screen redaction for web-to-mobile call handoff.
