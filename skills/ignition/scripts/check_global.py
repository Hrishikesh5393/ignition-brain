#!/usr/bin/env python3
"""Fail if the skill tree carries project- or gateway-specific references.

The skill holds global Ignition mechanics only; project/gateway facts belong in the
driver repo's project layer (conventions/, data/, AGENTS.md). Run from anywhere:
    python3 skill/scripts/check_global.py [skill_dir]
Exit 1 and list file:line for every hit. Extend PATTERNS, not the allowlist, when a
new class of leak shows up. Each ALLOW entry is (path suffix, regex) for a reviewed
false positive (release documentation, docs example URLs).
"""
import os, re, sys

PATTERNS = [
    r"MSN_?\w*", r"AI_Training", r"\bAXLAP\w*", r"\bmerit\b", r"\bMerit\w*",
    r"localhost:8088", r"Adoptium|ClaudeMem", r"firstmate", r"crewmate",
    r"this gateway", r"this install\b", r"this repo\b", r"this project\b",
    r"AGENTS\.md", r"\bfm/", r"hrishi", r"ignition-skill-build", r"\bdata/[a-z-]+/notes",
    r"conventions/",
]
ALLOW = [
    ("ignition-8-3/whats-new-8.3.md", r"localhost:8088"),   # docs example URL
    ("ignition-8-3/", r"this project|this install"),        # manual prose
    ("scripts/deploy_webdev_endpoints.py", r"localhost:8088"),  # documented default URL
    ("scripts/check_global.py", r".*"),                       # this file lists the patterns
]
RX = re.compile("|".join(PATTERNS))


def main(root):
    bad = 0
    sib = os.path.normpath(os.path.join(root, "..", "skills"))   # thin sibling skills
    walk = list(os.walk(root)) + (list(os.walk(sib)) if os.path.isdir(sib) else [])
    for dp, dn, fn in walk:
        dn[:] = [d for d in dn if d != "by-id" and not d.startswith(".")]
        for f in fn:
            if not f.endswith((".md", ".py", ".sh", ".json")) or f in ("system-api.json", "system-api-coverage.json"):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, os.path.join(root, ".."))
            for i, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
                m = RX.search(line)
                if m and not any(s in rel and re.search(r, line) for s, r in ALLOW):
                    bad += 1
                    print("%s:%d: %s" % (rel, i, line.strip()[:110]))
    print("%d project/gateway reference(s)" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..")))
