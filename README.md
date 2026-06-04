# thatvid

Claude Code workspace.

## MCP servers

### Chrome DevTools MCP

This project is configured with the official [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)
server via [`.mcp.json`](.mcp.json). It lets Claude control and inspect a live
Chrome browser — navigate pages, click/fill, capture screenshots, read the DOM
and console, run performance traces, and inspect network requests.

It is configured with `--isolated=true`, so each run uses a fresh temporary
profile that is cleaned up on exit — it never touches your day-to-day Chrome
profile. Drop that flag from `.mcp.json` if you'd rather reuse your real profile
(e.g. to stay logged in to sites).

**Requirements**

- Node.js LTS (the server runs via `npx`)
- A current stable Chrome installed locally

**Usage**

Project-scoped MCP servers in `.mcp.json` are loaded automatically by Claude
Code. The first time, Claude Code will prompt you to approve the server; run
`/mcp` to check its status. On first launch `npx` downloads
`chrome-devtools-mcp@latest`, then it connects to (or launches) Chrome.

**Common options**

Add flags to the `args` array in `.mcp.json` to customize behavior, e.g.:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--channel=stable",
        "--headless=true",
        "--isolated=true"
      ]
    }
  }
}
```

| Flag | Purpose |
| --- | --- |
| `--headless=true` | Run Chrome without a visible window |
| `--isolated=true` | Use a temporary profile that is cleaned up on exit |
| `--channel=<stable\|beta\|dev\|canary>` | Pick the Chrome channel to launch |
| `--executablePath=<path>` | Use a specific Chrome binary |
| `--browserUrl=<url>` | Attach to an already-running Chrome (e.g. `http://127.0.0.1:9222`) |
| `--viewport=<WxH>` | Set the initial viewport (e.g. `1280x720`) |

See the [upstream documentation](https://github.com/ChromeDevTools/chrome-devtools-mcp)
for the full tool and flag reference.
