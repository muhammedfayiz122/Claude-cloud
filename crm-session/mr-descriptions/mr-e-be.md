## Why

The workspace tracker (crm-backend #72) asks that an organization be able to run business units the way it wants, without a second authorization engine:
- collaborative, private or strict collaboration;
- department administrators who cannot touch the rest of the tenant;
- customers shared or restricted per unit;
- narrow, time-bound handoffs instead of broad sharing.

This MR covers crm-backend #79, #82, #83 and #84, and the server side of crm-frontend #71. Legacy organizations are unchanged, and Collaborative is the default.

**Stacked on crm-backend !683 (MR C, G1).** It targets that branch and moves onto `develop` when !683 merges. The frontend half is the crm-frontend MR from the branch of the same name.

## What changed

**Presets (#79, D660, D661)**
- Collaborative, Private and Strict only set existing governance primitives on the unit's own row: confidential, identity mode and handoff policy.
- A preset never declares an isolation pair, grants a role or switches governance on.
- The administrator previews a plan before applying it. The plan shows what changes, who gains or loses reach, and any warnings, blocks and next steps.
- Apply needs the plan's digest and the policy revision. It runs under the organization access lock, is versioned in `business_unit_setups`, and is audited.
- Changing the preset later shows the difference.

**Delegated unit administration (#82, D662)**
- The organization administrator names `business_unit_administrators` per unit, with areas (members, defaults, workspaces) and the roles a delegate may give.
- A delegate works only inside their own unit and never on themselves. The refusals are `role_not_assignable` and `delegated_self_change`.

**Customer identity (#83, D663–D665)**
- There is one canonical customer store. A unit is either shared or restricted.
- In a restricted unit, the customers it has work on are hidden from anyone who reaches none of that work.
- The relationship owner, the unit's members and an organization-wide `all` grant still read them.
- Restricted customers stay out of duplicate checks; their duplicates go to central review (D664).
- When a separate tenant, not a unit, is the right boundary is documented in CRM-GOV-001 §14 (D665).
- **Pre-existing fix:** a governed customer detail returned 404 where the list showed the row.

**Scoped handoffs (#84, D666, D667, D669)**
- A handoff gives one Lead or deal to one colleague for one purpose (review, decision or assist), for chosen categories, ending within 90 days.
- The unit's policy decides the flow:
  - open: the handoff is active at once;
  - approval: it is held, and unseen, until a sharer approves;
  - closed: it is refused. An isolation pair also refuses it.
- Access is an ordinary participant share with `share_origin = 'handoff'` and `access_until`. Every access predicate honours `access_until` at read time, so expiry needs no tick.
- An answer, cancel, revoke, expiry, or leaving or removing the share ends the handoff, through a `kernel.share_ends` hook in the same transaction.
- Notices go to the colleague, the approvers who could decide it and the requester. Each is written only to people who may open the record.
- Every act is audited and checked against the handoff's revision (412 if it moved).
- Request handover is a published Lead record action. The handoff's own acts are recorded as deliberately not record actions.
- **Services are excluded,** because they have no participation; D666 gives the reason and the access-team reference.

**Access check (D668)**
- Shows a member's keys and the units they reach, never their records.

**Schema**
- Migrations 0640–0647, chained on develop's 0519.
- New tables are in every isolation sweep and both migration gates.
- The deal foreign key is added NOT VALID and validated by `deploy/sql/validate_foreign_keys.sql`.
- COMPAT_VERSION 30, fingerprint computed under Python 3.12.

**Behaviour change**
- A member may leave their own Lead share or deal participation without the share key. Removing anyone else still needs it.

## How to verify

```bash
make check
make test-all
```

Run locally on the head:

| Suite | Result |
|---|---|
| gates | 2475 passed |
| isolation | 3471 passed |
| contract | 142 passed |
| `.claude/tests` | 1232 passed |
| unit | 13637 passed; the published-actions guard failure is fixed in 4fc6fe92e (unit + contract rerun: 13781) |
| integration | 11957 passed |

Known local-only failures:
- `test_s3_object_store`: the local S3 is moto, not MinIO.
- The `app_cache` cap: the affected files pass on rerun (142 passed).

Browser checks on a preview organization with units and restricted personas:
- the wizard and every preset;
- delegated limits;
- restricted identity;
- a Lead and a deal handoff end to end, including approval, answer, leave and expiry;
- Arabic RTL and phone width.

See `docs/session-log/2026-11-20-unit-presets-and-handoffs.md`.

## Requirement IDs

- crm-backend #79, #82, #83, #84 (tracker #72)
- crm-frontend #71
- Decisions D660–D669

## What is not covered

- **Approver notices** go to at most 50 members. The others find the handoff in their "To approve" box.
- **Services:** handoffs cover Leads and deals only (D666).
- **COMPAT_VERSION 30** is also used by crm-backend !680. Whichever merges second must recompute and bump it.
- **Pre-existing:** a share-only reader gets 404 from `/records/{kind}/{id}/responsibility`. The page tolerates it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
