#!/usr/bin/env python3
"""Panel gerbang SPEK QWEN-MAX (a) — Trilateral Shenzhen, 1024x340.

Spek: horizon rendah, meja panjang di sepertiga bawah; 3 pemimpin di
tengah di belakang meja, bendera naik di belakang tiap bahu; siluet
menara Ping An di pita jendela atas. Torso trapesium membulat + kepala
lingkaran, masing-masing miring 3-5 derajat BERBEDA (bukan kloning:
tiap figur digambar di layer sendiri lalu di-rotate +-3..4,5 derajat).
Meja = persegi panjang membulat lebar + 3 mic kecil. Bendera = 3
persegi vertikal US/China/Rusia (dipertahankan seperti v5; frasa
"hijau-bulan-sabit" di spek asli diabaikan — tidak cocok dengan
pemimpin mana pun). SATU dokumen bersama di tengah meja dengan ketiga
tangan menjangkaunya = "kesepakatan trilateral".

Palet: navy #1B2A4A, krem #F4E9D8, merah bendera #C8322B,
emas #D9A441, teal #2E6E65.
Aturan oklusi: kepala di atas bendera, meja di atas torso, tangan di
atas dokumen, kusen jendela di atas skyline; fokus (segel merah
dokumen + menara Ping An) di luar tengah; bobot garis hero 2px vs
latar 0-1px.
Render di resolusi kerja 2x lalu downscale (LANCZOS); teks digambar
di ukuran final sesudah downscale supaya tajam.
Deterministik: tanpa jam/random/network. Run: python3 gate_panel_spec.py
Output: gate_panel_shenzhen_spec.png (1024x340).
File v5 (gate_panel.py + gate_panel_shenzhen.png) TIDAK disentuh.
"""
import math
import os

from PIL import Image, ImageDraw

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import draw_flag_cn, draw_flag_ru, draw_flag_us, font  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
S = 2  # resolusi kerja 2x
W, H = 1024, 340
WW, HH = W * S, H * S

NAVY = (27, 42, 74)
NAVY_LT = (45, 62, 100)
CREAM = (244, 233, 216)
PALE = (239, 227, 204)
RED = (200, 50, 43)
GOLD = (217, 164, 65)
TEAL = (46, 110, 101)
INK = (17, 17, 17)
MUTED = (90, 86, 76)
GREY_LINE = (150, 150, 150)
MULLION = (220, 205, 175)
FINGER = (180, 140, 100)

CX = (297, 512, 727)       # Trump / Xi / Putin
HEAD_R = 44
HEAD_Y = 88
HALF_SH = 115
BAND_Y1 = 215              # tepi bawah band ilustrasi
TABLE_Y0, TABLE_Y1 = 178, 215

F_KICKER = font("DejaVuSans-Bold.ttf", 14)
F_HEAD = font("DejaVuSans-Bold.ttf", 40)
F_DECK = font("DejaVuSans.ttf", 15)
F_STAMP = font("DejaVuSans-Bold.ttf", 11)

HEADLINE = "TRUMP, XI & PUTIN MEET IN SHENZHEN"
DECK = ("First-ever three-way summit at APEC: nuclear arms, energy security "
        "and Ukraine on the table.")
KICKER = "SHENZHEN, CHINA — APEC SUMMIT"
STAMP = "20 NOV 2026  •  AP  •  STORY 01 OF 42"


def X(v):
    return v * S


def figure_layer(cx, skin, hair, suit, tie):
    """Satu figur (kepala + torso trapesium membulat + dasi) di layer
    transparan ukuran kanvas penuh, tegak — rotasi dilakukan pemanggil
    supaya tiap figur miring berbeda."""
    layer = Image.new("RGBA", (WW, HH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    shoulder_y = HEAD_Y + HEAD_R + 6
    body_y1 = BAND_Y1
    # torso: cap membulat + trapesium (menyempit ke bawah)
    d.pieslice([X(cx - HALF_SH), X(shoulder_y - 30),
                X(cx + HALF_SH), X(shoulder_y + 30)],
               180, 360, fill=suit + (255,))
    d.polygon([(X(cx - HALF_SH + 4), X(shoulder_y)),
               (X(cx - HALF_SH + 20), X(body_y1)),
               (X(cx + HALF_SH - 20), X(body_y1)),
               (X(cx + HALF_SH - 4), X(shoulder_y))],
              fill=suit + (255,))
    # kemeja + dasi (terlihat di atas meja: shoulder_y..~170)
    sw = HEAD_R // 3
    d.polygon([(X(cx - sw), X(shoulder_y + 2)), (X(cx + sw), X(shoulder_y + 2)),
               (X(cx), X(shoulder_y + sw + 6))], fill=(255, 255, 255, 255))
    d.polygon([(X(cx - 3), X(shoulder_y + 2)), (X(cx + 3), X(shoulder_y + 2)),
               (X(cx + 4), X(shoulder_y + sw + 8)),
               (X(cx), X(shoulder_y + sw + 12)),
               (X(cx - 4), X(shoulder_y + sw + 8))], fill=tie + (255,))
    # kepala: lingkaran + hair cap chord dangkal (gaya v5)
    d.ellipse([X(cx - HEAD_R), X(HEAD_Y - HEAD_R),
               X(cx + HEAD_R), X(HEAD_Y + HEAD_R)],
              fill=skin + (255,), outline=INK + (255,), width=2 * S)
    pts = [(X(cx + HEAD_R * math.cos(math.radians(a))),
            X(HEAD_Y + HEAD_R * math.sin(math.radians(a))))
           for a in range(200, 341, 5)]
    d.polygon(pts, fill=hair + (255,), outline=INK + (255,))
    return layer


def draw_skyline(d):
    """Siluet menara Shenzhen di pita jendela (baseline y=78).
    Menara Ping An = trapesium meruncing + spire, di kanan (off-center)."""
    d.polygon([(X(830), X(78)), (X(838), X(30)), (X(862), X(30)),
               (X(870), X(78))], fill=TEAL)
    d.polygon([(X(846), X(30)), (X(850), X(12)), (X(854), X(30))],
              fill=TEAL)
    for bx, bw, bh in ((60, 34, 34), (120, 26, 48),
                       (905, 30, 40), (950, 24, 30)):
        d.rectangle([X(bx), X(78 - bh), X(bx + bw), X(78)], fill=TEAL)


def render_panel():
    img = Image.new("RGBA", (WW, HH), CREAM + (255,))
    d = ImageDraw.Draw(img)
    # bar merah atas (aksen lead, gaya v5)
    d.rectangle([0, 0, WW, X(8)], fill=RED)
    # pita jendela atas: latar pucat + skyline + kusen di depan skyline
    d.rectangle([0, X(8), WW, X(78)], fill=PALE)
    draw_skyline(d)
    for mx in (200, 400, 600, 800):
        d.line([X(mx), X(8), X(mx), X(78)], fill=MULLION, width=2 * S)
    d.line([0, X(78), WW, X(78)], fill=NAVY, width=2 * S)
    # 3 bendera vertikal di belakang tiap bahu — digeser 70 px ke kiri
    # dari tiap figur supaya canton/bintang TIDAK tertutup kepala
    # (bendera di tengah figur = bintang China tertutup kepala),
    # dan dinaikkan ke y=18 supaya strip atas bendera terbaca jelas.
    fw, fh, fy = 120, 132, 18
    for cx, fl in zip(CX, (draw_flag_us, draw_flag_cn, draw_flag_ru)):
        fx = cx - 70 - fw // 2
        fl(d, X(fx), X(fy), X(fw), X(fh))
        d.rectangle([X(fx), X(fy), X(fx + fw), X(fy + fh)],
                    outline=INK, width=1 * S)
    # 3 figur, masing-masing layer sendiri + rotasi berbeda (bukan klon)
    # Trump: navy + dasi merah, miring -5,0; Putin: teal + dasi NAVY
    # (dasi krem hilang di atas kemeja putih — navy terbaca),
    # miring -3,5; Xi: charcoal + dasi emas, miring +4,0 (digambar terakhir)
    figs = [(CX[0], (232, 190, 150), (240, 205, 105), NAVY, RED, -5.0),
            (CX[2], (228, 185, 145), (128, 122, 112), TEAL, NAVY, -3.5),
            (CX[1], (238, 205, 170), (30, 30, 30), (35, 35, 35), GOLD, 4.0)]
    for cx, skin, hair, suit, tie, ang in figs:
        layer = figure_layer(cx, skin, hair, suit, tie)
        rot = layer.rotate(ang, resample=Image.BICUBIC,
                           center=(X(cx), X(HEAD_Y)))
        img.alpha_composite(rot)
    d = ImageDraw.Draw(img)
    # meja panjang: navy membulat + strip atas lebih terang + garis emas
    d.rounded_rectangle([X(56), X(TABLE_Y0), X(968), X(TABLE_Y1)],
                        radius=X(8), fill=NAVY)
    d.rounded_rectangle([X(56), X(TABLE_Y0), X(968), X(TABLE_Y0 + 8)],
                        radius=X(8), fill=NAVY_LT)
    d.line([X(56), X(TABLE_Y0), X(968), X(TABLE_Y0)], fill=GOLD, width=2 * S)
    # SATU dokumen bersama di tengah meja — diperlebar ke kanan supaya
    # segel merah di ujung kanan TIDAK tertutup tangan Putin
    d.rectangle([X(452), X(185), X(600), X(213)], fill=(255, 255, 255),
                outline=INK, width=1 * S)
    for ly in (193, 200):
        d.line([X(462), X(ly), X(565), X(ly)], fill=GREY_LINE, width=1 * S)
    d.ellipse([X(578), X(192), X(592), X(206)], fill=RED,
              outline=(255, 255, 255), width=1 * S)
    # lengan: lengan bawah muncul dari balik tepi atas meja (y=178) —
    # lengan atas tersembunyi di balik meja, jadi yang terlihat hanya
    # forearm yang rebah di atas meja menuju dokumen (konvensi flat).
    # Isi = tint jas terang (jas polos TIDAK terbaca di atas meja navy),
    # outline krem tipis.
    sleeves = [((350, 178), (468, 194), (70, 95, 135)),
               ((486, 178), (506, 188), (95, 95, 95)),
               ((674, 178), (556, 194), (75, 145, 135))]
    hands = [(470, 198, (232, 190, 150)),
             (512, 196, (238, 205, 170)),
             (554, 198, (228, 185, 145))]
    for (x1, y1), (x2, y2), tint in sleeves:
        d.line([X(x1), X(y1), X(x2), X(y2)], fill=CREAM, width=14 * S)
        d.line([X(x1), X(y1), X(x2), X(y2)], fill=tint, width=10 * S)
    for hx, hy, skin in hands:
        d.ellipse([X(hx - 13), X(hy - 8), X(hx + 13), X(hy + 8)],
                  fill=skin, outline=INK, width=1 * S)
        for fx in (-5, 1, 7):
            d.line([X(hx + fx), X(hy - 5), X(hx + fx), X(hy + 4)],
                   fill=FINGER, width=1 * S)
    # 3 mic kecil di atas meja (tangkai emas, kepala gelap)
    for mx in (352, 567, 782):
        d.line([X(mx), X(178), X(mx), X(152)], fill=GOLD, width=3 * S)
        d.ellipse([X(mx - 6), X(146), X(mx + 6), X(158)],
                  fill=(40, 40, 40), outline=GOLD, width=2 * S)
    # downscale ke ukuran final, lalu teks + bingkai di ukuran final
    final = img.convert("RGB").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(final)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=2)
    tx = 24
    d.text((tx, 226), KICKER, font=F_KICKER, fill=RED)
    d.text((tx, 246), HEADLINE, font=F_HEAD, fill=INK)
    d.text((tx, 292), DECK, font=F_DECK, fill=(60, 58, 52))
    d.line([tx, 313, W - 24, 313], fill=(200, 192, 172), width=1)
    d.text((tx, 321), STAMP, font=F_STAMP, fill=MUTED)
    tag = "LEAD STORY"
    tw = d.textlength(tag, font=F_STAMP)
    d.text((W - 24 - tw, 321), tag, font=F_STAMP, fill=RED)
    return final


def main():
    img = render_panel()
    out = os.path.join(HERE, "gate_panel_shenzhen_spec.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size,
          os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
