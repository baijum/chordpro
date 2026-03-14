# ChordPro

A Python tool that converts [ChordPro](https://www.chordpro.org/) files to PDF music sheets with ukulele chord diagrams.

## Features

- Parses standard ChordPro format (`.cho`, `.chordpro`)
- Renders PDF with lyrics, inline chord names, and 4-string ukulele chord diagrams
- Supports verses, choruses, tabs, and chorus recall
- Custom chord definitions with fret and finger positions (GCEA tuning)
- Metadata directives: title, subtitle, artist, key, tempo, time, capo
- Letter and A4 page sizes

## Installation

```bash
pip install chordpro-pdf
```

Requires Python 3.8+.

## Usage

```bash
chordpro input.cho -o output.pdf
```

### Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output PDF path (defaults to `input.pdf`) |
| `--page-size` | `letter` (default) or `a4` |

## ChordPro Format

```
{title: Amazing Grace}
{key: G}

{define: G base-fret 1 frets 0 2 3 2 fingers 0 1 3 2}
{define: C base-fret 1 frets 0 0 0 3 fingers 0 0 0 3}

{start_of_chorus: Chorus}
A[G]mazing [C]grace, how [G]sweet the sound
{end_of_chorus}
```

Chords are placed inline using `[ChordName]` notation. See [`sample.cho`](chordpro/sample.cho) for a complete example.

## License

MIT
