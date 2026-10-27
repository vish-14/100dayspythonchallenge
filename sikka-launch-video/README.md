# Sikka — 20s launch video

A 1920×1080, 20-second launch film for Sikka, built with [HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP → MP4).

**Rendered video:** [`sikka-launch.mp4`](sikka-launch.mp4)

| Time | Scene |
| --- | --- |
| 0–3.6s | Hook: "Still making invoices in ~~spreadsheets~~?" over a broken spreadsheet |
| 3.6–6.4s | ₹ coin drops and spins, "Sikka — Invoicing, minted." |
| 6.4–13.6s | An invoice builds itself: client typed in, line items, GST, total counts up to ₹1,65,200, PAID stamp |
| 13.6–16.8s | Features: templates, auto tax & totals, one-tap sharing |
| 16.8–20s | End card: "Bill smarter. Get paid faster." · Available now |

Sound (music bed + synced SFX) is synthesized by `assets/gen_audio.py` (`python3 assets/gen_audio.py out.wav`, needs numpy).

```bash
npm run check    # lint + layout + contrast checks
npm run dev      # preview in the HyperFrames studio
npm run render   # render to MP4
```
