"""Ignition-aware agent: Gemini (free API) + existing ignition-mcp server as tools.

Reuses the same ignition-mcp server Claude Code already talks to (config pulled
straight from .claude.json) instead of reimplementing Ignition Gateway calls.
Not tied to one project -- tools are discovered live from the MCP server, and
you point it at whatever project/path you want in your question.

Setup:
  pip install mcp
  put GEMINI_API_KEY=your_key in a .env file next to this script
"""
import asyncio
import json
import os
import re
import time
import urllib.request

ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_dotenv(path: str) -> None:
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


load_dotenv(ENV_FILE)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.6-flash:generateContent"
)
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma3:4b"
CLAUDE_JSON = os.path.expanduser("~/.claude.json")

ACTION_RE = re.compile(r"ACTION:\s*(\w+)\((.*)\)", re.DOTALL)
FINAL_RE = re.compile(r"FINAL:\s*(.*)", re.DOTALL)


def load_ignition_mcp_server_params() -> StdioServerParameters:
    with open(CLAUDE_JSON, encoding="utf-8") as f:
        cfg = json.load(f)["mcpServers"]["ignition-mcp"]
    return StdioServerParameters(command=cfg["command"], args=cfg["args"], env=cfg.get("env"))


def call_gemini(prompt: str, retries: int = 3) -> str:
    api_key = os.environ["GEMINI_API_KEY"]
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(
        f"{GEMINI_URL}?key={api_key}", data=body, headers={"Content-Type": "application/json"}
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = 2 ** (attempt + 2)
                print(f"  ... rate limited, waiting {wait}s")
                time.sleep(wait)
                continue
            raise
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def call_ollama(prompt: str) -> str:
    body = json.dumps({"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())["response"].strip()


def call_llm(prompt: str) -> str:
    try:
        return call_gemini(prompt)
    except Exception as e:
        print(f"  ... Gemini unavailable ({e}), falling back to local Ollama (slow)")
        return call_ollama(prompt)


def build_system_prompt(tools) -> str:
    lines = [
        "You are an agent that answers questions about an Ignition SCADA gateway.",
        "Available tools:",
    ]
    for t in tools:
        lines.append(f"- {t.name}({json.dumps(t.input_schema.get('properties', {}))}): {t.description}")
    lines += [
        "",
        "On each turn respond with EXACTLY ONE of:",
        "  ACTION: tool_name({\"arg\": \"value\"})   <- valid JSON object for args",
        "  FINAL: your answer",
        "Do not explain, do not use both in one turn. Wait for OBSERVATION before continuing.",
    ]
    return "\n".join(lines)


async def run_agent(session: ClientSession, system: str, task: str, max_steps: int = 6) -> str:
    transcript = f"{system}\n\nTask: {task}\n"
    for _ in range(max_steps):
        try:
            reply = call_llm(transcript)
        except Exception as e:
            return f"[both Gemini and Ollama failed: {e}]"
        transcript += reply + "\n"

        if m := FINAL_RE.search(reply):
            return m.group(1).strip()

        if m := ACTION_RE.search(reply):
            tool, raw_args = m.group(1).strip(), m.group(2).strip()
            print(f"  ... calling {tool}({raw_args})")
            try:
                args = json.loads(raw_args) if raw_args else {}
                result = await asyncio.wait_for(session.call_tool(tool, arguments=args), timeout=30)
                obs = "\n".join(c.text for c in result.content if hasattr(c, "text"))
            except TimeoutError:
                obs = f"ERROR: {tool} timed out after 30s"
            except Exception as e:
                obs = f"ERROR: {e}"
            transcript += f"OBSERVATION: {obs}\n"
            continue

        return f"[agent gave unparseable output]: {reply}"

    return "[max steps reached without FINAL answer]"


async def main():
    if "GEMINI_API_KEY" not in os.environ:
        print("No GEMINI_API_KEY set -- using local Ollama only (slow).")

    params = load_ignition_mcp_server_params()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            system = build_system_prompt(tools)
            print(f"Connected. {len(tools)} tools available.")

            demo = await run_agent(session, system, "What is the gateway's version and edition?")
            print("demo:", demo)

            print("\nType a question about the gateway (blank to quit):")
            while task := input("> ").strip():
                print(await run_agent(session, system, task))


if __name__ == "__main__":
    asyncio.run(main())
