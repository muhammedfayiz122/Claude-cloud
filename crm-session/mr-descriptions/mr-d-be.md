## Why

The workspace tracker (crm-backend #72) asks that, in a governed organization, each department or business context can run its own process. That covers which proposal types it offers, which delivery pipeline a service starts on, and which lead page its members see, and every choice must be explainable. This MR covers crm-backend #80 and #81 and the server side of crm-frontend #70 and #72–#75.

Legacy organizations (governance off) behave as before. Presentation never widens access.

**Stacked on crm-backend !680 (MR A).** It targets that branch and moves onto `develop` when !680 merges. The frontend half is the crm-frontend MR from the branch of the same name.

## What changed

**Delivery pipeline precedence (#81, D640)**
- A delivered service's pipeline is chosen in this order:
  1. the Journey process's `service_pipeline_key`;
  2. the unit's classification default (now allowed for services);
  3. the field-value rule (develop's D557), then its default;
  4. the catalogue item.
- The level that chose it, and what it overrode, are stored on the service (`pipeline_selection`) and returned with names.
- `previewServiceDeliveryPipeline` answers without writing.
- Two unit defaults that disagree refuse the start with `pipeline_default_ambiguous`.
- A Journey's direct start and Start delivery use the same selector (D648).

**Proposal types per unit (#80, D641)**
- `proposal_type_targets` lets an organization offer a type to chosen units, with one default per unit.
- A create takes:
  - the type it names, if that type is offered there (otherwise 422 `proposal_type_not_offered`, the same answer as an unknown type);
  - else the unit's default;
  - else the standard type.
- `type_selection` records which rule applied.
- New `listProposalTypeOptions`. Unit-only creators can now list the types offered to them.

**Lead page by unit, and templates by pipeline or unit (frontend #70, D642, D649)**
- Layout precedence is own → pipeline → unit → role → organization.
- With page-layout templates on, an administrator can assign a published Company template to a pipeline or to a unit (`page_template_assignments`). The resolved page names the rule that chose it.
- This also closes MR A's open item, where a template could not be assigned to a pipeline.

**Fields per unit (frontend #72, D643)**
- A field's unit is the set of units its pipelines belong to. There is no second rule that could disagree.
- The leads list takes `?pipeline=`, which narrows the request on the server.

**Workspaces and dashboards (frontend #73, D644)**
- A workspace cannot place a member's private board; publishing one is refused with `dashboard_not_placeable`.

**Lead outcomes (frontend #74, D645)**
- The lead process decides where a win goes.
- A process that ends at the lead closes it with no opportunity. Before, the dialog offered an opportunity that the process then refused.
- The qualification assessment returns the process and the setting that decided.

**Provenance (frontend #75, D646)**
- Proposal, service and settings reads say where each choice came from.

**Other fixes**
- **Role layouts per unit:** not built (D647). Dynamics and Salesforce do not combine role and unit for forms. Role-by-pipeline is recorded as the candidate if this is reopened.
- **Unit-scoped readers:** `/service-delivery-pipelines` now reads with the service list's scope rule, so unit workers no longer get 403 (D648).

**Schema**
- Migrations 0620–0624, chained on MR A's 0542.
- `proposal_type_targets`, `page_layout_targets` and `page_template_assignments` are in every isolation sweep and both migration gates.
- COMPAT_VERSION is unchanged; the fingerprint passes under Python 3.12.

## How to verify

```bash
make check
make test-all
```

Local results on the head:

| Suite | Result |
|---|---|
| gates | 2533 passed |
| isolation | 3530 passed (rerun after the last fix) |
| contract | 142 passed |
| `.claude/tests` | 1256 passed |
| unit | 13728 passed, plus the 2 guard failures, fixed in ddf0feb5f |
| integration | 12037 passed |

The integration run's 7 `external_agent` failures were fixed in ddf0feb5f, and the rerun of `external_agent`, `proposal`, `service`, `business_process` and `page_layout` gave 1927 passed.

Two groups of local-only failures remain:
- `test_s3_object_store`: the local S3 is moto, not MinIO.
- The `app_cache` 16-application cap: those files pass on rerun (145 passed).

Browser checks, on a preview organization with two business contexts and a restricted member of each:
- every issue's flow;
- English and Arabic, including RTL at phone width.

See `docs/session-log/2026-11-20-context-process-selection.md`.

## Requirement IDs

- crm-backend #80, #81 (tracker #72)
- crm-frontend #70, #72, #73, #74, #75
- Decisions D640–D649

## What is not covered

- **Delegated configuration:** delegating `proposal.configure` inside a unit is in the presets MR (#82).
- **Lead list columns:** the column picker is not narrowed per pipeline without the pipeline filter, because a list spans pipelines. Each field is labelled with its pipelines instead.
- **Pre-existing, not changed:** a share-only reader gets 404 from `/records/{kind}/{id}/responsibility`. The page tolerates it.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01AXp6mCvfCtqUNVuUc5UBuj
