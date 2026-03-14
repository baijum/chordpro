"""Static site builder: converts a directory of .cho files into HTML pages."""

import os
import re

from .html_renderer import render_song_html
from .parser import ChordProParser


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "song"


def _get_index_css() -> str:
    return """\
:root {
  --bg: #fff;
  --fg: #222;
  --link: #0000b3;
  --border-color: #ccc;
  --hover-bg: #f5f5f5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a2e;
    --fg: #e0e0e0;
    --link: #6b9bff;
    --border-color: #444;
    --hover-bg: #2a2a3e;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: Georgia, 'Times New Roman', serif;
  background: var(--bg);
  color: var(--fg);
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem 1rem;
}
h1 { font-size: 1.8rem; margin-bottom: 1.5rem; text-align: center; }
.song-list { list-style: none; }
.song-list li {
  border-bottom: 1px solid var(--border-color);
  padding: 0.6rem 0;
}
.song-list a {
  color: var(--link);
  text-decoration: none;
  font-size: 1.05rem;
}
.song-list a:hover { text-decoration: underline; }
.song-artist {
  color: var(--fg);
  opacity: 0.6;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}
"""

import html as html_module


def build_site(input_dir: str, output_dir: str, title: str = "Song Book") -> None:
    """Build a static HTML site from a directory of ChordPro files."""
    os.makedirs(output_dir, exist_ok=True)

    parser = ChordProParser()
    songs_info: list[dict] = []
    seen_slugs: set[str] = set()

    extensions = (".cho", ".chordpro")
    files = sorted(
        f for f in os.listdir(input_dir)
        if os.path.isfile(os.path.join(input_dir, f))
        and f.lower().endswith(extensions)
    )

    for filename in files:
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        document = parser.parse(text)
        for song in document.songs:
            song_title = song.metadata.title or os.path.splitext(filename)[0]
            slug = _slugify(song_title)

            # Ensure unique slugs
            base_slug = slug
            counter = 2
            while slug in seen_slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
            seen_slugs.add(slug)

            html_content = render_song_html(song)
            song_filename = f"{slug}.html"
            with open(os.path.join(output_dir, song_filename), "w", encoding="utf-8") as f:
                f.write(html_content)

            songs_info.append({
                "title": song_title,
                "artist": song.metadata.artist,
                "filename": song_filename,
            })

    # Sort alphabetically by title
    songs_info.sort(key=lambda s: s["title"].lower())

    # Generate index.html
    escaped_title = html_module.escape(title)
    index_parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escaped_title}</title>",
        "<style>",
        _get_index_css(),
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{escaped_title}</h1>",
        '<ul class="song-list">',
    ]

    for info in songs_info:
        link_title = html_module.escape(info["title"])
        href = html_module.escape(info["filename"])
        artist_span = ""
        if info["artist"]:
            artist_span = f' <span class="song-artist">— {html_module.escape(info["artist"])}</span>'
        index_parts.append(
            f'<li><a href="{href}">{link_title}</a>{artist_span}</li>'
        )

    index_parts.extend([
        "</ul>",
        "</body>",
        "</html>",
    ])

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(index_parts))

    print(f"Built {len(songs_info)} song(s) in {output_dir}/")
