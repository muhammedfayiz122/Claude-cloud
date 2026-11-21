## Why

The workspace tracker (crm-backend #72) asks for proof that a governed organization keeps business units apart on every surface, and for the leaks to be fixed. This MR covers #73–#78:
- approvals, notifications and task artifacts (#74);
- documents across unit links (#75);
- service record-graph inheritance (#76);
- confidential Lead fields (#77);
- process selection by business context (#78).

It does not turn on the governance switch; `legacy` organizations behave as before. It proves the isolation and fixes what leaked. The frontend half is the crm-frontend MR from the branch of the same name.

## What changed

**Isolation matrix**
- `tests/isolation/test_multi_unit_isolation_matrix.py` sets up two business units, a member in each unit, a dual-unit member, a department-scoped member, an organization-wide member and an administrator.
- It runs over 37 HTTP surfaces: lists, details, search, reports and figures, exports, Timeline, notifications, files on Leads, Proposals and Services, tasks, activities, payments, the approval queue, task subject and artifact, cases, inbox, duplicates, participants, completion approval, and customer aggregates.
- Each unit's records carry a secret word, and every response the other unit receives is searched for it.
- A revocation test checks that a revoked grant closes every surface on the next request.

**Fixes found by the matrix**
- `getDocument` asks `document.read` as the content does (D620).
- `getTimelineEntry` asks the history's own kind gate (D621).
- A notification about a record out of reach is not shown, in the feed, the counts or the stream (D622, amends D453).
- A Journey selects its process by its record's business context (D623, #78).
- A confidential field's metadata follows the owner's record read (D624).

**Service record graph (#76)**
- `tests/isolation/test_service_record_graph.py` covers:
  - inheritance from the source opportunity;
  - contradicting and unreachable sources;
  - `target_required`;
  - a moved service taking its files, tasks and completion approval with it.

**Confidential Lead fields (D625, #77)**
- New keys `lead.confidential.read` and `lead.confidential.edit`.
- Confidential values are withheld from the record, the list, AI reads, message placeholders and duplicate matching.
- Writes to them are refused (403 `field_not_writable`).
- They cannot be filtered, sorted or searched.

**Rules may not leak a confidential field (D627, D628)**
- Making a field confidential while a published scoring, routing or duplicate rule names it is refused with 409 `confidential_field_decides_behaviour`, which lists the rules.
- The existing uses (automations, entry forms, pipeline assignments) now refuse with 409 instead of 422.
- In existing data, a confidential criterion decides nothing at run time, and validation lists it.

**Lead scoring editor API (D629)**
- Each version carries its rules.
- Holders of `lead_scoring.explain` can read the configuration.
- Publish takes If-Match.
- Validation gives a structured `confidential_field` finding.

**Approval policies (D626, #74)**
- Validate, publish and simulate warn `no_approver_in_isolated_context` for a step nobody could decide inside an isolated context.

No migrations.

## How to verify

```bash
make check
make test-all
```

Results on the head (e1bf5721b), run locally:

| Suite | Passed |
|---|---|
| gates | 2454 |
| isolation | 3444 |
| contract | 142 |
| unit | 13622 |
| integration | 11936 |
| `.claude/tests` | 1223 |

The compat fingerprint passes under Python 3.12.

Three things fail only locally:
- `test_s3_object_store` (2): the local S3 is moto, not MinIO.
- The `tests/app_cache.py` 16-application cap (106 errors): it is hit only with 2–3 xdist workers. The affected files pass on rerun (142 passed).
- The compat fingerprint test fails under Python 3.13, which is why the result above was taken under 3.12.

Browser checks, against crm-frontend on the same branch:
- confidential field holder vs non-holder, including Arabic;
- the D628 refusal resolved entirely in the UI through the new Lead scoring editor;
- a read-only member;
- phone width.

See `docs/session-log/2026-11-20-multi-unit-isolation-verified.md`.

## Requirement IDs

crm-backend #73, #74, #75, #76, #77, #78 (tracker #72). Decisions D620–D629.

## What is not covered

- **`proposal_commands_of_mr_524`** stays `pending`. Flipping it is the owner's decision; its evidence passes.
- **Legacy organizations:** a file on a Proposal answers to `document.read` alone. Proposal is not in `GATED_CONTEXT_KINDS`. This is recorded in the legacy matrix and not changed.
- **Approval policy publish** does not warn about an approver set that an isolation pair makes empty. At run time the stage blocks with `no_eligible_approver`.
- **Other workspace issues:** presets, delegated administration, identity modes and handoffs (#79, #82–#84) and process selection (#80, #81) come in their own MRs.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
