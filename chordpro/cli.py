"""Command-line interface for ChordPro to PDF converter."""

import argparse
import sys

from .parser import ChordProParser
from .renderer import render_pdf


def main():
    parser = argparse.ArgumentParser(
        prog="chordpro",
        description="Convert ChordPro files to PDF music sheets.",
    )
    parser.add_argument("input", help="Input ChordPro file (.cho, .chordpro)")
    parser.add_argument("-o", "--output", default=None, help="Output PDF file path")
    parser.add_argument(
        "--page-size", choices=["letter", "a4"], default="a4",
        help="Page size (default: a4)",
    )

    args = parser.parse_args()

    if args.output is None:
        # Derive output name from input
        base = args.input.rsplit(".", 1)[0]
        args.output = base + ".pdf"

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    cp_parser = ChordProParser()
    document = cp_parser.parse(text)
    render_pdf(document, args.output, page_size=args.page_size)
    print(f"PDF written to {args.output}")


if __name__ == "__main__":
    main()
