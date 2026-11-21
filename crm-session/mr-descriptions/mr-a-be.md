## Why

Rolling the CRM out to an audit department on 2026-11-19 surfaced gaps that any organization would hit. They are filed as crm-backend #50–#67 (index #64) and crm-frontend #54–#65.

This MR closes them as general CRM features that each organization configures. Nothing is specific to the client that surfaced them. Every design follows the common pattern of Salesforce, Dynamics, Zoho, HubSpot and Creatio, cited in each decision.

The frontend half is the crm-frontend MR from the branch of the same name.

## What changed

**Who is told and who may see (WP1)**
- **D600 (#51)**: a notice tells exactly the people who may open the record. A notice that reaches nobody says so.
- **D601 (#58)**: a person field may give the people it names access to the record. The share's reason is the field.
- **D602**: a transfer waiting on a colleague is answered from their inbox.
- **D610**: a member with workspaces opens on one.
- **D611**: any active member may look up a colleague by identifier.
- **D635**: what a lent customer opens; whether task holders read the customer (off by default); keeping a field-given share by hand on leads and deals.

**Each pipeline decides for itself (WP2, WP2b)**

A pipeline now has its own:
- status names (D603, #52);
- won → opportunity rule, Always/Ask/Never (D604, #53);
- transfer policy, reasons and destinations (D605, #60);
- name template (D606, #62);
- fields (D608, #67);
- lead creators (D609);
- page layout (D634, #67).

Related lead changes:
- Bulk transfer and transfer-all follow each lead's own pipeline, one record at a time, with an `atomic` option (D632).
- A moved lead takes the new pipeline's name unless someone typed one (D631).
- A lead's name falls back from title to person to company (D633).
- A renamed contact or account renames the leads named after it (D636).
- Configuration reads and writes take each other's shapes (D607, #63).

**Proposals and documents (WP3)**
- Customers are created under the kind's create key everywhere (D570, #54).
- Record keys carry the year and month and restart per period (D571, #57).
- Tax precedence is proposal → customer tax profile → issuer (D572, #61).
- Document dates follow the organization's format or the box's own (D573, #66), with optional Hijri and Arabic-Indic digits (D580).
- Line text and templates use the proposal's and the customer's fields (D574, D579, #65).
- Document layout:
  - a designed box keeps its look (D575);
  - pricing-table column and total options (D578);
  - moving a line (D581);
  - a pinned reference block (D582).
- The Lead page lists its proposals (D576).
- Template drafts are kept on the server (D577).
- Creating a lead at its entry stage needs `lead.create` (D583).
- The duplicate policy runs for whoever may create the customer (D584).

**From client response to delivery (WP4)**
- Proposal response triggers and a Start services action (D612, #55).
- A proposal → service field mapping (D613, #59).
- A service-completed notice (D614).
- A completion request with confirmation and a note (D615).
- An ended request's undecided step reads as closed, not "Waiting" (D616).

**Search (#50)**
- A periodic `search.catch_up` job, with lag, cursor-age and organizations-behind gauges and two alerts (D630, amends D104).
- `CRM-OPS-001` §3.14.
- COMPAT_VERSION 30.

**Schema**
- Migrations 0520–0527, 0530–0535 and 0540–0542, chained on develop's 0519.
- Every new table is in the isolation sweeps and the migration gates.
- `db/schema.sql` and `openapi/crm-openapi.yaml` change with the code.

**Merged with develop at 6f9dca8d1**
- A field version carries both develop's `calculation` (D556) and this branch's access and pipeline options.
- A service started from a proposal is mapped first, then its pipeline is picked from the mapped value (D557 + D613, tested).

## How to verify

```bash
make check                  # every static gate (CONTRIBUTING §2.3), incl. schema + openapi conformance
make test-all               # every suite, distributed
UV_PROJECT_ENVIRONMENT=<py3.12 venv> uv run --python 3.12 pytest tests/unit/durable/test_compat_fingerprint.py
```

Run locally on the merged head:

| Suite | Passed |
|---|---|
| gates | 2509 |
| isolation | 3503 |
| contract | 142 |
| unit | 13729 |
| integration | 13274 |
| `.claude/tests` | ✓ |

Three groups of local failures are environmental:
- `tests/app_cache.py` 16-application cap: hit only with 2–3 xdist workers. The affected files pass when rerun (145 passed).
- `test_s3_object_store` (2): the local S3 stand-in is moto, not MinIO.
- The compat fingerprint test only passes under Python 3.12.

Browser checks ran each package's workflow against a real stack, including a restricted member, Arabic right-to-left and phone width. See `docs/session-log/2026-11-20-general-crm-gaps.md` and `2026-11-20-wp2b-lead-followups.md`.

## Requirement IDs

- crm-backend #50, #51, #52, #53, #54, #55, #57, #58, #59, #60, #61, #62, #63, #65, #66, #67.
- crm-frontend #54–#65 (frontend MR).
- Decisions D570–D584, D600–D616, D630–D636.

## What is not covered

- **#56** (sales orders and payment attribution) is its own MR.
- **#49** (switching separation on) is an operator runbook. The workspace issues (#72–#84) come in separate MRs.
- **D557** (a field value picks the pipeline) is wired for services only, as on develop. Leads and opportunities remain develop's open owner question.
- **Pipeline layouts**: a page-layout template (with templates on) cannot be assigned to a pipeline. A pipeline's own layout is designed in the layout designer.
- **Keep access** has no service form, because services have no participants panel.
- **Scoring rules**: a rule published before a field became confidential still scores by it.
- **Owner switches**: `proposal_commands_of_mr_524` stays off until the owner flips it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
