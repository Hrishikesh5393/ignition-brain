#!/usr/bin/env python3
"""Fail if a `references/…`, `schema/…` or `scripts/…` path cited in the skill or the
sibling skills (../skills/*) does not exist. Placeholders (<x>, *, …) are skipped.
    python3 skill/scripts/check_links.py
"""
import glob, os, re, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PATH = re.compile(r"`((?:references|schema|scripts)/[A-Za-z0-9_./-]+)`")
bad = 0
docs = glob.glob(ROOT + "/**/*.md", recursive=True) + glob.glob(ROOT + "/../skills/*/SKILL.md")
for p in sorted(docs):
    for i, line in enumerate(open(p, encoding="utf-8"), 1):
        for m in PATH.finditer(line):
            t = m.group(1).rstrip(".")
            if not os.path.exists(os.path.join(ROOT, t)):
                bad += 1
                print("%s:%d: missing %s" % (os.path.relpath(p, ROOT), i, t))
print("%d broken path(s)" % bad)
sys.exit(1 if bad else 0)
