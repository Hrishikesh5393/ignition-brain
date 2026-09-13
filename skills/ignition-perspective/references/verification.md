# Verifying Perspective behaviour

Four recipes. None needs a decompiler for the first, and none needs source access at
all. Every command below was run on Ignition 8.3.7 and the output shown is real.

Set these once:

```bash
JAR_CACHE="/c/Program Files/Inductive Automation/Ignition/data/jar-cache/com.inductiveautomation.perspective"
JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-17.0.20.8-hotspot"
GATEWAY="http://localhost:8088"
```

---

## 1. Component schema and child positions

The authoritative answer for any component's props. Plain JSON inside a jar.

```bash
"$JAVA_HOME/bin/jar" xf "$JAR_CACHE"/*perspective-common*.jar ia.components.json
```

70 components in `ia.components.json`. The palette also loads
`perspective-map`, `perspective-googlemap`, `perspective-timeseries`,
`perspective-amcharts`, `pdf-viewer` and `barcode` from sibling files in the same jar,
for **81 total**. Read one:

```bash
python -c "
import json,io
d=json.load(io.open('ia.components.json',encoding='utf8'))
items=d['components'] if 'components' in d else list(d.values())
f=[x for x in items if x.get('id')=='ia.container.flex'][0]
print('keys:', list(f.keys()))
print('props:', list(f['schema']['properties'].keys()))
print('required:', f['schema'].get('required'))
print('childPosition:', list(f['childPositionSchema']['properties'].keys()))
"
```

Real output:

```
keys: ['id', 'name', 'palette', 'schema', 'childPositionSchema', 'resources']
props: ['direction', 'wrap', 'justify', 'alignItems', 'alignContent', 'style']
required: ['direction', 'wrap', 'justify', 'alignItems', 'alignContent', 'style']
childPosition: ['grow', 'shrink', 'basis', 'align', 'display']
```

**`childPositionSchema` is a sibling of `schema`, not inside it.** That is how children
of a container are configured, and it is easy to miss if you only print `schema`.

Component ids follow the palette: `ia.container.*`, `ia.display.*`, `ia.input.*`,
`ia.navigation.*`, `ia.chart.*`, `ia.symbol.*`.

---

## 2. Client runtime behaviour

For "why does this do nothing". The client bundle is served by the gateway, unminified
enough to grep.

```bash
BUNDLE=$(curl -s "$GATEWAY/data/perspective/client/<AnyProject>" \
         | grep -oE '/res/perspective/js/PerspectiveClient\.[a-f0-9]+\.js' | head -1)
curl -s -o pc.js "$GATEWAY$BUNDLE"
```

The hash changes between versions, so always read it from the page rather than
hardcoding.

This is how the dead script action was found:

```bash
grep -oE 'if\("C"===[a-z]\)\{const [a-z]=[a-z]\.ActionRegistry\.get\([a-z]\).{0,70}' pc.js
```

```
if("C"===p){const e=n.ActionRegistry.get(i);if(e){const t=e.create(this.component,o);a.clientActions.push(t)}}els
```

`if (e)` with no else. A type with no client-side implementation is dropped silently.
Python has no client-side action, so `scope: "C"` on a script means nothing runs and
nothing is logged.

Same file answers what a PropertyTree can read:

```bash
grep -oE 'read(String|Number|Boolean|Object|Array|Encoded|Date|Color)\([a-z],' pc.js | sort -u
```

```
readArray(  readBoolean(  readColor(  readDate(  readEncoded(  readNumber(  readObject(  readString(
```

---

## 3. Java internals, designer and gateway

For module SDK work and anything the client cannot answer.

```bash
"$JAVA_HOME/bin/jar" xf "$JAR_CACHE"/*perspective-common*.jar \
  com/inductiveautomation/perspective/common/api/ComponentDescriptor.class
"$JAVA_HOME/bin/javap" com/inductiveautomation/perspective/common/api/ComponentDescriptor.class
```

```
public default java.util.Collection<...ComponentEventDescriptor> events();
public abstract java.util.Optional<javax.swing.Icon> getIcon();
```

`javap -p -c` gives bytecode when a method body matters. That is how
`Route.pathMatches` was found to require equal path-segment counts, and how
`ComponentNode` was found to call `descriptor.getIcon().ifPresent(this::setIcon)`.

SDK jars for compile-time classes live under the Gradle cache:

```bash
find ~/.gradle/caches/modules-2/files-2.1/com.inductiveautomation.ignition -name "*.jar"
```

---

## 4. The live gateway

For what this deployment is doing now, rather than what the platform can do. Use the
`ignition-mcp` tools, and see the `ignition` skill for the full list.

Quick probes that need no tooling:

```bash
curl -sI "$GATEWAY/system/webdev/"        # servlets mount at /system/<name>/
curl -sI "$GATEWAY/res/<module-alias>/"   # module jar resources
```

A `402` from a WebDev endpoint is the trial licence window expiring, not a code fault.

---

## Order of resort

0. `Ignition-knowledgebase/16-PERSPECTIVE-SCHEMA-TRUTH.md` - the schema index, the style
   precedence chain, and the full 81-component inventory, all jar-verified.
   `04-RESOURCE-MODEL.md` for the resource-type registry and on-disk layout.
1. `Ignition-knowledgebase/Components/<Category>/<Name>.md` - fastest, carries traps.
2. Recipe 1, the schema, when the KB is silent or the version differs.
3. Recipe 2, the client bundle, for "it does nothing".
4. Recipe 3, javap, for module SDK and designer internals.

If the KB and the schema disagree, the schema wins for this install, and the
disagreement is worth telling the user about rather than silently picking a side.
