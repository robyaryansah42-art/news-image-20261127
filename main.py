#!/usr/bin/env python3
"""news-image-20261127: draw a one-page newspaper front page summing up
the world news of Friday 27 November 2026.

Pure Python 3 standard library. No network, no external files, no clock,
no randomness: two runs produce byte-identical PNG output.

Writes entry.png into MAKEFUN_OUTPUT_DIR (default "out").
"""

import os
import struct
import zlib

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (185, 28, 28)
BLUE = (29, 78, 216)
GRAY = (90, 86, 76)
LIGHT = (232, 226, 210)
DARKRED = (127, 29, 29)

canvas = bytearray(PAPER[0] * 0 for _ in range(0))  # placeholder, replaced below
px = bytearray(W * H * 3)
for _i in range(W * H):
    px[_i * 3] = PAPER[0]
    px[_i * 3 + 1] = PAPER[1]
    px[_i * 3 + 2] = PAPER[2]


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        o = (y * W + x) * 3
        px[o] = c[0]
        px[o + 1] = c[1]
        px[o + 2] = c[2]


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            set_px(xx, yy, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                set_px(xx, yy, c)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits each (bit 4 = leftmost column).
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    'a': (0x00, 0x00, 0x0E, 0x01, 0x0F, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x00, 0x0E, 0x11, 0x10, 0x11, 0x0E),
    'd': (0x01, 0x01, 0x0D, 0x13, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x00, 0x0E, 0x11, 0x1F, 0x10, 0x0E),
    'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x16, 0x19, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x00, 0x1A, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x00, 0x16, 0x19, 0x11, 0x11, 0x11),
    'o': (0x00, 0x00, 0x0E, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10),
    'q': (0x00, 0x00, 0x0D, 0x13, 0x11, 0x0F, 0x01),
    'r': (0x00, 0x00, 0x16, 0x19, 0x10, 0x10, 0x10),
    's': (0x00, 0x00, 0x0F, 0x10, 0x0E, 0x01, 0x1E),
    't': (0x08, 0x08, 0x1E, 0x08, 0x08, 0x09, 0x06),
    'u': (0x00, 0x00, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x00, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x00, 0x11, 0x11, 0x15, 0x15, 0x1B),
    'x': (0x00, 0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11),
    'y': (0x00, 0x00, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x00, 0x1F, 0x02, 0x04, 0x08, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    ' ': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    '"': (0x0A, 0x0A, 0x0A, 0x00, 0x00, 0x00, 0x00),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '%': (0x18, 0x19, 0x02, 0x04, 0x08, 0x13, 0x03),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "'": (0x04, 0x04, 0x08, 0x00, 0x00, 0x00, 0x00),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '*': (0x00, 0x04, 0x15, 0x0E, 0x15, 0x04, 0x00),
    '+': (0x00, 0x04, 0x04, 0x1F, 0x04, 0x04, 0x00),
    ',': (0x00, 0x00, 0x00, 0x00, 0x0C, 0x04, 0x08),
    '-': (0x00, 0x00, 0x00, 0x1F, 0x00, 0x00, 0x00),
    '.': (0x00, 0x00, 0x00, 0x00, 0x00, 0x0C, 0x0C),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    ':': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x0C, 0x00),
    ';': (0x00, 0x0C, 0x0C, 0x00, 0x0C, 0x04, 0x08),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '=': (0x00, 0x00, 0x1F, 0x00, 0x1F, 0x00, 0x00),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    '@': (0x0E, 0x11, 0x01, 0x0D, 0x15, 0x15, 0x0E),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    '\\': (0x10, 0x10, 0x08, 0x04, 0x02, 0x01, 0x01),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '^': (0x04, 0x0A, 0x11, 0x00, 0x00, 0x00, 0x00),
    '_': (0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F),
    '`': (0x08, 0x04, 0x02, 0x00, 0x00, 0x00, 0x00),
    '{': (0x06, 0x08, 0x08, 0x1C, 0x08, 0x08, 0x06),
    '|': (0x04, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    '}': (0x0C, 0x02, 0x02, 0x0E, 0x02, 0x02, 0x0C),
    '~': (0x00, 0x00, 0x0E, 0x15, 0x00, 0x00, 0x00),
}

CHAR_W = 6  # 5 px glyph + 1 px spacing, times scale


def text_w(s, scale):
    return len(s) * CHAR_W * scale - scale


def draw_text(x, y, s, scale, c):
    for i, ch in enumerate(s):
        g = FONT.get(ch, FONT['?'])
        cx = x + i * CHAR_W * scale
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row & (1 << (4 - col)):
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
    return x + text_w(s, scale)


def draw_center(x, y, w, s, scale, c):
    tw = text_w(s, scale)
    draw_text(x + (w - tw) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns list of lines."""
    words = s.split(' ')
    lines, cur = [], ''
    for wd in words:
        trial = (cur + ' ' + wd).strip()
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_block(x, y, w, lines, scale, c, lh=None):
    lh = lh or (7 * scale + 4)
    for ln in lines:
        draw_text(x, y, ln, scale, c)
        y += lh
    return y


# ---------------------------------------------------------------- icons
def icon_burst(cx, cy, c):
    # explosion starburst
    for dx, dy in [(0, -16), (11, -11), (16, 0), (11, 11), (0, 16),
                   (-11, 11), (-16, 0), (-11, -11)]:
        x0, y0 = cx, cy
        x1, y1 = cx + dx, cy + dy
        steps = max(abs(dx), abs(dy))
        for s in range(steps + 1):
            set_px(x0 + (x1 - x0) * s // steps, y0 + (y1 - y0) * s // steps, c)
    circle(cx, cy, 6, c)


def icon_cloud(cx, cy, c):
    circle(cx - 10, cy + 2, 8, c)
    circle(cx + 2, cy - 4, 10, c)
    circle(cx + 12, cy + 2, 8, c)
    rect(cx - 18, cy - 2, 36, 10, c)
    for dx in (-12, -4, 4, 12):
        for dy in (12, 16, 20):
            set_px(cx + dx, cy + dy, c)


def icon_chess(cx, cy, c):
    for r in range(4):
        for col in range(4):
            if (r + col) % 2 == 0:
                rect(cx - 16 + col * 8, cy - 16 + r * 8, 8, 8, c)


def icon_ship(cx, cy, c):
    # hull
    for yy in range(0, 8):
        wdt = 26 - yy * 2
        rect(cx - wdt // 2, cy + yy, wdt, 1, c)
    vline(cx, cy - 16, 16, c)
    for yy in range(0, 10):
        rect(cx + 1, cy - 16 + yy, 10 - yy, 1, c)
    for dx in (-18, -6, 6, 18):
        set_px(cx + dx, cy + 12, c)
        set_px(cx + dx, cy + 14, c)


def icon_globe(cx, cy, c):
    circle(cx, cy, 15, c)
    # wipe interior back to paper, redraw outline + meridians
    for yy in range(cy - 13, cy + 14):
        for xx in range(cx - 13, cx + 14):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= 13 * 13:
                set_px(xx, yy, PAPER)
    for a in range(360):
        import math
        rad = a * 3.141592653589793 / 180.0
        set_px(cx + int(15 * math.cos(rad)), cy + int(15 * math.sin(rad)), c)
    hline(cx - 15, cy, 31, c)
    vline(cx, cy - 15, 31, c)


ICONS = {'burst': icon_burst, 'cloud': icon_cloud, 'chess': icon_chess,
         'ship': icon_ship, 'globe': icon_globe}


# ---------------------------------------------------------------- content
# Stories verified from reporting published on 27 November 2026
# (NYT, BBC, Reuters, NDTV, Newstalk ZB, CNA).
LEAD = {
    'tag': 'LEAD STORY - MIDDLE EAST',
    'head': 'DRONE STRIKE IN KUWAIT KILLS TWO ITALIANS',
    'deck': ('Kuwait says an Iranian drone strike killed two Italian workers. '
             'Tehran denies responsibility as Rome demands answers. '
             'Italy confirms the victims were two of its citizens.'),
}

STORIES = [
    {'tag': 'GAZA', 'icon': 'globe',
     'head': 'Hamas weighs reply after Israel kills 10 in Gaza',
     'deck': 'Ceasefire talks hang in the balance as the death toll rises.'},
    {'tag': 'THAILAND', 'icon': 'burst',
     'head': 'Blast at Bangkok oil depot injures nine',
     'deck': 'Bangchak shuts all units after the fire; several are critical.'},
    {'tag': 'UNITED STATES', 'icon': 'cloud',
     'head': 'Storm wrecks Thanksgiving travel',
     'deck': '100th Macy\'s parade postponed; 500,000 lose power.'},
    {'tag': 'BRITAIN', 'icon': 'globe',
     'head': 'UK net migration falls to lowest since 1997',
     'deck': 'New figures show a sharp drop, pandemic years aside.'},
    {'tag': 'FRANCE', 'icon': 'globe',
     'head': 'Depardieu to stand trial over alleged rape',
     'deck': 'Paris court rules on the 2018 case against the actor.'},
    {'tag': 'SPAIN', 'icon': 'ship',
     'head': 'Tanker capsizes off Ibiza; one dead',
     'deck': 'Diesel tanker carrying up to 7,000 tonnes goes down.'},
    {'tag': 'SPORT', 'icon': 'chess',
     'head': 'Gukesh, Sindarov draw marathon Game 3',
     'deck': 'World Chess Championship still level after three games.'},
    {'tag': 'NEW ZEALAND', 'icon': 'globe',
     'head': 'Final vote count to settle parliament',
     'deck': 'Roughly 400,000 special votes decide a slim majority.'},
]

TICKER = ('ALSO TODAY:  Black Friday sales begin  |  Ebola cases in Congo pass '
          '12,000  |  Trump seeks probe into US GDP figures  |  '
          'Sinner out of Australian Open with knee injury')


# ---------------------------------------------------------------- layout
def draw():
    M = 36
    CW = W - 2 * M

    # outer frame
    rect(0, 0, W, 10, INK)
    rect(0, H - 10, W, 10, INK)
    rect(M - 14, 24, 2, H - 48, INK)
    rect(W - M + 12, 24, 2, H - 48, INK)

    # masthead
    draw_center(M, 40, CW, 'THE WORLD TODAY', 7, INK)
    hline(M, 118, CW, INK, 3)
    draw_center(M, 130, CW, 'FRIDAY 27 NOVEMBER 2026', 4, RED)
    draw_center(M, 162, CW, "One day's world news - in a single page", 2, GRAY)
    hline(M, 192, CW, INK, 3)

    # ---- lead story
    ly = 210
    rect(M, ly, CW, 168, LIGHT)
    hline(M, ly, CW, RED, 4)
    draw_text(M + 16, ly + 16, LEAD['tag'], 2, RED)
    head_lines = wrap(LEAD['head'], CW - 32, 4)
    y = ly + 44
    for ln in head_lines:
        draw_text(M + 16, y, ln, 4, INK)
        y += 7 * 4 + 6
    deck_lines = wrap(LEAD['deck'], CW - 32, 2)
    y = draw_block(M + 16, y + 4, CW - 32, deck_lines, 2, GRAY, lh=7 * 2 + 5)

    # ---- grid of stories: 2 cols x 4 rows
    gy = 396
    cell_w = (CW - 16) // 2
    cell_h = 118
    for idx, st in enumerate(STORIES):
        cx0 = M + (idx % 2) * (cell_w + 16)
        cy0 = gy + (idx // 2) * (cell_h + 10)
        rect(cx0, cy0, cell_w, cell_h, PAPER)
        hline(cx0, cy0, cell_w, INK, 2)
        # icon
        ICONS[st['icon']](cx0 + 30, cy0 + 34, RED if st['icon'] in ('burst', 'cloud') else BLUE)
        # tag
        draw_text(cx0 + 64, cy0 + 12, st['tag'], 2, RED)
        # headline
        hl = wrap(st['head'], cell_w - 80, 2)
        yy = cy0 + 32
        for ln in hl:
            draw_text(cx0 + 64, yy, ln, 2, INK)
            yy += 7 * 2 + 4
        # deck
        dl = wrap(st['deck'], cell_w - 16, 1)
        yy = cy0 + 82
        for ln in dl[:2]:
            draw_text(cx0 + 16, yy, ln, 1, GRAY)
            yy += 7 + 3

    # ---- ticker
    ty = gy + 4 * (cell_h + 10) + 6
    rect(M, ty, CW, 48, INK)
    tl = wrap(TICKER, CW - 24, 1)
    yy = ty + 9
    for ln in tl:
        draw_text(M + 12, yy, ln, 1, PAPER)
        yy += 7 + 4

    # ---- footer
    fy = ty + 48 + 12
    draw_center(M, fy, CW, 'Friday 27 November 2026', 2, INK)
    draw_center(M, fy + 24, CW,
                'Sources: New York Times, BBC, Reuters, NDTV, Newstalk ZB',
                1, GRAY)


# ---------------------------------------------------------------- PNG out
def chunk(kind, data):
    c = struct.pack('>I', len(data)) + kind + data
    c += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return c


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)


def main():
    draw()
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', 'out')
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, 'entry.png'))


if __name__ == '__main__':
    main()
