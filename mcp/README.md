# Ignition MCP server (reference, not vendored)

The MCP server used for live-gateway tool calls (`mcp__ignition-mcp__*`) is a
clean, unmodified clone of a third-party project, not code authored here:

https://github.com/WhiskeyHouse/ignition-mcp (GPLv3)

Clone that repo directly on the new machine rather than copying a vendored
copy from here:

```
uv run --directory <path-to-clone> python -m ignition_mcp.main --transport stdio
```

## What's actually yours in here

The files in this folder are your working config templates, copied with
secrets stripped:

- `.env.example` — env var names for gateway URL / API key / basic auth /
  server host+port. Copy to `.env` next to the cloned server and fill in
  real values (never commit that file).
- `.mcp.json.example`, `.mcp-alt.json`, `.mcp-http.json`, `.mcp-simple.json`
  — Claude Code MCP registration variants tried during setup (stdio vs http,
  different arg shapes).

## Wiring it into Claude Code

Register it in `.claude.json` / project `.mcp.json` as a stdio server, e.g.:

```json
"ignition-mcp": {
  "type": "stdio",
  "command": "uv",
  "args": ["run", "--directory", "<path-to-clone>", "python", "-m", "ignition_mcp.main", "--transport", "stdio"],
  "env": { "IGNITION_MCP_IGNITION_GATEWAY_URL": "http://localhost:8088" }
}
```

`tools/ignition_agent.py` in this repo reads this same `mcpServers.ignition-mcp`
block out of `~/.claude.json` to reuse the server outside Claude Code (e.g.
with Gemini/Ollama as the driving model) — see that file's docstring.
