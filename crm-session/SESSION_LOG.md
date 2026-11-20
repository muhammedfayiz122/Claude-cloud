# CRM audit-rollout & general-CRM gaps — session log

_Last updated: 2026-11-19 (UTC). Owner: Fayiz (CODE7). Session runs as a Claude Code cloud session._
_This file is the single source of truth to continue the work in a new session/account. Copy it (button at the top of the page) into the new session as the first message, together with the "How to continue" section._

---

## 1. What the owner asked for (chronological)

1. **Original request (done).** Log in to GitLab (`$GITLAB_URL`=gitlab.code7it.com, `$GITLAB_TOKEN`, user `fayiz_code7`), understand the CRM (crm-backend project id **32**, crm-frontend project id **31**), implement the client **Arab Dreams** Audit Department workflow (CRM_AUDIT_Draft_1.md) on **crm-development.code7it.com** as a workspace isolated from normal sales, set up their proposal (ADQ2026-603 PDF), test end to end per role, file every bug/gap as detailed GitLab issues, and produce three artifacts (admin guide, daily-usage guide, fixes/gaps report).
2. **Proposal comparison (done).** How the generated proposal compares with the client's original.
3. **Main request (in progress), verbatim gist:** "Create all issues in GitLab. Then fix every issue and gap reported in this session and the GitLab issues related to these parts. We are NOT building the CRM for this audit team — we build a **general CRM** any company can use. **Never hardcode for any company**; build general features that end users customise. Test everything deeply before making an MR. Ensure everything works after implementation. Don't implement gaps like a dump — **enterprise-grade** (research Zoho, Creatio, Salesforce etc. first). New pages per feature where appropriate. **Very deep browser testing**, full workflow and button testing mandatory. **Minimum number of MRs** (runner crisis) unless necessary. Ask if in doubt; don't stop at checkpoints; leave no bug or gap, small or large."
4. **Design answers from the owner:**
   - Separation/governance (#49): do NOT activate in code; deliver a runbook artifact; research how enterprise CRMs do it.
   - Sales orders: build a generic **Sales Order module** (from accepted proposal).
   - Payments: **Payments page + attribution** to the linked record's owner and person fields (snapshotted).
   - Won leads: **per-pipeline setting** for opportunity creation (Always / Ask / Never).
5. **Follow-up instructions (2026-11-19, later):**
   - "Many issues are created in GitLab; address each. Fix **all issues related to workspace** plus the ones we are fixing." (workspace-labelled issues: backend #72–#84, frontend #70–#75)
   - Answers: (1) "No workspace" choice behaviour as today — **ok**; (2) lead name vs primary contact precedence — **follow how enterprise CRMs work**; (3) bulk / transfer-all follow each lead's pipeline reason rules — **yes**.
   - "We should support **fully independent** units like a workspace if a company needs it, but some companies need otherwise (shared)." → configurable per business unit.
   - "Update the issues you take in GitLab too."
   - "Progress feels slow" → parallelised (see §4).
   - "Keep a session log (this file) as an artifact, update whenever."

## 2. Repository rules that bind every change (read CLAUDE.md + CONTRIBUTING.md in each repo)

- `origin/develop` is the truth; branch `feature/<area>/<slug>` from it; every MR independently mergeable; target develop; never merge own MR.
- **Commits never carry a `Co-Authored-By` trailer** (repo rule overrides tool defaults). Types: feat/fix/chore/docs/refactor/ci. Small commits.
- Backend: Python 3.12+/FastAPI/SQLAlchemy async/Alembic forward-only/DBOS/uv only. Capability packages `src/crm/capabilities/<name>/{domain,application,infrastructure,transport}`; `kernel.unit_of_work`; RLS; errors from `kernel.errors`; invisible = NotFound.
- `db/schema.sql` and `openapi/crm-openapi.yaml` change **in the same commit** as the code. Decisions recorded in `docs/architecture/CRM-ADR-REG_Decision_Register.md` (D-numbers). One session-log file per session in `docs/session-log/` (backend) / `docs/sessions/` (frontend) — **to be written at the end**.
- "One module, one MR" (new Sales Order module = own MR). No organization-specific conditionals ever.
- Frontend: React + Vite + TanStack Query, `data-testid`s, bundle budgets enforced; contract copy re-pinned to the backend commit (`git log --grep re-pin`). Needs **Node ≥ 24.18.1**.
- CI: pushes to a branch **without** an open MR start a pipeline → always push with `git push -o ci.skip` until the MR is opened (runner crisis).
- The auto-mode safety classifier refused: force-push + dropping a DB, and downloading the MinIO binary. Use merge (not rebase) and new DB names instead.

## 3. Issues and status

Legend: ✅ implemented + browser-verified (MR pending) · 🔧 in progress · 📘 delivered as document · ⏳ queued

### 3.1 Audit-rollout issues (filed by this session; index = backend #64)

| Issue | Title (short) | Status | Package |
|---|---|---|---|
| BE #49 | Separation (governance) cannot be switched on | 📘 runbook https://claude.ai/artifact/2bYSFnnL7kc9u7jgonJcpu ; activation follow-ups in G1/G3 | — |
| BE #50 | Global search ~44 days behind | 🔧 root cause found (project-on-read, 200 events/search, no job); crm-development drained (pending 0). Code fix: scheduled catch-up job + lag alert | WP2b |
| BE #51 | Notify role silently tells nobody on unowned record | ✅ D553→**D600** | WP1 |
| BE #52 | Status names unique org-wide | ✅ | WP2 |
| BE #53 | Won always creates Opportunity | ✅ per pipeline Always/Ask/Never | WP2 |
| BE #54 | Customer-from-lead needs account.edit | ✅ D570 | WP3 |
| BE #55 | No automation on proposal client response / start delivery | ⏳ | WP4 |
| BE #56 | Payments per auditor/CPA; no sales order | 🔧 new module (own MR) | WP5 |
| BE #57 | Record ID year token | ✅ D571 | WP3 |
| BE #58 | Assignees cannot see file/customer | ✅ person field grants access D554→**D601** | WP1 |
| BE #59 | Proposal details not carried to services | ⏳ | WP4 |
| BE #60 | Transfer policy/destinations/reasons org-wide | ✅ per pipeline; bulk transfers still org policy → WP2b | WP2 |
| BE #61 | VAT needs tax data typed every time | ✅ D572 tax precedence + defaults | WP3 |
| BE #62 | Leads have no name | ✅ name template per pipeline; precedence vs contact → WP2b (enterprise research) | WP2 |
| BE #63 | API inconsistencies | ✅ | WP2 |
| BE #65 | Line description placeholders | ✅ D573 (custom-field placeholders closing) | WP3 |
| BE #66 | Date format per org / per box | ✅ D574/D575 (Hijri option closing) | WP3 |
| BE #67 | Fields/forms per pipeline | ✅ fields per pipeline; **per-pipeline page layouts → WP2b** | WP2 |
| FE #54 | Transfer receiver cannot accept/decline | ✅ D555→**D602** | WP1 |
| FE #55 | Proposal stale after submit | ✅ | WP3 |
| FE #56 | Audit file docs stale after upload | ⏳ | WP4 |
| FE #57 | Status dialog loses input | ✅ | WP2 |
| FE #58 | No proposal entry on lead page | ✅ D576 | WP3 |
| FE #59 | Pipelines & stages slow/blank | ✅ | WP2 |
| FE #60 | Template binding list raw keys | ✅ (draft autosave closing) | WP3 |
| FE #61 | 11 small UI defects | ✅ 2,5,6,7,8,9,10,11 · 🔧 3 (WP3) · ⏳ 4 (WP4) · item 1 not reproducible generically (check on client tenant) | WP2/3/4 |
| FE #62 | Quotation table styling / logo | ✅ (column/totals toggles closing) | WP3 |
| FE #63 | Cover box style / text removal | ✅ | WP3 |
| FE #64 | Pipeline picker unrestricted | ✅ | WP2 |
| FE #65 | Changes-requested guidance; completion confirm/notice | 🔧 proposal part WP3 · ⏳ audit-file part WP4 | WP3/WP4 |

### 3.2 Workspace / multi-department issues (created by owner, labelled `workspace`)

Tracker: **BE #72** (read it first; "do not convert into one big MR").

| Issue | Topic | Package | Status |
|---|---|---|---|
| BE #73 | Verify governed cross-department isolation, every surface | G1 | 🔧 |
| BE #74 | Approvals, task artifacts, notifications respect context | G1 | 🔧 |
| BE #75 | Document / signed-content access across unit links | G1 | 🔧 |
| BE #76 | Service record-graph isolation & classification inheritance | G1 | 🔧 |
| BE #77 | Field confidentiality for Lead metadata/values | G1 | 🔧 |
| BE #78 | Process selection derives unit scope from classification | G1 | 🔧 |
| BE #79 | Collaboration presets (Collaborative / Private / Strict) | G3 | ⏳ |
| BE #80 | Proposal type/process/approval by business context | G2 | ⏳ |
| BE #81 | Service pipeline selection precedence (check MR !673 / FE !741 first) | G2 | ⏳ |
| BE #82 | Delegated department configuration permissions | G3 | ⏳ |
| BE #83 | Shared vs isolated customer identity — **owner: support both, per unit** | G3 | ⏳ |
| BE #84 | Scoped cross-department requests/handoffs | G3 | ⏳ |
| FE #70 | Lead page templates by department/context | G2 | ⏳ |
| FE #71 | Business-unit setup wizard with presets + preview | G3 | ⏳ |
| FE #72 | Context-aware lead field/form designers | G2 | ⏳ |
| FE #73 | Department-aware dashboards / workspace presentation | G2 | ⏳ |
| FE #74 | Governed lead success outcomes & downstream process UI | G2 | ⏳ |
| FE #75 | Department-specific proposal/service/approval choices | G2 | ⏳ |

Related: BE #70 (owner to accept D553–D555 of MR !668 — **unrelated decisions**; that's why ours are renumbered to D600+).

All issues above have a status comment, assignee `fayiz_code7` and label `Working on it` (posted 2026-11-19). Update them again when MRs open.

## 4. Branches, worktrees, MRs (planned)

| Package | Backend branch / path | Frontend branch / path | MR plan |
|---|---|---|---|
| WP1 + WP2 (+WP3, WP4, WP2b merged in later) | `feature/audit-rollout/general-crm-gaps` — `/home/user/repos/crm-backend` | same name — `/home/user/repos/crm-frontend` | **MR A** (backend) + **MR A** (frontend): all audit fixes |
| WP3 proposals & templates | `feature/audit-rollout/wp3-proposals` — `/home/user/wt/be-wp3` (branched from 03d01c9) | same — `/home/user/wt/fe-wp3` (from ee39e29) | merged into MR A branch when done |
| WP5 Sales Orders + Payments | `feature/sales-order/sales-orders-and-payment-attribution` — `/home/user/wt/be-wp5` (off develop) | same — `/home/user/wt/fe-wp5` | **MR B** (new module, own MR per repo rule) |
| G1 governance P0 security | `feature/governance/multi-unit-isolation-verified` — `/home/user/wt/be-g1` (off develop) | same — `/home/user/wt/fe-g1` | **MR C** |
| G2 / G3 | to be created off develop | | **MR D / E** (tracker asks for separate MRs) |

All branches are pushed to GitLab with `-o ci.skip` (pipelines show "skipped"). Backup of WP2 work-in-progress: `backup/wp2-wip` (can be deleted).

### Numbering registry (avoid collisions with develop and open MRs)

- develop head migration: **0516** (D549 who-may-edit-lead-field). Open MRs claim 0517 (!670), 0518 (!673); D556/D557 (!670/!673); D553–D555 (!668).
- MR A: migrations renumbered **0520–0523** (WP1 0516,0517 → 0520,0521; WP2 0518,0519 → 0522,0523); decisions **D553–D563 → D600–D610** (D600 notices to readers, D601 person-field access, D602 transfer recipient Approvals, D603–D610 = old D556–D563 per-pipeline lead settings, API alignment, names_its_leads, D563 workspace default). _(Being finalised by the merge agent — verify in the register.)_
- WP3: migrations **0540+**, decisions **D570+** (re-chain onto MR A head at merge).
- WP5: migrations **0560, 0561** chained from 0515 (re-chain to develop head before MR), decisions **D590, D591**.
- G1: migrations **0600+**, decisions **D620+**. G2: 0620+/D640+. G3: 0640+/D660+ (proposed).
- Before opening each MR: re-check develop + open MRs and renumber if needed.

## 5. Work packages — detail

### WP1 ✅ Notifications & record access (BE #51, #58, FE #54)
Backend 90ca0bb, b75573d, 026050d, f21bbc0, 9588310, 8677c5b, 03d01c9. Frontend 2e411f4, 9782923, ec1f59f, 3df2bc2, 1754504, 4832c34, 95e4fda, ee39e29.
- Notify recipients via `RecordReaders.among` (same rules as read path); step codes notified / notified_some / no_recipient / recipients_cannot_read → run `needs_attention`; FE "Needs attention" badge.
- Person field `grants_access: read|edit` → `record_participants` share (origin member_field, field keys); lends customer read-only (no child records); service owner reads customer; `share_view_only` 403; FE PersonFieldAccess setting, "Given by <field>" badge.
- Transfer recipient: Approvals nav (`also_for_work`), Accept/Decline (note), deep link `?request=`, lead-page banner.
- Extra fixes: owner name fetched only with role_permission.manage; account with no contacts.
- Open owner questions: lent customer child records? task holders read customer? adopt field share as hand share? narrow member-name lookup for non-admins?

### WP2 ✅ Lead & pipeline configuration (BE #52, #53, #60, #62, #63, #67; FE #57, #59, #64, #61 items)
Backend 37448d6, 1dc66ff, e2c55e9, b35f23f, 905b406, 3e86ebb, 0a77ebf (+ merge with develop 63ce9d2…). Frontend 1a037b4…e93acbc (13 commits) + re-pin d8bdebb.
- Per-pipeline: statuses unique, opportunity_on_win, transfer policy/reasons/destinations, lead name template (live preview, names_its_leads), field applicability; API alignment; Pipelines & stages single request; pipeline picker restricted + remembered; permission labels en/ar (75 perms, 18 areas); default workspace for audience (D563→D610); hidden pages the role can't open.

### WP2b ⏳ follow-ups (main tree, after merge agent)
- Per-pipeline page layouts (#67) — extend page_layout capability.
- Bulk / transfer-all follow each lead's pipeline reason rules (owner: yes).
- Moving a lead to another pipeline re-applies that pipeline's name template.
- Lead name vs primary contact precedence — research Salesforce/Zoho/HubSpot/Dynamics and follow (owner).
- FE #61 item 1 (overlap) with a client-like form layout; item 4 (task panel Complete + owner name) may go to WP4.
- BE #50: scheduled durable search catch-up job per organization (bounded), lag metric/alert; update D104.

### WP3 🔧 Proposals & templates — built + browser-verified; closing last gaps
Worktree be-wp3/fe-wp3, stack crm_wp3 / API :8030 (+ approver API :8031, worker `wp3/worker.sh`, `CRM_RENDERER_URL=http://127.0.0.1:13000` in `wp3/env.sh`) / web :5230.
Backend e1983d1 (#54 create keys create customers), 9146874 (#57 record-key tokens {YYYY}{YY}{MM}{SEQ:n} + restart never/yearly/monthly, migration 0540), 38af36a (#61 tax precedence proposal → customer tax profile → issuer default, new `customer_tax_profiles`, migration 0541), c58817c (#65 line placeholders, #66 date masks, designed-page box options, table styling), 3e316db (#58 lead Proposals panel), 96db2ba (#63 text run size/weight/colour). Decisions D570–D576.
Frontend 4b59f43, 11700d4 (#55 live render/approval case, #65 changes-requested banner + Revise, confirm Ask for approval), 9291257 (#58), 5deded3 (#61.3 Ctrl+Delete + Undo), e16cfa1 (#57 UI), 07118aa, ae3bd34 (#61 UI), 908a339 (#60/#62/#63/#66 designer), cf3aa74, 2ac1a9b, 90576b5, 08edd6a, 8a93806.
Browser: full flow lead → customer → proposal (placeholders, tax defaults, SAR 25,500 + 3,750 VAT) → submit → restricted approver requests changes → revise v2 → approve → accepted; designed PDF imported (9 pages), replaced text keeps look and label prefix, DD/MM/YYYY date, styled quotation table; rendered PDFs checked as images.
**Sent back to close:** server-side template drafts (autosave, never auto-publish); hide-empty-columns / totals / tax breakdown toggles + configurable note; custom-field placeholders (customer + proposal); Hijri (Umm al-Qura) calendar option; move line between sections; restricted create-only user browser check; fix "Send it on Delivery tab" copy on changes-requested version, Ref/Date block placement option, canvas badge overlap.

### WP4 ⏳ Proposal response → delivery (BE #55, #59; FE #56, #65 audit-file part, #61 item 4)
- Proposal client-response automation trigger (record kind proposal; notify; start delivery/create services; follow-ups); field mapping proposal → service; stale document state after upload; completion confirm + "completed" notice to stakeholders; task panel Complete + owner name.

### WP5 🔧 Sales Orders + Payments (BE #56) — own MR
Backend 87a48eb, 84923e2; frontend d380a64, 34f053c. Capability `crm.sales_order` (D590), payment attribution (D591); permissions sales_order.read/create/edit/confirm/fulfil/cancel/sync/configure; CLI `grant-sales-order-keys`; events created/confirmed/fulfilled/cancelled; `/sales-orders`, create-from-proposal (idempotent), settings, cancel reasons; payments `sales_order_id`, `payment_attributions` snapshot, `GET /payment-entries` (+CSV export, 10k cap). FE workspaces, detail, panels, settings, en/ar. Browser verified incl. attribution unchanged after reassignment, restricted users.
**Now closing gaps:** search source, saved views + workspace placement, payment methods/types editor, recurring lines, AI agent read tools, proposal link label, account filter in URL. Owner-default answers applied: payments only on confirmed/fulfilled orders; snapshot owner's team + department; 10k export cap with truncation notice; CLI backfill + role templates carry keys.

### G1 🔧 Governance P0 security (BE #73–#78)
Worktree be-g1/fe-g1, stack crm_g1 / API :8070 (CRM_GOVERNANCE_PREVIEW=true) / web :5270. Executable isolation matrix (two units, restricted users, dual-unit member, admin) across all surfaces; fix leaks; same suite in legacy mode; evidence for owner to flip `proposal_commands_of_mr_524` (owner decision, not flipped by us).

### G2 ⏳ Process selection & context UI (BE #80, #81; FE #70, #72–#75)
### G3 ⏳ Presets, delegation, handoffs, identity modes (BE #79, #82, #83, #84; FE #71)
Owner direction: collaborative / private / strict presets per unit configure existing primitives (no second auth engine); legacy unchanged by default; workspace never grants access; customer identity: shared mode and context-restricted mode per unit on the canonical customer store (no second store), document separate-tenant boundary.

### Final ⏳
Full regression (backend `make check` steps by hand + full integration/isolation/gates; frontend typecheck, lint, full vitest, build), merge WP3/WP4/WP2b into MR A branch, re-chain migrations, renumber decisions against develop + open MRs, re-pin contract copies, write repo session logs (`docs/session-log/2026-11-19-…md`, `docs/sessions/2026-11-19-…md`), open MRs (minimum), post MR links on every issue, update artifacts (report) and this log.

## 6. Owner decisions & open questions

Decided: see §1.4 and §1.5. Delegated defaults chosen by the coordinator (owner may override): WP5 answers above.
Open questions for the owner:
1. WP1: should a customer lent through a person field also open its activities/tasks/other records? (now: none)
2. WP1: should a task holder on a record read its customer?
3. WP1: allow an admin to adopt a field-given share as a hand share?
4. WP1: published narrow member-name lookup for non-admins?
5. Governance: flipping `proposal_commands_of_mr_524` to ready (production activation lock) — owner's call after G1 evidence.

## 7. Artifacts

- Admin configuration guide: https://claude.ai/artifact/DoywVkTG8LdZCW1ha8xr2c
- Daily usage guide: https://claude.ai/artifact/NvCVG6YGtLMTTkU44QJvUj
- Fixes & gaps report: https://claude.ai/artifact/7wn9gdqPufA2JLVPaLEYFL
- Separation (governance) runbook (#49): https://claude.ai/artifact/2bYSFnnL7kc9u7jgonJcpu
- This session log: https://claude.ai/artifact/8WiZfEf7upmTxhtZzfXbtd (source: scratchpad `session-log/SESSION_LOG.md`, regenerate with `python3 gen.py`)

## 8. crm-development tenant state (shared test environment)

- Audit configuration applied (roles Audit · Auditing Staff / Audit Manager / Accountant / CPA, Bookkeeping · Staff; Audit Department + team; Audit Department Queue + first routing rule; pipelines "Audit Department Leads" and "Audit File (Audit Department)"; proposal type, designed-PDF template, approval policy, price book Audit Fees 2026, ADQ2026- numbering; automations; workspace "Audit Department").
- Test members: QA Audit Manager, QA Auditor Riyadh, QA Auditor Jeddah, QA Accountant, QA CPA, QA Bookkeeper, QA Sales Rep (passwords are NOT in this log; reset via `POST /api/v1/session/organization/people/{pid}/temporary-password` as an org admin).
- Org-wide changes on the shared tenant: lead transfer policy (receiver decides, reason required) and a routing policy rule. Search projection drained on 2026-11-19.

## 9. Local environment (cloud container; resets on restart)

- Repos: `/home/user/repos/crm-backend`, `/home/user/repos/crm-frontend`; worktrees under `/home/user/wt/`.
- Node 24: `/home/user/tools/node24/node_modules/.bin` (installed via `npm install node@24.18.1`) — prefix PATH for pnpm.
- Stack script: scratchpad `stack/stack.sh` (copy of the verify-ui skill script; MinIO replaced by `moto_server` on :19000; supports `DB=`, `API_PORT=`, `WEB_PORT=`).
- **After a container restart** (has happened twice; databases are lost because Postgres has no volume):
  1. `setsid nohup dockerd &`; `docker start crm-backend-test-postgres-1 crm-backend-test-gotenberg-1 crm-backend-test-clamav-1`
  2. `setsid nohup moto_server -H 127.0.0.1 -p 19000 &`; `curl -X PUT http://127.0.0.1:19000/crm-dev`
  3. Per stack, sequentially (parallel runs collide): `DB=<db> CRM_BACKEND_DIR=<be> CRM_FRONTEND_DIR=<fe> bash stack.sh db`
  4. Start detached: `DB=<db> API_PORT=<p> ... setsid nohup bash stack.sh api &` and `PATH=<node24>:$PATH WEB_PORT=<w> API_PORT=<p> ... setsid nohup bash stack.sh web &` — never with run_in_background (time limit kills servers).
  5. Stacks: main crm_verify2 :8000/:5199 · wp3 crm_wp3 :8030/:5230 · wp5 crm_wp5 :8050/:5250 · g1 crm_g1 :8070/:5270 (with `CRM_GOVERNANCE_PREVIEW=true`).
- Agent brief for implementation packages: scratchpad `BRIEF.md` (goal, rules, stack, definition of done, report format).

## 10. How to continue in a new session

1. Paste this log. Ask the new session to: log in to GitLab with `$GITLAB_URL`/`$GITLAB_TOKEN`; clone crm-backend and crm-frontend; `git fetch` the branches in §4.
2. Check each branch's latest commits against §5 to see what finished after this log was last updated.
3. Rebuild the local stack (§9) and continue the ⏳/🔧 items in §5 in this order: WP3 finish → merge into MR A branch → WP4 → WP2b → WP5 gap closing → G1 → G2 → G3 → Final.
4. Keep pushing with `-o ci.skip` until MRs open; keep the repo rules (§2).

## 11. Change history of this log

- 2026-11-19 — WP3 built and verified; sent back to close gaps. WP3 branches pushed (ci.skip).
- 2026-11-19 — created (WP1, WP2 done; WP3, WP5, G1, merge-with-develop running; GitLab issues updated).

---

## 12. Continuation session (2026-11-20, new account/session)

The previous session hit its weekly limit. Unpushed work was **lost**: the WP3 gap-closing round,
the WP5 gap-closing round, and all of G1 (its branch was never pushed). They are being redone.

### State found on GitLab (2026-11-20)
- `feature/audit-rollout/general-crm-gaps` BE 63ce9d23b / FE d8bdebb69 (WP1+WP2, renumbered 0520–0523, D600–D610). 4 behind develop.
- `feature/audit-rollout/wp3-proposals` BE 96db2bab2 / FE 8a93806c7 (WP3 first round only).
- `feature/sales-order/sales-orders-and-payment-attribution` BE 84923e2d1 / FE 34f053c5f (WP5 base only).
- G1 branch: missing. develop: migration head 0517 (lead export), decisions up to D558.

### Owner answers (2026-11-20)
- Commit trailers allowed (Co-Authored-By + Claude-Session).
- WP1 open questions 1–4: follow enterprise CRMs after deep research (folded into WP2b).
- business-platform-backend: cloned, not needed for now.

### Local environment (this session)
- Repos `/home/user/repos/crm-backend`, `/home/user/repos/crm-frontend` (on MR A branch), `/home/user/repos/business-platform-backend`.
- Worktrees `/home/user/wt/{be,fe}-{wp3,wp5,g1,...}`.
- Docker Hub rate-limits: images come from `mirror.gcr.io` (set `CRM_TEST_POSTGRES_IMAGE`, `CRM_TEST_CLAMAV_IMAGE`,
  `CRM_TEST_GOTENBERG_IMAGE` to `mirror.gcr.io/...` when running compose). MinIO replaced by moto_server :19000 (`uv tool install 'moto[server]'`).
- Stack script `/home/user/tools/stack.sh` (copy of verify-ui script + DB/API_PORT/WEB_PORT, renderer env, `worker`
  subcommand, dbos runtime schema in `db`). Node 24 at `/home/user/tools/node24`.
- Token is never written to disk: `git -c "http.extraHeader=PRIVATE-TOKEN: $GITLAB_TOKEN" ...`.
- Agent brief: `crm-session/BRIEF.md`.

### Stacks
| Package | DB | API | Web |
|---|---|---|---|
| WP3 | crm_wp3 | 8030 | 5230 |
| WP5 | crm_wp5 | 8050 | 5250 |
| G1 | crm_g1 | 8070 | 5270 (CRM_GOVERNANCE_PREVIEW=true) |
| main (MR A) | crm_main | 8000 | 5199 |

### Progress
- (updated as packages finish)

### Enterprise-research decisions (2026-11-20; detail in `crm-session/RESEARCH.md`)
Owner said "go with enterprise CRMs". Adopted defaults:
1. WP1 Q1 — customer lent through a person field: header read-only + only items attached to the granting record; per field-definition setting `None` (default) / `Customer activities & notes (read)`.
2. WP1 Q2 — task holder: sees the task plus the parent's and customer's names only; tenant setting "Task assignees may read customer header" (off by default).
3. WP1 Q3 — "Keep access" creates an independent manual share beside the field-derived one; the access panel lists every reason.
4. WP1 Q4 — narrow member lookup (id, name, avatar, active, title/department) for all internal members; setting `All members` (default) / `Department + hierarchy`.
5. Lead name precedence: template/custom title → primary contact name → company → "Lead #N"; subtitle "contact · company"; search matches all; per-pipeline switch.
6. Bulk transfer: preflight grouped by pipeline, reason once per pipeline group, per-record transactions + result report + "Retry failed"; `atomic=true` API flag.
7. G3 presets: Collaborative (default) / Private / Strict; customer identity always shared (one master); Strict = unit sees a customer only with work on it, cross-unit grants need approval.
8. Sales orders: copy header + all lines, lock + link proposal; recurring lines keep term/frequency; payments partial; credit = owner 100% default.

### Progress
- 2026-11-20 MR A merged with develop: BE 6e4075429 pushed (0520 re-chained on 0517; dropped bogus compat bump — fingerprint unchanged under py3.12; D600 §3 corrected). Unit suite 13547 passed (fingerprint test only fails under py3.13 = expected). Rehearsal gate 340 passed.
- 2026-11-20 G1 round 1 pushed: BE `feature/governance/multi-unit-isolation-verified` 6f93bd2a3 (D620–D624; isolation matrix 37 surfaces × 6 people, governed + legacy; service record graph tests). Leaks fixed: notifications exposing out-of-reach record ids (D622), spoofable process context (D623); over-restrictive reads aligned (D620, D621, D624). FE: no change needed. Round 2 running: #77 confidential Lead fields + approval-policy publish warning.
  Open for owner: `proposal_commands_of_mr_524` flip (evidence: governed command tests 34/34); legacy proposal files gated by document.read only (suggest extending gated record rule to proposals); unit members cannot use the inbox (mailbox keys org-wide, fail-closed).
- 2026-11-20 Container restarted (3rd time overall). All commits were pushed; local DBs rebuilt (crm_wp3, crm_wp5b, crm_g1, crm_wp4); agents WP3, WP5, G1, WP4 resumed.
- Owner (2026-11-20): "minimum number of MRs, but open an MR as soon as something is fully finished." → open each MR (A/B/C/D/E) the moment its package set is complete and regression-checked; avoid extra pushes to an open MR (each push runs a pipeline).
- 2026-11-20 **WP3 done** (BE 9ddd0d81e, FE f83bc0a5d): drafts D577 (0542), table options D578, customer-field placeholders D579, Hijri/Arabic digits D580, move line D581, pinned reference D582, create-only fixes D583 (lead entry stage w/o transition) + D584 (duplicate check lent to creators). Open: org date format stays Gregorian; v1 templates lack pinned reference; fresh dev DB shows proposal numbering enabled but stores no format row (check on client tenant).
- 2026-11-20 **WP4 done** (BE 91cc48702, FE 4bf830adc): proposal triggers record kind proposal + response/accepted/declined/changes triggers, Start services action, "owner's manager" recipient, 3 gallery templates (D612); proposal→service field mapping page (D613, 0524); doc checklist refresh; completion request note (D615, 0527); service completed notice (D614, 0525/0526); member directory lookup (D611); task panel Complete. Open: FE tsc not run (OOM) → regression; Arabic not browser-checked; pre-existing: superseded completion step still "Waiting", automation builder intro mentions only leads/opps/services, `{{custom.x}}` not offered in proposal notify.
- 2026-11-20 **WP5 functionally done** (BE da79e5d50, FE bedb44b40; D592–D596, 0562/0563). Coordinator regression found: FK VALIDATE inside migration fails on seeded DB (rehearsal 337 errors) + 7 isolation failures → agent fixing. MR B after green.
- 2026-11-20 WP3 merged into MR A locally (0540 re-chained on 0523; gate lists gained 0540–0542 which WP3 had omitted); verification running. WP2b started (branch feature/audit-rollout/wp2b-lead-followups, D630–D639, 0530–0539).
- 2026-11-20 **G1 round 2 done** (BE 2b0f649b5, FE af4b50c44): #77 confidential Lead fields D625 (lead.confidential.read/edit, all surfaces; FE banner + field setting), approval-policy isolation warning D626. Open: scoring rule published before a field became confidential still scores by it; FE build/budgets + full BE regression to run (coordinator).
- 2026-11-20 **MR A now holds WP1–WP4**: BE 7779b038f (chain 0517→0520–0527→0540–0542; gates list WP3/WP4 revisions + 4 new root tables, which both packages had omitted; D584 test updated), FE d465e2de3 (WP4's completion-ask dialog with note replaces WP3's simpler one; contract re-pinned). Full regressions running.
- 2026-11-20 12:00 MR A backend regression run 1 hung after 99% (no summary, killed by outer timeout) → rerun with CI's `--timeout=300 --timeout-method=thread` to name the hanging test (/tmp/mra-regression2.txt). WP4 leftover defects (superseded step "Waiting", automation intro list, `{{custom.x}}` for proposals) handed to an agent on branch fix/audit-rollout/wp4-followup-defects (worktrees wt/be-wp4fix, wt/fe-wp4fix; DB crm_wp4fix; D616–D619); merged into MR A when done.
- 2026-11-20 12:10 **WP2b round 1** (BE 4b7765659, FE b59033092; D630–D635, 0530–0535, COMPAT 30): per-pipeline layouts, per-pipeline bulk transfer reasons, name template re-apply, lead name vs contact, search catch-up job, WP1 Q1–Q3, FE #61 item 1. Open → sent back to agent: bundle budgets fail (SegmentLeads 141 > 140 — **MR A base already 140.1, so MR A needs it too**; LeadDetailScreen 142.1 > 142), transfer-all dialog without per-pipeline reasons, keep access only on leads, renamed contact/account not propagated, #61 item 5 (queue lead shows Owner), worker catch-up tick unobserved. WP2b folds into MR A.
- 2026-11-20 12:40 **WP4 defects fixed** (BE a274e8722, FE dad3f5992, D616, no migration): ended request's undecided step shows `closed` with its ending (replaced/withdrawn/not reached), automation intro lists kinds from the catalogue, proposal notify offers proposal fields, non-lead triggers' hint generic. Found pre-existing on MR A: BE contract test (`LeadPipelineSettingsItem` → WP2b fixes; `ProposalTemplateDraftSummary` → wp4fix agent), FE `every-required-header-is-sent` on lead-pipeline-settings PUT → WP2b agent. Wp4fix agent also checking proposal approval steps for the same "Waiting" defect.
- 2026-11-20 13:30 wp4fix round 2 (BE b5b6b3440, FE 6b367e092): proposal approval steps already end as `cancelled` (test added, D616 addendum); `ProposalTemplateDraftSummary` requires only id+revision. MR A regression attempt 2 cut by outer timeout (one worker hung in page_layout template create under load; page_layout alone 167 passed in 53s) → attempt 3 runs per directory (/tmp/mra-*.txt). Merge wp4fix + WP2b into MR A after attempt 3.
