# Validation results

Executed locally on macOS with **pebble-tool 5.0.40**, **SDK 4.33.1**, and the SDK's actual PebbleOS/QEMU emulators. No physical watch testing has been performed.

## Build and timekeeping

- The default production build compiled successfully for Basalt, Aplite, Diorite, Emery, and Flint and produced `build/pebblier.pbw` (approximately 49 KB).
- `scripts/check_bundle.py` verified all five native binaries and resource packs, watchface metadata, and the absence of phone JavaScript or capabilities.
- `scripts/test.sh` passed exact angle assertions for the requested poses and an exhaustive 43,200-second hour-hand cycle, including 12-hour wrap and overflow checks.
- The optional `PEBBLIER_SECONDS=0` build compiled for every target. [Basalt minute mode](screenshots/basalt-minute-mode.png) was installed and captured with the seconds hand and counterweight absent. The final delivered PBW was then rebuilt with the normal live clock and seconds enabled.
- `scripts/check_live_clock.py` passed against the **production build**, without fixed-time defines: the native hands advanced, the date read 31 before midnight and 1 afterward, and the date crops matched the visual fixtures pixel for pixel. The test clock was restored afterward. [Before midnight](screenshots/live-before-midnight.png), [after midnight](screenshots/live-after-midnight.png), [machine-readable result](screenshots/live-clock.json).

## Visual matrix

All **60 cases** were installed, captured, and visually reviewed: **5 platforms × 4 times × 3 dates**. The matrix covers **10:10:10, 03:00:00, 06:30:45, 12:00:00**, each with dates **1, 18, 31**.

| Target | Individual captures | Enlarged contact sheet | Result |
| --- | --- | --- | --- |
| Basalt | 12 at 144 × 168 | [Basalt matrix](screenshots/basalt-matrix.png) | Passed |
| Aplite | 12 at 144 × 168 | [Aplite matrix](screenshots/aplite-matrix.png) | Passed |
| Diorite | 12 at 144 × 168 | [Diorite matrix](screenshots/diorite-matrix.png) | Passed |
| Emery | 12 at 200 × 228 | [Emery matrix](screenshots/emery-matrix.png) | Passed |
| Flint | 12 at 144 × 168 | [Flint matrix](screenshots/flint-matrix.png) | Passed |

[Capture manifest](screenshots/manifest.json) identifies the platform, exact fixture time/date, filename, and capture source. Individual PNGs are uncorrected SDK screenshots at native resolution. Contact sheets use integer nearest-neighbor enlargement and labels; they are compositions of the captured images, not simulated renderings.

The visual fixtures are compile-time overrides in the same C renderer. This makes the requested positions deterministic despite clock advancement and Emery emulator clock behavior. The fixture code is absent from normal builds. `validate_emulators.py` restores a production PBW even if a capture fails. `--resume` retains captures from an interrupted run; use a complete fresh run after visual changes. All monochrome cases were recaptured after strengthening the hand silhouettes; color rendering was unchanged by that platform-conditional correction.

Review checked railway alignment and line weights, wordmark placement, centered one-/two-digit dates, exact pivot alignment, fractional hour progression, long hand clearance, and hand overlap at 12:00. The monochrome hour/minute silhouettes are separated from black numerals with white outer bevels. The tiny signature and bottom text are retained with optical compensation, with better readability on Emery.

## Footprint

The SDK reports these default-build values. Runtime allocations for the cached dial, digit atlas, layers, and paths use additional heap; these figures are **not total runtime RAM**.

| Platform | Resources | Linked RAM footprint | Heap available before runtime allocations |
| --- | ---: | ---: | ---: |
| Basalt | 6,669 B | 2,727 B | 62,809 B |
| Aplite | 7,427 B | 2,763 B | 21,813 B |
| Diorite | 5,653 B | 2,763 B | 62,773 B |
| Emery | 7,895 B | 2,727 B | 128,345 B |
| Flint | 5,653 B | 2,763 B | 62,773 B |

The resource difference between Aplite and newer monochrome targets comes from the SDK's bitmap encoding. The static color dial is cached in a palettized bitmap rather than a full-color framebuffer; no fctx scratch buffer is allocated. Resources are allocated once at load, reused on ticks, and destroyed on unload.

## Reproduce

With `pebble` and Pillow on the active Python environment:

```sh
sh scripts/test.sh
python3 scripts/validate_emulators.py
python3 scripts/contact_sheet.py
python3 scripts/check_live_clock.py
python3 scripts/check_bundle.py build/pebblier.pbw
```

`check_live_clock.py` also imports `pebble-tool`/`libpebble2`; the README gives a self-contained `uv run` invocation for that test.

## Limits and emulator notes

- These are native-resolution reconstructions. Fine serif detail, metallic gradients, and the miniature lettering cannot match a 1,254-pixel source exactly at 144 pixels. Color hands use Pebble's discrete blue palette; monochrome devices use black silhouettes with white separation.
- Long hands cross the square railway at axial poses, and all three hands overlap at 12:00. The date digits remain centered and the static date frame sits below the railway. No assets are stretched on the watch.
- Emery stalled during repeated installation and subsequently hung on the PebbleOS boot screen. Restarting alone did not recover that saved state. Its data was preserved at `~/Library/Application Support/Pebble SDK/4.33.1/emery.before-pebblier-validation`, and a fresh Emery emulator state completed the remaining captures. No other emulator data was wiped. The underlying firmware/state issue was not diagnosed.
- Each CLI `--emulator` connection sends the host time, so separate `emu-set-time` and `screenshot` calls are unsuitable for a midnight test. The production clock test keeps one SDK connection open for clock injection and both captures. This test implementation was verified against the installed CLI source.
- Battery lifetime and physical LCD appearance have not been measured. The default seconds hand requires one redraw per second; minute mode is available as a build option. Round targets require a separately designed layout and are not included.
- The SDK linker emits its RWX LOAD-segment warning; the application's C source compiles without application warnings in both build modes. No store release has been published.
