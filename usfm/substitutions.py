# -*- coding: utf-8 -*-
# substitutions module, used by translate.py.
# An ordered list of tuples to be used for string substitutions.

#import re

subs = [
    ("''''", "'\""),
    ("'''", "'\""),
    ("''", "\""),
    ("´", "'"),
    (" <<", " «"),
    (":<<", " «"),
    (",<<", " «"),
#    (" <", ", «"),
    (">>", "»"),
#    (">", "»"),
	(" ,", ","),
	(",,", ","),
	("?.", "?"),
	(".?", "?"),
	(".!", "!"),
	("!.", "!"),
	(", \" ", ", \""),
	("? \" ", "? \""),
	("! \" ", "! \""),
	(". \" ", ". \""),
	(" .\n", ".\n"),
	(" ?\n", "?\n"),
	("? \"\n", "?\"\n"),
	("! \"\n", "!\"\n"),
	(". \"\n", ".\"\n"),
	(": \" ", ": \""),
	(": ' ", ": '"),
	(":«", ": «"),
	(":\"", ": \""),
	("« ", "«"),
	(" »", "»"),
	(" ”", "”"),
	(" ’", "’"),
	(" : \" ", ": \""),
	(": “ ", ": “"),
    (" : ‘", ": ‘"),
    (" : “", ": “"),
    (" ( ", " ("),
    (" )", ")"),
    ("\\f+", "\\f +"),
    ("+\\f", "+ \\f")
]
