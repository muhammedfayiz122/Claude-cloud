## Why

This is the client half of the crm-backend MR for workspace issues #73–#78: verified multi-unit isolation and confidential Lead fields. The screens follow the server; nothing is decided on the client.

## What changed

**Confidential Lead fields (D625)**
- Settings offers the confidential class on a Lead field.
- The lead page says, once, that confidential fields are hidden from a member who may not read them.

**Field editor (D628)**
- Making a field confidential while published rules use it shows "This field cannot be confidential yet" and lists the rules, in English and Arabic.
- Each listed rule links to Lead scoring, Routing or Duplicate rules.
- Kinds the server names that the screen doesn't know are shown with the server's own wording.

**Settings › Lead scoring (D629), a new lazily loaded section**
- Live rules are shown, and a condition on a confidential field is marked "Skipped" (D627).
- Draft editing covers name, points, all/any conditions over the organization's fields, source, status and the counts.
- Rules the editor can't draw are kept exactly as written, read-only.
- Save and Publish send If-Match. Check shows the server's verdict.
- Members holding only `lead_scoring.explain` get a read-only view.

**Toasts**
- A toast about the same action replaces the earlier one, whatever its tone, so a refused save followed by a successful retry no longer leaves the failure on screen.

**Contract**
- Re-pinned to crm-backend 43a3ed022, byte-identical to the backend branch head.

## How to verify

```bash
pnpm install --frozen-lockfile
pnpm typecheck && pnpm lint
pnpm vitest run
pnpm build && node tools/check-bundle-budgets.mjs
```

Results locally:
- Typecheck, eslint and prettier are clean.
- Vitest on the touched areas passes: settings, toast, transport, locales, and the earlier G1 areas (5436).
- All 673 bundles are within budget. The Settings route is at 132.9 of 140 KB.

The browser check (screenshots read) covered:
- the refusal with "Open Lead scoring";
- editing the draft, then check and publish;
- retrying the field until it showed the Confidential badge;
- a legacy skipped rule fixed;
- a read-only member;
- Arabic RTL and phone width.

See `docs/sessions/2026-11-20-confidential-lead-fields.md`.

## Requirement IDs

crm-backend #73–#78 (tracker #72). Decisions D620–D629.

## What is not covered

- **Scoring conditions the editor can't author** (stage, service, `in` lists, nested groups) are kept as written but can't be created in the editor.
- **Server validation messages** other than the D627 finding are shown in the server's English.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
