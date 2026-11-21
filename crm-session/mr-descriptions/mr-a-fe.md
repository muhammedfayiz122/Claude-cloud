## Why

This is the client half of crm-backend !680. It covers general-CRM gaps found while rolling the CRM out to an audit department: crm-frontend #54–#65, plus the screens for crm-backend #50–#67. Everything is configured per organization or per pipeline; nothing is specific to the client that surfaced it.

## What changed

**Settings › Pipelines**
- Each pipeline sets its own:
  - status names;
  - won → opportunity rule (Always/Ask/Never);
  - transfer terms;
  - name template;
  - lead naming preference;
  - fields;
  - who creates leads.
- The pipeline picker is limited to what the member may use (#64).
- Pipelines and stages no longer load slowly or blank (#59).

**Leads**
- Leads use their pipeline's page layout. The designer has a "Leads in a pipeline" audience (D634).
- Proposals panel and New proposal (D576, #58).
- The header shows "contact · company". A queued lead names who brought it in instead of an Owner (#61 item 5).
- Keep access on field-given shares, for leads and deals (D635).

**Transfers**
- A colleague answers a transfer from their inbox, with Accept and Decline (#54).
- Bulk transfer and transfer-all ask one reason per pipeline and offer a retry (D632).

**Proposals and templates**
- Template drafts autosave to the server (#60).
- Pricing-table options, cover box style and the logo (#62, #63).
- Hijri dates, a pinned reference, and line moves.
- Line and template placeholders use the customer's fields.
- A proposal is no longer stale after submit (#55).

**Delivery**
- Start services from a client response.
- A Settings page for the proposal → service field mapping.
- The audit-file document checklist refreshes after upload (#56).
- Completion requests are confirmed with a note. An ended step says how it ended (#65).

**Automations**
- Proposal response triggers.
- The intro lists the record kinds from the server's catalogue.
- Proposal notify messages offer the proposal's fields.

**Other fixes**
- The status dialog keeps its input (#57).
- The #61 small UI defects, including select overflow (item 1).

**Bundles**
- Routes were split lazily instead of raising any ceiling:
  - SegmentLeads bulk bar;
  - lead pipeline migrate action;
  - field editor dialog;
  - My Work board and reminders.

**Contract and develop**
- The contract copy is re-pinned to crm-backend eef0dec84. It is byte-identical to the backend branch head's `openapi/crm-openapi.yaml`.
- Merged with develop.

## How to verify

```bash
pnpm install --frozen-lockfile
pnpm typecheck && pnpm lint
pnpm vitest run
pnpm build && node tools/check-bundle-budgets.mjs
```

Results locally:
- Typecheck: green.
- ESLint on the changed files: 0 errors.
- Vitest: green, apart from a few files that fail only under machine load and pass alone.
- Budgets: all 684 bundles within budget.

The browser check ran against crm-backend on the same branch. It covered each workflow and its buttons, a restricted member, Arabic right-to-left and phone width. See `docs/sessions/2026-11-20-general-crm-gaps.md` and `docs/sessions/2026-11-20-wp2b-lead-followups.md`.

## Requirement IDs

- crm-frontend #54, #55, #56, #57, #58, #59, #60, #61, #62, #63, #64, #65.
- Backend decisions D570–D584, D600–D616, D630–D636 (crm-backend !680).

## What is not covered

- **Sales orders and payments (crm-backend #56)** are their own MR.
- **Workspace issues #70–#75** come in separate MRs.
- **Field-value pipeline rules (develop's D557)** have no settings screen yet; on develop they are set through the API only.
- **Transfer-all retry** was seen in tests only, because nothing in the browser data was refused.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
