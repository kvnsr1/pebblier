#!/usr/bin/env python3
"""Build deterministic fixtures and capture the real PebbleOS renderer in QEMU.

Fixtures are compile-time only because Emery's QEMU RTC ignores emu-set-time.
Always rebuild a normal PBW in finally: fixture binaries must not be distributed.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PLATFORMS = ["basalt", "aplite", "diorite", "emery", "flint"]
TIMES = [(10,10,10), (3,0,0), (6,30,45), (12,0,0)]
DATES = [1,18,31]


def run(args, log, env=None):
    result = subprocess.run(args, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True, timeout=60)
    log.write("$ " + " ".join(args) + "\n" + result.stdout + "\n")
    log.flush()
    result.check_returncode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platforms", nargs="+", choices=PLATFORMS, default=PLATFORMS)
    parser.add_argument("--smoke", action="store_true", help="10:10:10, date 18 only")
    parser.add_argument("--resume", action="store_true", help="Keep existing screenshots from an interrupted matrix")
    args = parser.parse_args()
    screenshots = ROOT / "docs/screenshots"
    results = ROOT / "test-results"
    screenshots.mkdir(parents=True, exist_ok=True)
    results.mkdir(exist_ok=True)
    records = []
    cases = [((10,10,10),18)] if args.smoke else [(t,d) for t in TIMES for d in DATES]
    env = dict(os.environ)
    env.pop("PEBBLIER_FIXTURE", None)
    env.pop("PEBBLIER_SECONDS", None)
    with (results/"emulators.log").open("w") as log:
        try:
            for (hour,minute,second),day in cases:
                stamp = f"{hour:02}{minute:02}{second:02}-{day:02}"
                fixture_env = dict(env, PEBBLIER_FIXTURE=f"{hour}:{minute}:{second}:{day}")
                needed = [p for p in args.platforms if not
                          (args.resume and (screenshots/f"{p}-{stamp}.png").exists())]
                if needed:
                    print(f"Building fixture {stamp}", flush=True)
                    run(["pebble", "build"], log, fixture_env)
                for platform in args.platforms:
                    filename = f"{platform}-{stamp}.png"
                    if platform in needed:
                        try:
                            run(["pebble","install","--emulator",platform], log, env)
                        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                            # SDK emulators can stall after repeated installs. Restart,
                            # retaining flash/app data, and retry once. Never auto-wipe.
                            print(f"Restarting stalled emulator; retrying {platform}", flush=True)
                            run(["pebble","kill"], log, env)
                            run(["pebble","install","--emulator",platform], log, env)
                        run(["pebble","screenshot",str(screenshots/filename),"--emulator",platform,
                             "--no-open","--no-correction"], log, env)
                    records.append({"platform":platform, "time":f"{hour:02}:{minute:02}:{second:02}",
                                    "day":day, "file":filename, "source":"QEMU, compile-time clock fixture"})
                    (screenshots/"manifest.json").write_text(json.dumps(records, indent=2)+"\n")
                    print(f"{'Captured' if platform in needed else 'Retained'} {filename}", flush=True)
        finally:
            print("Restoring production clock build", flush=True)
            run(["pebble","build"], log, env)
    (screenshots/"manifest.json").write_text(json.dumps(records, indent=2)+"\n")
    print(f"Captured {len(records)} emulator screenshots. Production PBW restored.", flush=True)


if __name__ == "__main__":
    main()
