#!/usr/bin/env python3
"""Forge: turn a Scout map + its source export into a re-runnable build script.

    python3 scripts/forge.py --scout scout-report/ [--zip export.zip | --live PROJECT] \\
        --name <build-name> [--out-root scripts/builds]

Writes <out-root>/<name>/{build.py, src/, tags.json}. build.py (stdlib only) copies src/ into
./_staged/ (the layout scripts/loop.py deploys and SAT checks), optionally retargeting tag
providers; it holds no project name, so the same build deploys to any target project:

    python3 scripts/loop.py <out-root>/<name> --project <Target>

Staged: the perspective/ and ignition/ resource roots (views, page-config, style classes,
session props, named queries, script library, gateway timers). NOT staged, listed in the
report: alarm pipelines, event streams, reports, Vision (binary/other modules).
tags.json lists tag paths the project references; definitions are not in an export.
Stdlib only, no LLM, no MCP. Exit 0 ok, 2 bad input, 3 paused (HTTP 402).
"""
import argparse
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ign  # noqa: E402
import scout  # noqa: E402

ROOTS = (_ign.PERSP + "/", "ignition/")

BUILD = '''"""Rebuild of {project} (Forge, from Scout map of {source}).

    python3 build.py

Copies ./src/ (verbatim resources of the source project) into ./_staged/ for scripts/loop.py.
The build holds no project name: deploy to any target with
    python3 skill/scripts/loop.py . --project <Target>
Tag paths the project references (definitions are NOT in a project export): ./tags.json.
Set RETARGET to map a source tag provider to the target's, e.g. {{"OldProv": "NewProv"}}.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
STAGED = os.path.join(HERE, "_staged")
RETARGET = {{}}  # source tag provider -> target tag provider; applied to resource text (not resource.json)


def main():
    shutil.rmtree(STAGED, ignore_errors=True)
    n = 0
    for dp, _, fn in os.walk(SRC):
        for f in sorted(fn, key=lambda x: (x == "resource.json", x)):  # resource.json last
            src = os.path.join(dp, f)
            dst = os.path.join(STAGED, os.path.relpath(src, SRC))
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(src, "rb") as i:
                data = i.read()
            if RETARGET and f != "resource.json":
                try:
                    text = data.decode("utf-8")
                except UnicodeDecodeError:
                    text = None
                if text is not None:
                    for a, b in RETARGET.items():
                        text = text.replace("[%s]" % a, "[%s]" % b)
                    data = text.encode("utf-8")
            with open(dst, "wb") as o:
                o.write(data)
                o.flush()
                os.fsync(o.fileno())
            n += 1
    print("staged %d files -> %s" % (n, STAGED))


if __name__ == "__main__":
    main()
'''


def load_files(a):
    if a.zip:
        return scout.load_zip(a.zip, a.project)
    if a.live:
        return scout.load_live(a.live)
    zips = sorted(f for f in os.listdir(a.scout) if f.endswith(".zip"))
    if len(zips) != 1:
        raise scout.ScoutError("give --zip or --live (or leave exactly one .zip in %s)" % a.scout)
    return scout.load_zip(os.path.join(a.scout, zips[0]), a.project)


def tag_placeholder(m):
    """tags.json body from map['tags']['referenced']; suspect = regex false hit (empty path)."""
    out = []
    for t in m["tags"]["referenced"]:
        rest = t["path"].split("]", 1)[1] if "]" in t["path"] else ""
        out.append(dict(path=t["path"], provider=t["provider"], used_by=t["used_by"],
                        indirect=t.get("indirect", False), suspect=not rest))
    return dict(note="Referenced tag paths only; tag/UDT definitions are not in a project export. "
                     "Create them (ignition-tags) or retarget with RETARGET in build.py. "
                     "suspect = probably a regex false hit, verify.",
                source_tag_provider=m["project"].get("gateway", {}).get("tagProvider", ""),
                tags=out)


def forge(a):
    m = _ign.read_json(os.path.join(a.scout, "map.json"))
    src = load_files(a)
    if src["name"] != m["project"]["name"] and not a.zip:
        raise scout.ScoutError("map.json is for %r, source is %r" % (m["project"]["name"], src["name"]))
    dest = os.path.join(a.out_root, a.name)
    shutil.rmtree(os.path.join(dest, "src"), ignore_errors=True)
    staged, skipped = 0, {}
    for path, data in sorted(src["files"].items()):
        if path.startswith(ROOTS):
            p = os.path.join(dest, "src", path)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(data)
            staged += 1
        elif path != "project.json":
            k = "/".join(path.split("/")[:2])
            skipped[k] = skipped.get(k, 0) + 1
    with open(os.path.join(dest, "build.py"), "w") as f:
        f.write(BUILD.format(project=m["project"]["name"], source=m["source"]["ref"]))
    os.chmod(os.path.join(dest, "build.py"), 0o755)
    tags = tag_placeholder(m)
    with open(os.path.join(dest, "tags.json"), "w") as f:
        json.dump(tags, f, indent=2)
        f.write("\n")
    return dict(build=dest, staged_files=staged, tag_paths=len(tags["tags"]),
                tag_suspect=sum(t["suspect"] for t in tags["tags"]),
                not_staged=skipped, broken_refs={k: v for k, v in m["broken_refs"].items() if v})


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--scout", required=True, help="Scout output dir (map.json)")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--zip", help="source project export zip (default: the one .zip in --scout)")
    g.add_argument("--live", metavar="PROJECT", help="re-export the source project (read-only REST)")
    ap.add_argument("--project", help="source project name for --zip")
    ap.add_argument("--name", required=True, help="build name -> <out-root>/<name>/")
    ap.add_argument("--out-root", default="scripts/builds")
    a = ap.parse_args(argv)
    try:
        r = forge(a)
    except (scout.ScoutError, OSError, ValueError, KeyError) as e:
        print("forge: %s" % e, file=sys.stderr)
        return _ign.EXIT_USAGE
    print(json.dumps(r, indent=2))
    return _ign.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
