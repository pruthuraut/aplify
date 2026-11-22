"""Set up aplify's browser control for Codex CLI, Antigravity CLI (agy) and/or Gemini CLI.

Usage:  python setup/agent_setup.py [--codex] [--agy] [--gemini]      (no flag = all)

Every agent must drive YOUR everyday Chrome (your logins + Simplify), never a fresh browser profile.
- agy: primary = Chrome DevTools MCP (`chrome-devtools-mcp --autoConnect`), which attaches to the Chrome you already
  have open (Chrome 144+, enable chrome://inspect/#remote-debugging once). An existing `chrome-devtools` entry that
  launches its own browser (e.g. --executablePath) is updated to attach mode. Browser MCP + Playwright stay as fallbacks.
- Codex: primary = Browser MCP (https://browsermcp.io/, `@browsermcp/mcp@latest`); fallback = Playwright MCP.
- Gemini: the project ships .gemini/settings.json and GEMINI.md; this only checks `gemini` exists.
Nothing here is paid.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

BROWSERMCP = ["npx", "@browsermcp/mcp@latest"]
PLAYWRIGHT = ["npx", "-y", "@playwright/mcp@0.0.86", "--extension"]  # fallback
# Attach to the user's running Chrome; no usage stats / CrUX lookups (job-site URLs stay local);
# --workspace lets upload_file read the tailored PDFs in applications/.
CHROME_DEVTOOLS = ["npx", "-y", "chrome-devtools-mcp@latest", "--autoConnect", "--no-usage-statistics",
                   "--no-performance-crux", "--workspace", str(REPO)]

SERVERS = {
    "codex": {"browsermcp": BROWSERMCP, "playwright": PLAYWRIGHT},
    "agy": {"chrome-devtools": CHROME_DEVTOOLS, "browsermcp": BROWSERMCP, "playwright": PLAYWRIGHT},
}
# Existing entries are kept as-is unless their listed command lacks this marker (then they are updated).
REQUIRED_MARKER = {"chrome-devtools": "--autoConnect"}


def find(cmd: str, default: Path = None):
    path = shutil.which(cmd)
    if path:
        return path
    return str(default) if default and default.exists() else None


def run(cmd: list) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, shell=sys.platform == "win32")


def register(label: str, exe: str, add_cmd, remove_cmd=None) -> None:
    """add_cmd(name, server_args) -> full command list for that CLI."""
    listed = {line.split()[0]: line for line in run([exe, "mcp", "list"]).stdout.splitlines() if line.strip()}
    for name, server in SERVERS[label].items():
        marker = REQUIRED_MARKER.get(name)
        if name in listed and (not marker or marker in listed[name]):
            print(f"[{label}] MCP server '{name}' already configured.")
            continue
        action = "updated" if name in listed else "added"
        if name in listed and remove_cmd:
            run(remove_cmd(name))
        r = run(add_cmd(name, server))
        print(f"[{label}] {action} MCP server '{name}'." if r.returncode == 0
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
    register("agy", exe, lambda name, server: [exe, "mcp", "add", name, "--", *server],
             lambda name: [exe, "mcp", "remove", name])
    print("[agy] Chrome DevTools MCP attaches to your running Chrome: open chrome://inspect/#remote-debugging once,\n"
          "      turn on remote debugging, and click Allow when agy first connects.")


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
    sys.path.insert(0, str(REPO / "resume-builder"))
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
