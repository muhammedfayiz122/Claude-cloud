# Handoff: Call on my phone, after the backend merges (2026-11-10)

Paste everything below the line into a new session. Start it on the environment whose `GITLAB_TOKEN`
was just renewed.

---

Continue the "Call on my phone" rollout.
- The plan is `plans/Call on my phone implementation plan FINAL.md` (GitHub `muhammedfayiz122/claude-cloud`, branch `ccr-677bd7a9-uyy00w`).
- GitLab is https://gitlab.code7it.com. Use the REST API with `PRIVATE-TOKEN: $GITLAB_TOKEN`; glab is not available.
- **Do not merge or deploy anything.** The owner does that.

## State

| MR | Repo | State |
|---|---|---|
| !577 | crm-backend | **Merged** (decision D492) |
| !55 | business-platform-backend (project id 34) | **Merged** (push channel) |
| !578 | crm-backend | **Merged** at `a821b776` (squash `20b9a905`) |
| !61 | crm-app, branch `feat/call-on-my-phone` | Draft. Reviewed Ready (round 2, note 44080). Contract pinned to backend `b768a4e1`, which is not merged |
| !670 | crm-frontend, branch `feature/pipeline/call-on-my-phone` | Draft. Head `4231298ac`. Contract pinned to backend `fff26acac`, which is not merged. Round-2 review note may still be pending |

**Development deploy of !578:** `develop` pipeline #17788 failed at `migrate:development` and changed nothing. Both automation worker slots were occupied (blue at durable version 17, green at 16), and !578 brings version 18. The fix is CRM-DURABLE-001 §7.4: run `retire-worker:development`, then retry `migrate:development`, then the deploy jobs. That is the owner's call: report the pipeline's state, don't run it.

## Tasks

1. **Report the state.**
   - State of !61 and !670.
   - The latest crm-backend `develop` pipeline and its migrate/deploy jobs.
   - Whether business-platform-backend `develop` has deployed !55.
2. **Re-pin !61 (crm-app) to merged crm-backend `develop`.**
   - Run `tool/sync_openapi.sh <develop sha>` then `tool/generate_api.sh`. The tool scripts are mode 100644, so run them with `bash`.
   - Rebase or merge on `develop`.
   - Re-check the Platform push-registration route and body against merged !55: `PUT`/`DELETE /api/v1/native/session/push-registration`.
   - Update MOB-116 in `docs/project/DECISION_LOG.md`: it is no longer pinned to an unmerged commit.
   - Run:
     - `dart format --set-exit-if-changed lib test tool integration_test`
     - `flutter analyze`
     - full `flutter test`
     - the generated-API check
   - Flutter is at `/opt/flutter/bin` and the Android SDK at `/opt/android-sdk`, if this machine still has them. If not, ask before installing.
   - Commits:
     - author `Fayiz Code7 <fayiz@code7.ai>`, set in the repo-local git config;
     - this repo allows the `Co-Authored-By`/`Claude-Session` trailers.
3. **Re-pin !670 (crm-frontend) to merged crm-backend `develop`.** Follow CONTRIBUTING §2.7:
   - copy `openapi/crm-openapi.yaml` at that sha;
   - update `crm-openapi.source.json` (ref, bytes, sha256) and the `DOCUMENT_INDEX.md` row;
   - also copy the Platform contract from merged !55 into `docs/platform/platform-openapi.json`, and make the device contract test cover the `push` block.

   Rebase on `develop`, then run on Node 24 (`/opt/node24/bin`, `NODE_OPTIONS=--max-old-space-size=8192`):
   - `pnpm typecheck`, `pnpm lint`, `pnpm test`;
   - `pnpm build && node tools/check-bundle-budgets.mjs`. The shell was at 205.0/205 KB and the Lead route at 139.8/140 KB.

   Commits:
   - author `Fayiz Code7 <fayiz@code7.ai>`;
   - **no `Co-Authored-By` trailers and no tool notices** (repo rule);
   - each message ends with only a `Claude-Session:` line.
4. **Push and verify.**
   - Push each branch with `--force-with-lease=<branch>:<old sha>`; never push `develop` or `main`.
   - Wait for each MR pipeline and fix failures you caused. Retry an infrastructure failure once (image pull, the sqlite3 GitHub download) and report it.
5. **Ask the owner before taking !61 and !670 out of Draft.** Then post one note on each MR: what was re-pinned to which sha, the commands run with their results, and the pipeline status. No tool-attribution footer.
6. **Report.**
   - The final state of all MRs.
   - The remaining owner steps:
     - Firebase projects and the `CRM_FIREBASE_*` and `PLATFORM_PUSH_FCM_*` variables;
     - `PLATFORM_PUSH_SERVICE_TOKEN`, `CRM_PUSH_GATEWAY_*` and `CRM_PHONE_CALL_FINGERPRINT_KEY` on Development;
     - the org switch;
     - the real-device checklist (plan §6) on Samsung and Xiaomi.
