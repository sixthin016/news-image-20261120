#!/usr/bin/env python3
"""Render v2 — FASE 2: full-page build news-image-20261120.

Layout gaya pemenang #1 (r1.webp): masthead krem + judul serif, strip
timeline "First wires", 4 lead besar berilustrasi sebaris, 12 panel
berilustrasi (2 baris x 6, strip gambar di atas), peta full-width + daftar
bernomor sisa 26 cerita, strip "By the numbers", kotak DATE CHECK +
daftar eksklusi, footer sources.

Lead 01 (Shenzhen) memakai ulang motif gate_panel.py v5 — figur trio,
hair cap chord, bendera di belakang kepala, badan berpijak — tapi sebagai
fungsi berparameter ukuran (draw_shenzhen_scene / draw_figure_param)
karena band lead di sini 242x129, bukan 1024x155.

Membaca manifest.json (JANGAN diubah) dan menulis entry.png 1024x1024.
Deterministik: tanpa jam/random/network. Run: python3 render_v2.py
"""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import (  # noqa: E402
    CARD, INK, LINE, MUTED, PAPER, REGION_COLORS,
    draw_flag_cn, draw_flag_ru, draw_flag_us, draw_map,
    font, star_points, wrap,
)
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

RED = (192, 57, 43)
GOLD = (255, 214, 90)
DARK = (26, 26, 26)
SKY = (207, 224, 236)
SEA = (150, 190, 210)

F_TITLE = font("DejaVuSerif-Bold.ttf", 44)
F_KICK = font("DejaVuSans-Bold.ttf", 11)
F_DATE = font("DejaVuSans-Bold.ttf", 15)
F_META = font("DejaVuSans.ttf", 11)
F_WIRE_T = font("DejaVuSans-Bold.ttf", 10)
F_WIRE = font("DejaVuSans.ttf", 9)
F_LEAD_H = font("DejaVuSans-Bold.ttf", 15)
F_LEAD_D = font("DejaVuSans.ttf", 11)
F_LEAD_K = font("DejaVuSans-Bold.ttf", 9)
F_PAN_H = font("DejaVuSans-Bold.ttf", 11)
F_PAN_D = font("DejaVuSans.ttf", 9)
F_MICRO = font("DejaVuSans.ttf", 8)
F_MICRO_B = font("DejaVuSans-Bold.ttf", 8)
F_SEC = font("DejaVuSans-Bold.ttf", 12)
F_NUM_L = font("DejaVuSans.ttf", 8)
F_NUM_V = font("DejaVuSans-Bold.ttf", 13)
F_LIST = font("DejaVuSans.ttf", 9)
F_LIST_B = font("DejaVuSans-Bold.ttf", 9)
F_TAG = font("DejaVuSans-Bold.ttf", 8)


# ---------------------------------------------------------------- figures
def draw_figure_param(d, cx, head_y, head_r, half_sh, body_y1,
                      skin, hair, suit, tie):
    """Satu figur setengah badan, gaya gate_panel v5, ukuran parameter.

    head_r = radius kepala, half_sh = setengah lebar bahu,
    body_y1 = tepi bawah badan (berpijak). Hair cap = chord cap dangkal
    (arc 200..340 + garis hairline), bukan pieslice (apex di dahi)."""
    shoulder_y = head_y + head_r + max(3, head_r // 8)
    d.pieslice([cx - half_sh, shoulder_y - half_sh // 3,
                cx + half_sh, shoulder_y + half_sh // 3],
               180, 360, fill=suit)
    d.rectangle([cx - half_sh, shoulder_y, cx + half_sh, body_y1], fill=suit)
    sw = max(5, head_r // 3)
    d.polygon([(cx - sw, shoulder_y + 1), (cx + sw, shoulder_y + 1),
               (cx, shoulder_y + sw + 6)], fill=(255, 255, 255))
    d.polygon([(cx - 3, shoulder_y + 2), (cx + 3, shoulder_y + 2),
               (cx + 4, shoulder_y + sw + 8), (cx, shoulder_y + sw + 12),
               (cx - 4, shoulder_y + sw + 8)], fill=tie)
    d.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
              fill=skin, outline=INK, width=1)
    pts = [(cx + head_r * math.cos(math.radians(a)),
            head_y + head_r * math.sin(math.radians(a)))
           for a in range(200, 341, 5)]
    d.polygon(pts, fill=hair, outline=INK)


class SS:
    """Proxy ImageDraw: koordinat lokal dikali S ke kanvas kerja 2x.
    Dipakai semua scene lead supaya garis hero 2-3x tetap tajam setelah
    downscale LANCZOS. Box 4-angka / list titik diskala; width diskala."""

    def __init__(self, draw, s=2):
        self.d = draw
        self.s = s

    def _box(self, box):
        s = self.s
        if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
            return [box[0] * s, box[1] * s, box[2] * s, box[3] * s]
        if box and isinstance(box[0], (int, float)):
            # flat point list [x0, y0, x1, y1, ...] (PIL line)
            return [v * s for v in box]
        return [(x * s, y * s) for x, y in box]

    def _kw(self, kw):
        kw = dict(kw)
        if "width" in kw and kw["width"]:
            kw["width"] = kw["width"] * self.s
        return kw

    def rectangle(self, box, **kw):
        self.d.rectangle(self._box(box), **self._kw(kw))

    def rounded_rectangle(self, box, **kw):
        kw = self._kw(kw)
        if "radius" in kw:
            kw["radius"] = kw["radius"] * self.s
        self.d.rounded_rectangle(self._box(box), **kw)

    def ellipse(self, box, **kw):
        self.d.ellipse(self._box(box), **self._kw(kw))

    def polygon(self, pts, **kw):
        self.d.polygon(self._box(pts), **self._kw(kw))

    def line(self, pts, **kw):
        self.d.line(self._box(pts), **self._kw(kw))

    def pieslice(self, box, a0, a1, **kw):
        self.d.pieslice(self._box(box), a0, a1, **self._kw(kw))

    def arc(self, box, a0, a1, **kw):
        self.d.arc(self._box(box), a0, a1, **self._kw(kw))


def _lead_finish(img, w, h, tag=None):
    """Downscale kanvas 2x -> ukuran final; tag lokasi digambar tajam
    di ukuran final (bukan di-downscale)."""
    final = img.convert("RGB").resize((w, h), Image.LANCZOS)
    if tag:
        d = ImageDraw.Draw(final)
        tw = d.textlength(tag, font=F_TAG) + 8
        d.rectangle([5, 5, 5 + tw, 18], fill=(255, 255, 255),
                    outline=INK, width=1)
        d.text((9, 7), tag, font=F_TAG, fill=INK)
    return final


def draw_shenzhen_scene(w, h):
    """(01) Shenzhen trilateral — adaptasi gate_panel_spec.py ke slot lead.
    Mengembalikan Image (w,h). Pita jendela + skyline Ping An (kanan),
    3 bendera di belakang bahu, trio miring beda (-5/-3,5/+4), meja navy
    + SATU dokumen + 3 tangan + 2 mic. Render 2x -> LANCZOS.
    Disederhanakan vs panel 1024: mullion 4, mic 2, lengan stub pendek."""
    S = 2
    NAVY = (27, 42, 74)
    NAVY_LT = (45, 62, 100)
    CREAM = (244, 233, 216)
    PALE = (239, 227, 204)
    REDS = (200, 50, 43)
    GOLD = (217, 164, 65)
    TEAL = (46, 110, 101)
    HEAD_R, HEAD_Y, HALF_SH, TABLE_Y0 = 16, 52, 38, 104
    CX = (48, 120, 192)
    img = Image.new("RGBA", (w * S, h * S), CREAM + (255,))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # pita jendela atas + skyline (Ping An kanan, off-center)
    d.rectangle([0, 0, w, 30], fill=PALE)
    d.polygon([(196, 30), (200, 8), (210, 8), (214, 30)], fill=TEAL)
    d.polygon([(203, 8), (205, 0), (207, 8)], fill=TEAL)
    for bx, bw, bh in ((8, 12, 12), (26, 10, 18), (222, 10, 14), (234, 8, 10)):
        d.rectangle([bx, 30 - bh, bx + bw, 30], fill=TEAL)
    for mx in (48, 96, 144, 192):
        d.line([mx, 0, mx, 30], fill=(220, 205, 175), width=2)
    d.line([0, 30, w, 30], fill=NAVY, width=2)
    # 3 bendera vertikal, digeser kiri dari tiap figur (canton terbaca)
    for cx, fl in zip(CX, (draw_flag_us, draw_flag_cn, draw_flag_ru)):
        fx = cx - 45
        fl(d0, fx * S, 6 * S, 38 * S, 40 * S)
        d0.rectangle([fx * S, 6 * S, (fx + 38) * S, 46 * S],
                     outline=(17, 17, 17), width=1 * S)
    # 3 figur, layer sendiri + rotasi beda (bukan klon); Xi terakhir = maju
    figs = [(CX[0], (232, 190, 150), (240, 205, 105), NAVY, REDS, -5.0),
            (CX[2], (228, 185, 145), (128, 122, 112), TEAL, NAVY, -3.5),
            (CX[1], (238, 205, 170), (30, 30, 30), (35, 35, 35), GOLD, 4.0)]
    for cx, skin, hair, suit, tie, ang in figs:
        layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        ld = SS(ImageDraw.Draw(layer))
        shoulder_y = HEAD_Y + HEAD_R + 3
        ld.pieslice([cx - HALF_SH, shoulder_y - 14,
                     cx + HALF_SH, shoulder_y + 14],
                    180, 360, fill=suit + (255,))
        ld.polygon([(cx - HALF_SH + 2, shoulder_y),
                    (cx - HALF_SH + 9, TABLE_Y0),
                    (cx + HALF_SH - 9, TABLE_Y0),
                    (cx + HALF_SH - 2, shoulder_y)], fill=suit + (255,))
        sw = HEAD_R // 3
        ld.polygon([(cx - sw, shoulder_y + 1), (cx + sw, shoulder_y + 1),
                    (cx, shoulder_y + sw + 3)], fill=(255, 255, 255, 255))
        ld.polygon([(cx - 2, shoulder_y + 1), (cx + 2, shoulder_y + 1),
                    (cx + 3, shoulder_y + sw + 5),
                    (cx, shoulder_y + sw + 8),
                    (cx - 3, shoulder_y + sw + 5)], fill=tie + (255,))
        ld.ellipse([cx - HEAD_R, HEAD_Y - HEAD_R,
                    cx + HEAD_R, HEAD_Y + HEAD_R],
                   fill=skin + (255,), outline=(17, 17, 17, 255), width=2)
        pts = [(cx + HEAD_R * math.cos(math.radians(a)),
                HEAD_Y + HEAD_R * math.sin(math.radians(a)))
               for a in range(200, 341, 5)]
        ld.polygon(pts, fill=hair + (255,), outline=(17, 17, 17, 255))
        rot = layer.rotate(ang, resample=Image.BICUBIC,
                           center=(cx * S, HEAD_Y * S))
        img.alpha_composite(rot)
    d = SS(ImageDraw.Draw(img))
    # meja navy + garis emas
    d.rounded_rectangle([6, TABLE_Y0, w - 6, h], radius=4, fill=NAVY)
    d.rounded_rectangle([6, TABLE_Y0, w - 6, TABLE_Y0 + 5], radius=4,
                        fill=NAVY_LT)
    d.line([6, TABLE_Y0, w - 6, TABLE_Y0], fill=GOLD, width=2)
    # SATU dokumen bersama di tengah meja + segel merah (kanan, off-center)
    d.rectangle([98, 114, 146, 136], fill=(255, 255, 255),
                outline=(17, 17, 17), width=2)
    for ly in (121, 126):
        d.line([104, ly, 132, ly], fill=(150, 150, 150), width=1)
    d.ellipse([137, 127, 145, 135], fill=REDS,
              outline=(255, 255, 255), width=1)
    # lengan stub PENDEK: muncul dari balik tepi meja, berakhir di tepi
    # dokumen (bukan garis panjang menyeberangi meja); tint jas terang
    # + outline krem tipis, supaya terbaca di atas meja navy
    sleeves = [((84, TABLE_Y0), (100, 116), (70, 95, 135)),
               ((122, TABLE_Y0), (122, 115), (95, 95, 95)),
               ((156, TABLE_Y0), (142, 116), (75, 145, 135))]
    hands = [(100, 118, (232, 190, 150)),
             (122, 117, (238, 205, 170)),
             (142, 118, (228, 185, 145))]
    for (x1, y1), (x2, y2), tint in sleeves:
        d.line([x1, y1, x2, y2], fill=CREAM, width=5)
        d.line([x1, y1, x2, y2], fill=tint, width=3)
    for hx, hy, skin in hands:
        d.ellipse([hx - 9, hy - 5, hx + 9, hy + 5], fill=skin,
                  outline=(17, 17, 17), width=1)
        for fx in (-3, 0, 3):
            d.line([hx + fx, hy - 3, hx + fx, hy + 3],
                   fill=(180, 140, 100), width=1)
    # 2 mic emas di atas meja, di depan torso
    for mx in (70, 170):
        d.line([mx, TABLE_Y0, mx, 94], fill=GOLD, width=2)
        d.ellipse([mx - 3, 90, mx + 3, 96], fill=(40, 40, 40),
                  outline=GOLD, width=1)
    return _lead_finish(img, w, h)


def draw_tag(d, x, y, text):
    """Label lokasi putih kecil di pojok kiri atas scene."""
    tw = d.textlength(text, font=F_TAG) + 8
    d.rectangle([x, y, x + tw, y + 13], fill=(255, 255, 255), outline=INK, width=1)
    d.text((x + 4, y + 2), text, font=F_TAG, fill=INK)


def draw_bridge_scene(w, h):
    """(14) Crimea bridge — spek Qwen-Max (b). Dek DIAGONAL, titik patah
    di golden section (x=0,618w), bola api 3 starburst, mobil kecil di
    tepi celah + potongan dek jatuh, palet senja #F2B880 -> #5A4A6A.
    Mengembalikan Image (w,h). Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # gradien senja vertikal (pita 2 px lokal)
    top, bot = (242, 184, 128), (90, 74, 106)
    for y in range(0, h, 2):
        t = y / max(1, h - 2)
        col = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
        d.rectangle([0, y, w, y + 2], fill=col)
    # laut gelap bawah + ombak
    d.rectangle([0, 106, w, h], fill=(62, 58, 84))
    for wy in (116, 128, 140):
        for i in range(5):
            ax = 8 + i * w // 5
            d.arc([ax, wy - 4, ax + w // 5 - 4, wy + 5], 180, 360,
                  fill=(200, 190, 210), width=2)
    # matahari senja rendah, kanan (off-center)
    d.ellipse([198, 10, 222, 34], fill=(255, 220, 170))
    # asap 3 lingkaran di atas titik patah (di belakang bola api)
    for sx, sy, sr in ((138, 44, 9), (150, 32, 11), (162, 22, 12)):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(120, 118, 125))
    # tiang penyangga (di belakang dek)
    for px, py0 in ((34, 62), (92, 69), (206, 86)):
        d.rectangle([px - 3, py0, px + 3, 106], fill=(70, 70, 78))
    # dek diagonal: kiri utuh sampai golden section, kanan sesudah celah
    d.line([0, 58, 148, 76], fill=(45, 45, 52), width=7)
    d.line([0, 58, 148, 76], fill=(120, 120, 130), width=2)
    d.line([170, 80, w, 92], fill=(45, 45, 52), width=7)
    d.line([170, 80, w, 92], fill=(120, 120, 130), width=2)
    # potongan dek jatuh, miring di bawah celah (di depan laut)
    d.polygon([(146, 92), (170, 98), (166, 106), (142, 100)],
              fill=(60, 60, 66), outline=(30, 30, 36))
    # mobil kecil di tepi celah, di atas dek kiri
    d.rectangle([124, 65, 140, 72], fill=(178, 34, 34))
    d.rectangle([129, 60, 136, 65], fill=(178, 34, 34))
    d.ellipse([125, 70, 131, 76], fill=(20, 20, 20))
    d.ellipse([133, 70, 139, 76], fill=(20, 20, 20))
    # bola api 3 starburst di titik patah (di depan dek + asap)
    ex, ey = 148, 70
    d0.polygon(star_points(ex * S, ey * S, 24 * S, 10 * S, 8),
               fill=(240, 120, 30))
    d0.polygon(star_points(ex * S, ey * S, 15 * S, 6 * S, 8),
               fill=(255, 200, 60))
    d0.polygon(star_points(ex * S, ey * S, 8 * S, 3 * S, 8),
               fill=(255, 240, 180))
    return _lead_finish(img, w, h, "KERCH STRAIT")


def draw_tower_scene(w, h):
    """(34) KAFD Riyadh — spek Qwen-Max (c). Menara = batang grafik NAIK
    + tick jendela, SATU batang merah TERTEKAN + panah bawah, asap
    3 lingkaran dari menara gelap, garis tren emas, palet pasir #F0DFC0.
    Mengembalikan Image (w,h). Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S), (240, 223, 192))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # tanah + garis dasar + tick sumbu
    d.rectangle([0, 128, w, h], fill=(214, 196, 164))
    d.line([0, 128, w, 128], fill=(120, 100, 70), width=2)
    for tx in range(6, w, 12):
        d.line([tx, 128, tx, 132], fill=(120, 100, 70), width=1)
    # batang grafik naik; idx 3 = merah tertekan, idx 5 = gelap berasap
    xs = [14, 45, 76, 107, 138, 169, 200]
    hs = [38, 52, 46, 30, 66, 84, 76]
    for i, (bx, bh) in enumerate(zip(xs, hs)):
        top = 128 - bh
        if i == 3:
            col, ow = (200, 50, 43), 2
        elif i == 5:
            col, ow = (58, 62, 72), 1
        else:
            col, ow = (122, 143, 168), 1
        d.rectangle([bx, top, bx + 22, 128], fill=col,
                    outline=(60, 60, 60), width=ow)
        # tick jendela putih di tiap batang
        for wy in (top + 8, top + 18):
            if wy < 122:
                d.line([bx + 4, wy, bx + 18, wy],
                       fill=(255, 255, 255), width=1)
    # garis tren emas melewati puncak batang (melompati batang merah)
    d.line([25, 90, 56, 76, 87, 82, 149, 62, 180, 44, 211, 52],
           fill=(217, 164, 65), width=3)
    # panah bawah merah di atas batang tertekan (ujung = puncak batang)
    d.line([118, 66, 118, 92], fill=(200, 50, 43), width=3)
    d.polygon([(118, 98), (110, 88), (126, 88)], fill=(200, 50, 43))
    # asap 3 lingkaran dari menara gelap
    for sx, sy, sr in ((180, 36, 7), (188, 26, 9), (196, 16, 10)):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                  fill=(120, 120, 125))
    return _lead_finish(img, w, h, "KAFD — RIYADH")


def draw_cyclone_scene(w, h):
    """(02) Cyclone Akvan — spek Qwen-Max (d). Spiral 4 busur TEBAL +
    mata putih (off-center), 3 cincin target (terluar PUTUS-PUTUS),
    cincin merah terdalam melingkungi blok kota, palet slate #22303C.
    Mengembalikan Image (w,h). Render 2x -> LANCZOS."""
    S = 2
    img = Image.new("RGB", (w * S, h * S), (34, 48, 60))
    d0 = ImageDraw.Draw(img)
    d = SS(d0)
    # laut bawah + ombak
    d.rectangle([0, 118, w, h], fill=(46, 66, 84))
    for wy in (126, 138):
        for i in range(5):
            ax = 8 + i * w // 5
            d.arc([ax, wy - 4, ax + w // 5 - 4, wy + 5], 180, 360,
                  fill=(140, 170, 200), width=2)
    cx, cy = 96, 66
    # hujan miring kiri-kanan
    for i in range(4):
        for sx in (6, 214):
            rx, ry = sx + i * 8, 12 + i * 11
            d.line([rx, ry, rx - 5, ry + 10], fill=(120, 160, 190), width=2)
    # blok kota kecil di dalam cincin merah (digambar dulu, cincin di depan)
    # isi TANAH TERANG supaya terbaca di atas slate gelap; semua sudut
    # di dalam lingkaran r=28 (pusat 96,66)
    for bx, by, bw, bh in ((86, 82, 8, 10), (95, 76, 8, 16), (104, 80, 6, 8)):
        d.rectangle([bx, by, bx + bw, by + bh], fill=(216, 200, 160))
        d.rectangle([bx + 2, by + 3, bx + 4, by + 6], fill=(34, 48, 60))
        d.rectangle([bx + 2, by + 8, bx + 4, by + 11], fill=(34, 48, 60))
    # spiral 4 busur tebal (hero, width 5 lokal)
    for k, r in enumerate((13, 24, 35, 46)):
        a0 = -40 + k * 80
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 240,
              fill=(165, 200, 220), width=5)
    # 3 cincin target: terluar putus-putus, tengah tipis, terdalam merah
    for a in range(0, 360, 24):
        d.arc([cx - 62, cy - 62, cx + 62, cy + 62], a, a + 14,
              fill=(140, 175, 205), width=2)
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52],
              outline=(127, 168, 200), width=2)
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28],
              outline=(212, 61, 42), width=4)
    # mata putih (fokus, paling depan)
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(255, 255, 255),
              outline=(34, 48, 60), width=2)
    return _lead_finish(img, w, h, "BAY OF BENGAL")

# ---------------------------------------------------------------- panel scenes
# Setiap scene: (d, x0, y0, w, h) dengan h ~52. Latar berwarna + bentuk
# besar yang terbaca sekilas — bukan ikon mikro.

def _bust(d, cx, head_y, r, y1, skin, hair, suit, long_hair=False):
    """Bust kecil: kepala + bahu, dipakai panel 03. y1 = tepi bawah scene."""
    if long_hair:
        d.ellipse([cx - r - 2, head_y - r - 2, cx + r + 2, head_y + r + 6],
                  fill=hair)
    d.pieslice([cx - r * 2, head_y + r - 4, cx + r * 2, head_y + r + 10],
               180, 360, fill=suit)
    d.rectangle([cx - r * 2, head_y + r + 2, cx + r * 2, y1], fill=suit)
    d.ellipse([cx - r, head_y - r, cx + r, head_y + r], fill=skin,
              outline=INK, width=1)
    pts = [(cx + r * math.cos(math.radians(a)),
            head_y + r * math.sin(math.radians(a)))
           for a in range(200, 341, 5)]
    d.polygon(pts, fill=hair, outline=INK)


def sc_03(d, x0, y0, w, h):
    """Modi + William & Kate: 3 bust + bendera India/UK kecil."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 236, 220))
    # bendera India (kiri atas) + Union Jack sederhana (kanan atas)
    d.rectangle([x0 + 6, y0 + 5, x0 + 26, y0 + 8], fill=(255, 153, 51))
    d.rectangle([x0 + 6, y0 + 8, x0 + 26, y0 + 11], fill=(255, 255, 255))
    d.rectangle([x0 + 6, y0 + 11, x0 + 26, y0 + 14], fill=(19, 136, 8))
    d.rectangle([x0 + w - 26, y0 + 5, x0 + w - 6, y0 + 14], fill=(0, 36, 125))
    d.line([x0 + w - 26, y0 + 9, x0 + w - 6, y0 + 9], fill=(255, 255, 255), width=2)
    d.line([x0 + w - 16, y0 + 5, x0 + w - 16, y0 + 14], fill=(255, 255, 255), width=2)
    _bust(d, x0 + w * 0.24, y0 + 26, 9, y0 + h, (210, 170, 130),
          (240, 240, 240), (70, 70, 70))
    _bust(d, x0 + w * 0.50, y0 + 24, 9, y0 + h, (232, 190, 150),
          (210, 170, 90), (38, 55, 90))
    _bust(d, x0 + w * 0.76, y0 + 26, 9, y0 + h, (238, 205, 170),
          (90, 60, 40), (60, 40, 90), long_hair=True)


def sc_05(d, x0, y0, w, h):
    """Seoul court: gedung pengadilan (pedimen + kolom)."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(226, 232, 238))
    bx, bw = x0 + w * 0.14, w * 0.72
    d.polygon([(bx, y0 + 16), (bx + bw, y0 + 16), (bx + bw / 2, y0 + 4)],
              fill=(90, 100, 115))
    for i in range(4):
        cx = bx + 8 + i * (bw - 16) / 3
        d.rectangle([cx - 3, y0 + 17, cx + 3, y0 + 40], fill=(245, 245, 245),
                    outline=(120, 125, 135))
    d.rectangle([bx, y0 + 40, bx + bw, y0 + 44], fill=(90, 100, 115))
    d.rectangle([bx - 4, y0 + 44, bx + bw + 4, y0 + 48], fill=(70, 78, 90))
    # palu kecil di depan
    d.rectangle([x0 + w * 0.68, y0 + 34, x0 + w * 0.86, y0 + 38], fill=(120, 80, 40))
    d.line([x0 + w * 0.77, y0 + 38, x0 + w * 0.77, y0 + 48], fill=(120, 80, 40),
           width=2)


def sc_09(d, x0, y0, w, h):
    """Sensex: bar chart naik + panah hijau + +1.21%."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(226, 240, 226))
    base = y0 + h - 8
    for i, bh in enumerate((12, 20, 28)):
        bx = x0 + 14 + i * 18
        d.rectangle([bx, base - bh, bx + 12, base], fill=(30, 122, 76))
    d.line([(x0 + 12, base - 10), (x0 + 32, base - 20), (x0 + 52, base - 26),
            (x0 + 78, base - 38)], fill=(20, 100, 60), width=5)
    d.polygon([(x0 + 78, base - 44), (x0 + 88, base - 40), (x0 + 76, base - 32)],
              fill=(20, 100, 60))
    d.text((x0 + w - 52, y0 + 6), "+1.21%", font=F_MICRO_B, fill=(20, 100, 60))


def sc_13(d, x0, y0, w, h):
    """ICJ Myanmar: gedung mahkamah + timbangan."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(222, 230, 240))
    bx, bw = x0 + 8, w * 0.52
    d.polygon([(bx, y0 + 14), (bx + bw, y0 + 14), (bx + bw / 2, y0 + 4)],
              fill=(46, 95, 163))
    for i in range(3):
        cx = bx + 8 + i * (bw - 16) / 2
        d.rectangle([cx - 3, y0 + 15, cx + 3, y0 + 38], fill=(245, 245, 245),
                    outline=(120, 125, 135))
    d.rectangle([bx, y0 + 38, bx + bw, y0 + 42], fill=(46, 95, 163))
    # timbangan kanan
    sx = x0 + w * 0.74
    d.line([sx, y0 + 8, sx, y0 + 40], fill=(60, 60, 60), width=2)
    d.line([sx - 14, y0 + 12, sx + 14, y0 + 12], fill=(60, 60, 60), width=2)
    d.polygon([(sx - 18, y0 + 26), (sx - 10, y0 + 26), (sx - 14, y0 + 16)],
              fill=(200, 170, 30))
    d.polygon([(sx + 10, y0 + 26), (sx + 18, y0 + 26), (sx + 14, y0 + 16)],
              fill=(200, 170, 30))


def sc_15(d, x0, y0, w, h):
    """Kyiv embassies: dua gedung + ledakan di antaranya."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(238, 228, 220))
    for bx, bw, bh in ((0.06, 0.30, 0.62), (0.62, 0.32, 0.70)):
        tx, ty = x0 + w * bx, y0 + h * (1 - bh)
        d.rectangle([tx, ty, tx + w * bw, y0 + h], fill=(150, 140, 125))
        for r in range(3):
            for c in range(2):
                d.rectangle([tx + 4 + c * 14, ty + 6 + r * 10,
                             tx + 10 + c * 14, ty + 12 + r * 10],
                            fill=(255, 230, 140))
    ex, ey = x0 + w * 0.50, y0 + h * 0.42
    d.polygon(star_points(ex, ey, 16, 7, 8), fill=(240, 120, 30))
    d.polygon(star_points(ex, ey, 8, 4, 8), fill=(255, 210, 60))
    d.ellipse([ex - 12, ey - 22, ex + 2, ey - 8], fill=(140, 140, 140))


def sc_23(d, x0, y0, w, h):
    """US-Venezuela: dua bendera + cincin terkait."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(243, 238, 228))
    draw_flag_us(d, x0 + 10, y0 + 7, 56, 26)
    d.rectangle([x0 + 10, y0 + 7, x0 + 66, y0 + 33], outline=INK, width=1)
    # bendera Venezuela: kuning-biru-merah
    vx = x0 + w - 66
    for i, c in enumerate([(255, 204, 0), (0, 56, 147), (207, 20, 43)]):
        d.rectangle([vx, y0 + 7 + i * 9, vx + 56, y0 + 16 + i * 9], fill=c)
    d.rectangle([vx, y0 + 7, vx + 56, y0 + 33], outline=INK, width=1)
    # cincin terkait di tengah bawah
    cy = y0 + h - 12
    d.ellipse([x0 + w * 0.38 - 9, cy - 7, x0 + w * 0.38 + 9, cy + 7],
              outline=(60, 60, 60), width=3)
    d.ellipse([x0 + w * 0.58 - 9, cy - 7, x0 + w * 0.58 + 9, cy + 7],
              outline=(60, 60, 60), width=3)


def sc_27(d, x0, y0, w, h):
    """Anthropic: chip + $1.5T di latar gelap."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(30, 34, 48))
    cx, cy = x0 + 30, y0 + h // 2
    d.rectangle([cx - 13, cy - 13, cx + 13, cy + 13], outline=GOLD, width=3)
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD)
    for i in range(3):
        d.line([cx - 8 + i * 8, cy - 18, cx - 8 + i * 8, cy - 13], fill=GOLD, width=2)
        d.line([cx - 8 + i * 8, cy + 13, cx - 8 + i * 8, cy + 18], fill=GOLD, width=2)
    d.text((x0 + 52, y0 + 14), "$1.5T", font=font("DejaVuSans-Bold.ttf", 20),
           fill=(255, 255, 255))
    d.text((x0 + 52, y0 + 36), "VALUATION", font=F_MICRO_B, fill=GOLD)


def sc_30(d, x0, y0, w, h):
    """Hormuz ship: kapal kontainer + ledakan + ombak."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(190, 210, 225))
    sea_y = y0 + int(h * 0.66)
    d.rectangle([x0, sea_y, x0 + w, y0 + h], fill=(90, 140, 180))
    # kontainer warna-warni
    for i, c in enumerate([(200, 60, 40), (40, 120, 180), (220, 160, 40)]):
        d.rectangle([x0 + 14 + i * 20, sea_y - 22, x0 + 32 + i * 20, sea_y - 10],
                    fill=c)
    # lambung kapal
    d.polygon([(x0 + 8, sea_y - 10), (x0 + w - 8, sea_y - 10),
               (x0 + w - 20, sea_y + 6), (x0 + 20, sea_y + 6)], fill=(50, 50, 55))
    # ledakan di dek
    ex, ey = x0 + w * 0.62, sea_y - 26
    d.polygon(star_points(ex, ey, 15, 6, 8), fill=(240, 120, 30))
    d.polygon(star_points(ex, ey, 8, 3, 8), fill=(255, 210, 60))
    for i in range(4):
        ax = x0 + 10 + i * w // 4
        d.arc([ax, sea_y + 8, ax + 22, sea_y + 16], 180, 360,
              fill=(255, 255, 255), width=2)


def sc_31(d, x0, y0, w, h):
    """Gaza: bangunan runtuh + asap + puing."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(228, 224, 214))
    # gedung utuh kiri, gedung patah kanan
    d.rectangle([x0 + 10, y0 + 12, x0 + 46, y0 + h], fill=(150, 140, 125))
    for r in range(3):
        d.rectangle([x0 + 16, y0 + 18 + r * 11, x0 + 40, y0 + 24 + r * 11],
                    fill=(90, 85, 75))
    d.polygon([(x0 + 62, y0 + h), (x0 + 62, y0 + 26), (x0 + 82, y0 + 18),
               (x0 + 96, y0 + 30), (x0 + 110, y0 + 24), (x0 + 118, y0 + h)],
              fill=(120, 112, 100))
    # asap + puing
    d.ellipse([x0 + 84, y0 + 4, x0 + 104, y0 + 20], fill=(140, 140, 140))
    d.ellipse([x0 + 96, y0 + 12, x0 + 112, y0 + 26], fill=(160, 160, 160))
    for bx, by in ((56, 46), (120, 44), (132, 48)):
        d.rectangle([x0 + bx, y0 + by, x0 + bx + 8, y0 + by + 5], fill=(100, 94, 84))


def sc_37(d, x0, y0, w, h):
    """Sudan gold mine: mulut tambang gelap + bongkahan emas + ledakan."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 220, 200))
    # bukit + mulut tambang
    d.polygon([(x0 + 8, y0 + h), (x0 + 30, y0 + 10), (x0 + 90, y0 + 6),
               (x0 + 130, y0 + h)], fill=(170, 145, 110))
    d.pieslice([x0 + 46, y0 + 18, x0 + 86, y0 + 52], 180, 360, fill=(30, 25, 20))
    d.rectangle([x0 + 46, y0 + 34, x0 + 86, y0 + 52], fill=(30, 25, 20))
    # bongkahan emas
    for gx, gy, gr in ((0.78, 0.78, 5), (0.86, 0.68, 4), (0.70, 0.86, 4)):
        d.ellipse([x0 + w * gx - gr, y0 + h * gy - gr, x0 + w * gx + gr,
                   y0 + h * gy + gr], fill=(230, 180, 40), outline=(150, 110, 20))
    # ledakan kecil di mulut tambang
    ex, ey = x0 + 66, y0 + 16
    d.polygon(star_points(ex, ey, 10, 4, 8), fill=(240, 120, 30))
    d.polygon(star_points(ex, ey, 5, 2, 8), fill=(255, 210, 60))


def sc_41(d, x0, y0, w, h):
    """Nicholls cricket: batsman + pitch + stumps + bola."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(200, 225, 190))
    # pitch
    d.rectangle([x0 + w * 0.30, y0 + 6, x0 + w * 0.70, y0 + h - 4],
                fill=(232, 214, 170))
    # stumps
    sx = x0 + w * 0.66
    for i in range(3):
        d.line([sx - 4 + i * 4, y0 + 10, sx - 4 + i * 4, y0 + 22],
               fill=(200, 170, 60), width=2)
    # batsman: kepala + badan + bat
    bx, by = x0 + w * 0.42, y0 + 24
    d.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=(232, 190, 150),
              outline=INK, width=1)
    d.line([bx, by + 6, bx + 2, by + 18], fill=(255, 255, 255), width=5)
    d.line([bx + 2, by + 18, bx - 2, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 2, by + 18, bx + 8, y0 + h - 6], fill=(40, 40, 40), width=4)
    d.line([bx + 4, by + 10, bx + 16, by + 26], fill=(180, 140, 80), width=4)
    # bola merah
    d.ellipse([x0 + w * 0.80 - 4, y0 + h - 14, x0 + w * 0.80 + 4, y0 + h - 6],
              fill=(200, 40, 40))
    d.text((x0 + 6, y0 + 4), "113*", font=font("DejaVuSans-Bold.ttf", 10),
           fill=(20, 80, 40))


def sc_42(d, x0, y0, w, h):
    """Fiji drought: tanah retak + matahari + tanaman kering."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(245, 230, 190))
    # matahari
    sx, sy = x0 + w * 0.82, y0 + 12
    d.ellipse([sx - 9, sy - 9, sx + 9, sy + 9], fill=(255, 200, 40),
              outline=(230, 160, 20), width=1)
    for a in range(0, 360, 45):
        d.line([sx + 12 * math.cos(math.radians(a)), sy + 12 * math.sin(math.radians(a)),
                sx + 16 * math.cos(math.radians(a)), sy + 16 * math.sin(math.radians(a))],
               fill=(230, 160, 20), width=2)
    # tanah retak
    d.rectangle([x0, y0 + h * 0.55, x0 + w, y0 + h], fill=(190, 150, 100))
    for cx, cy, pts in ((0.25, 0.62, [(0, 0), (10, 6), (4, 12), (14, 18)]),
                        (0.55, 0.60, [(0, 0), (-8, 7), (2, 13), (-6, 19)]),
                        (0.75, 0.66, [(0, 0), (10, 5), (6, 11)])):
        ox, oy = x0 + w * cx, y0 + h * cy
        d.line([(ox + px, oy + py) for px, py in pts], fill=(120, 85, 55), width=2)
    # tanaman kering
    d.line([x0 + w * 0.15, y0 + h * 0.58, x0 + w * 0.12, y0 + h * 0.34],
           fill=(140, 110, 60), width=2)
    d.line([x0 + w * 0.12, y0 + h * 0.34, x0 + w * 0.06, y0 + h * 0.28],
           fill=(140, 110, 60), width=2)


PANEL_SCENES = {"03": sc_03, "05": sc_05, "09": sc_09, "13": sc_13,
                "15": sc_15, "23": sc_23, "27": sc_27, "30": sc_30,
                "31": sc_31, "37": sc_37, "41": sc_41, "42": sc_42}
LEAD_SCENES = {"01": draw_shenzhen_scene, "14": draw_bridge_scene,
               "34": draw_tower_scene, "02": draw_cyclone_scene}
LEAD_KICKER = {"01": "SHENZHEN, CHINA — APEC SUMMIT",
               "14": "KERCH STRAIT — UKRAINE WAR",
               "34": "RIYADH, SAUDI ARABIA — KAFD",
               "02": "ODISHA, INDIA — BAY OF BENGAL"}


# ---------------------------------------------------------------- cards
def draw_lead(d, img, s, x, y, w, h):
    """Kartu lead besar: strip ilustrasi 53% + kicker + headline + deck.
    Scene digambar di kanvas 2x oleh LEAD_SCENES (return Image) lalu
    ditempel — bukan digambar langsung di kanvas final."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 4], fill=REGION_COLORS[s["region"]])
    scene_h = int(h * 0.53)
    scene = LEAD_SCENES[s["num"]](int(w - 2), scene_h)
    img.paste(scene, (int(x + 1), int(y + 5)))
    ty = y + 5 + scene_h + 7
    d.text((x + 8, ty), s["num"] + " • " + LEAD_KICKER[s["num"]],
           font=F_LEAD_K, fill=RED)
    lines = wrap(d, s["headline"], F_LEAD_H, w - 16)
    for i, line in enumerate(lines[:3]):
        d.text((x + 8, ty + 15 + i * 18), line, font=F_LEAD_H, fill=INK)
    deck_lines = wrap(d, s["deck"], F_LEAD_D, w - 16)
    dy = ty + 15 + min(len(lines), 3) * 18 + 3
    for i, line in enumerate(deck_lines[:2]):
        d.text((x + 8, dy + i * 14), line, font=F_LEAD_D, fill=(74, 72, 66))
    d.text((x + 8, y + h - 14), "20 NOV • " + s["source"], font=F_MICRO, fill=MUTED)
    tag = "STORY " + s["num"] + " OF 42"
    tw = d.textlength(tag, font=F_MICRO_B)
    d.text((x + w - 8 - tw, y + h - 14), tag, font=F_MICRO_B, fill=RED)


def trunc1(d, text, fnt, max_w):
    """Potong teks jadi satu baris muat max_w, tambah '…' bila terpotong."""
    if d.textlength(text, font=fnt) <= max_w:
        return text
    out = ""
    for word in text.split():
        trial = (out + " " + word).strip()
        if d.textlength(trial + "…", font=fnt) <= max_w:
            out = trial
        else:
            break
    return (out + "…") if out else text[:8] + "…"


def draw_panel(d, s, x, y, w, h):
    """Kartu panel kecil: strip gambar ~43% + headline + deck 1 baris."""
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 3], fill=REGION_COLORS[s["region"]])
    scene_h = int(h * 0.46)
    PANEL_SCENES[s["num"]](d, x + 1, y + 4, w - 2, scene_h)
    ty = y + 4 + scene_h + 5
    d.text((x + 6, ty), s["num"] + " • " + s["region"], font=F_MICRO_B,
           fill=REGION_COLORS[s["region"]])
    lines = wrap(d, s["headline"], F_PAN_H, w - 12)
    for i, line in enumerate(lines[:2]):
        d.text((x + 6, ty + 11 + i * 13), line, font=F_PAN_H, fill=INK)
    dy = ty + 11 + min(len(lines), 2) * 13 + 2
    d.text((x + 6, dy), trunc1(d, s["deck"], F_PAN_D, w - 12),
           font=F_PAN_D, fill=(74, 72, 66))
    d.text((x + 6, y + h - 11), "20 NOV • " + s["source"], font=F_MICRO,
           fill=MUTED)

# ---------------------------------------------------------------- sections
def draw_masthead(d, data):
    d.rectangle([0, 0, W, 58], fill=PAPER)
    d.text((16, 6), "ONE DAY OF WORLD NEWS, ONE PICTURE", font=F_KICK, fill=RED)
    meta_r = "42 STORIES  •  6 REGIONS"
    mw = d.textlength(meta_r, font=F_META)
    d.text((W - 16 - mw, 8), meta_r, font=F_META, fill=MUTED)
    d.text((16, 24), data["title"], font=F_TITLE, fill=INK)
    d.rectangle([0, 60, W, 90], fill=DARK)
    d.text((16, 68), data["edition"].upper(), font=F_DATE, fill=GOLD)
    meta = data["meta"]
    mw = d.textlength(meta, font=F_META)
    d.text((W - 16 - mw, 70), meta, font=F_META, fill=(200, 200, 200))


def draw_wires(d, data, y0, y1):
    """Strip timeline 'First wires' gaya #1: label merah + 5 kolom waktu."""
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


def draw_also_list(d, stories, x0, y0, col_w, rows=13, row_h=11):
    """Daftar bernomor dua kolom, nomor berwarna region + headline."""
    for i, s in enumerate(stories):
        col, r = divmod(i, rows)
        x = x0 + col * (col_w + 12)
        yy = y0 + r * row_h
        col = REGION_COLORS[s["region"]]
        d.ellipse([x, yy + 1, x + 7, yy + 8], fill=col)
        d.text((x + 10, yy), s["num"], font=F_LIST_B, fill=col)
        d.text((x + 28, yy), s["headline"], font=F_LIST, fill=INK)


def draw_numbers(d, numbers, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=DARK, outline=INK, width=1)
    d.text((x + 10, y + 11), "BY THE NUMBERS", font=F_SEC, fill=GOLD)
    cell_w = (w - 170) // len(numbers)
    for i, (label, val) in enumerate(numbers):
        cx = x + 170 + i * cell_w
        d.text((cx, y + 5), label, font=F_NUM_L, fill=(200, 200, 200))
        d.text((cx, y + 17), val, font=F_NUM_V, fill=(255, 255, 255))
    d.text((x + w - 52, y + 11), "20 NOV", font=F_MICRO_B, fill=(200, 200, 200))


def draw_bottom(d, data, y0):
    """DATE CHECK + eksklusi eksplisit + footer sources."""
    d.rectangle([16, y0, 108, y0 + 20], fill=RED)
    d.text((24, y0 + 5), "DATE CHECK", font=F_MICRO_B, fill=(255, 255, 255))
    d.text((116, y0 + 1),
           "Every story here happened or was first reported on Friday 20 November 2026.",
           font=font("DejaVuSans-Bold.ttf", 10), fill=INK)
    d.text((116, y0 + 16),
           "Left out — they broke before Friday: Germany's electricity-tax cut (18 Nov); "
           "Crimean Bridge span falls (17–18 Nov); Anthropic's $81.34bn IPO (19 Nov).",
           font=F_WIRE, fill=(60, 58, 52))
    yy = y0 + 42
    d.line([16, yy, W - 16, yy], fill=LINE, width=1)
    d.text((16, yy + 6), data["footer"], font=F_MICRO, fill=MUTED)
    right = "CLAIM = one side's account, not independently confirmed."
    rw = d.textlength(right, font=F_MICRO)
    d.text((W - 16 - rw, yy + 6), right, font=F_MICRO, fill=MUTED)
    d.text((16, yy + 19), "FRIDAY 20 NOVEMBER 2026  •  ONE DAY, ONE PICTURE",
           font=F_MICRO_B, fill=INK)


# ---------------------------------------------------------------- render
LEAD_NUMS = ["01", "14", "34", "02"]
PANEL_NUMS = ["03", "05", "09", "13", "15", "23",
              "27", "30", "31", "37", "41", "42"]


def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    by_num = {s["num"]: s for s in data["stories"]}
    by_num["01"] = data["hero"]

    draw_masthead(d, data)
    draw_wires(d, data, 96, 150)

    # 4 lead besar sebaris
    lead_y, lead_h = 158, 280
    lw = (W - 32 - 3 * 8) / 4
    for i, num in enumerate(LEAD_NUMS):
        x = 16 + i * (lw + 8)
        draw_lead(d, img, by_num[num], x, lead_y, lw, lead_h)

    # 12 panel berilustrasi, 2 baris x 6
    pw = (W - 32 - 5 * 8) / 6
    for row in range(2):
        y = 446 + row * 132
        for c in range(6):
            s = by_num[PANEL_NUMS[row * 6 + c]]
            x = 16 + c * (pw + 8)
            draw_panel(d, s, x, y, pw, 124)

    # peta + daftar bernomor sisa 26 cerita
    map_y = 722
    d.text((16, map_y), "WHERE IT HAPPENED — 20 NOV 2026", font=F_SEC, fill=INK)
    d.text((436, map_y), "ALSO ON FRIDAY 20 NOVEMBER", font=F_SEC, fill=RED)
    draw_map(d, (16, map_y + 18, 420, 888), data["pins"])
    rest = [s for s in data["stories"]
            if s["num"] not in LEAD_NUMS and s["num"] not in PANEL_NUMS]
    draw_also_list(d, rest, 436, map_y + 20, 280)

    draw_numbers(d, data["numbers"], 16, 894, W - 32, 36)
    draw_bottom(d, data, 936)
    img = add_grain(img)
    return img


def add_grain(img, n=45000, seed=20261120):
    """Bintik kertas koran (random.Random berseed — deterministik):
    menaikkan tekstur + ukuran file tanpa mengubah isi. 1 px, kontras
    sangat rendah.
    JEBAKAN (ditemukan 20 Nov): LCG lama `x % 1024` untuk px DAN py hanya
    memakai 10 bit rendah — pengali 621 (mod 1024) membuat pasangan
    (px,py) bersiklus <=1024 titik, jadi 50k vs 160k bintik HASILNYA
    IDENTIK (0 piksel beda, ukuran tetap 223.761). random.Random tidak
    punya jebakan ini.
    CATATAN: noise per-pixel full-frame (effect_noise / randbytes) DICOBA
    20 Nov — walau blend 0,5% saja ukuran meledak 164 KB -> 688 KB karena
    tiap piksel datar ikut berubah +-1 dan PNG tak bisa kompres; JANGAN
    dipakai lagi."""
    d = ImageDraw.Draw(img)
    pxmap = img.load()
    rng = random.Random(seed)
    for _ in range(n):
        px = rng.randrange(W)
        py = rng.randrange(H)
        r, g, b = pxmap[px, py]
        if r + g + b > 480:
            # area terang (kertas): bintik sedikit lebih gelap
            pxmap[px, py] = (r - 16, g - 16, b - 16)
        elif r + g + b < 240:
            # area gelap (masthead/strip hitam): bintik sedikit lebih terang
            pxmap[px, py] = (r + 16, g + 16, b + 16)
        # area tengah: lewati (bintik putih murni di sana tampak kotor)
    return img


def main():
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        data = json.load(f)
    img = render(data)
    img.save(os.path.join(HERE, "entry.png"), format="PNG", optimize=True)
    print("wrote entry.png", img.size,
          os.path.getsize(os.path.join(HERE, "entry.png")), "bytes")


if __name__ == "__main__":
    main()
