#!/usr/bin/env python3
"""Build loop: build -> FAT -> deploy -> SAT -> report. Stops at the first red. No LLM, no MCP.

    IGNITION_URL=http://host:8088 IGNITION_API_KEY=keyName:secret \\
    python3 skill/scripts/loop.py <build-dir> --project <name> [--no-deploy] [--report out.json]

<build-dir> holds build.py, which writes project-relative resources to <build-dir>/_staged
(the repo's scripts/builds/<x>/ convention). Deploy copies the staged tree into the gateway's
data/projects/<name>/ with the write-fsync-scan protocol (references/gateway/resource-formats.md
§10-11): scan-lock, gateway-side copy with fsync (resource.json last), POST scan.
The gateway host must be able to read a directory this host can write ("stage dir"):
auto-detected on WSL (Windows %TEMP%), else pass --stage-dir and --stage-dir-gw.
Exit 0 green, 1 red, 2 usage, 3 paused (HTTP 402: trial lapsed -- report and stop, never reset).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ign  # noqa: E402
import fat  # noqa: E402
import sat  # noqa: E402

COPY = r'''
import os
from com.inductiveautomation.ignition.gateway import IgnitionGateway
src = %(src)r
proj = os.path.join(system.util.getProperty('user.dir'), 'data', 'projects', %(project)r)
n = 0
for dp, dn, fn in os.walk(src):
    for f in sorted(fn, key=lambda x: (x == 'resource.json', x)):
        dst = os.path.join(proj, os.path.relpath(os.path.join(dp, f), src))
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        with open(os.path.join(dp, f), 'rb') as i:
            data = i.read()
        with open(dst, 'wb') as o:
            o.write(data)
            o.flush()
            os.fsync(o.fileno())
        n += 1
result = n
'''


def stage_location(a):
    """(local dir, path as the gateway sees it). WSL default: Windows %TEMP% via cmd.exe."""
    if a.stage_dir:
        return a.stage_dir, a.stage_dir_gw or a.stage_dir
    try:
        win = subprocess.run(["cmd.exe", "/c", "echo %TEMP%"], cwd="/mnt/c", capture_output=True,
                             text=True, timeout=20).stdout.strip()
        loc = subprocess.run(["wslpath", "-u", win], capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        win = loc = ""
    if not win or not loc:
        sys.exit("cannot detect a stage dir; pass --stage-dir and --stage-dir-gw")
    sub = "ign-loop-%d" % time.time()
    return os.path.join(loc, sub), win + "\\" + sub


def deploy(a, staged):
    local, gw = stage_location(a)
    n = 0
    for root in sat.ROOTS:
        s = os.path.join(staged, root)
        if os.path.isdir(s):
            shutil.copytree(s, os.path.join(local, root))
            n += sum(len(f) for _, _, f in os.walk(s))
    _ign.http("POST", "/data/api/v1/scan-lock/projects", {"acquireTimeout": 10, "holdTimeout": 120})
    try:
        copied = _ign.script_exec(COPY % dict(src=gw, project=a.project))
    finally:
        shutil.rmtree(local, ignore_errors=True)
    code, _ = _ign.http("POST", "/data/api/v1/scan/projects")
    if copied != n or code != 200:
        raise RuntimeError("deploy: staged %d files, gateway copied %s, scan HTTP %s" % (n, copied, code))
    return dict(files=n, stage=gw)


def step(name, fn, steps):
    t = time.time()
    try:
        out = fn()
    except _ign.Paused as e:
        steps.append(dict(step=name, ok=False, paused=True, error=str(e)))
        return False
    except Exception as e:
        steps.append(dict(step=name, ok=False, error=str(e)[:500]))
        return False
    ok = out.get("ok", True) if isinstance(out, dict) else True
    steps.append(dict(step=name, ok=ok, seconds=round(time.time() - t, 1), result=out))
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("build_dir")
    ap.add_argument("--project", required=True)
    ap.add_argument("--staged", default="_staged")
    ap.add_argument("--no-deploy", action="store_true", help="build + FAT only")
    ap.add_argument("--wait", type=int, default=300, help="seconds SAT waits for the scan to load resources")
    ap.add_argument("--stage-dir")
    ap.add_argument("--stage-dir-gw")
    ap.add_argument("--report")
    a = ap.parse_args()
    bd = os.path.abspath(a.build_dir)
    staged = os.path.join(bd, a.staged)
    steps, since = [], int(time.time() * 1000)

    def build():
        shutil.rmtree(staged, ignore_errors=True)
        r = subprocess.run([sys.executable, "build.py"], cwd=bd, capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError("build.py exited %d: %s" % (r.returncode, (r.stderr or r.stdout)[-400:]))
        return dict(ok=True, output=r.stdout.strip()[-200:])

    def do_sat():
        return sat.run(a.project, staged, since, a.wait).data()

    plan = [("build", build), ("fat", lambda: fat.run(staged).data())]
    if not a.no_deploy:
        plan += [("deploy", lambda: deploy(a, staged)), ("sat", do_sat)]
    ok = all(step(n, f, steps) for n, f in plan)          # all() stops at the first red
    paused = any(s.get("paused") or (s.get("result") or {}).get("paused") for s in steps)
    out = dict(tool="loop", ok=ok and not paused, paused=paused, project=a.project, steps=steps)
    text = json.dumps(out, indent=2)
    if a.report:
        open(a.report, "w").write(text + "\n")
    print(text)
    return _ign.EXIT_PAUSED if paused else (_ign.EXIT_OK if ok else _ign.EXIT_RED)


if __name__ == "__main__":
    sys.exit(main())
