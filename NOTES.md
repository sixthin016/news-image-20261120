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
