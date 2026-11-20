# news-image-20261120 v4 — gap vs #1 + build progress (20 Nov 2026, builder bundle)

## Referensi #1 (live, diambil ulang 20 Nov ~18:50 WITA)
- Leaderboard API: 7.292 entri. #1 = **888dao-sats**, submission
  `01a1f778-412a-72d2-b25d-bb71cfe514c8`, judge 991.652, "Friday 20
  November 2026: 36 stories, 6 continents — Cyclone Akvan landfall,
  Kyiv ballistic missiles, COP31 final day deadlock". Repo
  `source_withheld` — gambar diambil dari artifact API
  (`/api/submissions/01a1f778.../artifact.webp`, 1024x1024).
- Entri kita (v3, submission 01a1f781, handle uding-uding): **rank 476**
  saat fetch (turun dari 400/5.948 — field kini 7.292).
- #2 kiencx dan #3 kho22 juga diunduh sebagai pembanding sekunder.

## Gap v3 vs #1 (dilihat berdampingan, zoom lead/panel/bottom — urut dampak)

1. **Lead Akvan masih abstrak / cacat terlihat.** Spiral putih di
   lapangan navy datar tanpa darat/pantai — terbaca target, bukan
   badai mendarat. Lebih parah: busur spiral MEMOTONG teks tag
   "LANDFALL: NOON IST" (huruf O di NOON tertabrak busur — terlihat
   jelas di zoom). #1 Akvan adalah scene pesisir: daratan tan,
   label ODISHA/Gopalpur/BAY OF BENGAL, band data bawah
   "LANDFALL • GUSTS 110 KM/H".
2. **Ruang mati di bawah deck ketiga lead** (~40 px kosong antara
   deck dan baris "20 NOV • SUMBER / STORY X OF 42"). #1 mengisi
   zona itu dengan deck 3 baris + sumber inline; halaman #1 tidak
   punya lubang putih sebesar itu.
3. **Tidak ada chip jumlah region + tidak ada subline ringkasan.**
   #1 punya baris chip warna (EUROPE 7 • AMERICAS 8 • ASIA-PACIFIC
   10 …) dan subline miring merah di bawah masthead ("Cyclone Akvan
   strikes India • Ballistic missiles hit Kyiv • …") — dua cue
   otoritas koran paling kuat yang tidak kita punya.
4. **Panel 09 & 23 masih diagram murni** (panah hijau naik / panah
   merah turun di atas batang) — persis yang dihindari #1 (panel
   pasarnya scene + chip data). Catatan: spek v3 mengklaim panel ini
   sudah diperbaiki, tapi `render_v2_v3.py` md5-nya IDENTIK dengan
   `render_v2.py`, dan `render_v3.py` mengimpor `sc_09` dari v2 /
   menulis ulang `sc_23` sebagai chart — jadi di entri live v3
   keduanya MASIH chart. Perbaikan di v4 adalah pekerjaan baru,
   bukan ulangan.
5. **Panel 01 / 03 / 27 masih ikon, bukan scene.** 01 = bendera +
   dokumen datar; 03 = tiga bust TANPA WAJAH yang identik; 27 =
   glyph chip + teks besar. Semua panel #1 membawa tempat/scene +
   chip data overlay.
6. **Panel 31 & 37 tidak terbaca sekilas.** 31 = gedung abu-abu +
   gumpalan asap abu-abu; 37 = gundukan cokelat + lengkung hitam —
   judge tidak bisa tahu apa yang digambarkan tanpa membaca headline.
7. **Kriket 41/42 gambar yang sama dua kali** (batsman identik,
   dicerminkan) — duplikasi yang langsung kentara saat membandingkan
   dua panel bersebelahan.
8. **Lower third pucat & padat.** Peta krem/biru pudar, pin kecil,
   label bertabrakan (ANTALYA/HORMUZ/ODISHA saling tumpuk, SHENZHEN
   di tepi). #1: peta navy gelap, benua tan kontras, pin merah besar
   bernomor. Daftar 3 kolom kita rapat ke tepi; DATE CHECK 4 baris
   kecil berdesakan.
9. (Minor) **Lead COP31 setengah laut kosong** — deret busur ombak
   berulang mengisi ~40% scene; gedung kotak putih datar, tanpa
   manusia/globe. #1 COP31: globe + termometer + badge merah
   "FINAL DAY — DEADLOCK".

## Rencana edit v4 (semua Pillow deterministik, di atas render_v3.py)
- E1 Akvan: scene pesisir baru (`draw_akvan_coast`) — daratan tan +
  garis pantai + spiral di atas laut + label ODISHA/Gopalpur/BAY OF
  BENGAL + band data bawah; tag tidak lagi di bawah busur.
- E2 Lead: scene_h 190→210, lead_h 330→324, leads y 194 — ruang mati
  di bawah deck mengecil; band data bawah ditambahkan di scene Kyiv.
- E3 Masthead: subline miring merah di bawah judul; baris chip region
  (dihitung dari manifest: ASIA 10, EUROPE 10, AMERICAS 8, MIDDLE
  EAST 6, AFRICA 5, OCEANIA 2, GLOBAL 1) antara strip angka & lead.
- E4 Panel 09 = fasad BSE + ticker band "+1.21%"; panel 23 = skyline
  malam + ticker merah "-2% NASDAQ" + satu trader berwajah.
- E5 Panel 01 = jabat tangan di atas dokumen; 03 = wajah (mata/
  mulut, rambut beda) + India Gate + karpet merah; 27 = skyline +
  garis emas naik + "$97.17".
- E6 Panel 31 = jalan reruntuhan + figur helm putih; 37 = tambang
  terbuka berteras + truk + emas.
- E7 Kriket: 41 = batsman + wicketkeeper + tribun penonton; 42 =
  papan skor "NZ 368 • PHILLIPS 118" + stumps & bails — tanpa batsman.
- E8 Peta: ocean navy gelap, benua tan, pin merah r9, label dalam
  pill navy (kontras di mana pun), anchor HORMUZ dipindah ke bawah
  (tabrakan dengan ODISHA selesai), legenda "1–3 LEAD • 4–13 FEATURE".
- E9 COP31: laut dipangkas, tambah 3 delegasi + globe, "$120BN"
  mengecil, palem dirapikan.
- TIDAK diubah: manifest.json / cerita / tanggal / jumlah (42 cerita,
  3 lead + 12 panel + peta + numbers + DATE CHECK; tetap), font
  headline/deck & `validate()` (2 baris max, tanpa "..."). Catatan:
  ≤41 karakter" dari v1 TIDAK berlaku untuk manifest v3 (deck lead
  15 & 14 >60 karakter, panel 05 = 43) — mengubahnya butuh ubah
  manifest, yang dilarang; constraint yang mengikat adalah wrap
  2 baris + tanpa elipsis, yang ditegakkan `validate()`.

## Verifikasi (20 Nov ~19:00 WITA)
- `python3 render_v4.py` 2x SETELAH perbaikan akhir: md5 identik
  `95a7d984a98ea558116c7887748749a6` (deterministik).
- Ukuran: **397.086 byte** (target 250–450 KB tercapai).
- `validate()`: 42 cerita (hero + 41), tanpa "…"/"..." — lolos (render
  gagal keras bila ada overflow; tidak ada yang gagal).
- `main.py` 2x ke /tmp: byte-identik dengan entry_v4.png (`cmp` OK).
- Cek visual halaman penuh 2x + zoom (masthead, leads, panels,
  bottom): tidak ada teks terpotong/tumpang tindih setelah 2 iterasi
  perbaikan — (a) subline sempat menabrak judul (judul 58→54pt,
  subline 12pt di y=69, dicek zoom: bersih); (b) garis emas panel 27
  sempat menabrak "+17% DEBUT" (garis diturunkan, dicek zoom: terbaca).
- Gate berdampingan vs #1 (888dao-sats, artifact live): v4 JELAS lebih
  visual/scene-like daripada v3 sekilas — lead Akvan kini scene
  pesisir (bukan target abstrak), panel 09/23/27 bukan chart/ikon
  lagi, panel 31/37 terbaca, kriket tidak duplikat, peta gelap
  kontras, plus chip region + subline + band data lead seperti #1.
- Sisa gap jujur vs #1: scene #1 lebih halus/detil (vektor lebih
  rapi, mis. panel luar angkasa & kriketnya); #1 hanya 36 cerita
  (tipografi lebih lega) vs kita 42 (lebih padat — trade-off brief).
  Panel 23 trader masih kecil; panel 01 jabat tangan masih sederhana.
- TIDAK bundle, TIDAK submit — koordinator yang memutuskan kuota.
