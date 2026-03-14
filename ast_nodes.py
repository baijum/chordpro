"""AST node dataclasses for ChordPro documents."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SectionType(Enum):
    VERSE = "verse"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    TAB = "tab"
    GRID = "grid"
    INTRO = "intro"
    OUTRO = "outro"
    INSTRUMENTAL = "instrumental"


class CommentStyle(Enum):
    NORMAL = "normal"
    ITALIC = "italic"
    BOX = "box"


@dataclass
class ChordSegment:
    """A chord+lyric fragment. chord may be None for plain text."""
    chord: Optional[str]
    text: str


@dataclass
class LyricsLine:
    """A line of lyrics with inline chords."""
    segments: list[ChordSegment] = field(default_factory=list)


@dataclass
class Metadata:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    artist: Optional[str] = None
    composer: Optional[str] = None
    lyricist: Optional[str] = None
    album: Optional[str] = None
    year: Optional[str] = None
    key: Optional[str] = None
    tempo: Optional[str] = None
    time: Optional[str] = None
    capo: Optional[str] = None
    duration: Optional[str] = None
    extra: dict = field(default_factory=dict)


@dataclass
class Section:
    section_type: SectionType
    label: Optional[str]
    lines: list = field(default_factory=list)


@dataclass
class Comment:
    text: str
    style: CommentStyle = CommentStyle.NORMAL


@dataclass
class ChordDefinition:
    name: str
    base_fret: int = 1
    frets: list[int] = field(default_factory=list)
    fingers: list[int] = field(default_factory=list)


@dataclass
class EmptyLine:
    pass


@dataclass
class NewPage:
    pass


@dataclass
class ColumnBreak:
    pass


@dataclass
class ChorusRef:
    """Reference to repeat the last chorus."""
    pass


@dataclass
class Song:
    metadata: Metadata = field(default_factory=Metadata)
    body: list = field(default_factory=list)
    chord_definitions: list[ChordDefinition] = field(default_factory=list)
    columns: int = 1


@dataclass
class Document:
    songs: list[Song] = field(default_factory=list)
