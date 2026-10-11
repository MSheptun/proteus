import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
S = 2048; C = S // 2
def canvas(): return Image.new("RGBA", (S, S), (0, 0, 0, 0))
def disk(r, cx=C, cy=C):
    m = Image.new("L", (S, S), 0); ImageDraw.Draw(m).ellipse([cx-r, cy-r, cx+r, cy+r], fill=255); return m
def ring(r1, r0): return ImageChops.subtract(disk(r1), disk(r0))
def grad(c_in, c_out, rmax, cx=C, cy=C, light=(-0.35,-0.45)):
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.sqrt((x-cx-light[0]*rmax)**2 + (y-cy-light[1]*rmax)**2) / (rmax*1.4)
    d = np.clip(d, 0, 1)[..., None]
    a = np.array(c_in, np.float32); b = np.array(c_out, np.float32)
    return Image.fromarray((a*(1-d)+b*d).astype(np.uint8), "RGB").convert("RGBA")
def paint(base, mask, fill):
    layer = fill.copy(); layer.putalpha(mask); base.alpha_composite(layer)
def bevel(base, mask, depth=14, strength=0.55):
    """cheap emboss: highlight on upper-left edge, shadow on lower-right"""
    m = mask.filter(ImageFilter.GaussianBlur(depth))
    hi = ImageChops.subtract(mask, ImageChops.offset(m, depth//2, depth//2))
    sh = ImageChops.subtract(mask, ImageChops.offset(m, -depth//2, -depth//2))
    h = Image.new("RGBA", (S,S), (255,240,200,255)); h.putalpha(hi.point(lambda v: int(v*strength))); base.alpha_composite(h)
    s = Image.new("RGBA", (S,S), (0,0,0,255)); s.putalpha(sh.point(lambda v: int(v*strength))); base.alpha_composite(s)

img = canvas()
# --- cardinal spikes
spk = Image.new("L", (S,S), 0); sd = ImageDraw.Draw(spk)
for ang in (0, 90, 180, 270):
    a = math.radians(ang); ca, sa_ = math.cos(a), math.sin(a)
    tip = (C+1020*ca, C+1020*sa_); b1 = (C+880*ca-70*sa_, C+880*sa_+70*ca); b2 = (C+880*ca+70*sa_, C+880*sa_-70*ca)
    sd.polygon([tip, b1, b2], fill=255)
paint(img, spk, grad((190,150,64), (60,38,14), 1000))
bevel(img, spk, 10)
# --- cog (Mechanicus-style): 24 teeth
R_out, R_root = 990, 905
pts = []
N = 24
for i in range(N):
    a0 = 2*math.pi*i/N
    for da, r in ((-0.30, R_root), (-0.17, R_out), (0.17, R_out), (0.30, R_root)):
        a = a0 + da*(2*math.pi/N)
        pts.append((C+r*math.cos(a), C+r*math.sin(a)))
cog = Image.new("L", (S,S), 0); ImageDraw.Draw(cog).polygon(pts, fill=255)
paint(img, cog, grad((205,160,70), (70,45,18), 1000))
bevel(img, cog, 16)
# dark groove + iron band
paint(img, ring(880, 840), Image.new("RGBA",(S,S),(18,14,12,255)))
band = ring(835, 640)
paint(img, band, grad((95,95,100), (22,22,26), 900))
bevel(img, band, 14)
# rivets on the band
d = ImageDraw.Draw(img)
for i in range(16):
    a = 2*math.pi*i/16 + math.pi/16
    cx, cy = C+738*math.cos(a), C+738*math.sin(a)
    r = 24
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(160,125,55,255), outline=(20,16,12,255), width=5)
    d.ellipse([cx-9-6, cy-9-6, cx+3, cy+3], fill=(235,205,130,255))
# --- Chrome tri-colour wheel (segments red top, green lower-left, yellow lower-right)
Rw = 640
cols = {
  "red":   ((196,44,44), (70,6,10), 30, 150),
  "green": ((78,140,72), (10,44,22), 150, 270),
  "gold":  ((222,176,64), (104,64,6), 270, 390),
}
for name, (c1, c2, a0, a1) in cols.items():
    m = Image.new("L", (S,S), 0); md = ImageDraw.Draw(m)
    steps = 60
    poly = [(C, C)]
    for k in range(steps+1):
        a = math.radians(a0 + (a1-a0)*k/steps)
        poly.append((C+Rw*math.cos(a), C-Rw*math.sin(a)))
    md.polygon(poly, fill=255)
    m = ImageChops.multiply(m, disk(Rw))
    paint(img, m, grad(c1, c2, Rw))
    bevel(img, m, 12, 0.5)
# iron seams between segments
dd = ImageDraw.Draw(img)
for ang in (30, 150, 270):
    a = math.radians(ang)
    dd.line([(C, C), (C+Rw*math.cos(a), C-Rw*math.sin(a))], fill=(15,12,10,255), width=22)
dd.ellipse([C-Rw, C-Rw, C+Rw, C+Rw], outline=(15,12,10,255), width=18)
# --- centre: steel ring + blue lens
paint(img, disk(300), grad((235,235,240), (80,80,90), 320))
paint(img, disk(262), Image.new("RGBA",(S,S),(14,12,12,255)))
lens = disk(246)
paint(img, lens, grad((90,170,255), (10,50,140), 260, light=(-0.2,-0.3)))
bevel(img, lens, 10, 0.4)
# skull in the lens (bone white)
bone = (235,228,205,255); dark = (12,16,34,255)
sk = ImageDraw.Draw(img)
sk.ellipse([C-120, C-170, C+120, C+60], fill=bone)                 # cranium
sk.rounded_rectangle([C-78, C+20, C+78, C+130], radius=26, fill=bone)  # jaw
for ex in (-52, 52):
    sk.ellipse([C+ex-36, C-60, C+ex+36, C+12], fill=dark)           # sockets
sk.polygon([(C, C+6), (C-20, C+52), (C+20, C+52)], fill=dark)       # nose
for tx in range(-60, 61, 30):
    sk.rectangle([C+tx-3, C+82, C+tx+3, C+128], fill=dark)          # teeth gaps
sk.line([(C-78, C+82), (C+78, C+82)], fill=dark, width=6)
sk.polygon([(C-120, C-20), (C-92, C+30), (C-70, C+6)], fill=(205,196,170,255))   # cheekbones
sk.polygon([(C+120, C-20), (C+92, C+30), (C+70, C+6)], fill=(205,196,170,255))
sk.line([(C+30, C-168), (C+8, C-112), (C+26, C-84), (C+4, C-58)], fill=dark, width=6)  # crack
# glow on the eyes (Chrome blue "machine spirit")
glow = Image.new("RGBA", (S,S), (0,0,0,0)); gd = ImageDraw.Draw(glow)
for ex in (-52, 52): gd.ellipse([C+ex-16, C-40, C+ex+16, C-8], fill=(80,190,255,255))
img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(glow)
# --- weathering: grain + scratches clipped to the artwork
rng = np.random.default_rng(40)
noise = (rng.normal(0, 1, (S, S)) * 26).astype(np.int16)
n = Image.fromarray(np.clip(128 + noise, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.2))
grain = Image.merge("RGBA", (n, n, n, Image.new("L", (S,S), 46)))
sc = Image.new("RGBA", (S,S), (0,0,0,0)); scd = ImageDraw.Draw(sc)
for _ in range(70):
    x0, y0 = rng.integers(60, S-60, 2); L = rng.integers(40, 220); a = rng.uniform(0, math.pi)
    scd.line([(x0, y0), (x0+L*math.cos(a), y0+L*math.sin(a))], fill=(10,8,6,int(rng.integers(60,130))), width=int(rng.integers(2,5)))
for _ in range(40):
    x0, y0 = rng.integers(60, S-60, 2); L = rng.integers(30, 150); a = rng.uniform(0, math.pi)
    scd.line([(x0, y0), (x0+L*math.cos(a), y0+L*math.sin(a))], fill=(240,225,190,int(rng.integers(30,70))), width=2)
alpha = img.getchannel("A")
for layer in (grain, sc):
    l = layer.copy(); l.putalpha(ImageChops.multiply(l.getchannel("A"), alpha)); img.alpha_composite(l)
# --- soft drop shadow, final
shadow = Image.new("RGBA", (S,S), (0,0,0,0)); sa = Image.new('L',(S,S),0); ImageDraw.Draw(sa).ellipse([C-1000,C-1000,C+1000,C+1000], fill=255); sa = sa.filter(ImageFilter.GaussianBlur(26))
shadow.paste((0,0,0,150), mask=ImageChops.offset(sa, 0, 22))
out = Image.alpha_composite(shadow, img).resize((1024,1024), Image.LANCZOS)
out.save("/tmp/claude-0/-home-user-proteus/f6a733c2-e2ab-5cca-ac3a-8b90b729079c/scratchpad/chrome40k_1024.png")
print("ok")
