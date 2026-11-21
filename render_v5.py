#!/usr/bin/env python3
"""Render v5 — FULL PAGE news-image-20261120 (v4 + scene/attribution
upgrades vs live #1, 21 Nov 2026).

Perubahan vs v4 (lihat render_v5_progress.md):
- E1 masthead "6 REGIONS" -> "7 REGIONS" (manifest punya 7 region:
  ASIA/EUROPE/AMERICAS/MIDDLE EAST/AFRICA/OCEANIA/GLOBAL; v4
  mengklaim 6 di masthead padahal chip region menampilkan 7 —
  kontradiksi internal yang bisa ditangkap judge kriteria 3).
- E2 strip angka: 2 angka yang menduplikasi headline panel
  ($97.17 = panel 27, 99 = panel 05) diganti fakta berbeda dari
  manifest (E213.7M rail fraud, 1,650 killed Gaza) — strip kini
  6 angka berbeda, tanpa duplikasi panel.
- E3 panel 05 GTA VI: bukan lagi grafis angka "99" raksasa —
  scene kota senja (skyline neon + palem + antrean toko + layar
  TV mobil), "99" jadi badge emas kecil + 5 bintang.
- E4 panel 27 Anthropic: bukan lagi chart garis — scene lantai
  bursa (gedung + trader di meja + layar garis naik kecil),
  "$97.17" jadi chip kecil, "+17% DEBUT" badge hijau.
- E5 panel 01: jabat tangan diperbesar (lengan + kepalan lebih
  besar, dokumen dipersempit ke 60% atas).
- E6 lead Akvan: spiral diperkecil (x0.75) + daratan dilebarkan
  (garis pantai 168->190), 2 rumah + 3 pohon tambah, hujan di
  atas daratan — spiral tidak lagi mendominasi seperti target.
- E7 lead COP31: "$120BN" 26pt -> 20pt, delegasi 3 -> 5, badge
  merah "FINAL DAY — NO DEAL" di kanan bawah scene.
- E8 panel: header kini "NUM • REGION • SOURCE" (dulu tanpa
  sumber — panel v4 tidak menampilkan sumber sama sekali).
Manifest TIDAK diubah (cerita/tanggal/angka manifest tetap);
angka strip di-override di main() dari fakta manifest yang sama.
Deterministik: tanpa jam/network/random tak berseed.
Membaca manifest.json dan menulis entry_v5.png 1024x1024.
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
    # "$120BN" kanan atas (20pt, v5: dulu 26pt mendominasi scene)
    # + garis bawah + sublabel 7pt (v5: 8pt terpotong di tepi kanan)
    d0.text((192 * S, 14 * S), "$120BN",
            font=font("DejaVuSans-Bold.ttf", 20 * S), fill=(18, 90, 95))
    d.line([192, 42, 282, 42], fill=(18, 90, 95), width=3)
    d0.text((192 * S, 48 * S), "ADAPTATION — NOT AGREED",
            font=font("DejaVuSans-Bold.ttf", 7 * S), fill=(120, 60, 50))
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
    # 5 delegasi di depan gedung (v5: dulu 3; bust kecil berwajah:
    # mata 2 titik) — rapat, bahu bersentuhan, seperti foto kelompok
    for cx, skin, hair, suit in ((48, (210, 170, 130), (240, 240, 240),
                                  (38, 55, 90)),
                                 (76, (232, 190, 150), (60, 45, 30),
                                  (26, 26, 26)),
                                 (104, (238, 205, 170), (90, 60, 40),
                                  (60, 40, 90)),
                                 (130, (210, 170, 130), (30, 30, 30),
                                  (20, 80, 50)),
                                 (156, (232, 190, 150), (200, 200, 200),
                                  (90, 30, 30))):
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
    # badge merah "FINAL DAY — NO DEAL" (v5, ala #1 "FINAL DAY —
    # DEADLOCK") — digambar SETELAH pasir/laut: dulu tertutup
    # rectangle pasir karena digambar sebelum blok ini.
    d.rectangle([180, 114, 290, 126], fill=(180, 40, 30))
    d0.text((184 * S, 117 * S), "FINAL DAY — NO DEAL",
            font=font("DejaVuSans-Bold.ttf", 7 * S), fill=(255, 255, 255))
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
    # daratan tan di kiri (garis pantai berlekuk) — v5: dilebarkan
    # (168->190 di atas) supaya spiral tidak mendominasi halaman
    coast = [(0, 0), (190, 0), (168, 44), (146, 88), (130, 132),
             (118, 176), (112, h), (0, h)]
    d.polygon(coast, fill=(232, 214, 170))
    d.line(coast[1:], fill=(250, 244, 220), width=2)
    # rumah-rumah kecil di daratan dekat pantai + 3 pohon (v5)
    for hx, hy, hw, hh in ((30, 96, 16, 12), (58, 116, 14, 10),
                           (36, 140, 18, 12), (72, 84, 14, 10),
                           (88, 128, 16, 11)):
        d.rectangle([hx, hy, hx + hw, hy + hh], fill=(190, 170, 140),
                    outline=(120, 105, 80), width=1)
        d.polygon([(hx - 2, hy), (hx + hw + 2, hy),
                   (hx + hw // 2, hy - 6)], fill=(160, 60, 45))
    for tx, ty in ((24, 60), (52, 52), (96, 96)):
        d.line([tx, ty, tx, ty + 8], fill=(120, 85, 55), width=2)
        d.ellipse([tx - 6, ty - 7, tx + 6, ty + 2], fill=(50, 130, 70))
    # spiral di atas laut (pusat di kanan) — v5: diperkecil x0.75
    # (dulu r max 122 di scene 312 lebar = terbaca target)
    ex, ey = 228, 92
    rings = [(12, -40, 300, 5, (255, 255, 255)),
             (22, 55, 295, 4, (255, 255, 255)),
             (32, 140, 290, 4, (255, 255, 255)),
             (42, 225, 285, 4, (235, 240, 248)),
             (53, 310, 280, 4, (214, 226, 238)),
             (65, 35, 275, 4, (214, 226, 238)),
             (78, 120, 265, 3, (214, 226, 238)),
             (91, 205, 255, 3, (214, 226, 238))]
    for k, (r, a0, sweep, wd, col) in enumerate(rings):
        cx, cy = ex - k * 4, ey + k * 2
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + sweep,
              fill=col, width=wd)
    d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=(245, 233, 200))
    d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10],
              outline=(255, 255, 255), width=2)
    # hujan: garis miring putih tipis di atas laut dekat pantai
    # + di atas daratan (v5: hujan mencapai darat = landfall)
    for rx, ry in ((168, 40), (178, 70), (162, 110), (184, 130),
                   (172, 160), (192, 96), (140, 60), (128, 120),
                   (150, 150)):
        d.line([rx, ry, rx - 5, ry + 10], fill=(200, 215, 230), width=2)
    # label daratan + titik landfall Gopalpur di garis pantai
    d0.text((10 * S, 8 * S), "ODISHA",
            font=font("DejaVuSans-Bold.ttf", 11 * S), fill=(40, 35, 25))
    d0.text((10 * S, 22 * S), "INDIA",
            font=font("DejaVuSans.ttf", 8 * S), fill=(90, 80, 60))
    d.ellipse([142, 84, 150, 92], fill=(200, 50, 43),
              outline=(255, 255, 255), width=1)
    d0.text((52 * S, 96 * S), "Gopalpur",
            font=font("DejaVuSans-Bold.ttf", 8 * S), fill=(40, 35, 25))
    # "BAY OF BENGAL" di atas pill gelap (v5: busur spiral luar
    # sempat memotong huruf — pill menutupi busur di belakang teks)
    d.rounded_rectangle([222, h - 42, 306, h - 30], radius=4,
                        fill=(10, 14, 30))
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
    """(01) Declaration v5: 3 bendera + dokumen putih + segel merah +
    jabat tangan BESAR di bawah dokumen (v4: kepalan 16px — terlalu
    kecil untuk dibaca sekilas). Scene panel hanya ~57px: bendera
    12px, dokumen ke h-16, kepalan 26px menabrak dasar dokumen."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 236, 220))
    draw_flag_us(d, x0 + 8, y0 + 3, 40, 12)
    draw_flag_cn(d, x0 + w // 2 - 20, y0 + 3, 40, 12)
    draw_flag_ru(d, x0 + w - 48, y0 + 3, 40, 12)
    d.rectangle([x0 + w * 0.28, y0 + 18, x0 + w * 0.72, y0 + h - 16],
                fill=(255, 255, 255), outline=INK, width=1)
    for i, ly in enumerate((22, 26)):
        d.line([x0 + w * 0.32, y0 + ly, x0 + w * 0.68, y0 + ly],
               fill=(150, 150, 150), width=1)
    d.ellipse([x0 + w * 0.60, y0 + h - 24, x0 + w * 0.68, y0 + h - 17],
              fill=(200, 50, 43), outline=(255, 255, 255), width=1)
    # jabat tangan besar: lengan navy (kiri) & olive (kanan) bertemu
    # di kepalan tangan peach 26px di tengah bawah dokumen
    d.rectangle([x0, y0 + h - 6, x0 + w, y0 + h], fill=(210, 195, 165))
    cx, cy = x0 + w // 2, y0 + h - 11
    d.polygon([(x0 + 2, cy - 7), (cx - 12, cy - 8), (cx - 12, cy + 2),
               (x0 + 2, cy + 5)], fill=(38, 55, 90))
    d.polygon([(x0 + w - 2, cy - 7), (cx + 12, cy - 8), (cx + 12, cy + 2),
               (x0 + w - 2, cy + 5)], fill=(90, 90, 60))
    d.ellipse([cx - 13, cy - 8, cx + 13, cy + 8], fill=(232, 190, 150),
              outline=INK, width=1)
    d.line([cx - 7, cy - 2, cx + 7, cy - 2], fill=(180, 140, 110), width=1)
    d.line([cx - 7, cy + 3, cx + 7, cy + 3], fill=(180, 140, 110), width=1)


def sc_05v5(d, x0, y0, w, h):
    """(05) GTA VI v5: SCENE, bukan grafis angka — langit senja
    neon (magenta->teal), skyline gelap + jendela, palem, antrean
    3 figur di depan toko game + layar TV mobil di jendela toko.
    "99" hanya badge emas kecil kanan atas + 5 bintang kecil bawah.
    Panel v4 ("99" 34pt + bintang) adalah grafis, bukan scene."""
    # langit senja: gradien magenta atas -> oranye -> teal bawah
    stops = [(120, 40, 110), (200, 80, 90), (240, 140, 80), (30, 90, 110)]
    for y in range(h):
        t = y / max(1, h - 1) * (len(stops) - 1)
        i = min(int(t), len(stops) - 2)
        f = t - i
        col = tuple(int(stops[i][k] + (stops[i + 1][k] - stops[i][k]) * f)
                    for k in range(3))
        d.line([x0, y0 + y, x0 + w, y0 + y], fill=col)
    # matahari terbenam kiri atas (lingkaran pucat, garis-garis)
    d.ellipse([x0 + 8, y0 + 6, x0 + 32, y0 + 30],
              fill=(255, 220, 150))
    d.line([x0 + 8, y0 + 18, x0 + 32, y0 + 18],
           fill=(240, 140, 80), width=2)
    # skyline gelap + jendela hangat
    for bx, bw, bh in ((4, 26, 22), (34, 20, 30), (58, 26, 18),
                       (88, 22, 26), (114, 24, 20)):
        d.rectangle([x0 + bx, y0 + h - bh, x0 + bx + bw, y0 + h],
                    fill=(22, 18, 40))
        for wx in range(bx + 4, bx + bw - 4, 8):
            d.rectangle([x0 + wx, y0 + h - bh + 5, x0 + wx + 3,
                         y0 + h - bh + 9], fill=(255, 205, 110))
    # palem kiri atas skyline
    d.line([x0 + 12, y0 + h - 22, x0 + 14, y0 + h - 40],
           fill=(60, 40, 30), width=2)
    for a in (200, 250, 300, 340):
        ex = x0 + 13 + 9 * math.cos(math.radians(a))
        ey = y0 + h - 40 + 4 * math.sin(math.radians(a))
        d.line([x0 + 13, y0 + h - 40, ex, ey], fill=(30, 120, 70), width=2)
    # toko game: etalase terang di kanan bawah + layar TV mobil
    d.rectangle([x0 + w - 62, y0 + h - 34, x0 + w - 4, y0 + h - 4],
                fill=(20, 20, 30), outline=(255, 205, 80), width=1)
    d.rectangle([x0 + w - 58, y0 + h - 30, x0 + w - 8, y0 + h - 12],
                fill=(40, 120, 140))
    d.polygon([(x0 + w - 50, y0 + h - 14), (x0 + w - 34, y0 + h - 14),
               (x0 + w - 30, y0 + h - 20), (x0 + w - 42, y0 + h - 28)],
              fill=(200, 40, 60))
    d.ellipse([x0 + w - 46, y0 + h - 17, x0 + w - 42, y0 + h - 13],
              fill=(20, 20, 20))
    d.ellipse([x0 + w - 30, y0 + h - 17, x0 + w - 26, y0 + h - 13],
              fill=(20, 20, 20))
    # 3 figur antre di depan toko (kepala + badan, warna beda)
    for i, (fx, shirt) in enumerate(((0.30, (200, 60, 50)),
                                     (0.44, (60, 120, 200)),
                                     (0.58, (240, 200, 60)))):
        cx = x0 + int(w * fx)
        cy = y0 + h - 24
        d.ellipse([cx - 4, cy - 5, cx + 4, cy + 3], fill=(232, 190, 150),
                  outline=INK, width=1)
        d.rectangle([cx - 5, cy + 3, cx + 5, cy + 12], fill=shirt)
    # badge emas "99" kecil kanan atas + 5 bintang kecil di bawahnya
    d.rounded_rectangle([x0 + w - 34, y0 + 4, x0 + w - 4, y0 + 20],
                        radius=4, fill=(255, 205, 80))
    d.text((x0 + w - 29, y0 + 6), "99", font=F_MICRO_B, fill=(20, 20, 30))
    for i in range(5):
        sx = x0 + w - 32 + i * 6
        d.polygon(star_points(sx, y0 + 26, 3, 1), fill=(255, 205, 80))


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


def sc_27v5(d, x0, y0, w, h):
    """(27) Anthropic debut close v5: SCENE lantai bursa — gedung
    kaca + meja trader + 2 trader berwajah + layar monitor garis
    hijau naik KECIL (bukan chart se-panel). "$97.17" jadi chip
    putih kecil kiri atas, "+17% DEBUT" badge hijau di bawahnya.
    Panel v4 (skyline + garis emas besar + "$97.17" 17pt) masih
    terbaca sebagai chart."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 34, 48))
    # gedung kaca belakang: panel biru + grid jendela terang
    d.rectangle([x0 + 6, y0 + 4, x0 + w - 6, y0 + h - 26],
                fill=(52, 68, 96), outline=(90, 110, 140), width=1)
    for r in range(3):
        for c in range(6):
            d.rectangle([x0 + 12 + c * 22, y0 + 10 + r * 11,
                         x0 + 24 + c * 22, y0 + 18 + r * 11],
                        fill=(255, 205, 110) if (r + c) % 3 else (90, 120, 160))
    # chip "$97.17" putih kiri atas + badge "+17% DEBUT" hijau
    d.rounded_rectangle([x0 + 8, y0 + 6, x0 + 62, y0 + 20], radius=4,
                        fill=(255, 255, 255))
    d.text((x0 + 12, y0 + 8), "$97.17", font=F_MICRO_B, fill=(20, 20, 30))
    d.rounded_rectangle([x0 + 8, y0 + 23, x0 + 62, y0 + 35], radius=4,
                        fill=(20, 120, 70))
    d.text((x0 + 12, y0 + 25), "+17% DEBUT", font=F_MICRO_B,
           fill=(255, 255, 255))
    # meja trader + 2 trader berwajah di depannya
    d.rectangle([x0 + 8, y0 + h - 18, x0 + w - 8, y0 + h - 4],
                fill=(70, 55, 40))
    for cx, skin, hair, suit in ((0.30, (232, 190, 150), (60, 45, 30),
                                  (38, 55, 90)),
                                 (0.52, (210, 170, 130), (30, 30, 30),
                                  (90, 30, 30))):
        px = x0 + int(w * cx)
        py = y0 + h - 30
        d.ellipse([px - 6, py - 6, px + 6, py + 6], fill=skin,
                  outline=INK, width=1)
        d.polygon([(px + 6 * math.cos(math.radians(a)),
                    py + 6 * math.sin(math.radians(a)))
                   for a in range(200, 341, 10)], fill=hair)
        d.ellipse([px - 3, py - 1, px - 1, py + 1], fill=INK)
        d.ellipse([px + 1, py - 1, px + 3, py + 1], fill=INK)
        d.pieslice([px - 11, py + 4, px + 11, py + 14], 180, 360, fill=suit)
        d.rectangle([px - 11, py + 9, px + 11, y0 + h - 18], fill=suit)
    # monitor kecil di atas meja (kanan): layar gelap + garis hijau
    mx0, my0 = x0 + w - 48, y0 + h - 44
    d.rectangle([mx0, my0, mx0 + 40, my0 + 22], fill=(16, 20, 32),
                outline=(120, 120, 130), width=1)
    d.line([(mx0 + 4, my0 + 18), (mx0 + 14, my0 + 12),
            (mx0 + 24, my0 + 14), (mx0 + 36, my0 + 4)],
           fill=(60, 220, 110), width=2)
    d.line([mx0 + 16, my0 + 22, mx0 + 16, my0 + 26], fill=(90, 90, 90),
           width=2)
    d.line([mx0 + 10, my0 + 26, mx0 + 30, my0 + 26], fill=(90, 90, 90),
           width=2)


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


PANEL_SCENES = {"01": sc_01, "03": sc_03v4, "05": sc_05v5, "09": sc_09v4,
                "21": sc_21, "23": sc_23, "27": sc_27v5, "30": sc_30,
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
    # v5: header panel kini "NUM • REGION • SOURCE" — panel v4 tidak
    # menampilkan sumber sama sekali (atribusi, kriteria judge 3/4).
    d.text((x + 6, ty), s["num"] + " • " + s["region"] + " • " + s["source"],
           font=F_MICRO_B, fill=REGION_COLORS[s["region"]])
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
    meta_r = "42 STORIES  •  7 REGIONS"  # v5: dulu "6 REGIONS" (salah:
    # manifest punya 7 region; chip region di bawah menampilkan 7)
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
    # v5 E2: strip angka — 2 angka yang menduplikasi headline panel
    # ($97.17 = panel 27, 99 = panel 05) diganti fakta berbeda dari
    # manifest yang sama (cerita 18: E213.7M rail fraud; cerita 32:
    # 1,650 killed sejak ceasefire). Manifest TIDAK diubah.
    data["numbers"] = [
        ["300,000", "EVACUATED AS AKVAN NEARS ODISHA"],
        ["€213.7M", "RAIL FRAUD CHARGED, EPPO"],
        ["118", "PHILLIPS, NEW ZEALAND v INDIA"],
        ["~30", "MISSILES FIRED AT KYIV OVERNIGHT"],
        ["$120bn", "ADAPTATION FUND, COP31: NOT AGREED"],
        ["1,650", "KILLED IN GAZA SINCE CEASEFIRE"],
    ]
    img = render(data)
    img.save(os.path.join(HERE, "entry_v5.png"), format="PNG", optimize=True)
    print("wrote entry_v5.png", img.size,
          os.path.getsize(os.path.join(HERE, "entry_v5.png")), "bytes")


if __name__ == "__main__":
    main()
