#!/usr/bin/env python3
"""Verify generated pixels, independent of platform PNG/zlib compression."""
from pathlib import Path
import subprocess
import sys
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
paths = sorted((ROOT/"resources/images").glob("*.png"))
expected = {path:Image.open(path).convert("RGB") for path in paths}
subprocess.run([sys.executable,str(ROOT/"scripts/generate_assets.py")],check=True)
assert set(paths) == set((ROOT/"resources/images").glob("*.png")), "Resource set changed"
for path, reference in expected.items():
    generated = Image.open(path).convert("RGB")
    assert reference.size == generated.size, f"Dimensions changed: {path.name}"
    delta = ImageChops.difference(reference,generated)
    assert delta.getbbox() is None, f"Generated pixels differ: {path.name}, region {delta.getbbox()}"
print(f"All {len(paths)} generated images match committed pixels exactly.")
