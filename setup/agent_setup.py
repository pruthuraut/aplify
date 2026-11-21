"""Set up aplify for Codex CLI and/or Gemini CLI with Playwright MCP (extension mode).

Usage:  python setup/agent_setup.py [--codex] [--gemini] [--agy]      (no flag = all)

- Codex: registers a global MCP server "playwright" (`codex mcp add ...`) unless one already exists.
- Gemini: the project already ships .gemini/settings.json (MCP server) and GEMINI.md (imports AGENTS.md);
  this only checks that the `gemini` command is installed.
- agy (Antigravity CLI): uses its built-in `/browser` subagent (Chrome DevTools MCP); this checks the
  command and prints the one-time Chrome remote-debugging step. Playwright MCP stays as its fallback.
Codex/Gemini then need the "Playwright MCP Bridge" Chrome extension so the agent can drive YOUR Chrome
(your logins + Simplify). Nothing here is paid: Playwright MCP is open source (Apache-2.0).
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PKG = "@playwright/mcp@0.0.86"
SERVER = ["npx", "-y", PKG, "--extension"]


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, shell=sys.platform == "win32")


def setup_codex() -> None:
    if not have("codex"):
        print("[codex] not installed - install it (e.g. `npm i -g @openai/codex`) and rerun.")
        return
    if run(["codex", "mcp", "get", "playwright"]).returncode == 0:
        print("[codex] MCP server 'playwright' already configured - leaving it as is.")
        return
    r = run(["codex", "mcp", "add", "playwright", "--", *SERVER])
    print("[codex] added MCP server 'playwright'." if r.returncode == 0 else f"[codex] failed:\n{r.stderr or r.stdout}")


def setup_gemini() -> None:
    if have("gemini"):
        print("[gemini] installed; .gemini/settings.json in this folder adds the Playwright MCP server.")
    else:
        print("[gemini] not installed - install it with `npm i -g @google/gemini-cli`; "
              ".gemini/settings.json in this folder already configures Playwright MCP.")


def setup_agy() -> None:
    default = Path.home() / "AppData" / "Local" / "agy" / "bin" / "agy.exe"  # Windows install location
    agy = shutil.which("agy") or (str(default) if default.exists() else None)
    if not agy:
        print("[agy] not found - install Antigravity CLI and run `agy install`, then rerun.")
        return
    print("[agy] installed. It uses `/browser` (your own Chrome). One-time: Chrome 144+, open\n"
          "      chrome://inspect/#remote-debugging and turn on 'Allow remote debugging for this browser instance';\n"
          "      click Allow when Chrome asks. Turn it off when you're done applying.")
    if "playwright" not in run([agy, "mcp", "list"]).stdout:
        print("[agy] optional fallback: agy mcp add playwright " + " ".join(SERVER))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--codex", action="store_true")
    ap.add_argument("--gemini", action="store_true")
    ap.add_argument("--agy", action="store_true")
    a = ap.parse_args()
    both = not (a.codex or a.gemini or a.agy)
    if not have("npx"):
        sys.exit("Node.js (npx) is required: https://nodejs.org/")
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "resume-builder"))
    from build_resume import find_pdflatex  # also finds per-user MiKTeX installs not on PATH
    try:
        find_pdflatex()
    except SystemExit:
        print("warning: pdflatex not found (needed for resume/cover-letter builds) - install MiKTeX or TeX Live.")
    if both or a.codex:
        setup_codex()
    if both or a.gemini:
        setup_gemini()
    if both or a.agy:
        setup_agy()
    print("\nCodex/Gemini, last step (once): install the 'Playwright MCP Bridge' extension in the Chrome you use for job sites,\n"
          "stay logged in there, and keep Simplify installed. When the agent first connects, the extension asks\n"
          "which tab to share - pick it. Then run `codex` or `gemini` from this folder.")


if __name__ == "__main__":
    main()
