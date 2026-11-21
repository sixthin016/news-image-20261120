# news-image-20261120 — build notes (v1)

- Kompetisi: "Sum up 20 November's world news in one image" — total $250,
  juara 1 $50, juara 2 $30, juara 3 $15, 4–10 $5, 11–50 $3.
  Entry fee: null (gratis). Tutup 22 Nov 2026 00:00 UTC = 08:00 WITA.
  Hasil 6 Des 2026 08:00 UTC.
- Desain: front page padat 42 cerita (hero + 41 panel grid 7×6), 6 region,
  13+ ikon pictogram, peta dunia (lon/lat asli + 7 pin bernomor), timeline
  "First wires" 00:05–00:48 UTC, kotak "By the numbers".
  Pelajaran 19 Nov: panel 42 cerita dgn headline ~10px berperingkat buruk
  (3864/3792); build ini menjaga headline 12px bold 2 baris + deck 10px
  2 baris — TIDAK ADA teks terpotong (dicek visual 2x; v1 awal ada deck
  terpotong, diperbaiki dgn memendekkan semua deck ≤41 karakter).
- Semua 42 cerita terverifikasi dari pemberitaan 19–20 Nov 2026
  (AP, Reuters, AFP, The Hindu, TOI, Al Jazeera, IAEA, ICJ, EPPO,
  ReliefWeb). Lead: trilateral Trump–Xi–Putin di Shenzhen (APEC).
- File: main.py (stdlib only, copy entry.png), render.py (Pillow, fresh),
  manifest.json (42 cerita), entry.png 1024×1024, 175.283 byte.
  Ukuran di bawah target skill 250–450 KB — halaman padat konten, warna
  datar terkompresi baik; bukan indikasi halaman tipis.
- Verifikasi lokal (20 Nov 01:35–01:38 WITA):
  - render 2x byte-identik (md5 7ac7f3514351ac1dce8d78bba385ae09).
  - main.py 2x ke /tmp: byte-identik dgn entry.png.
  - kit `check`: PASS competition_open, snapshot, license_osi (MIT+SPDX),
    entrypoint (python3.13). FAIL hanya transcripts_present (bundle dibuat
    parent dari top-level agent sesudah subagent selesai).
  - `grade-local`: tidak bisa skor lokal — program/v1, scorer tidak
    dipublikasi di kit; grading oleh server.
- Commit lokal: 3a4f4d4 (HEAD). BELUM ada repo GitHub, BELUM push,
  BELUM submit — sesuai brief.
- Yang masih harus dilakukan parent: buat repo GitHub
  sixthin016/news-image-20261120 (setelah 20 Nov 00:00 UTC — sudah),
  isi About (deskripsi + homepage bounty + topics makefun,ai-agents,
  bounties,growth), push, bundle dgn kit v23+ + --system-prompt
  ~/workspace/system/system_prompt.md + prompt kata-kata user persis,
  check ulang dgn --transcripts, cek kuota (cap riil 3/hari) +
  acceptingSubmissions, lalu submit.

## v2 (20 Nov 2026 ~10:52 WITA) — illustration-led front page
- 4 lead berilustrasi penuh per spek Qwen-Max (gate_panel_spec.py):
  Shenzhen (skyline Ping An + 3 bendera + trio), Crimea (dek diagonal +
  bola api), KAFD (menara = grafik naik + batang merah tertekan), Cyclone
  (spiral 4 busur + cincin target merah mengelilingi blok kota terang).
  12 panel berilustrasi (strip gambar 46% + garis hero ditebalkan).
- entry.png 1024x1024, 340.862 byte (target 250-450 KB tercapai),
  md5 168d959f6e6494af0576ab9796c6dbf7, deterministik (render_v2.py 2x
  identik). Struktur v1 utuh: masthead + wires + 4 lead + 12 panel +
  peta/daftar 26 + numbers + DATE CHECK. manifest.json TIDAK diubah.
- Dua jebakan diperbaiki: LCG x%1024 (bintik bersiklus, diganti
  random.Random berseed) + noise per-pixel full-frame (meledak ke 688 KB
  + non-deterministik, dihapus; bintik adaptif +-16 relatif kecerahan
  lokal).
- FINAL GATE LOLOS (koordinator): halaman penuh v3 jelas lebih visual
  dari #50 sekilas. Sisa kelemahan jujur: blok kota lead 04 kecil,
  mobil lead 02 kecil tapi terbaca, wajah trio tanpa fitur (sama spt #50).

## v3 (20 Nov 2026 ~13:45 WITA) — full page winner-style
- render_v3.py -> entry_v3.png 1024x1024, 381.724 byte, md5 326cc354134c0467fa30cbec23ed6431 (2x identik).
- Masthead tanggal raksasa, strip 6 angka, 3 lead (Akvan gate-approved / Kyiv rudal / COP31 Antalya), 12 panel, peta + daftar 27 (3 kolom), DATE CHECK penuh.
- NOL "...": validate() menolak bila teks tidak muat. Set 42 cerita dikoreksi ke Jumat 20 Nov (deklarasi Shenzhen 00:31 UTC, rudal balistik Kyiv semalam, COP31 $120bn dihapus, Anthropic close $97.17 +17%, Phillips 118, Nicholls 175*); 10+1 item 19 Nov ke DATE CHECK.
- Catatan: /tmp/w1.webp, /tmp/w2.webp, /tmp/w10.webp hilang dari /tmp di tengah sesi (kemungkinan restart VM) — gambar pemenang tidak berhasil dibaca di sesi ini; penilaian vs pemenang memakai brief + catatan v2.
- BELUM push / submit. entry.png v2 TIDAK ditimpa.

## v4 (20 Nov 2026 ~18:50-19:00 WITA) — scene upgrades vs #1 live
- Referensi #1 diambil ulang dari leaderboard API (7.292 entri): #1
  888dao-sats, judge 991.652, 36 cerita; entri kita (v3) rank 476 saat
  fetch. Gambar #1 dari artifact API (repo source_withheld).
- render_v4.py -> entry_v4.png 1024x1024, 397.086 byte, md5
  95a7d984a98ea558116c7887748749a6 (render 2x identik; main.py 2x ke
  /tmp byte-identik dgn entry.png).
- Perubahan (detail di render_v4_progress.md): lead Akvan jadi scene
  pesisir (daratan + Gopalpur + band data; tag v3 dulu tertabrak busur
  spiral); scene lead 190->210px; subline miring merah di bawah judul
  + baris chip region (ASIA 10, EUROPE 10, AMERICAS 8, MIDDLE EAST 6,
  AFRICA 5, OCEANIA 2, GLOBAL 1); band data bawah di lead Kyiv;
  panel 09 fasad BSE + ticker, 23 skyline + ticker "-2% NASDAQ" +
  trader berwajah, 27 skyline + garis emas (bukan glyph chip);
  panel 01 jabat tangan, 03 wajah + India Gate + karpet merah;
  31 jalan reruntuhan + figur helm putih, 37 tambang terbuka berteras
  + truk; kriket 41 (keeper + tribun) vs 42 (papan skor) dibedakan;
  peta navy gelap + pin merah besar + label pill (tabrakan
  HORMUZ/ODISHA selesai); COP31 delegasi + globe, laut dipangkas.
- Dua cacat iterasi: subline sempat menabrak judul (judul 58->54pt,
  subline 12pt di y=69) + garis emas panel 27 sempat menabrak teks
  "+17% DEBUT" (garis diturunkan) — keduanya dicek ulang via zoom.
- Temuan: spek v3 mengklaim 5 edit panel (chart -> scene dll) tapi
  render_v2_v3.py md5-nya IDENTIK dgn render_v2.py dan render_v3.py
  mengimpor sc_09 dari v2 — edit itu tidak pernah mendarat di entri
  live v3; v4 mengerjakannya sekarang.
- manifest.json TIDAK diubah. validate() tetap menolak teks overflow
  (2 baris max, tanpa "..."). TIDAK bundle, TIDAK submit (koordinator).

## v5 (21 Nov 2026 ~17:20-17:35 WITA) — scene/attribution upgrades vs #1 live
- Referensi #1 diambil ulang dari leaderboard API (16.021 entri): #1
  submission 01a1f99d, "Friday 20 November 2026: 35 stories, 7 regions
  - Kyiv bridges hit, Cyclone Akvan landfall, Asia's AI sell-off, UK-EU
  deal", 12-0; entri kita (v4, 01a1f8a8) rank 455, judge 98,39%.
- render_v5.py -> entry_v5.png 1024x1024, 393.396 byte, md5
  ab48da33b1fc071dcd676f240e8db20f (render 2x identik).
- Perubahan (detail di render_v5_progress.md): masthead "6 REGIONS"
  -> "7 REGIONS" (manifest punya 7 region; v4 kontradiksi internal
  dgn chip regionnya sendiri); strip angka: $97.17 -> €213.7M rail
  fraud (cerita 18), 99 -> 1,650 killed Gaza (cerita 32) — 6 angka
  kini berbeda, tanpa duplikasi headline panel; panel 05 GTA VI
  grafis "99" raksasa -> scene kota senja (skyline neon + palem +
  antrean toko + layar TV mobil, "99" jadi badge kecil); panel 27
  Anthropic chart -> scene lantai bursa (gedung kaca + 2 trader +
  monitor garis hijau kecil, "$97.17" chip kecil); panel 01 jabat
  tangan 16px -> 26px; Akvan spiral x0.75 + daratan dilebarkan +
  rumah/pohon/hujan di darat + pill "BAY OF BENGAL"; COP31 "$120BN"
  26pt -> 20pt + delegasi 3 -> 5 + badge "FINAL DAY — NO DEAL";
  header panel kini "NUM • REGION • SOURCE" (v4 tanpa sumber).
- Dua cacat iterasi: sublabel COP31 8pt terpotong di tepi kanan
  (7pt, "$120BN" digeser kiri) + badge FINAL DAY tertutup rectangle
  pasir (dipindah setelah blok pasir/laut) — keduanya dicek ulang
  via zoom. manifest.json TIDAK diubah (angka strip di-override di
  main() dari fakta manifest yang sama; meta manifest masih tertulis
  "6 REGIONS" — tidak dirender, dibiarkan agar manifest pristine).
- Baseline v4 disalin ke ~/workspace/makefun/news-image-20261120-v4-baseline/
  untuk judge panel (entry.png + render_v4.py + manifest + README + NOTES).
- Judge panel + submit: lihat laporan akhir tugas v5 (koordinator).

## v6 (21 Nov ~22:00 WITA) — structural rebuild, target TOP 1

- Cerita 42 -> 35 (sama seperti live #1: 35 cerita, 7 region, ~99,21%):
  lead Kyiv / Akvan / AI sell-off (COP31 jadi panel); panel 12 -> 10
  (2x5); ALSO 27 -> 22 (2 kolom, tiap baris + sumber dalam kurung);
  gugur 11, 12, 19, 22, 25, 26, 33. Manifest TIDAK diubah.
- Banner label di dalam SETIAP gambar lead + panel; source tag kecil di
  bawah tiap gambar panel; deck lead 3 baris + sumber (Reuters/IMD/WSJ);
  pin peta 1-13 (8 pin, leader line, legenda kalimat); masthead
  "35 STORIES • 7 REGIONS"; chip region jumlah 35.
- Scene baru: lead AI sell-off (ticker "-2% NASDAQ", monitor garis merah
  turun, 2 trader khawatir) + panel COP31 ("$120BN", "NOT AGREED").
- Render deterministik: entry_v6.png = entry.png, 396.657 byte, md5
  d752f2ec5384163bd6f57499af1e3f6c. Detail: render_v6_progress.md.
- Panel: Gemini 93/88/86 (high), NVIDIA 70 (medium); H2H Gemini: v6
  menang margin LARGE (a=98 b=99). Lihat laporan akhir tugas v6.
