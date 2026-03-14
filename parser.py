"""ChordPro parser: text -> AST Document."""

import re
from typing import Optional

from .ast_nodes import (
    ChordDefinition, ChordSegment, ChorusRef, ColumnBreak, Comment,
    CommentStyle, Document, EmptyLine, LyricsLine, Metadata, NewPage,
    Section, SectionType, Song,
)

# Directive alias mapping
ALIASES = {
    "t": "title",
    "st": "subtitle",
    "c": "comment",
    "ci": "comment_italic",
    "cb": "comment_box",
    "soc": "start_of_chorus",
    "eoc": "end_of_chorus",
    "sov": "start_of_verse",
    "eov": "end_of_verse",
    "sob": "start_of_bridge",
    "eob": "end_of_bridge",
    "sot": "start_of_tab",
    "eot": "end_of_tab",
    "sog": "start_of_grid",
    "eog": "end_of_grid",
    "soi": "start_of_intro",
    "eoi": "end_of_intro",
    "soou": "start_of_outro",
    "eoou": "end_of_outro",
    "np": "new_page",
    "colb": "column_break",
    "col": "columns",
}

SECTION_START_MAP = {
    "start_of_chorus": SectionType.CHORUS,
    "start_of_verse": SectionType.VERSE,
    "start_of_bridge": SectionType.BRIDGE,
    "start_of_tab": SectionType.TAB,
    "start_of_grid": SectionType.GRID,
    "start_of_intro": SectionType.INTRO,
    "start_of_outro": SectionType.OUTRO,
    "start_of_instrumental": SectionType.INSTRUMENTAL,
}

SECTION_END_DIRECTIVES = {
    "end_of_chorus", "end_of_verse", "end_of_bridge", "end_of_tab",
    "end_of_grid", "end_of_intro", "end_of_outro", "end_of_instrumental",
}

METADATA_FIELDS = {
    "title", "subtitle", "artist", "composer", "lyricist",
    "album", "year", "key", "tempo", "time", "capo", "duration",
}

# Regex patterns for line classification
RE_COMMENT_LINE = re.compile(r"^\s*#")
RE_DIRECTIVE = re.compile(r"^\s*\{([^}]*)\}\s*$")
RE_DIRECTIVE_PARTS = re.compile(r"^\s*([a-z_]+)\s*(?::\s*(.*?))?\s*$", re.IGNORECASE)
RE_CHORD_SPLIT = re.compile(r"\[([^\]]+)\]")
RE_EMPTY = re.compile(r"^\s*$")

# Define directive pattern for {define: ...}
RE_DEFINE_PARTS = re.compile(
    r"(\S+)\s+"
    r"(?:base-fret\s+(\d+)\s+)?"
    r"frets\s+([\dx\s]+?)"
    r"(?:\s+fingers\s+([\d\s]+))?\s*$",
    re.IGNORECASE,
)


def _parse_chord_segments(text: str) -> list[ChordSegment]:
    """Split a lyrics line into ChordSegment list using regex.

    re.split with a capture group returns alternating: text, chord, text, chord, ...
    parts[0] is text before first chord, then (chord, text) pairs follow.
    """
    parts = RE_CHORD_SPLIT.split(text)
    segments = []
    # Leading text before any chord
    if parts[0]:
        segments.append(ChordSegment(chord=None, text=parts[0]))
    # Chord/text pairs
    for i in range(1, len(parts), 2):
        chord = parts[i]
        following = parts[i + 1] if i + 1 < len(parts) else ""
        segments.append(ChordSegment(chord=chord, text=following))
    return segments if segments else [ChordSegment(chord=None, text=text)]


def _parse_define(value: str) -> Optional[ChordDefinition]:
    """Parse a {define: ...} directive value."""
    m = RE_DEFINE_PARTS.match(value.strip())
    if not m:
        return None
    name = m.group(1)
    base_fret = int(m.group(2)) if m.group(2) else 1
    frets_str = m.group(3).strip()
    frets = []
    for f in frets_str.split():
        frets.append(-1 if f.lower() == "x" else int(f))
    fingers = []
    if m.group(4):
        fingers = [int(x) for x in m.group(4).strip().split()]
    return ChordDefinition(name=name, base_fret=base_fret, frets=frets, fingers=fingers)


class ChordProParser:
    """Parse ChordPro text into a Document AST."""

    def parse(self, text: str) -> Document:
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        document = Document()
        song = Song()
        section_stack: list[Section] = []
        in_tab = False

        for raw_line in lines:
            # Comment line
            if RE_COMMENT_LINE.match(raw_line):
                continue

            # Directive line
            dm = RE_DIRECTIVE.match(raw_line)
            if dm:
                inner = dm.group(1)
                pm = RE_DIRECTIVE_PARTS.match(inner)
                if pm:
                    key = pm.group(1).lower()
                    value = (pm.group(2) or "").strip()
                    key = ALIASES.get(key, key)
                    self._handle_directive(
                        key, value, song, section_stack, document
                    )
                    # Update tab tracking
                    if key == "start_of_tab":
                        in_tab = True
                    elif key == "end_of_tab":
                        in_tab = False
                continue

            # Empty line
            if RE_EMPTY.match(raw_line):
                target = section_stack[-1].lines if section_stack else song.body
                target.append(EmptyLine())
                continue

            # Lyrics / tab line
            target = section_stack[-1].lines if section_stack else song.body
            if in_tab:
                # Tab lines are stored as plain LyricsLine with no chord parsing
                target.append(LyricsLine([ChordSegment(chord=None, text=raw_line)]))
            else:
                segments = _parse_chord_segments(raw_line)
                target.append(LyricsLine(segments))

        # Close any remaining open sections
        while section_stack:
            section = section_stack.pop()
            parent = section_stack[-1].lines if section_stack else song.body
            parent.append(section)

        document.songs.append(song)
        return document

    def _handle_directive(
        self, key: str, value: str, song: Song,
        section_stack: list[Section], document: Document
    ):
        target = section_stack[-1].lines if section_stack else song.body

        # Section start
        if key in SECTION_START_MAP:
            section = Section(
                section_type=SECTION_START_MAP[key],
                label=value or None,
            )
            section_stack.append(section)
            return

        # Section end
        if key in SECTION_END_DIRECTIVES:
            if section_stack:
                section = section_stack.pop()
                parent = section_stack[-1].lines if section_stack else song.body
                parent.append(section)
            return

        # Metadata
        if key in METADATA_FIELDS:
            setattr(song.metadata, key, value)
            return

        # Comments
        if key == "comment":
            target.append(Comment(value, CommentStyle.NORMAL))
            return
        if key == "comment_italic":
            target.append(Comment(value, CommentStyle.ITALIC))
            return
        if key == "comment_box":
            target.append(Comment(value, CommentStyle.BOX))
            return

        # Formatting
        if key == "new_page":
            target.append(NewPage())
            return
        if key == "column_break":
            target.append(ColumnBreak())
            return
        if key == "columns":
            try:
                song.columns = int(value)
            except ValueError:
                pass
            return

        # Chord definition
        if key == "define":
            defn = _parse_define(value)
            if defn:
                song.chord_definitions.append(defn)
            return

        # Chorus recall
        if key == "chorus":
            target.append(ChorusRef())
            return

        # New song
        if key == "new_song" or key == "ns":
            document.songs.append(song)
            return

        # Unknown directives stored in metadata.extra
        song.metadata.extra[key] = value
