# MCP Server: Decisions

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-Roberton003%2Fmcp--server--decisions-black?logo=github)](https://github.com/Roberton003/mcp-server-decisions)

**Architectural decision tracking with prediction validation and outcome gates.**<br />
Record decisions, make testable predictions, measure outcomes, and learn from every choice.
Whether you're an AI agent, a team lead, or building decision-critical systems — close the feedback loop.

Decisions are stored in a portable append-only JSONL log. No database, no migrations, zero external dependencies.

## Key Features

- **Decision Recording** — Capture architectural choices with problem, solution, alternatives, and technologies involved
- **Prediction Linking** — Make testable claims (latency, cost, scalability, reliability, etc.) tied to decisions
- **Outcome Validation** — Record measured results and automatically calculate accuracy (0-100 scale)
- **Technology Performance Registry** — Aggregate success rates and confidence metrics by technology
- **Outcome Gate Pattern** — In-band nudges in tool responses keep decision loops from leaking (3.8% → 14.5% closure rate)
- **Zero Dependencies** — Stdlib-only Python, append-only JSONL storage, fully portable

## Example Usage

### Record a decision

```bash
# Via MCP client (Claude, etc.) — agent calls this:
record-decision(
  problem="Query latency exceeds SLA (p99 > 500ms)",
  chosen_solution="DuckDB + Parquet caching",
  rejected_alternatives=["Redis", "Elasticsearch"],
  technologies=["duckdb", "parquet"],
  predictions=[
    {"prediction_type": "LATENCY", "predicted_value": "p99 < 200ms"},
    {"prediction_type": "COST", "predicted_value": "< $50/month"}
  ]
)
# Returns: DEC-2026-0001, PRD-2026-0001, PRD-2026-0002
```

### Record an outcome later

```bash
record-outcome(
  prediction_id="PRD-2026-0001",
  actual_value="p99 = 180ms",
  measurement_source="MONITORING",
  accuracy_score=95
)
# Returns: SUCCESS ✅, 95% accuracy
```

### Query prior decisions

```bash
# Did DuckDB work before?
query-decisions(technology="duckdb", max_results=5)
# Returns all decisions involving DuckDB, sorted by recency
```

### Technology Performance Report

```bash
python3 scripts/technology_performance_report.py
# Output:
# technology: duckdb  | successful: 12 | failed: 1 | avg_accuracy: 91.2% | confidence: HIGH
```

## Installation

1. **Install Python 3.10+**

2. **Clone or download the repository**
   ```bash
   git clone https://github.com/Roberton003/mcp-server-decisions.git
   cd mcp-server-decisions
   ```

3. **Install the package**
   ```bash
   pip install -e .
   ```

4. **Run self-tests**
   ```bash
   python3 server.py --selftest
   # ✅ All self-tests passed
   ```

## Running the Project

### As an MCP Server (Claude or Compatible Client)

Add to your MCP client configuration:

```json
{
  "mcp-server-decisions": {
    "type": "stdio",
    "command": "mcp-server-decisions"
  }
}
```

### Standalone Usage

```bash
# Run the MCP server directly
mcp-server-decisions

# Or via Python
python3 server.py
```

## How It Works

### The Loop

```
Decide → Predict → Implement → Measure → Validate → Learn → Next Decision
```

1. **Record a decision** — Store the problem, chosen solution, alternatives, and technologies
2. **Make predictions** — Attach testable claims (latency, cost, reliability, etc.)
3. **Implement** — Build the system
4. **Measure results** — Capture actual values from monitoring, logs, benchmarks
5. **Validate** — The server calculates accuracy (0-100) and validation status (SUCCESS / PARTIAL_SUCCESS / FAILED)
6. **Learn** — Review what worked via the Technology Performance Registry
7. **Next decision** — Query past decisions before making new recommendations

### The Outcome Gate Pattern

Decision loops leak because predictions aren't validated. This server embeds a reminder directly in tool responses:

**Without Outcome Gate:**
- Decision is made → implementation starts → results come in → nobody checks if prediction was right

**With Outcome Gate:**
```json
{
  "decision_id": "DEC-2026-0001",
  "status": "OK",
  "OUTCOME_GATE": "⚠️  2 prediction(s) from this session still lack outcomes: [PRD-2026-0001, PRD-2026-0002]. Record results via record-outcome before ending."
}
```

The nudge is in-band (inside the tool response), where agents are already looking. Result: **3.8% → 14.5% closure rate** improvement (validated on internal tool).

For the full pattern explanation, see [`docs/OUTCOME-GATE-PATTERN.md`](docs/OUTCOME-GATE-PATTERN.md).

## Architecture

- **Storage**: Single append-only JSONL file (no schema, no migrations, fully portable)
- **IDs**: Sequential per year (DEC-2026-0001, PRD-2026-0002, etc.)
- **Accuracy**: Automatic mapping (≥90 SUCCESS, 50–89 PARTIAL_SUCCESS, <50 FAILED)
- **Performance**: O(n) queries on small logs, easily indexed for large ones

## Tech Stack

- **Python 3.10+** — stdlib only, zero runtime dependencies
- **MCP** — Model Context Protocol (JSON-RPC 2.0 over stdin/stdout)
- **JSONL** — Portable, inspectable, git-friendly log format

## Environment Variables

- `MCP_DECISIONS_LOG_PATH` — Override the default log file location
  - Default: `~/.local/share/mcp-decisions/decisions_log.json`

## Documentation

- **[Quick Start](QUICKSTART.md)** — 5-minute setup guide
- **[Contributing](CONTRIBUTING.md)** — How to contribute
- **[Outcome Gate Pattern](docs/OUTCOME-GATE-PATTERN.md)** — Design philosophy and generalized recipe
- **[Wiki](https://github.com/Roberton003/mcp-server-decisions/wiki)** — FAQ and advanced topics

## Development

### Run Tests

```bash
python3 server.py --selftest
```

All tests pass on clean state with zero external dependencies.

### Contributing

We welcome pull requests. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- ✅ Core decision/prediction/outcome tracking
- ✅ Outcome Gate in-band nudges
- ✅ Technology Performance Registry
- 🔄 Web UI for browsing decisions
- 🔄 Webhooks for outcome notifications
- 🔄 Decision templates and patterns

## Disclaimer

This project is community-built and independent. It is not affiliated with any organization or standard-setting body. The Outcome Gate pattern is a general-purpose design that can be applied to any feedback loop.

## Support

- 🐛 [Report Issues](https://github.com/Roberton003/mcp-server-decisions/issues)
- 💬 [Discuss Ideas](https://github.com/Roberton003/mcp-server-decisions/discussions)
- 📖 [Read the Docs](https://github.com/Roberton003/mcp-server-decisions/wiki)

## License

MIT © 2026 Roberton003 — See [LICENSE](LICENSE)

---

**Made for AI agents. Built for teams. Learn from every decision.**
