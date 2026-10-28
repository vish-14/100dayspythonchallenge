# 25-second re-cut: three hook versions

The same reel with three different opening lines, made to test as Instagram **Trial Reels** (shown only to non-followers). Each is about 23 s, 1080 × 1920, 30 fps. Vish is on screen and speaking from the first frame. The hook text is readable on frame 0, and the four task chips pop in within the first second.

| File | Hook (on screen and spoken) | Style |
| --- | --- | --- |
| `reel_h1.mp4` | Still answering every enquiry and follow-up yourself? | Question |
| `reel_h2.mp4` | Business owners: stop doing these 4 jobs by hand. | Call-out |
| `reel_h3.mp4` | What if one AI agent handled your daily admin? | What if |

The rest is shared:
- **Agent scene:** "Here's how one AI agent helps. It replies to enquiries, follows up on time, summarises documents, and keeps your team updated. You approve what matters." (One hub with four tools, each lighting up with its result, then a human Approve click.)
- **Ending (1.1×):** "Want it built for your business? Follow me and comment workflow. I'll send the details to your DMs." (Follow → comment WORKFLOW → DM.)

Each `reel_hN.srt` holds that version's captions. The hook line has no burned-in caption, because it's already the on-screen text.

To rebuild one version: `python3 tools/make_variant.py h1 --render`. Hook text lives in `tools/variants.json`, where `*word*` highlights a word and `|` breaks a line.
