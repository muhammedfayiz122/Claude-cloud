## Why

This is the client half of the crm-backend Sales Orders MR, for crm-backend #56. An accepted proposal now becomes a sales order, and payments show who was credited as recorded when they were received. It is built for any organization that sells from proposals.

## What changed

**Sales Orders module (its own workspaces)**
- A list with saved views, and URL-owned filters (`?view=`, `?account=`, `?contact=`, status).
- An order page with confirm, fulfil, and cancel with a reason.
- "Raised from proposal — copied from its accepted version".
- In a governed organization, the department / business-unit picker on a new order.

**Proposal**
- A "Sales orders from this proposal" panel.
- "Create sales order" appears only when it can succeed. "Create an additional order" appears when the organization allows more than one.

**Payments page**
- Attribution as recorded: person, team and department.
- Filters, and CSV export with a truncation notice.
- Each order also has its own payments panel.

**Settings**
- Settings › Payments: payment types and methods, with create, rename (en/ar), reorder, retire and restore (`payment.configure`).
- Sales-order numbering and cancel reasons.
- Record IDs: labels for Proposals and Sales orders.

**Global search** finds orders. Both lists can be workspace pages.

**Contract and parsers**
- The contract copy is re-pinned. It is byte-identical to the backend branch head's `openapi/crm-openapi.yaml`.
- The parsers accept a payment reference value with only its key, as CRM-API-001 §4.4 allows.

## How to verify

```bash
pnpm install --frozen-lockfile
pnpm typecheck && pnpm lint
pnpm vitest run
pnpm build && node tools/check-bundle-budgets.mjs
```

All of these were green locally, and all 680 bundles are within budget.

The browser check ran against crm-backend on the same branch and covered:
- the full order flow;
- attribution unchanged after the owner was reassigned;
- CSV export;
- saved views in a fresh context, and workspace pages;
- search;
- a member without `sales_order.read`, and a read-only member;
- a governed tenant's unit picker and refusal;
- Arabic right-to-left and phone width.

See `docs/sessions/2026-11-20-sales-orders-and-payments.md`.

## Requirement IDs

crm-backend #56. Decisions D590–D597.

## What is not covered

- **Permission labels.** Labels for `payment.configure` and `sales_order.*` are added to the permission-label catalogue (crm-frontend !750) once both MRs land.
- **Owner picker.** Sellers without the member directory can choose only themselves or the current owner as an order's owner. The narrow member lookup in crm-backend !680 (D611) widens this once both MRs land.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
