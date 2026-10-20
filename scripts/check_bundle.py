#!/usr/bin/env python3
"""Fail if any requested native platform is missing from the PBW."""
import json
import sys
from zipfile import ZipFile

PLATFORMS = {"aplite", "basalt", "diorite", "emery", "flint"}
with ZipFile(sys.argv[1]) as bundle:
    names = set(bundle.namelist())
    for platform in PLATFORMS:
        prefix = platform + "/"
        for filename in ["pebble-app.bin", "app_resources.pbpack", "manifest.json"]:
            assert prefix + filename in names, (platform, filename)
    info = json.loads(bundle.read("appinfo.json"))
    assert info["watchapp"]["watchface"] is True
    assert not info.get("capabilities")
    assert set(info["targetPlatforms"]) == PLATFORMS
    assert not any("pebble-js-app.js" in name for name in names)
print("PBW contains all five native watchfaces, resources, and no phone JavaScript.")
