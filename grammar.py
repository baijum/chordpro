"""PEG grammar for ChordPro line-level classification."""

from parsimonious.grammar import Grammar

CHORDPRO_GRAMMAR = Grammar(r"""
    line            = comment_line / directive_line / empty_line / lyrics_line

    comment_line    = ~r"#[^\n]*"

    directive_line  = "{" ws directive ws "}"
    directive       = directive_kv / directive_flag

    directive_kv    = directive_key ws ":" ws directive_value
    directive_flag  = directive_key

    directive_key   = ~r"[a-z_]+"
    directive_value = ~r"[^}]*"

    lyrics_line     = ~r".+"

    empty_line      = ~r"\s*$"

    ws              = ~r"\s*"
""")
