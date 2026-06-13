#!/usr/bin/env bash
#
# Ensure a Chrome binary is available for chrome-devtools-mcp.
#
# Local machines: nothing to do — the system Chrome is used.
# Claude Code cloud sessions: the container is ephemeral and Google's apt/deb
# download hosts are blocked, so we fetch Chrome-for-Testing via puppeteer
# (its CDN is reachable) and expose it at a stable symlink that the MCP
# launcher points to with --executablePath.
#
# Idempotent: safe to run on every SessionStart. Only downloads when running
# in a Claude Code remote/cloud session and no linked Chrome exists yet.
set -euo pipefail

STABLE_LINK="${CDT_CHROME_BIN:-$HOME/.cache/chrome-devtools-mcp/chrome-bin}"

# Already linked from a previous run in this container.
if [ -x "$STABLE_LINK" ]; then
  echo "chrome-for-mcp: present at $STABLE_LINK"
  exit 0
fi

# Outside the cloud we rely on the user's system Chrome — never auto-download.
if [ -z "${CLAUDE_CODE_REMOTE:-}${CHROME_DEVTOOLS_MCP_HEADLESS:-}" ]; then
  echo "chrome-for-mcp: local environment, using system Chrome"
  exit 0
fi

echo "chrome-for-mcp: installing Chrome-for-Testing via puppeteer..."
npx -y puppeteer browsers install chrome >/tmp/cdt-chrome-install.log 2>&1 || {
  echo "chrome-for-mcp: install failed; see /tmp/cdt-chrome-install.log" >&2
  exit 1
}

# Resolve the newest installed binary.
BIN="$(ls -1 "$HOME"/.cache/puppeteer/chrome/*/chrome-linux64/chrome 2>/dev/null | sort -V | tail -1 || true)"
if [ -z "${BIN:-}" ] || [ ! -x "$BIN" ]; then
  echo "chrome-for-mcp: could not locate installed Chrome binary" >&2
  exit 1
fi

mkdir -p "$(dirname "$STABLE_LINK")"
ln -sf "$BIN" "$STABLE_LINK"
echo "chrome-for-mcp: linked $STABLE_LINK -> $BIN"
