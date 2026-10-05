#!/usr/bin/env python3
"""
Onekos - Desktop Pet Collection
A complete desktop pet with animals, accessories, and fun features!

Features:
- 17 unique animals with their own sprite sheets
- 8 accessories that fit naturally on each animal
- Playtime mode (autonomous wandering)
- Ctrl+Alt+H keyboard shortcut
- Right-click menu
- Google Docs typing detection (checks URL)
- Customizable size

Usage:
    pythonw onekos.py
    pythonw onekos.py --scale 4
    pythonw onekos.py --animal fox
    pythonw onekos.py --playtime

Left click   : pet the animal
Right click  : menu
Ctrl+Alt+H   : open menu
"""
import base64
import math
import random
import struct
import sys
import time
import threading
import traceback
import zlib

try:
    import tkinter as tk
except ImportError:  # lets the sprite code be imported on machines without Tk
    tk = None

W = H = 32
KEY = "#010203"          # window transparency key colour
TICK = 50                # ms per simulation step

# ---------------------------------------------------------------- palette
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

# Accessory colors
AP = {
    "tophat": (50, 50, 50, 255),
    "bow": (255, 100, 150, 255),
    "glasses": (200, 200, 200, 255),
    "crown": (255, 215, 0, 255),
    "flower": (255, 100, 200, 255),
    "santa": (255, 0, 0, 255),
    "witch": (100, 50, 150, 255),
    "witch_brim": (50, 25, 75, 255),
}


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


Z4 = ["1111", "0010", "0100", "1111"]
Z3 = ["111", "010", "111"]
HEART_PX = ["01010", "11111", "01110", "00100"]
BANG = ["11", "11", "11", "11", "11", "11", "00", "11", "11"]


# ================================================================
# UNIQUE SPRITE FUNCTIONS FOR EACH ANIMAL
# Each animal has its own distinct silhouette and features
# ================================================================

# ----------------------------------------------------------- Armadillo
def armadillo_side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0, tail=0, ears=0, shell=(14, 15, 9, 8), hole=False):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    scx, scy, srx, sry = shell
    scy += bob
    top = scy + sry - 3

    if hole:
        g.ellipse(21, 25, 7, 1.3, lambda x, y: DIRT_D)

    # Legs
    LEG_X = (10, 19, 7, 16)
    for i, lx in enumerate(LEG_X):
        x = lx + (0 if i < 2 else 0)
        bottom = max(top, 25 - legs[i][1])
        col = SKIN_D if i < 2 else SKIN
        edge = FAR_EDGE if i < 2 else SKIN_D
        g.rect(x, top, x + 1, bottom, col)
        for y in range(top, bottom + 1):
            g.set(x, y, edge)
        g.set(x + 1, bottom, CLAW)
        g.set(x + 2, bottom, CLAW)

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
    return g


def armadillo_front(f=0, eye="open"):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    scy = 13 + bob

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


def armadillo_back(f=0):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]

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


# ----------------------------------------------------------- Wolf
def wolf_side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0, tail=0, ears=0):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    
    # Body - wolf shape (longer, furry)
    g.ellipse(15, 15 + bob, 10, 6, lambda x, y: (120, 120, 120, 255))
    g.ellipse(15, 14 + bob, 10, 7, lambda x, y: (100, 100, 100, 255))
    
    # Head - wolf head with pointed ears
    hx, hy = 22 + head_dx, 12 + head_dy + bob
    g.ellipse(hx, hy, 5, 4, lambda x, y: (150, 150, 150, 255))
    
    # Ears - pointed
    g.rect(hx - 2, hy - 6, hx - 1, hy - 2, (130, 130, 130, 255))
    g.rect(hx + 1, hy - 6, hx + 2, hy - 2, (130, 130, 130, 255))
    
    # Snout
    for dx in range(-2, 4):
        g.set(hx + dx, hy + 1, (180, 180, 180, 255))
        g.set(hx + dx, hy + 2, (180, 180, 180, 255))
    g.set(hx + 3, hy + 1, (80, 80, 80, 255))  # nose
    
    # Eye
    if eye == "open":
        g.set(hx, hy - 1, (255, 255, 0, 255))
        g.set(hx + 1, hy - 1, (255, 255, 0, 255))
    else:
        g.rect(hx, hy - 1, hx + 1, hy - 1, OUT)
    
    # Legs
    LEG_X_WOLF = (8, 18, 5, 15)
    for i, lx in enumerate(LEG_X_WOLF):
        x = lx + (0 if i < 2 else 0)
        bottom = max(20 + bob, 25 - legs[i][1])
        g.rect(x, 20 + bob, x + 2, bottom, (140, 140, 140, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (200, 200, 200, 255))
    
    # Tail - bushy
    ty = 15 + bob
    line(g, 5, ty, 2, ty + 5 - tail, (100, 100, 100, 255), 3)
    
    if mouth:
        g.rect(hx + 1, hy + 3, hx + 3, hy + 3 + mouth, (200, 50, 50, 255))
    
    return g


def wolf_front(f=0, eye="open"):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    # Body
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (120, 120, 120, 255))
    
    # Head
    hy = 10 + bob
    g.ellipse(cx, hy, 6, 5, lambda x, y: (150, 150, 150, 255))
    
    # Ears
    g.rect(10, hy - 6, 12, hy - 2, (130, 130, 130, 255))
    g.rect(19, hy - 6, 21, hy - 2, (130, 130, 130, 255))
    
    # Eyes
    if eye == "open":
        g.set(12, hy, (255, 255, 0, 255))
        g.set(19, hy, (255, 255, 0, 255))
    else:
        g.rect(11, hy, 13, hy, OUT)
        g.rect(18, hy, 20, hy, OUT)
    
    # Nose
    g.rect(15, hy + 2, 16, hy + 3, (80, 80, 80, 255))
    
    # Legs
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 2, bottom, (140, 140, 140, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (200, 200, 200, 255))
    
    return g


def wolf_back(f=0):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    # Head peeking
    g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: (150, 150, 150, 255))
    g.rect(11, 2 + bob, 12, 5 + bob, (130, 130, 130, 255))
    g.rect(19, 2 + bob, 20, 5 + bob, (130, 130, 130, 255))
    
    # Body
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (120, 120, 120, 255))
    
    # Legs
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 2, bottom, (140, 140, 140, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (200, 200, 200, 255))
    
    # Tail
    sway = (0, 1, 1, 0, -1, -1)[f % 6]
    line(g, 15, 20 + bob, 15 + sway, 25, (100, 100, 100, 255), 3)
    
    return g


# ----------------------------------------------------------- Fox
def fox_side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0, tail=0, ears=0):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    
    # Body - orange/red
    g.ellipse(15, 15 + bob, 10, 6, lambda x, y: (200, 100, 50, 255))
    g.ellipse(15, 14 + bob, 10, 7, lambda x, y: (180, 80, 30, 255))
    
    # Head
    hx, hy = 22 + head_dx, 12 + head_dy + bob
    g.ellipse(hx, hy, 5, 4, lambda x, y: (220, 120, 70, 255))
    
    # Ears - pointed, fox-like
    g.rect(hx - 2, hy - 6, hx - 1, hy - 2, (180, 80, 30, 255))
    g.rect(hx + 1, hy - 6, hx + 2, hy - 2, (180, 80, 30, 255))
    g.set(hx - 2, hy - 6, (255, 255, 255, 255))  # ear tips
    g.set(hx + 2, hy - 6, (255, 255, 255, 255))
    
    # Snout - white
    for dx in range(-2, 4):
        g.set(hx + dx, hy + 1, (255, 255, 255, 255))
        g.set(hx + dx, hy + 2, (255, 255, 255, 255))
    g.set(hx + 3, hy + 1, (50, 50, 50, 255))  # nose
    
    # Eye
    if eye == "open":
        g.set(hx, hy - 1, EYE)
    else:
        g.rect(hx, hy - 1, hx + 1, hy - 1, OUT)
    
    # Legs
    LEG_X_FOX = (8, 18, 5, 15)
    for i, lx in enumerate(LEG_X_FOX):
        x = lx
        bottom = max(20 + bob, 25 - legs[i][1])
        g.rect(x, 20 + bob, x + 2, bottom, (180, 80, 30, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (240, 240, 240, 255))
    
    # Tail - bushy
    ty = 15 + bob
    line(g, 5, ty, 2, ty + 5 - tail, (180, 80, 30, 255), 3)
    g.rect(1, ty + 3, 4, ty + 5, (255, 255, 255, 255))  # tail tip
    
    if mouth:
        g.rect(hx + 1, hy + 3, hx + 3, hy + 3 + mouth, (200, 50, 50, 255))
    
    return g


def fox_front(f=0, eye="open"):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (200, 100, 50, 255))
    
    hy = 10 + bob
    g.ellipse(cx, hy, 6, 5, lambda x, y: (220, 120, 70, 255))
    
    g.rect(10, hy - 6, 12, hy - 2, (180, 80, 30, 255))
    g.rect(19, hy - 6, 21, hy - 2, (180, 80, 30, 255))
    g.set(10, hy - 6, (255, 255, 255, 255))
    g.set(21, hy - 6, (255, 255, 255, 255))
    
    if eye == "open":
        g.set(12, hy, EYE)
        g.set(19, hy, EYE)
    else:
        g.rect(11, hy, 13, hy, OUT)
        g.rect(18, hy, 20, hy, OUT)
    
    g.rect(15, hy + 2, 16, hy + 3, (50, 50, 50, 255))
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 2, bottom, (180, 80, 30, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (240, 240, 240, 255))
    
    return g


def fox_back(f=0):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: (220, 120, 70, 255))
    g.rect(11, 2 + bob, 12, 5 + bob, (180, 80, 30, 255))
    g.rect(19, 2 + bob, 20, 5 + bob, (180, 80, 30, 255))
    g.set(11, 2 + bob, (255, 255, 255, 255))
    g.set(20, 2 + bob, (255, 255, 255, 255))
    
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (200, 100, 50, 255))
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 2, bottom, (180, 80, 30, 255))
        g.rect(x - 1, bottom, x + 3, bottom, (240, 240, 240, 255))
    
    sway = (0, 1, 1, 0, -1, -1)[f % 6]
    line(g, 15, 20 + bob, 15 + sway, 25, (180, 80, 30, 255), 3)
    g.rect(15 + sway - 1, 23, 15 + sway + 1, 25, (255, 255, 255, 255))
    
    return g


# ----------------------------------------------------------- Cat
def cat_side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0, tail=0, ears=0):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    
    # Body
    g.ellipse(15, 15 + bob, 10, 6, lambda x, y: (200, 180, 160, 255))
    
    # Head
    hx, hy = 22 + head_dx, 12 + head_dy + bob
    g.ellipse(hx, hy, 5, 4, lambda x, y: (220, 200, 180, 255))
    
    # Ears - cat ears
    g.rect(hx - 2, hy - 6, hx - 1, hy - 2, (200, 180, 160, 255))
    g.rect(hx + 1, hy - 6, hx + 2, hy - 2, (200, 180, 160, 255))
    g.set(hx - 2, hy - 6, (180, 160, 140, 255))
    g.set(hx + 2, hy - 6, (180, 160, 140, 255))
    
    # Snout
    for dx in range(-2, 3):
        g.set(hx + dx, hy + 1, (230, 210, 190, 255))
        g.set(hx + dx, hy + 2, (230, 210, 190, 255))
    g.set(hx + 2, hy + 1, (255, 150, 150, 255))  # nose
    
    # Eye
    if eye == "open":
        g.set(hx, hy - 1, (255, 255, 0, 255))
    else:
        g.rect(hx, hy - 1, hx + 1, hy - 1, OUT)
    
    # Legs
    LEG_X_CAT = (9, 17, 6, 14)
    for i, lx in enumerate(LEG_X_CAT):
        x = lx
        bottom = max(20 + bob, 25 - legs[i][1])
        g.rect(x, 20 + bob, x + 1, bottom, (180, 160, 140, 255))
        g.rect(x - 1, bottom, x + 2, bottom, (240, 240, 240, 255))
    
    # Tail - long and thin
    ty = 15 + bob
    line(g, 5, ty, 1, ty + 6 - tail, (200, 180, 160, 255), 2)
    
    if mouth:
        g.rect(hx, hy + 3, hx + 2, hy + 3 + mouth, (200, 100, 100, 255))
    
    # Whiskers
    if eye == "open":
        g.set(hx - 3, hy, (255, 255, 255, 255))
        g.set(hx - 4, hy, (255, 255, 255, 255))
        g.set(hx + 4, hy, (255, 255, 255, 255))
        g.set(hx + 5, hy, (255, 255, 255, 255))
    
    return g


def cat_front(f=0, eye="open"):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (200, 180, 160, 255))
    
    hy = 10 + bob
    g.ellipse(cx, hy, 6, 5, lambda x, y: (220, 200, 180, 255))
    
    g.rect(10, hy - 6, 12, hy - 2, (200, 180, 160, 255))
    g.rect(19, hy - 6, 21, hy - 2, (200, 180, 160, 255))
    g.set(10, hy - 6, (180, 160, 140, 255))
    g.set(21, hy - 6, (180, 160, 140, 255))
    
    if eye == "open":
        g.set(12, hy, (255, 255, 0, 255))
        g.set(19, hy, (255, 255, 0, 255))
    else:
        g.rect(11, hy, 13, hy, OUT)
        g.rect(18, hy, 20, hy, OUT)
    
    g.rect(15, hy + 2, 16, hy + 3, (255, 150, 150, 255))
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 1, bottom, (180, 160, 140, 255))
        g.rect(x - 1, bottom, x + 2, bottom, (240, 240, 240, 255))
    
    # Whiskers
    g.set(8, hy, (255, 255, 255, 255))
    g.set(7, hy, (255, 255, 255, 255))
    g.set(9, hy, (255, 255, 255, 255))
    g.set(22, hy, (255, 255, 255, 255))
    g.set(21, hy, (255, 255, 255, 255))
    g.set(23, hy, (255, 255, 255, 255))
    
    return g


def cat_back(f=0):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: (220, 200, 180, 255))
    g.rect(11, 2 + bob, 12, 5 + bob, (200, 180, 160, 255))
    g.rect(19, 2 + bob, 20, 5 + bob, (200, 180, 160, 255))
    g.set(11, 2 + bob, (180, 160, 140, 255))
    g.set(20, 2 + bob, (180, 160, 140, 255))
    
    g.ellipse(cx, 15 + bob, 10, 7, lambda x, y: (200, 180, 160, 255))
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 1, bottom, (180, 160, 140, 255))
        g.rect(x - 1, bottom, x + 2, bottom, (240, 240, 240, 255))
    
    sway = (0, 1, 1, 0, -1, -1)[f % 6]
    line(g, 15, 20 + bob, 15 + sway, 26, (200, 180, 160, 255), 2)
    
    return g


# Gait tables (6 frames)
LIFT = (0, 1, 2, 1, 0, 0)
SWING = (-1, -1, 0, 1, 1, 0)
LEG_OFF = (0, 3, 3, 0)


def walk_legs(f):
    out = []
    for off in LEG_OFF:
        p = (f + off) % 6
        out.append((LIFT[p], SWING[p]))
    return out


# ================================================================
# ANIMAL SPRITE REGISTRY
# ================================================================

# Map animal names to their sprite functions
ANIMAL_SPRITES = {
    "armadillo": {
        "side": armadillo_side,
        "front": armadillo_front,
        "back": armadillo_back,
    },
    "wolf": {
        "side": wolf_side,
        "front": wolf_front,
        "back": wolf_back,
    },
    "fox": {
        "side": fox_side,
        "front": fox_front,
        "back": fox_back,
    },
    "cat": {
        "side": cat_side,
        "front": cat_front,
        "back": cat_back,
    },
}

# For animals not yet with unique sprites, use generic functions with color palettes
# We'll add more unique sprites below


def generic_side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0, tail=0, ears=0, colors=None):
    """Generic side view for animals without unique sprites yet"""
    g = Grid()
    legs = legs or [(0, 0)] * 4
    
    body_c, body_l, body_m, body_d = colors["body"], colors["body_l"], colors["body_m"], colors["body_d"]
    skin_c, skin_d, nose_c, eye_c, claw_c = colors["skin"], colors["skin_d"], colors["nose"], colors["eye"], colors["claw"]
    
    scx, scy = 15, 15 + bob
    srx, sry = 9, 8
    top = scy + sry - 3
    
    # Body
    def shell_px(x, y):
        if y > scy + sry - 2:
            return None
        yt = scy - sry * math.sqrt(max(0.0, 1 - ((x - scx) / srx) ** 2))
        rel = x - scx
        if y - yt < 1.2:
            return body_l
        if rel <= -srx + 4 or rel >= srx - 4:
            return body_c if (x + y) % 2 == 0 else body_m
        if (x - scx + (y - scy) // 4) % 3 == 0:
            return body_d
        if y >= scy + sry - 3:
            return body_m
        return body_c
    g.ellipse(scx, scy, srx, sry, shell_px)
    
    # Belly
    g.ellipse(scx, scy + sry - 2, srx - 1, 3, lambda x, y: skin_c)
    
    # Head
    hx, hy = scx + 9 + head_dx, scy + 2 + head_dy
    def head_px(x, y):
        if y <= hy - 1:
            if y <= hy - 3:
                return body_l
            return body_c if (x + y) % 2 == 0 else body_m
        return skin_c
    g.ellipse(hx, hy, 4, 3.2, head_px)
    
    # Snout
    for dx in range(3, 5):
        g.set(hx + dx, hy - 1, skin_c)
    for dx in range(3, 7):
        g.set(hx + dx, hy, skin_c)
    for dx in range(3, 6):
        g.set(hx + dx, hy + 1, skin_c)
    g.set(hx + 6, hy, nose_c)
    
    # Eye
    if eye == "open":
        g.set(hx + 2, hy, eye_c)
    elif eye == "wide":
        g.rect(hx + 2, hy - 1, hx + 3, hy, eye_c)
        g.set(hx + 2, hy - 1, WHITE)
    else:
        g.set(hx + 1, hy, OUT)
        g.set(hx + 2, hy, OUT)
    
    # Ears
    if ears == 0:
        g.rect(hx - 2, hy - 5, hx - 1, hy - 3, skin_d)
    elif ears == 1:
        g.rect(hx - 2, hy - 7, hx - 1, hy - 3, skin_d)
    else:
        g.rect(hx - 5, hy - 2, hx - 2, hy - 1, skin_d)
    
    # Legs
    LEG_X = (10, 19, 7, 16)
    for i, lx in enumerate(LEG_X):
        x = lx
        bottom = max(top, 25 - legs[i][1])
        col = skin_d if i < 2 else skin_c
        edge = FAR_EDGE if i < 2 else skin_d
        g.rect(x, top, x + 1, bottom, col)
        for y in range(top, bottom + 1):
            g.set(x, y, edge)
        g.set(x + 1, bottom, claw_c)
        g.set(x + 2, bottom, claw_c)
    
    # Tail
    ty = scy + 3
    line(g, scx - srx + 2, ty, 1, ty + 2 - tail, skin_d, 2)
    
    if mouth:
        g.rect(hx + 3, hy + 2, hx + 5, hy + 1 + mouth, MOUTH)
        if mouth >= 2:
            g.rect(hx + 4, hy + mouth, hx + 5, hy + mouth, TONGUE)
        g.rect(hx + 3, hy + 2 + mouth, hx + 5, hy + 2 + mouth, skin_c)
    else:
        g.rect(hx + 3, hy + 2, hx + 4, hy + 2, skin_c)
    
    return g


def generic_front(f=0, eye="open", colors=None):
    """Generic front view"""
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    body_c, body_l, body_m, body_d = colors["body"], colors["body_l"], colors["body_m"], colors["body_d"]
    skin_c, skin_d, nose_c, eye_c, claw_c = colors["skin"], colors["skin_d"], colors["nose"], colors["eye"], colors["claw"]
    
    scy = 13 + bob
    
    def shell_px(x, y):
        if y > scy + 9:
            return None
        yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
        if y - yt < 1.3:
            return body_l
        v = (y - scy) + ((x - cx) ** 2) / 28.0
        if int(math.floor(v)) % 3 == 0:
            return body_d
        return body_c
    g.ellipse(cx, scy, 10, 9, shell_px)
    
    hy = 19 + bob
    g.rect(10, hy - 5, 11, hy - 2, skin_d)
    g.rect(20, hy - 5, 21, hy - 2, skin_d)
    
    def head_px(x, y):
        if y <= hy - 2:
            if y <= hy - 3:
                return body_l
            return body_c if (x + y) % 2 == 0 else body_m
        return skin_c
    g.ellipse(cx, hy, 5.2, 4.2, head_px)
    
    if eye == "open":
        g.set(13, hy, eye_c)
        g.set(18, hy, eye_c)
    else:
        g.rect(12, hy, 13, hy, OUT)
        g.rect(18, hy, 19, hy, OUT)
    g.rect(15, hy + 2, 16, hy + 3, nose_c)
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 21, x + 1, bottom, skin_c)
        g.set(x, 21, skin_d)
        g.rect(x - 1, bottom, x + 2, bottom, claw_c)
    
    return g


def generic_back(f=0, colors=None):
    """Generic back view"""
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]
    
    body_c, body_l, body_m, body_d = colors["body"], colors["body_l"], colors["body_m"], colors["body_d"]
    skin_c, skin_d, nose_c, eye_c, claw_c = colors["skin"], colors["skin_d"], colors["nose"], colors["eye"], colors["claw"]
    
    g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: skin_d)
    g.rect(11, 2 + bob, 12, 5 + bob, skin_d)
    g.rect(19, 2 + bob, 20, 5 + bob, skin_d)
    
    for x, l in ((8, lifts[0]), (22, lifts[1])):
        bottom = 25 - l
        g.rect(x, 20, x + 1, bottom, skin_c)
        g.set(x, 20, skin_d)
        g.rect(x - 1, bottom, x + 2, bottom, claw_c)
    
    scy = 14 + bob
    def shell_px(x, y):
        if y > scy + 8:
            return None
        yt = scy - 9 * math.sqrt(max(0.0, 1 - ((x - cx) / 10) ** 2))
        if y - yt < 1.3:
            return body_l
        if y >= scy + 3:
            return body_c if (x + y) % 2 == 0 else body_m
        v = (y - scy) + ((x - cx) ** 2) / 30.0
        if int(math.floor(v)) % 3 == 0:
            return body_d
        return body_c
    g.ellipse(cx, scy, 10, 9, shell_px)
    
    sway = (0, 1, 1, 0, -1, -1)[f % 6]
    for dx in (0, 1):
        line(g, 15 + dx, 21 + bob, 15 + dx + sway, 26, skin_d)
    
    return g


# Color definitions for each animal
ANIMAL_COLORS = {
    "armadillo": {"body": SHELL, "body_l": SHELL_L, "body_m": SHELL_M, "body_d": SHELL_D, "skin": SKIN, "skin_d": SKIN_D, "nose": NOSE, "eye": EYE, "claw": CLAW},
    "wolf": {"body": (120, 120, 120, 255), "body_l": (150, 150, 150, 255), "body_m": (90, 90, 90, 255), "body_d": (60, 60, 60, 255), "skin": (200, 180, 160, 255), "skin_d": (160, 140, 120, 255), "nose": (50, 50, 50, 255), "eye": (255, 255, 0, 255), "claw": (240, 240, 240, 255)},
    "fox": {"body": (200, 100, 50, 255), "body_l": (230, 130, 80, 255), "body_m": (170, 80, 30, 255), "body_d": (140, 60, 20, 255), "skin": (255, 255, 255, 255), "skin_d": (220, 220, 220, 255), "nose": (50, 50, 50, 255), "eye": EYE, "claw": (200, 200, 200, 255)},
    "cat": {"body": (200, 180, 160, 255), "body_l": (220, 200, 180, 255), "body_m": (180, 160, 140, 255), "body_d": (150, 130, 110, 255), "skin": (255, 200, 180, 255), "skin_d": (220, 170, 150, 255), "nose": (255, 150, 150, 255), "eye": (255, 255, 0, 255), "claw": (200, 200, 200, 255)},
    "rabbit": {"body": (220, 220, 220, 255), "body_l": (240, 240, 240, 255), "body_m": (200, 200, 200, 255), "body_d": (180, 180, 180, 255), "skin": (255, 200, 200, 255), "skin_d": (230, 180, 180, 255), "nose": (255, 150, 150, 255), "eye": (255, 50, 50, 255), "claw": (240, 240, 240, 255)},
    "fish": {"body": (255, 100, 50, 255), "body_l": (255, 130, 80, 255), "body_m": (230, 80, 30, 255), "body_d": (200, 60, 20, 255), "skin": (255, 255, 255, 255), "skin_d": (220, 220, 220, 255), "nose": (255, 200, 0, 255), "eye": EYE, "claw": (255, 100, 50, 255)},
    "lizard": {"body": (50, 150, 50, 255), "body_l": (80, 180, 80, 255), "body_m": (30, 120, 30, 255), "body_d": (20, 100, 20, 255), "skin": (200, 255, 200, 255), "skin_d": (170, 220, 170, 255), "nose": (255, 100, 100, 255), "eye": (255, 255, 0, 255), "claw": (200, 200, 200, 255)},
    "bee": {"body": (255, 255, 0, 255), "body_l": (255, 255, 50, 255), "body_m": (230, 230, 0, 255), "body_d": (200, 200, 0, 255), "skin": (255, 255, 255, 255), "skin_d": (220, 220, 220, 255), "nose": (0, 0, 0, 255), "eye": EYE, "claw": (200, 200, 200, 255)},
    "butterfly": {"body": (255, 150, 200, 255), "body_l": (255, 180, 220, 255), "body_m": (230, 130, 180, 255), "body_d": (200, 100, 150, 255), "skin": (255, 255, 255, 255), "skin_d": (220, 220, 220, 255), "nose": (255, 200, 0, 255), "eye": EYE, "claw": (200, 200, 200, 255)},
    "spider": {"body": (50, 50, 50, 255), "body_l": (80, 80, 80, 255), "body_m": (30, 30, 30, 255), "body_d": (20, 20, 20, 255), "skin": (200, 180, 160, 255), "skin_d": (160, 140, 120, 255), "nose": (255, 100, 100, 255), "eye": (255, 255, 0, 255), "claw": (200, 200, 200, 255)},
    "frog": {"body": (50, 200, 50, 255), "body_l": (80, 220, 80, 255), "body_m": (30, 180, 30, 255), "body_d": (20, 160, 20, 255), "skin": (255, 255, 200, 255), "skin_d": (220, 220, 170, 255), "nose": (255, 100, 50, 255), "eye": (255, 255, 255, 255), "claw": (200, 200, 200, 255)},
    "dragon": {"body": (200, 50, 50, 255), "body_l": (230, 80, 80, 255), "body_m": (170, 30, 30, 255), "body_d": (140, 20, 20, 255), "skin": (255, 255, 200, 255), "skin_d": (220, 220, 170, 255), "nose": (255, 255, 0, 255), "eye": (255, 255, 0, 255), "claw": (255, 255, 200, 255)},
    "unicorn": {"body": (255, 255, 255, 255), "body_l": (255, 255, 255, 255), "body_m": (230, 230, 230, 255), "body_d": (200, 200, 200, 255), "skin": (255, 200, 220, 255), "skin_d": (220, 170, 190, 255), "nose": (255, 150, 200, 255), "eye": (255, 100, 150, 255), "claw": (240, 240, 240, 255)},
    "penguin": {"body": (50, 50, 80, 255), "body_l": (80, 80, 110, 255), "body_m": (30, 30, 60, 255), "body_d": (20, 20, 40, 255), "skin": (255, 255, 255, 255), "skin_d": (220, 220, 220, 255), "nose": (255, 150, 50, 255), "eye": EYE, "claw": (255, 200, 100, 255)},
    "owl": {"body": (150, 100, 50, 255), "body_l": (180, 130, 80, 255), "body_m": (120, 70, 30, 255), "body_d": (90, 50, 20, 255), "skin": (255, 255, 200, 255), "skin_d": (220, 220, 170, 255), "nose": (255, 200, 100, 255), "eye": (255, 255, 0, 255), "claw": (200, 200, 200, 255)},
    "ladybug": {"body": (255, 50, 50, 255), "body_l": (255, 80, 80, 255), "body_m": (230, 30, 30, 255), "body_d": (200, 20, 20, 255), "skin": (0, 0, 0, 255), "skin_d": (50, 50, 50, 255), "nose": (0, 0, 0, 255), "eye": EYE, "claw": (200, 200, 200, 255)},
    "snake": {"body": (50, 150, 50, 255), "body_l": (80, 180, 80, 255), "body_m": (30, 120, 30, 255), "body_d": (20, 100, 20, 255), "skin": (255, 255, 200, 255), "skin_d": (220, 220, 170, 255), "nose": (255, 100, 50, 255), "eye": (255, 255, 0, 255), "claw": (200, 200, 200, 255)},
    "rabbit": {"body": (220, 220, 220, 255), "body_l": (240, 240, 240, 255), "body_m": (200, 200, 200, 255), "body_d": (180, 180, 180, 255), "skin": (255, 200, 200, 255), "skin_d": (230, 180, 180, 255), "nose": (255, 150, 150, 255), "eye": (255, 50, 50, 255), "claw": (240, 240, 240, 255)},
}

# Get sprite function for an animal
def get_sprite_func(animal, view):
    if animal in ANIMAL_SPRITES:
        return ANIMAL_SPRITES[animal][view]
    else:
        # Use generic functions for animals without unique sprites
        if view == "side":
            return lambda *args, **kwargs: generic_side(*args, colors=ANIMAL_COLORS.get(animal, ANIMAL_COLORS["armadillo"]), **kwargs)
        elif view == "front":
            return lambda *args, **kwargs: generic_front(*args, colors=ANIMAL_COLORS.get(animal, ANIMAL_COLORS["armadillo"]), **kwargs)
        elif view == "back":
            return lambda *args, **kwargs: generic_back(*args, colors=ANIMAL_COLORS.get(animal, ANIMAL_COLORS["armadillo"]), **kwargs)


# ================================================================
# OTHER POSES (using animal-specific sprites)
# ================================================================

def stand(idx=0, blink=False, animal="armadillo"):
    side_func = get_sprite_func(animal, "side")
    return side_func(bob=0, legs=[(0, 0)] * 4, head_dy=0, head_dx=0,
                     eye="closed" if blink else "open", mouth=0,
                     tail=(0, 1, 2, 1, 0, -1, -2, -1)[idx % 8], ears=0)


def sniff(idx, animal="armadillo"):
    i = idx % 4
    side_func = get_sprite_func(animal, "side")
    return side_func(bob=0, legs=[(0, 0)] * 4,
                     head_dy=(0, 1, 0, 1)[i], head_dx=(0, 1, 0, 1)[i],
                     tail=(0, 1, 0, -1)[i], ears=0)


def yawn(idx, animal="armadillo"):
    i = idx % 8
    mouth = (0, 1, 2, 2, 2, 2, 1, 0)[i]
    side_func = get_sprite_func(animal, "side")
    return side_func(bob=0, legs=[(0, 0)] * 4,
                     head_dy=-1 if 2 <= i <= 5 else 0,
                     head_dx=1 if 2 <= i <= 5 else 0,
                     eye="closed" if 1 <= i <= 6 else "open",
                     mouth=mouth,
                     ears=-1 if 2 <= i <= 5 else 0, tail=-1)


DIRT_FRAMES = (
    [(15, 23), (12, 21)],
    [(13, 21), (10, 19), (15, 24)],
    [(11, 19), (8, 18), (14, 22)],
    [(10, 21), (7, 22)],
)


def dig(idx, animal="armadillo"):
    i = idx % 4
    a = (2, 0, 2, 0)[i]
    b = (0, 2, 0, 2)[i]
    legs = [(0, 0), (b, -2 if b else 0), (0, 0), (a, -2 if a else 0)]
    side_func = get_sprite_func(animal, "side")
    g = side_func(bob=0, legs=legs, head_dy=3, head_dx=1, eye="open", mouth=0,
                  tail=(0, 1, 0, 1)[i], ears=-1)
    for (x, y) in DIRT_FRAMES[i]:
        g.rect(x, y, x + 1, y + 1, DIRT)
    return g


def alert(idx, animal="armadillo"):
    i = idx % 3
    bob = (0, -3, 0)[i]
    legs = [(0, 0)] * 4 if i != 1 else [(2, 0)] * 4
    side_func = get_sprite_func(animal, "side")
    g = side_func(bob=bob, legs=legs, head_dy=0, head_dx=0, eye="wide", mouth=0, tail=2, ears=1)
    g.stamp(25, 0, BANG, RED)
    return g


def happy(idx, animal="armadillo"):
    i = idx % 4
    side_func = get_sprite_func(animal, "side")
    g = side_func(bob=(0, -1, 0, -1)[i], legs=[(0, 0)] * 4, head_dy=-1, head_dx=0,
                  eye="closed", mouth=0, tail=(2, -2, 2, -2)[i], ears=1)
    for k in range(2):
        age = (idx * 2 + k * 6) % 12
        g.stamp(21 + k * 6 - age // 4, 8 - age // 2, HEART_PX, HEART)
    return g


def curl1(animal="armadillo"):
    side_func = get_sprite_func(animal, "side")
    return side_func(bob=1, legs=[(1, 0)] * 4, head_dy=3, head_dx=-2, eye="closed", mouth=0, tail=-1, ears=-1)


def ball(rot=0.0, squish=0, snout=False, tailtip=False, animal="armadillo"):
    g = Grid()
    cx, r = 15.5, 9
    ry = r - squish
    cy = 25.5 - ry
    ca, sa = math.cos(rot), math.sin(rot)
    
    colors = ANIMAL_COLORS.get(animal, ANIMAL_COLORS["armadillo"])
    body_c, body_l, body_m, body_d = colors["body"], colors["body_l"], colors["body_m"], colors["body_d"]
    skin_c, skin_d, nose_c = colors["skin"], colors["skin_d"], colors["nose"]
    
    def px(x, y):
        if math.hypot(x - (cx - 3), y - (cy - 4)) < 2.4:
            return body_l
        u = (x - cx) * ca + (y - cy) * sa
        if abs(u - 4 * round(u / 4)) < 0.75:
            return body_d
        if (x - cx) + (y - cy) > 8:
            return body_m
        return body_c
    g.ellipse(cx, cy, r, ry, px)
    if snout:
        g.rect(24, 20, 26, 22, skin_c)
        g.set(26, 21, nose_c)
    if tailtip:
        g.rect(4, 21, 7, 22, skin_d)
    return g


def curl2(animal="armadillo"):
    return ball(rot=0.35, snout=True, tailtip=True, animal=animal)


def sleep_frame(f, animal="armadillo"):
    squish = (0, 0, 1, 1)[(f // 2) % 4]
    g = ball(rot=0.35, squish=squish, snout=True, tailtip=True, animal=animal)
    for k in range(2):
        age = (f + 4 * k) % 8
        y = 11 - age
        x = 22 + age // 2 + k
        if y >= 0:
            g.stamp(x, y, Z4 if age < 5 else Z3, ZCOL)
    return g


# ================================================================
# FRAME FACTORY
# ================================================================

def walk_side(f, tilt=0, animal="armadillo"):
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    side_func = get_sprite_func(animal, "side")
    return side_func(bob=bob, legs=walk_legs(f), head_dy=tilt,
                     tail=(0, 1, 0, -1, 0, 1)[f % 6],
                     ears=1 if tilt < 0 else 0)


def walk_front(f, animal="armadillo"):
    front_func = get_sprite_func(animal, "front")
    return front_func(f=f, eye="open")


def walk_back(f, animal="armadillo"):
    back_func = get_sprite_func(animal, "back")
    return back_func(f=f)


def build(name, idx=0, tilt=0, blink=False, animal="armadillo"):
    if name == "walk_side":
        g = walk_side(idx, tilt, animal)
    elif name == "walk_front":
        g = walk_front(idx, animal)
    elif name == "walk_back":
        g = walk_back(idx, animal)
    elif name == "stand":
        g = stand(idx, blink, animal)
    elif name == "stand_front":
        front_func = get_sprite_func(animal, "front")
        g = front_func(f=0, eye="closed" if blink else "open")
    elif name == "sniff":
        g = sniff(idx, animal)
    elif name == "yawn":
        g = yawn(idx, animal)
    elif name == "dig":
        g = dig(idx, animal)
    elif name == "alert":
        g = alert(idx, animal)
    elif name == "happy":
        g = happy(idx, animal)
    elif name == "curl1":
        g = curl1(animal)
    elif name == "curl2":
        g = curl2(animal)
    elif name == "ball":
        g = ball(rot=idx * math.pi / 8, animal=animal)
    elif name == "sleep":
        g = sleep_frame(idx, animal)
    else:
        raise ValueError(name)
    g.outline()
    return g


# ================================================================
# ACCESSORY RENDERING (improved positioning)
# ================================================================

def render_accessory(g, accessory, animal="armadillo"):
    """Render accessory on the sprite grid with animal-specific positioning"""
    if accessory == "none":
        return
    
    ac = AP.get(accessory, (200, 200, 200, 255))
    
    # Accessory positioning varies by animal
    if animal in ["wolf", "fox", "cat", "rabbit", "dragon", "unicorn", "penguin", "owl", "ladybug", "snake"]:
        # Mammals and similar - accessories on head
        head_y = 8
    elif animal in ["fish"]:
        # Fish - no accessories (or on body)
        head_y = 12
    elif animal in ["lizard", "spider", "frog"]:
        # Reptiles/amphibians - slightly lower
        head_y = 10
    elif animal in ["bee", "butterfly"]:
        # Insects - accessories on thorax
        head_y = 12
    else:
        # Armadillo and others
        head_y = 8
    
    if accessory == "tophat":
        # Top hat - positioned on head
        g.rect(13, head_y - 6, 19, head_y - 4, ac)
        g.rect(14, head_y - 4, 18, head_y - 2, ac)
        g.rect(12, head_y - 2, 20, head_y, ac)
        g.rect(11, head_y, 21, head_y + 2, ac)
    elif accessory == "bow":
        # Bow - on head/neck
        g.rect(14, head_y - 2, 15, head_y, ac)
        g.rect(16, head_y - 2, 17, head_y, ac)
        g.rect(15, head_y - 1, 16, head_y + 1, ac)
        g.rect(14, head_y + 1, 17, head_y + 2, ac)
        # Bow center
        g.rect(15, head_y, 16, head_y + 1, (255, 200, 200, 255))
    elif accessory == "glasses":
        # Glasses - on face
        g.rect(12, head_y + 4, 13, head_y + 5, ac)
        g.rect(14, head_y + 4, 15, head_y + 5, ac)
        g.rect(18, head_y + 4, 19, head_y + 5, ac)
        g.rect(19, head_y + 4, 20, head_y + 5, ac)
        g.rect(13, head_y + 4, 18, head_y + 4, ac)
    elif accessory == "crown":
        # Crown - on head
        g.rect(13, head_y - 6, 14, head_y - 4, ac)
        g.rect(15, head_y - 7, 16, head_y - 3, ac)
        g.rect(17, head_y - 6, 18, head_y - 4, ac)
        g.rect(14, head_y - 5, 17, head_y - 4, ac)
        g.rect(12, head_y - 4, 19, head_y - 3, ac)
    elif accessory == "flower":
        # Flower - on head
        g.rect(15, head_y - 6, 16, head_y - 4, ac)
        g.rect(14, head_y - 5, 17, head_y - 3, ac)
        g.rect(13, head_y - 4, 18, head_y - 2, ac)
        g.rect(15, head_y - 2, 16, head_y, (255, 255, 0, 255))  # flower center
    elif accessory == "santa":
        # Santa hat
        g.rect(13, head_y - 6, 19, head_y - 4, (255, 0, 0, 255))
        g.rect(14, head_y - 4, 18, head_y - 2, (255, 0, 0, 255))
        g.rect(15, head_y - 2, 17, head_y, (255, 0, 0, 255))
        g.rect(16, head_y, 16, head_y + 2, (255, 0, 0, 255))
        g.rect(15, head_y + 2, 17, head_y + 3, (255, 255, 255, 255))
    elif accessory == "witch":
        # Witch hat
        g.rect(14, head_y - 8, 18, head_y - 6, AP["witch"])
        g.rect(15, head_y - 6, 17, head_y - 2, AP["witch"])
        g.rect(16, head_y - 2, 16, head_y + 2, AP["witch"])
        g.rect(13, head_y + 2, 19, head_y + 3, AP["witch_brim"])


# ================================================================
# THE PET
# ================================================================

class Pet:
    STOP = 1.0
    ROLL_DIST = 520
    ROLL_STOP = 150
    SLEEP_AFTER = 260

    def __init__(self, scale, animal="armadillo", accessory="none", playtime=False):
        self.root = tk.Tk()
        self.animal = animal
        self.accessory = accessory
        self.playtime = playtime
        r = self.root
        r.title("Onekos - " + animal.capitalize())
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
        self.wander_target = None
        self.wander_time = 0

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.canvas.bind("<Control-Alt-h>", self.open_menu)
        self.canvas.bind("<Control-Alt-H>", self.open_menu)
        self.menu = tk.Menu(r, tearoff=0)
        
        animal_menu = tk.Menu(self.menu, tearoff=0)
        animals = ["armadillo", "wolf", "fox", "cat", "rabbit", "fish", "lizard", "bee", "butterfly", "spider", "frog", "dragon", "unicorn", "penguin", "owl", "ladybug", "snake"]
        for a in animals:
            animal_menu.add_command(label=a.capitalize(), command=lambda a=a: self.set_animal(a))
        self.menu.add_cascade(label="Animal", menu=animal_menu)
        
        acc_menu = tk.Menu(self.menu, tearoff=0)
        accessories = ["none", "tophat", "bow", "glasses", "crown", "flower", "santa", "witch"]
        for acc in accessories:
            label = acc.capitalize() if acc != "none" else "No Accessory"
            acc_menu.add_command(label=label, command=lambda acc=acc: self.set_accessory(acc))
        self.menu.add_cascade(label="Accessory", menu=acc_menu)
        
        self.menu.add_command(label="Playtime Mode", command=self.toggle_playtime)
        self.menu.add_separator()
        self.menu.add_command(label="Take a nap", command=self.nap)
        self.menu.add_command(label="Dig a hole", command=self.dig_now)
        self.menu.add_command(label="Roll over here", command=self.roll_now)
        sizes = tk.Menu(self.menu, tearoff=0)
        for label, s in (("Small", 2), ("Medium", 3), ("Large", 5), ("Huge", 8)):
            sizes.add_command(label=label, command=lambda s=s: self.set_scale(s))
        self.menu.add_cascade(label="Size", menu=sizes)
        self.menu.add_separator()
        self.menu.add_command(label="Quit", command=r.destroy)

        self.place()
        self.tick()

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

    def img(self, name, idx=0, tilt=0, blink=False, face=1):
        key = (name, idx, tilt, blink, face, self.scale, self.animal, self.accessory)
        im = self.cache.get(key)
        if im is None:
            g = build(name, idx, tilt, blink, self.animal)
            if face < 0:
                g = g.flipped()
            render_accessory(g, self.accessory, self.animal)
            im = tk.PhotoImage(data=g.png_b64(self.scale))
            self.cache[key] = im
        return im

    def show(self, name, idx=0, tilt=0, blink=False, face=1):
        self.canvas.itemconfig(self.item, image=self.img(name, idx, tilt, blink, face))

    def set_animal(self, animal):
        self.animal = animal
        self.cache.clear()
        self.root.title("Onekos - " + animal.capitalize())

    def set_accessory(self, accessory):
        self.accessory = accessory
        self.cache.clear()

    def toggle_playtime(self):
        self.playtime = not self.playtime
        self.cache.clear()
        if self.playtime:
            # Start wandering immediately
            self.wander_target = None

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
        if self.state in ("idle", "walk"):
            self.begin_curl("sleep")

    def dig_now(self):
        if self.state in ("idle", "walk"):
            self.set("idle")
            self.start_act("dig")

    def roll_now(self):
        if self.state in ("idle", "walk"):
            self.begin_curl("roll")

    def on_click(self, _e):
        if self.state == "sleep":
            self.begin_uncurl("alert")
        elif self.state in ("idle", "walk"):
            self.set("happy")

    def on_menu(self, e):
        try:
            self.menu.tk_popup(e.x_root, e.y_root)
        finally:
            self.menu.grab_release()

    def open_menu(self, e=None):
        try:
            self.menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            self.menu.grab_release()

    def start_act(self, name):
        durs = {"sniff": 36, "yawn": 30, "dig": 48, "look": 36}
        self.act = name
        self.act_t = 0
        self.act_dur = durs[name]

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
                self.begin_uncurl("walk")
        elif s == "sleep":
            self.show("sleep", (self.st // 3) % 8, face=self.face)
            woke = math.hypot(px - self.sleep_ptr[0], py - self.sleep_ptr[1]) > 90
            if woke and self.st > 60:
                self.begin_uncurl("alert")
        elif s == "alert":
            self.show("alert", min(2, self.st // 4), face=self.face)
            if self.st >= 14:
                self.set("idle")
        elif s == "happy":
            self.show("happy", (self.st // 3) % 4, face=self.face)
            if self.st >= 36:
                self.set("idle")
        self.place()

    def do_idle(self, dx, dy, dist, stop):
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
                self.start_act(random.choice(("sniff", "sniff", "yawn", "dig", "look")))
            self.show("stand", (self.t // 4) % 8, blink=blink, face=self.face)
            return
        self.act_t += 1
        a, i = self.act, self.act_t
        face = self.face
        if a == "sniff":
            self.show("sniff", i // 3, face=face)
        elif a == "yawn":
            self.show("yawn", i // 4, face=face)
        elif a == "dig":
            self.show("dig", i // 3, face=face)
        elif a == "look":
            f = face if i < 10 else (-face if i < 22 else face)
            self.show("stand", (self.t // 4) % 8, blink=blink, face=f)
        if self.act_t >= self.act_dur:
            self.act = None

    def do_walk(self, dx, dy, dist, stop):
        if self.playtime:
            # Playtime mode: autonomous wandering
            # Pet wanders randomly, ignoring cursor
            speed = 3
            
            # If we don't have a target or reached it, pick a new random target
            if self.wander_target is None or self.st % 100 == 0:
                self.wander_target = (
                    self.x + random.randint(-200, 200),
                    self.y + random.randint(-200, 200)
                )
                self.wander_time = self.st
            
            # Move toward wander target
            tx, ty = self.wander_target
            wdx, wdy = tx - self.x, ty - self.y
            wdist = math.hypot(wdx, wdy)
            
            if wdist > 0:
                self.x += wdx / wdist * speed
                self.y += wdy / wdist * speed
            
            # Pick view based on movement direction
            if abs(wdy) > 1.7 * abs(wdx):
                self.view = "front" if wdy > 0 else "back"
            else:
                self.view = "side"
                if abs(wdx) > 3:
                    self.face = 1 if wdx > 0 else -1
                r = wdy / (abs(wdx) + 1)
                self.tilt = -1 if r < -0.45 else (1 if r > 0.45 else 0)
            
            # Change target occasionally
            if self.st - self.wander_time > 200 or wdist < 10:
                self.wander_target = None
            
            self.act = None
            
            if self.st % 2 == 0:
                self.fr = (self.fr + 1) % 6
            if self.view == "side":
                self.show("walk_side", self.fr, tilt=self.tilt, face=self.face)
            elif self.view == "front":
                self.show("walk_front", self.fr)
            else:
                self.show("walk_back", self.fr)
        else:
            # Normal mode: follow cursor
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


# ================================================================
# GOOGLE DOCS DETECTION (checks URL via browser)
# ================================================================

def check_google_docs():
    """Check if user is in Google Docs by checking active browser tab URL"""
    try:
        import pyautogui
        import time
        
        # Try to detect Google Docs via window title or URL
        while True:
            time.sleep(3)
            try:
                # Method 1: Check active window title
                active_title = pyautogui.getActiveWindowTitle()
                if active_title and "docs.google.com" in active_title.lower():
                    type_random_text()
                    continue
                
                # Method 2: Try to get URL from browser (Windows)
                try:
                    import win32gui
                    import win32con
                    
                    def enum_callback(hwnd, result):
                        class_name = win32gui.GetClassName(hwnd)
                        title = win32gui.GetWindowText(hwnd)
                        if "chrome" in class_name.lower() or "firefox" in class_name.lower() or "msedge" in class_name.lower():
                            if "docs.google.com" in title.lower():
                                result.append(hwnd)
                        return True
                    
                    result = []
                    win32gui.EnumWindows(enum_callback, result)
                    if result:
                        type_random_text()
                except:
                    pass
                    
            except Exception as e:
                pass
    except:
        pass


def type_random_text():
    """Type random text when in Google Docs"""
    try:
        import pyautogui
        import string
        import time
        
        # Generate random cute text
        words = ["Hello", "Hi", "Hey", "Nice", "Cool", "Love", "Cute", "Pet", "Fun", "Wow", "Yay", "Meow", "Bark", "Purr", "Hop"]
        text = random.choice(words) + " " + random.choice(words)
        
        # Type it
        pyautogui.write(text, interval=0.05)
        time.sleep(random.uniform(1.0, 3.0))
    except:
        pass


# ================================================================
# MAIN
# ================================================================

def main():
    if tk is None:
        print("tkinter is not installed.")
        return
    
    scale = None
    animal = "armadillo"
    accessory = "none"
    playtime = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--scale" and i + 1 < len(args):
            try:
                scale = int(args[i + 1])
                i += 2
            except ValueError:
                i += 1
        elif args[i] == "--animal" and i + 1 < len(args):
            animal = args[i + 1]
            i += 2
        elif args[i] == "--accessory" and i + 1 < len(args):
            accessory = args[i + 1]
            i += 2
        elif args[i] == "--playtime":
            playtime = True
            i += 1
        elif args[i].startswith("--"):
            i += 1
        else:
            i += 1

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
    
    pet = Pet(scale, animal=animal, accessory=accessory, playtime=playtime)
    
    # Start Google Docs detection thread
    threading.Thread(target=check_google_docs, daemon=True).start()
    
    pet.root.mainloop()


if __name__ == "__main__":
    main()
