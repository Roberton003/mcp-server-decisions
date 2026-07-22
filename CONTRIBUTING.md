# Contributing

Thank you for your interest in improving mcp-server-decisions.

## Development

### Running locally

```bash
python3 server.py --selftest
```

### Testing with MCP client

```bash
# Direct invocation
python3 server.py

# Or via installed entry point
mcp-server-decisions
```

## Workflow

1. **Fork** the repository
2. **Create a feature branch** (`git checkout -b feature/your-feature`)
3. **Make changes** — keep commits minimal and well-described
4. **Test** — ensure `python3 server.py --selftest` still passes
5. **Push** and create a **pull request** with a clear description

## Code Style

- No external dependencies (stdlib only)
- Type hints for function signatures
- Minimal comments (code should be self-documenting)
- One-line docstrings preferred

## Reporting Issues

Open an issue with:
- Clear title
- Reproduction steps (if applicable)
- Expected vs. actual behavior
- Python version and OS

## License

All contributions are licensed under the MIT License.
