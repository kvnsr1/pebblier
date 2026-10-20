#!/usr/bin/env python3
"""Reconstruct the dial, not the photograph. No source image is needed.

Roman glyphs are original polygons with hairline serifs and radial shearing.
Everything is drawn at 8x each target size, then grid-fitted/quantized for Pebble.
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "resources/images"
S = 8
SERIF = ROOT / "assets/fonts/Tinos-Bold.ttf"
SANS = ROOT / "assets/fonts/Abel-Regular.ttf"


def roman_polygons(text):
    """100-unit cap-height; contrast and serifs drawn explicitly, no system font."""
    shapes, cursor = [], 0
    for letter in text:
        width = 36 if letter == "I" else 62
        if letter == "I":
            polys = [[(6, 0), (30, 0), (30, 100), (6, 100)]]
        elif letter == "V":
            polys = [[(1, 0), (27, 0), (45, 88), (38, 100)],
                     [(57, 0), (62, 0), (40, 100), (36, 100)]]
        else:
            polys = [[(0, 0), (28, 0), (62, 100), (34, 100)],
                     [(56, 0), (62, 0), (6, 100), (0, 100)]]
        # Hairline slab serifs are deliberately large enough to survive 1-bit.
        ends = [(0, width)] if letter == "I" else [(0, 24), (width - 24, width)]
        for a, b in ends:
            polys.extend([[(a, 0), (b, 0), (b, 3), (a, 3)],
                          [(a, 97), (b, 97), (b, 100), (a, 100)]])
        shapes.extend([[(x + cursor, y) for x, y in p] for p in polys])
        cursor += width + 3
    return shapes


def numeral(draw, text, box, orientation=0, shear=0):
    shapes = roman_polygons(text)
    angle = math.radians(orientation)
    def transform(p):
        x, y = p
        x += shear * y
        return (x * math.cos(angle) - y * math.sin(angle),
                x * math.sin(angle) + y * math.cos(angle))
    shapes = [[transform(p) for p in poly] for poly in shapes]
    points = [p for poly in shapes for p in poly]
    xmin, xmax = min(p[0] for p in points), max(p[0] for p in points)
    ymin, ymax = min(p[1] for p in points), max(p[1] for p in points)
    x, y, w, h = box
    for poly in shapes:
        draw.polygon([((x + (px-xmin)/(xmax-xmin)*w)*S,
                       (y + (py-ymin)/(ymax-ymin)*h)*S) for px, py in poly], fill=0)


def lettering(image, text, box, font_path, tracking=0):
    """Fit cap-height to a deliberate box; no dependence on font baselines."""
    # Linux wheels can enable optional RAQM shaping while macOS wheels use
    # BASIC. Explicit layout keeps glyph metrics identical on both systems.
    font = ImageFont.truetype(str(font_path), 96, layout_engine=ImageFont.Layout.BASIC)
    widths = [font.getlength(c) for c in text]
    bounds = font.getbbox(text)
    mask = Image.new("L", (math.ceil(sum(widths) + tracking*(len(text)-1))+4, 140), 0)
    draw = ImageDraw.Draw(mask)
    x = 0
    for c, width in zip(text, widths):
        draw.text((x, -bounds[1]), c, font=font, fill=255)
        x += width + tracking
    mask = mask.crop(mask.getbbox())
    if font_path == SANS:
        # Optical compensation: retain thin lettering after native 1-bit rasterization.
        mask = mask.filter(ImageFilter.MaxFilter(5))
    x, y, w, h = box
    mask = mask.resize((round(w*S), round(h*S)), Image.Resampling.LANCZOS)
    image.paste(0, (round(x*S), round(y*S)), mask)


def dial(width, height, mono):
    # The railway stays square. Extra screen height goes into numeral bands.
    k = width / 144
    yk = height / 168
    image = Image.new("L", (width*S, height*S), 255)
    draw = ImageDraw.Draw(image)
    def box(x, y, w, h):
        return (x*k, y*yk, w*k, h*yk)
    # Deliberate radial typography, including traditional watchmaker's IIII.
    placements = [
        ("XI", (24, 2, 30, 25), 0, .48),
        ("XII", (59, 2, 29, 25), 0, 0),
        ("I", (98, 2, 19, 25), 0, -.52),
        ("X", (2, 32, 20, 32), 90, -.62),
        ("IX", (2, 72, 20, 25), 90, 0),
        ("VIII", (2, 103, 20, 43), 90, .6),
        ("II", (123, 32, 20, 32), 90, -.6),
        ("III", (123, 72, 20, 25), 90, 0),
        ("IIII", (123, 103, 20, 43), 90, .6),
        ("VII", (15, 136, 35, 28), 180, -.45),
        ("V", (99, 136, 23, 28), 180, .5),
    ]
    for text, b, orient, shear in placements:
        numeral(draw, text, box(*b), orient, shear)

    cx, cy = width/2, round(79*yk)
    half, inset = round(48*k), max(4, round(4*k))
    outer = (cx-half, cy-half, cx+half, cy+half)
    inner = tuple(v + (inset if i < 2 else -inset) for i,v in enumerate(outer))
    # Ray/square intersections produce the characteristic diagonal railway.
    mask = Image.new("L", image.size, 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle(tuple(round(v*S) for v in outer), radius=round(3*k*S), fill=255)
    md.rounded_rectangle(tuple(round(v*S) for v in inner), radius=round(2*k*S), fill=0)
    ticks = Image.new("L", image.size, 255)
    td = ImageDraw.Draw(ticks)
    for minute in range(60):
        angle = minute*math.tau/60
        dx, dy = math.sin(angle), -math.cos(angle)
        r = half / max(abs(dx), abs(dy))
        ri = (half-inset) / max(abs(dx), abs(dy))
        # Snap before Pillow sees the coordinates: ARM/x86 trig ulps near an
        # integer endpoint otherwise choose different raster pixels.
        td.line(tuple(round(v*S) for v in (cx+ri*dx,cy+ri*dy,cx+r*dx,cy+r*dy)),
                fill=0, width=round((3.5 if minute%5==0 else .65)*k*S))
    image.paste(ticks, (0, 0), mask)
    draw = ImageDraw.Draw(image)
    for rect, radius in [(outer, 3*k), (inner, 2*k)]:
        draw.rounded_rectangle(tuple(round(v*S) for v in rect), radius=round(radius*S),
                               outline=0, width=max(S, round(.65*k*S)))

    lettering(image, "PEBBLIER", box(48, 47, 49, 7), SERIF)
    lettering(image, "AUTOMATIC", box(53, 109, 39, 5.5), SANS, tracking=12)
    lettering(image, "SWISS", box(49, 162, 13, 4), SANS, tracking=5)
    lettering(image, "MADE", box(83, 162, 13, 4), SANS, tracking=5)
    # Tiny signature lives in the open diagonal of VII, as in the reference.
    signature = Image.new("L", (22*S, 5*S), 255)
    lettering(signature, "PEBBLIER", (0, 0, 22, 4), SERIF)
    signature = signature.rotate(56, expand=True, resample=Image.Resampling.BICUBIC, fillcolor=255)
    # Composite ink only: the rotated signature's white bounding rectangle
    # must not erase the nearby VII strokes.
    image.paste(0, (round(34*k*S), round(141*yk*S)), signature.point(lambda v: 255-v))
    draw = ImageDraw.Draw(image)
    x, y, w, h = box(63, 133, 18, 28)
    # Nested frame is graphic; date interior and digit are drawn at runtime.
    for offset, shade in [(0,0), (.8,255), (1.6,85 if not mono else 0), (2.4,255)]:
        draw.rounded_rectangle((round((x+offset*k)*S), round((y+offset*k)*S),
                                round((x+w-offset*k)*S), round((y+h-offset*k)*S)),
                               radius=round(max(.3,1.7-offset*.5)*k*S), fill=shade)
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    if mono:
        # No dithering: crisp black serifs against a clean white field.
        image = image.point(lambda v: 255 if v >= 155 else 0).convert("1")
    else:
        image = image.point(lambda v: round(v/85)*85).convert("P")
    return image


def digits(width, mono):
    k = width/144
    cell_w, cell_h = round(7*k), round(17*k)
    image = Image.new("L", (cell_w*10*S, cell_h*S), 255)
    for n in range(10):
        lettering(image, str(n), (n*cell_w+.5*k, .5*k, cell_w-k, cell_h-k), SANS)
    image = image.resize((cell_w*10, cell_h), Image.Resampling.LANCZOS)
    if mono:
        return image.point(lambda v: 255 if v >= 155 else 0).convert("1")
    return image.point(lambda v: round(v/85)*85).convert("P")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for width, height in [(144,168), (200,228)]:
        for mono in [False,True]:
            suffix = f"~{width}w~{'bw' if mono else 'color'}"
            # Emery is color-only; don't package unused art.
            if width == 200 and mono:
                continue
            dial(width,height,mono).save(OUT/f"dial{suffix}.png", optimize=True)
            digits(width,mono).save(OUT/f"digits{suffix}.png", optimize=True)
    # Small, legible launcher mark. Store imagery comes from actual screenshots.
    icon = Image.new("1", (25,25), 1)
    d = ImageDraw.Draw(icon)
    d.rounded_rectangle((2,2,22,22), radius=3, outline=0)
    d.line((5,7,12,13,19,5), fill=0, width=2)
    d.ellipse((10,11,14,15), fill=0)
    icon.save(OUT/"menu_icon.png")


if __name__ == "__main__":
    main()
