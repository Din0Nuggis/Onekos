#!/usr/bin/env python3
"""
Onekos - Desktop Pet Collection

A cute collection of 17 desktop pets that follow your cursor or play autonomously.

Features:
- 17 animals: armadillo, wolf, fox, cat, rabbit, fish, lizard, bee, butterfly, spider, frog, dragon, unicorn, penguin, owl, ladybug, snake
- 8 accessories: tophat, bow, glasses, crown, flower, santa hat, witch hat
- Playtime mode (autonomous random movement)
- Ctrl+Alt+H keyboard shortcut for menu
- Right-click or Ctrl+Alt+H to open menu
- Left-click to interact (pet, wake from sleep)
- Customizable size

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

# Colour palettes - each animal has distinct cute colors
P = {
    "armadillo": {"O":(46,34,36,255),"S":(138,120,104,255),"SL":(182,164,142,255),
                 "SM":(118,101,88,255),"SD":(88,72,62,255),"K":(226,192,168,255),
                 "KD":(186,146,126,255),"FE":(150,115,100,255),"N":(238,140,152,255),
                 "E":(22,16,20,255),"W":(255,255,255,255),"C":(248,238,222,255),
                 "D":(140,98,60,255),"DD":(74,50,34,255),"M":(150,48,60,255),
                 "T":(232,112,124,255),"R":(232,56,56,255),"H":(244,84,124,255),
                 "Z":(120,176,255,255)},
    "wolf": {"O":(50,50,60,255),"F":(120,120,130,255),"FL":(160,160,170,255),
             "FD":(80,80,90,255),"K":(200,180,170,255),"E":(200,180,100,255),
             "W":(255,255,255,255),"N":(30,30,40,255),"C":(240,240,240,255),
             "M":(150,50,50,255),"T":(230,100,100,255),"H":(240,100,120,255),
             "Z":(150,180,255,255)},
    "fox": {"O":(40,30,25,255),"F":(220,140,80,255),"FL":(240,180,120,255),
            "FD":(180,100,60,255),"FW":(255,255,255,255),"K":(200,150,130,255),
            "E":(30,20,15,255),"W":(255,255,255,255),"N":(50,40,30,255),
            "C":(240,220,200,255),"M":(180,80,60,255),"T":(230,120,100,255),
            "H":(240,120,140,255),"Z":(200,150,255,255)},
    "cat": {"O":(40,40,50,255),"F":(150,150,160,255),"FL":(180,180,190,255),
            "FD":(100,100,110,255),"FW":(255,255,255,255),"K":(220,180,180,255),
            "E":(200,180,100,255),"W":(255,255,255,255),"N":(200,150,150,255),
            "C":(240,220,220,255),"M":(180,80,80,255),"T":(230,120,120,255),
            "H":(240,120,160,255),"Z":(180,150,255,255)},
    "rabbit": {"O":(30,25,20,255),"F":(240,220,210,255),"FL":(255,255,255,255),
               "FD":(200,180,170,255),"FW":(255,255,255,255),"K":(220,180,180,255),
               "E":(200,50,50,255),"W":(255,255,255,255),"N":(200,150,150,255),
               "C":(240,220,220,255),"M":(180,80,80,255),"T":(230,120,120,255),
               "H":(240,120,160,255),"Z":(200,150,255,255)},
    "fish": {"O":(20,40,60,255),"B":(250,120,60,255),"BL":(255,160,100,255),
            "BD":(200,80,40,255),"FI":(100,200,255,255),"FID":(50,150,200,255),
            "E":(30,20,15,255),"W":(255,255,255,255),"M":(200,50,50,255),
            "BU":(200,240,255,255),"H":(240,120,160,255),"Z":(150,200,255,255)},
    "lizard": {"O":(30,40,20,255),"B":(120,180,80,255),"BL":(150,200,100,255),
               "BD":(80,120,60,255),"K":(200,180,150,255),"E":(200,150,50,255),
               "W":(255,255,255,255),"N":(150,100,80,255),"C":(240,220,200,255),
               "M":(180,80,60,255),"T":(230,100,80,255),"H":(240,120,160,255),
               "Z":(200,180,255,255)},
    "bee": {"O":(30,30,20,255),"B":(255,220,80,255),"BD":(200,170,60,255),
            "ST":(30,30,30,255),"WI":(200,240,255,180),"E":(30,20,15,255),
            "W":(255,255,255,255),"M":(180,80,60,255),"H":(240,120,160,255),
            "Z":(200,180,255,255)},
    "butterfly": {"O":(20,40,30,255),"B":(200,150,100,255),"WI":(255,120,180,200),
                  "WIL":(255,180,220,200),"WID":(180,80,150,200),"E":(30,20,15,255),
                  "W":(255,255,255,255),"A":(150,100,80,255),"H":(240,120,160,255),
                  "Z":(200,180,255,255)},
    "spider": {"O":(20,10,10,255),"B":(40,20,20,255),"BL":(60,30,30,255),
               "L":(80,40,40,255),"E":(200,180,180,255),"W":(255,255,255,255),
               "F":(200,150,150,255),"WB":(200,220,240,180),"H":(240,80,100,255),
               "Z":(180,150,255,255)},
    "frog": {"O":(20,40,20,255),"B":(120,180,80,255),"BL":(150,200,100,255),
            "BD":(80,120,60,255),"K":(200,180,150,255),"E":(200,200,180,255),
            "W":(255,255,255,255),"N":(150,100,80,255),"M":(180,80,60,255),
            "T":(230,100,80,255),"H":(240,120,160,255),"Z":(200,180,255,255)},
    "dragon": {"O":(40,20,10,255),"B":(220,80,60,255),"BL":(255,120,80,255),
               "BD":(150,50,30,255),"WI":(255,200,100,200),"HN":(255,220,150,255),
               "E":(255,220,50,255),"W":(255,255,255,255),"C":(240,200,150,255),
               "M":(200,50,50,255),"T":(230,100,80,255),"H":(240,80,120,255),
               "Z":(255,200,150,255)},
    "unicorn": {"O":(30,25,40,255),"B":(240,220,230,255),"BL":(255,255,255,255),
                "BD":(200,180,200,255),"MA":(255,180,220,255),"HN":(255,220,240,255),
                "E":(150,100,150,255),"W":(255,255,255,255),"HF":(220,200,220,255),
                "M":(180,100,120,255),"H":(240,120,180,255),"Z":(220,200,255,255)},
    "penguin": {"O":(20,20,30,255),"B":(50,50,60,255),"BE":(240,240,250,255),
                 "BK":(255,150,50,255),"FT":(255,150,50,255),"E":(30,20,15,255),
                 "W":(255,255,255,255),"M":(180,80,60,255),"H":(240,120,160,255),
                 "Z":(150,200,255,255)},
    "owl": {"O":(30,25,20,255),"B":(150,120,100,255),"BL":(180,150,130,255),
            "BD":(100,80,60,255),"WI":(130,100,80,255),"E":(255,220,100,255),
            "W":(255,255,255,255),"BK":(200,150,100,255),"C":(200,180,150,255),
            "H":(240,120,160,255),"Z":(200,180,255,255)},
    "ladybug": {"O":(20,30,20,255),"B":(220,50,50,255),"BD":(180,30,30,255),
                "SP":(30,30,30,255),"WI":(200,180,200,180),"H":(30,30,30,255),
                "E":(255,255,255,255),"W":(255,255,255,255),"HE":(240,120,160,255),
                "Z":(200,180,255,255)},
    "snake": {"O":(20,40,20,255),"B":(120,180,80,255),"BL":(150,200,100,255),
             "BD":(80,120,60,255),"K":(200,180,150,255),"E":(200,50,50,255),
             "W":(255,255,255,255),"TO":(230,50,80,255),"M":(180,50,50,255),
             "H":(240,120,160,255),"Z":(200,180,255,255)},
}

ANIMALS = ["armadillo","wolf","fox","cat","rabbit","fish","lizard","bee","butterfly","spider","frog","dragon","unicorn","penguin","owl","ladybug","snake"]
ACCESSORIES = ["none","tophat","bow","glasses","crown","flower","santa","witch"]

# Accessory colors
AP = {
    "tophat":(50,50,60,255),"tophat_band":(200,180,150,255),
    "bow":(240,120,160,255),"bow_center":(255,200,220,255),
    "glasses":(200,180,150,255),"glasses_lens":(200,240,255,150),
    "crown":(255,220,100,255),"crown_gem":(255,80,120,255),
    "flower":(255,180,220,255),"flower_center":(255,220,100,255),
    "santa":(220,50,50,255),"santa_trim":(255,255,255,255),
    "witch":(50,50,60,255),"witch_trim":(150,100,200,255),
}

# Patterns
Z4=["1111","0010","0100","1111"]
Z3=["111","010","111"]
HEART_PX=["01010","11111","01110","00100"]
BANG=["11","11","11","11","11","11","00","11","11"]

# Gait
LIFT=(0,1,2,1,0,0)
SWING=(-1,-1,0,1,1,0)
LEG_OFF=(0,3,3,0)

def walk_legs(f):
    out=[]
    for off in LEG_OFF:
        p=(f+off)%6; out.append((LIFT[p],SWING[p]))
    return out

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
                            self.p[y][x]=(0,0,0,255); break
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
        png=(b"\x89PNG\r\n\x1a\n"
             +chunk(b"IHDR",struct.pack(">IIBBBBB",W*scale,H*scale,8,6,0,0,0))
             +chunk(b"IDAT",zlib.compress(bytes(raw),9))
             +chunk(b"IEND",b""))
        return base64.b64encode(png).decode("ascii")

def line(g,x0,y0,x1,y1,c,thick=1):
    n=max(abs(x1-x0),abs(y1-y0),1)
    for i in range(n+1):
        x=round(x0+(x1-x0)*i/n); y=round(y0+(y1-y0)*i/n)
        for t in range(thick): g.set(x,y+t,c)


def draw_armadillo(g,p,view="side",idx=0,face=1,tilt=0,blink=False,accessory=None):
    """Draw armadillo in various views. Uses palette p with keys: O,S,SL,SM,SD,K,KD,FE,N,E,W,C,D,DD,M,T,R,H,Z"""
    if view=="side":
        bob=(0,0,-1,0,0,-1)[idx%6]; legs=walk_legs(idx)
        scx,scy,srx,sry=14,15,9,8; scy+=bob; top=scy+sry-3
        LEG_X=(10,19,7,16)
        def _leg(g,x,top,lift,dx,col,edge):
            x+=dx; bottom=max(top,25-lift)
            g.rect(x,top,x+1,bottom,col)
            for y in range(top,bottom+1): g.set(x,y,edge)
            g.set(x+1,bottom,p["C"]); g.set(x+2,bottom,p["C"])
        # Dirt hole when digging
        if idx%4==0: g.ellipse(21,25,7,1.3,lambda x,y:p["DD"])
        _leg(g,LEG_X[0],top,*legs[0],p["KD"],p["FE"])
        _leg(g,LEG_X[1],top,*legs[1],p["KD"],p["FE"])
        ty=scy+3
        tail_wag=(0,1,0,-1,0,1)[idx%6]
        line(g,scx-srx+2,ty,1,ty+2-tail_wag,p["KD"],2)
        g.ellipse(scx,scy+sry-2,srx-1,3,lambda x,y:p["K"])
        def shell_px(x,y):
            if y>scy+sry-2: return None
            yt=scy-sry*math.sqrt(max(0.0,1-((x-scx)/srx)**2)); rel=x-scx
            if y-yt<1.2: return p["SL"]
            if rel<=-srx+4 or rel>=srx-4: return p["S"] if (x+y)%2==0 else p["SM"]
            if (x-scx+(y-scy)//4)%3==0: return p["SD"]
            if y>=scy+sry-3: return p["SM"]
            return p["S"]
        g.ellipse(scx,scy,srx,sry,shell_px)
        hx,hy=scx+9,scy+2+tilt
        def head_px(x,y):
            if y<=hy-1:
                if y<=hy-3: return p["SL"]
                return p["S"] if (x+y)%2==0 else p["SM"]
            return p["K"]
        g.ellipse(hx,hy,4,3.2,head_px)
        for dx in range(3,5): g.set(hx+dx,hy-1,p["K"])
        for dx in range(3,7): g.set(hx+dx,hy,p["K"])
        for dx in range(3,6): g.set(hx+dx,hy+1,p["K"])
        g.set(hx+6,hy,p["N"])
        # Mouth animation
        mouth=0
        if mouth:
            g.rect(hx+3,hy+2,hx+5,hy+1+mouth,p["M"])
            if mouth>=2: g.rect(hx+4,hy+mouth,hx+5,hy+mouth,p["T"])
            g.rect(hx+3,hy+2+mouth,hx+5,hy+2+mouth,p["K"])
        else:
            g.rect(hx+3,hy+2,hx+4,hy+2,p["K"])
        eye="closed" if blink else "open"
        if eye=="open": g.set(hx+2,hy,p["E"])
        elif eye=="wide":
            g.rect(hx+2,hy-1,hx+3,hy,p["E"])
            g.set(hx+2,hy-1,p["W"])
        else:
            g.set(hx+1,hy,p["O"])
            g.set(hx+2,hy,p["O"])
        ears=1 if tilt<0 else 0
        if ears==0: g.rect(hx-2,hy-5,hx-1,hy-3,p["KD"])
        elif ears==1: g.rect(hx-2,hy-7,hx-1,hy-3,p["KD"])
        else: g.rect(hx-5,hy-2,hx-2,hy-1,p["KD"])
        _leg(g,LEG_X[2],top,*legs[2],p["K"],p["KD"])
        _leg(g,LEG_X[3],top,*legs[3],p["K"],p["KD"])
    elif view=="front":
        cx=15.5; bob=(0,0,-1,0,0,-1)[idx%6]
        lifts=[(0,1,2,1,0,0)[(idx+off)%6] for off in (0,3)]
        scy=13+bob
        def shell_px(x,y):
            if y>scy+9: return None
            yt=scy-9*math.sqrt(max(0.0,1-((x-cx)/10)**2))
            if y-yt<1.3: return p["SL"]
            v=(y-scy)+((x-cx)**2)/28.0
            if int(math.floor(v))%3==0: return p["SD"]
            return p["S"]
        g.ellipse(cx,scy,10,9,shell_px)
        hy=19+bob
        g.rect(10,hy-5,11,hy-2,p["KD"])
        g.rect(20,hy-5,21,hy-2,p["KD"])
        def head_px(x,y):
            if y<=hy-2:
                if y<=hy-3: return p["SL"]
                return p["S"] if (x+y)%2==0 else p["SM"]
            return p["K"]
        g.ellipse(cx,hy,5.2,4.2,head_px)
        eye="closed" if blink else "open"
        if eye=="open":
            g.set(13,hy,p["E"])
            g.set(18,hy,p["E"])
        else:
            g.rect(12,hy,13,hy,p["O"])
            g.rect(18,hy,19,hy,p["O"])
        g.rect(15,hy+2,16,hy+3,p["N"])
        for x,l in ((8,lifts[0]),(22,lifts[1])):
            bottom=25-l
            g.rect(x,21,x+1,bottom,p["K"])
            g.set(x,21,p["KD"])
            g.rect(x-1,bottom,x+2,bottom,p["C"])
    elif view=="back":
        cx=15.5; bob=(0,0,-1,0,0,-1)[idx%6]
        lifts=[(0,1,2,1,0,0)[(idx+off)%6] for off in (0,3)]
        g.ellipse(cx,7+bob,4.4,3.4,lambda x,y:p["KD"])
        g.rect(11,2+bob,12,5+bob,p["KD"])
        g.rect(19,2+bob,20,5+bob,p["KD"])
        for x,l in ((8,lifts[0]),(22,lifts[1])):
            bottom=25-l
            g.rect(x,20,x+1,bottom,p["K"])
            g.set(x,20,p["KD"])
            g.rect(x-1,bottom,x+2,bottom,p["C"])
        scy=14+bob
        def shell_px(x,y):
            if y>scy+8: return None
            yt=scy-9*math.sqrt(max(0.0,1-((x-cx)/10)**2))
            if y-yt<1.3: return p["SL"]
            if y>=scy+3: return p["S"] if (x+y)%2==0 else p["SM"]
            v=(y-scy)+((x-cx)**2)/30.0
            if int(math.floor(v))%3==0: return p["SD"]
            return p["S"]
        g.ellipse(cx,scy,10,9,shell_px)
        sway=(0,1,1,0,-1,-1)[idx%6]
        for dx in (0,1):
            line(g,15+dx,21+bob,15+dx+sway,26,p["KD"])
    elif view=="ball":
        cx,r=15.5,9; ry=r; cy=25.5-ry
        ca,sa=math.cos(idx*math.pi/8),math.sin(idx*math.pi/8)
        def px(x,y):
            if math.hypot(x-(cx-3),y-(cy-4))<2.4: return p["SL"]
            u=(x-cx)*ca+(y-cy)*sa
            if abs(u-4*round(u/4))<0.75: return p["SD"]
            if (x-cx)+(y-cy)>8: return p["SM"]
            return p["S"]
        g.ellipse(cx,cy,r,ry,px)
    elif view=="sleep":
        squish=(0,0,1,1)[(idx//2)%4]
        g=Grid()
        cx,r=15.5,9; ry=r-squish; cy=25.5-ry
        ca,sa=math.cos(0.35),math.sin(0.35)
        def px(x,y):
            if math.hypot(x-(cx-3),y-(cy-4))<2.4: return p["SL"]
            u=(x-cx)*ca+(y-cy)*sa
            if abs(u-4*round(u/4))<0.75: return p["SD"]
            if (x-cx)+(y-cy)>8: return p["SM"]
            return p["S"]
        g.ellipse(cx,cy,r,ry,px)
        g.rect(24,20,26,22,p["K"])
        g.set(26,21,p["N"])
        g.rect(4,21,7,22,p["KD"])
        for k in range(2):
            age=(idx+4*k)%8; y=11-age; x=22+age//2+k
            if y>=0: g.stamp(x,y,Z4 if age<5 else Z3,p["Z"])
        g.outline()
        if accessory and accessory!="none":
            draw_accessory(g,p,accessory,view)
        return g
    elif view=="curl1":
        g=Grid()
        # Draw curled up armadillo
        bob=1; legs=[(1,0)]*4; scx,scy,srx,sry=14,15,9,8
        scy+=bob; top=scy+sry-3; LEG_X=(10,19,7,16)
        def _leg(g,x,top,lift,dx,col,edge):
            x+=dx; bottom=max(top,25-lift)
            g.rect(x,top,x+1,bottom,col)
            for y in range(top,bottom+1): g.set(x,y,edge)
            g.set(x+1,bottom,p["C"]); g.set(x+2,bottom,p["C"])
        _leg(g,LEG_X[0],top,*legs[0],p["KD"],p["FE"])
        _leg(g,LEG_X[1],top,*legs[1],p["KD"],p["FE"])
        ty=scy+3
        line(g,scx-srx+2,ty,1,ty+2-(-1),p["KD"],2)
        g.ellipse(scx,scy+sry-2,srx-1,3,lambda x,y:p["K"])
        def shell_px(x,y):
            if y>scy+sry-2: return None
            yt=scy-sry*math.sqrt(max(0.0,1-((x-scx)/srx)**2)); rel=x-scx
            if y-yt<1.2: return p["SL"]
            if rel<=-srx+4 or rel>=srx-4: return p["S"] if (x+y)%2==0 else p["SM"]
            if (x-scx+(y-scy)//4)%3==0: return p["SD"]
            if y>=scy+sry-3: return p["SM"]
            return p["S"]
        g.ellipse(scx,scy,srx,sry,shell_px)
        hx,hy=scx+9-2,scy+2+1
        def head_px(x,y):
            if y<=hy-1:
                if y<=hy-3: return p["SL"]
                return p["S"] if (x+y)%2==0 else p["SM"]
            return p["K"]
        g.ellipse(hx,hy,4,3.2,head_px)
        for dx in range(3,5): g.set(hx+dx,hy-1,p["K"])
        for dx in range(3,7): g.set(hx+dx,hy,p["K"])
        for dx in range(3,6): g.set(hx+dx,hy+1,p["K"])
        g.set(hx+6,hy,p["N"])
        g.rect(hx+3,hy+2,hx+4,hy+2,p["K"])
        g.set(hx+1,hy,p["O"]); g.set(hx+2,hy,p["O"])
        g.rect(hx-5,hy-2,hx-2,hy-1,p["KD"])
        _leg(g,LEG_X[2],top,*legs[2],p["K"],p["KD"])
        _leg(g,LEG_X[3],top,*legs[3],p["K"],p["KD"])
        g.outline()
        if accessory and accessory!="none":
            draw_accessory(g,p,accessory,view)
        return g
    
    g.outline()
    if accessory and accessory!="none":
        draw_accessory(g,p,accessory,view)
    return g


def draw_accessory(g,p,acc,view):
    """Draw accessory on the pet. p is the animal palette (for reference), acc is accessory name."""
    a=AP
    if acc=="tophat":
        if view=="side":
            g.rect(17,7,23,10,a["tophat"])
            g.rect(16,6,24,7,a["tophat"])
            g.rect(17,10,23,11,a["tophat_band"])
        elif view in ("front","back"):
            g.rect(12,6,20,9,a["tophat"])
            g.rect(11,5,21,6,a["tophat"])
            g.rect(12,9,20,10,a["tophat_band"])
    elif acc=="bow":
        if view=="side":
            g.ellipse(19,8,2,1.5,lambda x,y:a["bow"])
            g.ellipse(19,8,1,0.5,lambda x,y:a["bow_center"])
        elif view in ("front","back"):
            g.ellipse(15,6,2,1.5,lambda x,y:a["bow"])
            g.ellipse(15,6,1,0.5,lambda x,y:a["bow_center"])
    elif acc=="glasses":
        if view=="side":
            g.rect(20,10,22,11,a["glasses"])
            g.rect(23,10,25,11,a["glasses"])
            g.rect(22,10,23,11,a["glasses"])
            g.ellipse(21,10,1,1,lambda x,y:a["glasses_lens"])
            g.ellipse(24,10,1,1,lambda x,y:a["glasses_lens"])
        elif view in ("front","back"):
            g.rect(12,9,14,10,a["glasses"])
            g.rect(17,9,19,10,a["glasses"])
            g.rect(14,9,17,10,a["glasses"])
            g.ellipse(13,9,1,1,lambda x,y:a["glasses_lens"])
            g.ellipse(18,9,1,1,lambda x,y:a["glasses_lens"])
    elif acc=="crown":
        if view=="side":
            g.rect(18,6,22,8,a["crown"])
            for i in range(3):
                g.set(18+i*2,5,a["crown"])
                g.set(19+i*2,4,a["crown_gem"])
        elif view in ("front","back"):
            g.rect(13,5,19,7,a["crown"])
            for i in range(3):
                g.set(14+i*2,4,a["crown_gem"])
    elif acc=="flower":
        if view=="side":
            g.ellipse(20,6,1.5,1.5,lambda x,y:a["flower"])
            for i in range(4):
                ang=i*math.pi/2
                px=20+int(2*math.cos(ang))
                py=6+int(2*math.sin(ang))
                g.ellipse(px,py,1,1,lambda x,y:a["flower"])
            g.ellipse(20,6,0.5,0.5,lambda x,y:a["flower_center"])
        elif view in ("front","back"):
            g.ellipse(15,5,1.5,1.5,lambda x,y:a["flower"])
            for i in range(4):
                ang=i*math.pi/2
                px=15+int(2*math.cos(ang))
                py=5+int(2*math.sin(ang))
                g.ellipse(px,py,1,1,lambda x,y:a["flower"])
    elif acc=="santa":
        if view=="side":
            g.rect(17,6,23,9,a["santa"])
            g.rect(16,5,24,6,a["santa"])
            g.rect(23,6,25,9,a["santa"])
            g.rect(23,9,25,10,a["santa_trim"])
            g.rect(17,9,23,10,a["santa_trim"])
            g.ellipse(24,8,1,1,lambda x,y:a["santa_trim"])
        elif view in ("front","back"):
            g.rect(12,5,20,8,a["santa"])
            g.rect(11,4,21,5,a["santa"])
            g.rect(20,5,22,8,a["santa"])
            g.rect(20,8,22,9,a["santa_trim"])
            g.rect(12,8,20,9,a["santa_trim"])
    elif acc=="witch":
        if view=="side":
            g.rect(16,6,24,9,a["witch"])
            g.rect(15,5,25,6,a["witch"])
            g.rect(17,9,23,10,a["witch_trim"])
            g.ellipse(20,4,1.5,1,lambda x,y:a["witch_trim"])
        elif view in ("front","back"):
            g.rect(11,4,21,7,a["witch"])
            g.rect(10,3,22,4,a["witch"])
            g.rect(12,7,20,8,a["witch_trim"])
            g.ellipse(15,2,1.5,1,lambda x,y:a["witch_trim"])


class Pet:
    STOP=1.0; ROLL_DIST=520; ROLL_STOP=150; SLEEP_AFTER=260
    
    def __init__(self,scale,animal="armadillo",accessory="none",playtime=False):
        self.root=tk.Tk(); r=self.root
        r.title(f"Onekos - {animal.capitalize()}")
        r.overrideredirect(True); r.attributes("-topmost",True)
        try: r.attributes("-transparentcolor",KEY)
        except: pass
        r.config(bg=KEY)
        self.cache={}; self.canvas=tk.Canvas(r,bg=KEY,highlightthickness=0,bd=0)
        self.canvas.pack(); self.item=self.canvas.create_image(0,0,anchor="nw")
        self.set_scale(scale)
        self.vl,self.vt,self.vw,self.vh=self.virtual_screen()
        self.x=self.vl+self.vw-160; self.y=self.vt+self.vh-160
        self.lpx,self.lpy=r.winfo_pointerxy()
        self.state="idle"; self.st=0; self.t=0; self.fr=0; self.face=-1
        self.view="side"; self.tilt=0; self.idle_t=0; self.act=None
        self.act_t=0; self.act_dur=0; self.next_state=None; self.sleep_ptr=(0,0)
        self.animal=animal; self.accessory=accessory; self.playtime=playtime
        self.play_target_x=None; self.play_target_y=None; self.play_target_time=0
        self.canvas.bind("<Button-1>",self.on_click)
        self.canvas.bind("<Button-3>",self.on_menu)
        self.canvas.bind("<Control-Alt-h>",self.on_keyboard_menu)
        self.canvas.bind("<Control-Alt-H>",self.on_keyboard_menu)
        self.menu=tk.Menu(r,tearoff=0); self.build_menu()
        self.place(); self.tick()

    def build_menu(self):
        self.menu.delete(0,tk.END)
        # Animal submenu
        am=tk.Menu(self.menu,tearoff=0)
        for a in ANIMALS: am.add_command(label=a.capitalize(),command=lambda a=a:self.set_animal(a))
        self.menu.add_cascade(label="Animal",menu=am)
        # Accessory submenu
        ac=tk.Menu(self.menu,tearoff=0)
        for a in ACCESSORIES: 
            label=a.capitalize().replace("-"," ")
            ac.add_command(label=label,command=lambda a=a:self.set_accessory(a))
        self.menu.add_cascade(label="Accessory",menu=ac)
        self.menu.add_separator()
        self.menu.add_command(label="Playtime Mode",command=self.toggle_playtime)
        self.menu.add_separator()
        self.menu.add_command(label="Take a nap",command=self.nap)
        self.menu.add_command(label="Roll over here",command=self.roll_now)
        # Size submenu
        sz=tk.Menu(self.menu,tearoff=0)
        for l,s in (("Small",2),("Medium",3),("Large",5),("Huge",8)):
            sz.add_command(label=l,command=lambda s=s:self.set_scale(s))
        self.menu.add_cascade(label="Size",menu=sz)
        self.menu.add_separator()
        self.menu.add_command(label="Quit",command=self.root.destroy)

    def virtual_screen(self):
        try:
            import ctypes; u=ctypes.windll.user32
            return (u.GetSystemMetrics(76),u.GetSystemMetrics(77),u.GetSystemMetrics(78),u.GetSystemMetrics(79))
        except: return 0,0,self.root.winfo_screenwidth(),self.root.winfo_screenheight()

    def set_scale(self,s):
        self.scale=s; self.size=W*s; self.cache.clear()
        self.canvas.config(width=self.size,height=self.size)
        self.root.geometry(f"{self.size}x{self.size}")

    def set_animal(self,a):
        self.animal=a; self.cache.clear()
        self.root.title(f"Onekos - {a.capitalize()}")
    
    def set_accessory(self,a):
        self.accessory=a; self.cache.clear()
    
    def toggle_playtime(self):
        self.playtime=not self.playtime
        if self.playtime:
            self.play_target_x=None
            self.play_target_y=None

    def img(self,name,idx=0,tilt=0,blink=False,face=1):
        key=(self.animal,name,idx,tilt,blink,face,self.scale,self.accessory)
        im=self.cache.get(key)
        if im is None:
            p=P.get(self.animal,P["armadillo"])
            g=draw_armadillo(Grid(),p,name,idx,face,tilt,blink,self.accessory)
            if face<0: g=g.flipped()
            im=tk.PhotoImage(data=g.png_b64(self.scale))
            self.cache[key]=im
        return im

    def show(self,name,idx=0,tilt=0,blink=False,face=1):
        self.canvas.itemconfig(self.item,image=self.img(name,idx,tilt,blink,face))

    def place(self):
        half=self.size/2
        self.x=min(max(self.x,self.vl+half),self.vl+self.vw-half)
        self.y=min(max(self.y,self.vt+half),self.vt+self.vh-half)
        self.root.geometry(f"{self.size}x{self.size}+{int(self.x-half)}+{int(self.y-half)}")

    def set(self,state,**kw):
        self.state=state; self.st=0; self.fr=0
        for k,v in kw.items(): setattr(self,k,v)

    def begin_curl(self,then):
        self.set("curl_in",next_state=then)
        self.sleep_ptr=self.root.winfo_pointerxy()
    
    def begin_uncurl(self,then):
        self.set("curl_out",next_state=then)

    def nap(self):
        if self.state in ("idle","walk","play"):
            self.begin_curl("sleep")

    def roll_now(self):
        if self.state in ("idle","walk","play"):
            self.begin_curl("roll")

    def on_click(self,_e):
        if self.state=="sleep":
            self.begin_uncurl("alert")
        elif self.state in ("idle","walk","play"):
            self.set("happy")

    def on_menu(self,e):
        try: self.menu.tk_popup(e.x_root,e.y_root)
        finally: self.menu.grab_release()

    def on_keyboard_menu(self,e):
        try: self.menu.tk_popup(int(self.x),int(self.y))
        finally: self.menu.grab_release()

    def start_act(self,name):
        durs={"sniff":36,"yawn":30,"look":36}
        self.act=name; self.act_t=0; self.act_dur=durs.get(name,36)

    def tick(self):
        try: self.step()
        except: traceback.print_exc()
        self.root.after(TICK,self.tick)

    def step(self):
        px,py=self.root.winfo_pointerxy()
        dx,dy=px-self.x,py-self.y
        dist=math.hypot(dx,dy)
        pmoved=math.hypot(px-self.lpx,py-self.lpy)>4
        if pmoved:
            self.lpx,self.lpy=px,py
            self.idle_t=0
        self.t+=1; self.st+=1
        if self.t%40==0: self.root.lift()
        stop=self.size*0.62
        s=self.state

        if s=="idle":
            if self.playtime:
                self.set("play")
                return
            if dist>stop+24:
                if dist>self.ROLL_DIST:
                    self.begin_curl("roll")
                else:
                    self.set("walk")
                return
            if abs(dx)>12:
                self.face=1 if dx>0 else -1
            blink=(self.t%70)<3
            if self.act is None:
                self.idle_t+=1
                if self.idle_t>=self.SLEEP_AFTER:
                    self.idle_t=0
                    self.begin_curl("sleep")
                    return
                if self.idle_t>25 and random.random()<0.02:
                    self.start_act(random.choice(("sniff","sniff","yawn","look")))
                self.show("stand",(self.t//4)%8,blink=blink,face=self.face)
                return
            self.act_t+=1
            a,i=self.act,self.act_t
            face=self.face
            if a=="sniff":
                self.show("sniff",i//3,face=face)
            elif a=="yawn":
                self.show("yawn",i//4,face=face)
            elif a=="look":
                f=face if i<10 else (-face if i<22 else face)
                self.show("stand",(self.t//4)%8,blink=(self.t%70)<3,face=f)
            if self.act_t>=self.act_dur:
                self.act=None

        elif s=="walk":
            if self.playtime:
                self.set("play")
                return
            if dist<=stop:
                self.set("idle")
                return
            if dist>self.ROLL_DIST:
                self.begin_curl("roll")
                return
            speed=6 if dist<220 else 10
            self.x+=dx/dist*speed
            self.y+=dy/dist*speed
            self.act=None
            if abs(dy)>1.7*abs(dx):
                self.view="front" if dy>0 else "back"
            else:
                self.view="side"
                if abs(dx)>3:
                    self.face=1 if dx>0 else -1
                r=dy/(abs(dx)+1)
                self.tilt=-1 if r<-0.45 else (1 if r>0.45 else 0)
            step_ticks=2 if speed==6 else 1
            if self.st%step_ticks==0:
                self.fr=(self.fr+1)%6
            if self.view=="side":
                self.show("walk_side",self.fr,tilt=self.tilt,face=self.face)
            elif self.view=="front":
                self.show("walk_front",self.fr)
            else:
                self.show("walk_back",self.fr)

        elif s=="play":
            # Playtime mode - autonomous movement
            if self.play_target_x is None or self.st>self.play_target_time:
                self.play_target_x=random.randint(self.vl+50,self.vl+self.vw-50)
                self.play_target_y=random.randint(self.vt+50,self.vt+self.vh-50)
                self.play_target_time=self.st+random.randint(100,300)
            td_x=self.play_target_x-self.x
            td_y=self.play_target_y-self.y
            td_dist=math.hypot(td_x,td_y)
            if td_dist>5:
                speed=3+random.random()*2
                self.x+=td_x/td_dist*speed
                self.y+=td_y/td_dist*speed
                if abs(td_x)>3:
                    self.face=1 if td_x>0 else -1
                r=td_y/(abs(td_x)+1)
                self.tilt=-1 if r<-0.45 else (1 if r>0.45 else 0)
                if self.st%2==0:
                    self.fr=(self.fr+1)%6
                if abs(td_y)>1.7*abs(td_x):
                    self.view="front" if td_y>0 else "back"
                else:
                    self.view="side"
                if self.view=="side":
                    self.show("walk_side",self.fr,tilt=self.tilt,face=self.face)
                elif self.view=="front":
                    self.show("walk_front",self.fr)
                else:
                    self.show("walk_back",self.fr)
            else:
                # At target, do random action
                if random.random()<0.05:
                    self.start_act(random.choice(("sniff","yawn","look")))
                if self.act is None:
                    blink=(self.t%70)<3
                    self.show("stand",(self.t//4)%8,blink=blink,face=self.face)
                else:
                    self.act_t+=1
                    a,i=self.act,self.act_t
                    face=self.face
                    if a=="sniff":
                        self.show("sniff",i//3,face=face)
                    elif a=="yawn":
                        self.show("yawn",i//4,face=face)
                    elif a=="look":
                        f=face if i<10 else (-face if i<22 else face)
                        self.show("stand",(self.t//4)%8,blink=(self.t%70)<3,face=f)
                    if self.act_t>=self.act_dur:
                        self.act=None

        elif s=="curl_in":
            k=min(2,self.st//3)
            self.show(("curl1","curl2","ball")[k],face=self.face)
            if self.st>=9:
                self.set(self.next_state)

        elif s=="curl_out":
            k=2-min(2,self.st//3)
            self.show(("curl1","curl2","ball")[k],face=self.face)
            if self.st>=9:
                self.set(self.next_state)

        elif s=="roll":
            if abs(dx)>4:
                self.face=1 if dx>0 else -1
            if dist>1:
                self.x+=dx/dist*24
                self.y+=dy/dist*24
            self.fr=(self.fr+self.face)%8
            self.show("ball",self.fr)
            if dist<self.ROLL_STOP:
                self.begin_uncurl("walk" if not self.playtime else "play")

        elif s=="sleep":
            self.show("sleep",(self.st//3)%8,face=self.face)
            woke=math.hypot(px-self.sleep_ptr[0],py-self.sleep_ptr[1])>90
            if woke and self.st>60:
                self.begin_uncurl("alert")

        elif s=="alert":
            self.show("alert",min(2,self.st//4),face=self.face)
            if self.st>=14:
                self.set("idle" if not self.playtime else "play")

        elif s=="happy":
            self.show("happy",(self.st//3)%4,face=self.face)
            if self.st>=36:
                self.set("idle" if not self.playtime else "play")

        self.place()


def main():
    if tk is None:
        print("tkinter is not installed.")
        return
    scale=None
    animal="armadillo"
    playtime=False
    i=1
    while i<len(sys.argv):
        arg=sys.argv[i]
        if arg=="--scale":
            try: scale=int(sys.argv[i+1]); i+=2
            except: i+=1
        elif arg=="--animal":
            try: animal=sys.argv[i+1]; i+=2
            except: i+=1
        elif arg=="--playtime":
            playtime=True; i+=1
        else:
            i+=1
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
    if scale is None:
        probe=tk.Tk()
        dpi=probe.winfo_fpixels("1i")/96.0
        probe.destroy()
        scale=max(3,int(round(3*dpi)))
    pet=Pet(scale,animal=animal,accessory="none",playtime=playtime)
    pet.root.mainloop()


if __name__=="__main__":
    main()
