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
- Commit + push via `GIT_ASKPASS=~/workspace/.git-askpass.sh git push origin master`
  (branch master, bukan main).
- Kit check (`node cli/makefun.mjs check --kit <kit> --repo <repo> --worktree`):
  (diisi setelah push).
