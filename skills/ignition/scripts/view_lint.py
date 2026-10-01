"""Lint a Perspective view.json against its component by-id schemas.

Catches three bug classes seen in real Perspective builds:
  1. a chart/gauge left with a required prop genuinely unset (no schema
     default, no props/propConfig binding)
  2. an ia.display.view embed passing a params{} key the target view never
     declares (the appHeader/breadcrumb bug)
  3. a value set on a key the schema doesn't recognize -- especially one
     nested one level wrong, like a flat `title` where the schema wants
     `header.title` (a table's `title` set flat instead of under `header`). Checked recursively
     through every object/array prop, at the top-level props{} and inside
     every array item (e.g. each `columns` entry), against whatever nesting
     depth the schema actually has `additionalProperties: false` at.

Usage:
    python3 scripts/lib/view_lint.py <project-root>/com.inductiveautomation.perspective/views/<name>/view.json

Exits 1 if any finding is printed, 0 if clean.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED_SCHEMA_DIR = os.path.abspath(os.path.join(HERE, "..", "schema", "perspective", "by-id"))
SCHEMA_DIR = BUNDLED_SCHEMA_DIR


def _find_schema_dir(view_json_path):
    """Walk up from the target view.json looking for a project's own
    schema/perspective/by-id/ (e.g. a driver repo's own copy); fall back to the
    copy bundled alongside this script so the linter works standalone
    against any project."""
    d = os.path.dirname(os.path.abspath(view_json_path))
    while True:
        candidate = os.path.join(d, "schema", "perspective", "by-id")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(d)
        if parent == d:
            return BUNDLED_SCHEMA_DIR
        d = parent


def _load_schema(comp_type):
    path = os.path.join(SCHEMA_DIR, comp_type + ".json")
    if not os.path.isfile(path):
        return None
    with open(path) as f:
        return json.load(f)


def _has_recursive_default(prop_schema):
    """True if Perspective can fully construct this prop from schema defaults
    alone (a top-level default, or an object whose every property recursively
    resolves to a default) -- e.g. simple-gauge's `arc` has no top-level
    default but every one of its fields (width/color/cornerRadius) does, so
    Perspective's own component defaultProps cover it."""
    if not isinstance(prop_schema, dict):
        return False
    if "default" in prop_schema:
        return True
    if "$ref" in prop_schema:
        # shared schemas (style-properties, etc.) are always optional at the
        # view.json level -- every component ships full internal defaults for
        # them (confirmed empirically: components in real views routinely omit
        # `style` partially or fully and render fine).
        return True
    if prop_schema.get("type") == "object":
        properties = prop_schema.get("properties", {})
        if not properties:
            return False
        return all(_has_recursive_default(p) for p in properties.values())
    return False


def _propconfig_covers(propconfig_keys, prop_name):
    prefix = "props." + prop_name
    return any(k == prefix or k.startswith(prefix + ".") for k in propconfig_keys)


def _suggest_nesting(key, properties):
    """If `key` isn't a recognized property here but IS a direct property of
    some object-typed sibling in `properties`, that sibling is almost
    certainly where it belongs (the title-vs-header.title case, generalized:
    any same-named property one level deeper in an object-typed sibling)."""
    for sib_name, sib_schema in properties.items():
        if not isinstance(sib_schema, dict):
            continue
        if sib_schema.get("type") == "object" and key in sib_schema.get("properties", {}):
            return sib_name
    return None


def _unknown_key_msg(key, properties):
    suggestion = _suggest_nesting(key, properties)
    if suggestion:
        return "unknown property %r - did you mean nesting under %r?" % (key, suggestion)
    return "unknown property %r (not in schema)" % (key,)


def _check_object_keys(value, schema_node, path, findings):
    """Recursively walk an authored dict `value` against JSON-schema node
    `schema_node`. Flags any key not in schema_node's properties when
    schema_node has `additionalProperties: false`; always recurses into
    every key that IS a known object/array property, so a violation nested
    arbitrarily deep (e.g. inside each item of an array prop) is still
    found -- not just at the top level."""
    if not isinstance(value, dict) or not isinstance(schema_node, dict):
        return
    properties = schema_node.get("properties", {})
    if schema_node.get("additionalProperties") is False:
        for key in value:
            if key not in properties:
                findings.append("%s: %s" % (path, _unknown_key_msg(key, properties)))
    for key, val in value.items():
        sub_schema = properties.get(key)
        if not isinstance(sub_schema, dict):
            continue
        if sub_schema.get("type") == "object" and isinstance(val, dict):
            _check_object_keys(val, sub_schema, path + "." + key, findings)
        elif sub_schema.get("type") == "array" and isinstance(val, list):
            items_schema = sub_schema.get("items")
            if isinstance(items_schema, dict) and items_schema.get("type") == "object":
                for i, item in enumerate(val):
                    if isinstance(item, dict):
                        _check_object_keys(item, items_schema, "%s.%s[%d]" % (path, key, i), findings)


def _propconfig_tokens(key):
    # "props.columns[0].header.title" -> ["columns", "header", "title"]
    rest = key[len("props"):].lstrip(".")
    tokens = []
    for part in rest.split("."):
        while "[" in part:
            base, _, remainder = part.partition("[")
            if base:
                tokens.append(base)
            _idx, _, part = remainder.partition("]")
        if part:
            tokens.append(part)
    return tokens


def _check_propconfig_path(tokens, schema_node, orig_key, path, findings):
    """Schema-only walk (no authored value available) checking that a
    propConfig binding target path actually resolves through the schema --
    catches an unknown/misplaced nesting set only via a binding, never in
    props{} literally."""
    if not tokens or not isinstance(schema_node, dict):
        return
    head, rest = tokens[0], tokens[1:]
    properties = schema_node.get("properties", {})
    if head not in properties:
        if schema_node.get("additionalProperties") is False:
            findings.append("%s: propConfig %r targets %s" %
                             (path, orig_key, _unknown_key_msg(head, properties)))
        return
    if not rest:
        return
    sub = properties[head]
    if not isinstance(sub, dict):
        return
    if sub.get("type") == "array":
        items_schema = sub.get("items")
        if isinstance(items_schema, dict):
            _check_propconfig_path(rest, items_schema, orig_key, path, findings)
    elif sub.get("type") == "object":
        _check_propconfig_path(rest, sub, orig_key, path, findings)


_ACTION_ENVELOPE_KEYS = ("config", "scope", "type")


def _check_events_shape(events, path, findings):
    """Flag events.<domain>.<eventName> actions that are not the
    {config, scope, type} envelope (optional `permissions`). A bare
    {"script": "..."} throws `NullPointerException: ActionConfig$ActionScope
    .name() ... "actionConfig.scope" is null` on every project-diff request
    and breaks every client (see
    references/gateway/perspective-events.md)."""
    if not isinstance(events, dict):
        return
    for domain, domain_events in events.items():
        if not isinstance(domain_events, dict):
            continue
        for event_name, value in domain_events.items():
            if not isinstance(value, dict):
                continue
            missing = [k for k in _ACTION_ENVELOPE_KEYS if k not in value]
            if "script" in value or missing:
                findings.append(
                    "%s: events.%s.%s is not a {config, scope, type} action "
                    "(missing %s%s) -- a bare {\"script\": ...} action NPEs on "
                    "project-diff; use {\"config\": {\"script\": ...}, \"scope\": \"G\", "
                    "\"type\": \"script\"} (optional \"permissions\")"
                    % (path, domain, event_name, missing,
                       "; has bare 'script'" if "script" in value else ""))


def _views_root(view_json_path):
    # .../com.inductiveautomation.perspective/views/<name>/view.json
    #                                          ^ walk up to here
    d = os.path.dirname(view_json_path)
    while os.path.basename(d) != "views" and d != os.path.dirname(d):
        d = os.path.dirname(d)
    return d


def _target_params(views_root, view_path):
    # view_path is project-relative, bare (e.g. "common/appHeader" or "oee")
    candidate = os.path.join(views_root, view_path.replace("/", os.sep), "view.json")
    if not os.path.isfile(candidate):
        return None  # can't resolve; not this linter's problem
    with open(candidate) as f:
        v = json.load(f)
    return set(v.get("params", {}).keys())


def lint(view_json_path):
    findings = []
    with open(view_json_path) as f:
        view = json.load(f)
    views_root = _views_root(view_json_path)

    def walk(node, path):
        if not isinstance(node, dict):
            return
        comp_type = node.get("type")
        name = node.get("meta", {}).get("name", "?")
        node_path = "%s/%s" % (path, name)

        if comp_type:
            schema = _load_schema(comp_type)
            if schema is None:
                findings.append("%s: unknown component type %r (no by-id schema)"
                                 % (node_path, comp_type))
            else:
                comp_schema = schema.get("schema", {})
                required = comp_schema.get("required") or []
                properties = comp_schema.get("properties", {})
                props = node.get("props", {})
                propconfig_keys = list(node.get("propConfig", {}).keys())
                for r in required:
                    prop_schema = properties.get(r, {})
                    if _has_recursive_default(prop_schema):
                        continue  # has a runtime default; unset is fine
                    if r in props:
                        continue
                    if _propconfig_covers(propconfig_keys, r):
                        continue
                    findings.append(
                        "%s (%s): required prop %r missing from props and propConfig"
                        % (node_path, comp_type, r))

                _check_object_keys(props, comp_schema, "%s (%s) props" % (node_path, comp_type), findings)
                for pc_key in propconfig_keys:
                    if pc_key == "props" or pc_key.startswith("props."):
                        _check_propconfig_path(_propconfig_tokens(pc_key), comp_schema, pc_key,
                                                "%s (%s)" % (node_path, comp_type), findings)

                if comp_type == "ia.display.table":
                    if "data" not in props and not _propconfig_covers(propconfig_keys, "data"):
                        findings.append(
                            "%s (%s): props.data not bound (neither props nor propConfig) -- table will render empty"
                            % (node_path, comp_type))

            _check_events_shape(node.get("events"), node_path, findings)

            if comp_type == "ia.display.view":
                target = node.get("props", {}).get("path")
                passed_params = set(node.get("props", {}).get("params", {}).keys())
                if target:
                    target_params = _target_params(views_root, target)
                    if target_params is not None:
                        extra = passed_params - target_params
                        for k in sorted(extra):
                            findings.append(
                                "%s: embeds %r with params key %r not declared by that view (has %s)"
                                % (node_path, target, k, sorted(target_params)))

        for child in node.get("children", []):
            walk(child, node_path)

    walk(view.get("root", {}), "")
    return findings


def main():
    if len(sys.argv) != 2:
        print("usage: python3 scripts/lib/view_lint.py <view.json path>")
        return 2
    global SCHEMA_DIR
    SCHEMA_DIR = _find_schema_dir(sys.argv[1])
    findings = lint(sys.argv[1])
    for f in findings:
        print(f)
    if findings:
        print("%d finding(s)" % len(findings))
        return 1
    print("clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
