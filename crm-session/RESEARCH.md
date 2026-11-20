# Enterprise CRM behaviour research (access, naming, bulk actions, BUs, orders)

Date: 2026-11-20. Sources: vendor documentation (developer.salesforce.com / Trailhead, learn.microsoft.com, help.zoho.com / zoho.com/crm, knowledge.hubspot.com, academy.creatio.com). help.salesforce.com article pages could not be fetched directly (JS shell), so Salesforce statements cite the equivalent developer/architect docs, which say the same thing. Points marked *(unverified)* come only from secondary sources or memory and should be checked before quoting to customers.

Our terms: "person field" = a user lookup on a record (e.g. CPA on a Service Instance) that grants that user read/edit on the record. "Lent customer" = the read-only access to the record's Customer we grant today.

---

## 1. Customer lent through a person field or share: should child records follow?

### What each CRM does

**Salesforce: implicit sharing.**
- *Parent implicit sharing*: a user with access to a child Opportunity, Case or Contact automatically gets **read-only access to the parent Account only**. That is the account record itself, not the account's other children (no sibling opportunities, cases, contacts or activities). It is not configurable, and it is not used where the child is "Controlled by Parent".
- *Child implicit sharing*: the **account owner** gets access to the account's children, at a level set per role (View / Edit / None for Opportunities, Cases and Contacts).
- Activities on the account are visible only through the activity rules (see Q2), and only for records the user can already reach.
- https://developer.salesforce.com/docs/platform/draes/guide/draes-object-relationships-implicit-sharing.html
- https://developer.salesforce.com/docs/platform/salesforce-record-access-under-the-hood/guide/uth-grants.html

**Dynamics 365 / Dataverse: cascading per relationship.**
- Every 1:N relationship has a CascadeConfiguration for `Share`, `Unshare`, `Assign`, `Reparent`, `Delete` and `Merge`. The options are Cascade All, Cascade Active, Cascade User-Owned and Cascade None.
- With "Parental" behaviour (e.g. Account → Opportunities, Activities), **sharing the Account cascades the share down to its children**.
- `Reparent` gives "inherited access": the owner of a child gets access to the new parent.
- The direction is the opposite of Salesforce. Sharing the parent pushes access down to children, but access to a child does not grant the parent. Admins can switch any relationship to Configurable Cascading or Cascade None.
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/configure-entity-relationship-cascading-behavior
- https://learn.microsoft.com/en-us/power-apps/maker/data-platform/create-edit-entity-relationships
- https://learn.microsoft.com/en-us/troubleshoot/power-platform/power-apps/dataverse/cleanup-inherited-access

**Zoho CRM: the sharer chooses.**
- When a record is shared manually, the sharer ticks **"With Related List"** and can set a *different* permission for the related lists (e.g. Account Read/Write, related Contacts and open Activities Read Only).
- **Not shared** even then: closed activities, invited meetings, products, campaigns, contact roles, and integration related lists.
- Profile permissions still cap whatever the share grants.
- https://help.zoho.com/portal/en/kb/crm-v2-1/security-control/manage-data-sharing/articles/crm-v2-share-records
- https://www.zoho.com/crm/help/security/record-level-sharing.html

**HubSpot: record scope per object.**
- Each object is scoped to All / Team / Owned (+ Unassigned).
- A user can **see associated records as association cards** even when those records are hidden from them (e.g. restricted pipelines). Opening an associated record still requires access to it.
- Logging activities or notes needs the separate "Communicate" permission.
- https://knowledge.hubspot.com/records/assign-access-to-records
- https://knowledge.hubspot.com/settings/hubspot-user-permissions-guide

### Common pattern
- Access to a child grants **read of the parent header only** (Salesforce). Any wider spread is **explicit and chosen**: a per-relationship cascade set by the admin (Dynamics) or a "share with related lists" choice made by the sharer (Zoho).
- No vendor gives a person on one child record all of the account's other children by default.

### Recommendation
- **Default: keep today's behaviour.** A person-field or share grantee sees the Customer header read-only, plus only the activities, tasks and notes attached to *the granting record itself*.
- **Do not include** the customer's other opportunities, service files or proposals, or the customer-level activity timeline.
- Customer-level notes and activities that are not tied to the granting record stay hidden. Show a count or "N more items you don't have access to" at most.
- **Admin setting** (per person-field definition and per share): "Also grant access to the customer's related records". The options are `None` (default) / `Activities & notes on customer (read)` / `All related records of type X (read)`. This mirrors Dynamics cascade per relationship and Zoho "with related lists".
- Keep it per field definition, so a "CPA" field can be configured differently from an "Assistant" field.

---

## 2. Task holder reading the parent record's customer

### What each CRM does

**Salesforce.**
- Activity access is either Private or **"Controlled by Parent"**. Under Controlled by Parent, a user who can read the related record (WhatId/WhoId) can read the activity.
- The **assignee (owner) of a task always sees the task itself**, along with users above them in the role hierarchy.
- Owning a task does **not** grant access to the related Account, Opportunity or Contact. If the assignee lacks access to the parent, they see the task with the "Related To" name, but cannot open the parent record. *(Standard behaviour; consistent with activity sharing docs, help.salesforce.com `activities_access.htm` could not be fetched.)*
- https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_standard_objects_task_event_shared.htm (shared activities / parent records)
- Trailhead, Data Security: https://trailhead.salesforce.com/content/learn/modules/data_security/data_security_records

**Dynamics 365.**
- Activities (Task etc.) are their own user-owned records, secured by Activity privileges.
- Being owner or assignee of a task gives access to the task, **not** to the `regardingobjectid` (Account/Opportunity). The lookup renders as a name, but opening it requires the user's own Read privilege or a share.
- The reverse direction exists: sharing or assigning the Account cascades to its activities via Parental cascade.
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/configure-entity-relationship-cascading-behavior
- https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges

**Zoho CRM.**
- Activities belong to their parent and are shared only with it.
- A task owner sees their own task and the "Related To" name. Access to the Account or Deal still follows the role, territory and sharing rules.
- https://help.zoho.com/portal/en/kb/crm-v2-1/security-control/manage-data-sharing/articles/crm-v2-share-records

**HubSpot.**
- A task assigned to a user is visible to that user.
- Associated records show as cards, but opening them follows the object scope.
- https://knowledge.hubspot.com/records/assign-access-to-records

### Common pattern
- **The task does not open the parent.** The assignee sees the task, plus the parent's and the customer's *display name* (enough context to do the work), but not the parent record.
- Wider access must come from the role, a share, or a team.

### Recommendation
- **Default:** a task assignee gets the task (read/edit as assignee), plus a **name-only reference** to the parent record and its customer: title, a clickable chip and contact details that are needed to act (phone/email of the task's contact, if the task is on a contact).
- **No lent customer read by default.**
- **Admin setting (per tenant or per task type):** "Task assignees may read the related customer". Values: `Off` (default) / `Read customer header` (same as person-field lending).
  - Recommend turning it on for service-delivery tenants, where tasks are routinely handed to outside specialists who need the customer's address and identifiers.
- Never cascade from a task to sibling records.

---

## 3. Converting a field-given (rule/implicit) share into a manual share

### What each CRM does

**Salesforce.**
- Each share row has a `RowCause`: Owner, Manual, Rule (sharing rule), Team, Territory, ImplicitChild/Parent, or a custom **Apex sharing reason**.
- System-maintained rows (Rule, Team, Territory, implicit) are **recalculated and removed automatically** when criteria change. They cannot be edited into Manual ones; there is **no "convert" action**.
- To keep access, an admin **adds a separate Manual share** (Sharing button), which coexists with the rule share. Effective access is the maximum of all rows.
- Manual shares are dropped on owner change. Apex-reason shares survive owner change.
- https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_bulk_sharing_understanding.htm
- https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_bulk_sharing_creating_with_apex.htm

**Dynamics 365.**
- Access-team membership (template-based, per record) and explicit shares (PrincipalObjectAccess) are **distinct mechanisms**, with no conversion between them.
- Removing a user from the access team removes that grant. To keep access, the admin shares the record with the user directly.
- https://learn.microsoft.com/en-us/power-platform/admin/create-team-template-add-entity-form
- https://learn.microsoft.com/en-us/power-platform/admin/manage-principalobjectaccess-storage

**Zoho.**
- Rule-based (data sharing rules / territory) access is recalculated.
- Manual share is a separate list ("Shared with"). There is no conversion.
- https://help.zoho.com/portal/en/kb/crm/security-control/manage-data-sharing/articles/data-sharing-rules

### Common pattern
- Grants are stored per cause, and system causes are owned by the system.
- To "keep" access, a human adds an **independent manual grant**. The rule grant is never mutated.
- The UI typically lists all reasons a user has access (Salesforce "Sharing Hierarchy / View Access", Dynamics "Check Access").

### Recommendation
- Do **not** mutate the field-derived grant. Offer a one-click **"Keep access (add manual share)"** action on the access panel, next to a field-derived participant. It creates a new `record_participants` row with `source=manual` at the same level, records who and when, and leaves the field-derived row intact.
- When the field later changes, only the field-derived row is removed. The manual row stays.
- Show both causes in the "Who has access / why" panel.
- Permission: record owner, or a user with the "Manage sharing" right.
- Optionally, when an admin changes the person field, prompt: "Remove X's access" (default) or "Keep X as manual participant".

---

## 4. Member-name lookup for non-admins (user directory)

### What each CRM does

**Salesforce.**
- User records have their own org-wide default (Public Read Only or Private, internal and external separately).
- With **Public Read Only** (the default for internal users), every internal user can look up and see all internal users.
- With **Private**, users see themselves, their role-hierarchy subordinates, and users shared via user sharing rules or groups.
- **"View All Users"** (implied by "Manage Users") bypasses the restriction.
- External/community users default to seeing only users in their community.
- Field-level security still hides individual User fields.
- https://resources.docs.salesforce.com/242/latest/en-us/sfdc/pdf/salesforce_sharing_users_tipsheet.pdf
- https://developer.salesforce.com/blogs/2013/09/user-sharing-control-who-sees-who-in-your-organization

**Dynamics 365.**
- The User (systemuser) table is secured by role privileges.
- Standard roles (e.g. Basic User) grant Read on User broadly, so lookups and owner pickers list all users *(scope per role; check Basic User in the environment)*.
- Sensitive columns can be hidden with column security.
- https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/user-team-entities

**Zoho CRM.**
- All users are visible in user lookups and assignment pickers by default.
- A profile option restricts a user to **"Subordinates only"**. It applies to assignment, record sharing, **user lookup fields** and @mentions, and limits the visible user list. It is off by default and cannot be enabled for admins.
- https://help.zoho.com/portal/en-gb/community/topic/enhancements-in-user-management-listing-and-managing-subordinates

**HubSpot.**
- Owner and user dropdowns show all users in the portal.
- User management (roles, emails, permissions) is restricted to admins and users with "Users & Teams" permission.
- https://knowledge.hubspot.com/settings/hubspot-user-permissions-guide

### Common pattern
- **Internal users can see the names of all other internal users by default**, because pickers, owners and @mentions need it.
- The restriction is (a) an optional org-level "private user directory" limited to hierarchy or team, and (b) field-level hiding of profile details.
- Managing users and seeing security settings is admin-only.
- External users are restricted by default.

### Recommendation
- Provide a **narrow member-lookup endpoint** for all authenticated internal members: `id, display name, avatar, active/inactive status`, plus optionally job title and department.
- No email, phone, roles, permissions, last login or employment data. A **full profile** requires the "Manage members" permission, or the user viewing themselves.
- **Admin setting "Member directory visibility":** `All members` (default) / `Same department(s) + my hierarchy` (mirrors Salesforce Private user OWD and Zoho "Subordinates only").
- External or portal users always get only the members they collaborate with on shared records.
- Inactive users remain resolvable by id, so historical names render, but are excluded from pickers.

---

## 5. Lead name vs primary contact name precedence

### What each CRM does

**Salesforce.**
- Lead `Name` is a compound of First/Middle/Last/Suffix: **the person's name is the record name**.
- `LastName` and `Company` are required, and Company is a separate field.
- Lists, headers and global search show the person name, with Company as a column or secondary field. This is not configurable, though list columns are.
- Opportunity has its own free-text `Name`, often built by a convention or Flow like "Acme – Renewal".
- https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_lead.htm

**Dynamics 365.**
- Lead primary name attribute = `fullname` (first + last, format set org-wide).
- `subject` ("**Topic**") is required on create and describes the need, e.g. "100 laptops for Contoso".
- The form header and lookups use the full name. Views commonly show Name, Topic and Company as columns.
- Admins can change the default view columns and Quick Find columns, but not the primary-name column.
- https://learn.microsoft.com/en-us/dynamics365/sales/developer/entities/lead
- https://learn.microsoft.com/en-us/dynamics365/sales/create-edit-lead-sales

**Zoho CRM.**
- Lead Name = First + Last (Last Name mandatory), with Company a separate mandatory field.
- Deals have a free-text Deal Name.
- https://www.zoho.com/crm/help/leads/

**HubSpot.**
- No lead-as-person record. Contacts are named by first/last name.
- **Deals** have a free-text "Deal name". It can be templated with tokens such as company name or first name on the create form, and is shown in boards, lists and headers.
- The associated primary contact or company appears as a card, not as the name.
- https://knowledge.hubspot.com/object-settings/set-defaults-for-creating-deals

**Creatio.**
- Lead has a `Name` (LeadName) **filled by an out-of-the-box business process**, plus Contact and Account fields.
- The default page heading is built as "Customer need / Contact name, Account name".
- It is configurable by changing the process or the page.
- https://academy.creatio.com/guides/creatio-apps/8.3/products/sales-tools/lead-and-opportunity-management/leads/new-lead

### Common pattern
- **Person-centric lead objects** (Salesforce, Dynamics, Zoho) use the **person name** as the record name, with the need or company shown alongside.
- **Deal/opportunity-centric objects** (HubSpot deals, Salesforce/Zoho opportunities, Creatio lead with need) use a **free-text or templated title**.
- Where both exist, the title or need describes the work, and the person is shown as a secondary line. Creatio's "need / contact, account" heading is the closest to our model.

### Recommendation
- Our lead is closer to an opportunity (per-pipeline name template "{company} – {service}"). Use **precedence: explicit/template title → primary contact full name → company name → "Lead #<number>"**.
- In headers show the **title as primary** and "primary contact · company" as the subtitle.
- In lists show a Title column plus separate Contact and Company columns.
- **Search must match all three** (title, contact name, company).
- **Admin setting per pipeline:** "Record display name" = `Template title` (default when a template exists) / `Primary contact name` (Salesforce-style, for B2C pipelines).
- The template is re-evaluated only while the title has not been manually edited. Store a `title_is_custom` flag.

---

## 6. Bulk lead transfer and reason-required rules

### What each CRM does

**Salesforce.**
- Interactive **Mass Transfer Records** and list-view mass actions run validation rules per record. Records that fail are reported, and the others are saved.
- APIs make this explicit: `allOrNone=false` (the default for sObject Collections) returns a **per-record success/errors array**. `allOrNone=true` rolls the whole batch back and marks the good records `ALL_OR_NONE_OPERATION_ROLLED_BACK`.
- Typical per-record errors: `TRANSFER_REQUIRES_READ` and validation exceptions.
- https://developer.salesforce.com/docs/platform/api-rest/guide/resources-composite-allornone.html
- https://developer.salesforce.com/docs/platform/api-rest/guide/resources-composite-sobjects-collections-create.html

**Dynamics 365.**
- `ExecuteMultiple` runs **each request in its own transaction**. With `ContinueOnError=true`, faults are returned per `RequestIndex` and the rest succeed.
- The newer CreateMultiple/UpdateMultiple roll back the whole batch on standard tables.
- UI bulk "Assign" processes the selected rows and reports failures.
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/org-service/execute-multiple-requests
- https://learn.microsoft.com/en-us/power-apps/developer/data-platform/bulk-operations

**Zoho CRM.**
- Mass Change Owner / mass transfer is an **asynchronous job**, and its status is fetched via a job id. Records are processed individually.
- https://www.zoho.com/crm/developer/docs/api/v7/mass-change-owner.html *(path per Zoho API docs; see the Kaizen #251 post: https://help.zoho.com/portal/en/community/topic/kaizen-251-mass-actions-apis-in-zoho-crm-automating-lead-assignment-lead-conversion-conversion)*

**Oracle Sales.**
- Mass transfer runs as a job, with per-job status (completed/errored) on a "Mass Transfer Status" page.
- https://docs.oracle.com/en/cloud/saas/sales/oasal/transfer-records-between-users.html

### Common pattern
- UI mass actions are **per-record, best-effort, with a result report**.
- All-or-nothing exists only as an explicit API option.
- None of the vendors asks for a different reason per record inside the mass dialog. Mandatory values (e.g. a reason) are collected once in the dialog and applied to all records, and records that still fail their own rules are reported as failed.

### Recommendation
1. **Pre-flight.** Before executing, group the selection by pipeline and compute the union of requirements: "3 pipelines; 2 require a reason".
2. **Collect once.** Show one reason picker if any selected pipeline requires a reason. Allow a free-text note.
   - If pipelines use *different reason lists*, show one picker per pipeline group (usually 1–3).
   - The reason is applied to all records; pipelines that don't require one store it anyway as an optional note.
3. **Execute per record in its own transaction (best-effort).** Return a result list `{id, status: ok|failed|skipped, error_code, message}` with a summary ("47 transferred, 3 failed: reason missing for pipeline X / no permission").
   - Offer "Retry failed" and CSV export of the failures.
4. **Admin or API option `atomic=true`** for integrations that need all-or-nothing. Default false.
5. Run large selections (> ~200) as a background job with progress and a notification. Write an audit entry per record (old owner, new owner, reason, batch id).

---

## 7. Business-unit separation presets

### What each CRM does

**Dynamics 365 / Dataverse.**
- **Business units** are a security hierarchy. Role privileges are scoped User / BU / Parent-Child BU / Organization.
- Records are owned by a user or team and stamped with an owning BU.
- **Modernized BUs ("Record ownership across business units")**: a user can hold roles in several BUs, and records can be owned in a BU other than the owner's home BU. This makes "shared vs separate" a matter of role assignment rather than structure.
- **Accounts are ordinary owned records.** One account belongs to one BU, and users in other BUs see it only with an Organization-scope Read or a share.
- Common practice for shared customer identity is Org-level Read on Account/Contact with BU-level on Opportunities/Cases.
- https://learn.microsoft.com/en-us/power-platform/admin/wp-security-cds
- https://learn.microsoft.com/en-us/power-platform/admin/modernized-business-units-security
- https://learn.microsoft.com/en-us/power-platform/admin/security-roles-privileges

**Salesforce.**
- Separation comes from **OWD** (Private / Public Read Only / Public Read/Write per object), the **role hierarchy** (managers see subordinates' records), **sharing rules** (by role, group or criteria), and **Enterprise Territory Management** (an account can sit in several territories, which share it with their users).
- **Divisions** are a data-partitioning feature for very large orgs (>1M records in one object). They narrow search, list views and reports, and are **not a security boundary**.
- Accounts are single, shared-identity records. Separate units usually means Private OWD with sharing rules, or a separate org.
- https://developer.salesforce.com/docs/platform/salesforce-large-data-volumes-bp/guide/ldv-deployments-infrastructure-divisions.html
- https://developer.salesforce.com/docs/atlas.en-us.salesforce_sharing_cheatsheet.meta/salesforce_sharing_cheatsheet/sharing_cheatsheet.htm

**Zoho CRM.**
- Separation comes from the role hierarchy, module-level Private/Public default, **data sharing rules** (role or group to role or group, criteria-based), and **territories** (a record matching several territories is assigned to all of them).
- **Teamspaces**: *organization modules* (Accounts, Contacts, etc.) are shared across teamspaces under central admin control, while *team modules* are private to one teamspace.
- In other words, customer identity is org-wide and team-specific work can be siloed.
- https://help.zoho.com/portal/en/kb/crm/security-control/manage-data-sharing/articles/data-sharing-rules
- https://help.zoho.com/portal/en/kb/crm/users-and-control/territory-management/articles/assign-territories
- https://help.zoho.com/portal/en/kb/crm/using-crm-for-everyone/team-module/articles/faqs-team-module

**HubSpot.**
- **Brands (formerly Business Units)** sit inside one portal. Contacts, companies and deals can be associated with **multiple brands**, so the CRM database and identity are shared, and brand is a property used for segmentation and asset partitioning.
- Record visibility is Team/Owned scope.
- https://knowledge.hubspot.com/account/manage-brands-with-business-unit
- https://knowledge.hubspot.com/account/partition-your-hubspot-assets

**Creatio.**
- Organizational roles (divisions, with inherited permissions) and functional roles. Object operation permissions (CRUD per object) combine with **record permissions** (per record, by role, granted on create).
- A department-separated setup gives each division's org role read/edit on its records. Accounts are typically readable by all employees.
- https://academy.creatio.com/guides/setup-and-administration/8.3/administration/user-and-access-management/user-management/organizational-roles
- https://academy.creatio.com/docs/user/setup_and_administration/user_and_access_management/access_management/operation_permissions

### Common pattern
- All of them keep **one customer master per tenant** (shared identity; dedupe across units). They separate the **work records** (opportunities, cases, orders, activities) by unit.
- **Full separation of customer identity** is achieved only by separate orgs or environments, or by locking the Account object to BU scope (Dynamics), and is rare.

### Recommended presets

| Preset | Customer (Account/Contact) identity | Customer record visibility | Work records (Leads, Opps, Service files, Proposals, Tasks) | Cross-unit collaboration |
|---|---|---|---|---|
| **Collaborative** (default) | Shared, one master | All members read; edit by owner/unit | All departments read; edit per role scope | Free: anyone can be added via shares/person fields |
| **Private** | Shared, one master | All members can find and see the **header** (name, identifiers, owner unit); details and related lists only in units with work on it | Own department only (role scope Department) + explicit shares | Allowed via explicit share or person field; Q1 lending applies |
| **Strict** | **Shared identity, partitioned visibility**: dedupe still global; a unit sees a customer only if it owns or has a work record for it | Hidden from other units (duplicate check says "exists in another unit, request access") | Own department only; cross-unit shares need admin/approval | Cross-unit person-field grants disabled or admin-approved |

- Customer identity is **shared** (one master record) in all presets. That is what every vendor does and avoids duplicate customers.
- **Strict** changes *visibility*, not identity. A per-unit copy of customers would be a separate-tenant feature, not a preset.

---

## 8. Sales orders and payments (brief)

**Salesforce.**
- *Core Sales Cloud*: Quote → "Sync" to the Opportunity. Orders (Order + OrderItem) are created manually or by Flow; there is no native quote-to-order button in core.
- *CPQ / Revenue Cloud*: on the **primary quote**, tick **Ordered** (or Create Order) → an Order with Order Products is generated from the quote lines, copying product, quantity, prices, discounts, start date and subscription term. Optionally a subset of lines, or **separate orders per quote-line group** (e.g. one-time vs ongoing).
  - Recurring lines carry Subscription Type, Term and Billing Frequency. Activating and contracting the order creates **Contract + Subscriptions** (renewals), and Billing creates invoices and payment schedules.
- Payments are recorded in Salesforce Billing / Revenue Cloud (Payment, Payment Allocation) or in the ERP.
- Sales credit: **Opportunity Splits**. Revenue splits must total 100%; overlay splits can total any amount. Requires Team Selling. Commissions are computed in Spiff / ICM, typically on closed-won opp amount or booked orders.
- https://trailhead.salesforce.com/content/learn/modules/salesforce-cpq-order-generation/generate-your-first-order
- https://trailhead.salesforce.com/content/learn/modules/salesforce-cpq-order-generation/generate-multiple-orders-from-a-single-quote
- https://trailhead.salesforce.com/content/learn/modules/leads_opportunities_lightning_experience/sell-as-a-team-and-split-the-credit

**Dynamics 365 Sales.**
- Quote (Draft → **Activate**) → **Create Order** (Date Won and Description). **All quote products, the price list and the currency are copied**, and the quote is closed as Won.
- Order → **Create Invoice** (all order products copied).
- Payment: the **"Invoice Paid"** action, with status **Complete** or **Partial**. There is no payment ledger; detailed receivables live in Finance / Business Central.
- No native recurring lines. Subscriptions come via ISVs or Finance & Ops.
- Credit: the opportunity sales team (connection roles / access team). Revenue splits are handled by add-ons or customisation *(no native split feature found in Learn)*.
- https://learn.microsoft.com/en-us/dynamics365/sales/create-edit-order-sales
- https://learn.microsoft.com/en-us/dynamics365/sales/create-edit-invoice-sales
- https://learn.microsoft.com/en-us/training/modules/process-sales-orders-dynamics-365-sales/3-orders-and-invoices

**Zoho CRM.**
- Quote → **Convert → Sales Order / Invoice** (or **Mass Convert** from list view). Standard fields and product line items are copied, and **custom fields must be mapped beforehand** (quote → SO/invoice field mapping).
- SO → Invoice by convert.
- Payments and recurring invoices are handled in **Zoho Books / Zoho Invoice** (synced: payment status, payments received).
- Credit is by Deal owner; commissions via Books or Analytics customisation.
- https://help.zoho.com/portal/en/kb/crm-v2-1/manage-inventory/quotes/articles/crm-v2-create-quotes
- https://help.zoho.com/portal/en/kb/articles/create-sales-orders

### Common pattern
- An accepted (activated / primary) quote generates the order by **copying the header** (account, contacts, currency, price list, addresses, terms) **and all lines** (product, description, qty, unit price, discount, tax). The order keeps a link back to the quote and opportunity, and the quote is locked.
- Recurring items keep their term and frequency and spawn contract/subscription records.
- Payments are recorded against **invoices**, not orders, and supporting partial payments.
- **Salesperson credit derives from the opportunity** (owner + splits), not from the payment.

### Recommendation for us
- **Proposal (accepted) → Sales Order.**
  - One-click "Create order", allowed only from an accepted proposal.
  - Copies the header, all lines (or a selected subset, Salesforce-style) and the field mapping for custom fields (Zoho-style mapping table).
  - Locks the proposal and links Proposal ↔ Order ↔ Opportunity.
- **Recurring lines** keep `billing_frequency`, `term` and `start_date` and generate a schedule of billable periods. Optionally split into "one-time" and "recurring" orders.
- **Payments.** A `payment` entity (amount, date, method, reference) with **allocations to order or invoice lines**, supporting partial and over-payment. Order status: Unpaid / Partially paid / Paid.
- **Attribution.** A `sales_credit` table on the opportunity/order: user, role (primary/overlay), percent.
  - Default: 100% to the opportunity owner; the primary split must total 100%.
  - Commission reporting = payments received × credit percent, so paid-basis attribution is computed rather than stored on the payment.
