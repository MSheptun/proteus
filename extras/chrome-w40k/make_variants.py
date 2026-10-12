#!/usr/bin/env python3
"""Fan-made grimdark Chrome icons in the style of Warhammer 40K chapters/legions.

Original, simplified artwork drawn from scratch (not official Games Workshop art).
Personal use only.

    python3 make_variants.py <output-dir>

Writes <name>-1024.png and <name>.ico for every variant.
"""
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

S = 2048
C = S // 2
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


# ---------------------------------------------------------------- helpers
def canvas():
    return Image.new("RGBA", (S, S), (0, 0, 0, 0))


def disk(r, cx=C, cy=C):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    return m


def ring(r1, r0):
    return ImageChops.subtract(disk(r1), disk(r0))


def solid(c):
    return Image.new("RGBA", (S, S), tuple(c) + (255,) if len(c) == 3 else tuple(c))


def grad(c_in, c_out, rmax, cx=C, cy=C, light=(-0.35, -0.45)):
    y, x = np.mgrid[0:S, 0:S].astype(np.float32)
    d = np.sqrt((x - cx - light[0] * rmax) ** 2 + (y - cy - light[1] * rmax) ** 2) / (rmax * 1.4)
    d = np.clip(d, 0, 1)[..., None]
    a = np.array(c_in, np.float32)
    b = np.array(c_out, np.float32)
    return Image.fromarray((a * (1 - d) + b * d).astype(np.uint8), "RGB").convert("RGBA")


def paint(base, mask, fill):
    layer = fill.copy()
    layer.putalpha(mask)
    base.alpha_composite(layer)


def bevel(base, mask, depth=14, strength=0.55):
    m = mask.filter(ImageFilter.GaussianBlur(depth))
    hi = ImageChops.subtract(mask, ImageChops.offset(m, depth // 2, depth // 2))
    sh = ImageChops.subtract(mask, ImageChops.offset(m, -depth // 2, -depth // 2))
    h = Image.new("RGBA", (S, S), (255, 240, 200, 255))
    h.putalpha(hi.point(lambda v: int(v * strength)))
    base.alpha_composite(h)
    s = Image.new("RGBA", (S, S), (0, 0, 0, 255))
    s.putalpha(sh.point(lambda v: int(v * strength)))
    base.alpha_composite(s)


def poly_mask(points):
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).polygon(points, fill=255)
    return m


def rot(pts, ang, cx=C, cy=C):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


def U(x, y, k=232):
    """unit emblem coordinates -> pixels (lens centre, k = emblem radius)."""
    return (C + x * k, C + y * k)


# ---------------------------------------------------------------- outer decorations
def cog(img, c_in, c_out, teeth=24, pointed=False):
    R_out, R_root = 990, 905
    pts = []
    for i in range(teeth):
        a0 = 2 * math.pi * i / teeth
        shape = ((-0.34, R_root), (0.0, R_out), (0.34, R_root)) if pointed else (
            (-0.30, R_root), (-0.17, R_out), (0.17, R_out), (0.30, R_root))
        for da, r in shape:
            a = a0 + da * (2 * math.pi / teeth)
            pts.append((C + r * math.cos(a), C + r * math.sin(a)))
    m = poly_mask(pts)
    paint(img, m, grad(c_in, c_out, 1000))
    bevel(img, m, 16)
    return 1.0


def wings(img, c_in, c_out):
    """Two feathered wings behind the (smaller) disc."""
    for side in (-1, 1):
        for row, (n, a0, a1, l0, l1) in enumerate(((7, 8, 78, 640, 330), (4, -12, -52, 520, 330))):
            for i in range(n):
                t = i / (n - 1)
                ang = math.radians(a0 + (a1 - a0) * t) * (1 if row == 0 else 1)
                L = l0 + (l1 - l0) * t
                ox, oy = C + side * 640, C - 40 + (0 if row == 0 else 60)
                dx, dy = math.cos(ang) * side, -math.sin(ang)
                nx, ny = -dy, dx
                w = 78 - 14 * t
                tip = (ox + dx * L, oy + dy * L)
                mid = (ox + dx * L * 0.55, oy + dy * L * 0.55)
                pts = [(ox + nx * w * 0.5, oy + ny * w * 0.5), (mid[0] + nx * w, mid[1] + ny * w),
                       tip, (mid[0] - nx * w, mid[1] - ny * w), (ox - nx * w * 0.5, oy - ny * w * 0.5)]
                m = poly_mask(pts)
                edge = m.filter(ImageFilter.MaxFilter(9))
                paint(img, edge, solid((18, 14, 12)))
                paint(img, m, grad(c_in, c_out, 700, cx=ox, cy=oy))
                bevel(img, m, 8, 0.4)
    return 0.84


def laurel(img, c_in, c_out):
    for side in (-1, 1):
        for i in range(15):
            t = i / 14
            a = math.radians(95 + 150 * t) if side == 1 else math.radians(85 - 150 * t)
            r = 905
            px, py = C + r * math.cos(a), C + r * math.sin(a)
            tang = a + math.pi / 2 * (1 if side == 1 else -1)
            for k, off in enumerate((-26, 26)):
                ang = tang + math.radians(off * (1.4 if k == 0 else 1.4))
                L = 150 - 40 * abs(t - 0.5)
                tip = (px + math.cos(ang) * L, py + math.sin(ang) * L)
                nx, ny = -math.sin(ang), math.cos(ang)
                mid = ((px + tip[0]) / 2, (py + tip[1]) / 2)
                pts = [(px, py), (mid[0] + nx * 38, mid[1] + ny * 38), tip, (mid[0] - nx * 38, mid[1] - ny * 38)]
                m = poly_mask(pts)
                paint(img, m.filter(ImageFilter.MaxFilter(7)), solid((18, 14, 12)))
                paint(img, m, grad(c_in, c_out, 900, cx=px, cy=py))
    return 0.90


def scales(img, c_in, c_out):
    base = disk(990)
    paint(img, base, grad(c_in, c_out, 1000))
    d = ImageDraw.Draw(img)
    for row, (r, n) in enumerate(((955, 64), (925, 60))):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5 * row) / n
            cx, cy = C + r * math.cos(a), C + r * math.sin(a)
            rr = 52
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(8, 24, 20, 255), width=6,
                      fill=None)
    bevel(img, base, 14)
    return 1.0


def plain(img, c_in, c_out):
    m = disk(985)
    paint(img, m, grad(c_in, c_out, 1000))
    bevel(img, m, 16)
    return 1.0


OUTER = {"cog": cog, "wings": wings, "laurel": laurel, "scales": scales, "plain": plain}


# ---------------------------------------------------------------- emblems (drawn in the lens)
def e_drop(img, v):
    d = ImageDraw.Draw(img)
    col, hi = v["emb"], v["emb_hi"]
    d.ellipse([C - 0.56 * 232, C + 0.05 * 232 - 0.0, C + 0.56 * 232, C + 0.05 * 232 + 1.12 * 232], fill=col)
    d.polygon([U(-0.52, 0.30), U(0, -1.0), U(0.52, 0.30)], fill=col)
    d.ellipse([C - 0.36 * 232, C + 0.30 * 232, C - 0.12 * 232, C + 0.64 * 232], fill=hi)


def e_omega(img, v):
    f = ImageFont.truetype(SERIF, 400)
    d = ImageDraw.Draw(img)
    d.text((C, C + 10), "Ω", font=f, fill=v["emb"], anchor="mm")


def e_hydra(img, v):
    d = ImageDraw.Draw(img)
    col = v["emb"]
    heads = [(-0.78, -0.55), (0.0, -0.92), (0.78, -0.55)]
    for hx, hy in heads:
        pts = []
        for i in range(31):
            t = i / 30
            x = (1 - t) ** 2 * 0 + 2 * (1 - t) * t * (hx * 0.15) + t * t * hx
            y = (1 - t) ** 2 * 1.0 + 2 * (1 - t) * t * 0.1 + t * t * hy
            pts.append((x, y))
        for i, (x, y) in enumerate(pts):
            r = (0.20 - 0.08 * (i / 30)) * 232
            px, py = U(x, y)
            d.ellipse([px - r, py - r, px + r, py + r], fill=col)
        px, py = U(hx, hy)
        sx = 1 if hx >= 0 else -1
        if hx == 0:
            sx = 0
        # head + snout
        d.ellipse([px - 0.26 * 232, py - 0.2 * 232, px + 0.26 * 232, py + 0.2 * 232], fill=col)
        d.polygon([(px + sx * 0.1 * 215 - (0.16 * 215 if sx == 0 else 0), py - 0.2 * 215),
                   (px + sx * 0.42 * 215, py - 0.26 * 215 if sx else py - 0.5 * 215),
                   (px + sx * 0.12 * 232 + (0.16 * 215 if sx == 0 else 0), py + 0.06 * 215)], fill=col)
        d.ellipse([px - 4 - 8, py - 30, px + 18, py - 6], fill=v["lens"][1])
    base = U(0, 1.0)
    d.ellipse([base[0] - 70, base[1] - 50, base[0] + 70, base[1] + 40], fill=col)


def _skull(d, k, bone, dark, glow=None):
    d.ellipse([C - 0.56 * k, C - 0.8 * k, C + 0.56 * k, C + 0.28 * k], fill=bone)
    d.rounded_rectangle([C - 0.36 * k, C + 0.1 * k, C + 0.36 * k, C + 0.6 * k], radius=int(0.12 * k), fill=bone)
    for ex in (-0.24, 0.24):
        d.ellipse([C + (ex - 0.17) * k, C - 0.28 * k, C + (ex + 0.17) * k, C + 0.06 * k], fill=dark)
        if glow:
            d.ellipse([C + (ex - 0.07) * k, C - 0.19 * k, C + (ex + 0.07) * k, C - 0.04 * k], fill=glow)
    d.polygon([U(0, 0.03, k), U(-0.09, 0.25, k), U(0.09, 0.25, k)], fill=dark)
    for tx in (-0.28, -0.14, 0, 0.14, 0.28):
        d.rectangle([C + (tx - 0.015) * k, C + 0.38 * k, C + (tx + 0.015) * k, C + 0.58 * k], fill=dark)
    d.line([U(-0.36, 0.38, k), U(0.36, 0.38, k)], fill=dark, width=6)


def e_skull_cog(img, v):
    d = ImageDraw.Draw(img)
    pts = []
    for i in range(10):
        a0 = 2 * math.pi * i / 10
        for da, r in ((-0.30, 205), (-0.16, 245), (0.16, 245), (0.30, 205)):
            a = a0 + da * 0.6283
            pts.append((C + r * math.cos(a), C + r * math.sin(a)))
    d.polygon(pts, fill=v["emb_hi"])
    d.ellipse([C - 200, C - 200, C + 200, C + 200], fill=v["lens"][1])
    _skull(d, 190, v["emb"], v["lens"][1])


def e_wolf(img, v):
    d = ImageDraw.Draw(img)
    pts = [(-0.80, -0.95), (-0.40, -0.45), (0, -0.55), (0.40, -0.45), (0.80, -0.95), (0.85, -0.20),
           (0.55, 0.35), (0.18, 0.80), (0, 1.0), (-0.18, 0.80), (-0.55, 0.35), (-0.85, -0.20)]
    d.polygon([U(x, y, 200) for x, y in pts], fill=v["emb"])
    for sx in (-1, 1):
        d.polygon([U(sx * 0.15, -0.08, 200), U(sx * 0.62, -0.22, 200), U(sx * 0.50, 0.06, 200)], fill=v["lens"][1])
    d.polygon([U(-0.12, 0.74, 200), U(0.12, 0.74, 200), U(0, 0.96, 200)], fill=v["lens"][1])


def e_sword(img, v):
    d = ImageDraw.Draw(img)
    col = v["emb"]
    for side in (-1, 1):
        for i in range(5):
            ang = math.radians(15 + i * 14)
            ox, oy = U(side * 0.12, 0.05)
            L = (0.95 - 0.1 * i) * 215
            tip = (ox + side * math.cos(ang) * L, oy - math.sin(ang) * L)
            nx, ny = -math.sin(ang) * side * -1, -math.cos(ang) * 1
            w = 26
            d.polygon([(ox, oy), (ox + side * math.cos(ang) * L * 0.5 + w * 0.0, oy - math.sin(ang) * L * 0.5 - w),
                       tip, (ox + side * math.cos(ang) * L * 0.5, oy - math.sin(ang) * L * 0.5 + w)], fill=col)
    d.polygon([U(0, -1.05), U(0.12, -0.8), U(0.12, 0.4), U(-0.12, 0.4), U(-0.12, -0.8)], fill=v["emb_hi"])
    d.rectangle([*U(-0.5, 0.4), *U(0.5, 0.52)], fill=v["emb_hi"])
    d.rectangle([*U(-0.07, 0.52), *U(0.07, 0.82)], fill=v["emb_hi"])
    d.ellipse([*U(-0.12, 0.8), *U(0.12, 1.04)], fill=v["emb_hi"])


def e_fist(img, v):
    d = ImageDraw.Draw(img)
    col, line = v["emb"], v["lens"][1]
    d.rounded_rectangle([*U(-0.52, -0.18), *U(0.52, 0.55)], radius=26, fill=col)
    for x0 in (-0.52, -0.26, 0.0, 0.26):
        d.rounded_rectangle([*U(x0 + 0.01, -0.62), *U(x0 + 0.25, -0.05)], radius=24, fill=col, outline=line, width=5)
    d.rounded_rectangle([*U(-0.78, -0.02), *U(-0.48, 0.38)], radius=22, fill=col, outline=line, width=5)
    d.rectangle([*U(-0.40, 0.55), *U(0.40, 0.88)], fill=col, outline=line, width=5)
    d.line([U(-0.40, 0.66), U(0.40, 0.66)], fill=line, width=6)


EMBLEMS = {"drop": e_drop, "omega": e_omega, "hydra": e_hydra, "skullcog": e_skull_cog,
           "wolf": e_wolf, "sword": e_sword, "fist": e_fist}


# ---------------------------------------------------------------- composition
def build(v):
    img = canvas()
    scale = OUTER[v["outer"]](img, *v["outer_cols"], **v.get("outer_kw", {}))
    core = canvas()
    # dark groove + band
    paint(core, ring(880, 840), solid((18, 14, 12)))
    band = ring(835, 640)
    if v.get("hazard"):
        st = Image.new("RGBA", (S, S), v["band"][1] + (255,))
        sd = ImageDraw.Draw(st)
        for k in range(-S, 2 * S, 150):
            sd.polygon([(k, 0), (k + 75, 0), (k + 75 + S, S), (k + S, S)], fill=v["band"][0] + (255,))
        paint(core, band, st)
    else:
        paint(core, band, grad(v["band"][0], v["band"][1], 900))
    bevel(core, band, 14)
    d = ImageDraw.Draw(core)
    for i in range(16):
        a = 2 * math.pi * i / 16 + math.pi / 16
        cx, cy = C + 738 * math.cos(a), C + 738 * math.sin(a)
        r = 24
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=v["rivet"] + (255,), outline=(20, 16, 12, 255), width=5)
        d.ellipse([cx - 15, cy - 15, cx + 3, cy + 3], fill=tuple(min(255, c + 60) for c in v["rivet"]) + (255,))
    Rw = 640
    for (c1, c2), (a0, a1) in zip(v["seg"], ((30, 150), (150, 270), (270, 390))):
        poly = [(C, C)] + [(C + Rw * math.cos(math.radians(a0 + (a1 - a0) * k / 60)),
                            C - Rw * math.sin(math.radians(a0 + (a1 - a0) * k / 60))) for k in range(61)]
        m = ImageChops.multiply(poly_mask(poly), disk(Rw))
        paint(core, m, grad(c1, c2, Rw))
        bevel(core, m, 12, 0.5)
    dd = ImageDraw.Draw(core)
    for ang in (30, 150, 270):
        a = math.radians(ang)
        dd.line([(C, C), (C + Rw * math.cos(a), C - Rw * math.sin(a))], fill=(15, 12, 10, 255), width=22)
    dd.ellipse([C - Rw, C - Rw, C + Rw, C + Rw], outline=(15, 12, 10, 255), width=18)
    paint(core, disk(300), grad(v["steel"][0], v["steel"][1], 320))
    paint(core, disk(262), solid((14, 12, 12)))
    lens = disk(246)
    paint(core, lens, grad(v["lens"][0], v["lens"][1], 260, light=(-0.2, -0.3)))
    bevel(core, lens, 10, 0.4)
    EMBLEMS[v["emblem"]](core, v)
    if scale != 1.0:
        n = int(S * scale)
        small = core.resize((n, n), Image.LANCZOS)
        core = canvas()
        core.alpha_composite(small, ((S - n) // 2, (S - n) // 2))
    img.alpha_composite(core)

    # weathering
    rng = np.random.default_rng(40)
    noise = (rng.normal(0, 1, (S, S)) * 26).astype(np.int16)
    n_ = Image.fromarray(np.clip(128 + noise, 0, 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.2))
    grain = Image.merge("RGBA", (n_, n_, n_, Image.new("L", (S, S), 46)))
    sc = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sc)
    for _ in range(70):
        x0, y0 = rng.integers(60, S - 60, 2)
        L = rng.integers(40, 220)
        a = rng.uniform(0, math.pi)
        sd.line([(x0, y0), (x0 + L * math.cos(a), y0 + L * math.sin(a))],
                fill=(10, 8, 6, int(rng.integers(60, 130))), width=int(rng.integers(2, 5)))
    for _ in range(40):
        x0, y0 = rng.integers(60, S - 60, 2)
        L = rng.integers(30, 150)
        a = rng.uniform(0, math.pi)
        sd.line([(x0, y0), (x0 + L * math.cos(a), y0 + L * math.sin(a))],
                fill=(240, 225, 190, int(rng.integers(30, 70))), width=2)
    alpha = img.getchannel("A")
    for layer in (grain, sc):
        l = layer.copy()
        l.putalpha(ImageChops.multiply(l.getchannel("A"), alpha))
        img.alpha_composite(l)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sa = Image.new("L", (S, S), 0)
    ImageDraw.Draw(sa).ellipse([C - 1000, C - 1000, C + 1000, C + 1000], fill=255)
    if v["outer"] == "wings":
        sa = alpha.point(lambda p: 255 if p > 0 else 0)
    sa = sa.filter(ImageFilter.GaussianBlur(26))
    shadow.paste((0, 0, 0, 150), mask=ImageChops.offset(sa, 0, 22))
    return Image.alpha_composite(shadow, img).resize((1024, 1024), Image.LANCZOS)


GOLD = ((205, 160, 70), (70, 45, 18))
VARIANTS = {
    "blood-angels": dict(
        outer="wings", outer_cols=((235, 225, 200), (150, 120, 80)),
        band=((150, 24, 24), (40, 6, 8)), rivet=(190, 150, 60),
        seg=(((200, 40, 40), (80, 8, 12)), ((222, 176, 64), (104, 64, 6)), ((60, 22, 24), (14, 8, 8))),
        steel=((236, 220, 170), (90, 70, 40)), lens=((150, 20, 24), (40, 4, 6)),
        emblem="drop", emb=(244, 238, 226), emb_hi=(255, 255, 255)),
    "ultramarines": dict(
        outer="laurel", outer_cols=((230, 190, 80), (110, 80, 20)),
        band=((40, 80, 170), (10, 22, 60)), rivet=(210, 170, 70),
        seg=(((40, 90, 190), (10, 28, 90)), ((222, 176, 64), (104, 64, 6)), ((20, 40, 100), (6, 12, 40))),
        steel=((235, 235, 245), (80, 90, 120)), lens=((30, 70, 170), (8, 20, 70)),
        emblem="omega", emb=(236, 196, 84), emb_hi=(236, 196, 84)),
    "alpha-legion": dict(
        outer="scales", outer_cols=((70, 170, 150), (12, 56, 50)),
        band=((30, 90, 80), (8, 28, 26)), rivet=(170, 190, 150),
        seg=(((60, 150, 130), (10, 56, 50)), ((30, 100, 70), (8, 36, 24)), ((176, 140, 70), (80, 56, 18))),
        steel=((200, 230, 220), (60, 90, 84)), lens=((18, 60, 56), (4, 16, 16)),
        emblem="hydra", emb=(150, 225, 200), emb_hi=(150, 225, 200)),
    "iron-warriors": dict(
        outer="cog", outer_cols=((130, 130, 138), (34, 34, 40)),
        band=((226, 188, 30), (20, 18, 16)), hazard=True, rivet=(150, 150, 158),
        seg=(((150, 150, 158), (46, 46, 52)), ((60, 60, 66), (14, 14, 16)), ((220, 184, 40), (110, 84, 8))),
        steel=((205, 205, 212), (70, 70, 78)), lens=((70, 70, 78), (10, 10, 12)),
        emblem="skullcog", emb=(222, 222, 228), emb_hi=(226, 188, 30)),
    "space-wolves": dict(
        outer="cog", outer_cols=((230, 226, 214), (110, 106, 96)), outer_kw=dict(teeth=18, pointed=True),
        band=((90, 110, 130), (24, 30, 40)), rivet=(220, 216, 200),
        seg=(((150, 170, 190), (40, 56, 74)), ((236, 236, 240), (110, 118, 130)), ((50, 76, 110), (12, 24, 44))),
        steel=((235, 238, 245), (90, 100, 116)), lens=((50, 80, 120), (10, 22, 44)),
        emblem="wolf", emb=(240, 242, 246), emb_hi=(240, 242, 246)),
    "dark-angels": dict(
        outer="wings", outer_cols=((70, 110, 70), (18, 40, 24)),
        band=((22, 66, 40), (6, 20, 12)), rivet=(200, 190, 150),
        seg=(((40, 110, 64), (8, 40, 24)), ((228, 220, 190), (120, 112, 84)), ((22, 30, 26), (6, 8, 8))),
        steel=((228, 222, 196), (90, 86, 64)), lens=((26, 80, 50), (6, 24, 14)),
        emblem="sword", emb=(232, 226, 200), emb_hi=(250, 246, 230)),
    "imperial-fists": dict(
        outer="plain", outer_cols=((240, 200, 40), (120, 84, 8)),
        band=((226, 186, 32), (110, 80, 8)), rivet=(24, 20, 18),
        seg=(((240, 200, 40), (130, 94, 10)), ((30, 28, 28), (8, 8, 8)), ((236, 232, 220), (130, 126, 112))),
        steel=((250, 226, 120), (120, 90, 20)), lens=((240, 200, 50), (140, 100, 12)),
        emblem="fist", emb=(20, 18, 18), emb_hi=(20, 18, 18)),
}


def main(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, v in VARIANTS.items():
        im = build(v)
        im.save(out / f"{name}-1024.png")
        im.save(out / f"{name}.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        print("ok", name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
