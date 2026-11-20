#!/usr/bin/env python3
"""Render v4 — FULL PAGE news-image-20261120 (v3 + scene upgrades vs #1).

Perubahan vs v3 (lihat render_v4_progress.md): lead Akvan jadi scene
pesisir (bukan spiral abstrak — tagnya dulu tertabrak busur); scene lead
190->210px (ruang mati di bawah deck mengecil); subline miring di bawah
masthead + baris chip jumlah region; panel 09/23 bukan chart lagi
(fasad BSE / skyline + ticker); panel 01/03/27 jadi scene berwajah;
panel 31/37 digambar ulang supaya terbaca (reruntuhan / tambang
terbuka); kriket 41/42 dibedakan (keeper+tribun vs papan skor); peta
navy gelap + pin besar + label pill (tabrakan HORMUZ/ODISHA selesai);
COP31: delegasi + globe, laut dipangkas.
Manifest TIDAK diubah; validate() tetap menolak teks overflow (2 baris
max, tanpa "..."). Deterministik: tanpa jam/network/random tak berseed.
Membaca manifest.json dan menulis entry_v4.png 1024x1024.

Layout mengikuti pola pemenang #1: masthead raksasa tanggal
"Friday 20 November 2026", strip 6 angka besar, 3 lead BESAR
berilustrasi penuh (Akvan / Kyiv / COP31), 12 panel medium
berilustrasi, peta + daftar bernomor "ALSO ON FRIDAY 20 NOVEMBER",
kotak DATE CHECK lebar penuh, footer sumber.

Perubahan vs v2 (entry.png):
- Masthead: judul besar = tanggal (bukan "THE WORLD IN ONE PAGE").
- Lead: 3 — Akvan kini scene pesisir (draw_akvan_coast, ganti gate
  v3 yang tagnya tertabrak busur); Kyiv = jejak rudal di atas skyline
  malam + band data bawah; COP31 = Antalya + delegasi + globe.
- Angka: 6 angka besar dari gambar pemenang (300.000 / $97.17 /
  118 / ~30 / $120bn / 99), nilai BESAR di atas, label di bawah.
- NOL "..." di mana pun: headline/deck dipendekkan di manifest
  sampai muat penuh; validate() menolak bila wrap melebihi jatah
  baris (bukan memotong dengan elipsis seperti trunc1 v2).
- Set cerita dikoreksi ke peristiwa yang pertama dilaporkan Jumat
  20 Nov (lihat manifest.json + render_v3_progress.md); 10 item
  19 Nov pindah ke kotak DATE CHECK sebagai yang dikecualikan.

Run: python3 render_v4.py
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_v2 import (  # noqa: E402
    CARD, INK, LINE, MUTED, PAPER, REGION_COLORS, SS, add_grain,
    draw_flag_cn, draw_flag_ru, draw_flag_us, draw_map,
    font, sc_30, star_points, wrap,
)
from render import CONTINENTS, LAT_MAX, LAT_MIN, OCEAN_LABELS  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

RED = (192, 57, 43)
GOLD = (255, 214, 90)
DARK = (26, 26, 26)
NAVY = (27, 42, 74)

F_DATE = font("DejaVuSerif-Bold.ttf", 54)
F_SUB = ImageFont.truetype(
    "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf", 12)
F_CHIP = font("DejaVuSans-Bold.ttf", 8)
F_KICK = font("DejaVuSans-Bold.ttf", 11)
F_META = font("DejaVuSans.ttf", 11)
F_BAND = font("DejaVuSans-Bold.ttf", 13)
F_BAND_R = font("DejaVuSans.ttf", 11)
F_WIRE_T = font("DejaVuSans-Bold.ttf", 10)
F_WIRE = font("DejaVuSans.ttf", 9)
F_NUM_V = font("DejaVuSans-Bold.ttf", 24)
F_NUM_L = font("DejaVuSans-Bold.ttf", 8)
F_LEAD_H = font("DejaVuSans-Bold.ttf", 16)
F_LEAD_D = font("DejaVuSans.ttf", 11)
F_LEAD_K = font("DejaVuSans-Bold.ttf", 9)
F_PAN_H = font("DejaVuSans-Bold.ttf", 11)
F_PAN_D = font("DejaVuSans.ttf", 9)
F_MICRO = font("DejaVuSans.ttf", 8)
F_MICRO_B = font("DejaVuSans-Bold.ttf", 8)
F_SEC = font("DejaVuSans-Bold.ttf", 12)
F_LIST = font("DejaVuSans.ttf", 9)
F_LIST_B = font("DejaVuSans-Bold.ttf", 9)
F_TAG = font("DejaVuSans-Bold.ttf", 8)
F_DC = font("DejaVuSans-Bold.ttf", 10)
F_DC2 = font("DejaVuSans.ttf", 9)

LEAD_NUMS = ["02", "15", "14"]
PANEL_NUMS = ["01", "03", "05", "09", "21", "23",
              "27", "30", "31", "37", "41", "42"]
LEAD_KICKER = {"02": "ODISHA, INDIA — BAY OF BENGAL",
               "15": "KYIV, UKRAINE — OVERNIGHT",
               "14": "ANTALYA, TÜRKIYE — COP31"}


# ---------------------------------------------------------------- validation
def validate(d, data):
    """Gagal keras bila ada teks yang tidak muat — jangan pernah potong
    dengan '…' (cacat v2). Dijalankan sebelum render."""
    blob = json.dumps(data, ensure_ascii=False)
    assert "…" not in blob and "..." not in blob, "ellipsis in manifest"
    assert len(data["stories"]) == 41, "need 41 stories + hero"
    by_num = {s["num"]: s for s in data["stories"]}
    by_num["01"] = data["hero"]
    assert sorted(by_num) == [f"{i:02d}" for i in range(1, 43)]
    lw = (W - 32 - 2 * 10) / 3
    for num in LEAD_NUMS:
        s = by_num[num]
        assert len(wrap(d, s["headline"], F_LEAD_H, lw - 16)) <= 2, num
        assert len(wrap(d, s["deck"], F_LEAD_D, lw - 16)) <= 2, num
    pw = (W - 32 - 5 * 8) / 6
    for num in PANEL_NUMS:
        s = by_num[num]
        assert len(wrap(d, s["headline"], F_PAN_H, pw - 12)) <= 2, num
        assert len(wrap(d, s["deck"], F_PAN_D, pw - 12)) <= 2, num
    rest = [s for s in data["stories"]
            if s["num"] not in LEAD_NUMS and s["num"] not in PANEL_NUMS]
    assert len(rest) == 27, len(rest)
    col_w = (W - 16 - 436 - 2 * 10) / 3
    for s in rest:
        assert d.textlength(s["headline"], font=F_LIST) <= col_w - 30, s["num"]
    for val, lab in data["numbers"]:
        assert len(wrap(d, lab, F_NUM_L, (W - 32) / 6 - 16)) <= 2, val
    return by_num


# ---------------------------------------------------------------- lead scenes
def _finish(img, w, h, tag=None):
    final = img.convert("RGB").resize((w, h), Image.LANCZOS)
    if tag:
        dd = ImageDraw.Draw(final)
        tw = dd.textlength(tag, font=F_TAG) + 8
        dd.rectangle([5, 5, 5 + tw, 18], fill=(255, 255, 255),
                     outline=INK, width=1)
        dd.text((9, 7), tag, font=F_TAG, fill=INK)
    return final


def draw_kyiv_scene(w, h):
    """(15) Kyiv overnight — langit malam, skyline gelap berjendela
    terang, 3 jejak rudal oranye turun + 1 ledakan starburst.
    Render 2x -> LANCZOS. Bintang pakai random.Random berseed."""
    S = 2
    img = Image.new("RGB", (w * S, h * S))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    top, bot = (13, 19, 42), (52, 56, 88)
    for y in range(0, h, 2):
        t = y / max(1, h - 2)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.rectangle([0, y, w, y + 2], fill=col)
    rng = random.Random(20261120)
    for _ in range(46):
        sx, sy = rng.randrange(w), rng.randrange(70)
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=(220, 225, 240))
    # bulan sabit pucat, kanan atas
    d.ellipse([282, 12, 306, 36], fill=(240, 236, 210))
    d.ellipse([290, 10, 312, 36], fill=(28, 34, 62))
    # skyline gelap + jendela hangat (seeded, deterministik)
    base = h
    builds = [(0, 44, 62), (48, 58, 96), (110, 38, 70), (152, 52, 104),
              (208, 40, 76), (252, 56, 92), (300, 34, 58)]
    for bx, bw, bh in builds:
        d.rectangle([bx, base - bh, bx + bw, base], fill=(20, 25, 46))
        d.rectangle([bx, base - bh, bx + bw, base - bh + 3],
                    fill=(30, 36, 62))
    for _ in range(52):
        bx, bw, bh = builds[rng.randrange(len(builds))]
        wx = bx + 5 + rng.randrange(max(1, bw - 10))
        wy = base - bh + 6 + rng.randrange(max(1, bh - 12))
        d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 205, 110))
    # menara TV / antena di tengah (siluet + lampu merah)
    d.rectangle([160, 52, 166, base - 104], fill=(20, 25, 46))
    d.ellipse([161, 48, 165, 52], fill=(220, 60, 50))
    # 3 jejak rudal: garis terang menurun + kepala pijar + asap
    trails = [((30, 0), (96, 118), (255, 170, 80)),
              ((150, 0), (196, 128), (255, 200, 120)),
              ((262, 0), (228, 104), (255, 150, 60))]
    for (x1, y1), (x2, y2), col in trails:
        mx, my = (x1 + x2) / 2 + 14, (y1 + y2) / 2
        d.line([x1, y1, mx, my, x2, y2], fill=(120, 120, 130), width=4)
        d.line([x1, y1, mx, my, x2, y2], fill=col, width=2)
        d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=(255, 240, 190))
    # ledakan starburst di atap gedung kiri-tengah (fokus, paling depan)
    ex, ey = 96, 118
    d0.polygon(star_points(ex * S, ey * S, 26 * S, 11 * S, 8),
               fill=(240, 120, 30))
    d0.polygon(star_points(ex * S, ey * S, 16 * S, 7 * S, 8),
               fill=(255, 200, 60))
    d0.polygon(star_points(ex * S, ey * S, 8 * S, 3 * S, 8),
               fill=(255, 240, 180))
    d.ellipse([ex + 12, ey - 26, ex + 26, ey - 12], fill=(110, 110, 120))
    # band data bawah ala #1 (waktu + jumlah gelombang/rudal)
    d.rectangle([0, h - 20, w, h], fill=(10, 14, 30))
    d0.text((8 * S, (h - 16) * S), "01:25 LOCAL  \u2022  7 WAVES",
            font=font("DejaVuSans-Bold.ttf", 9 * S), fill=(255, 255, 255))
    d0.text((222 * S, (h - 16) * S), "~30 MISSILES",
            font=font("DejaVuSans-Bold.ttf", 9 * S), fill=(255, 120, 70))
    return _finish(img, w, h, "KYIV — OVERNIGHT")


def draw_cop31_scene(w, h):
    """(14) COP31 Antalya v4 — langit krem, matahari emas, globe +
    delegasi di depan gedung konferensi, laut dipangkas ke bawah.
    Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S), (250, 240, 220))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # matahari emas kiri atas + awan tipis
    d.ellipse([16, 8, 46, 38], fill=(235, 175, 60))
    d.ellipse([66, 18, 104, 26], fill=(255, 255, 255))
    # "$120BN" kanan atas (26pt) + garis bawah + sublabel
    d0.text((188 * S, 12 * S), "$120BN",
            font=font("DejaVuSans-Bold.ttf", 26 * S), fill=(18, 90, 95))
    d.line([188, 46, 296, 46], fill=(18, 90, 95), width=3)
    d0.text((188 * S, 52 * S), "ADAPTATION — NOT AGREED",
            font=font("DejaVuSans-Bold.ttf", 8 * S), fill=(120, 60, 50))
    # globe di atas palem, kanan: bola teal + benua hijau + dudukan
    d.ellipse([236, 66, 272, 102], fill=(70, 150, 170),
              outline=(18, 90, 95), width=2)
    d.ellipse([244, 72, 256, 84], fill=(80, 160, 90))
    d.ellipse([256, 86, 268, 98], fill=(80, 160, 90))
    d.line([254, 102, 254, 110], fill=(90, 90, 90), width=2)
    d.line([244, 110, 264, 110], fill=(90, 90, 90), width=2)
    # gedung konferensi putih (kiri-tengah) + kaca biru
    d.rectangle([28, 62, 168, 112], fill=(255, 255, 255),
                outline=(120, 120, 120), width=2)
    d.polygon([(28, 62), (168, 62), (148, 48), (48, 48)], fill=(18, 90, 95))
    for i in range(6):
        d.rectangle([38 + i * 21, 74, 52 + i * 21, 100], fill=(90, 160, 175))
    # deret bendera di atap gedung
    flag_cols = [(200, 50, 43), (255, 255, 255), (18, 90, 95), (235, 175, 60),
                 (60, 120, 60), (40, 60, 120), (200, 50, 43), (255, 255, 255)]
    for i, c in enumerate(flag_cols):
        fx = 44 + i * 15
        d.line([fx, 30, fx, 48], fill=(90, 90, 90), width=1)
        d.rectangle([fx, 32, fx + 11, 42], fill=c, outline=(60, 60, 60))
    # 3 delegasi di depan gedung (bust kecil berwajah: mata 2 titik)
    for cx, skin, hair, suit in ((62, (210, 170, 130), (240, 240, 240),
                                  (38, 55, 90)),
                                 (98, (232, 190, 150), (60, 45, 30),
                                  (26, 26, 26)),
                                 (134, (238, 205, 170), (90, 60, 40),
                                  (60, 40, 90))):
        d.pieslice([cx - 13, 96, cx + 13, 108], 180, 360, fill=suit)
        d.rectangle([cx - 13, 102, cx + 13, 112], fill=suit)
        d.ellipse([cx - 6, 86, cx + 6, 98], fill=skin, outline=INK, width=1)
        d.polygon([(cx + 6 * math.cos(math.radians(a)),
                    92 + 6 * math.sin(math.radians(a)))
                   for a in range(200, 341, 10)], fill=hair)
        d.ellipse([cx - 3, 91, cx - 1, 93], fill=INK)
        d.ellipse([cx + 1, 91, cx + 3, 93], fill=INK)
    # 1 palem kanan bawah (satunya diganti globe)
    d.line([300, 126, 304, 92], fill=(120, 85, 55), width=3)
    for a in (200, 240, 290, 330):
        ex = 302 + 16 * math.cos(math.radians(a))
        ey = 92 + 8 * math.sin(math.radians(a))
        d.line([302, 92, ex, ey], fill=(50, 130, 70), width=3)
    # pantai pasir + laut teal dipangkas (2 baris ombak saja)
    d.rectangle([0, 112, w, 126], fill=(232, 214, 170))
    d.rectangle([0, 126, w, h], fill=(64, 138, 148))
    for wy in (140, 160):
        for i in range(5):
            ax = 6 + i * w // 5
            d.arc([ax, wy - 5, ax + w // 5 - 4, wy + 6], 180, 360,
                  fill=(230, 245, 245), width=2)
    return _finish(img, w, h, "ANTALYA — COP31")


def draw_akvan_coast(w, h):
    """(02) Cyclone Akvan v4 — scene pesisir ala #1: daratan tan di
    kiri dengan garis pantai, spiral di atas laut kanan, label
    ODISHA / Gopalpur / BAY OF BENGAL, band data bawah. Tag TIDAK
    lagi ditulis di bawah busur (cacat v3). Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # laut: gradien navy-teal
    top, bot = (16, 58, 96), (10, 40, 78)
    for y in range(0, h, 2):
        t = y / max(1, h - 2)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.rectangle([0, y, w, y + 2], fill=col)
    # daratan tan di kiri (garis pantai berlekuk)
    coast = [(0, 0), (168, 0), (146, 44), (124, 88), (108, 132),
             (96, 176), (92, h), (0, h)]
    d.polygon(coast, fill=(232, 214, 170))
    d.line(coast[1:], fill=(250, 244, 220), width=2)
    # rumah-rumah kecil di daratan dekat pantai
    for hx, hy, hw, hh in ((30, 96, 16, 12), (58, 116, 14, 10),
                           (36, 140, 18, 12)):
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=(190, 170, 140),
                    outline=(120, 105, 80), width=1)
        d.polygon([(hx - 2, hy), (hx + hw + 2, hy),
                   (hx + hw // 2, hy - 6)], fill=(160, 60, 45))
    # spiral di atas laut (pusat di kanan, busur offset = pusaran)
    ex, ey = 212, 88
    rings = [(16, -40, 300, 6, (255, 255, 255)),
             (29, 55, 295, 5, (255, 255, 255)),
             (42, 140, 290, 5, (255, 255, 255)),
             (56, 225, 285, 5, (235, 240, 248)),
             (71, 310, 280, 5, (214, 226, 238)),
             (87, 35, 275, 4, (214, 226, 238)),
             (104, 120, 265, 4, (214, 226, 238)),
             (122, 205, 255, 4, (214, 226, 238))]
    for k, (r, a0, sweep, wd, col) in enumerate(rings):
        cx, cy = ex - k * 5, ey + k * 3
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + sweep,
              fill=col, width=wd)
    d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13], fill=(245, 233, 200))
    d.ellipse([ex - 13, ey - 13, ex + 13, ey + 13],
              outline=(255, 255, 255), width=2)
    # hujan: garis miring putih tipis di atas laut dekat pantai
    for rx, ry in ((150, 40), (162, 70), (146, 110), (170, 130),
                   (156, 160), (180, 96)):
        d.line([rx, ry, rx - 5, ry + 10], fill=(200, 215, 230), width=2)
    # label daratan + titik landfall Gopalpur di garis pantai
    d0.text((10 * S, 8 * S), "ODISHA",
            font=font("DejaVuSans-Bold.ttf", 11 * S), fill=(40, 35, 25))
    d0.text((10 * S, 22 * S), "INDIA",
            font=font("DejaVuSans.ttf", 8 * S), fill=(90, 80, 60))
    d.ellipse([120, 84, 128, 92], fill=(200, 50, 43),
              outline=(255, 255, 255), width=1)
    d0.text((52 * S, 96 * S), "Gopalpur",
            font=font("DejaVuSans-Bold.ttf", 8 * S), fill=(40, 35, 25))
    d0.text((228 * S, (h - 40) * S), "BAY OF BENGAL",
            font=font("DejaVuSans-Bold.ttf", 8 * S), fill=(200, 215, 230))
    # band data bawah (gelap, teks tidak tertabrak busur)
    d.rectangle([0, h - 20, w, h], fill=(10, 14, 30))
    d0.text((8 * S, (h - 16) * S), "LANDFALL  \u2022  GUSTS 110 KM/H",
            font=font("DejaVuSans-Bold.ttf", 9 * S), fill=(255, 255, 255))
    d0.text((232 * S, (h - 16) * S), "CYCLONE AKVAN",
            font=font("DejaVuSans-Bold.ttf", 9 * S), fill=(255, 214, 90))
    return img.convert("RGB").resize((w, h), Image.LANCZOS)


# ---------------------------------------------------------------- panel scenes
def sc_01(d, x0, y0, w, h):
    """(01) Declaration v4: 3 bendera + dokumen putih + segel merah +
    dua lengan berjabat tangan di atas dokumen + ground band."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 236, 220))
    draw_flag_us(d, x0 + 8, y0 + 5, 40, 19)
    draw_flag_cn(d, x0 + w // 2 - 20, y0 + 5, 40, 19)
    draw_flag_ru(d, x0 + w - 48, y0 + 5, 40, 19)
    d.rectangle([x0 + w * 0.28, y0 + 28, x0 + w * 0.72, y0 + h - 12],
                fill=(255, 255, 255), outline=INK, width=1)
    for i, ly in enumerate((34, 39)):
        d.line([x0 + w * 0.32, y0 + ly, x0 + w * 0.68, y0 + ly],
               fill=(150, 150, 150), width=1)
    d.ellipse([x0 + w * 0.60, y0 + h - 22, x0 + w * 0.68, y0 + h - 14],
              fill=(200, 50, 43), outline=(255, 255, 255), width=1)
    # ground band + jabat tangan: lengan navy (kiri) & olive (kanan)
    # bertemu di kepalan tangan peach di tengah bawah dokumen
    d.rectangle([x0, y0 + h - 8, x0 + w, y0 + h], fill=(210, 195, 165))
    cx, cy = x0 + w // 2, y0 + h - 13
    d.polygon([(x0 + 4, cy - 5), (cx - 8, cy - 6), (cx - 8, cy + 2),
               (x0 + 4, cy + 4)], fill=(38, 55, 90))
    d.polygon([(x0 + w - 4, cy - 5), (cx + 8, cy - 6), (cx + 8, cy + 2),
               (x0 + w - 4, cy + 4)], fill=(90, 90, 60))
    d.ellipse([cx - 8, cy - 7, cx + 8, cy + 7], fill=(232, 190, 150),
              outline=INK, width=1)
    d.line([cx - 4, cy - 2, cx + 4, cy - 2], fill=(180, 140, 110), width=1)
    d.line([cx - 4, cy + 2, cx + 4, cy + 2], fill=(180, 140, 110), width=1)


def sc_05(d, x0, y0, w, h):
    """(05) GTA VI: latar gelap, "99" emas raksasa + 5 bintang."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(24, 20, 40))
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=(90, 70, 140), width=1)
    d.text((x0 + 10, y0 + 2), "99", font=font("DejaVuSans-Bold.ttf", 34),
           fill=(255, 205, 80))
    d.text((x0 + 74, y0 + 8), "METACRITIC", font=F_MICRO_B,
           fill=(255, 255, 255))
    d.text((x0 + 74, y0 + 20), "151 REVIEWS", font=F_MICRO,
           fill=(200, 200, 220))
    for i in range(5):
        sx = x0 + 78 + i * 13
        d.polygon(star_points(sx, y0 + h - 12, 6, 3), fill=(255, 205, 80))
    # palem mini khas Vice City, kanan bawah
    d.line([x0 + w - 16, y0 + h, x0 + w - 12, y0 + h - 22],
           fill=(120, 85, 55), width=2)
    for a in (200, 250, 300, 340):
        ex = x0 + w - 14 + 10 * math.cos(math.radians(a))
        ey = y0 + h - 22 + 5 * math.sin(math.radians(a))
        d.line([x0 + w - 14, y0 + h - 22, ex, ey], fill=(50, 160, 90), width=2)


def sc_21(d, x0, y0, w, h):
    """(21) Steel plant blast: atap gergaji + cerobong + ledakan."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(235, 225, 210))
    d.rectangle([x0 + 8, y0 + 26, x0 + 16, y0 + h], fill=(110, 105, 100))
    d.ellipse([x0 + 6, y0 + 20, x0 + 18, y0 + 28], fill=(140, 140, 140))
    d.polygon([(x0 + 20, y0 + h), (x0 + 20, y0 + 30), (x0 + 48, y0 + 18),
               (x0 + 76, y0 + 30), (x0 + 104, y0 + 18), (x0 + 132, y0 + 30),
               (x0 + 132, y0 + h)], fill=(90, 88, 92))
    for i in range(3):
        d.rectangle([x0 + 28 + i * 30, y0 + 36, x0 + 40 + i * 30, y0 + 44],
                    fill=(255, 205, 110))
    ex, ey = x0 + w * 0.68, y0 + 14
    d.polygon(star_points(ex, ey, 15, 6, 8), fill=(240, 120, 30))
    d.polygon(star_points(ex, ey, 8, 3, 8), fill=(255, 210, 60))
    d.ellipse([ex - 20, ey - 16, ex - 6, ey - 2], fill=(140, 140, 140))


def sc_23(d, x0, y0, w, h):
    """(23) US stocks slide v4: skyline malam + ticker merah
    "-2% NASDAQ" + satu trader berwajah (mata + mulut turun)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 44, 62))
    # skyline gelap + jendela hangat
    for bx, bw, bh in ((6, 26, 26), (36, 22, 34), (62, 26, 22),
                       (92, 24, 30), (120, 26, 24)):
        d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + bw, y0 + h],
                    fill=(22, 26, 44))
        for wx in range(bx + 4, bx + bw - 4, 8):
            for wy in range(h - bh + 5, h - 6, 9):
                d.rectangle([x0 + wx, y0 + wy, x0 + wx + 3, y0 + wy + 4],
                            fill=(255, 205, 110))
    # ticker merah di tengah
    d.rectangle([x0, y0 + 8, x0 + w, y0 + 22], fill=(160, 30, 25))
    d.text((x0 + 6, y0 + 11), "-2% NASDAQ", font=F_MICRO_B,
           fill=(255, 255, 255))
    d.polygon([(x0 + w - 26, y0 + 12), (x0 + w - 14, y0 + 12),
               (x0 + w - 20, y0 + 20)], fill=(255, 255, 255))
    # trader: kepala + bahu, mulut turun (khawatir)
    cx, cy = x0 + w - 26, y0 + h - 26
    d.pieslice([cx - 14, cy + 2, cx + 14, cy + 12], 180, 360,
               fill=(38, 55, 90))
    d.rectangle([cx - 14, cy + 7, cx + 14, y0 + h], fill=(38, 55, 90))
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(232, 190, 150),
              outline=INK, width=1)
    d.polygon([(cx + 7 * math.cos(math.radians(a)),
                cy + 7 * math.sin(math.radians(a)))
               for a in range(200, 341, 10)], fill=(60, 45, 30))
    d.ellipse([cx - 4, cy - 2, cx - 2, cy], fill=INK)
    d.ellipse([cx + 2, cy - 2, cx + 4, cy], fill=INK)
    d.arc([cx - 3, cy + 1, cx + 3, cy + 6], 200, 340, fill=INK, width=1)


def sc_27b(d, x0, y0, w, h):
    """(27) Anthropic debut close v4: skyline + garis emas naik +
    "$97.17" di latar gelap (bukan glyph chip)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 34, 48))
    # skyline gelap + jendela emas
    for bx, bw, bh in ((4, 24, 20), (32, 20, 28), (56, 26, 16),
                       (86, 22, 24), (112, 24, 18)):
        d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + bw, y0 + h],
                    fill=(18, 22, 38))
        for wx in range(bx + 4, bx + bw - 4, 8):
            d.rectangle([x0 + wx, y0 + h - bh + 5, x0 + wx + 3,
                         y0 + h - bh + 9], fill=(255, 205, 110))
    # garis emas naik di atas skyline — dijaga di bawah teks "+17%
    # DEBUT" (y0+28..36): titik kiri di h-10..h-16, ujung kanan naik
    d.line([(x0 + 6, y0 + h - 10), (x0 + 40, y0 + h - 18),
            (x0 + 76, y0 + h - 16), (x0 + 112, y0 + h - 28),
            (x0 + w - 8, y0 + h - 34)], fill=GOLD, width=3)
    d.polygon([(x0 + w - 8, y0 + h - 40), (x0 + w - 2, y0 + h - 36),
               (x0 + w - 10, y0 + h - 28)], fill=GOLD)
    d.text((x0 + 8, y0 + 6), "$97.17", font=font("DejaVuSans-Bold.ttf", 17),
           fill=(255, 255, 255))
    d.text((x0 + 8, y0 + 28), "+17% DEBUT", font=F_MICRO_B, fill=GOLD)


def sc_41(d, x0, y0, w, h):
    """(41) Nicholls 175* v4: tribun penonton + batsman + wicketkeeper
    di belakang stumps — beda komposisi dari panel 42."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 225, 190))
    # tribun: band hijau gelap + 2 baris penonton (titik warna-warni)
    d.rectangle([x0, y0, x0 + w, y0 + 12], fill=(30, 90, 50))
    for i, c in enumerate([(255, 255, 255), (255, 205, 80), (200, 60, 50),
                           (90, 160, 220), (255, 255, 255), (255, 205, 80),
                           (200, 60, 50), (90, 160, 220), (255, 255, 255),
                           (255, 205, 80)]):
        d.ellipse([x0 + 8 + i * 14, y0 + 4, x0 + 13 + i * 14, y0 + 9],
                  fill=c)
    # pitch
    d.rectangle([x0 + w * 0.30, y0 + 14, x0 + w * 0.70, y0 + h - 4],
                fill=(232, 214, 170))
    # stumps + wicketkeeper berjongkok di belakangnya
    sx = x0 + w * 0.66
    for i in range(3):
        d.line([sx - 4 + i * 4, y0 + 18, sx - 4 + i * 4, y0 + 30],
               fill=(200, 170, 60), width=2)
    kx, ky = x0 + w * 0.80, y0 + 30
    d.ellipse([kx - 5, ky - 5, kx + 5, ky + 5], fill=(232, 190, 150),
              outline=INK, width=1)
    d.line([kx, ky + 5, kx + 1, ky + 14], fill=(20, 60, 120), width=5)
    d.line([kx + 1, ky + 14, kx - 3, y0 + h - 6], fill=(20, 60, 120),
           width=4)
    d.line([kx + 1, ky + 14, kx + 6, y0 + h - 6], fill=(20, 60, 120),
           width=4)
    # batsman: kepala + badan + kaki + bat mid-swing
    bx, by = x0 + w * 0.42, y0 + 32
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(232, 190, 150),
              outline=INK, width=1)
    d.arc([bx - 6, by - 8, bx + 6, by + 2], 180, 360, fill=(40, 40, 40),
          width=3)
    d.line([bx, by + 6, bx + 2, by + 18], fill=(255, 255, 255), width=5)
    d.line([bx + 2, by + 18, bx - 2, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 2, by + 18, bx + 8, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 4, by + 10, bx + 16, by + 26], fill=(180, 140, 80), width=4)
    d.ellipse([x0 + w * 0.16 - 4, y0 + h - 14, x0 + w * 0.16 + 4,
               y0 + h - 6], fill=(200, 40, 40))
    d.text((x0 + 6, y0 + 14), "175*", font=font("DejaVuSans-Bold.ttf", 10),
           fill=(20, 80, 40))


def sc_42(d, x0, y0, w, h):
    """(42) Phillips 118 v4: papan skor besar + stumps & bails
    terlempar — TANPA batsman, komposisi beda dari panel 41."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 225, 190))
    d.rectangle([x0 + w * 0.30, y0 + 6, x0 + w * 0.70, y0 + h - 4],
                fill=(232, 214, 170))
    # papan skor gelap di kiri
    d.rectangle([x0 + 6, y0 + 8, x0 + w * 0.52, y0 + 40], fill=(26, 26, 26),
                outline=GOLD, width=1)
    d.text((x0 + 10, y0 + 11), "NZ 368", font=F_MICRO_B,
           fill=(255, 255, 255))
    d.text((x0 + 10, y0 + 23), "PHILLIPS 118", font=F_MICRO_B, fill=GOLD)
    # stumps kanan + bails terlempar + bola merah
    sx = x0 + w * 0.66
    for i in range(3):
        d.line([sx - 4 + i * 4, y0 + 14, sx - 4 + i * 4, y0 + 28],
               fill=(200, 170, 60), width=2)
    d.rectangle([sx - 6, y0 + 6, sx - 1, y0 + 9], fill=(255, 220, 80))
    d.rectangle([sx + 6, y0 + 4, sx + 11, y0 + 7], fill=(255, 220, 80))
    d.ellipse([x0 + w * 0.84 - 4, y0 + h - 14, x0 + w * 0.84 + 4,
               y0 + h - 6], fill=(200, 40, 40))
    d.line([x0 + w * 0.78, y0 + h - 18, x0 + w * 0.84, y0 + h - 10],
           fill=(200, 40, 40), width=2)
    d.line([x0 + w * 0.78, y0 + h - 8, x0 + w * 0.84, y0 + h - 12],
           fill=(200, 40, 40), width=2)


def _bust_face(d, cx, head_y, r, y1, skin, hair, suit, long_hair=False):
    """Bust kecil BERWAJAH: mata 2 titik + mulut — v4 (v3 tanpa wajah)."""
    if long_hair:
        d.ellipse([cx - r - 2, head_y - r - 2, cx + r + 2, head_y + r + 6],
                  fill=hair)
    d.pieslice([cx - r * 2, head_y + r - 4, cx + r * 2, head_y + r + 10],
               180, 360, fill=suit)
    d.rectangle([cx - r * 2, head_y + r + 2, cx + r * 2, y1], fill=suit)
    d.polygon([(cx - 4, head_y + r + 1), (cx + 4, head_y + r + 1),
               (cx, head_y + r + 7)], fill=(255, 255, 255))
    d.ellipse([cx - r, head_y - r, cx + r, head_y + r], fill=skin,
              outline=INK, width=1)
    pts = [(cx + r * math.cos(math.radians(a)),
            head_y + r * math.sin(math.radians(a)))
           for a in range(200, 341, 5)]
    d.polygon(pts, fill=hair, outline=INK)
    d.ellipse([cx - r * 0.45, head_y - 1, cx - r * 0.45 + 2, head_y + 1],
              fill=INK)
    d.ellipse([cx + r * 0.45 - 2, head_y - 1, cx + r * 0.45, head_y + 1],
              fill=INK)
    d.line([cx - 3, head_y + r * 0.5, cx + 3, head_y + r * 0.5],
           fill=(120, 70, 60), width=1)


def sc_03v4(d, x0, y0, w, h):
    """(03) Modi + William & Kate v4: wajah + India Gate mini di
    belakang + karpet merah di dasar."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 236, 220))
    # India Gate: lengkung + tiang, siluet tan di tengah atas
    gx = x0 + w // 2
    d.rectangle([gx - 22, y0 + 6, gx - 14, y0 + 22], fill=(200, 175, 130))
    d.rectangle([gx + 14, y0 + 6, gx + 22, y0 + 22], fill=(200, 175, 130))
    d.pieslice([gx - 22, y0 - 4, gx + 22, y0 + 16], 180, 360,
               fill=(200, 175, 130))
    d.rectangle([gx - 26, y0 + 22, gx + 26, y0 + 25], fill=(180, 155, 110))
    # bendera India (kiri atas) + Union Jack (kanan atas)
    d.rectangle([x0 + 6, y0 + 5, x0 + 26, y0 + 8], fill=(255, 153, 51))
    d.rectangle([x0 + 6, y0 + 8, x0 + 26, y0 + 11], fill=(255, 255, 255))
    d.rectangle([x0 + 6, y0 + 11, x0 + 26, y0 + 14], fill=(19, 136, 8))
    d.rectangle([x0 + w - 26, y0 + 5, x0 + w - 6, y0 + 14], fill=(0, 36, 125))
    d.line([x0 + w - 26, y0 + 9, x0 + w - 6, y0 + 9], fill=(255, 255, 255), width=2)
    d.line([x0 + w - 16, y0 + 5, x0 + w - 16, y0 + 14], fill=(255, 255, 255), width=2)
    _bust_face(d, x0 + w * 0.24, y0 + 30, 9, y0 + h - 5, (210, 170, 130),
               (240, 240, 240), (70, 70, 70))
    _bust_face(d, x0 + w * 0.50, y0 + 28, 9, y0 + h - 5, (232, 190, 150),
               (210, 170, 90), (38, 55, 90))
    _bust_face(d, x0 + w * 0.76, y0 + 30, 9, y0 + h - 5, (238, 205, 170),
               (90, 60, 40), (60, 40, 90), long_hair=True)
    d.rectangle([x0, y0 + h - 5, x0 + w, y0 + h], fill=(180, 40, 30))


def sc_09v4(d, x0, y0, w, h):
    """(09) Sensex v4: fasad BSE (gedung + grid jendela + jam) +
    ticker band hijau "+1.21%" + pennant di atap — bukan chart."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(226, 240, 226))
    # gedung bursa krem + pedimen + jam
    d.rectangle([x0 + 10, y0 + 16, x0 + w - 10, y0 + h - 10],
                fill=(250, 246, 235), outline=(120, 120, 110), width=1)
    d.polygon([(x0 + 10, y0 + 16), (x0 + w - 10, y0 + 16),
               (x0 + w // 2, y0 + 5)], fill=(30, 122, 76))
    d.ellipse([x0 + w // 2 - 6, y0 + 8, x0 + w // 2 + 6, y0 + 20],
              fill=(255, 255, 255), outline=INK, width=1)
    d.line([x0 + w // 2, y0 + 14, x0 + w // 2, y0 + 10], fill=INK, width=1)
    d.line([x0 + w // 2, y0 + 14, x0 + w // 2 + 3, y0 + 14], fill=INK, width=1)
    for r in range(2):
        for c in range(5):
            d.rectangle([x0 + 18 + c * 24, y0 + 24 + r * 10,
                         x0 + 30 + c * 24, y0 + 32 + r * 10],
                        fill=(60, 130, 90))
    # pennant hijau kecil di atap kanan
    d.line([x0 + w - 22, y0 + 2, x0 + w - 22, y0 + 12], fill=(90, 90, 90),
           width=1)
    d.polygon([(x0 + w - 22, y0 + 2), (x0 + w - 10, y0 + 5),
               (x0 + w - 22, y0 + 8)], fill=(20, 100, 60))
    # ticker band hijau di dasar
    d.rectangle([x0, y0 + h - 11, x0 + w, y0 + h], fill=(20, 100, 60))
    d.text((x0 + 6, y0 + h - 9), "+1.21%  SENSEX", font=F_MICRO_B,
           fill=(255, 255, 255))


def sc_31v4(d, x0, y0, w, h):
    """(31) Gaza v4: jalan reruntuhan — gedung utuh kiri, gedung
    patah bergerigi kanan, puing di dasar, figur helm putih tengah."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(228, 224, 214))
    # gedung utuh kiri + jendela gelap
    d.rectangle([x0 + 8, y0 + 10, x0 + 44, y0 + h], fill=(150, 140, 125))
    for r in range(3):
        d.rectangle([x0 + 14, y0 + 16 + r * 11, x0 + 38, y0 + 22 + r * 11],
                    fill=(90, 85, 75))
    # gedung patah kanan (puncak bergerigi) + debu
    d.polygon([(x0 + 60, y0 + h), (x0 + 60, y0 + 30), (x0 + 74, y0 + 20),
               (x0 + 84, y0 + 30), (x0 + 96, y0 + 22), (x0 + 108, y0 + 32),
               (x0 + 120, y0 + 26), (x0 + 128, y0 + h)], fill=(120, 112, 100))
    d.ellipse([x0 + 88, y0 + 4, x0 + 108, y0 + 20], fill=(150, 148, 142))
    d.ellipse([x0 + 100, y0 + 12, x0 + 116, y0 + 26], fill=(168, 166, 160))
    # puing segitiga di dasar
    for px, pw, ph in ((52, 16, 8), (76, 20, 10), (104, 18, 9), (126, 14, 7)):
        d.polygon([(x0 + px, y0 + h), (x0 + px + pw // 2, y0 + h - ph),
                   (x0 + px + pw, y0 + h)], fill=(100, 94, 84))
    # figur helm putih membawa bundel
    fx, fy = x0 + w * 0.42, y0 + h - 22
    d.ellipse([fx - 5, fy - 5, fx + 5, fy + 5], fill=(255, 255, 255),
              outline=INK, width=1)
    d.line([fx, fy + 5, fx + 1, fy + 13], fill=(220, 110, 40), width=5)
    d.line([fx + 1, fy + 13, fx - 2, y0 + h - 2], fill=(40, 40, 40), width=3)
    d.line([fx + 1, fy + 13, fx + 4, y0 + h - 2], fill=(40, 40, 40), width=3)


def sc_37v4(d, x0, y0, w, h):
    """(37) Sudan gold mine v4: tambang terbuka berteras + jalan
    angkut + truk kuning + bongkahan emas + debu."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 220, 200))
    # teras tambang: 3 tingkat cokelat menurun ke tengah
    d.polygon([(x0 + 6, y0 + 8), (x0 + w - 6, y0 + 8), (x0 + w - 6, y0 + h),
               (x0 + 6, y0 + h)], fill=(190, 160, 120))
    d.polygon([(x0 + 18, y0 + 18), (x0 + w - 18, y0 + 18),
               (x0 + w - 18, y0 + h), (x0 + 18, y0 + h)],
              fill=(170, 140, 100))
    d.polygon([(x0 + 32, y0 + 30), (x0 + w - 32, y0 + 30),
               (x0 + w - 32, y0 + h), (x0 + 32, y0 + h)],
              fill=(150, 120, 82))
    d.ellipse([x0 + w // 2 - 12, y0 + h - 18, x0 + w // 2 + 12, y0 + h - 4],
              fill=(40, 32, 24))
    # jalan angkut diagonal + truk kuning kecil
    d.line([(x0 + 8, y0 + h - 6), (x0 + w - 30, y0 + 22)],
           fill=(220, 195, 150), width=4)
    tx, ty = x0 + w * 0.62, y0 + h * 0.42
    d.rectangle([tx, ty, tx + 16, ty + 7], fill=(230, 180, 40),
                outline=INK, width=1)
    d.ellipse([tx + 3, ty + 7, tx + 7, ty + 11], fill=INK)
    d.ellipse([tx + 10, ty + 7, tx + 14, ty + 11], fill=INK)
    # debu + bongkahan emas
    d.ellipse([x0 + w - 34, y0 + 4, x0 + w - 18, y0 + 16],
              fill=(200, 190, 170))
    for gx, gy, gr in ((0.16, 0.82, 5), (0.26, 0.72, 4), (0.86, 0.82, 5)):
        d.ellipse([x0 + w * gx - gr, y0 + h * gy - gr, x0 + w * gx + gr,
                   y0 + h * gy + gr], fill=(230, 180, 40),
                  outline=(150, 110, 20))


PANEL_SCENES = {"01": sc_01, "03": sc_03v4, "05": sc_05, "09": sc_09v4,
                "21": sc_21, "23": sc_23, "27": sc_27b, "30": sc_30,
                "31": sc_31v4, "37": sc_37v4, "41": sc_41, "42": sc_42}


def lead_scene(num, w, h):
    if num == "02":
        return draw_akvan_coast(w, h)
    if num == "15":
        return draw_kyiv_scene(w, h)
    return draw_cop31_scene(w, h)


# ---------------------------------------------------------------- cards
def draw_lead(d, img, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLORS[s["region"]])
    scene_h = 210
    scene = lead_scene(s["num"], int(w - 2), scene_h)
    img.paste(scene, (int(x + 1), int(y + 5)))
    ty = y + 5 + scene_h + 7
    d.text((x + 8, ty), s["num"] + " • " + LEAD_KICKER[s["num"]],
           font=F_LEAD_K, fill=RED)
    lines = wrap(d, s["headline"], F_LEAD_H, w - 16)
    for i, line in enumerate(lines[:2]):
        d.text((x + 8, ty + 15 + i * 19), line, font=F_LEAD_H, fill=INK)
    dy = ty + 15 + len(lines) * 19 + 4
    for i, line in enumerate(wrap(d, s["deck"], F_LEAD_D, w - 16)[:2]):
        d.text((x + 8, dy + i * 14), line, font=F_LEAD_D, fill=(74, 72, 66))
    d.text((x + 8, y + h - 14), "20 NOV • " + s["source"], font=F_MICRO,
           fill=MUTED)
    tag = "STORY " + s["num"] + " OF 42"
    tw = d.textlength(tag, font=F_MICRO_B)
    d.text((x + w - 8 - tw, y + h - 14), tag, font=F_MICRO_B, fill=RED)


def draw_panel(d, s, x, y, w, h):
    """Panel medium: strip gambar 45% + headline 2 baris + deck
    2 baris — semua muat penuh (validate() menjamin), tanpa '…'."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=REGION_COLORS[s["region"]])
    scene_h = int(h * 0.45)
    PANEL_SCENES[s["num"]](d, x + 1, y + 4, w - 2, scene_h)
    ty = y + 4 + scene_h + 5
    d.text((x + 6, ty), s["num"] + " • " + s["region"], font=F_MICRO_B,
           fill=REGION_COLORS[s["region"]])
    lines = wrap(d, s["headline"], F_PAN_H, w - 12)
    for i, line in enumerate(lines[:2]):
        d.text((x + 6, ty + 11 + i * 13), line, font=F_PAN_H, fill=INK)
    dy = ty + 11 + len(lines) * 13 + 2
    for i, line in enumerate(wrap(d, s["deck"], F_PAN_D, w - 12)[:2]):
        d.text((x + 6, dy + i * 11), line, font=F_PAN_D, fill=(74, 72, 66))


# ---------------------------------------------------------------- sections
def draw_masthead(d, data):
    d.text((16, 2), "ONE DAY OF WORLD NEWS, ONE PICTURE", font=F_KICK,
           fill=RED)
    meta_r = "42 STORIES  •  6 REGIONS"
    mw = d.textlength(meta_r, font=F_META)
    d.text((W - 16 - mw, 4), meta_r, font=F_META, fill=MUTED)
    d.text((16, 12), data["title"], font=F_DATE, fill=INK)
    sub = ("Akvan slams into Odisha  \u2022  Missiles rain on Kyiv  "
           "\u2022  COP31 split over $120bn fund  \u2022  US stocks slide")
    sw = d.textlength(sub, font=F_SUB)
    d.text(((W - sw) / 2, 69), sub, font=F_SUB, fill=(160, 45, 35))
    d.rectangle([0, 86, W, 114], fill=DARK)
    d.text((16, 94), "THE WORLD IN ONE PAGE", font=F_BAND, fill=GOLD)
    right = "EVERY STORY FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026"
    rw = d.textlength(right, font=F_BAND_R)
    d.text((W - 16 - rw, 96), right, font=F_BAND_R, fill=(200, 200, 200))


def draw_wires(d, data, y0, y1):
    d.rectangle([16, y0, 116, y1], fill=RED)
    d.text((24, y0 + 8), "THE DAY", font=F_WIRE_T, fill=(255, 255, 255))
    d.text((24, y0 + 22), "IN UTC", font=F_WIRE_T, fill=(255, 255, 255))
    d.text((24, y0 + 36), "20 NOV", font=F_MICRO_B, fill=GOLD)
    x = 126
    col_w = (W - 16 - x - 4 * 10) // 5
    for t, item in data["wires"]:
        d.text((x, y0 + 2), "~" + t + " UTC", font=F_WIRE_T, fill=RED)
        for i, line in enumerate(wrap(d, item, F_WIRE, col_w)):
            d.text((x, y0 + 17 + i * 12), line, font=F_WIRE, fill=INK)
        x += col_w + 10
    d.line([16, y1 + 4, W - 16, y1 + 4], fill=LINE, width=1)


def draw_numbers(d, numbers, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255), outline=LINE,
                width=1)
    cell_w = w / len(numbers)
    for i, (val, lab) in enumerate(numbers):
        cx = x + i * cell_w
        if i:
            d.line([cx, y + 8, cx, y + h - 8], fill=LINE, width=1)
        d.text((cx + 10, y + 4), val, font=F_NUM_V, fill=INK)
        for j, line in enumerate(wrap(d, lab, F_NUM_L, cell_w - 20)):
            d.text((cx + 10, y + 30 + j * 11), line, font=F_NUM_L,
                   fill=MUTED)


def draw_region_chips(d, data, y):
    """Baris chip jumlah cerita per region (ala #1), dihitung dari
    manifest — ASIA 10, EUROPE 10, AMERICAS 8, MIDDLE EAST 6,
    AFRICA 5, OCEANIA 2, GLOBAL 1 (total 42)."""
    from collections import Counter
    counts = Counter(s["region"] for s in data["stories"])
    counts[data["hero"]["region"]] += 1
    order = ["ASIA", "EUROPE", "AMERICAS", "MIDDLE EAST", "AFRICA",
             "OCEANIA", "GLOBAL"]
    chips = [(r, counts[r]) for r in order if counts[r]]
    widths = []
    total = 0
    for region, n in chips:
        tw = d.textlength(f"{region} {n}", font=F_CHIP) + 14
        widths.append(tw)
        total += tw
    total += 8 * (len(chips) - 1)
    x = (W - total) / 2
    for (region, n), tw in zip(chips, widths):
        d.rounded_rectangle([x, y, x + tw, y + 15], radius=7,
                            fill=REGION_COLORS[region])
        d.text((x + 7, y + 3), f"{region} {n}", font=F_CHIP,
               fill=(255, 255, 255))
        x += tw + 8


def draw_map_dark(d, box, pins):
    """Peta v4 ala #1: ocean navy gelap, benua tan, pin merah besar
    bernomor, label putih dalam pill navy (kontras di mana pun).
    Anchor HORMUZ dipindah ke bawah pin (di v3 labelnya bertabrakan
    dengan ODISHA); sisanya ikut anchor manifest."""
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(13, 30, 58))
    d.rectangle(box, outline=INK, width=1)
    mw, mh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360.0 * mw,
                y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * mh)

    for lon in range(-150, 181, 30):
        px = x0 + (lon + 180) / 360.0 * mw
        d.line([px, y0, px, y1], fill=(40, 60, 90), width=1)
    for lat in range(-60, 81, 30):
        py = y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * mh
        d.line([x0, py, x1, py], fill=(40, 60, 90), width=1)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly],
                  fill=(222, 205, 170), outline=(150, 130, 95))
    for name, lon, lat in OCEAN_LABELS:
        px, py = proj(lon, lat)
        d.text((px - 22, py - 5), name, font=F_MICRO_B,
               fill=(140, 165, 195))
    anchors = {"5": "b"}  # HORMUZ: label di bawah pin, bukan di atas
    for pin in pins:
        px, py = proj(pin["lon"], pin["lat"])
        col = REGION_COLORS[pin["region"]]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(192, 57, 43),
                  outline=(255, 255, 255), width=2)
        d.text((px - 3, py - 5), pin["n"], font=F_MICRO_B,
               fill=(255, 255, 255))
        lw = d.textlength(pin["label"], font=F_MICRO_B)
        anchor = anchors.get(pin["n"], pin.get("anchor", "r"))
        if anchor == "r":
            lx, ly = px + 12, py - 6
        elif anchor == "l":
            lx, ly = px - 12 - lw, py - 6
        elif anchor == "a":
            lx, ly = px - lw / 2, py - 22
        else:  # below
            lx, ly = px - lw / 2, py + 12
        lx = min(max(lx, x0 + 2), x1 - lw - 10)
        ly = min(max(ly, y0 + 2), y1 - 13)
        d.rounded_rectangle([lx - 4, ly - 2, lx + lw + 4, ly + 10],
                            radius=5, fill=(13, 30, 58),
                            outline=(120, 150, 190), width=1)
        d.text((lx, ly), pin["label"], font=F_MICRO_B, fill=(255, 255, 255))
    # legenda ala #1, pill kiri bawah di dalam peta
    leg = "1–3 LEAD  •  4–13 FEATURE"
    lw = d.textlength(leg, font=F_MICRO_B)
    d.rounded_rectangle([x0 + 8, y1 - 22, x0 + 16 + lw, y1 - 8], radius=6,
                        fill=(13, 30, 58), outline=(120, 150, 190), width=1)
    d.text((x0 + 12, y1 - 19), leg, font=F_MICRO_B, fill=(255, 255, 255))


def draw_also_list(d, stories, x0, y0, col_w, rows=9, row_h=13):
    for i, s in enumerate(stories):
        col, r = divmod(i, rows)
        x = x0 + col * (col_w + 10)
        yy = y0 + r * row_h
        c = REGION_COLORS[s["region"]]
        d.ellipse([x, yy + 1, x + 7, yy + 8], fill=c)
        d.text((x + 10, yy), s["num"], font=F_LIST_B, fill=c)
        d.text((x + 28, yy), s["headline"], font=F_LIST, fill=INK)


def draw_datecheck(d, y0):
    h = 48
    d.rectangle([16, y0, W - 16, y0 + h], fill=(255, 255, 255),
                outline=LINE, width=1)
    d.rectangle([16, y0, 108, y0 + 20], fill=RED)
    d.text((24, y0 + 5), "DATE CHECK", font=F_MICRO_B, fill=(255, 255, 255))
    d.text((116, y0 + 3),
           "Every story here was first reported on Friday 20 November 2026.",
           font=F_DC, fill=INK)
    d.text((116, y0 + 15),
           "Left out — they broke earlier: Shenzhen summit itself; Houthi strike on Riyadh's PIF tower;",
           font=F_DC2, fill=(60, 58, 52))
    d.text((116, y0 + 26),
           "Crimea Bridge attack; Anthropic IPO pricing, $81.34bn; ICJ Rohingya ruling; Van Gogh sale;",
           font=F_DC2, fill=(60, 58, 52))
    d.text((116, y0 + 37),
           "EU €45bn loan; US–Venezuela deal; Fiji drought; Han freed; Kyiv embassy strikes — 19 Nov (Fiji 18 Nov).",
           font=F_DC2, fill=(60, 58, 52))
    return h


def draw_footer(d, data, y0):
    d.line([16, y0, W - 16, y0], fill=LINE, width=1)
    d.text((16, y0 + 5), data["footer"], font=F_MICRO, fill=MUTED)
    right = "FRIDAY 20 NOVEMBER 2026  •  ONE DAY, ONE PICTURE"
    rw = d.textlength(right, font=F_MICRO_B)
    d.text((W - 16 - rw, y0 + 5), right, font=F_MICRO_B, fill=INK)


# ---------------------------------------------------------------- render
def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    by_num = validate(d, data)

    draw_masthead(d, data)
    # NB: v2 "First wires" strip dropped in v3 — the brief's winner
    # layout has no wires strip; the space buys airy lead/panel rows.
    # data["wires"] stays in the manifest as provenance only.
    draw_numbers(d, data["numbers"], 16, 120, W - 32, 52)
    draw_region_chips(d, data, 176)

    # 3 lead besar sebaris
    lead_y, lead_h = 194, 324
    lw = (W - 32 - 2 * 10) / 3
    for i, num in enumerate(LEAD_NUMS):
        x = 16 + i * (lw + 10)
        draw_lead(d, img, by_num[num], x, lead_y, lw, lead_h)

    # 12 panel berilustrasi, 2 baris x 6
    pw = (W - 32 - 5 * 8) / 6
    for row in range(2):
        y = 526 + row * 136
        for c in range(6):
            s = by_num[PANEL_NUMS[row * 6 + c]]
            x = 16 + c * (pw + 8)
            draw_panel(d, s, x, y, pw, 128)

    # peta + daftar bernomor sisa 27 cerita (3 kolom x 9)
    map_y = 798
    d.text((16, map_y), "WHERE IT HAPPENED — 20 NOV 2026", font=F_SEC,
           fill=INK)
    d.text((436, map_y), "ALSO ON FRIDAY 20 NOVEMBER", font=F_SEC, fill=RED)
    draw_map_dark(d, (16, map_y + 18, 420, 940), data["pins"])
    rest = [s for s in data["stories"]
            if s["num"] not in LEAD_NUMS and s["num"] not in PANEL_NUMS]
    draw_also_list(d, rest, 436, map_y + 20, 184)

    draw_datecheck(d, 946)
    draw_footer(d, data, 1000)
    img = add_grain(img)
    return img


def main():
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        data = json.load(f)
    img = render(data)
    img.save(os.path.join(HERE, "entry_v4.png"), format="PNG", optimize=True)
    print("wrote entry_v4.png", img.size,
          os.path.getsize(os.path.join(HERE, "entry_v4.png")), "bytes")


if __name__ == "__main__":
    main()
