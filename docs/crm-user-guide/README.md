# CRM User Guide

An illustrated end-user guide to the CRM (`code7/business-ecosystem/crm`). Open `index.html` in a browser.

- `index.html`: the guide.
- `images/`: screenshots taken from the real CRM frontend (develop branch) running against a local `crm-backend` in development mode, with sample data.
- `tools/`: how the guide was made. `capture.cjs` drives Playwright through the app and records the on-screen position of each annotated control in `marks.json`. `build_guide.py` turns the content, the screenshots and `marks.json` into `index.html`, drawing the numbered callouts from the recorded positions.

To refresh after UI changes: run the backend and frontend locally (see crm-backend `Makefile.linux` and crm-frontend `playwright.config.ts`, live server), run `node tools/capture.cjs`, copy the images, then run `python3 tools/build_guide.py`.
