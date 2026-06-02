# Jira MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

**Minimal, secure Jira MCP server with project-level configuration.** ~200 lines, 3 dependencies, zero third-party Jira wrappers. Fully auditable.

Works with **Claude Code**, **Kiro**, **Cursor**, **Windsurf**, **Codex**, **GitHub Copilot**, and any MCP-compatible AI coding agent.

## Why This Exists

Most Jira MCP servers use third-party wrappers with unknown code. This server:

- **~200 lines total** — read every line in 5 minutes
- **3 dependencies** — `mcp` (Anthropic), `httpx`, `python-dotenv`
- **Zero external calls** — only connects to your Jira instance
- **Project-level config** — different Jira instances per project via env vars
- **No telemetry, no analytics, no SaaS dependency**

## Tools (19)

| Category | Tool | Description |
|----------|------|-------------|
| **Search** | `jira_search` | Search issues using JQL (auto-scoped to project) |
| | `jira_my_issues` | Get my assigned/created/watched issues |
| | `jira_sprint_issues` | Get active sprint board |
| **Issues** | `jira_get_issue` | Get full issue details with comments |
| | `jira_create_issue` | Create a new issue (Task, Bug, Story) |
| | `jira_update_issue` | Update summary, description, priority, labels |
| **Workflow** | `jira_transition` | Change status (In Progress, Done, etc.) |
| | `jira_get_transitions` | List available transitions for an issue |
| **Comments** | `jira_add_comment` | Add a comment (ADF format) |
| | `jira_list_comments` | List all comments on an issue |
| | `jira_delete_comment` | Delete a comment |
| **Attachments** | `jira_attach_file` | Upload a file to an issue |
| | `jira_list_attachments` | List all attachments on an issue |
| | `jira_delete_attachment` | Delete an attachment |
| **People** | `jira_assign` | Assign issue to a user |
| | `jira_list_users` | Search users by name/email |
| **Links** | `jira_link_issues` | Link two issues (Blocks, Relates, Duplicate) |
| **Project** | `jira_get_project_info` | Get project details and issue types |
| **Time** | `jira_log_work` | Log work/time on an issue |

## Quick Start

### 1. Get API Token (Free)

Go to https://id.atlassian.com/manage-profile/security/api-tokens → Create API token

### 2. Install

```bash
git clone https://github.com/rishapgandhi/jira_mcp.git
cd jira_mcp
pip install -e .
```

### 3. Configure Per Project

Create `.kiro/mcp.json` in your project folder:

```json
{
  "mcpServers": {
    "jira": {
      "command": "python3",
      "args": ["-m", "src.server"],
      "cwd": "/path/to/jira_mcp",
      "env": {
        "JIRA_BASE_URL": "https://yourcompany.atlassian.net",
        "JIRA_EMAIL": "you@company.com",
        "JIRA_API_TOKEN": "your-api-token",
        "JIRA_PROJECT_KEY": "PROJ"
      }
    }
  }
}
```

### 4. Multiple Projects

```
project-a/.kiro/mcp.json  → JIRA_PROJECT_KEY=PA, company-a.atlassian.net
project-b/.kiro/mcp.json  → JIRA_PROJECT_KEY=PB, company-b.atlassian.net
project-c/.kiro/mcp.json  → JIRA_PROJECT_KEY=PC, client.atlassian.net
```

Same server code, different config per project. Each project connects to its own Jira board.

### Claude Code
```bash
claude mcp add jira -- python3 -m src.server --cwd /path/to/jira_mcp
```

### Cursor / Windsurf
Add to `.cursor/mcp.json` or `.windsurf/mcp.json` with same format as above.

## Security

| Aspect | Implementation |
|--------|---------------|
| Dependencies | 3 packages, all well-known |
| Network | Only connects to YOUR Jira instance |
| Credentials | API token via env vars (never stored in code) |
| Code | ~200 lines, fully auditable |
| Telemetry | None |
| Data flow | Your machine → Your Jira instance |

## Dependencies

| Package | Purpose |
|---------|---------|
| `mcp` | MCP protocol SDK (Anthropic) |
| `httpx` | HTTP client for Jira REST API |
| `python-dotenv` | .env file loading |

## Project Structure

```
jira_mcp/
├── pyproject.toml
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── src/
    ├── server.py      # MCP server (stdio transport)
    ├── client.py      # Jira API client (httpx + basic auth)
    └── tools/
        └── issues.py  # 9 tools: search, CRUD, transitions, sprint
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_BASE_URL` | Yes | `https://yourcompany.atlassian.net` |
| `JIRA_EMAIL` | Yes | Your Jira login email |
| `JIRA_API_TOKEN` | Yes | API token from Atlassian |
| `JIRA_PROJECT_KEY` | No | Scopes all queries to this project (e.g. `PV`) |

## Contributing

PRs welcome. Keep it minimal — the goal is a small, auditable codebase.

## License

[MIT](LICENSE) — use commercially, fork, modify, redistribute freely.
