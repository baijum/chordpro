"""Guitar chord diagram drawing using ReportLab."""

from reportlab.lib.colors import black, white, HexColor
from reportlab.lib.units import mm

from .ast_nodes import ChordDefinition


# Diagram dimensions
NUM_STRINGS = 4
NUM_FRETS = 4
STRING_SPACING = 5 * mm
FRET_SPACING = 5 * mm
DIAGRAM_WIDTH = (NUM_STRINGS - 1) * STRING_SPACING
DIAGRAM_HEIGHT = NUM_FRETS * FRET_SPACING
DOT_RADIUS = 1.5 * mm
OPEN_RADIUS = 1.3 * mm
NUT_THICKNESS = 2.5
LABEL_FONT_SIZE = 8
NAME_FONT_SIZE = 10
FINGER_FONT_SIZE = 6
TOTAL_WIDTH = DIAGRAM_WIDTH + 10 * mm  # padding
TOTAL_HEIGHT = DIAGRAM_HEIGHT + 20 * mm  # name + open/muted markers

# Colors
FRET_COLOR = HexColor("#444444")
STRING_COLOR = HexColor("#333333")
DOT_COLOR = HexColor("#2F5233")


def draw_chord_diagram(canvas, chord_def: ChordDefinition, x: float, y: float):
    """Draw a chord diagram at position (x, y) where y is top of diagram area."""
    c = canvas
    name = chord_def.name
    base_fret = chord_def.base_fret
    frets = chord_def.frets
    fingers = chord_def.fingers

    # Starting positions
    grid_left = x + 5 * mm
    grid_top = y - 15 * mm  # leave room for name and open/mute markers

    # Draw chord name centered above
    c.setFont("Helvetica-Bold", NAME_FONT_SIZE)
    name_x = grid_left + DIAGRAM_WIDTH / 2
    c.drawCentredString(name_x, y - 5 * mm, name)

    # Draw nut or fret number
    nut_y = grid_top
    is_open_position = (base_fret <= 1)

    if is_open_position:
        c.setStrokeColor(STRING_COLOR)
        c.setLineWidth(NUT_THICKNESS)
        c.line(grid_left, nut_y, grid_left + DIAGRAM_WIDTH, nut_y)
        c.setLineWidth(0.5)
    else:
        c.setStrokeColor(FRET_COLOR)
        c.setLineWidth(0.8)
        c.line(grid_left, nut_y, grid_left + DIAGRAM_WIDTH, nut_y)
        c.setLineWidth(0.5)
        # Draw fret number label to the left
        c.setFont("Helvetica-Bold", LABEL_FONT_SIZE)
        c.setFillColor(black)
        c.drawString(grid_left - 5 * mm, nut_y - FRET_SPACING + 1 * mm, f"{base_fret}fr")

    # Draw fret lines
    c.setStrokeColor(FRET_COLOR)
    c.setLineWidth(0.7)
    for i in range(1, NUM_FRETS + 1):
        fret_y = nut_y - i * FRET_SPACING
        c.line(grid_left, fret_y, grid_left + DIAGRAM_WIDTH, fret_y)

    # Draw string lines
    c.setStrokeColor(STRING_COLOR)
    c.setLineWidth(0.8)
    for i in range(NUM_STRINGS):
        sx = grid_left + i * STRING_SPACING
        c.line(sx, nut_y, sx, nut_y - DIAGRAM_HEIGHT)

    # Draw finger positions, X and O markers
    marker_y = nut_y + 3 * mm

    for i, fret_num in enumerate(frets[:NUM_STRINGS]):
        sx = grid_left + i * STRING_SPACING

        if fret_num < 0:
            # Muted string - draw X as crossed lines
            x_size = 1.2 * mm
            c.setStrokeColor(black)
            c.setLineWidth(1.2)
            c.line(sx - x_size, marker_y - x_size, sx + x_size, marker_y + x_size)
            c.line(sx - x_size, marker_y + x_size, sx + x_size, marker_y - x_size)
        elif fret_num == 0:
            # Open string - draw open circle
            c.setStrokeColor(black)
            c.setLineWidth(1.0)
            c.setFillColor(white)
            c.circle(sx, marker_y, OPEN_RADIUS, fill=1, stroke=1)
        else:
            # Filled dot at fret position
            if is_open_position:
                display_fret = fret_num
            else:
                display_fret = fret_num - base_fret + 1

            # Clamp to visible range
            if display_fret < 1:
                display_fret = 1
            if display_fret > NUM_FRETS:
                display_fret = NUM_FRETS

            dot_y = nut_y - (display_fret - 0.5) * FRET_SPACING
            c.setFillColor(DOT_COLOR)
            c.circle(sx, dot_y, DOT_RADIUS, fill=1, stroke=0)

            # Draw finger number inside the dot
            if fingers and i < len(fingers) and fingers[i] > 0:
                c.setFillColor(white)
                c.setFont("Helvetica-Bold", FINGER_FONT_SIZE)
                c.drawCentredString(sx, dot_y - FINGER_FONT_SIZE / 3, str(fingers[i]))

    # Reset fill color
    c.setFillColor(black)
    c.setStrokeColor(black)


def get_diagram_size():
    """Return (width, height) of a single chord diagram."""
    return TOTAL_WIDTH, TOTAL_HEIGHT
