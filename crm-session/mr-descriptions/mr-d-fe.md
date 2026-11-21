## Why

This is the client half of the context-process-selection backend MR, covering crm-frontend #70 and #72–#75. In a governed organization, each department or business context sees its own process choices, and every screen says why a choice was made. Nothing is decided on the client. Legacy organizations are unchanged.

**Stacked on crm-frontend !750 (MR A).** It targets that branch and moves onto `develop` when !750 merges.

## What changed

**Lead page (#70)**
- The page draws its unit's layout, with a caption naming whose layout it is.
- The layout designer offers a "Leads of <unit>" audience.
- When templates are on, a new panel assigns published templates to pipelines and units.

**Field designer and leads list (#72)**
- The field designer names each pipeline with its units, and says separately where a field shows, who reads it and who changes it.
- The leads list takes `?pipeline=`. With it set, the column, filter and quick-filter pickers offer only that pipeline's fields. Without it, each limited field is labelled with its pipelines.

**Dashboards and workspaces (#73)**
- The dashboards screen says why each board is shown.
- The workspace editor leaves out members' private boards and labels team and role boards.

**Lead outcomes (#74)**
- The qualify dialog shows the process and the setting that decided where a win goes.
- A lead whose process ends at the lead closes as Won, with no opportunity offered.

**Proposal, service and approval choices (#75)**
- New Proposal offers only the types the unit may use, and names the default and why.
- Start service previews the pipeline ("Starts on Visa Delivery, the default for Visa Services, would otherwise be General Delivery"), and the service shows the stored reason.
- Settings covers:
  - a service's unit default;
  - the units a proposal type is offered to;
  - a business process's delivery pipeline.
- In a governed organization, the New transaction direct-service step offers the unit.

**Bundles**
- New pieces load lazily, and no ceiling was raised. LeadDetailScreen is 141.4 / 142 KB and LeadsWorkspace is 136.2 / 140 KB.

**Contract and base**
- Merged with MR A's latest test fixes.
- The contract copy is re-pinned to the backend branch.

## How to verify

```bash
pnpm install --frozen-lockfile
pnpm typecheck && pnpm lint
pnpm vitest run
pnpm build && node tools/check-bundle-budgets.mjs
```

Results locally:
- Typecheck is clean, and lint shows 0 errors.
- Build and budgets are green.
- Vitest: the full run passed 21737. After the last fixes, `src/lib` with locales (2940) and pipeline with commerce (5353) passed.

The browser check used two business contexts with a restricted member of each, in English and Arabic, with RTL at phone width. See `docs/sessions/2026-11-20-context-process-selection.md`.

## Requirement IDs

crm-frontend #70, #72, #73, #74, #75; crm-backend #80, #81. Decisions D640–D649.

## What is not covered

- The workspace editor's board picker was checked in vitest only, not in the browser.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
