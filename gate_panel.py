#!/usr/bin/env python3
"""Fase 1 — Gate panel: lead story 01 (trilateral Shenzhen), 1024x340.

v5 (iterasi dari v4, 20 Nov 2026 ~10:35): perbaikan atas penilaian
koordinator terhadap v4 — figur masih kecil/jarang, kepala botak, bendera
mengambang, figur tanpa pijakan. Perubahan v5:
  1. Figur ~1,5x: kepala r 46/48, bahu setengah-lebar 115; trio dirapatkan
     (cx 297/512/727, jarak 215 -> bahu tumpang tindih 15 px); cluster
     182..842 = 660 px (~64% lebar band — 75% harfiah butuh bahu 2,75x
     lebar kepala, terlalu kartun; sisi diisi skyline, lihat #5).
  2. Hair cap kembali, TAPI dangkal (chord cap arc 200..340, bukan
     setengah lingkaran seperti v1) + warna kontras dari kulit: Xi hitam,
     Putin abu-coklat, Trump pirang — plus garis hairline (outline INK).
  3. Bendera 110x60 diturunkan: tepi bawah y=72 = setinggi tengah kepala,
     digambar SEBELUM figur -> kepala/bahu menumpuk di depannya, celah
     mengambang hilang.
  4. Grounding: badan sampai tepi bawah band (y=163, tanpa celah) +
     elips bayangan samar di bawah cluster (terlihat di kiri-kanan).
  5. Skyline Shenzhen samar (gaya v1) kembali di zona sisi yang kosong
     (x 30..170 dan 854..994), warna hangat samar di atas PAPER.
Deterministik: tanpa jam/random/network. Run: python3 gate_panel.py
Output: gate_panel_shenzhen.png (1024x340) di dir yang sama.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import (  # noqa: E402
    INK, MUTED, PAPER, draw_flag_cn, draw_flag_ru, draw_flag_us, font,
    star_points,
)
from PIL import Image, ImageDraw  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 340

F_KICKER = font("DejaVuSans-Bold.ttf", 14)
F_HEAD = font("DejaVuSans-Bold.ttf", 40)
F_DECK = font("DejaVuSans.ttf", 15)
F_STAMP = font("DejaVuSans-Bold.ttf", 11)

RED = (192, 57, 43)
SKYLINE = (205, 196, 178)   # samar di atas PAPER (247,243,232)
SHADOW = (210, 200, 180)

HEADLINE = "TRUMP, XI & PUTIN MEET IN SHENZHEN"
DECK = ("First-ever three-way summit at APEC: nuclear arms, energy security "
        "and Ukraine on the table.")
KICKER = "SHENZHEN, CHINA — APEC SUMMIT"
STAMP = "20 NOV 2026  •  AP  •  STORY 01 OF 42"

# geometri cluster v5 (band ilustrasi y=8..163)
CX = (297, 512, 727)        # Trump / Xi / Putin, jarak 215
HALF_SHOULDER = 115         # -> bahu tumpang tindih 2*115-215 = 15 px
HEAD_R = (46, 48, 46)
HEAD_Y = (72, 74, 72)       # Xi tengah sedikit lebih rendah/maju


def draw_figure(d, cx, head_y, head_r, skin, hair, suit, tie):
    """One flat leader, gaya lead #50, skala v5: kepala besar + hair cap
    dangkal, bahu lebar, badan sampai tepi bawah band (y=163)."""
    shoulder_y = head_y + head_r + 6
    body_y1 = 163
    # suit: shoulders with rounded top corners (chord = top half of ellipse)
    d.pieslice([cx - HALF_SHOULDER, shoulder_y - 30,
                cx + HALF_SHOULDER, shoulder_y + 30],
               180, 360, fill=suit)
    d.rectangle([cx - HALF_SHOULDER, shoulder_y,
                 cx + HALF_SHOULDER, body_y1], fill=suit)
    # white shirt triangle + tie in flag colour (tip ends inside the scene)
    d.polygon([(cx - 16, shoulder_y + 2), (cx + 16, shoulder_y + 2),
               (cx, shoulder_y + 28)], fill=(255, 255, 255))
    d.polygon([(cx - 6, shoulder_y + 4), (cx + 6, shoulder_y + 4),
               (cx + 8, shoulder_y + 28), (cx, shoulder_y + 36),
               (cx - 8, shoulder_y + 28)], fill=tie)
    # head: plain circle + shallow hair cap (chord cap: arc 200..340 deg
    # closed by a straight hairline chord — NOT pieslice, whose wedge
    # apex would point down to the middle of the forehead)
    d.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
              fill=skin, outline=INK, width=1)
    pts = [(cx + head_r * math.cos(math.radians(a)),
            head_y + head_r * math.sin(math.radians(a)))
           for a in range(200, 341, 5)]
    d.polygon(pts, fill=hair, outline=INK)


def draw_scene(d):
    """Illustration band y=8..163, gaya lead #50 skala v5: latar PAPER +
    skyline samar di sisi, bayangan bawah cluster, 3 bendera besar di
    belakang kepala (tepi bawah = tengah kepala), 3 figur setengah badan
    yang bahunya bersentuhan dan badannya berpijak di tepi bawah band."""
    x0, x1, y0, y1 = 2, W - 2, 8, 163
    d.rectangle([x0, y0, x1, y1], fill=PAPER)
    # faint Shenzhen skyline silhouette, hanya di zona sisi yang kosong
    # (cluster menutup x 182..842); alas menara y=141, di belakang figur
    for bx, bw, bh in ((30, 40, 50), (80, 30, 72), (120, 44, 40),
                       (854, 36, 60), (900, 28, 84), (940, 44, 46)):
        d.rectangle([bx, y1 - 22 - bh, bx + bw, y1 - 22], fill=SKYLINE)
    d.polygon([(906, y1 - 22 - 84), (914, y1 - 22 - 104),
               (922, y1 - 22 - 84)], fill=SKYLINE)
    # ground shadow ellipse under the cluster (peeks out left/right)
    d.ellipse([512 - 370, 153, 512 + 370, 167], fill=SHADOW)
    # flags BEHIND the figures: 110x60, bottom edge y=72 = mid-head height
    flag_w, flag_h = 110, 60
    flag_y = 12
    for cx, draw_flag in ((CX[0], draw_flag_us), (CX[1], draw_flag_cn),
                          (CX[2], draw_flag_ru)):
        fx = cx - flag_w // 2
        draw_flag(d, fx, flag_y, flag_w, flag_h)
        d.rectangle([fx, flag_y, fx + flag_w, flag_y + flag_h],
                    outline=INK, width=1)
    # three leaders, centre one slightly forward (drawn last, on top)
    draw_figure(d, CX[0], HEAD_Y[0], HEAD_R[0], (232, 190, 150),
                (240, 205, 105), (38, 55, 90), (178, 34, 34))
    # Trump: navy suit, red tie, blond hair cap
    draw_figure(d, CX[2], HEAD_Y[2], HEAD_R[2], (228, 185, 145),
                (128, 122, 112), (110, 35, 45), (0, 57, 166))
    # Putin: maroon suit, blue tie, grey-brown hair cap
    draw_figure(d, CX[1], HEAD_Y[1], HEAD_R[1], (238, 205, 170),
                (30, 30, 30), (35, 35, 35), (255, 200, 0))
    # Xi: black suit, gold tie, black hair cap


def render_panel():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # red top bar (lead accent, gaya #50) + ink frame
    d.rectangle([0, 0, W, 8], fill=RED)
    draw_scene(d)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=2)
    # --- text block below the scene ---
    tx = 24
    d.text((tx, 178), KICKER, font=F_KICKER, fill=RED)
    d.text((tx, 200), HEADLINE, font=F_HEAD, fill=INK)
    d.text((tx, 256), DECK, font=F_DECK, fill=(60, 58, 52))
    d.line([tx, 296, W - 24, 296], fill=(200, 192, 172), width=1)
    d.text((tx, 308), STAMP, font=F_STAMP, fill=MUTED)
    tag = "LEAD STORY"
    tw = d.textlength(tag, font=F_STAMP)
    d.text((W - 24 - tw, 308), tag, font=F_STAMP, fill=RED)
    return img


def main():
    img = render_panel()
    out = os.path.join(HERE, "gate_panel_shenzhen.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
