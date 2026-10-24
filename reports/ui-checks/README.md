# UI checks (Claude)

Headless checks of the live room at http://127.0.0.1:8765. Every script blocks non-GET requests, so nothing is ever posted.

Setup, in a scratch folder: `npm install jsdom@24.1.3 playwright@1.48.2 && npx playwright install chromium`.

| File | What it checks |
|---|---|
| `test.js` (jsdom) | AI-native layer: suggestions, agent badges, slash menu, @ autocomplete, send-ready, Ctrl K palette open/filter/close |
| `test2.js` (jsdom) | output enrichment: headlines, status rows, callouts, numeric columns, path/commit chips, copy buttons, outlines, Needs-you, filters, Calm/Expressive |
| `test3.js` (jsdom) | colour palettes in the View menu and in Ctrl K |
| `test_mentions_synthetic.js` | @mention chips on an injected card (the live room has no @mentions to test) |
| `shot.js` (Playwright) | screenshot + layout boxes: `node shot.js NAME 1600 1000 calm light` |
| `shot2.js` | rail sidebar + compact + dark + Ocean, View menu open |

Screenshots, 1600×1000: `before.png` (feed 428 px tall, 1008 px wide), `after.png` / `final.png` (703 px × 1352 px), `variant.png` (rail, compact, dark, Ocean).
Known result: "@mentions turned into chips" reports FAIL on the live room only because no message contains an @Name; the synthetic test covers it.
