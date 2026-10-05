#!/usr/bin/env python3
"""
Armadillo - a tiny desktop pet that chases your mouse cursor, oneko style.

Everything (all the pixel art, all the animations) is drawn by this one file,
so there are no image files to ship. Only needs Python + tkinter.

    pythonw armadillo.py            run it
    pythonw armadillo.py --scale 4  bigger armadillo

Left click   : pet the armadillo
Right click  : menu (nap, dig, size, quit)
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


# ----------------------------------------------------------- side view
LEG_X = (10, 19, 7, 16)   # back_far, front_far, back_near, front_near


def _leg(g, x, top, lift, dx, col, edge):
    x += dx
    bottom = max(top, 25 - lift)
    g.rect(x, top, x + 1, bottom, col)
    for y in range(top, bottom + 1):
        g.set(x, y, edge)
    g.set(x + 1, bottom, CLAW)
    g.set(x + 2, bottom, CLAW)


def side(bob=0, legs=None, head_dy=0, head_dx=0, eye="open", mouth=0,
         tail=0, ears=0, shell=(14, 15, 9, 8), hole=False):
    g = Grid()
    legs = legs or [(0, 0)] * 4
    scx, scy, srx, sry = shell
    scy += bob
    top = scy + sry - 3

    if hole:
        g.ellipse(21, 25, 7, 1.3, lambda x, y: DIRT_D)

    _leg(g, LEG_X[0], top, *legs[0], SKIN_D, FAR_EDGE)
    _leg(g, LEG_X[1], top, *legs[1], SKIN_D, FAR_EDGE)

    ty = scy + 3                                   # tail
    line(g, scx - srx + 2, ty, 1, ty + 2 - tail, SKIN_D, 2)

    g.ellipse(scx, scy + sry - 2, srx - 1, 3, lambda x, y: SKIN)   # belly

    def shell_px(x, y):                            # shell
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

    hx, hy = scx + 9 + head_dx, scy + 2 + head_dy  # head

    def head_px(x, y):
        if y <= hy - 1:
            if y <= hy - 3:
                return SHELL_L
            return SHELL if (x + y) % 2 == 0 else SHELL_M
        return SKIN
    g.ellipse(hx, hy, 4, 3.2, head_px)

    # snout + jaw
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

    # eye
    if eye == "open":
        g.set(hx + 2, hy, EYE)
    elif eye == "wide":
        g.rect(hx + 2, hy - 1, hx + 3, hy, EYE)
        g.set(hx + 2, hy - 1, WHITE)
    else:  # closed
        g.set(hx + 1, hy, OUT)
        g.set(hx + 2, hy, OUT)

    # ear
    if ears == 0:
        g.rect(hx - 2, hy - 5, hx - 1, hy - 3, SKIN_D)
    elif ears == 1:
        g.rect(hx - 2, hy - 7, hx - 1, hy - 3, SKIN_D)
    else:
        g.rect(hx - 5, hy - 2, hx - 2, hy - 1, SKIN_D)

    _leg(g, LEG_X[2], top, *legs[2], SKIN, SKIN_D)
    _leg(g, LEG_X[3], top, *legs[3], SKIN, SKIN_D)
    return g


# gait tables (6 frames)
LIFT = (0, 1, 2, 1, 0, 0)
SWING = (-1, -1, 0, 1, 1, 0)
LEG_OFF = (0, 3, 3, 0)          # diagonal pairs move together


def walk_legs(f):
    out = []
    for off in LEG_OFF:
        p = (f + off) % 6
        out.append((LIFT[p], SWING[p]))
    return out


def walk_side(f, tilt=0):
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    return side(bob=bob, legs=walk_legs(f), head_dy=tilt,
                tail=(0, 1, 0, -1, 0, 1)[f % 6],
                ears=1 if tilt < 0 else 0)


# ---------------------------------------------------------- front view
def front(f=0, eye="open"):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = []
    for off in (0, 3):
        lifts.append(LIFT[(f + off) % 6])

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
    g.rect(10, hy - 5, 11, hy - 2, SKIN_D)           # ears
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

    for x, l in ((8, lifts[0]), (22, lifts[1])):     # front legs
        bottom = 25 - l
        g.rect(x, 21, x + 1, bottom, SKIN)
        g.set(x, 21, SKIN_D)
        g.rect(x - 1, bottom, x + 2, bottom, CLAW)
    return g


# ----------------------------------------------------------- back view
def back(f=0):
    g = Grid()
    cx = 15.5
    bob = (0, 0, -1, 0, 0, -1)[f % 6]
    lifts = [LIFT[(f + off) % 6] for off in (0, 3)]

    g.ellipse(cx, 7 + bob, 4.4, 3.4, lambda x, y: SKIN_D)      # head peeking
    g.rect(11, 2 + bob, 12, 5 + bob, SKIN_D)
    g.rect(19, 2 + bob, 20, 5 + bob, SKIN_D)

    for x, l in ((8, lifts[0]), (22, lifts[1])):                # hind legs
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
        if y >= scy + 3:                                         # rear shield
            return SHELL if (x + y) % 2 == 0 else SHELL_M
        v = (y - scy) + ((x - cx) ** 2) / 30.0
        if int(math.floor(v)) % 3 == 0:
            return SHELL_D
        return SHELL
    g.ellipse(cx, scy, 10, 9, shell_px)

    sway = (0, 1, 1, 0, -1, -1)[f % 6]
    for dx in (0, 1):                                            # tail
        line(g, 15 + dx, 21 + bob, 15 + dx + sway, 26, SKIN_D)
    return g


# ---------------------------------------------------------------- ball
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


# --------------------------------------------------------- other poses
def stand(idx=0, blink=False):
    return side(tail=(0, 1, 2, 1, 0, -1, -2, -1)[idx % 8],
                eye="closed" if blink else "open")


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
    return ball(rot=0.35, snout=True, tailtip=True)


# ------------------------------------------------------- frame factory
def build(name, idx=0, tilt=0, blink=False):
    if name == "walk_side":
        g = walk_side(idx, tilt)
    elif name == "walk_front":
        g = front(idx)
    elif name == "walk_back":
        g = back(idx)
    elif name == "stand":
        g = stand(idx, blink)
    elif name == "stand_front":
        g = front(0, "closed" if blink else "open")
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
    STOP = 1.0       # multiplied by sprite size
    ROLL_DIST = 520
    ROLL_STOP = 150
    SLEEP_AFTER = 260   # idle ticks (13 s) before a nap

    def __init__(self, scale):
        self.root = tk.Tk()
        r = self.root
        r.title("Armadillo")
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
        self.st = 0          # ticks in state
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

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_menu)
        self.menu = tk.Menu(r, tearoff=0)
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

    # -- setup helpers
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
        key = (name, idx, tilt, blink, face, self.scale)
        im = self.cache.get(key)
        if im is None:
            g = build(name, idx, tilt, blink)
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

    # -- state helpers
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

    def start_act(self, name):
        durs = {"sniff": 36, "yawn": 30, "dig": 48, "look": 36}
        self.act = name
        self.act_t = 0
        self.act_dur = durs[name]

    # -- main loop
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

        # pick view
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


def main():
    if tk is None:
        print("tkinter is not installed.")
        return
    scale = None
    if "--scale" in sys.argv:
        try:
            scale = int(sys.argv[sys.argv.index("--scale") + 1])
        except (IndexError, ValueError):
            pass
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
    pet.root.mainloop()


if __name__ == "__main__":
    main()
