"""Run: python3 skill/scripts/test_fat_playbook.py -- Playbook FAT warnings fire on bad input, stay quiet on good."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fat  # noqa: E402


def tr(code):
    return {"root": {"type": "ia.display.label", "props": {"text": {"binding": {"type": "property", "config": {
        "path": "x"}, "transforms": [{"type": "script", "code": code}]}}}}}


def checks(doc):
    return [c for _, c, _ in fat.playbook_warnings(doc)]


assert checks(tr("\treturn value * 2")) == ["playbook.script-transform"]
assert checks(tr("\treturn value != \"\"")) == ["playbook.script-transform"]
assert not checks(tr("\tout = []\n\tfor r in value:\n\t\tout.append(r[0])\n\treturn out"))
assert not checks(tr("\treturn system.tag.readBlocking(['a'])[0].value"))
assert not checks(tr("\treturn value.getColumnNames()"))

lbl = lambda t, s: {"root": {"type": t, "props": {"style": s}}}  # noqa: E731
assert checks(lbl("ia.display.label", {"color": "#FF000F"})) == ["playbook.hex-literal"]
assert not checks(lbl("ia.display.label", {"color": "var(--hmi-text)"}))
assert not checks(lbl("ia.chart.xy", {"color": "#FF000F"}))  # charts need literal hex
print("ok")
