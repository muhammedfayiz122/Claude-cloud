# Review prompt: Call on my phone (5 MRs)

Paste everything below the line into a new session that has GitLab access (`$GITLAB_TOKEN`).

---

Review the five GitLab merge requests that implement **"Call on my phone"**, then post one review note on each MR. Do not merge, approve, deploy, push code, or change any MR's Draft state. This is a review only.

## The feature

A consultant clicks **Call on my phone** on a Lead in the web CRM. Their own phone, signed in to the CRM Android app, gets a push notification. They tap it, the phone's own dialer opens with the number (`ACTION_DIAL`, so the user confirms the call), and the call goes out on their own SIM. The web shows a draggable call card with truthful status, and the call is logged exactly once.

**Out of scope:** no telephony provider, no bridge or call-back, no generic device-command platform, no iOS, no recording, no one-tap `CALL_PHONE`.

## The authoritative plan

Read this before you start:

- `plans/Call on my phone implementation plan FINAL.md`
- Repo: GitHub `muhammedfayiz122/claude-cloud`, branch `ccr-677bd7a9-uyy00w`

Review the code against this plan, the decision records, and each repo's own `CLAUDE.md`, `CONTRIBUTING` and engineering rules.

## The MRs (GitLab: https://gitlab.code7it.com)

| # | Project | MR | Branch | Status |
|---|---|---|---|---|
| 0 | `code7/business-ecosystem/crm/crm-backend` | !577 | `feature/contract/d492-call-on-my-phone` | Decision D492 and API conventions |
| 1 | `code7/business-ecosystem/business-platform-backend` (id 34) | !55 | `feature/notifications/push-channel-native-sessions` | Push registration on native session; `POST /api/v1/notifications/push-deliveries`; PLATFORM-ADR-003 |
| 2 | `code7/business-ecosystem/crm/crm-backend` | !578 | `feature/phone_call/call-on-my-phone` | `phone_call` capability, migration 0343, `logCall` link, tenant switch |
| 3 | `code7/business-ecosystem/crm/crm-app` | !61 (Draft) | `feat/call-on-my-phone` | FCM, single-use open, existing call tracker, events; decision MOB-116 |
| 4 | `code7/business-ecosystem/crm/crm-frontend` | !670 (Draft) | `feature/pipeline/call-on-my-phone` | Lead action, pickers, call card, Log Call link, admin switch |

**Draft MRs:** #3 and #4 are Drafts by owner decision. They are pinned to crm-backend commit `b768a4e1710f1514ae8f164e984b404c8c8bb337`, which is not merged yet. Being pinned to an unmerged contract is expected and is not a finding.

## How to access

`glab` may not be installable. If so, use the REST API:

```
curl -sS -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.code7it.com/api/v4/projects/<url-encoded-path>/merge_requests/<iid>/changes"
```

Clone each repo and check out the MR branch to read code in context. Run the repo's own fast checks where you can:

- **crm-backend:** unit tests and ruff. CI uses Python 3.12.
- **Platform:** pytest.
- **crm-app:** `flutter analyze` and `flutter test`.
- **crm-frontend:** `pnpm typecheck`, `pnpm lint`, `pnpm test` and the bundle budget check, all on Node 24.

## What to check (prioritise correctness and security)

1. **Identity and authorization**
   - Only the targeted phone (token `session_id` equals the request's target device) can open a request.
   - Open re-checks the following:
     - membership
     - Lead visibility
     - the `call.log` permission
     - Do Not Call
     - that the number is unchanged
   - Cross-user and cross-tenant access is refused.
   - RLS applies to the new tables.
   - The Platform service token is separate and compared in constant time.
2. **Single use / no double dial**
   - The `open` `attempt_id` fence is enforced, so a retried open after a lost response is answered from the first open.
   - The phone writes its compare-and-set to disk before opening the dialer.
   - A duplicate push or a double tap dials at most once.
3. **State machine and expiry**
   - States move forward only.
   - `requested` and `sent` both expire, including when the dispatch workflow fails permanently.
   - Write-time expiry and the read projection both apply expiry, with the 15-minute D208 backstop behind them.
   - There is one active request per member.
4. **Logging**
   - `activity_calls.phone_call_request_id` is UNIQUE, with an FK `ON DELETE RESTRICT`.
   - `logged` is final.
   - Concurrent web and phone logging produces exactly one Activity.
   - The codes `call_already_logged`, `call_request_not_loggable` and `phone_call_lead_mismatch` are handled.
5. **Do Not Call**
   - Matching uses canonical E.164 only.
   - National-format numbers are blocked (`number_not_international`) rather than bypassing suppression.
   - The request never sends the number to the push provider or the web; only `open` returns it.
6. **Push**
   - The data carries no business data: no name and no number.
   - TTL and collapse/tag behaviour are correct.
   - `deferred`, `ambiguous` and `rejected` states map to bounded retries or failure.
   - An `UNREGISTERED` token is cleared, and the token dies with the session (logout or revoke).
7. **Events**
   - Events are deduplicated durably by event id.
   - Late or duplicate events are ignored.
   - The phone sends events only in the foreground (no background refresh, D316).
8. **Migration safety (crm-backend 0343)**
   - Locking and ownership grants are correct.
   - The FK is deliberately left `NOT VALID`, following 0312/0317.
   - Check that the revision number doesn't collide with `develop`.
9. **Durable workflows:** confirm the COMPAT_VERSION 18 bump and its fingerprint are justified.
10. **Mobile**
    - No new runtime permission is requested.
    - Firebase config comes from CI variables, and no `google-services.json` is committed.
    - Cold-start, background and foreground taps are handled.
    - The sign-out partition is deleted.
    - Confirm the new production sync queue is limited to `reportPhoneCallEvent`. This is an owner decision to flag, not necessarily a defect.
11. **Web**
    - Status wording is truthful: no "answered" or "connected" claims.
    - The call card survives navigation and a refresh.
    - Only the tab that started the call shows the log prompt.
    - Keyboard dragging and accessibility work.
    - English and Arabic strings and RTL are present.
    - Bundle budgets: the shell has about 33 bytes of headroom left.
12. **Repo rules**
    - Commit format.
    - No `Co-Authored-By` trailers in crm-backend, crm-frontend or Platform. Those repos forbid them.
    - Session-log files are present.
    - No secrets.
    - MRs are independently mergeable.

## Known, already-disclosed items (don't re-report unless you think they're wrong)

- No APK build, Kotlin tests, merged-manifest check, real-device test or Firebase project yet.
- Web Playwright and backend Docker-dependent suites were not run locally.
- Web: in the Lead contact menu, "Call on my phone" is greyed only for "no phone number". Other reasons show in the dialog because of the bundle budget.
- Web: the action is hidden when the feature is off, and Do Not Call is known only after a `409`.
- Mobile: the new contract pin brings unrelated contract changes (listed in MOB-116).

## Output

For each MR, post **one note** on the MR via `POST /projects/<id>/merge_requests/<iid>/notes` with this structure:

```
## Review: <MR title>
**Verdict:** Ready / Ready with minor fixes / Changes required

### Findings
| # | Severity (Critical/Major/Minor/Nit) | File:line | Problem | Concrete failure scenario | Suggested fix |

### Verified
- what you checked and how (commands run + results)

### Not verified
- what you could not check and why

---
_Generated by [Claude Code](https://claude.ai/code)_
```

**Rules for findings:**

- Only report findings you verified in the code.
- Give each one a concrete failure scenario, with inputs or state leading to a wrong result.
- No style opinions dressed up as defects.
- Confirm each note landed by re-reading the MR's notes.

**Final reply:** a short summary table of all five MRs giving the verdict and the Critical and Major counts, plus links to each note.
