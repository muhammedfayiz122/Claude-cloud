## Why

Organizations that sell from proposals need what comes after acceptance: an order raised from the accepted version, and payments credited to the people, team and department who earned them. Today an accepted proposal has nowhere to go, and payments can't be attributed. This came up in the audit-department rollout as crm-backend #56, but it's built for any organization; nothing names that client.

The frontend half is the crm-frontend MR from the branch of the same name.

## What changed

**Sales orders (D590)**
- New capability `crm.sales_order`.
- An order is raised from an accepted proposal version. This is idempotent: one open order per proposal unless the organization allows additional orders.
- The order copies the header and every line, including the period and term of recurring lines (D595).
- An order moves draft → confirmed → fulfilled, or is cancelled with a configured reason.
- Keys: `sales_order.read`, `create`, `edit`, `confirm`, `fulfil`, `cancel`, `sync` and `configure`. Role templates carry them, and the CLI `grant-sales-order-keys` backfills them.
- Events: `crm.sales_order.*`.
- Settings: numbering (default `SO-00001`), cancel reasons, and whether additional orders are allowed.

**Payment attribution (D591)**
- A payment may name a confirmed or fulfilled order.
- On receipt, `payment_attributions` snapshots the order owner, the owner's team and department, and the people in person fields. A later reassignment never rewrites who was credited.
- `GET /payment-entries` lists payments with attribution, filtered by person, team, department, customer or period. The CSV export is capped at 10,000 rows, with a truncation notice.

**Around the order**
- Global search (D592).
- Saved views and workspace pages (D593).
- A Settings editor for payment types and methods, with the key `payment.configure` (D594).
- Read tools for AI apps under the role policy. A payment's evidence file, bank reference and note never leave the CRM (D596, consent v5).

**A sales order is a governed kind (D597)**
- It is classified in the same step as its create.
- An order raised from a proposal takes the proposal's business context or unit. One entered by hand names its own.
- The owner must be someone who can open the order.
- Detail, list, search, Payments and Timeline answer by the order's own classification.

**Migrations 0560–0565**, chained on develop's 0519:
- 0564 widens the classification kind check `NOT VALID`.
- 0565 validates it under `SHARE UPDATE EXCLUSIVE`.
- Every new table is in the isolation sweeps and migration gates.

**Fixes found on the way**
- An unconfigured sales-order key was shown as `REC001` in Settings › Record IDs.
- `PaymentReferenceValue` now requires only `revision` (CRM-API-001 §4.4).

## Release step (operators)

`GOVERNED_KINDS_REVISION` and `GOVERNED_WRITERS_REVISION` go to 2. After every API and worker process runs this release, run for each organization that has ever verified record contexts:
1. `backfill-record-contexts`
2. `verify-record-contexts`

See `deploy/README.md` §6.1, "Sales orders join the governed records".

## How to verify

```bash
make check
make test-all
```

Results on the head, run locally:

| Suite | Result |
|---|---|
| unit | 13636 |
| integration | 11946 |
| gates + contract + isolation | 6119 |
| `.claude/tests` | 1238 |
| compat fingerprint | passes under Python 3.12 |

Local-only failures:
- `test_s3_object_store` (2): the local S3 is moto, not MinIO.
- The `tests/app_cache.py` 16-application cap, hit only with 2–3 xdist workers. The affected files pass on rerun (142 passed).

Browser checks against crm-frontend on the same branch:
- the order flow from an accepted proposal: confirm, payment, attribution, owner reassigned with attribution unchanged, fulfil, cancel, CSV;
- a governed tenant's unit picker and refusal;
- a member without `sales_order.read`, and a read-only member;
- Arabic and phone width.

See `docs/session-log/2026-11-20-sales-orders-and-payment-attribution.md`.

## Requirement IDs

crm-backend #56. Decisions D590–D597.

## What is not covered

- **AI consent:** the Platform consent page must offer consent v5 (`sales_details`) before AI connections can use the new tools. That lives in the platform repo.
- **Permission labels:** labels for `payment.configure` and `sales_order.*` belong in the permission-label catalogue, which is in crm-backend !680. They will be added once both MRs land.
- **Responsibility transfers:** an open order doesn't move with its proposal's or opportunity's responsibility transfer, the same as a started service (D597 "Not decided here").

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
