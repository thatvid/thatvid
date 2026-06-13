# thatvid

Claude Code workspace.

## MCP servers

### Chrome DevTools MCP

This project is configured with the official [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
server. It lets Claude control and inspect a live Chrome browser — navigate
pages, click/fill, capture screenshots, read the DOM and console, run
performance traces, and inspect network requests.

The setup works **automatically in both local and Claude Code cloud/web
sessions**, with no manual steps:

| Piece | What it does |
| --- | --- |
| [`.mcp.json`](.mcp.json) | Registers the `chrome-devtools` server, launched via the wrapper script below. |
| [`scripts/chrome-devtools-mcp.sh`](scripts/chrome-devtools-mcp.sh) | Env-aware launcher. Picks the right Chrome flags for where it's running. |
| [`scripts/install-chrome.sh`](scripts/install-chrome.sh) | Ensures a Chrome binary exists (used by the SessionStart hook). |
| [`.claude/settings.json`](.claude/settings.json) | `SessionStart` hook that runs the installer each session. |

**How it adapts**

- **Local desktop** — launches a *visible, isolated* Chrome using your system
  install. A real browser window opens so you can watch it work. Each run uses a
  fresh temporary profile (`--isolated`), so it never touches your day-to-day
  Chrome profile.
- **Claude Code cloud / web** — the container is ephemeral, headless, and runs
  as root, and Google's Chrome download hosts are blocked. So the SessionStart
  hook fetches Chrome-for-Testing via puppeteer (an allowed CDN) and the
  launcher runs Chrome headless with `--no-sandbox` and `--acceptInsecureCerts`
  (the last so a TLS-intercepting proxy doesn't break CDN script loads).

Detection is via the `CLAUDE_CODE_REMOTE` environment variable, which Claude
Code sets in cloud sessions. Force the headless/cloud path anywhere by setting
`CHROME_DEVTOOLS_MCP_HEADLESS=1`.

**Requirements**

- Node.js LTS (everything runs via `npx`)
- Locally: a current stable Chrome installed. (Cloud sessions self-install.)

**Usage**

Project-scoped MCP servers load automatically. The first time, Claude Code
prompts you to approve the `chrome-devtools` server; run `/mcp` to check its
status. Then just ask in natural language, e.g. *"open example.com, screenshot
it, and show me any console errors."*

**Using it everywhere (all projects)**

This setup is per-repo. To get Chrome DevTools MCP in **every** project:

- **Local, all projects:** add the same `chrome-devtools` entry to your
  user-level `~/.claude/settings.json` `mcpServers` (a global server applies
  everywhere on your machine).
- **Cloud, all repos:** add `bash scripts/install-chrome.sh`'s logic to your
  environment's setup script in the Claude Code web UI, or copy these four files
  into each repo.

**Customizing**

Chrome flags live in [`scripts/chrome-devtools-mcp.sh`](scripts/chrome-devtools-mcp.sh)
(not `.mcp.json`). Useful knobs from the upstream CLI:

| Flag | Purpose |
| --- | --- |
| `--headless` | Run Chrome without a visible window |
| `--isolated` | Use a temporary profile that is cleaned up on exit |
| `--channel=<stable\|beta\|dev\|canary>` | Pick the Chrome channel to launch |
| `--executablePath=<path>` | Use a specific Chrome binary |
| `--chrome-arg=<arg>` | Pass an arbitrary flag through to Chrome (e.g. `--no-sandbox`) |
| `--acceptInsecureCerts` | Ignore TLS cert errors (useful behind proxies) |
| `--browserUrl=<url>` | Attach to an already-running Chrome (e.g. `http://127.0.0.1:9222`) |
| `--viewport=<WxH>` | Set the initial viewport (e.g. `1280x720`) |

See the [upstream documentation](https://github.com/ChromeDevTools/chrome-devtools-mcp)
for the full tool and flag reference.
