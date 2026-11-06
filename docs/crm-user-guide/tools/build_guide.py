import json, html

M = json.load(open('/home/user/crm/marks.json'))
OUT = '/home/user/Claude-cloud/docs/crm-user-guide/index.html'


def fig(img, caption, marks_key=None, notes=None, small=False):
    """A screenshot with optional numbered callouts drawn from recorded element boxes."""
    marks = M.get(marks_key or img, []) if marks_key is not False else []
    boxes, legend = [], []
    for i, m in enumerate(marks, 1):
        if 'x' not in m:
            continue
        half = min(m['w'], 2.78) / 2
        left, top = m['x'] - half, m['y'] - m['h'] / 2
        boxes.append(
            f'<span class="hot" style="left:{left - 0.7:.2f}%;top:{top - 0.9:.2f}%;'
            f'width:{m["w"] + 1.4:.2f}%;height:{m["h"] + 1.8:.2f}%"><b>{i}</b></span>')
        text = (notes or {}).get(m['label'], '')
        legend.append(f'<li><b>{i}</b><span><strong>{html.escape(m["label"])}</strong>'
                      f'{" — " + text if text else ""}</span></li>')
    cls = 'shot small' if small else 'shot'
    leg = f'<ol class="legend">{"".join(legend)}</ol>' if legend else ''
    return (f'<figure class="{cls}"><div class="frame"><img src="images/{img}.jpg" '
            f'alt="{html.escape(caption)}" loading="lazy">{"".join(boxes)}</div>'
            f'<figcaption>{caption}</figcaption>{leg}</figure>')


def steps(*items):
    return '<ol class="steps">' + ''.join(f'<li>{s}</li>' for s in items) + '</ol>'


def tip(text, kind='tip'):
    label = {'tip': 'Tip', 'note': 'Note', 'admin': 'Admins'}[kind]
    return f'<aside class="callout {kind}"><span>{label}</span><p>{text}</p></aside>'


def pair(a, b):
    return f'<div class="pair">{a}{b}</div>'


K = lambda k: f'<kbd>{k}</kbd>'
B = lambda b: f'<span class="ui">{b}</span>'

sections = []

def section(id_, eyebrow, title, body):
    sections.append((id_, eyebrow, title, body))

# ---------------------------------------------------------------- 1
section('tour', 'Start here', 'Find your way around', f'''
<p>Every screen in the CRM shares the same frame. The sidebar on the left lists the workspaces you have
access to, and the bar across the top holds search, the date, notifications and your account menu.
Workspaces you don't have permission for are hidden, so your sidebar may be shorter than the one shown here.</p>
{fig('shell', 'The application frame, shown on the Leads workspace.', notes={
  'Sidebar navigation': 'every workspace you can open. Hover an item and pin it to keep it at the top; the arrow at the top collapses the sidebar.',
  'Global search (Ctrl K)': 'find any record or jump to any screen from anywhere.',
  'Language switch': 'switches the interface language when your organisation offers more than one.',
  'Notifications': 'assignments, mentions, approvals and reminders addressed to you.',
  'Your account': 'organisation switcher, your profile and sign out.',
  'Assistant': 'ask the built-in assistant about your records.'})}
<h3>Search and jump with {K('Ctrl')} {K('K')}</h3>
<p>Press {K('Ctrl')} {K('K')} ({K('⌘')} {K('K')} on a Mac) on any screen and start typing. Results are grouped
into recently viewed items, records, actions you can take, things you can create, and screens you can go to.
Use the arrow keys and {K('Enter')} to open a result.</p>
{fig('command-palette', 'Typing “Aisha” finds the lead and offers to open it.', marks_key=False)}
''')

# ---------------------------------------------------------------- 2
section('setup', 'Administrators', 'First-time setup', f'''
<p>The first time an administrator opens a new organisation, the CRM walks them through six short steps.
Each step is saved as you go, and everything you choose can be changed later in {B('Settings')}.</p>
<div class="gallery">
{fig('setup-1', '<b>1 · Starting point.</b> Pick a template close to how you work. Each shows how many teams, pipeline stages and services it creates.', marks_key=False, small=True)}
{fig('setup-2', '<b>2 · Your teams.</b> Name a department and the teams inside it. Add or remove teams freely.', marks_key=False, small=True)}
{fig('setup-3', '<b>3 · Lead pipeline.</b> The stages a lead moves through. Mark which end as won and which as lost.', marks_key=False, small=True)}
{fig('setup-4', '<b>4 · Where new leads go.</b> Name the fallback queue that catches any lead not assigned automatically.', marks_key=False, small=True)}
{fig('setup-5', '<b>5 · Services you offer.</b> Optional. Add your service catalogue now or choose <i>Skip for now</i>.', marks_key=False, small=True)}
{fig('setup-6', '<b>6 · Ready to launch.</b> Review the summary and choose <i>Launch CRM</i>.', marks_key=False, small=True)}
</div>
{tip('If a step reports that it didn’t finish, some of it may already be saved. Read the summary on the last step before trying again, and contact support with the reference shown in the message if it repeats.', 'admin')}
''')

# ---------------------------------------------------------------- 3
section('leads', 'Leads', 'Work your lead list', f'''
<p>A <em>lead</em> is an enquiry from someone who might become a customer. The Leads workspace lists every
lead you are allowed to see, newest activity first. The count above the table always comes from the server,
so it reflects every matching lead, not only the rows on screen.</p>
{fig('leads-list', 'The Leads list.', notes={
  'Search leads': 'match on name, email or phone.',
  'Choose a view': 'switch between active, archived and all leads.',
  'Add filter': 'narrow by owner, source, stage, dates and any custom field.',
  'New Lead': 'open the new-lead form.',
  'Export': 'download the current view as a spreadsheet.',
  'Click a name to open the lead': 'opens the full lead record.'})}
{pair(fig('leads-views', 'The view menu: <i>Active</i>, <i>Archived</i> or <i>All</i> leads.', marks_key=False, small=True),
      fig('pools', '<b>Lead pools</b> let a team share incoming leads. Anyone in the team can claim one.', marks_key=False, small=True))}

<h3 id="create-lead">Create a lead</h3>
{steps(f'On the Leads screen choose the blue {B('+')} button (<i>New Lead</i>).',
       'Enter the person’s <b>Name</b>. It is the only required field.',
       'Pick the <b>Source</b> so reports can show which channels bring in business.',
       'Add an email and phone number. The phone field picks the country code from your organisation’s default.',
       'Type anything you learned in <b>Note</b>; it becomes the first note on the record.',
       'Leave <b>Stage</b> on <i>New</i> unless the lead has already been worked.',
       f'Leave <b>Assign to</b> on <i>Automated</i> to let your routing rules choose the owner, or pick a person to send it straight to them. Choose {B('Create lead')}.')}
{fig('lead-new', 'The New Lead panel, filled in.', notes={
  'Name (required)': '', 'Where the lead came from': 'Inbound call, Referral, Walk in, Website and any sources your admin adds.',
  'Contact details': '', 'First note': '', 'Starting stage': '',
  'Owner – leave on Automated to use routing': '', 'Save': ''})}
{tip('Your administrator decides which fields appear on this form and in what order. If you need a field that isn’t there, ask them to add it under Settings → Lead fields.', 'note')}
''')

# ---------------------------------------------------------------- 4
section('lead-record', 'Leads', 'Inside a lead record', f'''
<p>Open any lead to see everything about it on one page: who owns it, where it stands, what happened and
what is due next.</p>
{fig('lead-detail', 'A lead record.', notes={
  'Header actions': 'contact the lead, schedule a meeting, edit, close the inquiry (<i>Qualify</i>), transfer or share it. <i>Customize page</i> rearranges the blocks.',
  'Owner & assignment': 'who owns the lead and which queue or team it sits in. Use <i>Change</i> to reassign.',
  'Stage path – click a stage to move': 'shows progress through your pipeline. Click a later stage to move the lead there.',
  'Record tabs': 'Overview, Activity, Meetings, Timeline, Work, Files, Started services, Stage history and Contacts.',
  'Quick actions': 'call, WhatsApp, email, create a task, add a note or copy the lead’s details.',
  'Upcoming work': 'open tasks and meetings for this lead, with due dates.'})}

<h3>Move a lead through the pipeline</h3>
<p>Click the next stage in the stage path. The lead moves at once and a confirmation such as
“Aisha Rahman moved to Contacted” appears. Every move is kept under the <i>Stage history</i> tab.
Some organisations require approval for certain stages; when that applies, the move waits in the approver’s
{B('Approvals')} queue.</p>

<h3>Plan the next step</h3>
{pair(fig('lead-task', '<b>Create task</b>: title, type, due date and time, notes and an optional reminder.', marks_key=False, small=True),
      fig('lead-meeting', '<b>Schedule meeting</b>: subject, agenda, time and time zone, location or video link, guests and reminder.', marks_key=False, small=True))}

<h3>Close or hand over a lead</h3>
{pair(fig('lead-close', '<b>Qualify</b> closes the inquiry as <i>Engaged</i> (won) or <i>Declined</i> (lost).', marks_key=False, small=True),
      fig('lead-transfer', '<b>Transfer</b> hands the lead to a colleague or team, with an optional reason.', marks_key=False, small=True))}
{fig('lead-timeline', 'The Timeline tab records every change, meeting and task on the lead, newest first.', marks_key=False)}
''')

# ---------------------------------------------------------------- 5
section('daily', 'Your day', 'Follow-ups, My Work and the calendar', f'''
<p>When a follow-up falls due, the CRM tells you even if you are on another screen. Deal with each one in
place, or choose <i>Later</i> to come back to them.</p>
{fig('followups-due', 'The follow-ups-due reminder.', notes={
  'Complete, snooze or open the lead': '<i>Complete</i> closes the task, <i>Snooze</i> pushes it back, <i>Open lead</i> takes you to the record, <i>Dismiss</i> hides the reminder.',
  'Decide later': 'closes the reminder without changing anything. <i>Dismiss all</i> clears every reminder in the list.'})}

<h3>My Work</h3>
<p>My Work is your to-do list across every lead and customer. Overdue tasks are flagged in red and tasks due
today in amber. Each row lets you complete the task, log a call, schedule a meeting or jump to the lead.</p>
{fig('my-work', 'My Work, listing tasks across several leads.', notes={
  'Tasks / Reminders / My Day': '<i>My Day</i> combines today’s tasks and meetings.',
  'Due-date buckets': 'All, Overdue, Due today, Upcoming, Unassigned and Completed.',
  'Add task': 'create a task that isn’t tied to a record, or link one.'})}

<h3>Calendar and meetings</h3>
{fig('calendar', 'The calendar in week view, showing meetings and tasks.', notes={
  'Day / Week / Month': '', 'Schedule meeting': '',
  'Whose calendar': 'switch between your own items, everyone’s and your team’s. Turn on <i>Show cancelled</i> to see cancelled meetings.'})}
{pair(fig('meetings', '<b>Meetings</b> lists every meeting you can see, filtered by state and date.', marks_key=False, small=True),
      fig('notifications', '<b>Notifications</b> filter by unread, category and priority.', marks_key=False, small=True))}
{fig('inbox', '<b>Inbox</b> gathers email threads and WhatsApp conversations you work, split into Mine, Unassigned, Team and All.', marks_key=False)}
''')

# ---------------------------------------------------------------- 6
section('customers', 'Customers', 'Accounts and contacts', f'''
<p>An <em>account</em> is an organisation you do business with: a company, an authority or a partner.
A <em>contact</em> is a person. A contact can act for one or more accounts, or be a direct customer
in their own right.</p>
{fig('accounts', 'The Accounts list.', notes={
  'Columns & saved views': 'choose the columns you want and save the combination as a view.',
  'New account': 'only a name is required; add the legal name for documents.'})}
{fig('account-detail', 'An account record: information, related contacts, leads, opportunities, services, payments and documents.', marks_key=False)}
{pair(fig('contacts', 'The Contacts list.', marks_key=False, small=True),
      fig('contact-new', 'New contact: name, given and family name, preferred language and how to reach them.', marks_key=False, small=True))}
''')

# ---------------------------------------------------------------- 7
section('sales', 'Sales', 'Opportunities, proposals and approvals', f'''
<p>An <em>opportunity</em> is a deal you are working: who it is with, what it is worth, how likely it is to
close and when. Switch between a list and a board to see deals by stage.</p>
{fig('opps-list', 'Opportunities in list view.', notes={
  'List / Board': 'the board groups deals by stage with the total value of each column.',
  'New opportunity': 'link a customer, then enter the value, currency, expected close date and probability.'})}
{fig('opps-board', 'The board view. Use <i>Move to…</i> on a card to change its stage.', marks_key=False)}
{pair(fig('opp-new', 'Creating an opportunity.', marks_key=False, small=True),
      fig('opp-detail', 'An opportunity record, with <i>Mark won</i> and <i>Mark lost</i> at the top right.', marks_key=False, small=True))}
{pair(fig('proposals', '<b>Proposals</b> keeps each commercial proposal with its versions and approvals.', marks_key=False, small=True),
      fig('approvals', '<b>Approvals</b> collects decisions waiting on you: transfers, stage moves, proposals and service completions.', marks_key=False, small=True))}
''')

# ---------------------------------------------------------------- 8
section('insight', 'Insight', 'Dashboards and reports', f'''
<p>Every figure on a dashboard or report is counted by the server across the records you are allowed to see,
so two people may see different totals for the same report.</p>
{fig('dashboard', 'Your home dashboard.', notes={
  'Filters': 'limit every tile to a period, owner or team.',
  'Templates': 'start from a ready-made layout.',
  'Customize': 'add, remove and rearrange tiles.'})}
{fig('reports', 'The Reports workspace, showing the Lead Intake Summary.', notes={
  'Pick a report': '', 'Period & grouping': 'choose the period, the owner and how to group results (by day, week or month).',
  'Export CSV': 'download the report’s rows.'})}
''')

# ---------------------------------------------------------------- 9
section('marketing', 'Outreach', 'Segments, campaigns and imports', f'''
<div class="gallery three">
{fig('segments', '<b>Segments</b> are saved groups of leads or contacts to send campaigns to.', marks_key=False, small=True)}
{fig('campaigns', '<b>Campaigns</b> reach a segment by email, WhatsApp templates and call tasks, once or as a sequence.', marks_key=False, small=True)}
{fig('imports', '<b>Imports</b> bring in leads from a spreadsheet and keep a record of each import.', marks_key=False, small=True)}
</div>
''')

# ---------------------------------------------------------------- 10
section('admin', 'Administrators', 'Teams, queues and settings', f'''
{pair(fig('teams', '<b>Teams</b> group people who work together. Group teams into departments so a manager can see across them.', marks_key=False, small=True),
      fig('queues', '<b>Queues</b> hold unassigned work. The fallback queue receives any lead that routing could not place.', marks_key=False, small=True))}
{fig('settings', 'Settings.', notes={
  'Search settings': 'type what you want to change, such as “stages” or “time zone”.',
  'Quick access': 'organisation details, users and members, lead fields, roles and permissions, notifications.'})}
<p>Common changes:</p>
<table><thead><tr><th>To change…</th><th>Go to</th></tr></thead><tbody>
<tr><td>Organisation name, time zone, date format, languages</td><td>Settings → General → Organization</td></tr>
<tr><td>Who can sign in, and their roles</td><td>Settings → People &amp; access</td></tr>
<tr><td>Fields on the lead form and their order</td><td>Settings → Lead settings → Lead fields</td></tr>
<tr><td>Pipeline stages, statuses and lifecycle</td><td>Settings → Lead settings → Pipelines &amp; stages</td></tr>
<tr><td>Assignment and routing rules</td><td>Settings → Assignment</td></tr>
<tr><td>Email and WhatsApp channels</td><td>Settings → Channels</td></tr>
<tr><td>Duplicate rules</td><td>Settings → Duplicate management</td></tr>
</tbody></table>
''')

# ---------------------------------------------------------------- 11
section('help', 'Reference', 'Common questions', f'''
<dl class="faq">
<dt>A screen in this guide is missing from my sidebar.</dt>
<dd>Workspaces appear only when your role allows them and your organisation has the feature. Ask your administrator.</dd>
<dt>A panel says I may not see something, rather than showing it empty.</dt>
<dd>That is deliberate. “Nothing here” and “you don’t have access” are shown differently so an empty list never hides a permission problem.</dd>
<dt>My lead went to a queue instead of to me.</dt>
<dd>When <i>Assign to</i> is left on <i>Automated</i>, routing rules decide the owner. Leads that no rule matches go to the fallback queue, where anyone with access can pick them up.</dd>
<dt>Times look wrong.</dt>
<dd>Times are shown in your organisation’s time zone, which an administrator sets in Settings → General.</dd>
<dt>An error mentions a reference code.</dt>
<dd>Copy the reference and send it to your support contact. It lets them find exactly what happened.</dd>
</dl>
<h3>Keyboard shortcuts</h3>
<table><tbody>
<tr><td>{K('Ctrl')} {K('K')}</td><td>Search, open a record or go to a screen</td></tr>
<tr><td>{K('Alt')} {K('Shift')} {K('N')}</td><td>New personal note</td></tr>
<tr><td>{K('Esc')}</td><td>Close the current panel or dialog</td></tr>
</tbody></table>
''')

toc = ''.join(f'<li><a href="#{i}"><span>{e}</span>{t}</a></li>' for i, e, t, _ in sections)
body = ''.join(
    f'<section id="{i}"><p class="eyebrow">{e}</p><h2>{t}</h2>{b}</section>' for i, e, t, b in sections)

page = open('/home/user/crm/guide_shell.html').read().replace('{{TOC}}', toc).replace('{{BODY}}', body)
open(OUT, 'w').write(page)
print('written', len(page))
