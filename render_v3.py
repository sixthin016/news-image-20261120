#!/usr/bin/env python3
"""Render v3 — FULL PAGE news-image-20261120 (winner-style rebuild).

Layout mengikuti pola pemenang #1: masthead raksasa tanggal
"Friday 20 November 2026", strip 6 angka besar, 3 lead BESAR
berilustrasi penuh (Akvan / Kyiv / COP31), 12 panel medium
berilustrasi, peta + daftar bernomor "ALSO ON FRIDAY 20 NOVEMBER",
kotak DATE CHECK lebar penuh, footer sumber.

Perubahan vs v2 (entry.png):
- Masthead: judul besar = tanggal (bukan "THE WORLD IN ONE PAGE").
- Lead: 3 (bukan 4) — Shenzhen/KAFD/Crimea keluar; Akvan memakai
  panel gate_v3_akvan.py yang sudah disetujui (dirender native
  330x200 lalu di-resize ke slot, komposisi tidak diubah); Kyiv =
  jejak rudal di atas skyline malam; COP31 = Antalya.
- Angka: 6 angka besar dari gambar pemenang (300.000 / $97.17 /
  118 / ~30 / $120bn / 99), nilai BESAR di atas, label di bawah.
- NOL "..." di mana pun: headline/deck dipendekkan di manifest
  sampai muat penuh; validate() menolak bila wrap melebihi jatah
  baris (bukan memotong dengan elipsis seperti trunc1 v2).
- Set cerita dikoreksi ke peristiwa yang pertama dilaporkan Jumat
  20 Nov (lihat manifest.json + render_v3_progress.md); 10 item
  19 Nov pindah ke kotak DATE CHECK sebagai yang dikecualikan.

Membaca manifest.json dan menulis entry_v3.png 1024x1024.
Deterministik: tanpa jam/network; random hanya random.Random
berseed (bintang Kyiv + grain). Run: python3 render_v3.py
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
    font, sc_03, sc_09, sc_30, sc_31, sc_37, star_points, wrap,
)
from gate_v3_akvan import draw_akvan_gate  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

RED = (192, 57, 43)
GOLD = (255, 214, 90)
DARK = (26, 26, 26)
NAVY = (27, 42, 74)

F_DATE = font("DejaVuSerif-Bold.ttf", 58)
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
    return _finish(img, w, h, "KYIV — OVERNIGHT")


def draw_cop31_scene(w, h):
    """(14) COP31 Antalya — langit krem, matahari emas, laut teal,
    gedung konferensi putih + deret bendera, palem, "$120BN" besar.
    Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S), (250, 240, 220))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # matahari emas kiri atas + awan tipis
    d.ellipse([18, 10, 52, 44], fill=(235, 175, 60))
    d.ellipse([70, 22, 110, 30], fill=(255, 255, 255))
    d.ellipse([210, 14, 260, 22], fill=(255, 255, 255))
    # "$120BN" besar kanan atas (angka kunci lead) + garis bawah.
    # x=176, 30pt: lebar ~120px -> berakhir ~296 < 324 (v1: 34pt di
    # x=196 terpotong di tepi kanan).
    d0.text((176 * S, 16 * S), "$120BN",
            font=font("DejaVuSans-Bold.ttf", 30 * S), fill=(18, 90, 95))
    d.line([176, 54, 296, 54], fill=(18, 90, 95), width=3)
    d0.text((172 * S, 60 * S), "ADAPTATION — NOT AGREED",
            font=font("DejaVuSans-Bold.ttf", 9 * S), fill=(120, 60, 50))
    # laut teal + ombak putih
    d.rectangle([0, 128, w, h], fill=(64, 138, 148))
    for wy in (140, 156, 172):
        for i in range(5):
            ax = 6 + i * w // 5
            d.arc([ax, wy - 5, ax + w // 5 - 4, wy + 6], 180, 360,
                  fill=(230, 245, 245), width=2)
    # pantai pasir
    d.rectangle([0, 112, w, 128], fill=(232, 214, 170))
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
    # 2 palem kanan
    for px in (232, 286):
        d.line([px, 112, px + 4, 76], fill=(120, 85, 55), width=3)
        for a in (200, 240, 290, 330):
            ex = px + 2 + 16 * math.cos(math.radians(a))
            ey = 76 + 8 * math.sin(math.radians(a))
            d.line([px + 2, 76, ex, ey], fill=(50, 130, 70), width=3)
    return _finish(img, w, h, "ANTALYA — COP31")


# ---------------------------------------------------------------- panel scenes
def sc_01(d, x0, y0, w, h):
    """(01) Declaration: 3 bendera + dokumen putih + segel merah."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 236, 220))
    draw_flag_us(d, x0 + 8, y0 + 5, 40, 19)
    draw_flag_cn(d, x0 + w // 2 - 20, y0 + 5, 40, 19)
    draw_flag_ru(d, x0 + w - 48, y0 + 5, 40, 19)
    d.rectangle([x0 + w * 0.28, y0 + 28, x0 + w * 0.72, y0 + h - 4],
                fill=(255, 255, 255), outline=INK, width=1)
    for i, ly in enumerate((34, 39, 44)):
        d.line([x0 + w * 0.32, y0 + ly, x0 + w * 0.68, y0 + ly],
               fill=(150, 150, 150), width=1)
    d.ellipse([x0 + w * 0.60, y0 + h - 14, x0 + w * 0.68, y0 + h - 6],
              fill=(200, 50, 43), outline=(255, 255, 255), width=1)


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
    """(23) US stocks slide: batang merah turun + panah bawah."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(240, 228, 226))
    base = y0 + h - 8
    for i, bh in enumerate((30, 24, 18)):
        bx = x0 + 14 + i * 18
        d.rectangle([bx, base - bh, bx + 12, base], fill=(192, 57, 43))
    d.line([(x0 + 12, base - 28), (x0 + 32, base - 22), (x0 + 52, base - 16),
            (x0 + 78, base - 6)], fill=(160, 30, 25), width=5)
    d.polygon([(x0 + 78, base - 2), (x0 + 88, base - 6), (x0 + 76, base - 14)],
              fill=(160, 30, 25))
    d.text((x0 + w - 46, y0 + 6), "-2%", font=font("DejaVuSans-Bold.ttf", 13),
           fill=(160, 30, 25))


def sc_27b(d, x0, y0, w, h):
    """(27) Anthropic debut close: chip emas + $97.17 di latar gelap."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 34, 48))
    cx, cy = x0 + 28, y0 + h // 2
    d.rectangle([cx - 12, cy - 12, cx + 12, cy + 12], outline=GOLD, width=3)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
    for i in range(3):
        d.line([cx - 7 + i * 7, cy - 17, cx - 7 + i * 7, cy - 12],
               fill=GOLD, width=2)
        d.line([cx - 7 + i * 7, cy + 12, cx - 7 + i * 7, cy + 17],
               fill=GOLD, width=2)
    d.text((x0 + 50, y0 + 12), "$97.17", font=font("DejaVuSans-Bold.ttf", 17),
           fill=(255, 255, 255))
    d.text((x0 + 50, y0 + 34), "+17% DEBUT", font=F_MICRO_B, fill=GOLD)


def _cricket(d, x0, y0, w, h, runs, accent):
    """Batsman + pitch + stumps + bola; `runs` = skor besar di pojok."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 225, 190))
    d.rectangle([x0 + w * 0.30, y0 + 6, x0 + w * 0.70, y0 + h - 4],
                fill=(232, 214, 170))
    sx = x0 + w * 0.66
    for i in range(3):
        d.line([sx - 4 + i * 4, y0 + 10, sx - 4 + i * 4, y0 + 22],
               fill=(200, 170, 60), width=2)
    bx, by = x0 + w * 0.42, y0 + 24
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(232, 190, 150),
              outline=INK, width=1)
    d.line([bx, by + 6, bx + 2, by + 18], fill=(255, 255, 255), width=5)
    d.line([bx + 2, by + 18, bx - 2, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 2, by + 18, bx + 8, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 4, by + 10, bx + 16, by + 26], fill=(180, 140, 80), width=4)
    d.ellipse([x0 + w * 0.80 - 4, y0 + h - 14, x0 + w * 0.80 + 4, y0 + h - 6],
              fill=(200, 40, 40))
    d.text((x0 + 6, y0 + 4), runs, font=font("DejaVuSans-Bold.ttf", 10),
           fill=accent)


def sc_41(d, x0, y0, w, h):
    _cricket(d, x0, y0, w, h, "175*", (20, 80, 40))


def sc_42(d, x0, y0, w, h):
    _cricket(d, x0, y0, w, h, "118", (20, 60, 120))


PANEL_SCENES = {"01": sc_01, "03": sc_03, "05": sc_05, "09": sc_09,
                "21": sc_21, "23": sc_23, "27": sc_27b, "30": sc_30,
                "31": sc_31, "37": sc_37, "41": sc_41, "42": sc_42}


def lead_scene(num, w, h):
    if num == "02":
        # gate yang sudah disetujui, komposisi tidak diubah: render
        # native 330x200 lalu resize ke slot (selisih aspek ~3%)
        return draw_akvan_gate(330, 200).resize((w, h), Image.LANCZOS)
    if num == "15":
        return draw_kyiv_scene(w, h)
    return draw_cop31_scene(w, h)


# ---------------------------------------------------------------- cards
def draw_lead(d, img, s, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLORS[s["region"]])
    scene_h = 190
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
    d.text((16, 16), data["title"], font=F_DATE, fill=INK)
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
        d.text((cx + 10, y + 6), val, font=F_NUM_V, fill=INK)
        for j, line in enumerate(wrap(d, lab, F_NUM_L, cell_w - 20)):
            d.text((cx + 10, y + 34 + j * 11), line, font=F_NUM_L,
                   fill=MUTED)


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
    draw_numbers(d, data["numbers"], 16, 120, W - 32, 60)

    # 3 lead besar sebaris
    lead_y, lead_h = 188, 330
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
    draw_map(d, (16, map_y + 18, 420, 940), data["pins"])
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
    img.save(os.path.join(HERE, "entry_v3.png"), format="PNG", optimize=True)
    print("wrote entry_v3.png", img.size,
          os.path.getsize(os.path.join(HERE, "entry_v3.png")), "bytes")


if __name__ == "__main__":
    main()
