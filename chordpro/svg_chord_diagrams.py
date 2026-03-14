"""SVG chord diagram rendering for HTML output."""

import html

from .ast_nodes import ChordDefinition

# Diagram dimensions (in pixels)
NUM_STRINGS = 4
NUM_FRETS = 4
STRING_SPACING = 20
FRET_SPACING = 20
DIAGRAM_WIDTH = (NUM_STRINGS - 1) * STRING_SPACING
DIAGRAM_HEIGHT = NUM_FRETS * FRET_SPACING
DOT_RADIUS = 6
OPEN_RADIUS = 5
NUT_THICKNESS = 3

# Layout offsets
LEFT_PAD = 20
TOP_PAD = 30  # room for chord name
MARKER_SPACE = 12  # room for X/O markers above nut
BOTTOM_PAD = 5

SVG_WIDTH = DIAGRAM_WIDTH + 2 * LEFT_PAD
SVG_HEIGHT = TOP_PAD + MARKER_SPACE + DIAGRAM_HEIGHT + BOTTOM_PAD

# Colors
DOT_COLOR = "#2F5233"
FRET_COLOR = "#444444"
STRING_COLOR = "#333333"


def render_chord_diagram_svg(chord_def: ChordDefinition) -> str:
    """Render a single chord diagram as an inline SVG element."""
    name = html.escape(chord_def.name)
    base_fret = chord_def.base_fret
    frets = chord_def.frets
    fingers = chord_def.fingers

    parts: list[str] = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{SVG_WIDTH}" height="{SVG_HEIGHT}" '
        f'class="chord-diagram" role="img" aria-label="Chord diagram for {name}">'
    )

    grid_left = LEFT_PAD
    grid_top = TOP_PAD + MARKER_SPACE

    # Chord name
    name_x = grid_left + DIAGRAM_WIDTH / 2
    parts.append(
        f'<text x="{name_x}" y="{TOP_PAD - 5}" '
        f'text-anchor="middle" font-weight="bold" font-size="12" '
        f'font-family="sans-serif">{name}</text>'
    )

    is_open = base_fret <= 1

    # Nut or top fret line
    if is_open:
        parts.append(
            f'<line x1="{grid_left}" y1="{grid_top}" '
            f'x2="{grid_left + DIAGRAM_WIDTH}" y2="{grid_top}" '
            f'stroke="{STRING_COLOR}" stroke-width="{NUT_THICKNESS}"/>'
        )
    else:
        parts.append(
            f'<line x1="{grid_left}" y1="{grid_top}" '
            f'x2="{grid_left + DIAGRAM_WIDTH}" y2="{grid_top}" '
            f'stroke="{FRET_COLOR}" stroke-width="1"/>'
        )
        # Fret number label
        parts.append(
            f'<text x="{grid_left - 5}" y="{grid_top + FRET_SPACING - 3}" '
            f'text-anchor="end" font-size="9" font-weight="bold" '
            f'font-family="sans-serif">{base_fret}fr</text>'
        )

    # Fret lines
    for i in range(1, NUM_FRETS + 1):
        fy = grid_top + i * FRET_SPACING
        parts.append(
            f'<line x1="{grid_left}" y1="{fy}" '
            f'x2="{grid_left + DIAGRAM_WIDTH}" y2="{fy}" '
            f'stroke="{FRET_COLOR}" stroke-width="0.7"/>'
        )

    # String lines
    for i in range(NUM_STRINGS):
        sx = grid_left + i * STRING_SPACING
        parts.append(
            f'<line x1="{sx}" y1="{grid_top}" '
            f'x2="{sx}" y2="{grid_top + DIAGRAM_HEIGHT}" '
            f'stroke="{STRING_COLOR}" stroke-width="0.8"/>'
        )

    # Dots, X/O markers
    marker_y = grid_top - 7

    for i, fret_num in enumerate(frets[:NUM_STRINGS]):
        sx = grid_left + i * STRING_SPACING

        if fret_num < 0:
            # Muted string — X
            sz = 4
            parts.append(
                f'<line x1="{sx - sz}" y1="{marker_y - sz}" '
                f'x2="{sx + sz}" y2="{marker_y + sz}" '
                f'stroke="black" stroke-width="1.5"/>'
            )
            parts.append(
                f'<line x1="{sx - sz}" y1="{marker_y + sz}" '
                f'x2="{sx + sz}" y2="{marker_y - sz}" '
                f'stroke="black" stroke-width="1.5"/>'
            )
        elif fret_num == 0:
            # Open string — O
            parts.append(
                f'<circle cx="{sx}" cy="{marker_y}" r="{OPEN_RADIUS}" '
                f'fill="none" stroke="black" stroke-width="1.2"/>'
            )
        else:
            # Finger dot
            if is_open:
                display_fret = fret_num
            else:
                display_fret = fret_num - base_fret + 1
            display_fret = max(1, min(display_fret, NUM_FRETS))

            dot_y = grid_top + (display_fret - 0.5) * FRET_SPACING
            parts.append(
                f'<circle cx="{sx}" cy="{dot_y}" r="{DOT_RADIUS}" '
                f'fill="{DOT_COLOR}"/>'
            )

            # Finger number
            if fingers and i < len(fingers) and fingers[i] > 0:
                parts.append(
                    f'<text x="{sx}" y="{dot_y + 3.5}" '
                    f'text-anchor="middle" fill="white" '
                    f'font-size="8" font-weight="bold" '
                    f'font-family="sans-serif">{fingers[i]}</text>'
                )

    parts.append("</svg>")
    return "\n".join(parts)
