#!/usr/bin/env python3
"""Render the 20 November 2026 front page: 42 verified stories, 6 regions.

Reads manifest.json (headlines verified against reporting filed 19-20 Nov
2026) and writes entry.png, 1024x1024, deterministic: no clock, no random,
no network. Run: python3 render.py
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
MUTED = (90, 86, 76)
CARD = (255, 255, 255)
LINE = (200, 192, 172)
OCEAN = (207, 224, 236)
LAND = (232, 216, 178)
LAND_EDGE = (168, 148, 108)

REGION_COLORS = {
    "GLOBAL": (26, 26, 26),
    "ASIA": (192, 57, 43),
    "EUROPE": (46, 95, 163),
    "AMERICAS": (30, 122, 76),
    "MIDDLE EAST": (183, 121, 31),
    "AFRICA": (125, 60, 152),
    "OCEANIA": (14, 124, 123),
}

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


F_TITLE = font("DejaVuSerif-Bold.ttf", 40)
F_DATE = font("DejaVuSans-Bold.ttf", 15)
F_META = font("DejaVuSans.ttf", 12)
F_HERO = font("DejaVuSans-Bold.ttf", 27)
F_HERO_DECK = font("DejaVuSans.ttf", 14)
F_STAMP = font("DejaVuSans-Bold.ttf", 10)
F_CELL_H = font("DejaVuSans-Bold.ttf", 12)
F_CELL_D = font("DejaVuSans.ttf", 10)
F_MICRO = font("DejaVuSans.ttf", 8)
F_MICRO_B = font("DejaVuSans-Bold.ttf", 8)
F_BAND = font("DejaVuSans-Bold.ttf", 9)
F_MAP_T = font("DejaVuSans-Bold.ttf", 12)
F_WIRE = font("DejaVuSans.ttf", 11)
F_WIRE_B = font("DejaVuSans-Bold.ttf", 11)
F_NUM = font("DejaVuSans-Bold.ttf", 13)
F_NUML = font("DejaVuSans.ttf", 11)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning lines that fit max_w pixels."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def star_points(cx, cy, r_out, r_in, points=5, rot=-90):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180.0 / points)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_icon(d, kind, x, y, s, color):
    """Tiny white pictogram, s = box size, drawn inside (x, y, x+s, y+s)."""
    if kind == "summit":  # three small flags
        for i, c in enumerate([(178, 34, 34), (200, 170, 30), (40, 90, 160)]):
            fx = x + i * (s // 3)
            d.rectangle([fx, y + 2, fx + s // 3 - 2, y + s - 4], fill=c)
            d.line([fx + 1, y + 2, fx + 1, y + s - 2], fill=(255, 255, 255), width=1)
    elif kind == "storm":  # cloud + rain
        d.ellipse([x + 1, y + 2, x + s - 6, y + s // 2 + 2], fill=color)
        d.ellipse([x + s // 3, y, x + s - 1, y + s // 2], fill=color)
        for i in range(3):
            rx = x + 3 + i * 5
            d.line([rx, y + s // 2 + 3, rx - 1, y + s - 2], fill=color, width=2)
    elif kind == "court":  # scales
        d.line([x + s // 2, y + 1, x + s // 2, y + s - 3], fill=color, width=2)
        d.line([x + 2, y + 4, x + s - 2, y + 4], fill=color, width=2)
        d.polygon([(x + 1, y + s - 3), (x + 6, y + s - 3), (x + 3, y + 6)], fill=color)
        d.polygon([(x + s - 6, y + s - 3), (x + s - 1, y + s - 3), (x + s - 3, y + 6)], fill=color)
    elif kind == "watch":  # atom
        d.ellipse([x + s // 2 - 2, y + s // 2 - 2, x + s // 2 + 2, y + s // 2 + 2], fill=color)
        for ang in (0, 60, 120):
            a = math.radians(ang)
            rx, ry = s // 2 - 1, s // 4
            pts = []
            for t in range(25):
                th = 2 * math.pi * t / 24
                px = x + s // 2 + rx * math.cos(th) * math.cos(a) - ry * math.sin(th) * math.sin(a)
                py = y + s // 2 + rx * math.cos(th) * math.sin(a) + ry * math.sin(th) * math.cos(a)
                pts.append((px, py))
            d.line(pts, fill=color, width=1)
    elif kind == "trade":  # bar chart
        for i, h in enumerate((5, 9, 13)):
            bx = x + 2 + i * 5
            d.rectangle([bx, y + s - 2 - h, bx + 3, y + s - 2], fill=color)
    elif kind == "diplomacy":  # two linked rings
        d.ellipse([x + 1, y + 3, x + s // 2 + 2, y + s - 3], outline=color, width=2)
        d.ellipse([x + s // 2 - 2, y + 3, x + s - 1, y + s - 3], outline=color, width=2)
    elif kind == "market":  # rising line
        d.line([(x + 1, y + s - 4), (x + s // 3, y + s // 2), (x + 2 * s // 3, y + s // 2 - 3),
                (x + s - 2, y + 2)], fill=color, width=2)
        d.polygon([(x + s - 5, y + 1), (x + s - 1, y + 1), (x + s - 3, y + 5)], fill=color)
    elif kind == "fire":  # flame
        d.polygon([(x + s // 2, y + 1), (x + s - 2, y + s // 2 + 2), (x + s - 4, y + s - 2),
                   (x + 4, y + s - 2), (x + 2, y + s // 2 + 2)], fill=color)
    elif kind == "sport":  # ball
        d.ellipse([x + 1, y + 1, x + s - 1, y + s - 1], outline=color, width=2)
        d.line([x + 1, y + s // 2, x + s - 1, y + s // 2], fill=color, width=1)
        d.arc([x + 1, y + 1, x + s - 1, y + s - 1], 300, 60, fill=color, width=1)
    elif kind == "war":  # burst
        d.polygon(star_points(x + s // 2, y + s // 2, s // 2, s // 5, 8), fill=color)
    elif kind == "tech":  # chip
        d.rectangle([x + 3, y + 3, x + s - 3, y + s - 3], outline=color, width=2)
        d.rectangle([x + s // 2 - 2, y + s // 2 - 2, x + s // 2 + 2, y + s // 2 + 2], fill=color)
        for i in range(3):
            d.line([x + 4 + i * 4, y, x + 4 + i * 4, y + 3], fill=color, width=1)
            d.line([x + 4 + i * 4, y + s - 3, x + 4 + i * 4, y + s], fill=color, width=1)
    elif kind == "disaster":  # warning triangle
        d.polygon([(x + s // 2, y + 1), (x + s - 1, y + s - 2), (x + 1, y + s - 2)], outline=color, width=2)
        d.line([x + s // 2, y + 5, x + s // 2, y + s - 6], fill=color, width=2)
        d.point([x + s // 2, y + s - 4], fill=color)
    elif kind == "energy":  # bolt
        d.polygon([(x + s // 2 + 2, y + 1), (x + 2, y + s // 2 + 1), (x + s // 2 - 1, y + s // 2 + 1),
                   (x + s // 2 - 2, y + s - 1), (x + s - 2, y + s // 2 - 1),
                   (x + s // 2 + 1, y + s // 2 - 1)], fill=color)
    elif kind == "vote":  # ballot box + tick
        d.rectangle([x + 1, y + s // 2, x + s - 1, y + s - 2], outline=color, width=2)
        d.line([(x + 2, y + s // 2 - 2), (x + s // 2, y + 3), (x + s - 1, y + 1)], fill=color, width=2)
    elif kind == "press":  # newspaper
        d.rectangle([x + 1, y + 2, x + s - 1, y + s - 2], outline=color, width=2)
        d.line([x + 3, y + 5, x + s - 3, y + 5], fill=color, width=2)
        d.line([x + 3, y + 9, x + s - 5, y + 9], fill=color, width=1)
        d.line([x + 3, y + 12, x + s - 5, y + 12], fill=color, width=1)
    else:  # globe fallback
        d.ellipse([x + 1, y + 1, x + s - 1, y + s - 1], outline=color, width=2)
        d.line([x + 1, y + s // 2, x + s - 1, y + s // 2], fill=color, width=1)


# ---------------------------------------------------------------- flags
def draw_flag_us(d, x, y, w, h):
    for i in range(13):
        c = (178, 34, 34) if i % 2 == 0 else (255, 255, 255)
        d.rectangle([x, y + i * h // 13, x + w, y + (i + 1) * h // 13], fill=c)
    cw, ch = w * 2 // 5, h * 7 // 13
    d.rectangle([x, y, x + cw, y + ch], fill=(40, 60, 120))
    for r in range(4):
        for c in range(5):
            d.ellipse([x + 4 + c * (cw - 8) // 4, y + 3 + r * (ch - 6) // 3,
                       x + 7 + c * (cw - 8) // 4, y + 6 + r * (ch - 6) // 3], fill=(255, 255, 255))


def draw_flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    d.polygon(star_points(x + w // 5, y + h // 4, 9, 4), fill=(255, 222, 0))
    for sx, sy in ((w // 2, h // 6), (w * 3 // 5, h // 3), (w * 3 // 5, h * 7 // 12), (w // 2, h * 3 // 4)):
        d.polygon(star_points(x + sx, y + sy, 4, 2), fill=(255, 222, 0))


def draw_flag_ru(d, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        d.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=c)


# ---------------------------------------------------------------- world map
# Coarse lon/lat outlines, good enough to read at strip size.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 69), (-80, 73), (-60, 62), (-55, 52),
     (-70, 42), (-75, 35), (-80, 26), (-85, 20), (-90, 15), (-95, 18), (-105, 22),
     (-115, 30), (-125, 40), (-125, 50), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-70, 12), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -54), (-73, -40), (-73, -20), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (24, 59), (30, 60), (28, 66), (40, 68), (45, 66), (40, 60), (35, 55),
     (30, 50), (28, 45), (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (-2, 37)],
    [(-6, 35), (10, 37), (20, 32), (32, 31), (35, 28), (38, 22), (43, 12), (48, 11),
     (51, 10), (44, 2), (40, -10), (35, -18), (32, -26), (26, -34), (19, -35),
     (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5), (-15, 11), (-17, 15),
     (-16, 20), (-14, 25), (-10, 30)],
    [(40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (170, 67), (178, 65),
     (162, 60), (158, 52), (142, 50), (140, 40), (130, 35), (127, 33), (120, 28),
     (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 15), (75, 10),
     (70, 20), (60, 25), (55, 26), (50, 29), (45, 30), (40, 35), (35, 36),
     (30, 36), (28, 40), (30, 45), (35, 50), (40, 55)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (132, -32), (137, -35),
     (142, -38), (147, -39), (150, -37), (153, -32), (153, -27), (150, -23),
     (146, -19), (142, -11), (137, -12), (132, -12), (126, -14), (122, -17), (118, -20)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44)],
    [(95, 5), (100, 0), (105, -5), (110, -7), (115, -8), (120, -10), (125, -8),
     (130, -4), (135, -3), (140, -8), (138, -5)],
    [(167, -45), (170, -42), (173, -40), (176, -38), (178, -37), (174, -41), (170, -43)],
    [(-21, 64), (-18, 66), (-14, 65), (-18, 63)],
]
OCEAN_LABELS = [("PACIFIC", -150, -5), ("ATLANTIC", -30, 5), ("INDIAN", 80, -30),
                ("PACIFIC", 150, -10)]
LAT_MIN, LAT_MAX = -58, 80


def draw_map(d, box, pins):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=OCEAN)
    d.rectangle(box, outline=INK, width=1)
    mw, mh = x1 - x0, y1 - y0

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360.0 * mw,
                y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * mh)

    for lon in range(-150, 181, 30):
        px = x0 + (lon + 180) / 360.0 * mw
        d.line([px, y0, px, y1], fill=(255, 255, 255), width=1)
    for lat in range(-60, 81, 30):
        py = y0 + (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * mh
        d.line([x0, py, x1, py], fill=(255, 255, 255), width=1)
    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND, outline=LAND_EDGE)
    for name, lon, lat in OCEAN_LABELS:
        px, py = proj(lon, lat)
        d.text((px - 22, py - 5), name, font=F_MICRO_B, fill=(110, 140, 165))
    for pin in pins:
        px, py = proj(pin["lon"], pin["lat"])
        col = REGION_COLORS[pin["region"]]
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline=(255, 255, 255), width=2)
        d.text((px - 3, py - 5), pin["n"], font=F_MICRO_B, fill=(255, 255, 255))
        lw = d.textlength(pin["label"], font=F_MICRO_B)
        anchor = pin.get("anchor", "r")
        if anchor == "r":
            lx, ly = px + 11, py - 5
        elif anchor == "l":
            lx, ly = px - 11 - lw, py - 5
        elif anchor == "a":
            lx, ly = px - lw / 2, py - 19
        else:  # below
            lx, ly = px - lw / 2, py + 10
        lx = min(max(lx, x0 + 2), x1 - lw - 2)
        ly = min(max(ly, y0 + 2), y1 - 11)
        d.text((lx, ly), pin["label"], font=F_MICRO_B, fill=INK)


# ---------------------------------------------------------------- layout
MARGIN = 16
COLS, ROWS = 7, 6
GAP = 6


def draw_masthead(d, data):
    d.rectangle([0, 0, W, 86], fill=INK)
    d.text((MARGIN, 8), data["title"], font=F_TITLE, fill=(247, 243, 232))
    d.text((MARGIN, 58), data["edition"].upper(), font=F_DATE, fill=(255, 214, 90))
    meta = data["meta"]
    mw = d.textlength(meta, font=F_META)
    d.text((W - MARGIN - mw, 60), meta, font=F_META, fill=(200, 200, 200))


def draw_hero(d, hero):
    y0, y1 = 92, 246
    d.rectangle([MARGIN, y0, W - MARGIN, y1], fill=(255, 255, 255), outline=INK, width=2)
    fx, fy, fw, fh = MARGIN + 14, y0 + 30, 96, 60
    draw_flag_us(d, fx, fy, fw, fh)
    draw_flag_cn(d, fx + fw + 8, fy, fw, fh)
    draw_flag_ru(d, fx + 2 * (fw + 8), fy, fw, fh)
    d.text((fx, fy + fh + 8), hero["place"] + " — APEC SUMMIT", font=F_MICRO_B, fill=MUTED)
    tx = fx + 3 * fw + 2 * 8 + 18
    d.text((tx, y0 + 14), hero["headline"], font=F_HERO, fill=INK)
    for i, line in enumerate(wrap(d, hero["deck"], F_HERO_DECK, W - MARGIN - tx - 14)):
        d.text((tx, y0 + 58 + i * 19), line, font=F_HERO_DECK, fill=(60, 58, 52))
    stamp = "20 NOV 2026  •  " + hero["source"] + "  •  STORY 01 OF 42"
    d.text((tx, y1 - 30), stamp, font=F_STAMP, fill=REGION_COLORS["GLOBAL"])
    d.text((fx, y1 - 30), "LEAD STORY", font=F_STAMP, fill=(192, 57, 43))


def draw_cell(d, s, x, y, w, h):
    col = REGION_COLORS[s["region"]]
    d.rectangle([x, y, x + w, y + h], fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + w, y + 18], fill=col)
    d.text((x + 5, y + 4), s["num"] + " · " + s["region"], font=F_BAND, fill=(255, 255, 255))
    draw_icon(d, s["icon"], x + w - 17, y + 2, 14, (255, 255, 255))
    lines = wrap(d, s["headline"], F_CELL_H, w - 10)
    for i, line in enumerate(lines[:2]):
        d.text((x + 5, y + 23 + i * 15), line, font=F_CELL_H, fill=INK)
    deck_lines = wrap(d, s["deck"], F_CELL_D, w - 10)
    for i, line in enumerate(deck_lines[:2]):
        d.text((x + 5, y + 55 + i * 12), line, font=F_CELL_D, fill=(74, 72, 66))
    d.text((x + 5, y + h - 11), "20 NOV • " + s["source"], font=F_MICRO, fill=MUTED)


def draw_numbers(d, numbers, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 26, 26), outline=INK, width=1)
    d.text((x + 6, y + 4), "BY THE NUMBERS", font=F_BAND, fill=(255, 214, 90))
    d.text((x + w - 42, y + 4), "20 NOV", font=F_MICRO_B, fill=(200, 200, 200))
    yy = y + 20
    for label, val in numbers:
        d.text((x + 6, yy), label, font=F_MICRO, fill=(200, 200, 200))
        vw = d.textlength(val, font=F_NUM)
        d.text((x + w - 6 - vw, yy - 2), val, font=F_NUM, fill=(255, 255, 255))
        yy += 12


def draw_bottom(d, data):
    y0, y1 = 842, 1008
    # left: map
    mx0, my0, mx1, my1 = MARGIN, y0, 500, y1
    d.text((mx0, y0), "WHERE IT HAPPENED — 20 NOV 2026", font=F_MAP_T, fill=INK)
    d.text((mx0, y0 + 16), "Numbered pins match the story numbers above", font=F_MICRO, fill=MUTED)
    draw_map(d, (mx0, y0 + 32, mx1, y1), data["pins"])
    # right: first wires + footer
    rx0, rx1 = 516, W - MARGIN
    d.text((rx0, y0), "FIRST WIRES — 20 NOV, UTC", font=F_MAP_T, fill=INK)
    yy = y0 + 22
    for t, item in data["wires"]:
        d.text((rx0, yy), t, font=F_WIRE_B, fill=(192, 57, 43))
        for i, line in enumerate(wrap(d, item, F_WIRE, rx1 - rx0 - 52)):
            d.text((rx0 + 46, yy + i * 14), line, font=F_WIRE, fill=INK)
        yy += 14 + 13 * (len(wrap(d, item, F_WIRE, rx1 - rx0 - 52)) - 1)
    yy += 2
    d.line([rx0, yy, rx1, yy], fill=LINE, width=1)
    yy += 7
    d.text((rx0, yy), "DATE CHECK — every story verified against", font=F_WIRE_B, fill=INK)
    yy += 15
    d.text((rx0, yy), "reporting dated 20 Nov 2026 (UTC).", font=F_WIRE, fill=INK)
    yy += 16
    d.text((rx0, yy), "42 stories  •  6 regions  •  7 pins on the map", font=F_WIRE, fill=INK)
    yy += 16
    for line in wrap(d, data["footer"], F_MICRO, rx1 - rx0):
        d.text((rx0, yy), line, font=F_MICRO, fill=MUTED)
        yy += 11


def render(data):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d, data)
    draw_hero(d, data["hero"])
    grid_y0, grid_y1 = 252, 836
    cw = (W - 2 * MARGIN - (COLS - 1) * GAP) / COLS
    ch = (grid_y1 - grid_y0 - (ROWS - 1) * GAP) / ROWS
    cells = data["stories"] + [None]  # 41 stories + numbers box = 42 slots
    for idx, s in enumerate(cells):
        r, c = divmod(idx, COLS)
        x = MARGIN + c * (cw + GAP)
        y = grid_y0 + r * (ch + GAP)
        if s is None:
            draw_numbers(d, data["numbers"], x, y, cw, ch)
        else:
            draw_cell(d, s, x, y, cw, ch)
    draw_bottom(d, data)
    return img


def main():
    with open(os.path.join(HERE, "manifest.json"), encoding="utf-8") as f:
        data = json.load(f)
    img = render(data)
    img.save(os.path.join(HERE, "entry.png"), format="PNG", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
