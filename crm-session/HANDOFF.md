# Hand-off: continue the CODE7 CRM general-CRM work (written 2026-11-21)

Paste the prompt below into a new Claude Code session on this repository: GitHub `muhammedfayiz122/claude-cloud`, branch `ccr-99d47d83-mm8xyv`.

---

## Prompt for the new session

> Continue the CODE7 CRM work from the previous session. Everything is in the repository, under `crm-session/` on branch `ccr-99d47d83-mm8xyv`.
>
> 1. **Read the session notes**, in this order:
>    - `crm-session/HANDOFF.md`, this file (the state, the rules, and what is left);
>    - `crm-session/SESSION_LOG.md`, at least §12–§14, the latest entries;
>    - `crm-session/BRIEF.md`, the rules for implementation agents;
>    - `crm-session/RESEARCH.md`, the enterprise CRM research behind the decisions.
> 2. **Set up the environment:**
>    - Log in to GitLab using `$GITLAB_TOKEN` and `$GITLAB_URL` from the environment. Never write the token to disk.
>    - For every fetch and push, run `git -c "http.extraHeader=PRIVATE-TOKEN: $GITLAB_TOKEN" ...`.
>    - Clone crm-backend (project 32) and crm-frontend (project 31) into `/home/user/repos/`.
>    - Copy `crm-session/tools/*` to `/home/user/tools/`.
>    - Rebuild the local stack. SESSION_LOG §12 lists the test services (Postgres 15432, ClamAV 13310, Gotenberg 13000, moto S3 19000) and the Node 24 and Python 3.12 helpers.
> 3. **Pick up the open work** in "What is left", below. Start each follow-up branch from its remote head (`ls-remote`).
> 4. **Follow the owner's rules** listed below.
>
> Don't ask me to re-explain the project. Ask only if a real product decision is missing.

---

## Owner's rules (binding)

**Scope**
- We are building a **general CRM**, not one for a single client. Never hardcode anything for a company.
- Quality is enterprise grade: follow the common pattern of Salesforce, Dynamics, Zoho, HubSpot and Creatio, and record each choice as a D-number.
- **Fix only issues related to what we are implementing.** That means the audit-rollout issues (index crm-backend #64) and the workspace issues (tracker crm-backend #72).
  - Out of scope (dropped): crm-frontend #78 (Arabian Sky dashboards), develop's D557 for leads and opportunities and its settings screen, and the generic Arabic translation of server refusal messages.

**Merge requests and CI**
- **Keep the number of merge requests to a minimum; the runners are in crisis.** Do not open new MRs.
- Fold follow-ups into the existing MRs, with **one push per MR at the end**. Push every intermediate branch with `-o ci.skip`.
- Never merge your own MR; the owner reviews and merges.

**Before calling anything done**
- **No gaps.** Do not call anything complete while gaps remain. Run a deep browser check of every workflow and button, with a restricted user, Arabic, and phone width.
- Check GitLab for new issues in our scope before saying it's finished.

**Git and commits**
- Use commit trailers:
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
  ```
  In a new session, use that session's URL.
- Merge; never rebase or force-push. Never drop a database; use a new database name instead.
- Keep a session log: repo logs go in `docs/session-log/` (backend) and `docs/sessions/` (frontend). Keep `crm-session/SESSION_LOG.md` up to date and pushed to GitHub. The container can end at any time.

---

## State at checkpoint (2026-11-21)

### Open merge requests (all target `develop` or are stacked on another MR; squash on merge)

| MR | What it covers | Backend | Frontend | Base | Issues |
|---|---|---|---|---|---|
| A | General-CRM gaps from the audit rollout (WP1–WP4, WP2b) | !680 `feature/audit-rollout/general-crm-gaps` | !750 (same branch name) | develop | BE #50–#55, #57–#67; FE #54–#65 |
| B | Sales orders and payment attribution | !682 `feature/sales-order/sales-orders-and-payment-attribution` | !752 | develop | BE #56 |
| C | G1: isolation verified, confidential Lead fields, Lead scoring editor | !683 `feature/governance/multi-unit-isolation-verified` | !753 | develop | BE #73–#78 |
| D | G2: process selection by unit, unit-aware screens | !684 `feature/governance/context-process-selection` | !754 | stacked on A | BE #80, #81; FE #70, #72–#75 |
| E | G3: presets, delegated unit admin, identity modes, handoffs | !685 `feature/governance/unit-presets-and-handoffs` | !755 | stacked on C | BE #79, #82–#84; FE #71 |

- **Merge order:** A and C first, then B, D and E. GitLab retargets D and E onto `develop` automatically.
- **Merge note:** A and E both set `COMPAT_VERSION = 30`. Whichever merges second must bump it and recompute the fingerprint under **Python 3.12**. It always fails under 3.13.
- **MR B release step:** after deploy, run `backfill-record-contexts` then `verify-record-contexts` for each organization (`deploy/README.md` §6.1).
- **CI status:** `verify:backup-restore` passes on !680 and !684 after the schema-ordering fix. The remaining red jobs are runner problems that develop's own pipelines show too:
  - backend `test:system` times out;
  - frontend `test:snapshot-renderer` fails;
  - frontend unit shards fail when lazy loads exceed 5 s.

### Follow-up branches (in progress at checkpoint, pushed with `-o ci.skip`)

| Package | Branch, both repos | Merges into | Content |
|---|---|---|---|
| FU1 | `fix/audit-rollout/followups` | MR A | BE #85 (completion evidence and approver availability), BE #87 (required deadlines), FE #76 (Edit Lead save after a customized form), FE #77 (automation run step labels and outcomes), transfer-all retry browser check. Migrations 0543–0545, D650–D654. |
| FU2 | `feature/audit-rollout/change-approval` | MR A | BE #86 (configurable manager approval for service reassignment, person-field changes and controlled fields). Migrations 0546–0549 (re-chain after FU1 at merge), D655–D659. |
| FU3a | `fix/governance/g1-followups` | MR C | Scoring editor authors every condition kind (stage, service, `in` list, nested groups). A Proposal file needs the proposal's own read in legacy organizations. The approval policy warns when an isolation pair empties an approver set. Browser checks of the D628 refusals for routing and duplicate rules. D670–D674. |
| FU3b | `fix/governance/g3-followups` | MR E | Handoff approver notices go to every eligible approver (no cap of 50). Service participants, so Keep access and Hand over work on services. `/records/{kind}/{id}/responsibility` answers share-only readers instead of returning 404. Migrations 0648–0649, D675–D679. |


### Exact state of the follow-up branches (reported by the agents at checkpoint; all pushed, remote = local)

| Package | Backend head | Frontend head | Done | Left (next steps) |
|---|---|---|---|---|
| FU1 `fix/audit-rollout/followups` | 70f72ebaf (migration 0543 on 0542, D650–D653) | 6dbf0b82f | FE #76 **fixed + browser-checked** (D653). BE #85 (D650), BE #87 (D651) and FE #77 (D652) built and tested. Unit suite: 13734 passed. | Re-run the frontend typecheck and eslint at 6dbf0b82f. Write D653 into the backend decision register. Browser-check #85, #87 and FE #77 with a restricted member and in Arabic. Do the transfer-all retry browser check (not started). Run gates, isolation, contract, and the pipeline, service and automation integration suites. Run build:bundles and the budget check. |
| FU2 `feature/audit-rollout/change-approval` | 54d383bc7 (migrations 0546–0549 on 0542, D655–D659, EXPECTED_HEAD 0549) | bc2ac44c9 (`wip:` 685339b9f) | Backend complete and tested: change-approval integration 7 passed, gates + isolation 6078, contract 142. Frontend built; browser check passed in English with three personas. | Write vitest for the queries, panel, settings and the edit request path. Run eslint, then build:bundles and budgets. Check Arabic and phone width (the earlier run stopped on a disabled control). Run the full service integration suite. Fix two cosmetic issues: "Steps are decided" shows with a single step, and Approve stays enabled after a failed apply. **Merge note:** 0548 replaces the notification kind and source checks. When re-chaining after FU1's 0543, carry both sets of kinds. |
| FU3a `fix/governance/g1-followups` | 2ec4df24f (no migrations, D670–D672) | 326b41138 | **Finished.** Scoring editor for every condition kind (D672), proposal files gated (D670), approval warnings (D671), D628 refusal browser checks. gates + isolation + contract: 6043 passed. Budgets green. | Merge into MR C. |
| FU3b `fix/governance/g3-followups` (contains FU3a) | 905879837 (migrations 0648–0649, D675–D677, EXPECTED_HEAD 0649) | 699e975dd (`wip:` 21471e4b2) | Approver notices go to everyone (D675). Service participants and handoffs, backend side (D676). Responsibility read for share-only readers, backend side (D677). | Fix the failing gate `tests/gates/test_a_share_tells_the_access_model.py::test_only_the_two_owners_write_a_share` by adding the service participant repository as a third writer, with D676's reason, then re-run. Frontend: run the wider vitest, build and budgets, an Arabic browser check with a restricted member (share, hand over, shared chip), and the re-pin. Finish the session log and replace the `wip:` commit with a finished one. |

The environment was rebuilt mid-way. A machine restart lost dockerd, the test containers and moto. FU1 restarted the existing `crm-backend-test-*` containers and started moto on :19000. All earlier local databases are gone, so run `stack.sh db` on fresh database names.

Each branch's real status is in its repo session log, in the section **"State at checkpoint"**. Read it, and check `ls-remote` for the heads, before continuing.

---

## What is left (in order)

1. **Finish FU1, FU2, FU3a and FU3b.** Each branch's checkpoint section lists what is left.
2. **MR B items** (do these on the MR B branch, under `-o ci.skip`, then push once):
   - An open sales order should follow its proposal's or opportunity's responsibility transfer, as a dependent, the way the transfer engine treats other dependents. Record this as D598.
   - Add labels for `sales_order.*` and `payment.configure` to the permission-label catalogue. The catalogue lives on MR A. Either add the labels on MR A, guarded so a key unknown to the contract is ignored, or stack MR B on MR A. Choose the way that keeps CI green, and record the choice.
3. **Merge each follow-up into its MR:**
   - Re-chain migrations into one line, update both gate lists and EXPECTED_HEAD, and register new tables in the isolation sweeps.
   - Merge MR A's result into the MR D branches, and MR C's into MR E.
4. **Before each single push:**
   - Run the full backend regression in chunks (gates, isolation, contract, `.claude/tests`, unit, integration), with `-n 2 --timeout=900 --timeout-method=thread`.
     - Rerun the files that hit the `tests/app_cache.py` 16-application cap; they pass alone.
     - `test_s3_object_store` fails only locally (moto, not MinIO).
   - Run the full frontend vitest, then rerun the failing files alone.
   - Frontend build: `NODE_OPTIONS=--max-old-space-size=4096 pnpm build:bundles && node tools/check-bundle-budgets.mjs`. Plain `pnpm build` gets OOM-killed here.
   - `python3 tools/schema-forward-refs.py db/schema.sql` must print nothing.
   - `tools/schema-apply-check.sh <backend dir>` must say OK.
5. **Push each MR once, then:**
   - Update the MR descriptions; drafts are in `crm-session/mr-descriptions/`.
   - Comment on the issues the follow-ups close (BE #85, #86, #87; FE #76, #77) with the MR links, and update the tracker #72 summary.
6. **Final check:**
   - List open issues in both projects created since 2026-11-20 and decide which are in scope.
   - Then hand over to the owner with the merge order and the release steps.

---

## Useful facts

- **Local stack script:** `stack.sh` (in `crm-session/tools`). Commands: `db`, `api`, `worker`, `web`, `status`, `stop`. Configure it with `DB=… CRM_BACKEND_DIR=… CRM_FRONTEND_DIR=… API_PORT=… WEB_PORT=…`.
  - Run servers detached: `(setsid nohup bash stack.sh api > log 2>&1 &)`.
  - The dev principal `local-verifier` holds every permission. To test as a restricted member, change the role with SQL.
- **Contract re-pin:** `tools/repin.sh <frontend dir> <backend dir>` copies the backend `openapi/crm-openapi.yaml` and records the source ref.
- **Migration gate lists:**
  - `tests/gates/test_s0_03_production_schema_lifecycle.py`: the chain dict, `EXPECTED_HEAD` and `ROOT_REFERENCING_TABLES`.
  - `tests/gates/test_s0_03b_upgrade_rehearsal.py`: the revision tuple.
- **New tables** go in `tests/conftest.py` (ALL_TABLES, TENANT_SCOPED_TABLES and APP_READABLE_TABLES, plus a seeded row per organization), the cross-tenant read and write sweeps, the missing-context probes, and `test_root_foreign_key`.
- **Foreign keys:**
  - In `db/schema.sql`, a key to a table created later in the file is added with `ALTER TABLE … ADD CONSTRAINT <name the migration gives it>`, placed after that table.
  - A foreign key added to an existing table is created `NOT VALID` and validated by `deploy/sql/validate_foreign_keys.sql`. Never validate inside a migration; it fails under RLS.
- **Decision numbers used so far:**
  - D570–D584 (WP3)
  - D590–D597 (MR B)
  - D600–D616 (WP1–WP4)
  - D620–D629 (G1)
  - D630–D636 (WP2b)
  - D640–D649 (G2)
  - D650–D659 (FU1/FU2)
  - D660–D669 (G3)
  - D670–D679 (FU3)

  Free: D598–D599, D617–D619, D637–D639, D680+.
- **MR description structure** (per CONTRIBUTING): why → what changed → how to verify → requirement IDs → what is not covered.
