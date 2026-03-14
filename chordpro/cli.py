"""Command-line interface for ChordPro to PDF/HTML converter."""

import argparse
import sys

from .parser import ChordProParser
from .renderer import render_pdf
from .html_renderer import render_song_html
from .site_builder import build_site

SUBCOMMANDS = {"build-site"}


def _build_convert_parser():
    parser = argparse.ArgumentParser(
        prog="chordpro",
        description="Convert ChordPro files to PDF or HTML music sheets.",
    )
    parser.add_argument("input", help="Input ChordPro file (.cho, .chordpro)")
    parser.add_argument("-o", "--output", default=None, help="Output file path")
    parser.add_argument(
        "--format", choices=["pdf", "html"], default="pdf",
        help="Output format (default: pdf)",
    )
    parser.add_argument(
        "--page-size", choices=["letter", "a4"], default="a4",
        help="Page size for PDF output (default: a4)",
    )
    return parser


def _build_site_parser():
    parser = argparse.ArgumentParser(
        prog="chordpro build-site",
        description="Build a static HTML site from a directory of ChordPro files.",
    )
    parser.add_argument("input_dir", help="Directory containing .cho/.chordpro files")
    parser.add_argument("-o", "--output", default="_site", help="Output directory (default: _site)")
    parser.add_argument("--title", default="Song Book", help="Site title (default: Song Book)")
    return parser


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "build-site":
        parser = _build_site_parser()
        args = parser.parse_args(sys.argv[2:])
        build_site(args.input_dir, args.output, title=args.title)
        return

    parser = _build_convert_parser()
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    cp_parser = ChordProParser()
    document = cp_parser.parse(text)

    if args.format == "html":
        if args.output is None:
            args.output = args.input.rsplit(".", 1)[0] + ".html"
        html_parts = [render_song_html(song) for song in document.songs]
        with open(args.output, "w", encoding="utf-8") as f:
            f.write("\n".join(html_parts))
        print(f"HTML written to {args.output}")
    else:
        if args.output is None:
            args.output = args.input.rsplit(".", 1)[0] + ".pdf"
        render_pdf(document, args.output, page_size=args.page_size)
        print(f"PDF written to {args.output}")


if __name__ == "__main__":
    main()
