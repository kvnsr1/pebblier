# Artwork sources

The dial is reconstructed by `scripts/generate_assets.py` using original Roman numeral polygons and railway geometry. The supplied image is a visual reference only and is not embedded in the application. The generator is the editable source for every committed PNG.

Fonts are bundled so regeneration does not depend on locally installed fonts or network access:

| File | Use | Upstream |
| --- | --- | --- |
| `fonts/Tinos-Bold.ttf` | PEBBLIER and tiny diagonal signature | [Tinos](https://github.com/googlefonts/tinos), retrieved from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/tinos) |
| `fonts/Abel-Regular.ttf` | AUTOMATIC, SWISS / MADE, date atlas | [Google Fonts Abel](https://github.com/google/fonts/tree/main/ofl/abel) |

Both are distributed under the SIL Open Font License 1.1. Their license files are adjacent to the fonts. The fonts themselves are not loaded on the watch: only the resulting compact bitmap resources are packaged.

Resource suffixes are SDK tags: `~144w~color` selects Basalt, `~144w~bw` selects Aplite/Diorite/Flint, and `~200w~color` selects Emery. The SDK chooses the smallest compatible bitmap memory format automatically. Each resource is drawn at its target resolution; Pebble's bitmap API never scales it.
