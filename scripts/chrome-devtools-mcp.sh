#!/usr/bin/env bash
#
# Environment-aware launcher for the Chrome DevTools MCP server.
#
# Local desktop:   launch a visible, isolated Chrome (system install).
# Claude Code cloud / headless root container: launch headless Chrome with
#   --no-sandbox (required as root), a self-installed Chrome-for-Testing
#   binary, and lax TLS so TLS-intercepting proxies don't break CDN loads.
#
# Detection uses CLAUDE_CODE_REMOTE, which Claude Code sets in cloud/web
# sessions. Force the headless path anywhere by setting
# CHROME_DEVTOOLS_MCP_HEADLESS=1.
set -euo pipefail

ARGS=(--isolated)

if [ -n "${CLAUDE_CODE_REMOTE:-}" ] || [ -n "${CHROME_DEVTOOLS_MCP_HEADLESS:-}" ]; then
  CHROME_BIN="${CDT_CHROME_BIN:-$HOME/.cache/chrome-devtools-mcp/chrome-bin}"
  ARGS+=(--headless
         --acceptInsecureCerts
         --chrome-arg=--no-sandbox
         --chrome-arg=--disable-setuid-sandbox
         --chrome-arg=--disable-dev-shm-usage)
  [ -x "$CHROME_BIN" ] && ARGS+=(--executablePath="$CHROME_BIN")
fi

exec npx -y chrome-devtools-mcp@latest "${ARGS[@]}" "$@"
