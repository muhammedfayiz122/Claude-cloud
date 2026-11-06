const { chromium } = require('playwright');
const fs = require('fs');
const meta = {};
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const go = async (path, w = 4000) => { await p.goto('http://localhost:5199' + path, { waitUntil: 'load' }); await p.waitForTimeout(w); await p.mouse.move(1430, 890); const later = p.getByRole('button', { name: 'Later', exact: true }); if (await later.count()) { if (!meta['followups-due']) await shot('followups-due', [['Complete, snooze or open the lead', p.getByRole('button', { name: 'Complete' })], ['Decide later', later]]); await later.click(); await p.waitForTimeout(800); } };
  const box = async (loc) => { try { const bb = await loc.first().boundingBox({ timeout: 3000 }); if (!bb) return null; return { x: +((bb.x + Math.min(bb.width, 40) / 2 ) / 14.4).toFixed(2), y: +((bb.y + bb.height / 2) / 9).toFixed(2), w: +(bb.width/14.4).toFixed(2), h: +(bb.height/9).toFixed(2) }; } catch { return null; } };
  const shot = async (name, marks = []) => {
    const m = []; for (const [label, loc] of marks) { const bx = await box(loc); if (!bx) console.log('  miss', name, label); m.push({ label, ...(bx || {}) }); }
    await p.screenshot({ path: `final/${name}.png` }); meta[name] = m; console.log('shot', name);
  };
  const main = p.locator('main');
  // App shell (leads list)
  await go('/leads', 5000);
  await shot('shell', [
    ['Sidebar navigation', p.getByRole('link', { name: 'Leads', exact: true })],
    ['Global search (Ctrl K)', p.getByRole('button', { name: /Search/ }).first()],
    ['Language switch', p.getByRole('button', { name: /Switch the interface/ })],
    ['Notifications', p.getByRole('button', { name: 'Notifications', exact: true })],
    ['Your account', p.getByRole('button', { name: /Account menu for Local/ })],
    ['Assistant', p.getByRole('button', { name: 'Ask the assistant' }).first()],
  ]);
  await shot('leads-list', [
    ['Search leads', main.getByPlaceholder('Search leads')],
    ['Choose a view', main.getByLabel('Which leads to show')],
    ['Add filter', main.getByRole('button', { name: 'Add filter' })],
    ['New Lead', main.getByRole('button', { name: 'New Lead' })],
    ['Export', main.getByRole('button', { name: 'Export' })],
    ['Click a name to open the lead', main.getByRole('link', { name: 'Aisha Rahman' })],
  ]);
  await main.getByLabel('Which leads to show').click(); await p.waitForTimeout(800);
  await shot('leads-views'); await p.keyboard.press('Escape');
  await main.getByRole('button', { name: 'New Lead' }).click(); await p.waitForTimeout(1200);
  const d = p.getByRole('dialog');
  await d.getByLabel(/^Name/).fill('Hamza Qureshi'); await d.getByLabel('Email').fill('hamza@qureshigroup.com'); await d.getByLabel('Note').fill('Met at the Dubai SME expo. Wants a quote for monthly bookkeeping.');
  await shot('lead-new', [
    ['Name (required)', d.getByLabel(/^Name/)], ['Where the lead came from', d.getByLabel('Source')], ['Contact details', d.getByLabel('Email')],
    ['First note', d.getByLabel('Note')], ['Starting stage', d.getByLabel('Stage')], ['Owner – leave on Automated to use routing', d.getByLabel('Assign to')], ['Save', d.getByRole('button', { name: 'Create lead' })],
  ]);
  await p.keyboard.press('Escape');
  // Lead detail
  await go('/leads/01a1ae6f-e3fe-7e4c-be24-be26d2b1a51e', 5000);
  await shot('lead-detail', [
    ['Header actions', main.getByRole('button', { name: 'Schedule meeting' })],
    ['Owner & assignment', main.getByText('Owner', { exact: true })],
    ['Stage path – click a stage to move', main.getByRole('button', { name: /Qualified/ })],
    ['Record tabs', main.getByRole('tab', { name: 'Overview' })],
    ['Quick actions', main.getByText('Quick actions')],
    ['Upcoming work', main.getByText('Upcoming work')],
  ]);
  await p.screenshot({ path: 'final/lead-detail-full.png', fullPage: true });
  for (const [btn, name] of [['Create task','lead-task'],['Schedule meeting','lead-meeting'],['Qualify','lead-close'],['Transfer','lead-transfer']]) {
    await main.getByRole('button', { name: btn }).first().click(); await p.waitForTimeout(1500); await shot(name); await p.keyboard.press('Escape'); await p.waitForTimeout(700);
  }
  await main.getByRole('tab', { name: 'Timeline' }).click().catch(()=>{}); await p.waitForTimeout(2000); await shot('lead-timeline');
  // Pools, opportunities
  await go('/pods'); await shot('pools');
  await go('/opportunities'); await shot('opps-list', [['List / Board', main.getByRole('button', { name: 'Board' }).or(main.getByRole('tab', { name: 'Board' }))], ['New opportunity', main.getByRole('button', { name: 'New opportunity' })]]);
  await main.getByRole('button', { name: 'Board' }).or(main.getByRole('tab', { name: 'Board' })).first().click().catch(()=>{}); await p.waitForTimeout(2500); await shot('opps-board');
  await main.getByRole('button', { name: 'New opportunity' }).first().click(); await p.waitForTimeout(1500); await shot('opp-new'); await p.keyboard.press('Escape');
  await go('/opportunities/01a1ae75-5319-7833-aa20-b0e3913f1c3c'); await shot('opp-detail');
  await go('/accounts'); await shot('accounts', [['Columns & saved views', main.getByRole('button', { name: 'Columns' })], ['New account', main.getByRole('button', { name: 'New account' })]]);
  await go('/accounts/01a1ae74-4233-7185-8f23-fcaba3c8b5e4'); await shot('account-detail');
  await go('/contacts'); await shot('contacts');
  await main.getByRole('button', { name: 'New contact' }).first().click(); await p.waitForTimeout(1500); await shot('contact-new'); await p.keyboard.press('Escape');
  await go('/my-work'); await shot('my-work', [['Tasks / Reminders / My Day', main.getByRole('tab', { name: 'Tasks' }).or(main.getByRole('button', { name: 'Tasks' }))], ['Due-date buckets', main.getByRole('button', { name: 'Overdue' }).or(main.getByRole('tab', { name: 'Overdue' }))], ['Add task', main.getByRole('button', { name: 'Add task' })]]);
  await go('/calendar'); await shot('calendar', [['Day / Week / Month', main.getByRole('button', { name: 'Week' }).or(main.getByRole('tab', { name: 'Week' }))], ['Schedule meeting', main.getByRole('button', { name: 'Schedule meeting' })], ['Whose calendar', main.getByRole('button', { name: 'Everyone' }).or(main.getByRole('radio', { name: 'Everyone' }))]]);
  await go('/meetings'); await shot('meetings');
  await go('/dashboards', 6000); await shot('dashboard', [['Filters', main.getByRole('button', { name: 'Filters' })], ['Templates', main.getByRole('button', { name: 'Templates' })], ['Customize', main.getByRole('button', { name: 'Customize' })]]);
  await go('/reports', 5000); await shot('reports', [['Pick a report', main.getByLabel('Report')], ['Period & grouping', main.getByLabel('Period')], ['Export CSV', main.getByRole('button', { name: 'Export CSV' })]]);
  await go('/inbox'); await shot('inbox');
  await go('/notifications'); await shot('notifications');
  await go('/approval-queue'); await shot('approvals');
  await go('/proposals'); await shot('proposals');
  await go('/campaigns'); await shot('campaigns');
  await go('/segments'); await shot('segments');
  await go('/imports'); await shot('imports');
  await go('/teams'); await shot('teams');
  await go('/queues'); await shot('queues');
  await go('/settings', 4000); await shot('settings', [['Search settings', main.getByPlaceholder(/Search settings/)], ['Quick access', main.getByText('QUICK ACCESS')]]);
  await go('/leads'); await p.keyboard.press('Control+k'); await p.waitForTimeout(1200); await p.keyboard.type('Aisha'); await p.waitForTimeout(2000); await shot('command-palette');
  await p.keyboard.press('Escape');
  fs.writeFileSync('final/marks.json', JSON.stringify(meta, null, 1));
  await b.close();
})();
