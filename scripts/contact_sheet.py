#!/usr/bin/env python3
"""Assemble labeled QEMU screenshots without altering any captured pixels."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT/"docs/screenshots"
PLATFORMS = ["basalt","aplite","diorite","emery","flint"]


def main():
    font = ImageFont.load_default(size=13)
    for platform in PLATFORMS:
        files = [SHOTS/f"{platform}-{time}-{date}.png"
                 for time in ["101010","030000","063045","120000"] for date in ["01","18","31"]]
        if not all(f.exists() for f in files):
            continue
        # 2x nearest-neighbor presentation; originals remain at native resolution.
        w,h = Image.open(files[0]).size
        tile_w, tile_h = w*2+24, h*2+38
        sheet = Image.new("RGB", (tile_w*3,tile_h*4), "#e9e8e4")
        draw = ImageDraw.Draw(sheet)
        for i,file in enumerate(files):
            x,y = (i%3)*tile_w,(i//3)*tile_h
            shot = Image.open(file).convert("RGB").resize((w*2,h*2), Image.Resampling.NEAREST)
            sheet.paste(shot,(x+12,y+27))
            draw.text((x+12,y+7),file.stem,fill="#333333",font=font)
        sheet.save(SHOTS/f"{platform}-matrix.png",optimize=True)
    # One larger hero per hardware layout, all taken from real emulator captures.
    tile_w, tile_h = 432,530
    sheet = Image.new("RGB",(tile_w*3,tile_h),"#e9e8e4")
    draw = ImageDraw.Draw(sheet)
    for i,platform in enumerate(["basalt","emery","flint"]):
        shot = Image.open(SHOTS/f"{platform}-101010-18.png").convert("RGB")
        scale = 2
        shot = shot.resize((shot.width*scale,shot.height*scale),Image.Resampling.NEAREST)
        sheet.paste(shot,(i*tile_w+(tile_w-shot.width)//2,42))
        draw.text((i*tile_w+20,16),platform,fill="#333333",font=font)
    sheet.save(SHOTS/"overview.png",optimize=True)


if __name__ == "__main__":
    main()
