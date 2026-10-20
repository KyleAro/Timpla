"""Build Timpla's vector logo master and measured construction sheet.

The symbol is a deliberate redraw of the selected raster concept. The
wordmark is outlined from the bundled OFL-licensed Fredoka font, so the SVGs
do not depend on a font being installed on a viewer's machine.
"""

from __future__ import annotations

from math import atan2, degrees
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


HERE = Path(__file__).resolve().parent
FONT = HERE / "Fredoka-variable.ttf"
RED = "#C84B35"
CREAM = "#FFF8ED"
CHARCOAL = "#302A26"
GUIDE = "#8A8179"

# Construction coordinates in a 512 x 512 symbol grid. The visible mark is
# approximately x=92..421 and y=94..390. The bowl is one connected outline,
# with the open interior forming the horizontal and vertical strokes of T.
BOWL = (
    "M92 202 "
    "C96 183 161 172 235 172 "
    "C286 171 317 173 337 176 "
    "L325 190 "
    "C310 188 269 186 235 188 "
    "C169 189 124 196 104 208 "
    "C126 222 175 227 224 227 "
    "C235 227 241 233 241 245 "
    "L241 321 "
    "C241 338 248 346 256 346 "
    "C264 346 271 338 271 321 "
    "L271 245 "
    "C271 233 277 227 288 227 "
    "C337 227 386 222 408 208 "
    "C396 202 377 198 349 194 "
    "L359 179 "
    "C393 184 418 193 420 207 "
    "C423 277 386 338 327 361 "
    "C307 370 285 375 270 375 "
    "L242 375 "
    "C227 375 205 370 185 361 "
    "C126 338 89 277 92 202 Z"
)
BASE = (
    "M207 362 C211 374 207 376 201 379 "
    "C197 382 198 388 204 390 "
    "C226 398 286 398 308 390 "
    "C314 388 315 382 311 379 "
    "C305 376 301 374 305 362 Z"
)
SPOON = (
    "M326 191 "
    "C345 158 368 121 391 104 "
    "C404 94 421 101 421 115 "
    "C421 126 411 136 395 148 "
    "C370 169 351 188 342 199 Z"
)


def mark(color: str) -> str:
    return (
        f'<path d="{BOWL}" fill="{color}"/>'
        f'<path d="{BASE}" fill="{color}"/>'
        f'<path d="{SPOON}" fill="{color}"/>'
    )


def svg(view_box: str, content: str, title: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{view_box}" role="img" aria-label="{escape(title)}">\n'
        f'<title>{escape(title)}</title>\n{content}\n</svg>\n'
    )


def wordmark(x: float, baseline: float, scale: float) -> tuple[str, float]:
    variable_font = TTFont(FONT)
    font = instantiateVariableFont(
        variable_font, {"wdth": 100, "wght": 650}, inplace=False
    )
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()
    metrics = font["hmtx"].metrics
    parts = []
    cursor = x
    for character in "Timpla":
        glyph_name = cmap[ord(character)]
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        path = pen.getCommands()
        parts.append(
            f'<path d="{path}" fill="{CHARCOAL}" '
            f'transform="translate({cursor:.3f} {baseline:.3f}) '
            f'scale({scale:.5f} {-scale:.5f})"/>'
        )
        cursor += metrics[glyph_name][0] * scale
    return "\n".join(parts), cursor - x


def write(name: str, body: str) -> None:
    target = HERE / name
    if target.exists() and "Timpla" not in target.read_text(encoding="utf-8"):
        raise FileExistsError(f"Refusing to overwrite unrelated asset: {target}")
    target.write_text(body, encoding="utf-8")


def main() -> None:
    if not FONT.is_file():
        raise FileNotFoundError(f"Required font not found: {FONT}")

    write("timpla-mark.svg", svg("0 0 512 512", mark(RED), "Timpla bowl and spoon T mark"))

    horizontal_wordmark, horizontal_width = wordmark(410, 275, 0.205)
    horizontal = (
        f'<g transform="translate(45 0) scale(.82)">{mark(RED)}</g>\n'
        f'{horizontal_wordmark}'
    )
    write(
        "timpla-logo-horizontal.svg",
        svg("0 0 1110 390", horizontal, "Timpla horizontal logo"),
    )

    icon = (
        f'<rect width="1024" height="1024" fill="{RED}"/>\n'
        f'<g transform="translate(-64 -64) scale(2.25)">{mark(CREAM)}</g>'
    )
    write("timpla-app-icon.svg", svg("0 0 1024 1024", icon, "Timpla app icon"))

    sheet_wordmark, sheet_word_width = wordmark(322, 730, 0.16)
    angle = round(degrees(atan2(191 - 111, 404 - 335)))
    anatomy = f'''
<rect width="1200" height="900" fill="{CREAM}"/>
<g font-family="Arial,sans-serif" fill="{CHARCOAL}">
  <text x="74" y="65" font-size="29" font-weight="700">TIMPLA / LOGO CONSTRUCTION</text>
  <text x="74" y="92" font-size="15">Vector master · bowl, spoon, and T-shaped negative space</text>
</g>
<line x1="74" y1="111" x2="1126" y2="111" stroke="{GUIDE}" stroke-width="1"/>

<!-- Exact master paths, enlarged by 1.1 around origin (220,135). -->
<g transform="translate(220 135) scale(1.1)">{mark(RED)}</g>

<!-- Construction guides measured from the master coordinate grid. -->
<g fill="none" stroke="{GUIDE}" stroke-width="1.4" stroke-dasharray="6 5">
  <line x1="501.6" y1="189" x2="501.6" y2="672"/>
  <line x1="291" y1="363.8" x2="718" y2="363.8"/>
  <rect x="321.2" y="238.4" width="361.9" height="334.4"/>
  <line x1="485.1" y1="365" x2="485.1" y2="489"/>
  <line x1="518.1" y1="365" x2="518.1" y2="489"/>
</g>
<g fill="none" stroke="{CHARCOAL}" stroke-width="1.5">
  <line x1="321.2" y1="176" x2="683.1" y2="176"/>
  <path d="M321.2 168v16 M683.1 168v16"/>
  <line x1="277" y1="238.4" x2="277" y2="572.8"/>
  <path d="M269 238.4h16 M269 572.8h16"/>
  <line x1="485.1" y1="508" x2="518.1" y2="508"/>
  <path d="M485.1 500v16 M518.1 500v16"/>
  <line x1="322" y1="814" x2="{322 + sheet_word_width:.1f}" y2="814"/>
  <path d="M322 807v14 M{322 + sheet_word_width:.1f} 807v14"/>
</g>

<!-- Outlined wordmark uses Fredoka weight 650; no viewer font required. -->
{sheet_wordmark}

<g font-family="Arial,sans-serif" fill="{CHARCOAL}" font-size="17">
  <text x="501" y="164" text-anchor="middle">symbol width: 329u</text>
  <text x="257" y="438" transform="rotate(-90 257 438)" text-anchor="middle">symbol height: about 304u</text>
  <text x="322" y="840">wordmark width: {sheet_word_width:.1f} sheet units</text>
</g>

<g fill="none" stroke="{GUIDE}" stroke-width="1.5">
  <path d="M824 258 L662 317"/>
  <path d="M824 344 L635 375"/>
  <path d="M824 433 L519 466"/>
  <path d="M824 521 L659 536"/>
</g>
<g font-family="Arial,sans-serif" fill="{CHARCOAL}">
  <text x="835" y="243" font-size="20" font-weight="700">SPOON</text>
  <text x="835" y="266" font-size="15">axis ≈ {angle}° to horizontal</text>
  <text x="835" y="329" font-size="20" font-weight="700">OPEN RIM</text>
  <text x="835" y="352" font-size="15">ingredient bowl silhouette</text>
  <text x="835" y="418" font-size="20" font-weight="700">T CUTOUT</text>
  <text x="835" y="441" font-size="15">30u central stem</text>
  <text x="835" y="506" font-size="20" font-weight="700">BOWL BODY</text>
  <text x="835" y="529" font-size="15">single connected path</text>
</g>
<line x1="74" y1="859" x2="1126" y2="859" stroke="{GUIDE}" stroke-width="1"/>
<text x="74" y="883" font-family="Arial,sans-serif" font-size="14" fill="{CHARCOAL}">1u = 1 symbol-grid unit · Geometry is measured from this redrawn vector master, not the original AI raster.</text>
'''
    write("timpla-logo-anatomy.svg", svg("0 0 1200 900", anatomy, "Timpla logo anatomy and construction sheet"))

    print("Created:")
    for filename in (
        "timpla-mark.svg",
        "timpla-logo-horizontal.svg",
        "timpla-app-icon.svg",
        "timpla-logo-anatomy.svg",
    ):
        print(HERE / filename)
    print(f"Horizontal wordmark width: {horizontal_width:.1f} SVG units")


if __name__ == "__main__":
    main()
