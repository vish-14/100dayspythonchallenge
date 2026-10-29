# Daily run: research → approval → reel → PDF → post kit

Triggered by `/vish daily` (or "today's reel", "daily vish", "make today's post"). One run produces one ready-to-post reel, a matching PDF guide for the WORKFLOW DM, and everything needed to publish. The goal of every run is **leads for AI automation and AI agent projects**, from any industry, anywhere in the world.

Work in the user's current folder. Everything for the day goes in `vish-daily/<YYYY-MM-DD>-<slug>/`. The running memory of the page is `vish-daily/content-log.md`. Create it from `assets/content-log.template.md` if it doesn't exist.

## Step 0: Set up and read the log (2 min)

1. Get today's date and time in IST: `TZ=Asia/Kolkata date '+%A %d %B %Y, %H:%M'`.
2. Read `vish-daily/content-log.md`. Note the last 7 industries, pillars and hooks, and any performance numbers.
3. Ask once, in one short question, for the numbers from the last posted reel (views, WORKFLOW comments, DMs, calls booked). Accept "skip". Write any answer into the log.
4. In a fresh container, run `bash <skill>/scripts/setup.sh` in the background while you research. If something fails, read the environment docs and tell the user what to allow (npm, PyPI, huggingface.co, github.com).

## Step 1: Research and pick 3 concepts (≈15 min)

Follow `references/concept-engine.md`:
- run the research lenses with today's month and year;
- score 6–10 ideas;
- respect the rotation rules and the log.

Learn from the log: lean towards the industries, pillars and hooks that produced the most WORKFLOW comments and calls, but keep exploring new industries at least 3 days a week.

## Gate 1: Concept approval (required)

Show the 3 concepts in the format from concept-engine §6, ranked. Ask with AskUserQuestion: concept 1, 2, 3, or "3 more ideas". Free-text tweaks are welcome. **Do not start production before the user picks.**

## Step 2: Script and storyboard (≈10 min)

- Pacing: about 55–65 s of explainer at 0.9× with en-gb pronunciation, then the standard ~8 s WORKFLOW CTA at 1.0× (about 70–75 s in total). Clarity beats speed: the audience is largely Indian, and the first version at 1.0×/1.1× with US pronunciation was reported as hard to understand. Don't rush the problem → solution turn; it gets a slightly longer pause (`GAP` in `make_vo.py`).
- **Narrative (required): problem → my solution → how its workflows work → CTA.** Never jump from the problem straight into a numbered list.
  - **Hook** (≤2 s, names the audience and the pain, in their own words: "Property agents: your enquiries go cold while you're out on site visits.").
  - **Problem** (one relatable moment: "A buyer enquires at 9 PM. You reply the next morning. By then, another broker is already talking to them.").
  - **Solution** (the turn, first person, names the solution and the number of workflows): "That's why I built an AI agent solution for [audience], with [four] connected workflows."
  - **Workflow beats** (3 or 4, each an ordinal intro **followed at once** by its explanation): "First, respond to enquiries. [what happens]" / "Second, qualify buyers. […]" / "Third, route leads and book site visits. […]" / "Fourth, follow up. […]". Use "First / Second / Third / Fourth", not "One: / Two:", and don't list all the names up front and explain them later. Each explanation shows trigger → AI step → human approval → result.
  - **Reliability beat**: connected tools, clear rules, you approving what matters.
  - **CTA** (unchanged, never reworded): "Want this workflow built for your business? Follow me and comment workflow, and I'll send you the details in your DMs."
- **Say who acts.** The AI agent or the automation does the work and sends the alerts; customers only enquire or reply. Write "The agent alerts you on WhatsApp when a buyer meets your criteria", never "Serious buyers alert you on WhatsApp". Read every sentence and ask: who is the subject, and does that person really do this?
- Write `tools/script.json`. `say` is what Kokoro reads: spell out acronyms ("C R M") and write numbers as words. `text` is the caption.
- Plan the on-screen beats per scene. Every reveal lands on the word that names it, and something changes every 1–2 s.

## Gate 2: Script approval (required)

Show the voiceover script (with an estimated duration at ~2.3 words/s, the rate at 0.9×), the on-screen headline per scene, and the PDF outline (title + workflow names). Ask: approve, or edit. Apply edits, then continue without further gates unless something is unclear.

## Step 3: Produce the reel (≈30–60 min)

1. `cp -r <skill>/template vish-daily/<date>-<slug>/reel`, then work in that folder.
2. Edit `project.config.json`: video duration, copy per scene, chapter labels, SFX cues tied to the new words. The brand, handle and CTA stay unchanged.
3. Rebuild the scenes in `src/scenes/` for the new topic, reusing the template's patterns:
   - `hook.html`: full-screen takeover (also the cover frame);
   - `problem.html`: the relatable moment;
   - `solution.html`: the turn. A light panel: THE SOLUTION, MY AI AGENT, FOR [AUDIENCE], then the numbered workflow nodes that pop on "four", link on "connected" and label on "workflows". Node 01 lights up as the hand-off to the first beat. Keep the node labels identical to the beat titles;
   - `a1–a4.html`: one workflow each. The title matches the spoken intro ("01 RESPOND TO ENQUIRIES") and lands on those words, then a UI card animates the trigger → AI → approval;
   - `key.html`: the reliability takeover;
   - `cta.html`: **keep as is**.

   Use 3 or 4 beats. If you use 3, drop `a4` from the config and the script, delete node 04 in `solution.html`, and say "three connected workflows".
4. Run the voice → transcription → analysis → music → mix → build pipeline exactly as in `reel-pipeline.md`.
5. **Update the word anchors in `tools/build.py`** for the presenter's entrance and exit, brow lifts and head moves (the `abs_word("scene:word")` calls near line 130). They must name words in the new script.
6. Run `npx hyperframes check`, then look at snapshots across the whole timeline. Fix overlaps, clipped text, captions under the Instagram UI and empty frames.
7. Render with `npx hyperframes render -q delivery --fps 30 -o ../reel.mp4`.
8. QA:
   - extract frames every ~2 s with ffmpeg and inspect them;
   - check that the hook frame works as a cover;
   - run the loudness check (target −16 to −17 LUFS, true peak ≤ −1.5 dBTP);
   - check the length.

   Say that the audio was measured, not heard.
9. Export the cover: `ffmpeg -ss <hook frame time> -i reel.mp4 -frames:v 1 cover.png`. Pick a frame with the full hook headline.

## Step 4: Make the PDF guide (≈10 min)

Follow `references/guide-pdf.md`:
- write `guide.json` for this topic (2 or 4 workflows, with the reel's workflow first);
- run `python3 <skill>/scripts/guide/make_guide.py guide.json guide.pdf --png-dir guide-pages`;
- **look at every page PNG**: balanced pages, no clipped or orphaned text, links listed in the output.

## Step 5: Post kit (`post.md`)

Write `vish-daily/<date>-<slug>/post.md` with:

1. **Post time:**
   - Default: **8:00 PM IST**, or anywhere in 7:30–8:30 PM. That reaches India in the evening, the Gulf in the early evening, the UK in the afternoon and the US East Coast in the morning.
   - If it is already past 8:30 PM IST, say "tomorrow 8:00 PM IST".
   - Give the matching local times for Dubai, London and New York, accounting for daylight saving on today's date.
   - If the log shows a better slot from Insights, use that instead.
2. **Caption:** use the SEO template in `brand-and-page.md`.
   - The first ≤125 characters are the hook.
   - Use the industry's own search phrases.
   - Include the follow + comment WORKFLOW CTA.
   - Add "💾 Save this".
   - The company line goes last: "…, by Sri Trilinga Technologies Private Limited."
   - Use 3–5 hashtags: 2 broad (#AIAutomation, #BusinessAutomation) and 2–3 industry tags (for example #RealEstateMarketing or #DentalPractice).
3. **On-screen cover text** (≤6 words) and **alt text**.
4. **Pinned comment:** "Comment WORKFLOW and I'll send you the full [topic] guide 👇 (follow first so it reaches your DMs)".
5. **Story share text** with a link sticker to the booking page.
6. **SuperProfile for this reel:**
   - A new automation on *this* reel only, keyword `WORKFLOW`, followers only.
   - Message B: the reel-specific guide link (the uploaded PDF), plus the booking button https://cal.com/vishworkflows/discovery.
   - Messages A, C and D as in `dm-playbook.md`, with the industry name filled in.
7. **First-hour checklist:**
   - reply to every comment within 60 minutes;
   - answer DMs personally after the auto-DM;
   - share to Story;
   - don't edit the caption in the first hour.
8. **Lead follow-up:** for anyone who replies BUILD or books a call, make 3 tailored discovery questions for that industry (see `lead-engine.md`).

## Step 6: Log, save, deliver

1. Append one row to `vish-daily/content-log.md`: date, slug, industry, pillar, format, hook, keyword, post time, and blank metric columns.
2. Add any new industry insight to the concept engine's industry map if research found one.
3. If the folder is a git repo, commit (`vish-daily: <date> <slug>`) and push to the session's branch. Don't commit model caches or `node_modules`.
4. Send the user `reel.mp4`, `cover.png`, `guide.pdf` and `post.md`. End with a short summary: concept, length, post time (IST plus local times), what to upload to SuperProfile, and anything you couldn't verify.

## A/B with Trial Reels (when reach is low)

When the user wants to test a variation (language, hook, length), build both from the same project (a copy per variant, e.g. `reel-short/` and `reel-hinglish/`), post both as Instagram **Trial Reels** (shown to non-followers only), compare after 24–72 h on watch time, the 3-second hold, shares, saves and WORKFLOW comments, then share the winner to the profile and log the result. Hinglish variants: Hindi sentences with the English words brokers use (lead, site visit, WhatsApp, approve), with Devanagari for the voice (`"lang": "hi"`) and Roman Hinglish captions. Re-time every scene's word cues, since the word order changes. A Hinglish variant needs the natural Hindi voice (Parler-TTS or a recording) for a fair test.

## Time-savers and guardrails

- If the user says "fast", skip Gate 2: show the script and continue unless they object.
- If rendering tools are unavailable, still deliver: the script, the storyboard, the PDF, the post kit and exact instructions. Say clearly that the MP4 wasn't produced, and why.
- Never invent statistics, client names, results or testimonials. Example data on screen is clearly illustrative.
- Keep Vish's character and the CTA identical every day (non-negotiables in `SKILL.md`).
