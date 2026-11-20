# news-image-20261120 v3 — FULL PAGE (winner-style rebuild, 20 Nov 2026 ~13:30–13:45 WITA)

## Yang dikerjakan
- **Masthead baru:** tanggal raksasa serif "Friday 20 November 2026"
  (bukan lagi "THE WORLD IN ONE PAGE" sebagai judul); pita gelap
  "THE WORLD IN ONE PAGE — EVERY STORY FIRST REPORTED ON FRIDAY
  20 NOVEMBER 2026".
- **Strip 6 angka besar** tepat di bawah masthead (nilai besar di
  atas, label di bawah): 300.000 dievakuasi Akvan / $97.17 Anthropic
  close +17% / 118 Phillips / ~30 rudal Kyiv / $120bn adaptasi
  COP31 belum sepakat / 99 Metacritic GTA VI.
- **3 lead BESAR berilustrasi penuh (~324×330):**
  - 02 Akvan — panel `gate_v3_akvan.py` yang sudah disetujui
    (dirender native 330×200 lalu di-resize ke slot 324×190;
    komposisi tidak diubah).
  - 15 Kyiv — BARU: skyline malam + 3 jejak rudal oranye + 1
    ledakan starburst + bulan sabit.
  - 14 COP31 — BARU: Antalya (gedung konferensi putih + deret
    bendera + palem + laut teal + "$120BN" besar).
- **12 panel medium berilustrasi** (2×6): 01 deklarasi (bendera +
  dokumen + segel), 03, 05 GTA VI ("99" emas + bintang, BARU),
  09, 21 pabrik meledak (BARU), 23 saham turun (BARU), 27
  Anthropic (chip + "$97.17 / +17% DEBUT"), 30, 31, 37, 41
  Nicholls 175*, 42 Phillips 118 (kriket diparameterisasi).
- **NOL "..." di mana pun:** `validate()` di render_v3.py menolak
  render bila headline/deck mana pun melebihi jatah baris —
  bukan dipotong seperti `trunc1` v2. Panel 01 sempat gagal
  validasi (headline 3 baris) → dipendekkan di manifest.
  Daftar 27 item (3 kolom × 9) juga divalidasi lebarnya; 10
  headline daftar dipendekkan agar muat satu baris.
- **Strip "First wires" v2 DIHAPUS** — layout pemenang tidak
  memakainya; ruangnya dipakai untuk baris lead/panel yang lega.
  Data wires tetap di manifest sebagai provenance.
- **Peta + daftar:** pin 3 BRUSSELS → ANTALYA (lead COP31);
  daftar 27 cerita dalam 3 kolom.

## Set cerita dikoreksi (42 cerita, 6 region)
Pengganti (semua terverifikasi via pencarian web 20 Nov):
- 01: deklarasi bersama Trump–Xi–Putin — teks diterbitkan
  00:31 UTC 20 Nov, beberapa jam setelah trilateral 19 Nov
  (BUKAN pertemuan itu sendiri).
- 05: GTA VI 99 Metacritic, 151 kritikus, 100% positif.
- 13: EU akan memanggil duta Rusia (Kallas, Jumat) — ganti
  putusan ICJ Rohingya.
- 14: COP31 — draf hapus angka $120bn; belum sepakat (ganti
  serangan Jembatan Crimea).
- 15: rudal balistik Rusia ke Kyiv semalam (01:22 UTC 20 Nov);
  kebakaran di beberapa distrik; 3 jembatan Dnipro rusak —
  ganti "STRIKES DAMAGE KYIV EMBASSIES" (serangan itu 19 Nov,
  terverifikasi; kini disebut di DATE CHECK).
- 23: saham AS turun meski debut Anthropic (Nasdaq −2%+, WSJ).
- 27: Anthropic tutup debut $97.17, +17% dari harga IPO $83
  (buka $111.50) — ganti pricing IPO $81.34bn.
- 34: Afrika tolak renegosiasi Perjanjian Paris di COP31
  (54 negara, 20 Nov) — ganti serangan Houthi ke menara PIF.
- 41: Nicholls 175* (bukan 113*), NZ 368 — ganti Fiji.
- 42: Phillips 118, 216-run stand dengan Nicholls.
- DATE CHECK: 10 item 19 Nov dari brief + serangan kedubes
  Kyiv (19 Nov) + Fiji ditulis 18 Nov (terverifikasi RNZ).

Catatan kejujuran:
- Skor GTA VI 99 pertama kali terbit 18 Nov (embargo), bukan
  20 Nov; yang Jumat adalah angka 99 yang bertahan + ulasan
  pengguna dibuka 20 Nov 12:00 PST. Tetap dipakai karena angka
  itu ada di strip pemenang (brief).
- Close Anthropic $97.17 terjadi Kamis 19 Nov waktu AS,
  dilaporkan Jumat 20 Nov UTC — dipakai sebagai angka Jumat
  sesuai brief.
- Item lain di luar daftar eksklusi brief dipertahankan dari
  manifest v2 apa adanya (tidak di-reverifikasi satu per satu).

## Verifikasi
- `python3 render_v3.py` 2x: md5 identik
  `326cc354134c0467fa30cbec23ed6431` (deterministik).
- Ukuran: **381.724 byte** (target 250–450 KB tercapai).
- `validate()`: 42 cerita (hero + 41), 6 region, tanpa "…"/"...".
- Cek visual (baca PNG 2x + zoom crop): tidak ada teks tumpang
  tindih; semua headline/deck panel lengkap. Dua perbaikan
  iterasi: teks "$120BN" sempat terpotong di tepi kanan (34pt
  di x=196 → 30pt di x=176) + sublabel "ADAPTATION — NOT
  AGREED" sempat terpotong (11pt → 9pt di x=172, diukur
  145,2px). Tag "LANDFALL: NOON IST" di lead Akvan dicek via
  zoom: tidak terpotong (busur spiral lewat di balik huruf O).
- TIDAK push GitHub, TIDAK submit, TIDAK sentuh credentials.

## Penilaian jujur vs gambar pemenang
- KETERBATASAN: file referensi /tmp/w1.webp, /tmp/w2.webp,
  /tmp/w10.webp HILANG dari /tmp di tengah pengerjaan (listing
  awal masih ada, lalu direktori kosong — kemungkinan restart
  VM); gambar pemenang TIDAK berhasil dibaca di sesi ini.
  Penilaian di bawah memakai deskripsi brief + observasi v2
  yang tercatat, bukan perbandingan side-by-side segar.
- vs #1 (dari catatan v2 + brief): struktur kini sama persis
  (tanggal raksasa + strip angka + 3 lead + panel + peta +
  DATE CHECK). Lead kami lebih ilustratif dari #1 (lead #1
  sebagian besar teks + ikon kecil), dan Akvan kami = panel
  yang sudah dibandingkan langsung dengan lead #1 dan lolos gate.
- vs #10/#50: halaman kami jauh lebih padat (42 cerita vs
  ~5) — trade-off bawaan brief. Per cerita, hero pemenang
  tetap lebih berani; tapi halaman penuh v3 kini jelas lebih
  visual dari v2: 3 lead penuh warna berbeda + 12 panel
  bergambar, tanpa satu pun headline terpotong.
- Sisa kelemahan jujur: peta 404×124 agak gepeng (label
  HORMUZ/ODISHA berdekatan tapi terbaca); dua panel kriket
  memakai template scene yang sama (satu pertandingan yang
  sama — bisa dibenarkan); zona teks lead agak lega di bawah
  deck sebelum baris sumber (gaya lapang pemenang, bukan cacat).
- File: render_v3.py, entry_v3.png, manifest.json (diperbarui),
  render_v3_progress.md. Commit lokal (tanpa push).
