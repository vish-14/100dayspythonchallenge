# PDF guide source

`guide-print.html` is the print layout for `vish-4-task-workflow.pdf` (A4, 4 pages, Inter, white background, blue accents).
Rebuild: `node render.js "$PWD/guide-print.html" "$PWD/../vish-4-task-workflow.pdf"` (Playwright + Chromium; footer and page numbers come from `render.js`).
Pages are fixed by `<section class="page">`: 1 cover + overview + three rules, 2 automations 01–02, 3 automations 03–04, 4 start this week + booking.
Booking link: https://cal.com/vishworkflows/discovery · support@sritrilinga.com
