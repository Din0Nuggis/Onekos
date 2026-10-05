#!/usr/bin/env python3
"""
Onekos - 17 COMPLETELY UNIQUE Desktop Pets
Each animal has a fundamentally different shape, silhouette, and features.
NO two animals look even remotely similar.

Animals with RADICALLY DIFFERENT designs:
- Armadillo: Wide armored ball
- Wolf: Long lean predator
- Fox: Short stocky hunter
- Cat: Arched back feline
- Rabbit: Upright tall ears
- Fish: Horizontal swimmer
- Lizard: Flat long reptile
- Bee: Small striped flyer
- Butterfly: Huge wings
- Spider: 8-legged creepy
- Frog: Squat jumper
- Dragon: Long-necked flyer
- Unicorn: Horse with horn
- Penguin: Upright waddler
- Owl: Round bird
- Ladybug: Perfect circle
- Snake: S-curve slitherer

Each has UNIQUE: body shape, leg count, head shape, tail, features
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
except ImportError:
    tk = None

W = H = 32
KEY = "#010203"
TICK = 50

OUT = (46, 34, 36, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
RED = (232, 56, 56, 255)
HEART = (244, 84, 124, 255)
ZCOL = (120, 176, 255, 255)
MOUTH = (150, 48, 60, 255)
TONGUE = (232, 112, 124, 255)
DIRT = (140, 98, 60, 255)
DIRT_D = (74, 50, 34, 255)

LIFT = (0, 1, 2, 1, 0, 0)
SWING = (-1, -1, 0, 1, 1, 0)
LEG_OFF = (0, 3, 3, 0)

def walk_legs(f):
    out = []
    for off in LEG_OFF:
        p = (f + off) % 6
        out.append((LIFT[p], SWING[p]))
    return out

AP = {
    "tophat": (50, 50, 50, 255), "tophat_trim": (200, 200, 200, 255),
    "bow": (255, 100, 150, 255), "bow_center": (255, 200, 200, 255),
    "glasses": (200, 200, 200, 255), "glasses_frame": (100, 100, 100, 255),
    "crown": (255, 215, 0, 255), "crown_gem": (255, 0, 0, 255),
    "flower": (255, 100, 200, 255), "flower_center": (255, 255, 0, 255),
    "santa": (255, 0, 0, 255), "santa_trim": (255, 255, 255, 255),
    "witch": (100, 50, 150, 255), "witch_brim": (50, 25, 75, 255),
}

Z4 = ["1111", "0010", "0100", "1111"]
Z3 = ["111", "010", "111"]
HEART_PX = ["01010", "11111", "01110", "00100"]
BANG = ["11","11","11","11","11","11","00","11","11"]
DIRT_FRAMES = ([(15,23),(12,21)],[(13,21),(10,19),(15,24)],[(11,19),(8,18),(14,22)],[(10,21),(7,22)])


class Grid:
    def __init__(self):
        self.p = [[None]*W for _ in range(H)]
    def set(self,x,y,c):
        if 0<=x<W and 0<=y<H: self.p[y][x]=c
    def rect(self,x0,y0,x1,y1,c):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1): self.set(x,y,c)
    def ellipse(self,cx,cy,rx,ry,fn):
        for y in range(int(cy-ry)-1,int(cy+ry)+2):
            for x in range(int(cx-rx)-1,int(cx+rx)+2):
                if ((x-cx)/rx)**2+((y-cy)/ry)**2<=1.0:
                    c=fn(x,y)
                    if c: self.set(x,y,c)
    def stamp(self,x,y,rows,c):
        for j,row in enumerate(rows):
            for i,ch in enumerate(row):
                if ch=="1": self.set(x+i,y+j,c)
    def outline(self):
        src=[r[:] for r in self.p]
        for y in range(H):
            for x in range(W):
                if src[y][x] is None:
                    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                        nx,ny=x+dx,y+dy
                        if 0<=nx<W and 0<=ny<H and src[ny][nx] is not None:
                            self.p[y][x]=OUT; break
    def flipped(self):
        g=Grid(); g.p=[r[::-1] for r in self.p]; return g
    def png_b64(self,scale):
        raw=bytearray()
        for row in self.p:
            line=bytearray()
            for c in row: line+=(bytes(c) if c else b"\x00\x00\x00\x00")*scale
            for _ in range(scale): raw.append(0); raw+=line
        def chunk(t,d):
            c=struct.pack(">I",len(d))+t+d
            return c+struct.pack(">I",zlib.crc32(t+d)&0xFFFFFFFF)
        png=(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",W*scale,H*scale,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(bytes(raw),9))+chunk(b"IEND",b""))
        return base64.b64encode(png).decode("ascii")

def line(g,x0,y0,x1,y1,c,thick=1):
    n=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(n+1):
        x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n)
        for t in range(thick): g.set(x,y+t,c)


# ================================================================
# 17 RADICALLY DIFFERENT ANIMALS
# Each has: unique silhouette, different leg count, distinct features
# ================================================================

# --- 1. ARMADILLO: Wide, low, armored ball with shell plates ---
SHELL=(138,120,104,255); SHELL_L=(182,164,142,255); SHELL_M=(118,101,88,255); SHELL_D=(88,72,62,255)
SKIN_A=(226,192,168,255); SKIN_D_A=(186,146,126,255); NOSE_A=(238,140,152,255); EYE_A=(22,16,20,255)
CLAW_A=(248,238,222,255); FAR_EDGE=(150,115,100,255)

def arm_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    scx,scy=14,16+bob
    # WIDE shell - unique armored look
    def sp(x,y):
        if y>scy+6: return None
        yt=scy-6*math.sqrt(max(0,1-((x-scx)/7)**2))
        if y-yt<1.2: return SHELL_L
        if abs(x-scx)>=5: return SHELL if (x+y)%2==0 else SHELL_M
        if (x-scx+(y-scy)//3)%3==0: return SHELL_D
        return SHELL
    g.ellipse(scx,scy,7,6,sp)
    g.ellipse(scx,scy+4,6,2,lambda x,y:SKIN_A)
    # 4 SHORT legs
    LX=(10,18,6,14)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+1,b,SKIN_D_A)
        for y in range(20+bob,b+1): g.set(x,y,FAR_EDGE if i<2 else SKIN_D_A)
        g.set(x+1,b,CLAW_A); g.set(x+2,b,CLAW_A)
    # Short tail
    line(g,scx-6,scy+3,1,scy+3-tail,SKIN_D_A,2)
    # Head
    hhx,hhy=scx+8+hx,scy-2+hd
    def hp(x,y):
        if y<=hhy-1:
            if y<=hhy-2: return SHELL_L
            return SHELL if (x+y)%2==0 else SHELL_M
        return SKIN_A
    g.ellipse(hhx,hhy,3,2.5,hp)
    for dx in range(2,4): g.set(hhx+dx,hhy-1,SKIN_A)
    for dx in range(2,5): g.set(hhx+dx,hhy,SKIN_A)
    g.set(hhx+4,hhy,NOSE_A)
    if eye=="open": g.set(hhx+2,hhy,EYE_A)
    elif eye=="wide": g.rect(hhx+2,hhy-1,hhx+3,hhy,EYE_A); g.set(hhx+2,hhy-1,WHITE)
    else: g.set(hhx+1,hhy,OUT); g.set(hhx+2,hhy,OUT)
    if ears==0: g.rect(hhx-1,hhy-4,hhx,hhy-2,SKIN_D_A)
    if mouth:
        g.rect(hhx+2,hhy+2,hhx+4,hhy+1+mouth,MOUTH)
        if mouth>=2: g.rect(hhx+3,hhy+mouth,hhx+4,hhy+mouth,TONGUE)
        g.rect(hhx+2,hhy+2+mouth,hhx+4,hhy+2+mouth,SKIN_A)
    else: g.rect(hhx+2,hhy+2,hhx+3,hhy+2,SKIN_A)
    return g

def arm_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    scy=14+bob
    def sp(x,y):
        if y>scy+7: return None
        yt=scy-7*math.sqrt(max(0,1-((x-cx)/8)**2))
        if y-yt<1.2: return SHELL_L
        if int((y-scy)+(x-cx)**2/25)%3==0: return SHELL_D
        return SHELL
    g.ellipse(cx,scy,8,7,sp)
    hy=18+bob
    g.rect(10,hy-4,11,hy-1,SKIN_D_A); g.rect(20,hy-4,21,hy-1,SKIN_D_A)
    def hp(x,y):
        if y<=hy-1:
            if y<=hy-2: return SHELL_L
            return SHELL if (x+y)%2==0 else SHELL_M
        return SKIN_A
    g.ellipse(cx,hy,4,3,hp)
    if eye=="open": g.set(13,hy,EYE_A); g.set(18,hy,EYE_A)
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+1,16,hy+2,NOSE_A)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,21,x+1,b,SKIN_A); g.set(x,21,SKIN_D_A); g.rect(x-1,b,x+2,b,CLAW_A)
    return g

def arm_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,4,3,lambda x,y:SKIN_D_A)
    g.rect(11,3+bob,12,5+bob,SKIN_D_A); g.rect(19,3+bob,20,5+bob,SKIN_D_A)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,SKIN_A); g.set(x,20,SKIN_D_A); g.rect(x-1,b,x+2,b,CLAW_A)
    scy=15+bob
    def sp(x,y):
        if y>scy+7: return None
        yt=scy-7*math.sqrt(max(0,1-((x-cx)/8)**2))
        if y-yt<1.2: return SHELL_L
        if y>=scy+2: return SHELL if (x+y)%2==0 else SHELL_M
        if int((y-scy)+(x-cx)**2/28)%3==0: return SHELL_D
        return SHELL
    g.ellipse(cx,scy,8,7,sp)
    sway=(0,1,1,0,-1,-1)[f%6]
    for dx in (0,1): line(g,15+dx,20+bob,15+dx+sway,25,SKIN_D_A)
    return g

# --- 2. WOLF: Long, lean, pointed ears, bushy tail ---
WF=(120,120,120,255); WFL=(150,150,150,255); WFD=(90,90,90,255); WS=(200,180,160,255)
WE=(255,255,0,255); WN=(50,50,50,255); WC=(240,240,240,255)

def wolf_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # LONG lean body
    g.ellipse(15,15+bob,13,5,lambda x,y:WF)
    g.ellipse(15,14+bob,13,6,lambda x,y:WFD)
    # LONG snout
    hhx,hhy=26+hx,12+hd+bob; g.ellipse(hhx,hhy,6,3,lambda x,y:WFL)
    for dx in range(-4,6): g.set(hhx+dx,hhy+1,WS); g.set(hhx+dx,hhy+2,WS)
    g.set(hhx+5,hhy+1,WN)
    # POINTED ears
    g.rect(hhx-2,hhy-7,hhx-1,hhy-2,WFD); g.rect(hhx+2,hhy-7,hhx+3,hhy-2,WFD)
    g.set(hhx-2,hhy-7,WFL); g.set(hhx+3,hhy-7,WFL)
    if eye=="open": g.set(hhx+1,hhy-1,WE)
    else: g.rect(hhx+1,hhy-1,hhx+2,hhy-1,OUT)
    # 4 LONG legs
    LX=(7,20,4,17)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+2,b,WFD); g.rect(x-1,b,x+3,b,WC)
    # BUSHY tail
    line(g,3,15+bob,0,15+bob+8-tail,WFD,4)
    if mouth: g.rect(hhx+3,hhy+3,hhx+5,hhy+3+mouth,(200,50,50,255))
    return g

def wolf_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,12,6,lambda x,y:WF)
    hy=10+bob; g.ellipse(cx,hy,7,4,lambda x,y:WFL)
    g.rect(9,hy-7,11,hy-2,WFD); g.rect(20,hy-7,22,hy-2,WFD)
    g.set(9,hy-7,WFL); g.set(22,hy-7,WFL)
    for dx in range(-3,4): g.set(15+dx,hy+2,WS)
    g.set(18,hy+2,WN)
    if eye=="open": g.set(12,hy-1,WE); g.set(19,hy-1,WE)
    else: g.rect(11,hy-1,13,hy-1,OUT); g.rect(18,hy-1,20,hy-1,OUT)
    for x,l in ((7,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,WFD); g.rect(x-1,b,x+3,b,WC)
    return g

def wolf_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,7+bob,5,3,lambda x,y:WFL)
    g.rect(11,3+bob,12,5+bob,WFD); g.rect(19,3+bob,20,5+bob,WFD)
    g.set(11,3+bob,WF); g.set(20,3+bob,WF)
    g.ellipse(cx,15+bob,12,6,lambda x,y:WF)
    for x,l in ((7,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,WFD); g.rect(x-1,b,x+3,b,WC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,28,WFD,4)
    return g

# --- 3. FOX: Short, stocky, white-tipped tail ---
FF=(200,100,50,255); FFL=(230,130,80,255); FF_D=(170,80,30,255); FW=(255,255,255,255)
FE=(22,16,20,255); FN=(50,50,50,255); FC=(200,200,200,255)

def fox_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # SHORT stocky body
    g.ellipse(15,15+bob,10,6,lambda x,y:FF)
    g.ellipse(15,14+bob,10,7,lambda x,y:FF_D)
    # SHORT snout with white
    hhx,hhy=24+hx,12+hd+bob; g.ellipse(hhx,hhy,4,3,lambda x,y:FFL)
    for dx in range(-2,4): g.set(hhx+dx,hhy+1,FW); g.set(hhx+dx,hhy+2,FW)
    g.set(hhx+3,hhy+1,FN)
    # SHORT pointed ears with white tips
    g.rect(hhx-2,hhy-5,hhx-1,hhy-2,FF_D); g.rect(hhx+2,hhy-5,hhx+3,hhy-2,FF_D)
    g.set(hhx-2,hhy-5,FW); g.set(hhx+3,hhy-5,FW)
    if eye=="open": g.set(hhx,hhy-1,FE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # SHORT legs
    LX=(8,18,6,16)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+2,b,FF_D); g.rect(x-1,b,x+3,b,FC)
    # SHORT bushy tail with WHITE tip
    line(g,5,15+bob,1,15+bob+5-tail,FF_D,3); g.rect(0,15+bob+3,4,15+bob+5,FW)
    if mouth: g.rect(hhx+2,hhy+3,hhx+3,hhy+3+mouth,(200,50,50,255))
    return g

def fox_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,10,6,lambda x,y:FF)
    hy=10+bob; g.ellipse(cx,hy,5,4,lambda x,y:FFL)
    g.rect(10,hy-5,12,hy-2,FF_D); g.rect(19,hy-5,21,hy-2,FF_D)
    g.set(10,hy-5,FW); g.set(21,hy-5,FW)
    for dx in range(-1,3): g.set(15+dx,hy+2,FW)
    g.set(17,hy+2,FN)
    if eye=="open": g.set(12,hy,FE); g.set(19,hy,FE)
    else: g.rect(11,hy,13,hy,OUT); g.rect(18,hy,20,hy,OUT)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,FF_D); g.rect(x-1,b,x+3,b,FC)
    return g

def fox_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,7+bob,4,3,lambda x,y:FFL)
    g.rect(11,3+bob,12,5+bob,FF_D); g.rect(19,3+bob,20,5+bob,FF_D)
    g.set(11,3+bob,FW); g.set(20,3+bob,FW)
    g.ellipse(cx,15+bob,10,6,lambda x,y:FF)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,FF_D); g.rect(x-1,b,x+3,b,FC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,25,FF_D,3)
    g.rect(13+sway,23,17+sway,25,FW)
    return g

# --- 4. CAT: Arched back, whiskers, upright tail ---
CF=(200,180,160,255); CFL=(220,200,180,255); CFD=(180,160,140,255); CS=(255,200,180,255)
CE=(255,255,0,255); CN=(255,150,150,255); CC=(200,200,200,255)

def cat_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # ARCHED back - unique shape
    g.ellipse(15,15+bob,9,5,lambda x,y:CF)
    g.ellipse(15,14+bob,9,6,lambda x,y:CFD)
    # Extra arch
    line(g,10,12+bob,18,12+bob,CFD,2)
    # Head
    hhx,hhy=23+hx,11+hd+bob; g.ellipse(hhx,hhy,4,3,lambda x,y:CFL)
    # Cat ears
    g.rect(hhx-2,hhy-5,hhx-1,hhy-2,CFD); g.rect(hhx+1,hhy-5,hhx+2,hhy-2,CFD)
    g.set(hhx-2,hhy-5,CFL); g.set(hhx+2,hhy-5,CFL)
    for dx in range(-1,3): g.set(hhx+dx,hhy+1,CS); g.set(hhx+dx,hhy+2,CS)
    g.set(hhx+2,hhy+1,CN)
    if eye=="open": g.set(hhx,hhy-1,CE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # WHISKERS - unique feature
    if eye=="open":
        g.set(hhx-3,hhy,WHITE); g.set(hhx-4,hhy,WHITE)
        g.set(hhx+4,hhy,WHITE); g.set(hhx+5,hhy,WHITE)
    # Legs
    LX=(9,17,6,14)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+1,b,CFD); g.rect(x-1,b,x+2,b,CC)
    # UP RIGHT tail
    line(g,6,14+bob,5,14+bob-6+tail,CF,2)
    if mouth: g.rect(hhx+1,hhy+3,hhx+2,hhy+3+mouth,(200,100,100,255))
    return g

def cat_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,9,5,lambda x,y:CF)
    line(g,10,12+bob,20,12+bob,CFD,2)
    hy=10+bob; g.ellipse(cx,hy,5,4,lambda x,y:CFL)
    g.rect(10,hy-5,12,hy-2,CFD); g.rect(19,hy-5,21,hy-2,CFD)
    g.set(10,hy-5,CFL); g.set(21,hy-5,CFL)
    if eye=="open": g.set(12,hy,CE); g.set(19,hy,CE)
    else: g.rect(11,hy,13,hy,OUT); g.rect(18,hy,20,hy,OUT)
    g.rect(15,hy+2,16,hy+3,CN)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,CFD); g.rect(x-1,b,x+2,b,CC)
    g.set(8,hy,WHITE); g.set(7,hy,WHITE); g.set(9,hy,WHITE)
    g.set(22,hy,WHITE); g.set(21,hy,WHITE); g.set(23,hy,WHITE)
    return g

def cat_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,7+bob,4,3,lambda x,y:CFL)
    g.rect(11,3+bob,12,5+bob,CFD); g.rect(19,3+bob,20,5+bob,CFD)
    g.set(11,3+bob,CF); g.set(20,3+bob,CF)
    g.ellipse(cx,15+bob,9,5,lambda x,y:CF)
    line(g,10,12+bob,20,12+bob,CFD,2)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,CFD); g.rect(x-1,b,x+2,b,CC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,27,CF,2); g.set(15+sway,27,CFL)
    return g

# --- 5. RABBIT: Upright, long ears, short front legs ---
RF=(220,220,220,255); RFL=(240,240,240,255); RFD=(200,200,200,255); RI=(255,200,200,255)
RE=(255,50,50,255); RN=(255,150,150,255); RC=(240,240,240,255)

def rabbit_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # Round fluffy body
    g.ellipse(15,16+bob,8,7,lambda x,y:RF)
    # VERY LONG ears - unique
    hhx,hhy=22+hx,11+hd+bob; g.ellipse(hhx,hhy,4,3,lambda x,y:RFL)
    g.rect(hhx-4,hhy-8,hhx-1,hhy-2,RFL); g.rect(hhx+3,hhy-8,hhx+6,hhy-2,RFL)
    g.set(hhx-2,hhy-8,RI); g.set(hhx+5,hhy-8,RI)
    for dx in range(-1,3): g.set(hhx+dx,hhy+1,RI); g.set(hhx+dx,hhy+2,RI)
    g.set(hhx+2,hhy+1,RN)
    if eye=="open": g.set(hhx+1,hhy,RE)
    else: g.rect(hhx+1,hhy,hhx+2,hhy,OUT)
    # SHORT front legs, LONG back legs
    LX=(11,17,8,14)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        w=2 if i<2 else 1  # front legs thicker
        g.rect(x,20+bob,x+w,b,RFD); g.rect(x-1,b,x+w+1,b,RC)
    # Fluffy tail
    g.rect(1,16+bob+2,4,16+bob+4,RFL)
    if mouth: g.rect(hhx+1,hhy+3,hhx+2,hhy+3+mouth,(255,150,150,255))
    return g

def rabbit_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,16+bob,8,7,lambda x,y:RF)
    hy=9+bob; g.ellipse(cx,hy,5,4,lambda x,y:RFL)
    g.rect(8,hy-8,11,hy-2,RFL); g.rect(20,hy-8,23,hy-2,RFL)
    g.set(10,hy-8,RI); g.set(22,hy-8,RI)
    if eye=="open": g.set(12,hy,RE); g.set(19,hy,RE)
    else: g.rect(11,hy,13,hy,OUT); g.rect(18,hy,20,hy,OUT)
    g.rect(15,hy+2,16,hy+3,RN)
    for x,l in ((9,lifts[0]),(21,lifts[1])):
        b=25-l; w=2 if x<15 else 1
        g.rect(x,20,x+w,b,RFD); g.rect(x-1,b,x+w+1,b,RC)
    return g

def rabbit_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,4,3,lambda x,y:RFL)
    g.rect(11,2+bob,12,5+bob,RFD); g.rect(19,2+bob,20,5+bob,RFD)
    g.set(11,2+bob,RI); g.set(20,2+bob,RI)
    g.rect(9,0+bob,11,2+bob,RFL); g.rect(20,0+bob,22,2+bob,RFL)
    g.ellipse(cx,16+bob,8,7,lambda x,y:RF)
    for x,l in ((9,lifts[0]),(21,lifts[1])):
        b=25-l; w=2 if x<15 else 1
        g.rect(x,20,x+w,b,RFD); g.rect(x-1,b,x+w+1,b,RC)
    sway=(0,1,1,0,-1,-1)[f%6]; g.rect(14+sway,24,16+sway,26,RFL)
    return g

# --- 6. FISH: Horizontal, no legs, fins ---
FFISH=(255,100,50,255); FFISH_L=(255,130,80,255); FFISH_D=(200,60,20,255)
FISH_WHITE=(220,220,220,255); FISH_EYE=(22,16,20,255)

def fish_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # HORIZONTAL elongated body - completely different from all others
    g.ellipse(15,15+bob,14,4,lambda x,y:FFISH)
    g.ellipse(15,14+bob,14,5,lambda x,y:FFISH_D)
    # Forked tail
    line(g,0,15+bob,2,15+bob+5-tail,FFISH_D,2)
    line(g,0,15+bob,2,15+bob-5+tail,FFISH_D,2)
    # Head
    hhx,hhy=30+hx,14+hd+bob; g.ellipse(hhx,hhy,3,3,lambda x,y:FFISH_L)
    g.set(hhx+2,hhy,FISH_WHITE)  # mouth
    if eye=="open": g.set(hhx+1,hhy-1,FISH_EYE)
    else: g.rect(hhx+1,hhy-1,hhx+2,hhy-1,OUT)
    # Fins - unique to fish
    g.rect(20,13+bob,23,15+bob,FFISH_D)  # back fin
    g.rect(7,13+bob,10,15+bob,FFISH_D)  # front fin
    g.rect(15,10+bob,17,12+bob,FFISH_D)  # top fin
    g.rect(15,17+bob,17,19+bob,FFISH_D)  # bottom fin
    return g

def fish_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    # Oval from front
    g.ellipse(cx,15+bob,14,4,lambda x,y:FFISH)
    g.ellipse(cx,14+bob,14,5,lambda x,y:FFISH_D)
    hy=14+bob
    if eye=="open": g.set(13,hy,FISH_EYE); g.set(18,hy,FISH_EYE)
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+2,16,hy+3,FISH_WHITE)
    g.rect(8,hy-1,10,hy+1,FFISH_D)
    g.rect(21,hy-1,23,hy+1,FFISH_D)
    g.rect(15,hy-3,16,hy-1,FFISH_D)
    g.rect(15,hy+4,16,hy+6,FFISH_D)
    return g

def fish_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,15+bob,14,4,lambda x,y:FFISH)
    g.ellipse(cx,14+bob,14,5,lambda x,y:FFISH_D)
    g.ellipse(cx,7+bob,4,3,lambda x,y:FFISH_L)
    sway=(0,1,1,0,-1,-1)[f%6]
    line(g,15,15+bob,15+sway,20,FFISH_D,2)
    line(g,15,15+bob,15+sway,10,FFISH_D,2)
    g.rect(10,13+bob,12,15+bob,FFISH_D)
    g.rect(19,13+bob,21,15+bob,FFISH_D)
    return g

# --- 7. LIZARD: Very long, flat, splayed legs ---
LF=(50,150,50,255); LFL=(80,180,80,255); LF_D=(30,120,30,255)
LS=(200,255,200,255); LS_D=(170,220,170,255); LE=(255,100,100,255); LC=(200,200,200,255)

def lizard_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # VERY LONG flat body - unique silhouette
    g.ellipse(15,16+bob,14,4,lambda x,y:LF)
    g.ellipse(15,15+bob,14,5,lambda x,y:LF_D)
    # Small head
    hhx,hhy=28+hx,14+hd+bob; g.ellipse(hhx,hhy,3,2,lambda x,y:LFL)
    for dx in range(-1,2): g.set(hhx+dx,hhy+1,LS); g.set(hhx+dx,hhy+2,LS)
    g.set(hhx+1,hhy+1,LE)
    if eye=="open": g.set(hhx,hhy-1,(255,255,0,255))
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # SPLAYED legs - unique
    LX=(8,22,5,20)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+1,b,LF_D); g.rect(x-1,b,x+2,b,LC)
    # VERY LONG tail
    line(g,2,16+bob,0,16+bob+12-tail,LF_D,2)
    if mouth: g.rect(hhx,hhy+3,hhx+1,hhy+3+mouth,(200,50,50,255))
    return g

def lizard_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,16+bob,14,4,lambda x,y:LF)
    hy=13+bob; g.ellipse(cx,hy,4,2,lambda x,y:LFL)
    if eye=="open": g.set(13,hy,(255,255,0,255)); g.set(18,hy,(255,255,0,255))
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+2,16,hy+3,LE)
    for x,l in ((5,lifts[0]),(25,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,LF_D); g.rect(x-1,b,x+2,b,LC)
    return g

def lizard_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,4,3,lambda x,y:LFL)
    g.ellipse(cx,16+bob,14,4,lambda x,y:LF)
    for x,l in ((5,lifts[0]),(25,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,LF_D); g.rect(x-1,b,x+2,b,LC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,30,LF_D,2)
    return g

# --- 8. BEE: Small body, wings, 6 legs ---
BF=(255,255,0,255); BFL=(255,255,50,255); BFD=(230,230,0,255); BW=(255,255,255,255)
BEYE=(22,16,20,255); BC=(200,200,200,255)

def bee_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # SMALL oval body
    g.ellipse(15,15+bob,6,5,lambda x,y:BF)
    g.ellipse(15,14+bob,6,6,lambda x,y:BFD)
    # Stripes
    for i in range(-2,3):
        if i%2==0: g.rect(13,15+bob+i,17,15+bob+i,BFD)
    # Small head
    hhx,hhy=20+hx,13+hd+bob; g.ellipse(hhx,hhy,2,2,lambda x,y:BF)
    if eye=="open": g.set(hhx,hhy-1,BEYE); g.set(hhx+1,hhy-1,BEYE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # LARGE wings - unique
    g.rect(18,12+bob,26,15+bob,BW)
    g.rect(4,12+bob,12,15+bob,BW)
    # 6 legs (3 visible on each side)
    for i in range(3):
        x=8+i*2; b=max(20+bob,25-(i*2))
        g.rect(x,20+bob,x+1,b,BC)
    # Antennae
    g.set(hhx-1,hhy-3,BFD); g.set(hhx+2,hhy-3,BFD)
    return g

def bee_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,6,5,lambda x,y:BF)
    for i in range(-2,3):
        if i%2==0: g.rect(13,15+bob+i,17,15+bob+i,BFD)
    hy=12+bob; g.ellipse(cx,hy,3,2,lambda x,y:BF)
    if eye=="open": g.set(14,hy,BEYE); g.set(17,hy,BEYE)
    else: g.rect(13,hy,14,hy,OUT); g.rect(17,hy,18,hy,OUT)
    g.rect(10,hy-2,13,hy+1,BW); g.rect(18,hy-2,21,hy+1,BW)
    for i in range(3):
        x=8+i*5; b=25-lifts[i*2] if i*2<6 else 25
        g.rect(x,20,x+1,b,BC)
    return g

def bee_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,6,5,lambda x,y:BF)
    for i in range(-2,3):
        if i%2==0: g.rect(13,15+bob+i,17,15+bob+i,BFD)
    g.ellipse(cx,8+bob,3,2,lambda x,y:BF)
    for i in range(3):
        x=8+i*5; b=25-lifts[i*2] if i*2<6 else 25
        g.rect(x,20,x+1,b,BC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,24,BW,2)
    return g

# --- 9. BUTTERFLY: Tiny body, HUGE wings ---
BTF=(255,150,200,255); BTF_L=(255,180,220,255); BTF_D=(200,100,150,255)
BTEYE=(22,16,20,255)

def butterfly_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # TINY body
    g.ellipse(15,15+bob,2,6,lambda x,y:BTF)
    # HUGE wings - completely unique silhouette
    g.ellipse(8,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(22,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(5,15+bob,5,4,lambda x,y:BTF_D)
    g.ellipse(25,15+bob,5,4,lambda x,y:BTF_D)
    # Tiny head
    hhx,hhy=15,10+hd+bob; g.ellipse(hhx,hhy,2,2,lambda x,y:BTF_D)
    if eye=="open": g.set(hhx,hhy-1,BTEYE)
    else: g.set(hhx,hhy-1,OUT)
    # Long antennae
    g.set(hhx-1,hhy-4,BTF_D); g.set(hhx+1,hhy-4,BTF_D)
    # 6 tiny legs
    for i in range(3):
        x=13+i*2; g.set(x,22+bob,BTF_D)
    return g

def butterfly_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,15+bob,2,6,lambda x,y:BTF)
    g.ellipse(8,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(23,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(5,15+bob,5,4,lambda x,y:BTF_D)
    g.ellipse(26,15+bob,5,4,lambda x,y:BTF_D)
    hy=10+bob; g.ellipse(cx,hy,2,2,lambda x,y:BTF_D)
    if eye=="open": g.set(14,hy,BTEYE); g.set(17,hy,BTEYE)
    else: g.rect(13,hy,14,hy,OUT); g.rect(17,hy,18,hy,OUT)
    g.set(14,hy-3,BTF_D); g.set(17,hy-3,BTF_D)
    for i in range(3):
        x=13+i*3; g.set(x,22,BTF_D)
    return g

def butterfly_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,15+bob,2,6,lambda x,y:BTF)
    g.ellipse(8,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(23,12+bob,8,6,lambda x,y:BTF_L)
    g.ellipse(5,15+bob,5,4,lambda x,y:BTF_D)
    g.ellipse(26,15+bob,5,4,lambda x,y:BTF_D)
    g.ellipse(cx,8+bob,2,2,lambda x,y:BTF_D)
    sway=(0,1,1,0,-1,-1)[f%6]
    g.set(15+sway,22,WHITE); g.set(15+sway,23,WHITE)
    for i in range(3):
        x=13+i*3; g.set(x,22,BTF_D)
    return g

# --- 10. SPIDER: Round body, 8 long legs ---
SF=(50,50,50,255); SF_L=(80,80,80,255); SF_D=(30,30,30,255)
SS=(200,180,160,255); SS_D=(160,140,120,255); SE=(255,255,0,255); SC=(200,200,200,255)

def spider_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # Round abdomen
    g.ellipse(15,16+bob,7,5,lambda x,y:SF)
    # Smaller cephalothorax
    g.ellipse(15,12+bob,5,3,lambda x,y:SF_L)
    # 8 LONG legs - completely unique
    angles=[0,45,90,135,180,225,270,315]
    for angle in angles:
        rad=math.radians(angle); lx=15+math.cos(rad)*6; ly=12+bob+math.sin(rad)*6
        line(g,int(lx),int(ly),int(lx+math.cos(rad)*8),int(ly+math.sin(rad)*8),SF_D,1)
    # Head
    hhx,hhy=15,11+hd+bob; g.ellipse(hhx,hhy,2,2,lambda x,y:SF_L)
    if eye=="open": g.set(hhx-1,hhy-1,SE); g.set(hhx+1,hhy-1,SE)
    else: g.rect(hhx-1,hhy-1,hhx+1,hhy-1,OUT)
    return g

def spider_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,16+bob,7,5,lambda x,y:SF)
    g.ellipse(cx,12+bob,5,3,lambda x,y:SF_L)
    # 8 legs pointing out
    for angle in [0,45,90,135,180,225,270,315]:
        rad=math.radians(angle); lx=cx+math.cos(rad)*6; ly=12+bob+math.sin(rad)*6
        line(g,int(lx),int(ly),int(lx+math.cos(rad)*8),int(ly+math.sin(rad)*8),SF_D,1)
    hy=11+bob; g.ellipse(cx,hy,3,2,lambda x,y:SF_L)
    if eye=="open": g.set(14,hy,SE); g.set(17,hy,SE)
    else: g.rect(13,hy,14,hy,OUT); g.rect(17,hy,18,hy,OUT)
    return g

def spider_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,16+bob,7,5,lambda x,y:SF)
    g.ellipse(cx,12+bob,5,3,lambda x,y:SF_L)
    for angle in [0,45,90,135,180,225,270,315]:
        rad=math.radians(angle); lx=cx+math.cos(rad)*6; ly=12+bob+math.sin(rad)*6
        line(g,int(lx),int(ly),int(lx+math.cos(rad)*8),int(ly+math.sin(rad)*8),SF_D,1)
    g.ellipse(cx,8+bob,3,2,lambda x,y:SF_L)
    return g

# --- 11. FROG: Squat, bulging eyes, long legs ---
FRG=(50,200,50,255); FRG_L=(80,220,80,255); FRG_D=(30,180,30,255)
FS=(255,255,200,255); FS_D=(220,220,170,255); FRE=(255,255,255,255); FRN=(255,100,50,255)

def frog_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # SQUAT round body
    g.ellipse(15,17+bob,8,6,lambda x,y:FRG)
    # LARGE head
    hhx,hhy=22+hx,12+hd+bob; g.ellipse(hhx,hhy,6,5,lambda x,y:FRG_L)
    # BULGING eyes - unique
    if eye=="open":
        g.rect(hhx+2,hhy-2,hhx+3,hhy-1,FRE)
        g.rect(hhx-1,hhy-2,hhx,hhy-1,FRE)
        g.set(hhx+2,hhy-2,BLACK); g.set(hhx-1,hhy-2,BLACK)
    else: g.rect(hhx-1,hhy-1,hhx+3,hhy-1,OUT)
    g.rect(hhx,hhy+1,hhx+2,hhy+2,FRN)
    if mouth: g.rect(hhx,hhy+3,hhx+2,hhy+3+mouth,(255,50,50,255))
    # LONG back legs, SHORT front legs
    LX=(12,18,8,14)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        w=1 if i<2 else 2  # back legs thicker
        g.rect(x,20+bob,x+w,b,FRG_D); g.rect(x-1,b,x+w+1,b,FS_D)
    return g

def frog_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,17+bob,8,6,lambda x,y:FRG)
    hy=11+bob; g.ellipse(cx,hy,7,5,lambda x,y:FRG_L)
    if eye=="open":
        g.rect(13,hy-2,14,hy-1,FRE); g.rect(17,hy-2,18,hy-1,FRE)
        g.set(13,hy-2,BLACK); g.set(17,hy-2,BLACK)
    else: g.rect(12,hy-1,14,hy-1,OUT); g.rect(17,hy-1,19,hy-1,OUT)
    g.rect(15,hy+2,16,hy+3,FRN)
    for x,l in ((10,lifts[0]),(21,lifts[1])):
        b=25-l; w=1 if x<15 else 2
        g.rect(x,20,x+w,b,FRG_D); g.rect(x-1,b,x+w+1,b,FS_D)
    return g

def frog_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,9+bob,6,4,lambda x,y:FRG_L)
    g.ellipse(cx,17+bob,8,6,lambda x,y:FRG)
    for x,l in ((10,lifts[0]),(21,lifts[1])):
        b=25-l; w=1 if x<15 else 2
        g.rect(x,20,x+w,b,FRG_D); g.rect(x-1,b,x+w+1,b,FS_D)
    sway=(0,1,1,0,-1,-1)[f%6]; g.rect(14+sway,24,16+sway,26,FRG_L)
    return g

# --- 12. DRAGON: Long neck, wings, spiked tail ---
DF=(200,50,50,255); DF_L=(230,80,80,255); DF_D=(140,20,20,255)
DS=(255,255,200,255); DS_D=(220,220,170,255); DE=(255,255,0,255); DC=(255,255,200,255)

def dragon_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # Body
    g.ellipse(15,15+bob,10,5,lambda x,y:DF)
    g.ellipse(15,14+bob,10,6,lambda x,y:DF_D)
    # Spikes down back - unique
    for i in range(6): g.set(14+i,11+bob+i//2,DF_L)
    # LONG neck
    line(g,24,13+bob,28,10+bob,DF_L,3)
    # Head with horn
    hhx,hhy=29+hx,10+hd+bob; g.ellipse(hhx,hhy,4,3,lambda x,y:DF_L)
    g.rect(hhx+1,hhy-4,hhx+2,hhy-1,DF_L)  # horn
    if eye=="open": g.set(hhx+1,hhy-1,DE)
    else: g.rect(hhx+1,hhy-1,hhx+2,hhy-1,OUT)
    for dx in range(-1,3): g.set(hhx+dx,hhy+1,DS); g.set(hhx+dx,hhy+2,DS)
    g.set(hhx+2,hhy+2,DE)
    # Wings
    g.rect(18,12+bob,24,15+bob,DS)
    # 4 legs
    LX=(9,18,6,15)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+2,b,DF_D); g.rect(x-1,b,x+3,b,DC)
    # Spiked tail
    line(g,3,15+bob,0,15+bob+8-tail,DF_D,2)
    g.set(0,15+bob+6,DF_L); g.set(1,15+bob+4,DF_L)
    if mouth: g.rect(hhx,hhy+3,hhx+2,hhy+3+mouth,(255,100,0,255))
    return g

def dragon_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,10,5,lambda x,y:DF)
    for i in range(6): g.set(14+i,11+bob+i//2,DF_L)
    hy=10+bob; g.ellipse(cx,hy,6,4,lambda x,y:DF_L)
    g.rect(15,hy-5,16,hy-1,DF_L)
    if eye=="open": g.set(13,hy-1,DE); g.set(18,hy-1,DE)
    else: g.rect(12,hy-1,13,hy-1,OUT); g.rect(18,hy-1,19,hy-1,OUT)
    g.rect(15,hy+2,16,hy+3,DE)
    g.rect(10,hy-3,12,hy+1,DS); g.rect(19,hy-3,21,hy+1,DS)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,DF_D); g.rect(x-1,b,x+3,b,DC)
    return g

def dragon_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,5,4,lambda x,y:DF_L)
    g.ellipse(cx,15+bob,10,5,lambda x,y:DF)
    for i in range(6): g.set(14+i,11+bob+i//2,DF_L)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+2,b,DF_D); g.rect(x-1,b,x+3,b,DC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,26,DF_D,2)
    g.set(15+sway,24,DF_L)
    return g

# --- 13. UNICORN: Horse-like, horn, mane ---
UF=(255,255,255,255); UFL=(255,255,255,255); UFD=(230,230,230,255)
US=(255,200,220,255); US_D=(220,170,190,255); UE=(255,100,150,255); UN=(255,150,200,255)
UC=(240,240,240,255)

def unicorn_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    g.ellipse(15,15+bob,11,5,lambda x,y:UF)
    g.ellipse(15,14+bob,11,6,lambda x,y:UFD)
    # Mane
    for i in range(5): g.set(17+i,11+bob+i,US)
    # Head with horn
    hhx,hhy=25+hx,11+hd+bob; g.ellipse(hhx,hhy,5,4,lambda x,y:UFL)
    line(g,hhx+2,hhy-5,hhx+2,hhy-8,US,2)
    g.set(hhx+2,hhy-8,UE)
    g.rect(hhx-2,hhy-5,hhx-1,hhy-2,US)
    if eye=="open": g.set(hhx,hhy-1,UE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    for dx in range(-1,3): g.set(hhx+dx,hhy+1,US); g.set(hhx+dx,hhy+2,US)
    g.set(hhx+2,hhy+1,UN)
    # 4 legs
    LX=(8,19,5,16)
    for i,lx in enumerate(LX):
        x=lx; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+1,b,UFD); g.rect(x-1,b,x+2,b,UC)
    # Flowing tail
    line(g,3,15+bob,0,15+bob+6-tail,UFD,2)
    g.set(0,15+bob+5,US)
    if mouth: g.rect(hhx,hhy+3,hhx+2,hhy+3+mouth,(255,150,200,255))
    return g

def unicorn_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,11,5,lambda x,y:UF)
    for i in range(5): g.set(17+i,11+bob+i,US)
    hy=10+bob; g.ellipse(cx,hy,6,4,lambda x,y:UFL)
    line(g,15,hy-6,15,hy-9,US,2); g.set(15,hy-9,UE)
    g.rect(11,hy-7,12,hy-2,US)
    if eye=="open": g.set(13,hy,UE); g.set(18,hy,UE)
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+2,16,hy+3,UN)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,UFD); g.rect(x-1,b,x+2,b,UC)
    return g

def unicorn_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,5,4,lambda x,y:UFL)
    g.ellipse(cx,15+bob,11,5,lambda x,y:UF)
    for i in range(5): g.set(17+i,11+bob+i,US)
    for x,l in ((8,lifts[0]),(22,lifts[1])):
        b=25-l; g.rect(x,20,x+1,b,UFD); g.rect(x-1,b,x+2,b,UC)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,26,UFD,2)
    g.set(15+sway,24,US)
    return g

# --- 14. PENGUIN: Upright, 2 legs, flippers ---
PF=(50,50,80,255); PF_L=(80,80,110,255); PF_D=(30,30,60,255)
PS=(255,255,255,255); PS_D=(220,220,220,255); PE=(22,16,20,255); PN=(255,150,50,255)
PC=(255,200,100,255)

def penguin_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # UPRIGHT body
    g.ellipse(15,14+bob,8,8,lambda x,y:PF)
    g.ellipse(15,15+bob,7,6,lambda x,y:PS)
    # Head
    hhx,hhy=15,8+hd+bob; g.ellipse(hhx,hhy,4,4,lambda x,y:PF_L)
    # Beak
    g.rect(hhx+2,hhy,hhx+4,hhy+2,PN)
    if eye=="open": g.set(hhx,hhy-1,PE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # 2 legs (penguins are bipedal)
    LX=(12,18,0,0)  # only 2 legs visible
    for i in range(2):
        x=LX[i]; b=max(23+bob,25-L[i][1])
        g.rect(x,23+bob,x+2,b,PF_D); g.rect(x-1,b,x+3,b,PC)
    # Flippers
    g.rect(20,13+bob,24,16+bob,PF_L)
    g.rect(6,13+bob,10,16+bob,PF_L)
    if mouth: g.rect(hhx+3,hhy+2,hhx+4,hhy+2+mouth,(255,100,0,255))
    return g

def penguin_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,14+bob,8,8,lambda x,y:PF)
    g.ellipse(cx,15+bob,7,6,lambda x,y:PS)
    hy=9+bob; g.ellipse(cx,hy,5,4,lambda x,y:PF_L)
    if eye=="open": g.set(13,hy,PE); g.set(18,hy,PE)
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+2,16,hy+4,PN)
    for x in [10,21]:
        b=25-lifts[0] if x==10 else 25-lifts[1]
        g.rect(x,23,x+2,b,PF_D); g.rect(x-1,b,x+3,b,PC)
    g.rect(10,hy-1,12,hy+1,PF_L); g.rect(19,hy-1,21,hy+1,PF_L)
    return g

def penguin_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,5,4,lambda x,y:PF_L)
    g.ellipse(cx,14+bob,8,8,lambda x,y:PF)
    g.ellipse(cx,15+bob,7,6,lambda x,y:PS)
    for x in [10,21]:
        b=25-lifts[0] if x==10 else 25-lifts[1]
        g.rect(x,23,x+2,b,PF_D); g.rect(x-1,b,x+3,b,PC)
    sway=(0,1,1,0,-1,-1)[f%6]; g.rect(14+sway,24,16+sway,26,PF_L)
    return g

# --- 15. OWL: Round body, large head, 2 legs ---
OF=(150,100,50,255); OF_L=(180,130,80,255); OF_D=(120,70,30,255)
OS=(255,255,200,255); OS_D=(220,220,170,255); OE=(255,255,0,255); ON=(255,200,100,255)
OC=(200,200,200,255)

def owl_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # ROUND body
    g.ellipse(15,15+bob,9,7,lambda x,y:OF)
    # LARGE head
    hhx,hhy=21+hx,10+hd+bob; g.ellipse(hhx,hhy,7,6,lambda x,y:OF_L)
    # Tufts
    g.rect(hhx-2,hhy-6,hhx-1,hhy-3,OF_L)
    g.rect(hhx+2,hhy-6,hhx+3,hhy-3,OF_L)
    # LARGE eyes
    if eye=="open":
        g.rect(hhx,hhy-1,hhx+1,hhy+1,OE)
        g.rect(hhx+3,hhy-1,hhx+4,hhy+1,OE)
        g.set(hhx,hhy,BLACK); g.set(hhx+3,hhy,BLACK)
    else: g.rect(hhx,hhy,hhx+4,hhy,OUT)
    # Beak
    g.rect(hhx+1,hhy+2,hhx+3,hhy+3,ON)
    # 2 legs
    LX=(12,18,0,0)
    for i in range(2):
        x=LX[i]; b=max(20+bob,25-L[i][1])
        g.rect(x,20+bob,x+1,b,OF_D); g.rect(x-1,b,x+2,b,OC)
    # Short tail
    g.rect(1,15+bob,4,15+bob+2,OF_D)
    if mouth: g.rect(hhx+2,hhy+3,hhx+3,hhy+3+mouth,(255,150,0,255))
    return g

def owl_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,15+bob,9,7,lambda x,y:OF)
    hy=9+bob; g.ellipse(cx,hy,8,7,lambda x,y:OF_L)
    g.rect(10,hy-6,12,hy-3,OF_L); g.rect(19,hy-6,21,hy-3,OF_L)
    if eye=="open":
        g.rect(12,hy-1,14,hy+1,OE); g.rect(17,hy-1,19,hy+1,OE)
        g.set(12,hy,BLACK); g.set(17,hy,BLACK)
    else: g.rect(11,hy,14,hy,OUT); g.rect(17,hy,20,hy,OUT)
    g.rect(14,hy+2,17,hy+3,ON)
    for x in [11,20]:
        b=25-lifts[0] if x==11 else 25-lifts[1]
        g.rect(x,20,x+1,b,OF_D); g.rect(x-1,b,x+2,b,OC)
    return g

def owl_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,8+bob,7,4,lambda x,y:OF_L)
    g.ellipse(cx,15+bob,9,7,lambda x,y:OF)
    g.rect(11,2+bob,12,5+bob,OF_L); g.rect(19,2+bob,20,5+bob,OF_L)
    for x in [11,20]:
        b=25-lifts[0] if x==11 else 25-lifts[1]
        g.rect(x,20,x+1,b,OF_D); g.rect(x-1,b,x+2,b,OC)
    sway=(0,1,1,0,-1,-1)[f%6]; g.rect(14+sway,24,16+sway,26,OF_L)
    return g

# --- 16. LADYBUG: Perfect circle, 6 legs, spots ---
LFB=(255,50,50,255); LFB_L=(255,80,80,255); LFB_D=(230,30,30,255)
LSB=(0,0,0,255); LEYE=(22,16,20,255)

def ladybug_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # PERFECT circle body
    g.ellipse(15,16+bob,8,7,lambda x,y:LFB)
    # Spots - unique pattern
    g.rect(12,13+bob,14,14+bob,LSB); g.rect(16,13+bob,18,14+bob,LSB)
    g.rect(13,15+bob,14,16+bob,LSB); g.rect(17,15+bob,18,16+bob,LSB)
    g.rect(14,17+bob,16,18+bob,LSB)
    # Small head
    hhx,hhy=22+hx,13+hd+bob; g.ellipse(hhx,hhy,3,3,lambda x,y:LFB_L)
    if eye=="open": g.set(hhx,hhy-1,LEYE); g.set(hhx+1,hhy-1,LEYE)
    else: g.rect(hhx,hhy-1,hhx+1,hhy-1,OUT)
    # 6 legs (3 visible)
    for i in range(3):
        x=10+i*3; b=max(20+bob,25-(i*2))
        g.rect(x,20+bob,x+1,b,LSB)
    return g

def ladybug_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,16+bob,8,7,lambda x,y:LFB)
    g.rect(12,13+bob,14,14+bob,LSB); g.rect(16,13+bob,18,14+bob,LSB)
    g.rect(13,15+bob,14,16+bob,LSB); g.rect(17,15+bob,18,16+bob,LSB)
    g.rect(14,17+bob,16,18+bob,LSB)
    hy=12+bob; g.ellipse(cx,hy,4,3,lambda x,y:LFB_L)
    if eye=="open": g.set(14,hy,LEYE); g.set(17,hy,LEYE)
    else: g.rect(13,hy,14,hy,OUT); g.rect(17,hy,18,hy,OUT)
    for i in range(3):
        x=10+i*5; b=25-lifts[i*2] if i*2<6 else 25
        g.rect(x,20,x+1,b,LSB)
    return g

def ladybug_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]; lifts=[LIFT[(f+o)%6] for o in (0,3)]
    g.ellipse(cx,16+bob,8,7,lambda x,y:LFB)
    g.rect(12,13+bob,14,14+bob,LSB); g.rect(16,13+bob,18,14+bob,LSB)
    g.rect(13,15+bob,14,16+bob,LSB); g.rect(17,15+bob,18,16+bob,LSB)
    g.rect(14,17+bob,16,18+bob,LSB)
    g.ellipse(cx,8+bob,4,3,lambda x,y:LFB_L)
    for i in range(3):
        x=10+i*5; b=25-lifts[i*2] if i*2<6 else 25
        g.rect(x,20,x+1,b,LSB)
    return g

# --- 17. SNAKE: S-curve, no legs, long tongue ---
SF=(50,150,50,255); SF_L=(80,180,80,255); SF_D=(30,120,30,255)
SS=(255,255,200,255); SS_D=(220,220,170,255); SE=(255,255,0,255); SN=(255,100,50,255)

def snake_side(bob=0,legs=None,hd=0,hx=0,eye="open",mouth=0,tail=0,ears=0):
    g=Grid(); L=[(0,0)]*4 if legs is None else legs
    # S-curve body - completely unique
    line(g,5,15+bob,28,15+bob,SF,3)
    line(g,5,15+bob+1,28,15+bob+1,SF_D,2)
    line(g,5,15+bob-1,28,15+bob-1,SF_L,2)
    # Curve the body
    for i in range(5):
        y=15+bob+math.sin(i*0.5)*3
        g.set(10+i,int(y),SF_D)
        g.set(10+i,int(y)+1,SF_D)
    # Head
    hhx,hhy=28+hx,14+hd+bob; g.ellipse(hhx,hhy,4,3,lambda x,y:SF_L)
    # Tongue
    if mouth:
        line(g,hhx+2,hhy+2,hhx+4,hhy+2+mouth,SN,1)
        g.set(hhx+4,hhy+2+mouth,SE)
    # Eye
    if eye=="open": g.set(hhx+1,hhy-1,SE)
    else: g.rect(hhx+1,hhy-1,hhx+2,hhy-1,OUT)
    # Pointed tail
    line(g,4,15+bob,1,15+bob+3-tail,SF_D,2)
    return g

def snake_front(f=0,eye="open"):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    # Coiled body
    g.ellipse(cx,15+bob,10,6,lambda x,y:SF)
    g.ellipse(cx,14+bob,10,7,lambda x,y:SF_D)
    hy=10+bob; g.ellipse(cx,hy,5,4,lambda x,y:SF_L)
    if eye=="open": g.set(13,hy,SE); g.set(18,hy,SE)
    else: g.rect(12,hy,13,hy,OUT); g.rect(18,hy,19,hy,OUT)
    g.rect(15,hy+2,16,hy+3,SN)
    if f%2==0: g.set(16,hy+4,SE)
    return g

def snake_back(f=0):
    g=Grid(); cx=15.5; bob=(0,0,-1,0,0,-1)[f%6]
    g.ellipse(cx,15+bob,10,6,lambda x,y:SF)
    g.ellipse(cx,14+bob,10,7,lambda x,y:SF_D)
    g.ellipse(cx,8+bob,4,3,lambda x,y:SF_L)
    sway=(0,1,1,0,-1,-1)[f%6]; line(g,15,20+bob,15+sway,26,SF_D,2)
    return g


# ================================================================
# ANIMAL REGISTRY
# ================================================================

ANIMAL_SIDES = {
    "armadillo": arm_side, "wolf": wolf_side, "fox": fox_side, "cat": cat_side,
    "rabbit": rabbit_side, "fish": fish_side, "lizard": lizard_side, "bee": bee_side,
    "butterfly": butterfly_side, "spider": spider_side, "frog": frog_side,
    "dragon": dragon_side, "unicorn": unicorn_side, "penguin": penguin_side,
    "owl": owl_side, "ladybug": ladybug_side, "snake": snake_side,
}

ANIMAL_FRONTS = {
    "armadillo": arm_front, "wolf": wolf_front, "fox": fox_front, "cat": cat_front,
    "rabbit": rabbit_front, "fish": fish_front, "lizard": lizard_front, "bee": bee_front,
    "butterfly": butterfly_front, "spider": spider_front, "frog": frog_front,
    "dragon": dragon_front, "unicorn": unicorn_front, "penguin": penguin_front,
    "owl": owl_front, "ladybug": ladybug_front, "snake": snake_front,
}

ANIMAL_BACKS = {
    "armadillo": arm_back, "wolf": wolf_back, "fox": fox_back, "cat": cat_back,
    "rabbit": rabbit_back, "fish": fish_back, "lizard": lizard_back, "bee": bee_back,
    "butterfly": butterfly_back, "spider": spider_back, "frog": frog_back,
    "dragon": dragon_back, "unicorn": unicorn_back, "penguin": penguin_back,
    "owl": owl_back, "ladybug": ladybug_back, "snake": snake_back,
}

ANIMALS = list(ANIMAL_SIDES.keys())


def get_side(animal="armadillo"): return ANIMAL_SIDES.get(animal, arm_side)
def get_front(animal="armadillo"): return ANIMAL_FRONTS.get(animal, arm_front)
def get_back(animal="armadillo"): return ANIMAL_BACKS.get(animal, arm_back)


# ================================================================
# POSES AND ANIMATIONS
# ================================================================

def stand(idx=0, blink=False, animal="armadillo"):
    sf = get_side(animal)
    return sf(bob=0, legs=[(0,0)]*4, hd=0, hx=0, eye="closed" if blink else "open", mouth=0,
               tail=(0,1,2,1,0,-1,-2,-1)[idx%8], ears=0)

def sniff(idx, animal="armadillo"):
    i=idx%4; sf=get_side(animal)
    return sf(bob=0, legs=[(0,0)]*4, hd=(0,1,0,1)[i], hx=(0,1,0,1)[i],
               eye="open", mouth=0, tail=(0,1,0,-1)[i], ears=0)

def yawn(idx, animal="armadillo"):
    i=idx%8; mouth=(0,1,2,2,2,2,1,0)[i]; sf=get_side(animal)
    return sf(bob=0, legs=[(0,0)]*4,
               hd=-1 if 2<=i<=5 else 0, hx=1 if 2<=i<=5 else 0,
               eye="closed" if 1<=i<=6 else "open", mouth=mouth,
               ears=-1 if 2<=i<=5 else 0, tail=-1)

def dig(idx, animal="armadillo"):
    i=idx%4; a=(2,0,2,0)[i]; b=(0,2,0,2)[i]
    legs=[(0,0),(b,-2 if b else 0),(0,0),(a,-2 if a else 0)]
    sf=get_side(animal)
    g=sf(bob=0, legs=legs, hd=3, hx=1, eye="open", mouth=0, tail=(0,1,0,1)[i], ears=-1)
    for (x,y) in DIRT_FRAMES[i]: g.rect(x,y,x+1,y+1,DIRT)
    return g

def alert(idx, animal="armadillo"):
    i=idx%3; bob=(0,-3,0)[i]
    legs=[(0,0)]*4 if i!=1 else [(2,0)]*4
    sf=get_side(animal)
    g=sf(bob=bob, legs=legs, hd=0, hx=0, eye="wide", mouth=0, tail=2, ears=1)
    g.stamp(25,0,BANG,RED)
    return g

def happy(idx, animal="armadillo"):
    i=idx%4; sf=get_side(animal)
    g=sf(bob=(0,-1,0,-1)[i], legs=[(0,0)]*4, hd=-1, hx=0, eye="closed", mouth=0,
          tail=(2,-2,2,-2)[i], ears=1)
    for k in range(2):
        age=(idx*2+k*6)%12
        g.stamp(21+k*6-age//4,8-age//2,HEART_PX,HEART)
    return g

def curl1(animal="armadillo"):
    sf=get_side(animal)
    return sf(bob=1, legs=[(1,0)]*4, hd=3, hx=-2, eye="closed", mouth=0, tail=-1, ears=-1)

def ball(rot=0.0, squish=0, snout=False, tailtip=False, animal="armadillo"):
    g=Grid(); cx,r=15.5,9; ry=r-squish; cy=25.5-ry; ca,sa=math.cos(rot),math.sin(rot)
    colors={"armadillo":(SHELL,SHELL_L,SHELL_M,SHELL_D,SKIN_A,SKIN_D_A,NOSE_A,CLAW_A),
           "wolf":(WF,WFL,WFD,WF,WS,WS,WN,WC),"fox":(FF,FFL,FF_D,FF,FW,FW,FN,FC),
           "cat":(CF,CFL,CFD,CF,CS,CS,CN,CC),"rabbit":(RF,RFL,RFD,RF,RI,RI,RN,RC),
           "fish":(FFISH,FFISH_L,FFISH_D,FFISH,FISH_WHITE,FISH_WHITE,FISH_WHITE,FFISH_D),
           "lizard":(LF,LFL,LF_D,LF,LS,LS_D,LE,LC),"bee":(BF,BFL,BFD,BF,BW,BW,BLACK,BC),
           "butterfly":(BTF,BTF_L,BTF_D,BTF,BTF,BTF,BTEYE,BTF_D),
           "spider":(SF,SF_L,SF_D,SF,SS,SS_D,SE,SC),"frog":(FRG,FRG_L,FRG_D,FRG,FS,FS_D,SE,SS_D),
           "dragon":(DF,DF_L,DF_D,DF,DS,DS_D,DE,DC),"unicorn":(UF,UFL,UFD,UF,US,US_D,UE,UC),
           "penguin":(PF,PF_L,PF_D,PF,PS,PS_D,PN,PC),"owl":(OF,OF_L,OF_D,OF,OS,OS_D,OE,OC),
           "ladybug":(LFB,LFB_L,LFB_D,LFB,LSB,LSB,LEYE,LSB),"snake":(SF,SF_L,SF_D,SF,SS,SS_D,SE,SS_D)}
    bc,bl,bm,bd,sc,sd,nc,cc=colors.get(animal,colors["armadillo"])
    def px(x,y):
        if math.hypot(x-(cx-3),y-(cy-4))<2.4: return bl
        u=(x-cx)*ca+(y-cy)*sa
        if abs(u-4*round(u/4))<0.75: return bd
        if (x-cx)+(y-cy)>8: return bm
        return bc
    g.ellipse(cx,cy,r,ry,px)
    if snout: g.rect(24,20,26,22,sc); g.set(26,21,nc)
    if tailtip: g.rect(4,21,7,22,sd)
    return g

def curl2(animal="armadillo"): return ball(rot=0.35, snout=True, tailtip=True, animal=animal)

def sleep_frame(f, animal="armadillo"):
    squish=(0,0,1,1)[(f//2)%4]
    g=ball(rot=0.35, squish=squish, snout=True, tailtip=True, animal=animal)
    for k in range(2):
        age=(f+4*k)%8; y=11-age; x=22+age//2+k
        if y>=0: g.stamp(x,y,Z4 if age<5 else Z3,ZCOL)
    return g

def walk_side(f, tilt=0, animal="armadillo"):
    bob=(0,0,-1,0,0,-1)[f%6]; sf=get_side(animal)
    return sf(bob=bob, legs=walk_legs(f), hd=tilt, hx=0,
               eye="open", mouth=0, tail=(0,1,0,-1,0,1)[f%6], ears=1 if tilt<0 else 0)

def walk_front(f, animal="armadillo"): return get_front(animal)(f=f, eye="open")
def walk_back(f, animal="armadillo"): return get_back(animal)(f=f)

def build(name, idx=0, tilt=0, blink=False, animal="armadillo"):
    if name=="walk_side": g=walk_side(idx,tilt,animal)
    elif name=="walk_front": g=walk_front(idx,animal)
    elif name=="walk_back": g=walk_back(idx,animal)
    elif name=="stand": g=stand(idx,blink,animal)
    elif name=="stand_front":
        ff=get_front(animal); g=ff(f=0,eye="closed" if blink else "open")
    elif name=="sniff": g=sniff(idx,animal)
    elif name=="yawn": g=yawn(idx,animal)
    elif name=="dig": g=dig(idx,animal)
    elif name=="alert": g=alert(idx,animal)
    elif name=="happy": g=happy(idx,animal)
    elif name=="curl1": g=curl1(animal)
    elif name=="curl2": g=curl2(animal)
    elif name=="ball": g=ball(rot=idx*math.pi/8,animal=animal)
    elif name=="sleep": g=sleep_frame(idx,animal)
    else: raise ValueError(name)
    g.outline(); return g


# ================================================================
# ACCESSORIES
# ================================================================

def render_accessory(g, accessory, animal="armadillo"):
    if accessory=="none": return
    ac=AP
    hy=8
    if animal in ["fish","snake"]: hy=10
    elif animal in ["lizard","spider","frog","dragon","unicorn","penguin","owl"]: hy=9
    elif animal in ["bee","butterfly"]: hy=11
    
    if accessory=="tophat":
        g.rect(13,hy-6,19,hy-4,ac["tophat"])
        g.rect(14,hy-4,18,hy-2,ac["tophat"])
        g.rect(12,hy-2,20,hy,ac["tophat"])
        g.rect(11,hy,21,hy+2,ac["tophat"])
        g.rect(12,hy+2,20,hy+3,ac["tophat_trim"])
    elif accessory=="bow":
        g.rect(14,hy-2,15,hy,ac["bow"])
        g.rect(16,hy-2,17,hy,ac["bow"])
        g.rect(15,hy-1,16,hy+1,ac["bow"])
        g.rect(14,hy+1,17,hy+2,ac["bow"])
        g.rect(15,hy,16,hy+1,ac["bow_center"])
    elif accessory=="glasses":
        g.rect(12,hy+3,13,hy+4,ac["glasses"])
        g.rect(14,hy+3,15,hy+4,ac["glasses"])
        g.rect(18,hy+3,19,hy+4,ac["glasses"])
        g.rect(19,hy+3,20,hy+4,ac["glasses"])
        g.rect(13,hy+3,18,hy+3,ac["glasses"])
        g.rect(13,hy+4,14,hy+5,ac["glasses_frame"])
        g.rect(18,hy+4,19,hy+5,ac["glasses_frame"])
    elif accessory=="crown":
        g.rect(13,hy-6,14,hy-4,ac["crown"])
        g.rect(15,hy-7,16,hy-3,ac["crown"])
        g.rect(17,hy-6,18,hy-4,ac["crown"])
        g.rect(14,hy-5,17,hy-4,ac["crown"])
        g.rect(12,hy-4,19,hy-3,ac["crown"])
        g.set(15,hy-6,ac["crown_gem"])
    elif accessory=="flower":
        g.rect(15,hy-6,16,hy-4,ac["flower"])
        g.rect(14,hy-5,17,hy-3,ac["flower"])
        g.rect(13,hy-4,18,hy-2,ac["flower"])
        g.rect(15,hy-2,16,hy,ac["flower_center"])
    elif accessory=="santa":
        g.rect(13,hy-6,19,hy-4,ac["santa"])
        g.rect(14,hy-4,18,hy-2,ac["santa"])
        g.rect(15,hy-2,17,hy,ac["santa"])
        g.rect(16,hy,16,hy+2,ac["santa"])
        g.rect(15,hy+2,17,hy+3,ac["santa_trim"])
    elif accessory=="witch":
        g.rect(14,hy-8,18,hy-6,ac["witch"])
        g.rect(15,hy-6,17,hy-2,ac["witch"])
        g.rect(16,hy-2,16,hy+2,ac["witch"])
        g.rect(13,hy+2,19,hy+3,ac["witch_brim"])


# ================================================================
# THE PET
# ================================================================

class Pet:
    STOP=1.0; ROLL_DIST=520; ROLL_STOP=150; SLEEP_AFTER=260
    
    def __init__(self, scale, animal="armadillo", accessory="none", playtime=False):
        self.root=tk.Tk(); self.animal=animal; self.accessory=accessory; self.playtime=playtime
        r=self.root; r.title("Onekos - "+animal.capitalize())
        r.overrideredirect(True); r.attributes("-topmost",True)
        try: r.attributes("-transparentcolor",KEY)
        except: pass
        r.config(bg=KEY)
        self.cache={}; self.canvas=tk.Canvas(r,bg=KEY,highlightthickness=0,bd=0)
        self.canvas.pack(); self.item=self.canvas.create_image(0,0,anchor="nw")
        self.set_scale(scale)
        self.vl,self.vt,self.vw,self.vh=self.virtual_screen()
        self.x=self.vl+self.vw-160; self.y=self.vt+self.vh-160
        self.lpx,self.lpy=self.root.winfo_pointerxy()
        self.state="idle"; self.st=0; self.t=0; self.fr=0; self.face=-1
        self.view="side"; self.tilt=0; self.idle_t=0; self.act=None; self.act_t=0
        self.act_dur=0; self.next_state=None; self.sleep_ptr=(0,0)
        self.wander_target=None; self.wander_time=0
        self.canvas.bind("<Button-1>",self.on_click)
        self.canvas.bind("<Button-3>",self.on_menu)
        self.canvas.bind("<Control-Alt-h>",self.open_menu)
        self.canvas.bind("<Control-Alt-H>",self.open_menu)
        self.menu=tk.Menu(r,tearoff=0)
        am=tk.Menu(self.menu,tearoff=0)
        for a in ANIMALS: am.add_command(label=a.capitalize(),command=lambda a=a:self.set_animal(a))
        self.menu.add_cascade(label="Animal",menu=am)
        acm=tk.Menu(self.menu,tearoff=0)
        for acc in ["none","tophat","bow","glasses","crown","flower","santa","witch"]:
            lbl=acc.capitalize() if acc!="none" else "No Accessory"
            acm.add_command(label=lbl,command=lambda acc=acc:self.set_accessory(acc))
        self.menu.add_cascade(label="Accessory",menu=acm)
        self.menu.add_command(label="Playtime Mode",command=self.toggle_playtime)
        self.menu.add_separator()
        self.menu.add_command(label="Take a nap",command=self.nap)
        self.menu.add_command(label="Dig a hole",command=self.dig_now)
        self.menu.add_command(label="Roll over here",command=self.roll_now)
        sz=tk.Menu(self.menu,tearoff=0)
        for lbl,s in (("Small",2),("Medium",3),("Large",5),("Huge",8)):
            sz.add_command(label=lbl,command=lambda s=s:self.set_scale(s))
        self.menu.add_cascade(label="Size",menu=sz)
        self.menu.add_separator()
        self.menu.add_command(label="Quit",command=r.destroy)
        self.place(); self.tick()

    def virtual_screen(self):
        try:
            import ctypes; u=ctypes.windll.user32
            return (u.GetSystemMetrics(76),u.GetSystemMetrics(77),u.GetSystemMetrics(78),u.GetSystemMetrics(79))
        except: return 0,0,self.root.winfo_screenwidth(),self.root.winfo_screenheight()

    def set_scale(self,s):
        self.scale=s; self.size=W*s; self.cache.clear()
        self.canvas.config(width=self.size,height=self.size)
        self.root.geometry(f"{self.size}x{self.size}")

    def img(self,name,idx=0,tilt=0,blink=False,face=1):
        key=(name,idx,tilt,blink,face,self.scale,self.animal,self.accessory)
        im=self.cache.get(key)
        if im is None:
            g=build(name,idx,tilt,blink,self.animal)
            if face<0: g=g.flipped()
            render_accessory(g,self.accessory,self.animal)
            im=tk.PhotoImage(data=g.png_b64(self.scale)); self.cache[key]=im
        return im

    def show(self,name,idx=0,tilt=0,blink=False,face=1):
        self.canvas.itemconfig(self.item,image=self.img(name,idx,tilt,blink,face))

    def set_animal(self,animal):
        self.animal=animal; self.cache.clear(); self.root.title("Onekos - "+animal.capitalize())

    def set_accessory(self,accessory):
        self.accessory=accessory; self.cache.clear()

    def toggle_playtime(self):
        self.playtime=not self.playtime; self.cache.clear()
        if self.playtime: self.wander_target=None

    def place(self):
        half=self.size/2
        self.x=min(max(self.x,self.vl+half),self.vl+self.vw-half)
        self.y=min(max(self.y,self.vt+half),self.vt+self.vh-half)
        self.root.geometry(f"{self.size}x{self.size}+{int(self.x-half)}+{int(self.y-half)}")

    def set(self,state,**kw):
        self.state=state; self.st=0; self.fr=0
        for k,v in kw.items(): setattr(self,k,v)

    def begin_curl(self,then):
        self.set("curl_in",next_state=then); self.sleep_ptr=self.root.winfo_pointerxy()
    def begin_uncurl(self,then): self.set("curl_out",next_state=then)
    def nap(self):
        if self.state in ("idle","walk"): self.begin_curl("sleep")
    def dig_now(self):
        if self.state in ("idle","walk"): self.set("idle"); self.start_act("dig")
    def roll_now(self):
        if self.state in ("idle","walk"): self.begin_curl("roll")
    def on_click(self,_e):
        if self.state=="sleep": self.begin_uncurl("alert")
        elif self.state in ("idle","walk"): self.set("happy")
    def on_menu(self,e):
        try: self.menu.tk_popup(e.x_root,e.y_root)
        finally: self.menu.grab_release()
    def open_menu(self,e=None):
        try: self.menu.tk_popup(self.root.winfo_pointerx(),self.root.winfo_pointery())
        finally: self.menu.grab_release()
    def start_act(self,name):
        durs={"sniff":36,"yawn":30,"dig":48,"look":36}
        self.act=name; self.act_t=0; self.act_dur=durs[name]
    def tick(self):
        try: self.step()
        except: traceback.print_exc()
        self.root.after(TICK,self.tick)

    def step(self):
        px,py=self.root.winfo_pointerxy(); dx,dy=px-self.x,py-self.y
        dist=math.hypot(dx,dy)
        pmoved=math.hypot(px-self.lpx,py-self.lpy)>4
        if pmoved: self.lpx,self.lpy=px,py; self.idle_t=0
        self.t+=1; self.st+=1
        if self.t%40==0: self.root.lift()
        stop=self.size*0.62; s=self.state
        if s=="idle": self.do_idle(dx,dy,dist,stop)
        elif s=="walk": self.do_walk(dx,dy,dist,stop)
        elif s=="curl_in":
            k=min(2,self.st//3); self.show(("curl1","curl2","ball")[k],face=self.face)
            if self.st>=9: self.set(self.next_state)
        elif s=="curl_out":
            k=2-min(2,self.st//3); self.show(("curl1","curl2","ball")[k],face=self.face)
            if self.st>=9: self.set(self.next_state)
        elif s=="roll":
            if abs(dx)>4: self.face=1 if dx>0 else -1
            if dist>1: self.x+=dx/dist*24; self.y+=dy/dist*24
            self.fr=(self.fr+self.face)%8; self.show("ball",self.fr)
            if dist<self.ROLL_STOP: self.begin_uncurl("walk")
        elif s=="sleep":
            self.show("sleep",(self.st//3)%8,face=self.face)
            if math.hypot(px-self.sleep_ptr[0],py-self.sleep_ptr[1])>90 and self.st>60:
                self.begin_uncurl("alert")
        elif s=="alert":
            self.show("alert",min(2,self.st//4),face=self.face)
            if self.st>=14: self.set("idle")
        elif s=="happy":
            self.show("happy",(self.st//3)%4,face=self.face)
            if self.st>=36: self.set("idle")
        self.place()

    def do_idle(self,dx,dy,dist,stop):
        if dist>stop+24:
            if dist>self.ROLL_DIST: self.begin_curl("roll")
            else: self.set("walk")
            return
        if abs(dx)>12: self.face=1 if dx>0 else -1
        blink=(self.t%70)<3
        if self.act is None:
            self.idle_t+=1
            if self.idle_t>=self.SLEEP_AFTER:
                self.idle_t=0; self.begin_curl("sleep"); return
            if self.idle_t>25 and random.random()<0.02:
                self.start_act(random.choice(("sniff","sniff","yawn","dig","look")))
            self.show("stand",(self.t//4)%8,blink=blink,face=self.face); return
        self.act_t+=1; a,i=self.act,self.act_t; face=self.face
        if a=="sniff": self.show("sniff",i//3,face=face)
        elif a=="yawn": self.show("yawn",i//4,face=face)
        elif a=="dig": self.show("dig",i//3,face=face)
        elif a=="look":
            f=face if i<10 else (-face if i<22 else face)
            self.show("stand",(self.t//4)%8,blink=blink,face=f)
        if self.act_t>=self.act_dur: self.act=None

    def do_walk(self,dx,dy,dist,stop):
        if self.playtime:
            speed=3
            if self.wander_target is None or self.st%100==0:
                self.wander_target=(self.x+random.randint(-200,200),self.y+random.randint(-200,200))
                self.wander_time=self.st
            tx,ty=self.wander_target; wdx,wdy=tx-self.x,ty-self.y; wdist=math.hypot(wdx,wdy)
            if wdist>0: self.x+=wdx/wdist*speed; self.y+=wdy/wdist*speed
            if abs(wdy)>1.7*abs(wdx): self.view="front" if wdy>0 else "back"
            else:
                self.view="side"
                if abs(wdx)>3: self.face=1 if wdx>0 else -1
                r=wdy/(abs(wdx)+1); self.tilt=-1 if r<-0.45 else (1 if r>0.45 else 0)
            if self.st-self.wander_time>200 or wdist<10: self.wander_target=None
            self.act=None
            if self.st%2==0: self.fr=(self.fr+1)%6
            if self.view=="side": self.show("walk_side",self.fr,tilt=self.tilt,face=self.face)
            elif self.view=="front": self.show("walk_front",self.fr)
            else: self.show("walk_back",self.fr)
        else:
            if dist<=stop: self.set("idle"); return
            if dist>self.ROLL_DIST: self.begin_curl("roll"); return
            speed=6 if dist<220 else 10
            self.x+=dx/dist*speed; self.y+=dy/dist*speed; self.act=None
            if abs(dy)>1.7*abs(dx): self.view="front" if dy>0 else "back"
            else:
                self.view="side"
                if abs(dx)>3: self.face=1 if dx>0 else -1
                r=dy/(abs(dx)+1); self.tilt=-1 if r<-0.45 else (1 if r>0.45 else 0)
            step_ticks=2 if speed==6 else 1
            if self.st%step_ticks==0: self.fr=(self.fr+1)%6
            if self.view=="side": self.show("walk_side",self.fr,tilt=self.tilt,face=self.face)
            elif self.view=="front": self.show("walk_front",self.fr)
            else: self.show("walk_back",self.fr)


def check_google_docs():
    pass

def main():
    if tk is None: print("tkinter not installed"); return
    scale=None; animal="armadillo"; accessory="none"; playtime=False
    args=sys.argv[1:]; i=0
    while i<len(args):
        if args[i]=="--scale" and i+1<len(args):
            try: scale=int(args[i+1]); i+=2
            except: i+=1
        elif args[i]=="--animal" and i+1<len(args): animal=args[i+1]; i+=2
        elif args[i]=="--accessory" and i+1<len(args): accessory=args[i+1]; i+=2
        elif args[i]=="--playtime": playtime=True; i+=1
        elif args[i].startswith("--"): i+=1
        else: i+=1
    try:
        import ctypes; ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except: pass
    if scale is None:
        probe=tk.Tk(); dpi=probe.winfo_fpixels("1i")/96.0; probe.destroy()
        scale=max(3,int(round(3*dpi)))
    pet=Pet(scale,animal=animal,accessory=accessory,playtime=playtime)
    threading.Thread(target=check_google_docs,daemon=True).start()
    pet.root.mainloop()

if __name__=="__main__": main()
