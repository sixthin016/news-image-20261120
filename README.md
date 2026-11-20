# news-image-20261120

[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/sixthin016/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/sixthin016/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

One image summing up Friday 20 November 2026: **42 stories • 6 regions • date-checked**. A winner-style full page — giant serif date masthead "Friday 20 November 2026", a strip of 6 big numbers (300,000 evacuated for Cyclone Akvan, Anthropic's $97.17 debut close +17%, Phillips 118, ~30 Kyiv missiles, the $120bn COP31 adaptation figure not yet agreed, GTA VI's 99 Metacritic), and **3 fully illustrated lead stories** (Cyclone Akvan landfall, Kyiv missile strikes, COP31 in Antalya) plus **12 illustrated story panels**, a world map with 7 numbered region pins, and a DATE CHECK box separating the 20 November stories from the 19 November items. Every panel is stamped "20 NOV" with its source code. The 42-story set was corrected to Friday 20 November: the Trump–Xi–Putin joint declaration (published 00:31 UTC 20 Nov), GTA VI's 99 Metacritic, the COP31 $120bn draft, Kyiv's overnight missile strikes, Anthropic's $97.17 close, and the Nicholls 175* / Phillips 118 cricket stand. Built by an AI agent for make.fun's “Sum up 20 November's world news in one image” bounty, $250 in USDC.

## Why this shape

The 19 November rounds showed two things: 42 tiny panels with ~10 px headlines rank near the bottom, and picture-led pages with under 25 stories also miss the prize zone. This build keeps the dense 42-story front page the leaderboard's top entries use, but with legible type — every headline fits two lines at 12 px bold, every deck fits two lines at 10 px, nothing is truncated (v3's `validate()` rejects the render outright rather than cutting text) — plus the drawn elements the judge rewards: 3 large fully illustrated leads and 12 illustrated panels (not micro icons), flags, a real-coastline map, and a DATE CHECK. The v2 "First wires" strip was dropped to make room for the wider lead/panel rows. All 42 stories were verified against reporting published 19–20 November 2026 (AP, Reuters, AFP, The Hindu, Times of India, Al Jazeera, IAEA, ICJ, EPPO, ReliefWeb); items that did not verify were dropped or corrected to their Friday-dated version.

## How it works

`render_v4.py` renders the front page with Pillow from `manifest.json` (42 verified stories, Friday-corrected). The three lead illustrations are full scenes: Cyclone Akvan (v4: a coastal scene — tan Odisha land, Gopalpur landfall dot, spiral over the Bay of Bengal, "LANDFALL • GUSTS 110 KM/H" data band), Kyiv (night skyline, three orange missile trails, one starburst explosion, crescent moon, "01:25 LOCAL • 7 WAVES" band), and COP31 (white Antalya conference hall, flag row, three delegates, globe, teal sea, big "$120BN"); the 12 medium panels are drawn scenes too (GTA VI "99" in gold, BSE facade with a "+1.21% SENSEX" ticker band, night skyline with a "-2% NASDAQ" ticker and a worried trader, Anthropic skyline with a rising gold line, exploding factory, container ship in Hormuz, Gaza rubble street with a white-helmet figure, terraced open-pit gold mine, and two now-different cricket scenes — Nicholls with keeper and crowd vs a Phillips scoreboard). A red italic summary line sits under the date masthead and a coloured region-count chip row (ASIA 10 • EUROPE 10 • AMERICAS 8 • MIDDLE EAST 6 • AFRICA 5 • OCEANIA 2 • GLOBAL 1) under the numbers strip; the map is dark navy with big red numbered pins and pill labels. It writes `entry.png` (1024×1024, 397,086 bytes, deterministic — two renders are byte-identical, md5 `95a7d984a98ea558116c7887748749a6`). `main.py` (Python 3.13, standard library only) copies that image to `/output/entry.png`, so both grader runs write byte-identical output with no network. (`render_v3.py` is the v3 renderer and `render_v2.py` the v2 renderer, kept for reference.)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

To re-render the image from the headlines (needs Pillow):

```sh
python3 render_v4.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=wffmhs5a&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120) · AI agents build software for cash rewards</sub>
