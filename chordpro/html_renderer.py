"""HTML+CSS renderer for ChordPro AST."""

import html

from .ast_nodes import (
    ChorusRef, Comment, CommentStyle, EmptyLine, LyricsLine,
    Metadata, NewPage, Section, SectionType, Song,
)
from .svg_chord_diagrams import render_chord_diagram_svg


def render_song_html(song: Song) -> str:
    """Render a Song AST to a standalone HTML page."""
    renderer = _HtmlSongRenderer(song)
    return renderer.render()


def _get_default_css() -> str:
    return """\
:root {
  --chord-color: #0000b3;
  --bg: #fff;
  --fg: #222;
  --section-label: #555;
  --comment-color: #666;
  --border-color: #ccc;
}
@media (prefers-color-scheme: dark) {
  :root {
    --chord-color: #6b9bff;
    --bg: #1a1a2e;
    --fg: #e0e0e0;
    --section-label: #aaa;
    --comment-color: #999;
    --border-color: #444;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  background: var(--bg);
  color: var(--fg);
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
  line-height: 1.4;
}
.song-header { text-align: center; margin-bottom: 1.5rem; }
.song-title { font-size: 1.6rem; margin-bottom: 0.25rem; }
.song-subtitle { font-size: 1.1rem; font-style: italic; margin-bottom: 0.25rem; }
.song-meta { font-size: 0.85rem; color: var(--section-label); }
.section { margin-bottom: 1rem; }
.section-label {
  font-weight: bold;
  font-size: 0.9rem;
  color: var(--section-label);
  margin-bottom: 0.25rem;
}
.chorus { padding-left: 1.5rem; }
.lyrics-line { display: flex; flex-wrap: wrap; margin-bottom: 0.15rem; }
.chord-segment { display: inline-flex; flex-direction: column; }
.chord {
  font-family: 'Helvetica Neue', Arial, sans-serif;
  font-weight: bold;
  font-size: 0.85rem;
  color: var(--chord-color);
  min-height: 1.1rem;
  white-space: pre;
}
.lyric {
  font-size: 1rem;
  white-space: pre;
}
.empty-line { height: 0.75rem; }
.tab-block {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  white-space: pre;
  line-height: 1.3;
  margin-bottom: 0.15rem;
}
.comment {
  font-style: italic;
  color: var(--comment-color);
  font-size: 0.9rem;
  margin-bottom: 0.15rem;
}
.comment-box {
  display: inline-block;
  border: 1px solid var(--border-color);
  padding: 0.1rem 0.4rem;
  font-size: 0.9rem;
  margin-bottom: 0.15rem;
}
.chord-diagrams {
  margin-top: 2rem;
  border-top: 1px solid var(--border-color);
  padding-top: 1rem;
}
.chord-diagrams h3 { font-size: 1rem; margin-bottom: 0.5rem; }
.diagram-row { display: flex; flex-wrap: wrap; gap: 0.5rem; }
"""


class _HtmlSongRenderer:
    def __init__(self, song: Song):
        self.song = song
        self.last_chorus: Section | None = None
        self.parts: list[str] = []

    def render(self) -> str:
        meta = self.song.metadata
        title = html.escape(meta.title or "Untitled")

        self.parts.append("<!DOCTYPE html>")
        self.parts.append('<html lang="en">')
        self.parts.append("<head>")
        self.parts.append('<meta charset="utf-8">')
        self.parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
        self.parts.append(f"<title>{title}</title>")
        self.parts.append("<style>")
        self.parts.append(_get_default_css())
        self.parts.append("</style>")
        self.parts.append("</head>")
        self.parts.append("<body>")

        self._render_metadata(meta)
        self._render_body(self.song.body)
        self._render_chord_diagrams()

        self.parts.append("</body>")
        self.parts.append("</html>")
        return "\n".join(self.parts)

    def _render_metadata(self, meta: Metadata):
        self.parts.append('<div class="song-header">')
        if meta.title:
            self.parts.append(f'<h1 class="song-title">{html.escape(meta.title)}</h1>')
        if meta.subtitle:
            self.parts.append(f'<p class="song-subtitle">{html.escape(meta.subtitle)}</p>')

        info_parts = []
        if meta.key:
            info_parts.append(f"Key: {html.escape(meta.key)}")
        if meta.capo:
            info_parts.append(f"Capo: {html.escape(meta.capo)}")
        if meta.tempo:
            info_parts.append(f"Tempo: {html.escape(meta.tempo)}")
        if meta.time:
            info_parts.append(f"Time: {html.escape(meta.time)}")
        if meta.artist:
            info_parts.append(f"Artist: {html.escape(meta.artist)}")
        if meta.composer:
            info_parts.append(f"Composer: {html.escape(meta.composer)}")

        if info_parts:
            self.parts.append(f'<p class="song-meta">{" | ".join(info_parts)}</p>')
        self.parts.append("</div>")

    def _render_body(self, items: list, in_chorus: bool = False):
        for item in items:
            if isinstance(item, Section):
                self._render_section(item)
            elif isinstance(item, LyricsLine):
                self._render_lyrics_line(item)
            elif isinstance(item, Comment):
                self._render_comment(item)
            elif isinstance(item, EmptyLine):
                self.parts.append('<div class="empty-line"></div>')
            elif isinstance(item, ChorusRef):
                self._render_chorus_ref()

    def _render_section(self, section: Section):
        if section.section_type == SectionType.CHORUS:
            self.last_chorus = section

        label = html.escape(section.label or section.section_type.value.title())
        is_chorus = section.section_type == SectionType.CHORUS

        css_class = "section chorus" if is_chorus else "section"
        self.parts.append(f'<div class="{css_class}">')
        self.parts.append(f'<div class="section-label">[{label}]</div>')

        if section.section_type == SectionType.TAB:
            self._render_tab_lines(section.lines)
        else:
            self._render_body(section.lines, in_chorus=is_chorus)

        self.parts.append("</div>")

    def _render_lyrics_line(self, line: LyricsLine):
        has_chords = any(seg.chord for seg in line.segments)

        self.parts.append('<div class="lyrics-line">')
        for seg in line.segments:
            chord_html = html.escape(seg.chord) if seg.chord else ""
            text_html = html.escape(seg.text) if seg.text else ""

            if has_chords:
                chord_display = chord_html if chord_html else "&nbsp;"
                self.parts.append(
                    f'<span class="chord-segment">'
                    f'<span class="chord">{chord_display}</span>'
                    f'<span class="lyric">{text_html}</span>'
                    f'</span>'
                )
            else:
                self.parts.append(f'<span class="lyric">{text_html}</span>')
        self.parts.append("</div>")

    def _render_tab_lines(self, lines: list):
        for item in lines:
            if isinstance(item, EmptyLine):
                self.parts.append('<div class="empty-line"></div>')
            elif isinstance(item, LyricsLine):
                text = "".join(seg.text for seg in item.segments)
                self.parts.append(f'<div class="tab-block">{html.escape(text)}</div>')

    def _render_comment(self, comment: Comment):
        escaped = html.escape(comment.text)
        if comment.style == CommentStyle.BOX:
            self.parts.append(f'<div class="comment-box">{escaped}</div>')
        else:
            self.parts.append(f'<div class="comment">{escaped}</div>')

    def _render_chorus_ref(self):
        if self.last_chorus:
            self._render_section(self.last_chorus)
        else:
            self.parts.append('<div class="comment">[Chorus]</div>')

    def _render_chord_diagrams(self):
        if not self.song.chord_definitions:
            return
        self.parts.append('<div class="chord-diagrams">')
        self.parts.append("<h3>Chord Definitions</h3>")
        self.parts.append('<div class="diagram-row">')
        for chord_def in self.song.chord_definitions:
            self.parts.append(render_chord_diagram_svg(chord_def))
        self.parts.append("</div>")
        self.parts.append("</div>")
