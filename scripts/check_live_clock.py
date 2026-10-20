#!/usr/bin/env python3
"""Exercise the production tick/date path across midnight in the Basalt emulator."""
import datetime
import json
import os
from pathlib import Path
import subprocess
import time
from PIL import Image, ImageChops
from libpebble2.communication import PebbleConnection
from libpebble2.communication.transports.websocket import WebsocketTransport
from libpebble2.protocol.system import TimeMessage, SetUTC
from libpebble2.services.screenshot import Screenshot
from pebble_tool.sdk.emulator import get_emulator_info

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT/"docs/screenshots"


def main():
    env = dict(os.environ)
    env.pop("PEBBLIER_FIXTURE", None)
    env.pop("PEBBLIER_SECONDS", None)
    def run(*args):
        subprocess.run(["pebble",*args],cwd=ROOT,env=env,check=True,timeout=60)
    run("build")
    run("install","--emulator","basalt")
    # Every CLI --emulator connection synchronizes time with the host. Use ONE
    # SDK connection for setting the clock and taking both captures, so the
    # screenshot command cannot silently undo the injected midnight time.
    info = get_emulator_info("basalt")
    transport = WebsocketTransport(f"ws://localhost:{info['pypkjs']['port']}/")
    connection = PebbleConnection(transport)
    connection.connect()
    connection.run_async()
    def capture(filename):
        rows = Screenshot(connection).grab_image()
        Image.frombytes("RGB", (len(rows[0])//3,len(rows)), b"".join(rows)).save(SHOTS/filename)
    target = datetime.datetime(2026,10,31,23,59,54,tzinfo=datetime.timezone.utc)
    try:
        connection.send_packet(TimeMessage(message=SetUTC(unix_time=int(target.timestamp()), utc_offset=0, tz_name="UTC")))
        time.sleep(1.2) # Allow one native tick to deliver the new local time.
        capture("live-before-midnight.png")
        time.sleep(6)
        capture("live-after-midnight.png")
        # Exact pixel comparison against independently captured date fixtures.
        rect = (65,143,79,160)
        for live,fixture in [("live-before-midnight.png","basalt-101010-31.png"),
                             ("live-after-midnight.png","basalt-101010-01.png")]:
            actual = Image.open(SHOTS/live).convert("RGB").crop(rect)
            expected = Image.open(SHOTS/fixture).convert("RGB").crop(rect)
            assert ImageChops.difference(actual,expected).getbbox() is None, live
        before = Image.open(SHOTS/"live-before-midnight.png").convert("RGB")
        after = Image.open(SHOTS/"live-after-midnight.png").convert("RGB")
        assert ImageChops.difference(before.crop((24,14,120,130)),
                                    after.crop((24,14,120,130))).getbbox(), "Hands did not advance"
        report = {"platform":"basalt", "build":"production local clock, no fixture defines",
                  "clock_input":"2026-10-31T23:59:54Z", "date_before":31,"date_after":1,
                  "assertions":["date crops match 31 and 1", "hands advance with system ticks"]}
        (SHOTS/"live-clock.json").write_text(json.dumps(report,indent=2)+"\n")
        print("Production clock passed: live hands advance and date rolls from 31 to 1 at midnight.")
    finally:
        transport.ws.close()
        env["TZ"] = "America/Los_Angeles"
        run("emu-set-time",str(int(time.time())),"--emulator","basalt")


if __name__ == "__main__":
    main()
