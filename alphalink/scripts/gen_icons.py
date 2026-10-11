#!/usr/bin/env python3
"""Generate the AlphaLink icon set from branding/logo_mask.png.

Usage: gen_icons.py <rustdesk-source-root>

Writes desktop (Windows/Linux/macOS), tray and Android launcher icons into an
upstream RustDesk checkout, using the AlphaLink palette: dark green surface and
green accent logo.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

BG = (0x11, 0x1A, 0x17, 255)
ACCENT = (0x5C, 0xB8, 0x88, 255)
MASK = Image.open(Path(__file__).resolve().parent.parent / "branding" / "logo_mask.png").convert("RGBA")


def tint(color, size):
    """Logo (alpha of the mask) painted in `color`, scaled to size x size."""
    alpha = MASK.getchannel("A").resize((size, size), Image.LANCZOS)
    img = Image.new("RGBA", (size, size), color)
    img.putalpha(alpha)
    return img


def tile(size, radius=0.22, logo=0.62, rounded=True, bg=BG):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * radius), fill=bg)
    else:
        d.rectangle([0, 0, size - 1, size - 1], fill=bg)
    l = int(size * logo)
    img.alpha_composite(tint(ACCENT, l), ((size - l) // 2, (size - l) // 2))
    return img


def save(img, path, size=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if size:
        img = img.resize((size, size), Image.LANCZOS)
    img.save(path)


def main(root):
    root = Path(root)
    big = tile(1024)
    # res/ (Linux packages, installer, Sciter)
    save(big, root / "res/icon.png", 1024)
    for name, size in {"32x32.png": 32, "64x64.png": 64, "128x128.png": 128, "128x128@2x.png": 256}.items():
        save(big, root / "res" / name, size)
    save(tile(1024, radius=0.0, logo=0.6, rounded=False), root / "res/mac-icon.png", 1024)
    sizes = [(s, s) for s in (16, 32, 48, 64, 128, 256)]
    big.save(root / "res/icon.ico", sizes=sizes)
    big.save(root / "res/tray-icon.ico", sizes=[(32, 32)])
    big.save(root / "flutter/windows/runner/resources/app_icon.ico", sizes=sizes)
    # macOS app icon + monochrome tray templates (dark / light menu bar)
    big.save(root / "flutter/macos/Runner/AppIcon.icns")
    for name, color in (("mac-tray-dark-x2.png", (0, 0, 0, 255)), ("mac-tray-light-x2.png", (255, 255, 255, 255))):
        save(tint(color, 60), root / "res" / name)
    # Flutter in-app logo
    save(big, root / "flutter/assets/icon.png", 512)
    # Android launcher: legacy + round + adaptive foreground + status-bar glyph
    density = {"mdpi": 1, "hdpi": 1.5, "xhdpi": 2, "xxhdpi": 3, "xxxhdpi": 4}
    for d, k in density.items():
        base = root / f"flutter/android/app/src/main/res/mipmap-{d}"
        save(tile(1024), base / "ic_launcher.png", int(48 * k))
        round_img = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        ImageDraw.Draw(round_img).ellipse([0, 0, 1023, 1023], fill=BG)
        round_img.alpha_composite(tint(ACCENT, 640), (192, 192))
        save(round_img, base / "ic_launcher_round.png", int(48 * k))
        fg = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        fg.alpha_composite(tint(ACCENT, 600), (212, 212))  # inside the adaptive safe zone
        save(fg, base / "ic_launcher_foreground.png", int(108 * k))
        save(tint((255, 255, 255, 255), 512), base / "ic_stat_logo.png", int(24 * k))
    bg_xml = root / "flutter/android/app/src/main/res/values/ic_launcher_background.xml"
    bg_xml.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        '    <color name="ic_launcher_background">#111a17</color>\n</resources>\n'
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
