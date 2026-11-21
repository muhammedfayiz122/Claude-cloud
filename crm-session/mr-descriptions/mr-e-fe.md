## Why

This is the client half of the unit presets and handoffs backend MR, for crm-frontend #71 and the screens for crm-backend #79 and #82–#84. Administrators set up business units from a preset, previewing the plan first. Department admins manage only their own unit. Members hand a record over for one purpose instead of sharing it broadly.

**Stacked on crm-frontend !753 (MR C, G1).** It targets that branch and moves onto `develop` when !753 merges.

## What changed

**Business-unit setup wizard (#71)**
- The "Set up" dialog has:
  - a preset choice (Collaborative, Private or Strict) and an optional customize step;
  - the plan, with what changes, who gains or loses reach, warnings, blocks and next steps, and Apply;
  - History, with the diff between revisions;
  - Administrators;
  - an Access check for one member's keys and units.
- The "separate team" wizard includes the preset picker and always previews before applying.

**My units**
- A settings section for delegated unit administrators. It covers members and the roles they may give, unit defaults and unit workspaces. A refusal names its reason.

**Handoffs**
- "Hand over" on a Lead is drawn from the server's published action, and on a deal from its Participants panel. You choose the colleague, purpose, categories and end date.
- A Handoffs screen has Received, Sent and To approve.
- Answer, cancel and revoke are available there, with notices in English and Arabic.

**Panels**
- A 403 or 404 from a panel's own read shows "You can't see this here." for every panel that draws failures the standard way. The account Tasks panel no longer says the server could not complete the request.

**Arabic**
- Account, contact and deal section titles are translated.
- A new test (`record-section-titles.test.ts`) fails whenever a built-in section title has no Arabic.

**Base and contract**
- Contains G1's latest work: the Lead scoring editor, plus toasts that replace earlier ones about the same subject, which the handoff toasts use.
- The contract copy is re-pinned to crm-backend 4fc6fe92e, byte-identical to the backend branch head.

## How to verify

```bash
pnpm install --frozen-lockfile
pnpm typecheck && pnpm lint
pnpm vitest run
pnpm build && node tools/check-bundle-budgets.mjs
```

Results locally:
- Typecheck and eslint are clean.
- Full vitest: 21656 passed. The one failure was a load flake that passes alone. After the Hand over change, the lead module passed 4123.
- All 679 bundles are within budget.

Browser checks (screenshots read):
- the wizard and setup dialog;
- delegated limits;
- restricted customer 404;
- Lead and deal handoffs end to end;
- the refused Tasks panel;
- Arabic RTL at 390 px.

See `docs/sessions/2026-11-20-unit-presets-and-handoffs.md`.

## Requirement IDs

- crm-frontend #71
- crm-backend #79, #82, #83, #84
- Decisions D660–D669

## What is not covered

- A deal's stage names come from the pipeline definition, so they show in whatever language the organization wrote them.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
