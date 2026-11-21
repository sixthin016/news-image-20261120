# news-image-20261120 v5 — gap vs live #1 + build progress (21 Nov 2026, builder bundle)

## State (verified 21 Nov ~17:20 WITA)

- Live entry: v4, submission `01a1f8a8-8a79-7621-92a1-bbcfad4da5e1`,
  claim (v4, dari submit sebelumnya — lihat submit report koordinator),
  commit `5339f8a`, **rank 455/16.021, judge 98,39%**
  (judge 983.928, interval 977.336–990.521). Target: top 50 ($250).
  Closes **22 Nov 08:00 WITA** (deadline 2026-11-22T00:00:00Z).
  Kuota saat build: day cap 6, taken 0, left 6, can_submit=true.
- Repo: `~/workspace/makefun/news-image-20261120/` (branch `master`,
  remote https://github.com/sixthin016/news-image-20261120).
  Kit: `~/workspace/makefun/news-image-20261120-kit/`.
- Live #1 (21 Nov 17:20): submission `01a1f99d-e16b-7062-b919-dbeaa4e4b017`,
  "Friday 20 November 2026: 35 stories, 7 regions - Kyiv bridges hit,
  Cyclone Akvan landfall, Asia's AI sell-off, UK-EU deal", 12-0.
  Top-10 semua 12-0; #3 "36 stories, 6 continents — Cyclone Akvan
  landfall, Kyiv ballistic missiles, COP31 final day deadlock";
  #4 "33 sourced stories, 13 drawn"; #5 "38 stories ... every figure
  attributed"; #10 "35 sourced stories, a UTC timeline and a date check".
- Baseline v4 disalin ke `~/workspace/makefun/news-image-20261120-v4-baseline/`
  (entry.png + render_v4.py + manifest + README + NOTES) untuk judge panel.

## Gap v4 vs #1 (dilihat berdampingan, urut dampak)

1. **Masthead salah hitung region: "6 REGIONS" padahal ada 7**
   (ASIA/EUROPE/AMERICAS/MIDDLE EAST/AFRICA/OCEANIA/GLOBAL — chip
   region di halaman yang sama menampilkan 7). Kontradiksi internal,
   kriteria judge 3 ("nothing self-contradictory").
2. **Strip angka menduplikasi headline panel** ($97.17 = panel 27,
   99 = panel 05) — 2 dari 6 angka strip bukan fakta baru.
3. **Panel 05 masih grafis, bukan scene**: "99" 34pt + 5 bintang
   memenuhi panel; tidak ada tempat/figur/kejadian.
4. **Panel 27 masih terbaca chart**: skyline + garis emas besar +
   "$97.17" 17pt — garis adalah elemen dominan panel.
5. **Panel 01 jabat tangan 16px** — terlalu kecil dibaca sekilas.
6. **Spiral Akvan masih mendominasi** (r max 122 di scene 312 lebar)
   dan label "BAY OF BENGAL" dipotong busur luar spiral.
7. **COP31 "$120BN" 26pt mendominasi scene**; tidak ada badge
   "FINAL DAY" seperti #1 ("FINAL DAY — DEADLOCK").
8. **Panel tidak menampilkan sumber sama sekali** (header hanya
   "NUM • REGION") — #1 menaruh sumber di tiap panel
   ("Reported · Reuters", "Filed · AP", "Scorecard · ICC").

## Rencana edit v5 (semua Pillow deterministik, di atas render_v4.py)

- E1 Masthead: "42 STORIES • 7 REGIONS".
- E2 Strip angka: $97.17 -> "€213.7M / RAIL FRAUD CHARGED, EPPO"
  (cerita 18); 99 -> "1,650 / KILLED IN GAZA SINCE CEASEFIRE"
  (cerita 32). 6 angka kini berbeda, tanpa duplikasi panel.
- E3 Panel 05 = scene kota senja (gradien magenta-oranye-teal,
  skyline + palem + antrean 3 figur + etalase toko + layar TV
  mobil); "99" jadi badge emas kecil + 5 bintang kecil.
- E4 Panel 27 = scene lantai bursa (gedung kaca + meja trader +
  2 trader berwajah + monitor garis hijau naik kecil); "$97.17"
  chip putih kecil, "+17% DEBUT" badge hijau.
- E5 Panel 01: jabat tangan 16px -> 26px, dokumen dipersempit.
- E6 Akvan: spiral x0.75 (r max 91), daratan dilebarkan (168->190),
  +2 rumah +3 pohon, hujan mencapai daratan, titik Gopalpur
  dipindah ke garis pantai, "BAY OF BENGAL" di atas pill gelap.
- E7 COP31: "$120BN" 26pt -> 20pt, sublabel 7pt (8pt terpotong
  di tepi kanan — diperbaiki setelah render pertama), delegasi
  3 -> 5, badge merah "FINAL DAY — NO DEAL" di pasir (digambar
  SETELAH pasir/laut — render pertama badge tertutup rectangle
  pasir, diperbaiki).
- E8 Panel: header "NUM • REGION • SOURCE".
- TIDAK diubah: manifest.json (cerita/tanggal/angka manifest
  tetap); angka strip di-override di main() dari fakta manifest
  yang sama. Catatan: meta manifest masih tertulis "6 REGIONS"
  (tidak dirender oleh render_v4/v5 — masthead di-hardcode di
  renderer; dibiarkan agar manifest tetap pristine).

## Verifikasi (21 Nov ~17:30 WITA)

- `python3 render_v5.py` 2x: md5 identik `ab48da33b1fc071dcd676f240e8db20f`
  (deterministik; md5 pertama sebelum perbaikan COP31/Akvan:
  `bb795eb77485177e09c12f8f898de12e`).
- Ukuran: **393.396 byte** (target 250–450 KB tercapai).
- `validate()`: 42 cerita, tanpa "…"/"..." — lolos.
- Cek visual halaman penuh + zoom (leads, panel baris 1+2, bawah):
  COP31 "$120BN"/sublabel utuh + badge FINAL DAY terlihat; Akvan
  pill BAY OF BENGAL bersih, Gopalpur di garis pantai; panel 05
  scene senja (bukan angka raksasa); panel 27 scene bursa (bukan
  chart); panel 01 jabat tangan lebih besar; header panel memuat
  sumber. Tidak ada teks terpotong/tumpang tindih.
- Self-grade jujur: v5 JELAS lebih scene-like dan lebih teratribusi
  daripada v4 sekilas (2 panel grafis -> scene, 2 fakta strip baru,
  7 region benar, sumber di semua panel). Sisa gap vs #1: scene #1
  masih lebih halus/detil (vektor lebih rapi); #1 hanya 35 cerita
  (tipografi lebih lega) vs kita 42 (lebih padat — trade-off brief).
  Panel 05/23: figur trader masih kecil; panel 05 antrean berupa
  blob kecil di ukuran thumbnail.
- TIDAK bundle, TIDAK submit — koordinator yang memutuskan kuota
  (tugas ini: builder + submit bila panel lolos — lihat laporan akhir).

## Promote + push + kit check

- `cp entry_v5.png entry.png`; README.md + NOTES.md diperbarui (v5).
- Commit `ca811915e147d1b1824f718068d4ba5e6f952aa6` (6 file:
  entry.png, entry_v5.png, render_v5.py, render_v5_progress.md,
  README.md, NOTES.md). Push OK via
  `GIT_ASKPASS=~/workspace/.git-askpass.sh git push origin master`
  (branch master, bukan main); remote HEAD = `ca81191` terverifikasi.
- Repo About terverifikasi via GitHub API (PAT valid, login
  sixthin016): description + homepage bounty URL + topics
  (ai-agents, bounties, growth, makefun).
- Kit check (`node cli/makefun.mjs check --kit <kit> --repo <repo>
  --worktree`): **4 passed** (competition_open, snapshot,
  license_osi, entrypoint), **1 failed = transcripts_present
  (DIHARAPKAN — bundle route)**, 14 skipped, 5 checks "at submission".
  Catatan kit: copy level 27, site level 33 — level 27 >= 20 memenuhi
  syarat run record; tidak di-download ulang.

## Judge panel (21 Nov ~17:45 WITA) — LOLOS

- Panel v1.0.5, `--models nvidia,gemini` (OpenRouter habis 50/hari
  15:30). Percobaan pertama NO_JUDGE (NVIDIA unparseable + Gemini
  HTTP 503 high demand); retry berhasil.
- **NVIDIA 78 (medium), Gemini 88 (high) → mean 83,0, min 78 →
  VERDICT: SUBMIT.**
- Head-to-head vs v4: **B (v5) menang 2-0**, margin medium;
  NVIDIA a=72 b=86 (+14), Gemini a=93 b=97 (+4) — di atas noise ~5.
- Laporan panel:
  `~/workspace/makefun/judge-panel-news-image-20261120-news-image-20261120-20261121T093224Z.json`.
  Grade/evidence: `news-image-20261120-v5-grade.txt`,
  `news-image-20261120-v4-grade.txt`, `news-image-20261120-evidence.txt`.

## Bundle + check (21 Nov ~17:55 WITA) — MENUNGGU PARENT

- Bundle: `~/workspace/makefun/news-image-20261120-bundle-v5.tar.gz`
  (21.188.852 byte, sha256
  7a5f6500dd3e549b23767fcc1ccf1a32564cc2b59dc9d4068a4ad38ef3ca0611),
  56 sesi (1 Hermes + 55 Muse app, termasuk sesi build v5 ini),
  prompt file v4-prompt.txt ("kejar terus semuanya sampai masuk
  target top rank", origin other), system prompt
  `~/workspace/system/system_prompt.md`, harness muse 1.3 / meta /
  muse-spark-1.3 / default, mcp none. Log:
  `~/workspace/makefun/bundle-news-image-20261120-v5.log`.
- Check terhadap bundle: **12 passed, 1 failed, 6 skipped, 5 at
  submission**. Satu-satunya FAIL = thinking_priced (0 usage rows) —
  subagent TIDAK BISA melampirkan usage rows-nya sendiri; row ditulis
  hanya setelah run subagent selesai. **Parent harus: query muse.db
  → append ke `~/.makefun/muse-usage-news-image-20261120.jsonl` →
  bundle ulang dengan --muse-usage → check → submit.**
  Detail + perintah persis: `news-image-20261120-v5-HANDOFF.md`.
- JANGAN submit bundle 0-usage-rows (ditolak). Deadline submit
  08:00 WITA 22 Nov 2026; kuota terakhir dicek 17:40 WITA: day left 6,
  can_submit=true, accepting=true.

---

# news-image-20261120 v6 — STRUCTURAL REBUILD (21 Nov 2026, ~21:36–22:15 WITA)

Target diperbarui user 21:46: **KEJAR TOP 1** (bukan sekadar kalahkan v4).
#1 live 99,21% (992.057), 35 cerita, 7 region. Gate submit tetap: panel
harus jelas menunjukkan v6 yang terbaik.

## Desain v6 (lihat ~/workspace/makefun/news-image-20261120-v6-design.md)

- S1 cerita 42 -> 35: leads 15 Kyiv / 02 Akvan / 23 AI sell-off (COP31
  turun jadi panel); panel 10 (01, 14, 03, 09, 27, 21, 30, 31, 37, 42);
  ALSO 22 (2 kolom); gugur 7 (11, 12, 19, 22, 25, 26, 33).
  Manifest TIDAK diubah — seleksi hanya di kode render.
- S2 banner label di DALAM setiap gambar lead + panel + source tag
  kecil di bawah tiap gambar panel.
- S3 deck lead 3 baris + sumber dalam kurung (hanya sumber manifest).
- S4 lower third: pin peta 1-13 (8 pin yang muat tanpa tabrakan),
  ALSO 2 kolom + sumber per baris, legenda peta = kalimat caption.
- S5 masthead "35 STORIES • 7 REGIONS", chip region jumlah 35.
- Panel 2 baris x 5 (192x132, lebih lebar/lega); lead tinggi 324,
  scene 196px.

## Implementasi (render_v6.py, di atas render_v5.py)

- LEAD_NUMS/PANEL_NUMS/ALSO_NUMS eksplisit; LEAD_BANNER, PANEL_BANNER,
  PANEL_SOURCETAG; LEAD_DECKS di-override di main() dari fakta manifest.
- Scene lead baru draw_ai_selloff_lead() (23): skyline malam Wall
  Street, ticker merah "-2% NASDAQ" + segitiga turun, monitor garis
  merah turun, chip "AI", 2 trader berwajah khawatir, band data bawah.
- Scene panel baru sc_14() (COP31, dulu lead): langit krem, matahari,
  "$120BN" teal, gedung konferensi + globe, 3 delegasi mini.
  PANEL_SCENES diperbarui (14 masuk; 05/23/41 keluar).
- _banner_text(): teks banner putih bold, font mengecil sampai muat.
- draw_lead(): banner 26px menutupi atas scene, deck 3 baris,
  "STORY N OF 35".
- draw_panel(): banner 14px + source tag pill navy di bawah gambar.
- draw_region_chips(): dihitung dari 35 cerita tampil (bukan 42
  manifest) — ASIA 8 • EUROPE 8 • AMERICAS 6 • MIDDLE EAST 5 •
  AFRICA 5 • OCEANIA 2 • GLOBAL 1.
- draw_map_dark(): label pin pakai offset eksplisit (dx, dy) + garis
  leader tipis ke pin; pin dijepit ke dalam kotak peta; legenda
  "NUMBERS MATCH THE STORIES ON THIS PAGE".
- draw_also_list(): 2 kolom x 11, baris 11px, headline + " (SOURCE)".
- main(): strip angka sama seperti v5; pin 8 (dx/dy per pin dihitung
  dari posisi proyeksi — klaster Timur Tengah/Asia dalam pita 95x25px);
  output entry_v6.png.

## Defect yang ditemukan di zoom + diperbaiki (semua terverifikasi visual)

1. Chip region menjumlah 42 (dihitung dari manifest) — diperbaiki
   ke 35 (lihat draw_region_chips).
2. Label pin peta bertabrakan parah (ANTALYA/HORMUZ/ODISHA menumpuk,
   pin 13 Wellington terpotong tepi kanan) — diperbaiki dengan offset
   + leader line + clamp; verifikasi zoom: 8 pin + label semua terbaca.
3. Banner menutupi teks atas 3 scene panel — diperbaiki dengan geser
   konten ke bawah banner 14px: sc_27v5 chip "$97.17" + badge
   "+17% DEBUT", sc_14 "$120BN"/"NOT AGREED", sc_42 scoreboard +
   stumps/bails; bendera sc_01 + sc_03v4 juga digeser.
4. Badge "+17% DEBUT" tertutup badan trader (teks 51,45px > pill 54px
   minus margin) — pill dilebarkan ke 74px, trader 1 ke 0.44,
   trader 2 ke 0.56; verifikasi zoom NEAREST 8x: "+17% DEBUT" penuh.
5. Globe sc_14 menutupi ujung "NOT AGREED" — globe dipindah ke kiri
   bawah.
6. Chip "AI" lead 23 tertutup kepala trader kanan — digeser ke antara
   kedua trader.
7. Sisa nit (diterima): pin 1 dan 5 (Kyiv/Antalya, satu longitude)
   bersentuhan di tepi — kedua nomor tetap terbaca penuh.

## Verifikasi render (21 Nov ~22:0x WITA)

- `python3 render_v6.py` 2x: md5 identik `d752f2ec5384163bd6f57499af1e3f6c`
  (deterministik). Ukuran **396.657 byte** (target 250–450 KB).
- `validate()`: 35 cerita, tanpa "…"/"..." — lolos (headline 2 baris,
  deck 2 baris, ALSO 1 baris + sumber).
- Cek visual halaman penuh + zoom (3 lead, 2 baris panel, peta,
  badge 8x NEAREST): banner semua lead/panel terbaca, source tag
  semua panel terbaca, deck lead 3 baris + sumber, chip region jumlah
  35, peta 8 pin + leader, ALSO 22 + sumber, tidak ada teks
  terpotong/tumpang tindih (kecuali nit pin 1/5 di atas).

## Promote (repo)

- `cp entry_v6.png entry.png` (md5 sama `d752f2ec...`).
- main.py: docstring "42 stories" -> "35 shown of 42".
- README.md: intro + "Why this shape" + "How it works" ditulis ulang
  untuk v6 (35 cerita, 10 panel, banner label, source tag, pin peta 8,
  ukuran + md5 baru). Render: `python3 render_v6.py`.
- Grade/evidence v6:
  `~/workspace/makefun/news-image-20261120-v6-grade.txt`,
  `~/workspace/makefun/news-image-20261120-v6-evidence.txt`.
- Commit + push: BELUM (menunggu hasil panel ke-3; lihat bawah).

## Judge panel v1.0.5 (21 Nov ~22:0x WITA) — models nvidia,gemini

- Run 1: NVIDIA FAILED (unparseable); **Gemini 93 (high)** — strengths:
  struktur sama seperti #1 (35 cerita, 7 region, pin peta bernomor),
  deterministik, tanpa overflow, atribusi kaya; weaknesses: noise
  panel ~5pt, pin 1/5 bersentuhan. Mean 93, min 93 -> SUBMIT.
  H2H null (butuh semua judge OK — lihat judge_panel.py:575).
- Run 2: **NVIDIA 70 (medium)**; Gemini FAILED HTTP 503 (high demand).
  Mean 70, min 70 -> SUBMIT. H2H null.
- Gabungan 2 run: Gemini 93 + NVIDIA 70 -> mean 81,5, min 70
  (ambang SUBMIT: mean >=70, min >=55 — LOLOS), tapi H2H vs v4
  belum pernah jalan.
- Run 3: NVIDIA FAILED (unparseable); **Gemini 88 (high)**. Mean 88 -> SUBMIT.
  H2H null.
- Run 4 (gemini saja): **Gemini 86 (high)** -> SUBMIT. **H2H: B (v6) menang,
  margin LARGE, a=98 b=99** — "Version B significantly improves upon
  Version A by resolving internal contradictions present in A (such as
  the masthead claiming 6 regions while listing 7), reducing the story
  count from 42 to 35 to m…".
- Run 5 (nvidia saja): NVIDIA FAILED (socket error). NO_JUDGE.
- Run 6 (nvidia saja, retry): **NVIDIA 74 (medium)** -> SUBMIT.
  **H2H: B (v6) menang, margin MEDIUM, a=75 b=88** — "Version B matches
  the live #1 entry's exact format (35 stories, 7 regions) and
  systematically fixes v4's documented weaknesses: banner labels inside
  every picture replace the duplicated numbers strip …".
- **GATE LOLOS: H2H 2-0 untuk v6 (Gemini LARGE + NVIDIA MEDIUM).**
  Semua 5 skor sukses: Gemini 93/88/86, NVIDIA 70/74 -> mean 82,2,
  min 70 (ambang SUBMIT: mean >=70, min >=55 — LOLOS).
  Laporan: `judge-panel-news-image-20261120-v6.json` (run 3),
  `judge-panel-news-image-20261120-v6-gemini.json` (H2H Gemini),
  `judge-panel-news-image-20261120-v6-nvidia.json` (H2H NVIDIA).
- JUJUR SOAL ODDS: panel lokal TIDAK memprediksi judge live pada
  margin ~0,5pt — v5 menang panel 2-0 atas v4 tapi turun di live
  (97,90% vs 98,39%). Panel win adalah syarat perlu, bukan bukti
  menang live. Gap v4 -> #1 ~0,8pt; v6 menargetkannya lewat struktur
  yang sama seperti #1, tapi tidak ada jaminan live.
- TIDAK ADA UTC timeline di v6 (sengaja): manifest tidak punya waktu
  per cerita — membuat timeline UTC berarti mengarang waktu, dan
  konversi "01:25 LOCAL" Kyiv = 23:25 UTC 19 Nov justru
  self-contradictory (kriteria judge 3). DATE CHECK tetap jadi elemen
  waktu di halaman.
