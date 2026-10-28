# PDF guides (the WORKFLOW lead magnet)

Every reel gets its own short guide, sent in the auto-DM. Build it from JSON with `scripts/guide/make_guide.py`, so the design stays identical every day:
- A4 page, white background, dark text, restrained blue (#1F4FD8);
- one font (Inter, bundled in `scripts/guide/fonts/`);
- consistent margins (20 mm) and a footer with page numbers.

```bash
python3 <skill>/scripts/guide/make_guide.py guide.json guide.pdf --png-dir guide-pages
```

The script prints the page count and every link, writes `guide.html` next to the PDF, and saves a PNG of each page. **Open and inspect every PNG before delivering.** Check for:
- awkward wrapping or one-word lines;
- clipped text;
- pages that are nearly empty or crowded;
- a booking link that is missing from the link list.

Needs Node + Playwright (preinstalled in Claude Code cloud), plus `pypdf` and `pypdfium2`.

## Layout (automatic)

| Page | Content |
| --- | --- |
| 1 | Brand row (avatar, Vish, @vish.workflows) · kicker · title · subtitle · overview table (one row per workflow) · optional three rules |
| 2.. | Two workflows per page. Each one runs: label "Automation 01" → name → one-line goal → Trigger → numbered Steps → Tools (grouped lines) → light-blue Human approval note |
| last | "Start this week" checklist (5 items), then the booking invitation (button + written URL, BUILD alternative, support email) |

**Use 2 or 4 workflows.** With 2 workflows the guide is 3 pages; with 4 it is 4 pages. With an odd count the script still works, but it adds a page; check the PNGs, or set `"pages"` manually, for example `[["cover"],["wf:0","wf:1"],["wf:2","start"],["cta-alone"]]`. The available blocks are `cover`, `wf:N`, `start`, `cta` and `cta-alone` (the CTA plus "What we'll cover").

## JSON schema

See `assets/lead-magnet/4-task-workflow.guide.json` for a complete example.

```json
{
  "title": "5 words max, the outcome",
  "kicker": "A practical guide for [industry] owners",
  "subtitle": "One sentence: what gets automated, with a person approving what matters.",
  "overview": {
    "heading": "The automations at a glance",
    "intro": "Each one runs on its own…",
    "columns": ["Automation", "Starts when", "You approve"],
    "rows": [["Name", "Trigger in plain words", "The human checkpoint"]]
  },
  "rules": {"label": "What makes it reliable", "heading": "Three rules that keep it working",
            "items": [{"title": "…", "text": "…"}]},
  "workflows": [{
    "name": "Verb + object",
    "goal": "One sentence outcome.",
    "trigger": "When exactly it starts.",
    "steps": ["4 steps, each one line", "…"],
    "tools": [["Automation", "Make, Zapier or n8n"], ["CRM", "…"], ["AI", "ChatGPT or Claude"]],
    "approval": "lower-case sentence: what a person approves."
  }],
  "start": {"intro": "…", "items": [{"lead": "Bold first words.", "text": "the rest."}]},
  "cta": {"lede": "optional override; the URL defaults to cal.com/vishworkflows/discovery"},
  "footer": "optional; defaults to '<title> · Vish | AI Automation · @vish.workflows'"
}
```

## Writing rules

- Plain words for owners, not engineers. Name real, common tools; group them in three short lines.
- Exactly 4 steps per workflow, each fitting one or two lines.
- Every workflow has a human approval point.
- No invented statistics, prices, client names or guaranteed results.
- Use the industry's own vocabulary ("patients", "listings", "covers", "orders").
- The booking link is always https://cal.com/vishworkflows/discovery and the support email is support@sritrilinga.com, unless the user changes them. If they do, update `DEFAULT_CTA` in `make_guide.py` and the brand files.
