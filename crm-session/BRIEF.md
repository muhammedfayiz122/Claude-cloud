# Brief for implementation agents — CRM general-CRM gaps (continuation session)

You are one of several agents working in parallel on the CODE7 CRM. You own ONE work package
(named in your prompt). Read this whole brief first, then the session log
`/home/user/Claude-cloud/crm-session/SESSION_LOG.md` (sections for your package).

## Goal (owner's words, condensed)
We build a **general CRM any company can use**, not a CRM for one audit team. **Never hardcode
for any company** — build general features end users customise. **Enterprise grade**: before
designing a feature, check how Salesforce / Zoho / Dynamics / HubSpot / Creatio do it and follow
the common enterprise pattern. New pages per feature where appropriate. **Deep browser testing**
of the full workflow and every button is mandatory. Leave no bug or gap, small or large.
Don't stop at checkpoints. If something is a genuine product decision only the owner can make,
pick the enterprise-standard default, record it as a decision (D-number) and list it in your report.

## Repository rules (binding — read CLAUDE.md + CONTRIBUTING.md §0–§4 of each repo you touch)
- Backend: Python/FastAPI/SQLAlchemy async/Alembic forward-only/DBOS/**uv only**. Capability packages
  `src/crm/capabilities/<name>/{domain,application,infrastructure,transport}`; `kernel.unit_of_work`;
  RLS; errors from `kernel.errors`; invisible = NotFound. No organization-specific conditionals.
- `db/schema.sql` and `openapi/crm-openapi.yaml` change **in the same commit** as the code.
- Decisions go in `docs/architecture/CRM-ADR-REG_Decision_Register.md` with the D-numbers assigned
  to your package (below). Migrations use the revision numbers assigned to your package.
- Frontend: React + Vite + TanStack Query, `data-testid`s, metadata renderer (no hand-written forms),
  logical CSS only, en + ar strings, **bundle budgets** (`pnpm build && node tools/check-bundle-budgets.mjs`).
  When the backend contract changes, re-pin the frontend contract copy (`git log --grep re-pin` shows how).
- Small commits, types feat/fix/chore/docs/refactor/ci, title format per CONTRIBUTING §4.
- End every commit message with these two trailer lines (owner approved trailers):
  ```
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
  ```
- **Merge, never rebase or force-push.** Never drop a database — use a new DB name instead.
- Do NOT open merge requests and do NOT comment on GitLab issues — the coordinator does that.

## Git / GitLab
- Token is in `$GITLAB_TOKEN`, host `$GITLAB_URL` (gitlab.code7it.com). Never write the token to disk.
- Every fetch/push: `git -c "http.extraHeader=PRIVATE-TOKEN: $GITLAB_TOKEN" <fetch|push> ...`
- **Always push with `-o ci.skip`** (runner crisis): `git -c "http.extraHeader=PRIVATE-TOKEN: $GITLAB_TOKEN" push -o ci.skip origin <branch>`
- Push after every meaningful commit group — the container can restart at any time and unpushed work is lost
  (that already happened once and cost a whole package).
- Read issues: `curl -sS -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://$GITLAB_URL/api/v4/projects/<32 backend|31 frontend>/issues/<iid>"` and `/notes?per_page=100` for comments.

## Local stack
- Test services already running: Postgres 127.0.0.1:15432, ClamAV :13310, Gotenberg :13000, moto S3 :19000.
  Never restart/remove these containers.
- Script: `/home/user/tools/stack.sh` — commands `db | api | worker | web | status | stop`, configured by env:
  `DB=<db> CRM_BACKEND_DIR=<be> CRM_FRONTEND_DIR=<fe> API_PORT=<p> WEB_PORT=<w>`.
  - `db` creates/migrates the DB, roles, dev tenant, baseline, the dbos runtime schema. Run `db` when migrations change.
  - Start servers **detached**: `(setsid nohup bash /home/user/tools/stack.sh api > /tmp/<pkg>-api.log 2>&1 &)`
    (same for `worker` and `web`). Never use run_in_background for servers. Restart api/worker after backend code changes.
  - The API answers as dev principal `local-verifier` with every permission. For restricted users grant
    a narrower role via SQL/API on your DB and say so.
- Node 24: `export PATH=/home/user/tools/node24/node_modules/.bin:$PATH` before pnpm.
- Browser harness: skill `anthropic-skills:verify-ui` (load it). Its `ui.mjs` takes a scenario; set the
  base URL to your WEB_PORT (read ui.mjs for the variable). Screenshots: read every one you take.
- **Machine has 4 CPUs shared by several agents.** Run targeted tests (`uv run pytest tests/<area> -q -n 2`),
  not the whole suite; frontend: `pnpm vitest run <paths>`, `pnpm typecheck`, `pnpm lint`. The coordinator
  runs full regression at the end.
- DB-backed pytest needs the six `CRM_TEST_*` variables from backend CONTRIBUTING §6.1 (services are on the ports above;
  `make` exports them — read the Makefile).

## Definition of done for your package
1. Every item implemented generically (no tenant hardcoding), with backend + frontend tests.
2. Migrations applied to a real Postgres via `stack.sh db`; endpoints exercised through HTTP.
3. Deep browser check of the full workflow + every new button/state, incl. a restricted user where permissions matter,
   Arabic/RTL glance, phone width glance. Screenshots read.
4. ruff, mypy, lint-imports, schema conformance, openapi conformance (backend); typecheck, lint, vitest, build + budgets (frontend) — green for touched areas.
5. Committed with trailers, pushed with `-o ci.skip`.

## Report format (your final message)
- Branch(es) + head commits pushed.
- Per item: what was built, decision numbers, tests added, browser evidence (screenshot names + what they showed) — PASS/FAIL.
- Verified in browser vs. unit-tested only vs. not checked.
- Decisions taken on the owner's behalf (with the enterprise reference).
- Anything left open, with reason.

## Resource tips (learned 2026-11-20)
- Node runs out of heap on `pnpm typecheck` / `pnpm lint` while other agents run: prefix `NODE_OPTIONS=--max-old-space-size=6144`.
- Tests that start their own containers expect `postgres:16-alpine` etc.; these are tagged locally from mirror.gcr.io (Docker Hub rate-limits us). Never `docker pull` from Docker Hub.
- The compat fingerprint test (`tests/unit/durable/test_compat_fingerprint.py`) must be computed under Python 3.12:
  `UV_PROJECT_ENVIRONMENT=/home/user/tools/venv312 uv run --python 3.12 pytest tests/unit/durable/test_compat_fingerprint.py -q`. Under 3.13 it always fails — ignore that.
