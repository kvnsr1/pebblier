# Artwork sources

The dial is reconstructed by `scripts/generate_assets.py` using original Roman numeral polygons and railway geometry. The supplied image is a visual reference only and is not embedded in the application. The generator is the editable source for every committed PNG.

Fonts are bundled so regeneration does not depend on locally installed fonts or network access:

| File | Use | Upstream |
| --- | --- | --- |
| `fonts/Tinos-Bold.ttf` | PEBBLIER and tiny diagonal signature | [Tinos](https://github.com/googlefonts/tinos), retrieved from [Google Fonts](https://github.com/google/fonts/tree/main/ofl/tinos) |
| `fonts/Abel-Regular.ttf` | Date atlas | [Google Fonts Abel](https://github.com/google/fonts/tree/main/ofl/abel) |

Both are distributed under the SIL Open Font License 1.1. Their license files are adjacent to the fonts. The fonts themselves are not loaded on the watch: only the resulting compact bitmap resources are packaged.

AUTOMATIC and SWISS / MADE use original 3 × 5 pixel glyphs at 144 pixels wide and 5 × 7 pixel glyphs on Emery. The generator defines these patterns directly. The main wordmark occupies 46 × 6 pixels or 64 × 8 pixels, retaining a finer serif style and ample surrounding white space.

Resource suffixes are SDK tags: `~144w~color` selects Basalt, `~144w~bw` selects Aplite/Diorite/Flint, and `~200w~color` selects Emery. The SDK chooses the smallest compatible bitmap memory format automatically. Each resource is drawn at its target resolution; Pebble's bitmap API never scales it.

`scripts/check_assets.py` regenerates and compares decoded RGB pixels and dimensions exactly. PNG/zlib encoders can produce different compressed bytes on macOS and Linux even when their pixels are identical; the CI check therefore validates artwork rather than compression output.
