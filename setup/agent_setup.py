"""Set up aplify's browser control for Codex CLI, Antigravity CLI (agy) and/or Gemini CLI.

Usage:  python setup/agent_setup.py [--codex] [--agy] [--gemini]      (no flag = all)

Primary browser server: Browser MCP (https://browsermcp.io/, `@browsermcp/mcp@latest`), which drives YOUR Chrome
(your logins + Simplify) in its own tab group. Fallback: Playwright MCP in extension mode.
- Codex / agy: registers the `browsermcp` and `playwright` MCP servers unless they already exist.
- Gemini: the project ships .gemini/settings.json (both servers) and GEMINI.md; this only checks `gemini` exists.
Then install the "Browser MCP" Chrome extension and click Allow the first time an agent connects.
Nothing here is paid.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SERVERS = {
    "browsermcp": ["npx", "@browsermcp/mcp@latest"],
    "playwright": ["npx", "-y", "@playwright/mcp@0.0.86", "--extension"],  # fallback
}


def find(cmd: str, default: Path = None):
    path = shutil.which(cmd)
    if path:
        return path
    return str(default) if default and default.exists() else None


def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, shell=sys.platform == "win32")


def register(label: str, exe: str, add_cmd) -> None:
    """add_cmd(name, server_args) -> full command list for that CLI."""
    listed = run([exe, "mcp", "list"]).stdout
    for name, server in SERVERS.items():
        if name in listed:
            print(f"[{label}] MCP server '{name}' already configured.")
            continue
        r = run(add_cmd(name, server))
        print(f"[{label}] added MCP server '{name}'." if r.returncode == 0
              else f"[{label}] adding '{name}' failed:\n{r.stderr or r.stdout}")


def setup_codex() -> None:
    exe = find("codex")
    if not exe:
        print("[codex] not installed - install it (e.g. `npm i -g @openai/codex`) and rerun.")
        return
    register("codex", exe, lambda name, server: [exe, "mcp", "add", name, "--", *server])


def setup_agy() -> None:
    exe = find("agy", Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe")  # Windows install location
    if not exe:
        print("[agy] not found - install Antigravity CLI and run `agy install`, then rerun.")
        return
    register("agy", exe, lambda name, server: [exe, "mcp", "add", name, *server])


def setup_gemini() -> None:
    if find("gemini"):
        print("[gemini] installed; .gemini/settings.json in this folder adds Browser MCP + Playwright MCP.")
    else:
        print("[gemini] not installed - `npm i -g @google/gemini-cli`; .gemini/settings.json already configures it.")


def main() -> None:
    ap = argparse.ArgumentParser()
    for flag in ("--codex", "--agy", "--gemini"):
        ap.add_argument(flag, action="store_true")
    a = ap.parse_args()
    every = not (a.codex or a.agy or a.gemini)
    if not shutil.which("npx"):
        sys.exit("Node.js 20+ (npx) is required: https://nodejs.org/")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "resume-builder"))
    from build_resume import find_pdflatex  # also finds per-user MiKTeX installs not on PATH
    try:
        find_pdflatex()
    except SystemExit:
        print("warning: pdflatex not found (needed for resume/cover-letter builds) - install MiKTeX or TeX Live.")
    if every or a.codex:
        setup_codex()
    if every or a.agy:
        setup_agy()
    if every or a.gemini:
        setup_gemini()
    print("\nLast step (once): install the 'Browser MCP' extension (https://browsermcp.io/) in the Chrome you use for\n"
          "job sites, pin it, stay logged in, and keep Simplify installed. The first time an agent connects it shows a\n"
          "six-digit code: check the extension popup shows the same code and click Allow.")


if __name__ == "__main__":
    main()
