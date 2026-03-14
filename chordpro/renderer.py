"""PDF renderer for ChordPro AST using ReportLab Canvas."""

from reportlab.lib.colors import Color, black, gray, blue
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.pdfgen.canvas import Canvas

from .ast_nodes import (
    ChorusRef, ColumnBreak, Comment, CommentStyle, Document, EmptyLine,
    LyricsLine, Metadata, NewPage, Section, SectionType, Song,
)
from .chord_diagrams import draw_chord_diagram, get_diagram_size

PAGE_SIZES = {"letter": letter, "a4": A4}

# Layout constants
MARGIN_TOP = 0.75 * inch
MARGIN_BOTTOM = 0.75 * inch
MARGIN_LEFT = 0.75 * inch
MARGIN_RIGHT = 0.75 * inch
CHORD_FONT_SIZE = 10
LYRIC_FONT_SIZE = 12
LINE_SPACING = 4  # extra space between lines
SECTION_SPACING = 10
CHORUS_INDENT = 15
CHORD_COLOR = Color(0, 0, 0.7)


def render_pdf(document: Document, output_path: str, page_size: str = "letter"):
    """Render a Document AST to a PDF file."""
    ps = PAGE_SIZES.get(page_size.lower(), letter)
    page_width, page_height = ps

    c = Canvas(output_path, pagesize=ps)
    content_width = page_width - MARGIN_LEFT - MARGIN_RIGHT

    for song in document.songs:
        renderer = _SongRenderer(c, page_width, page_height, content_width, song)
        renderer.render()

    c.save()


class _SongRenderer:
    def __init__(self, canvas: Canvas, page_width, page_height, content_width, song: Song):
        self.c = canvas
        self.page_width = page_width
        self.page_height = page_height
        self.content_width = content_width
        self.song = song
        self.y = page_height - MARGIN_TOP
        self.x_left = MARGIN_LEFT
        self.last_chorus: Section | None = None

    def render(self):
        self._draw_metadata()
        self._draw_body(self.song.body)
        self._draw_chord_diagrams()
        self.c.showPage()

    def _new_page(self):
        self.c.showPage()
        self.y = self.page_height - MARGIN_TOP

    def _check_space(self, needed: float):
        if self.y - needed < MARGIN_BOTTOM:
            self._new_page()

    def _draw_metadata(self):
        meta = self.song.metadata
        if meta.title:
            self._check_space(30)
            self.c.setFont("Helvetica-Bold", 18)
            self.c.drawCentredString(self.page_width / 2, self.y, meta.title)
            self.y -= 22

        if meta.subtitle:
            self._check_space(20)
            self.c.setFont("Helvetica-Oblique", 14)
            self.c.drawCentredString(self.page_width / 2, self.y, meta.subtitle)
            self.y -= 18

        # Info line: key, capo, tempo, time
        info_parts = []
        if meta.key:
            info_parts.append(f"Key: {meta.key}")
        if meta.capo:
            info_parts.append(f"Capo: {meta.capo}")
        if meta.tempo:
            info_parts.append(f"Tempo: {meta.tempo}")
        if meta.time:
            info_parts.append(f"Time: {meta.time}")
        if meta.artist:
            info_parts.append(f"Artist: {meta.artist}")
        if meta.composer:
            info_parts.append(f"Composer: {meta.composer}")

        if info_parts:
            self._check_space(16)
            self.c.setFont("Helvetica", 10)
            info_text = "  |  ".join(info_parts)
            self.c.drawCentredString(self.page_width / 2, self.y, info_text)
            self.y -= 14

        if meta.title or meta.subtitle or info_parts:
            self.y -= 10  # extra space after header

    def _draw_body(self, items: list, indent: float = 0):
        for item in items:
            if isinstance(item, Section):
                self._draw_section(item)
            elif isinstance(item, LyricsLine):
                self._draw_lyrics_line(item, indent)
            elif isinstance(item, Comment):
                self._draw_comment(item, indent)
            elif isinstance(item, EmptyLine):
                self.y -= LYRIC_FONT_SIZE + LINE_SPACING
            elif isinstance(item, NewPage):
                self._new_page()
            elif isinstance(item, ChorusRef):
                self._draw_chorus_ref()

    def _draw_section(self, section: Section):
        # Store chorus for recall
        if section.section_type == SectionType.CHORUS:
            self.last_chorus = section

        self.y -= SECTION_SPACING

        # Section label
        label = section.label or section.section_type.value.title()
        self._check_space(LYRIC_FONT_SIZE + CHORD_FONT_SIZE + LINE_SPACING + 20)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.setFillColor(black)
        self.c.drawString(self.x_left, self.y, f"[{label}]")
        self.y -= 15

        # Draw section content
        indent = CHORUS_INDENT if section.section_type == SectionType.CHORUS else 0

        if section.section_type == SectionType.TAB:
            self._draw_tab_lines(section.lines)
        else:
            self._draw_body(section.lines, indent)

        self.y -= SECTION_SPACING / 2

    def _draw_lyrics_line(self, line: LyricsLine, indent: float = 0):
        has_chords = any(seg.chord for seg in line.segments)
        line_height = LYRIC_FONT_SIZE + LINE_SPACING
        if has_chords:
            line_height += CHORD_FONT_SIZE + LYRIC_FONT_SIZE

        self._check_space(line_height)

        x = self.x_left + indent

        if has_chords:
            # Draw chords well above lyrics — need full lyric ascent clearance
            chord_y = self.y
            lyric_y = self.y - CHORD_FONT_SIZE - LYRIC_FONT_SIZE + 2
            cx = x
            for seg in line.segments:
                chord_width = 0
                text_width = 0
                if seg.chord:
                    self.c.setFont("Helvetica-Bold", CHORD_FONT_SIZE)
                    self.c.setFillColor(CHORD_COLOR)
                    self.c.drawString(cx, chord_y, seg.chord)
                    chord_width = self.c.stringWidth(seg.chord, "Helvetica-Bold", CHORD_FONT_SIZE)
                    chord_width += 3  # min gap after chord name
                if seg.text:
                    self.c.setFont("Helvetica", LYRIC_FONT_SIZE)
                    self.c.setFillColor(black)
                    self.c.drawString(cx, lyric_y, seg.text)
                    text_width = self.c.stringWidth(seg.text, "Helvetica", LYRIC_FONT_SIZE)
                cx += max(chord_width, text_width)

            self.y = lyric_y - LYRIC_FONT_SIZE - 2
        else:
            # Lyrics only
            full_text = "".join(seg.text for seg in line.segments)
            self.c.setFont("Helvetica", LYRIC_FONT_SIZE)
            self.c.setFillColor(black)
            self.c.drawString(x, self.y, full_text)
            self.y -= LYRIC_FONT_SIZE + LINE_SPACING

    def _draw_tab_lines(self, lines: list):
        for item in lines:
            if isinstance(item, EmptyLine):
                self.y -= 10
                continue
            if isinstance(item, LyricsLine):
                text = "".join(seg.text for seg in item.segments)
                self._check_space(12)
                self.c.setFont("Courier", 10)
                self.c.setFillColor(black)
                self.c.drawString(self.x_left, self.y, text)
                self.y -= 12

    def _draw_comment(self, comment: Comment, indent: float = 0):
        self._check_space(14)
        x = self.x_left + indent

        if comment.style == CommentStyle.ITALIC:
            self.c.setFont("Helvetica-Oblique", 10)
            self.c.setFillColor(gray)
            self.c.drawString(x, self.y, comment.text)
        elif comment.style == CommentStyle.BOX:
            self.c.setFont("Helvetica", 10)
            text_width = self.c.stringWidth(comment.text, "Helvetica", 10)
            self.c.setStrokeColor(gray)
            self.c.setFillColor(gray)
            self.c.rect(x - 2, self.y - 3, text_width + 4, 14, fill=0, stroke=1)
            self.c.setFillColor(black)
            self.c.drawString(x, self.y, comment.text)
        else:
            self.c.setFont("Helvetica-Oblique", 10)
            self.c.setFillColor(gray)
            self.c.drawString(x, self.y, comment.text)

        self.c.setFillColor(black)
        self.y -= 14

    def _draw_chorus_ref(self):
        if self.last_chorus:
            self._draw_section(self.last_chorus)
        else:
            self._check_space(14)
            self.c.setFont("Helvetica-Oblique", 10)
            self.c.setFillColor(gray)
            self.c.drawString(self.x_left, self.y, "[Chorus]")
            self.c.setFillColor(black)
            self.y -= 14

    def _draw_chord_diagrams(self):
        if not self.song.chord_definitions:
            return

        diag_w, diag_h = get_diagram_size()
        per_row = int(self.content_width // diag_w)
        if per_row < 1:
            per_row = 1

        self.y -= 15
        self._check_space(diag_h + 20)

        # Label
        self.c.setFont("Helvetica-Bold", 11)
        self.c.setFillColor(black)
        self.c.drawString(self.x_left, self.y, "Chord Definitions")
        self.y -= 5

        x = self.x_left
        col = 0
        for chord_def in self.song.chord_definitions:
            self._check_space(diag_h)
            draw_chord_diagram(self.c, chord_def, x, self.y)
            col += 1
            if col >= per_row:
                col = 0
                x = self.x_left
                self.y -= diag_h
            else:
                x += diag_w

        if col > 0:
            self.y -= diag_h
