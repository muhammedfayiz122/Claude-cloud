# Cloud telephony and OS-level handoff: how a desktop or web trigger places a call on the user's phone

Scope: Aircall, Dialpad, RingCentral, JustCall, CallHippo, Microsoft Phone Link, Apple Continuity, Google Phone Hub and Chrome click-to-call, Samsung "Call & text on other devices". Research date 2026-11-08. About 17 searches and fetches. Many vendor help pages could only be seen as search snippets, and some fetches returned only partial pages; these limits are noted where they apply.

## Delivery mechanism: how the call actually reaches the phone (VoIP vs SIM vs callback/bridge)

### Takeaway
Three architectures exist, and none of them is "the desktop tells the phone's native dialer to dial":
1. **VoIP/WebRTC softphone.** The web or extension dialer is itself the endpoint (Aircall, Dialpad, JustCall, CallHippo). The call never touches the user's SIM.
2. **Server-side callback/bridge.** RingCentral RingOut, and Aircall "Forward to external number" for inbound. The cloud PBX calls the user's phone over the PSTN first and then bridges in the customer. This works with any phone and no app, even when the app is closed.
3. **OS-level relay of the phone's own SIM call.** Phone Link, Apple Continuity, Samsung, Phone Hub. The paired phone places a real cellular call, and audio is relayed to the computer over Bluetooth HFP or Wi-Fi. Proximity and pairing are required.

Chrome's removed click-to-call was a fourth, lighter pattern: an FCM push message to the user's own signed-in Android Chrome, which opened the native dialer pre-filled.

### Cited Findings
**Callback/bridge (RingCentral RingOut)**
- RingOut: "RingCentral calls your RingOut number first", the user answers on their own device, "and press 1 if prompted", then RingCentral connects the other party and shows the RingCentral number as caller ID, so the personal number stays hidden — [RingCentral support: Managing RingOut](https://support.ringcentral.com/app/phone/desktop-web/enabling-using-ringout-ringcentral-app-desktop-web.html)
- Setup on desktop and web: Settings > Phone > Outgoing > RingOut toggle > enter phone number. On mobile, multiple RingOut numbers can be added. "Prompt me to press 1 before connecting calls" is an optional checkbox on desktop/web and in the Admin Portal — [RingCentral support](https://support.ringcentral.com/app/phone/desktop-web/enabling-using-ringout-ringcentral-app-desktop-web.html)
- Positioned for hotel, courtesy, or mobile phones without a DigitalLine. It is billed as an inbound leg — [RingCentral intro to RingOut](https://support.ringcentral.com/au/en/app/phone/desktop-web/intro-ringout.html); [RingCentral click-to-call overview](https://www.ringcentral.com/ca/en/office/features/click-to-call/overview.html)
- Known pitfalls reported by community users: the second leg can connect before the user picks up the first, so the customer hears greetings or voicemail, and configuring the first leg to ring both a desk phone and a softphone is not straightforward — [RingCentral community: first leg ringing both](https://community.ringcentral.com/developer-platform-apis-integrations-5/how-can-you-configure-the-first-leg-of-ringout-call-to-ring-both-desk-phone-and-softphone-9155); [RingCentral community: RingOut flow](https://community.ringcentral.com/developer-platform-apis-integrations-5/what-is-the-flow-of-creating-ringout-for-users-714)

**Inbound forwarding to a mobile (Aircall)**
- Aircall "Forward to external number": calls keep following Aircall's distribution and ring times. If the user is logged into Aircall Workspace with forwarding on, "your phone app and your forwarding number will ring simultaneously". There is no ring-one-first option — [Aircall support 10375354624413](https://support.aircall.io/en-gb/articles/10375354624413) (seen via search snippet)
- Aircall warns that if the mobile app or a SIP device is installed alongside forwarding, you must either turn off forwarding or log out of and uninstall the mobile app. This implies conflicts when both paths are active — [Aircall support](https://support.aircall.io/en-gb/articles/10375354624413) (snippet)
- A third-party integrator reports that Aircall's external-number forward asks the person to "press 1", a whisper/confirm step that an automated receptionist can't complete — [ElevenLabs Aircall integration doc](https://elevenlabs.io/docs/reception-ai/integrations/aircall)

**VoIP softphones in the browser**
- The Aircall extension detects phone numbers on a page, and clicking one places the call in Aircall Workspace, the desktop/web app. It runs in Chrome and Edge. Power Dialer needs the Professional plan and cannot run on the Aircall mobile app — [Aircall support 10375354868893](https://support.aircall.io/en-gb/articles/10375354868893); [Aircall support 23996034990493](https://support.aircall.io/en-gb/articles/23996034990493) (snippets)
- Aircall marketing says click-to-dial needs both the CTI and the Chrome extension — [Aircall click-to-dial](https://aircall.io/en-gb/call-center-software-features/click-to-dial/)
- The Dialpad extension highlights numbers for click-to-call or click-to-message. Calls route through the Dialpad desktop app (Mac/Windows), the web app in Chrome, or the ChromeOS app. A Company Admin must enable it. There is an optional "Confirm phone number before placing call" setting and a step to "select your preferred Dialpad device" — [Dialpad help: Dialpad Extension](https://help.dialpad.com/docs/dialpad-extension.md); [Dialpad help: Click-to-Call with Chrome](https://help.dialpad.com/hc/en-us/articles/211463286-Enable-Click-to-Call-with-Chrome) (snippets)
- CallHippo extension: if the CallHippo desktop app is installed, users can choose to place calls through it, otherwise calls go directly from Chrome. The user must stay logged into CallHippo in the browser — [CallHippo help: Click to Call](https://callhippo.ladesk.com/871505-Click-to-Call); [CallHippo help: installing extension](https://callhippo.ladesk.com/247633-Installing-the-CallHippo-Click-to-Call-chrome-extension) (snippets)
- JustCall: the pop-up dialer lets reps call, text, and answer incoming calls from any tab, and adds call/text icons inside HubSpot, Salesforce, Pipedrive, Zoho, and others. Troubleshooting asks the user to enable "Allow JustCall to add click to call/text icons wherever possible", grant Chrome notification permission, and select audio devices — [JustCall help: getting started](https://help.justcall.io/en/articles/3933637-getting-started-with-justcall-chrome-extension); [JustCall help: click to call on any webpage](https://help.justcall.io/en/articles/5210632-how-to-use-click-to-call-on-any-webpage-with-the-justcall-chrome-extension) (snippets)

**OS-level SIM relay**
- Phone Link calls require a Bluetooth connection between the phone and the PC. Android 10+, iOS 15+, Windows 10 (May 2019 update+) or 11 — [Microsoft: Setting up calls in Phone Link](https://support.microsoft.com/en-us/help/4531605/setting-up-and-using-calls)
- The PC's Bluetooth adapter must support Hands-Free Profile (HFP), otherwise calling is unavailable (community answer) — [Microsoft Q&A](https://learn.microsoft.com/answers/a/12449752) (snippet)
- Apple: iPhone calls on Mac need the same Apple Account and FaceTime sign-in on both devices, both on the same Wi-Fi, within about 10 m (30 ft), plus iPhone Settings > Apps > Phone > Calls on Other Devices > allow, and pick the Mac. With Dual SIM, the default voice line is used — [Apple Mac User Guide](https://support.apple.com/guide/mac-help/receive-calls-text-messages-mac-mchl1b152152/mac)
- The relaying iPhone needs an activated carrier plan — [Apple support 108046](https://support.apple.com/en-us/108046)
- Samsung: same Samsung account and the feature turned on for both devices. Samsung US says calls need the same Wi-Fi network, while messages work either way. Samsung AU says there is "no distance restriction" if both are on the same account. There is a "Wi-Fi only / Wi-Fi and mobile networks" option. Same country or region is required, and some carriers (Verizon, AT&T per a community post) are unsupported — [Samsung US](https://www.samsung.com/us/support/answer/ANS00083152/); [Samsung AU](https://www.samsung.com/au/support/mobile-devices/using-call-text-on-other-devices/); [Samsung community](https://us.community.samsung.com/t5/Samsung-Apps-and-Services/Feedback-Call-and-Text-on-Other-Devices-Phone-Calls-policy/m-p/2938270/highlight/true). The sources conflict on Wi-Fi vs distance.

**Chrome click-to-call (push-to-dialer)**
- Chromium's `chrome/browser/sharing` holds features "for sharing data between one user's Chrome instances" such as click-to-call and shared clipboard, backed by Firebase Cloud Messaging, optionally with VAPID. The newer `components/sharing_message` README says "FCM or Chime" — [Chromium sharing README](https://chromium.googlesource.com/chromium/src/+/main/chrome/browser/sharing/README.md); [components/sharing_message](https://chromium.googlesource.com/chromium/src.git/+/main/components/sharing_message)
- `sharing_message.proto` has a oneof payload that includes `ClickToCallMessage`. `RecipientInfo` holds the target device's FCM registration token plus keys for encrypted delivery — [sharing_message.proto](https://chromium.googlesource.com/chromium/src/+/689912289c/chrome/browser/sharing/proto/sharing_message.proto)

### Inferences
- For a CRM that wants the call to go out on the user's own SIM, the only vendor-neutral, app-closed-safe option is the **callback/bridge**, and it uses a cloud number as caller ID, not the user's SIM identity. True SIM calling triggered from the web needs either an OS relay, which a web app can't drive, or an app on the phone that receives a push (the Chrome click-to-call model).
- The RingOut "press 1" step exists to stop the bridge connecting the customer to the user's voicemail. Any callback design needs an equivalent answer-confirmation step.

### Gaps
- I couldn't confirm that Dialpad, JustCall, or CallHippo offer a RingOut-style "call my mobile first" mode for outbound calls from the extension. These vendors do offer mobile apps and forwarding, but no source tied that to the extension's click-to-call.
- I couldn't fetch the Chromium sender/handler source (`sharing_fcm_sender.cc`, `sharing_fcm_handler.cc`), so ack and timeout behavior is unverified.

## Pairing and device registry

### Takeaway
OS features pair through a shared account plus local radio pairing (Bluetooth PIN, or the same Wi-Fi). Chrome used the account-synced device list. VoIP vendors' "registry" is simply which of the user's logged-in endpoints are active (web, desktop, mobile app, SIP desk phone, forwarded number).

### Cited Findings
- Phone Link calls setup: PC > Calls > Get Started. Phone Link tries to connect automatically, asks for app permissions, makes the phone discoverable, and asks the user to confirm that the PIN matches on both devices. On the Android popup, the user selects Allow. Later this can be toggled under Settings > Features > Calls > "Allow this app to make and manage calls from my phone". For iPhone, the user finds the PC under iPhone Bluetooth settings and turns on "Sync Contacts" — [Microsoft support 4531605](https://support.microsoft.com/en-us/help/4531605/setting-up-and-using-calls)
- Windows privacy toggles "Let apps make phone calls" and "Let apps access call history" may need to be on (community) — [Microsoft troubleshooting calls](https://support.microsoft.com/en-US/Windows/Apps/PhoneLink/troubleshooting-calls-in-the-Phone-Link) (snippet)
- Apple: Apple Account, FaceTime, and the phone-number registration, plus a per-device allow list in iPhone settings ("Calls on Other Devices", choose your Mac) — [Apple Mac User Guide](https://support.apple.com/guide/mac-help/receive-calls-text-messages-mac-mchl1b152152/mac)
- Samsung: same Samsung account, with the feature turned on per device (Quick Panel toggle). The setting doesn't appear on a tablet signed into a different account — [Samsung US](https://www.samsung.com/us/support/answer/ANS00083152/); [Samsung community](https://eu.community.samsung.com/t5/mobile-apps-services/call-and-text-on-other-devices/td-p/5331370)
- Phone Hub (Chromebook) requires Bluetooth on for both devices. If pairing fails, Google suggests removing previous Bluetooth pairings on both devices — [Google: Set up & use Phone Hub](https://support.google.com/chromebook/answer/10480029)
- Chrome click-to-call needed an Android phone linked to the same Google account. A 2023 desktop popup read "To send a number from here to your android phone, sign in to chrome on both devices" — [9to5Google](https://9to5google.com/2023/08/30/google-chrome-click-to-call-feature-removed/); [Reddit r/JoinApp](https://redlib.belloworld.it/r/JoinApp/comments/170mui4/clicktocall)
- Each Chromium sharing recipient is addressed by an FCM registration token and encryption keys (RecipientInfo) — [sharing_message.proto](https://chromium.googlesource.com/chromium/src/+/689912289c/chrome/browser/sharing/proto/sharing_message.proto)

### Inferences
- From prior knowledge of Chromium, not re-verified this session: the device list for Sharing came from Chrome Sync's DeviceInfo data type. Each Chrome instance published its sharing FCM token, its keys, and which sharing features it supported (for example click-to-call only on Android), and the desktop filtered for devices that were recently active. Treat this as unverified.
- Design lesson: the registry should store per-device capability flags (can-dial, has-SIM) and a last-seen timestamp, not just a token.

### Gaps
- I found no public docs on how Aircall, Dialpad, and the others store endpoint registrations. This is proprietary.

## Device selection: ring all vs. preferred device

### Takeaway
Telephony vendors default to simultaneous ringing across every logged-in endpoint for inbound calls. For outbound calls, a setting picks the endpoint (app vs RingOut vs desktop app). OS features pick the single paired phone. Chrome showed a chooser menu listing the user's devices.

### Cited Findings
- Aircall: the app and the forwarding number ring simultaneously, with no sequential option — [Aircall support](https://support.aircall.io/en-gb/articles/10375354624413) (snippet)
- RingCentral: the outbound "make calls with" choice is a RingOut toggle and number under Settings > Phone > Outgoing. Multiple RingOut numbers can be saved on mobile. Admins can choose a saved number or "Custom Phone Number" — [RingCentral support](https://support.ringcentral.com/app/phone/desktop-web/enabling-using-ringout-ringcentral-app-desktop-web.html)
- Dialpad: a step to "select your preferred Dialpad device" (snippet only) — [Dialpad help](https://help.dialpad.com/hc/en-us/articles/211463286-Enable-Click-to-Call-with-Chrome)
- CallHippo: the user chooses between the desktop app and calling directly in Chrome — [CallHippo help](https://callhippo.ladesk.com/871505-Click-to-Call)
- Chrome click-to-call: clicking a tel: link, or right-clicking an unlinked number, opened a "Call from your devices" menu where the user chose which linked handset receives the number. It also appeared in the omnibox — [TechSpot](https://www.techspot.com/news/82282-chrome-beta-desktop-you-send-phone-numbers-android.html); [9to5Google 2019](https://9to5google.com/2019/02/22/google-chrome-click-call-android/); [9to5Google 2023](https://9to5google.com/2023/08/30/google-chrome-click-to-call-feature-removed/)
- Apple: the iPhone side allows a list of specific devices (choose your Mac) — [Apple](https://support.apple.com/guide/mac-help/receive-calls-text-messages-mac-mchl1b152152/mac)

### Inferences
- A good pattern for a CRM is a "Call via: [This browser] [My phone — Pixel 8] [Callback to +1…]" selector with a remembered default, like Chrome's per-click device chooser combined with RingCentral's persistent setting.

### Gaps
- I couldn't fetch the detailed ring-group settings for JustCall and CallHippo (simultaneous vs sequential).

## Presence / heartbeat and offline / locked feedback

### Takeaway
Public documentation is thin. OS features mostly fail with generic "reconnect / re-pair" guidance instead of a precise "phone locked" or "phone offline" state. Telephony vendors document user availability statuses (available, DND, and so on) more than device health.

### Cited Findings
- Phone Link troubleshooting for calls is generic: close Phone Link, remove the Bluetooth pairing, and pair again from Calls. If Do Not Disturb is on, call notifications may be silenced — [Microsoft troubleshooting calls](https://support.microsoft.com/en-US/Windows/Apps/PhoneLink/troubleshooting-calls-in-the-Phone-Link) (snippet)
- Phone Link does not relay an Android call to a Bluetooth headset connected to the phone — [Microsoft troubleshooting](https://support.microsoft.com/en-gb/topic/troubleshooting-calls-in-the-phone-link-app-1644add0-a51e-ff32-1b55-82b1ecf6b359) (snippet)
- Phone Hub's Smart Lock/unlock feature needs the phone unlocked, nearby, and with Bluetooth on (third-party guide, consistent with Google's page). Call requirements are not detailed on Google's page — [Google Phone Hub](https://support.google.com/chromebook/answer/10480029); [Technipages](https://www.technipages.com/how-to-use-phone-hub-on-chromebooks/)
- Apple's only stated limit is proximity (about 10 m), the same Wi-Fi, and the same account. Outside these, calls simply don't relay — [Apple](https://support.apple.com/guide/mac-help/receive-calls-text-messages-mac-mchl1b152152/mac)
- Samsung troubleshooting from a moderator: check the same Wi-Fi network and that the feature is on in the Quick Panel on both devices — [Samsung community](https://us.community.samsung.com/t5/Galaxy-Watch/Call-and-text-on-other-devices-not-working-between-Galaxy-Watch/td-p/3428337)

### Inferences
- With Bluetooth HFP relays (Phone Link), the phone being locked usually doesn't block placing a call, because the call is driven over HFP. This is general Bluetooth knowledge and is unverified for Phone Link specifically.
- With push-to-dialer (Chrome model), a locked phone means the user must unlock it to complete the call. Android also restricts background activity starts, so a notification the user taps is the likely UX. This is an inference. I found no source on the exact behavior of Chrome's Android receiver.
- None of the OS vendors expose a "last seen / reachable" indicator before the user clicks. Chrome filtered its device list by recency. A CRM could do better by showing a pre-flight "Phone reachable · last seen 2 min ago" state.

### Gaps
- No vendor source found on Aircall, Dialpad, or RingCentral presence semantics (Available, Busy, DND, Offline) or what happens to a click-to-call when no endpoint is online. This needs a follow-up.
- I found no documented "phone locked" message for any OS feature.

## UI pattern: live call widget in the browser

### Takeaway
Telephony vendors ship a persistent dialer surface: a Chrome extension popup or side panel, a CTI iframe docked in the CRM (Salesforce Open CTI style), or a separate desktop app that the extension hands off to. Click-to-call icons are injected next to every detected number.

### Cited Findings
- JustCall: a pop-up dialer usable from any tab, with call/text icons injected into CRMs — [JustCall help](https://help.justcall.io/en/articles/3933637-getting-started-with-justcall-chrome-extension); [Chrome Web Store](https://chrome.google.com/webstore/detail/justcall-click-to-call-fo/ahiickjmnblnnhjcomiegpdikaboegda)
- JustCall Salesforce CTI needs the Pro plan and Lightning (not Classic). Call/text buttons are added next to each contact number — [JustCall blog: Salesforce integration](https://justcall.io/blog/salesforce-justcall-phone-integration.html)
- A 2021 JustCall post recommended the desktop app over the Chrome extension for active calls. It may be outdated — [JustCall blog](https://justcall.io/blog/best-chrome-extension-dialers.html)
- Aircall: the extension hands off to Aircall Workspace, and a Power Dialer list can be built from page numbers — [Aircall support](https://support.aircall.io/en-gb/articles/10375354868893)
- Dialpad: numbers are highlighted when "Launch CTI automatically" is on, with an optional confirm-before-dial step — [Dialpad help](https://help.dialpad.com/docs/dialpad-extension.md)

### Inferences
- The confirm-before-dial step (Dialpad, RingOut "press 1") is a recurring safety pattern against misdials from auto-detected numbers.

### Gaps
- I couldn't verify floating/draggable vs docked behavior per vendor (Aircall Workspace, Dialpad CTI, RingCentral Embeddable) from fetched docs.

## Status sync across devices and CRM logging

### Takeaway
Within cloud PBXs, the server owns call state. Simultaneous ringing ends on the other endpoints when one answers (standard SIP forking behavior). CRM logging is done server-side or by the CTI after the call. OS relays sync only within their own ecosystem and don't log to third-party CRMs.

### Cited Findings
- Aircall: calls follow Aircall's distribution and ring times until answered, either in the app or at the external number — [Aircall support](https://support.aircall.io/en-gb/articles/10375354624413) (snippet)
- JustCall's changelog lists "Better CRM Integration and Call Logging". One reviewer reported spotty accuracy linking data back to Zoho — [Chrome Web Store reviews](https://chromewebstore.google.com/detail/justcall-click-to-call-fo/ahiickjmnblnnhjcomiegpdikaboegda/reviews)
- Chrome click-to-call was moved behind a flag in early 2023, disabled by default around May 2023, and the `#click-to-call` flag was removed in Chrome 116 (crbug 1418774), with no formal announcement. A Chromium team member said they would discuss with the product team "whether we can continue to support the feature" — [9to5Google](https://9to5google.com/2023/08/30/google-chrome-click-to-call-feature-removed/). I found no evidence it was restored as of 2026.

### Inferences
- "Answered on one device stops the others" is inherent to server-side forking (VoIP) and to the OS relays (the phone owns the call). The push-to-dialer model has no call-state feedback at all. The web app can't know whether the call connected unless the phone app reports back. This is the main gap for a web-to-SIM design.
- CRM logging for SIM calls placed via push would need a companion app reading the phone's call log or reporting call events. A bridge design gets logging for free because the cloud places both legs.

### Gaps
- No primary docs fetched on how Aircall, Dialpad, RingCentral, or CallHippo map calls to CRM records (matching by phone number, activity creation, recordings).
- Google Messages for web pairing (QR code, and account-based pairing since about 2023) was not researched in this session due to budget.
