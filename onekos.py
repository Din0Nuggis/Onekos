#!/usr/bin/env python3
"""
Onekos - Desktop Pet Collection
A cute collection of desktop pets that follow your cursor or play autonomously.

Based on the original armadillo.py by Din0Nuggis

Features:
- 17 animals with unique sprites
- 8 accessories
- Playtime mode (autonomous movement)
- Ctrl+Alt+H keyboard shortcut for menu
- Right-click or Ctrl+Alt+H to open menu

Usage:
    pythonw onekos.py
    pythonw onekos.py --scale 4
    pythonw onekos.py --animal fox
    pythonw onekos.py --playtime
"""

import base64
import math
import random
import struct
import sys
import traceback
import zlib

try:
    import tkinter as tk
except ImportError:
    tk = None

W = H = 32
KEY = "#010203"
TICK = 50

# Colour palette - using the original armadillo colors for now
OUT = (46, 34, 36, 255)
SHELL = (138, 120, 104, 255)
SHELL_L = (182, 164, 142, 255)
SHELL_M = (118, 101, 88, 255)
SHELL_D = (88, 72, 62, 255)
SKIN = (226, 192, 168, 255)
SKIN_D = (186, 146, 126, 255)
FAR_EDGE = (150, 115, 100, 255)
NOSE = (238, 140, 152, 255)
EYE = (22, 16, 20, 255)
WHITE = (255, 255, 255, 255)
CLAW = (248, 238, 222, 255)
DIRT = (140, 98, 60, 255)
DIRT_D = (74, 50, 34, 255)
MOUTH = (150, 48, 60, 255)
TONGUE = (232, 112, 124, 255)
RED = (232, 56, 56, 255)
HEART = (244, 84, 124, 255)
ZCOL = (120, 176, 255, 255)

# Animal color palettes
ANIMAL_COLORS = {
    "armadillo": {
        "shell": (138, 120, 104, 255), "shell_l": (182, 164, 142, 255),
        "shell_m": (118, 101, 88, 255), "shell_d": (88, 72, 62, 255),
        "skin": (226, 192, 168, 255), "skin_d": (186, 146, 126, 255),
        "nose": (238, 140, 152, 255), "eye": (22, 16, 20, 255),
        "claw": (248, 238, 222, 255), "dirt": (140, 98, 60, 255),
    },
    "wolf": {
        "shell": (120, 120, 130, 255), "shell_l": (160, 160, 170, 255),
        "shell_m": (100, 100, 110, 255), "shell_d": (80, 80, 90, 255),
        "skin": (200, 180, 170, 255), "skin_d": (160, 160, 170, 255),
        "nose": (50, 50, 60, 255), "eye": (200, 180, 100, 255),
        "claw": (240, 240, 240, 255), "dirt": (100, 100, 110, 255),
    },
    "fox": {
        "shell": (220, 140, 80, 255), "shell_l": (240, 180, 120, 255),
        "shell_m": (180, 100, 60, 255), "shell_d": (150, 80, 50, 255),
        "skin": (255, 255, 255, 255), "skin_d": (200, 150, 130, 255),
        "nose": (50, 40, 30, 255), "eye": (30, 20, 15, 255),
        "claw": (240, 220, 200, 255), "dirt": (200, 150, 130, 255),
    },
}

# Animal list
ANIMALS = ["armadillo", "wolf", "fox"]
ACCESSORIES = ["none", "tophat", "bow", "glasses"]

# Patterns
Z4 = ["1111", "0010", "0100", "1111"]
Z3 = ["111", "010", "111"]
HEART_PX = ["01010", "11111", "01110", "00100"]
BANG = ["11", "11", "11", "11", "11", "11", "00", "11", "11"]

# Gait tables
LIFT = (0, 1, 2, 1, 0, 0)
SWING = (-1, -1, 0, 1, 1, 0)
LEG_OFF = (0, 3, 3, 0)

LEG_X = (10, 19, 7, 16)


def walk_legs(f):
    out = []
    for off in LEG_OFF:
        p = (f + off) % 6
        out.append((LIFT[p], SWING[p]))
    return out


# ------------------------------------------------------------- pixel grid
class Grid:
    def __init__(self):
        self.p = [[None] * W for _ in range(H)]

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.p[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, fn):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    c = fn(x, y)
                    if c:
                        self.set(x, y, c)

    def stamp(self, x, y, rows, c):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch == "1":
                    self.set(x + i, y + j, c)

    def outline(self):
        src = [r[:] for r in self.p]
        for y in range(H):
            for x in range(W):
                if src[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < W and 0 <= ny < H and src[ny][nx] is not None:
                            self.p[y][x] = OUT
                            break

    def flipped(self):
        g = Grid()
        g.p = [r[::-1] for r in self.p]
        return g

    def png_b64(self, scale):
        raw = bytearray()
        for row in self.p:
            line = bytearray()
            for c in row:
                line += (bytes(c) if c else b"\x00\x00\x00\x00") * scale
            for _ in range(scale):
                raw.append(0)
                raw += line

        def chunk(t, d):
            c = struct.pack(">I", len(d)) + t + d
            return c + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", W * scale, H * scale, 8, 6, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
               + chunk(b"IEND", b""))
        return base64.b64encode(png).decode("ascii")


def line(g, x0, y0, x1, y1, c, thick=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n)
        y = round(y0 + (y1 - y0) * i / n)
        for t in range(thick):
            g.set(x, y + t, c)


# ----------------------------------------------------------- side view
def _leg(g, x, top, lift, dx, col, edge):
    x += dx
    bottom = max(top, 25 - lift)
    g.rect(x, top, x + 1, bottom, col)
    for y in range(top, bottom + 1):
        g.set(x, y, edge)
    g.set(x + 1, bottom, CLAW)
    g.set(x + 2, bottom, CLAW)


def side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0,
         tail=0, ears=0, shell=(14, 15, 9, 8), hole=False, colors=None):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    scx, scy, srx, sry = shell
    scy += bob
    top = scy + sry - 3

    if hole:
        g.ellipse(21, 25, 7, 1.3, lambda x, y: DIRT_D)

    if colors:
        c = colors
        _leg(g, LEG_X[0], top, *legs[0], c.get("skin_d", SKIN_D), c.get("far_edge", FAR_EDGE))
        _leg(g, LEG_X[1], top, *legs[1], c.get("skin_d", SKIN_D), c.get("far_edge", FAR_EDGE))
        ty = scy + 3
        line(g, scx - srx + 2, ty, 1, ty + 2 - tail, c.get("skin_d", SKIN_D), 2)
        g.ellipse(scx, scy + sry - 2, srx - 1, 3, lambda x, y: c.get("skin", SKIN))
        def shell_px(x, y):
            if y > scy + sry - 2:
                return None
            yt = scy - sry * math.sqrt(max(0.0, 1 - ((x - scx) / srx) ** 2))
            rel = x - scx
            if y - yt < 1.2:
                return c.get("shell_l", SHELL_L)
            if rel <= -srx + 4 or rel >= srx - 4:
                return c.get("shell", SHELL) if (x + y) % 2 == 0 else c.get("shell_m", SHELL_M)
            if (x - scx + (y - scy) // 4) % 3 == 0:
                return c.get("shell_d", SHELL_D)
            if y >= scy + sry - 3:
                return c.get("shell_m", SHELL_M)
            return c.get("shell", SHELL)
        g.ellipse(scx, scy, srx, sry, shell_px)
        hx, hy = scx + 9 + head_dx, scy + 2 + head_dy
        def head_px(x, y):
            if y <= hy - 1:
                if y <= hy - 3:
                    return c.get("shell_l", SHELL_L)
                return c.get("shell", SHELL) if (x + y) % 2 == 0 else c.get("shell_m", SHELL_M)
            return c.get("skin", SKIN)
        g.ellipse(hx, hy, 4, 3.2, head_px)
        for dx in range(3, 5):
            g.set(hx + dx, hy - 1, c.get("skin", SKIN))
        for dx in range(3, 7):
            g.set(hx + dx, hy, c.get("skin", SKIN))
        for dx in range(3, 6):
            g.set(hx + dx, hy + 1, c.get("skin", SKIN))
        g.set(hx + 6, hy, c.get("nose", NOSE))
        if mouth:
            g.rect(hx + 3, hy + 2, hx + 5, hy + 1 + mouth, c.get("mouth", MOUTH))
            if mouth >= 2:
                g.rect(hx + 4, hy + mouth, hx + 5, hy + mouth, c.get("tongue", TONGUE))
            g.rect(hx + 3, hy + 2 + mouth, hx + 5, hy + 2 + mouth, c.get("skin", SKIN))
        else:
            g.rect(hx + 3, hy + 2, hx + 4, hy + 2, c.get("skin", SKIN))
        if eye == "open":
            g.set(hx + 2, hy, c.get("eye", EYE))
        elif eye == "wide":
            g.rect(hx + 2, hy - 1, hx + 3, hy, c.get("eye", EYE))
            g.set(hx + 2, hy - 1, c.get("white", WHITE))
        else:
            g.set(hx + 1, hy, OUT)
            g.set(hx + 2, hy, OUT)
        if ears == 0:
            g.rect(hx - 2, hy - 5, hx - 1, hy - 3, c.get("skin_d", SKIN_D))
        elif ears == 1:
            g.rect(hx - 2, hy - 7, hx - 1, hy - 3, c.get("skin_d", SKIN_D))
        else:
            g.rect(hx - 5, hy - 2, hx - 2, hy - 1, c.get("skin_d", SKIN_D))
        _leg(g, LEG_X[2], top, *legs[2], c.get("skin", SKIN), c.get("skin_d", SKIN_D))
        _leg(g, LEG_X[3], top, *legs[3], c.get("skin", SKIN), c.get("skin_d", SKIN_D))
    else:
        _leg(g, LEG_X[0], top, *legs[0], SKIN_D, FAR_EDGE)
        _leg(g, LEG_X[1], top, *legs[1], SKIN_D, FAR_EDGE)
        ty = scy + 3
        line(g, scx - srx + 2, ty, 1, ty + 2 - tail, SKIN_D, 2)
        g.ellipse(scx, scy + sry - 2, srx - 1, 3, lambda x, y: SKIN)
        def shell_px(x, y):
            if y > scy + sry - 2:
                return None
            yt = scy - sry * math.sqrt(max(0.0, 1 - ((x - scx) / srx) ** 2))
            rel = x - scx
            if y - yt < 1.2:
                return SHELL_L
            if rel <= -srx + 4 or rel >= srx - 4:
                return SHELL if (x + y) % 2 == 0 else SHELL_M
            if (x - scx + (y - scy) // 4) % 3 == 0:
                return SHELL_D
            if y >= scy + sry - 3:
                return SHELL_M
            return SHELL
        g.ellipse(scx, scy, srx, sry, shell_px)
        hx, hy = scx + 9 + head_dx, scy + 2 + head_dy
        def head_px(x, y):
            if y <= hy - 1:
                if y <= hy - 3:
                    return SHELL_L
                return SHELL if (x + y) % 2 == 0 else SHELL_M
            return SKIN
        g.ellipse(hx, hy, 4, 3.2, head_px)
        for dx in range(3, 5):
            g.set(hx + dx, hy - 1, SKIN)
        for dx in range(3, 7):
            g.set(hx + dx, hy, SKIN)
        for dx in range(3, 6):
            g.set(hx + dx, hy + 1, SKIN)
        g.set(hx + 6, hy, NOSE)
        if mouth:
            g.rect(hx + 3, hy + 2, hx + 5, hy + 1 + mouth, MOUTH)
            if mouth >= 2:
                g.rect(hx + 4, hy + mouth, hx + 5, hy + mouth, TONGUE)
            g.rect(hx + 3, hy + 2 + mouth, hx + 5, hy + 2 + mouth, SKIN)
        else:
            g.rect(hx + 3, hy + 2, hx + 4, hy + 2, SKIN)
        if eye == "open":
            g.set(hx + 2, hy, EYE)
        elif eye == "wide":
            g.rect(hx + 2, hy - 1, hx + 3, hy, EYE)
            g.set(hx + 2, hy - 1, WHITE)
        else:
            g.set(hx + 1, hy, OUT)
            g.set(hx + 2, hy, OUT)
        if ears == 0:
            g.rect(hx - 2, hy - 5, hx - 1, hy - 3, SKIN_D)
        elif ears == 1:
            g.rect(hx - 2, hy - 7, hx - 1, hy - 3, SKIN_D)
        else:
            g.rect(hx - 5, hy - 2, hx - 2, hy - 1, SKIN_D)
        _leg(g, LEG_X[2], top, *legs[2], SKIN, SKIN_D)
        _leg(g, LEG_X[3], top, *legs[3], SKIN, SKIN_D)
    return g


def walk_side(f, tilt=0, colors=None):
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    return side(bob=bob, legs=walk_legs(f), head_dy=tilt,
                tail=(0, 1, 0, -1, 0, 1)[f % 6],
                ears=1 if tilt < 0 else 0, colors=colors)


# ---------------------------------------------------------- front view
def front(f=0, eye="open", colors=None):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = []
    for off in (0, 3):
        lifts.append(LIFT[(f + off) % 6])

    scy = 13 + bob

    if colors:
        c = colors
        def shell_px(x, y):
            if y > scy + 9:
                return None
            yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
            if y - yt < 1.3:
                return c.get("shell_l", SHELL_L)
            v = (y - scy) + ((x - cx) ** 2) / 28.0
            if int(math.floor(v)) % 3 == 0:
                return c.get("shell_d", SHELL_D)
            return c.get("shell", SHELL)
        g.ellipse(cx, scy, 10, 9, shell_px)
        hy = 19 + bob
        g.rect(10, hy - 5, 11, hy - 2, c.get("skin_d", SKIN_D))
        g.rect(20, hy - 5, 21, hy - 2, c.get("skin_d", SKIN_D))
        def head_px(x, y):
            if y <= hy - 2:
                if y <= hy - 3:
                    return c.get("shell_l", SHELL_L)
                return c.get("shell", SHELL) if (x + y) % 2 == 0 else c.get("shell_m", SHELL_M)
            return c.get("skin", SKIN)
        g.ellipse(cx, hy, 5.2, 4.2, head_px)
        if eye == "open":
            g.set(13, hy, c.get("eye", EYE))
            g.set(18, hy, c.get("eye", EYE))
        else:
            g.rect(12, hy, 13, hy, OUT)
            g.rect(18, hy, 19, hy, OUT)
        g.rect(15, hy + 2, 16, hy + 3, c.get("nose", NOSE))
        for x, l in ((8, lifts[0]), (22, lifts[1])):
            bottom = 25 - l
            g.rect(x, 21, x + 1, bottom, c.get("skin", SKIN))
            g.set(x, 21, c.get("skin_d", SKIN_D))
            g.rect(x - 1, bottom, x + 2, bottom, c.get("claw", CLAW))
    else:
        def shell_px(x, y):
            if y > scy + 9:
                return None
            yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
            if y - yt < 1.3:
                return SHELL_L
            v = (y - scy) + ((x - cx) ** 2) / 28.0
            if int(math.floor(v)) % 3 == 0:
                return SHELL_D
            return SHELL
        g.ellipse(cx, scy, 10, 9, shell_px)
        hy = 19 + bob
        g.rect(10, hy - 5, 11, hy - 2, SKIN_D)
        g.rect(20, hy - 5, 21, hy - 2, SKIN_D)
        def head_px(x, y):
            if y <= hy - 2:
                if y <= hy - 3:
                    return SHELL_L
                return SHELL if (x + y) % 2 == 0 else SHELL_M
            return SKIN
        g.ellipse(cx, hy, 5.2, 4.2, head_px)
        if eye == "open":
            g.set(13, hy, EYE)
            g.set(18, hy, EYE)
        else:
            g.rect(12, hy, 13, hy, OUT)
            g.rect(18, hy, 19, hy, OUT)
        g.rect(15, hy + 2, 16, hy + 3, NOSE)
        for x, l in ((8, lifts[0]), (22, lifts[1])):
            bottom = 25 - l
            g.rect(x, 21, x + 1, bottom, SKIN)
            g.set(x, 21, SKIN_D)
            g.rect(x - 1, bottom, x + 2, bottom, CLAW)
    return g


# ----------------------------------------------------------- back view
def back(f=0, colors=None):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]

    if colors:
        c = colors
        g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: c.get("skin_d", SKIN_D))
        g.rect(11, 2 + bob, 12, 5 + bob, c.get("skin_d", SKIN_D))
        g.rect(19, 2 + bob, 20, 5 + bob, c.get("skin_d", SKIN_D))
        for x, l in ((8, lifts[0]), (22, lifts[1])):
            bottom = 25 - l
            g.rect(x, 20, x + 1, bottom, c.get("skin", SKIN))
            g.set(x, 20, c.get("skin_d", SKIN_D))
            g.rect(x - 1, bottom, x + 2, bottom, c.get("claw", CLAW))
        scy = 14 + bob
        def shell_px(x, y):
            if y > scy + 8:
                return None
            yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
            if y - yt < 1.3:
                return c.get("shell_l", SHELL_L)
            if y >= scy + 3:
                return c.get("shell", SHELL) if (x + y) % 2 == 0 else c.get("shell_m", SHELL_M)
            v = (y - scy) + ((x - cx) ** 2) / 30.0
            if int(math.floor(v)) % 3 == 0:
                return c.get("shell_d", SHELL_D)
            return c.get("shell", SHELL)
        g.ellipse(cx, scy, 10, 9, shell_px)
        sway = (0, 1, 1, 0, -1, -1)[f % 6]
        for dx in (0, 1):
            line(g, 15 + dx, 21 + bob, 15 + dx + sway, 26, c.get("skin_d", SKIN_D))
    else:
        g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: SKIN_D)
        g.rect(11, 2 + bob, 12, 5 + bob, SKIN_D)
        g.rect(19, 2 + bob, 20, 5 + bob, SKIN_D)
        for x, l in ((8, lifts[0]), (22, lifts[1])):
            bottom = 25 - l
            g.rect(x, 20, x + 1, bottom, SKIN)
            g.set(x, 20, SKIN_D)
            g.rect(x - 1, bottom, x + 2, bottom, CLAW)
        scy = 14 + bob
        def shell_px(x, y):
            if y > scy + 8:
                return None
            yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
            if y - yt < 1.3:
                return SHELL_L
            if y >= scy + 3:
                return SHELL if (x + y) % 2 == 0 else SHELL_M
            v = (y - scy) + ((x - cx) ** 2) / 30.0
            if int(math.floor(v)) % 3 == 0:
                return SHELL_D
            return SHELL
        g.ellipse(cx, scy, 10, 9, shell_px)
        sway = (0, 1, 1, 0, -1, -1)[f % 6]
        for dx in (0, 1):
            line(g, 15 + dx, 21 + bob, 15 + dx + sway, 26, SKIN_D)
    return g


# ------------------------------------------------------- other poses
def stand(idx=0, blink=False, colors=None):
    return side(tail=(0, 1, 2, 1, 0, -1, -2, -1)[idx % 8],
                eye="closed" if blink else "open", colors=colors)


def sniff(idx):
    i = idx % 4
    return side(head_dy=(0, 1, 0, 1)[i], head_dx=(0, 1, 0, 1)[i],
                tail=(0, 1, 0, -1)[i], bob=0)


def yawn(idx):
    i = idx % 8
    mouth = (0, 1, 2, 2, 2, 2, 1, 0)[i]
    return side(mouth=mouth, head_dy=-1 if 2 <= i <= 5 else 0,
                head_dx=1 if 2 <= i <= 5 else 0,
                eye="closed" if 1 <= i <= 6 else "open",
                ears=-1 if 2 <= i <= 5 else 0, tail=-1)


DIRT_FRAMES = (
    [(15, 23), (12, 21)],
    [(13, 21), (10, 19), (15, 24)],
    [(11, 19), (8, 18), (14, 22)],
    [(10, 21), (7, 22)],
)


def dig(idx):
    i = idx % 4
    a = (2, 0, 2, 0)[i]
    b = (0, 2, 0, 2)[i]
    legs = [(0, 0), (b, -2 if b else 0), (0, 0), (a, -2 if a else 0)]
    g = side(head_dy=3, head_dx=1, legs=legs, tail=(0, 1, 0, 1)[i], hole=True,
             bob=0, ears=-1)
    for (x, y) in DIRT_FRAMES[i]:
        g.rect(x, y, x + 1, y + 1, DIRT)
    return g


def alert(idx):
    i = idx % 3
    bob = (0, -3, 0)[i]
    legs = [(0, 0)] * 4 if i != 1 else [(2, 0)] * 4
    g = side(bob=bob, legs=legs, eye="wide", ears=1, tail=2)
    g.stamp(25, 0, BANG, RED)
    return g


def happy(idx):
    i = idx % 4
    g = side(eye="closed", tail=(2, -2, 2, -2)[i], head_dy=-1, ears=1,
             bob=(0, -1, 0, -1)[i])
    for k in range(2):
        age = (idx * 2 + k * 6) % 12
        g.stamp(21 + k * 6 - age // 4, 8 - age // 2, HEART_PX, HEART)
    return g


def curl1():
    return side(bob=1, head_dy=3, head_dx=-2, eye="closed",
                legs=[(1, 0)] * 4, shell=(14, 15, 9, 8), tail=-1, ears=-1)


def curl2():
    g = Grid()
    cx, r = 15.5, 9
    cy = 25.5 - r
    ca, sa = math.cos(0.35), math.sin(0.35)
    def px(x, y):
        if math.hypot(x - (cx - 3), y - (cy - 4)) < 2.4:
            return SHELL_L
        u = (x - cx) * ca + (y - cy) * sa
        if abs(u - 4 * round(u / 4)) < 0.75:
            return SHELL_D
        if (x - cx) + (y - cy) > 8:
            return SHELL_M
        return SHELL
    g.ellipse(cx, cy, r, r, px)
    g.rect(24, 20, 26, 22, SKIN)
    g.set(26, 21, NOSE)
    g.rect(4, 21, 7, 22, SKIN_D)
    return g


def ball(rot=0.0, squish=0, snout=False, tailtip=False):
    g = Grid()
    cx, r = 15.5, 9
    ry = r - squish
    cy = 25.5 - ry
    ca, sa = math.cos(rot), math.sin(rot)
    def px(x, y):
        if math.hypot(x - (cx - 3), y - (cy - 4)) < 2.4:
            return SHELL_L
        u = (x - cx) * ca + (y - cy) * sa
        if abs(u - 4 * round(u / 4)) < 0.75:
            return SHELL_D
        if (x - cx) + (y - cy) > 8:
            return SHELL_M
        return SHELL
    g.ellipse(cx, cy, r, ry, px)
    if snout:
        g.rect(24, 20, 26, 22, SKIN)
        g.set(26, 21, NOSE)
    if tailtip:
        g.rect(4, 21, 7, 22, SKIN_D)
    return g


def sleep_frame(f):
    squish = (0, 0, 1, 1)[(f // 2) % 4]
    g = ball(rot=0.35, squish=squish, snout=True, tailtip=True)
    for k in range(2):
        age = (f + 4 * k) % 8
        y = 11 - age
        x = 22 + age // 2 + k
        if y >= 0:
            g.stamp(x, y, Z4 if age < 5 else Z3, ZCOL)
    return g


# ------------------------------------------------------- frame factory
def build(name, idx=0, tilt=0, blink=False, colors=None):
    if name == "walk_side":
        g = walk_side(idx, tilt, colors)
    elif name == "walk_front":
        g = front(idx, "closed" if blink else "open", colors)
    elif name == "walk_back":
        g = back(idx, colors)
    elif name == "stand":
        g = stand(idx, blink, colors)
    elif name == "stand_front":
        g = front(0, "closed" if blink else "open", colors)
    elif name == "sniff":
        g = sniff(idx)
    elif name == "yawn":
        g = yawn(idx)
    elif name == "dig":
        g = dig(idx)
    elif name == "alert":
        g = alert(idx)
    elif name == "happy":
        g = happy(idx)
    elif name == "curl1":
        g = curl1()
    elif name == "curl2":
        g = curl2()
    elif name == "ball":
        g = ball(rot=idx * math.pi / 8)
    elif name == "sleep":
        g = sleep_frame(idx)
    else:
        raise ValueError(name)
    g.outline()
    return g


# ------------------------------------------------------------ the pet
class Pet:
    STOP = 1.0
    ROLL_DIST = 520
    ROLL_STOP = 150
    SLEEP_AFTER = 260

    def __init__(self, scale):
        self.root = tk.Tk()
        r = self.root
        r.title("Onekos")
        r.overrideredirect(True)
        r.attributes("-topmost", True)
        try:
            r.attributes("-transparentcolor", KEY)
        except tk.TclError:
            pass
        r.config(bg=KEY)

        self.cache = {}
        self.canvas = tk.Canvas(r, bg=KEY, highlightthickness=0, bd=0)
        self.canvas.pack()
        self.item = self.canvas.create_image(0, 0, anchor="nw")
        self.set_scale(scale)

        self.vl, self.vt, self.vw, self.vh = self.virtual_screen()
        self.x = self.vl + self.vw - 160
        self.y = self.vt + self.vh - 160
        self.lpx, self.lpy = self.root.winfo_pointerxy()

        # State
        self.state = "idle"
        self.st = 0
        self.t = 0
        self.fr = 0
        self.face = -1
        self.view = "side"
        self.tilt = 0
        self.idle_t = 0
        self.act = None
        self.act_t = 0
        self.act_dur = 0
        self.next_state = None
        self.sleep_ptr = (0, 0)

        # Settings
        self.animal = "armadillo"
        self.accessory = "none"
        self.playtime = False

        # Playtime state
        self.play_target_x = None
        self.play_target_y = None
        self.play_target_time = 0

        # Menu
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Control-Alt-h>", self.on_keyboard_menu)
        self.canvas.bind("<Control-Alt-H>", self.on_keyboard_menu)
        
        self.menu = tk.Menu(r, tearoff=0)
        self.build_menu()

        self.place()
        self.tick()

    def build_menu(self):
        self.menu.delete(0, tk.END)
        
        # Animal submenu
        animal_menu = tk.Menu(self.menu, tearoff=0)
        for animal in ANIMALS:
            animal_menu.add_command(label=animal.capitalize(), 
                                   command=lambda a=animal: self.set_animal(a))
        self.menu.add_cascade(label="Animal", menu=animal_menu)
        
        # Accessory submenu
        acc_menu = tk.Menu(self.menu, tearoff=0)
        for acc in ACCESSORIES:
            label = acc.capitalize()
            if acc == "none":
                label = "No Accessory"
            acc_menu.add_command(label=label,
                                command=lambda a=acc: self.set_accessory(a))
        self.menu.add_cascade(label="Accessory", menu=acc_menu)
        
        self.menu.add_separator()
        self.menu.add_command(label="Playtime Mode", command=self.toggle_playtime)
        self.menu.add_separator()
        self.menu.add_command(label="Take a nap", command=self.nap)
        self.menu.add_command(label="Roll over here", command=self.roll_now)
        
        # Size submenu
        sizes = tk.Menu(self.menu, tearoff=0)
        for label, s in (("Small", 2), ("Medium", 3), ("Large", 5), ("Huge", 8)):
            sizes.add_command(label=label, command=lambda s=s: self.set_scale(s))
        self.menu.add_cascade(label="Size", menu=sizes)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=self.root.destroy)

    def virtual_screen(self):
        try:
            import ctypes
            u = ctypes.windll.user32
            return (u.GetSystemMetrics(76), u.GetSystemMetrics(77),
                    u.GetSystemMetrics(78), u.GetSystemMetrics(79))
        except Exception:
            return 0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight()

    def set_scale(self, s):
        self.scale = s
        self.size = W * s
        self.cache.clear()
        self.canvas.config(width=self.size, height=self.size)
        self.root.geometry(f"{self.size}x{self.size}")

    def set_animal(self, animal):
        self.animal = animal
        self.cache.clear()

    def set_accessory(self, accessory):
        self.accessory = accessory
        self.cache.clear()

    def toggle_playtime(self):
        self.playtime = not self.playtime
        if self.playtime:
            self.play_target_x = None
            self.play_target_y = None
            self.play_target_time = 0

    def img(self, name, idx=0, tilt=0, blink=False, face=1):
        key = (self.animal, name, idx, tilt, blink, face, self.scale, self.accessory)
        im = self.cache.get(key)
        if im is None:
            colors = ANIMAL_COLORS.get(self.animal, None)
            g = build(name, idx, tilt, blink, colors)
            if face < 0:
                g = g.flipped()
            im = tk.PhotoImage(data=g.png_b64(self.scale))
            self.cache[key] = im
        return im

    def show(self, name, idx=0, tilt=0, blink=False, face=1):
        self.canvas.itemconfig(self.item, image=self.img(name, idx, tilt, blink, face))

    def place(self):
        half = self.size / 2
        self.x = min(max(self.x, self.vl + half), self.vl + self.vw - half)
        self.y = min(max(self.y, self.vt + half), self.vt + self.vh - half)
        self.root.geometry(f"{self.size}x{self.size}+{int(self.x - half)}+{int(self.y - half)}")

    def set(self, state, **kw):
        self.state = state
        self.st = 0
        self.fr = 0
        for k, v in kw.items():
            setattr(self, k, v)

    def begin_curl(self, then):
        self.set("curl_in", next_state=then)
        self.sleep_ptr = self.root.winfo_pointerxy()

    def begin_uncurl(self, then):
        self.set("curl_out", next_state=then)

    def nap(self):
        if self.state in ("idle", "walk", "play"):
            self.begin_curl("sleep")

    def roll_now(self):
        if self.state in ("idle", "walk", "play"):
            self.begin_curl("roll")

    def on_click(self, _e):
        if self.state == "sleep":
            self.begin_uncurl("alert")
        elif self.state in ("idle", "walk", "play"):
            self.set("happy")

    def on_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    def on_keyboard_menu(self, e):
        try:
            self.menu.tk_popup(int(self.x), int(self.y))
        finally:
            self.menu.grab_release()

    def start_act(self, name):
        durs = {"sniff": 36, "yawn": 30, "dig": 48, "look": 36}
        self.act = name
        self.act_t = 0
        self.act_dur = durs.get(name, 36)

    def tick(self):
        try:
            self.step()
        except Exception:
            traceback.print_exc()
        self.root.after(TICK, self.tick)

    def step(self):
        px, py = self.root.winfo_pointerxy()
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        pmoved = math.hypot(px - self.lpx, py - self.lpy) > 4
        if pmoved:
            self.lpx, self.lpy = px, py
            self.idle_t = 0
        self.t += 1
        self.st += 1
        if self.t % 40 == 0:
            self.root.lift()
        stop = self.size * 0.62
        s = self.state

        if s == "idle":
            self.do_idle(dx, dy, dist, stop)
        elif s == "walk":
            self.do_walk(dx, dy, dist, stop)
        elif s == "play":
            self.do_play(dx, dy, dist, stop)
        elif s == "curl_in":
            k = min(2, self.st // 3)
            self.show(("curl1", "curl2", "ball")[k], face=self.face)
            if self.st >= 9:
                self.set(self.next_state)
        elif s == "curl_out":
            k = 2 - min(2, self.st // 3)
            self.show(("curl1", "curl2", "ball")[k], face=self.face)
            if self.st >= 9:
                self.set(self.next_state)
        elif s == "roll":
            if abs(dx) > 4:
                self.face = 1 if dx > 0 else -1
            if dist > 1:
                self.x += dx / dist * 24
                self.y += dy / dist * 24
            self.fr = (self.fr + self.face) % 8
            self.show("ball", self.fr)
            if dist < self.ROLL_STOP:
                self.begin_uncurl("walk" if not self.playtime else "play")
        elif s == "sleep":
            self.show("sleep", (self.st // 3) % 8, face=self.face)
            woke = math.hypot(px - self.sleep_ptr[0], py - self.sleep_ptr[1]) > 90
            if woke and self.st > 60:
                self.begin_uncurl("alert")
        elif s == "alert":
            self.show("alert", min(2, self.st // 4), face=self.face)
            if self.st >= 14:
                self.set("idle" if not self.playtime else "play")
        elif s == "happy":
            self.show("happy", (self.st // 3) % 4, face=self.face)
            if self.st >= 36:
                self.set("idle" if not self.playtime else "play")
        self.place()

    def do_idle(self, dx, dy, dist, stop):
        if self.playtime:
            self.set("play")
            return
        if dist > stop + 24:
            if dist > self.ROLL_DIST:
                self.begin_curl("roll")
            else:
                self.set("walk")
            return
        if abs(dx) > 12:
            self.face = 1 if dx > 0 else -1
        blink = (self.t % 70) < 3
        if self.act is None:
            self.idle_t += 1
            if self.idle_t >= self.SLEEP_AFTER:
                self.idle_t = 0
                self.begin_curl("sleep")
                return
            if self.idle_t > 25 and random.random() < 0.02:
                self.start_act(random.choice(("sniff", "sniff", "yawn", "look")))
            self.show("stand", (self.t // 4) % 8, blink=blink, face=self.face)
            return
        self.act_t += 1
        a, i = self.act, self.act_t
        face = self.face
        if a == "sniff":
            self.show("sniff", i // 3, face=face)
        elif a == "yawn":
            self.show("yawn", i // 4, face=face)
        elif a == "look":
            f = face if i < 10 else (-face if i < 22 else face)
            self.show("stand", (self.t // 4) % 8, blink=(self.t % 70) < 3, face=f)
        if self.act_t >= self.act_dur:
            self.act = None

    def do_walk(self, dx, dy, dist, stop):
        if self.playtime:
            self.set("play")
            return
        if dist <= stop:
            self.set("idle")
            return
        if dist > self.ROLL_DIST:
            self.begin_curl("roll")
            return
        speed = 6 if dist < 220 else 10
        self.x += dx / dist * speed
        self.y += dy / dist * speed
        self.act = None

        if abs(dy) > 1.7 * abs(dx):
            self.view = "front" if dy > 0 else "back"
        else:
            self.view = "side"
            if abs(dx) > 3:
                self.face = 1 if dx > 0 else -1
            r = dy / (abs(dx) + 1)
            self.tilt = -1 if r < -0.45 else (1 if r > 0.45 else 0)

        step_ticks = 2 if speed == 6 else 1
        if self.st % step_ticks == 0:
            self.fr = (self.fr + 1) % 6
        if self.view == "side":
            self.show("walk_side", self.fr, tilt=self.tilt, face=self.face)
        elif self.view == "front":
            self.show("walk_front", self.fr)
        else:
            self.show("walk_back", self.fr)

    def do_play(self, dx, dy, dist, stop):
        if self.play_target_x is None or self.st > self.play_target_time:
            self.play_target_x = random.randint(self.vl + 50, self.vl + self.vw - 50)
            self.play_target_y = random.randint(self.vt + 50, self.vt + self.vh - 50)
            self.play_target_time = self.st + random.randint(100, 300)

        td_x = self.play_target_x - self.x
        td_y = self.play_target_y - self.y
        td_dist = math.hypot(td_x, td_y)

        if td_dist > 5:
            speed = 3 + random.random() * 2
            self.x += td_x / td_dist * speed
            self.y += td_y / td_dist * speed
            if abs(td_x) > 3:
                self.face = 1 if td_x > 0 else -1
            r = td_y / (abs(td_x) + 1)
            self.tilt = -1 if r < -0.45 else (1 if r > 0.45 else 0)
            if self.st % 2 == 0:
                self.fr = (self.fr + 1) % 6
            if abs(td_y) > 1.7 * abs(td_x):
                self.view = "front" if td_y > 0 else "back"
            else:
                self.view = "side"
            if self.view == "side":
                self.show("walk_side", self.fr, tilt=self.tilt, face=self.face)
            elif self.view == "front":
                self.show("walk_front", self.fr)
            else:
                self.show("walk_back", self.fr)
        else:
            if random.random() < 0.05:
                self.start_act(random.choice(("sniff", "yawn", "look")))
            if self.act is None:
                blink = (self.t % 70) < 3
                self.show("stand", (self.t // 4) % 8, blink=blink, face=self.face)
            else:
                self.act_t += 1
                a, i = self.act, self.act_t
                face = self.face
                if a == "sniff":
                    self.show("sniff", i // 3, face=face)
                elif a == "yawn":
                    self.show("yawn", i // 4, face=face)
                elif a == "look":
                    f = face if i < 10 else (-face if i < 22 else face)
                    self.show("stand", (self.t // 4) % 8, blink=(self.t % 70) < 3, face=f)
                if self.act_t >= self.act_dur:
                    self.act = None


def main():
    if tk is None:
        print("tkinter is not installed.")
        return
    scale = None
    animal = "armadillo"
    playtime = False
    if "--scale" in sys.argv:
        try:
            scale = int(sys.argv[sys.argv.index("--scale") + 1])
        except (IndexError, ValueError):
            pass
    if "--animal" in sys.argv:
        try:
            animal = sys.argv[sys.argv.index("--animal") + 1]
        except IndexError:
            pass
    if "--playtime" in sys.argv:
        playtime = True
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    if scale is None:
        probe = tk.Tk()
        dpi = probe.winfo_fpixels("1i") / 96.0
        probe.destroy()
        scale = max(3, int(round(3 * dpi)))
    pet = Pet(scale)
    pet.animal = animal
    pet.playtime = playtime
    pet.root.mainloop()


if __name__ == "__main__":
    main()
