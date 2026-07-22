# Client Integrations

`mcp-server-decisions` is a generic MCP server compatible with any MCP-supporting client. Configuration varies by platform.

## Claude (claude.ai / Claude Code)

### Via ~/.claude.json

```json
{
  "mcp-server-decisions": {
    "type": "stdio",
    "command": "mcp-server-decisions"
  }
}
```

### Via Environment Variable

```bash
export MCP_DECISIONS_LOG_PATH="/custom/path/decisions_log.json"
mcp-server-decisions
```

## OpenCode Harness

OpenCode uses JSONC config format with additional fields (timeout, env vars).

### In opencode.jsonc

```jsonc
{
  "mcpServers": {
    "decisions": {
      "type": "local",  // OpenCode-specific: "local" = stdio via bash wrapper
      "command": "bash",
      "args": ["-c", "python3 -u ~/.local/lib/python*/site-packages/server.py"],
      "timeout": 30000,  // 30s timeout for tool calls
      "env": {
        "MCP_DECISIONS_LOG_PATH": "~/.local/share/mcp-decisions/decisions_log.json"
      }
    }
  }
}
```

Or use the entry point directly:

```jsonc
{
  "mcpServers": {
    "decisions": {
      "type": "local",
      "command": "mcp-server-decisions",
      "timeout": 30000
    }
  }
}
```

## Codex

Codex uses a similar stdio-based configuration but may register MCPs differently depending on version.

### Codex Config (if supported)

```json
{
  "agents": {
    "default": {
      "mcp_servers": {
        "decisions": {
          "type": "stdio",
          "command": "python3",
          "args": ["-m", "server"]
        }
      }
    }
  }
}
```

Check Codex documentation for current MCP registration format.

## Antigravity (GEMINI.md)

Antigravity (Roberto's harness) registers MCPs via GEMINI.md or local skill configuration.

### In GEMINI.md

```yaml
mcp:
  decisions:
    type: stdio
    command: mcp-server-decisions
    # Optional: override log path
    env:
      MCP_DECISIONS_LOG_PATH: ~/.local/share/mcp-decisions/decisions_log.json
```

Or as a registered skill:

```bash
cd ~/.config/opencode/skills
mkdir -p mcp-server-decisions
# Copy server.py here or link to pip-installed version
```

## Generic MCP Clients

Any client supporting MCP (JSON-RPC 2.0 over stdin/stdout) can use this server:

1. **Start the server:**
   ```bash
   mcp-server-decisions
   ```

2. **Send JSON-RPC requests:**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/list"
   }
   ```

3. **Receive responses:**
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "tools": [...]
     }
   }
   ```

## Installation Methods

### 1. Via pip (Recommended for Most Clients)

```bash
pip install mcp-server-decisions
```

Creates entry point `mcp-server-decisions` available globally.

**Best for**: Claude, generic clients, shared environments

### 2. Via Local Path (Development)

```bash
git clone https://github.com/Roberton003/mcp-server-decisions.git
cd mcp-server-decisions
pip install -e .
```

**Best for**: OpenCode (local harness), Antigravity, development

### 3. Via uvx (Temporary, No Install)

```bash
uvx mcp-server-decisions
```

**Best for**: One-off testing, CI/CD, sandbox environments

### 4. Direct Python (Debug)

```bash
python3 /path/to/server.py
```

**Best for**: Troubleshooting, custom integration, local development

## Endpoint Discovery

If your client requires explicit endpoint discovery:

- **Protocol**: JSON-RPC 2.0
- **Transport**: stdio (stdin/stdout)
- **Initialization method**: `initialize`
- **Tool discovery method**: `tools/list`
- **Tool invocation method**: `tools/call`

## Troubleshooting Integration Issues

### "mcp-server-decisions: command not found"

The entry point wasn't created. Try:

```bash
pip install --upgrade mcp-server-decisions
which mcp-server-decisions  # Should return a path
```

### "Connection refused" or "Pipe broken"

The server process exited unexpectedly. Check:

```bash
mcp-server-decisions --selftest
# If selftest fails, there's a bug in the server
```

### "Tool call timeout"

Increase timeout in client config (e.g., `timeout: 60000` for 60s).

### "Log file not found"

Verify `MCP_DECISIONS_LOG_PATH`:

```bash
echo $MCP_DECISIONS_LOG_PATH
# Or check default:
ls ~/.local/share/mcp-decisions/
```

## Multi-Client Setup

To use the same decisions log across multiple clients:

1. **Set a fixed path:**
   ```bash
   export MCP_DECISIONS_LOG_PATH="/shared/path/decisions_log.json"
   ```

2. **Configure each client to use the same `MCP_DECISIONS_LOG_PATH`**

3. **Ensure file permissions allow concurrent reads:**
   ```bash
   chmod 644 /shared/path/decisions_log.json
   ```

**Warning**: JSONL append-only is safe for concurrent writes, but reads may see partial updates. For consistent reads, consider sequential access or brief pauses between tool calls.

---

**Not seeing your client?** [Open an issue](https://github.com/Roberton003/mcp-server-decisions/issues) with your MCP client name and config format.
