# Dial reconstruction

The reference's hierarchy is preserved: XI / XII / I above a square railway, oversized radial side numerals, PEBBLIER above the pivot, AUTOMATIC below, and a date replacing VI. The right side uses watchmaker's IIII. Full-screen white art runs to the display edges without an artificial bezel.

The taller display is accommodated through numeral placement and vertical spacing, rather than stretching the supplied picture. The railway remains square. The top and bottom numeral bands are taller than in a square crop, and side numerals approach the edges. Roman glyphs are deliberately shaped/sheared for their positions and are independent of the wordmark font.

| Geometry | 144 × 168 | 200 × 228 |
| --- | --- | --- |
| Pivot | (72, 79) | (100, 107) |
| Outer railway | (24, 31) to (120, 127) | (33, 40) to (167, 174) |
| Inner railway | (28, 35) to (116, 123) | (39, 46) to (161, 168) |
| Date outer frame | (63, 133), 18 × 28 | (87.5, 180.5), 25 × 38 |
| Hour length | 45 px | 63 px |
| Minute / seconds length | 63 px | 88 px |

Sixty rays intersect both nested squares to create the diagonal minute marks. Every fifth mark is heavier. Rounded masks clip the ticks to the railway band and clean one-pixel outlines define the rails. Drawings are supersampled at 8× then separately quantized to four grayscale levels or 1-bit black/white. Small lettering receives optical stroke compensation before reduction.

The hands use fixed-point native paths with blue shaded facets on color displays. On monochrome displays black swords have thin white bevels so overlapping shapes can be distinguished. A thin seconds hand and a wider opposite counterweight reproduce the unusual rear weight in the supplied reference. The lower pivot ring, upper blue cap, and light pin are drawn independently.

At axial hand positions the long minute hand crosses the railway toward the outer numerals, as it does in the reference. At 12:00 the hands necessarily overlap. The miniature signature and bottom lettering have fewer available pixels than the source and are more legible on Emery. These are intentional native-resolution compromises, not scaled photographic detail.

No external library is needed at runtime. fctx was evaluated; native paths avoid its 24,192-byte Basalt color scratch buffer (45,600 bytes on Emery) while the expensive typography is already cached in a compact bitmap.
