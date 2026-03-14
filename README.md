# ChordPro

A Python tool that converts [ChordPro](https://www.chordpro.org/) files to PDF or HTML music sheets with ukulele chord diagrams. Build a static song book site and deploy it to GitHub Pages.

## Features

- Parses standard ChordPro format (`.cho`, `.chordpro`)
- Renders PDF with lyrics, inline chord names, and 4-string ukulele chord diagrams
- Renders responsive HTML+CSS with inline SVG chord diagrams and dark mode support
- Builds a static site from a directory of songs with an index page
- Deploys to GitHub Pages via included workflow
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

### Convert to PDF (default)

```bash
chordpro input.cho -o output.pdf
```

### Convert to HTML

```bash
chordpro input.cho --format html -o output.html
```

### Build a static site

```bash
chordpro build-site songs/ -o _site/ --title "My Song Book"
```

This scans the directory for `.cho`/`.chordpro` files, generates an HTML page per song, and creates an `index.html` listing all songs alphabetically.

### Options

| Flag | Description |
|------|-------------|
| `-o`, `--output` | Output file or directory path |
| `--format` | `pdf` (default) or `html` |
| `--page-size` | `a4` (default) or `letter` (PDF only) |
| `--title` | Site title for `build-site` (default: "Song Book") |

## GitHub Pages Deployment

The included `.github/workflows/deploy-pages.yml` workflow automatically builds and deploys your songs to GitHub Pages on every push to `main`. Place your `.cho` files in a `songs/` directory and enable GitHub Pages (Settings > Pages > Source: GitHub Actions).

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
