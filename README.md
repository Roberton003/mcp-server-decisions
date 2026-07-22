# MCP Server: Decisions 🏗️

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Architectural decision tracking with prediction validation and outcome gates.

## Why This Exists

Most systems that recommend decisions forget to check whether those decisions actually worked. This server closes that loop: **decide → predict → measure → validate**.

When an agent or human makes a decision, they can record predictions about what will happen (latency, cost, scalability, reliability, etc.). When results are in, outcomes are recorded. The server automatically validates predictions against reality and flags decisions whose accuracy was poor, so you learn over time what works and what doesn't.

The tool is shipped with an **Outcome Gate** pattern embedded in responses — pending predictions from the current session are surfaced directly in tool outputs, raising the organic closure rate of the decision-outcome loop without external reminders or discipline.

## What It Does

Four MCP tools:

- **`record-decision`** — Register a technical decision (problem, chosen solution, rejected alternatives, technologies involved)
- **`record-prediction`** — Link a measurable prediction to a decision (latency, cost, scalability, etc.)
- **`record-outcome`** — Close the loop with observed results and accuracy score (0–100)
- **`query-decisions`** — Search prior decisions by keyword, technology, or domain

All entries are stored in a single append-only JSONL log. No database migration, no schema versioning — portable, inspectable, diff-able.

## The Outcome Gate Pattern

The Outcome Gate pattern solves a real problem: **decision loops leak**. A classic flow is:

```
Agent: "I'll use DuckDB for this cache."
System: "OK, DuckDB chosen. Here's the plan."
[Time passes. Latency measured. Accuracy known.]
Agent: "Wait, did we ever check if DuckDB was actually fast?"
System: "No one asked me to."
```

Instead, every call to `query-decisions` or `record-decision` includes an `OUTCOME_GATE` field in the response if predictions from this session lack outcomes:

```json
{
  "decision_id": "DEC-2026-0001",
  "status": "OK",
  "OUTCOME_GATE": "⚠️  2 prediction(s) from this session still lack outcomes: [PRD-2026-0001, PRD-2026-0002]. Record results via record-outcome before ending."
}
```

No external reminders, no hope that the agent will remember — the nudge is **right there** in the tool response, close to where decisions are made.

Validated on a sibling internal tool: 3.8% → 14.5% organic closure rate when outcome nudges are in-band vs. external.

See [`docs/OUTCOME-GATE-PATTERN.md`](docs/OUTCOME-GATE-PATTERN.md) for the generalized pattern and how to apply it to other feedback loops.

## Architecture

- **Log storage**: Single JSONL file (append-only, no migrations, zero dependencies)
- **ID generation**: Sequential per year (DEC-2026-0001, PRD-2026-0002, etc.)
- **Outcome validation**: Automatic accuracy_score mapping (≥90 SUCCESS, 50–89 PARTIAL_SUCCESS, <50 FAILED)
- **Technology performance**: Aggregated registry of success/failure rates by technology (see below)

## Tech Stack

- Python 3.10+ (stdlib only — no runtime dependencies)
- MCP (Model Context Protocol) — JSON-RPC 2.0 over stdin/stdout
- JSONL for portable, inspectable storage

## Installation

### As an MCP server (via Claude or compatible client)

Add to your MCP client configuration:

```json
{
  "type": "stdio",
  "command": "python3",
  "args": ["-m", "server"],
  "env": {
    "MCP_DECISIONS_LOG_PATH": "~/.local/share/mcp-decisions/decisions_log.json"
  }
}
```

Or install via pip:

```bash
pip install mcp-server-decisions
# Then in config:
{
  "type": "stdio",
  "command": "mcp-server-decisions"
}
```

### Local usage

```bash
python3 server.py --selftest
```

## Usage Examples

### Record a decision

```python
# Via MCP client or cURL:
# POST to the MCP server with method=tools/call

record-decision(
  problem="Query latency exceeds SLA (p99 > 500ms)",
  chosen_solution="Cache with DuckDB + Parquet snapshots",
  rejected_alternatives=["Redis cluster", "Elasticsearch", "MemSQL"],
  technologies=["duckdb", "parquet", "arrow"],
  domain="data-engineering",
  predictions=[
    {
      "prediction_type": "LATENCY",
      "predicted_value": "p99 < 200ms with <2% memory overhead"
    },
    {
      "prediction_type": "COST",
      "predicted_value": "storage cost < $50/month at 1TB"
    }
  ]
)
# Returns: {"decision_id": "DEC-2026-0001", "prediction_ids": ["PRD-2026-0001", "PRD-2026-0002"], "status": "OK"}
```

### Record an outcome

```python
record-outcome(
  prediction_id="PRD-2026-0001",
  actual_value="p99 = 180ms, memory overhead = 1.2%",
  measurement_source="MONITORING",
  accuracy_score=95
)
# Returns: {"validation_status": "SUCCESS", "accuracy_score": 95}
```

### Query prior decisions

```python
query-decisions(
  technology="duckdb",
  max_results=5
)
# Returns all decisions involving DuckDB, sorted by recency
```

## Technology Performance Registry

Run the performance aggregator:

```bash
python3 scripts/technology_performance_report.py
```

Example output:

```
================================================================================
Technology Performance Registry
================================================================================

technology: duckdb            | successful_projects:  12 | failed_projects:   1 | total:  13 | average_accuracy:  91.2% | confidence: HIGH
technology: redis            | successful_projects:   8 | failed_projects:   3 | total:  11 | average_accuracy:  78.3% | confidence: MEDIUM
technology: elasticsearch    | successful_projects:   2 | failed_projects:   4 | total:   6 | average_accuracy:  52.1% | confidence: MEDIUM

================================================================================
Note: decisions count as 'successful' if >= 1 outcome SUCCESS and no FAILED
Confidence: LOW (<3 samples), MEDIUM (3-9), HIGH (>=10)
================================================================================
```

Use this before recommending a technology — if average_accuracy is low or confidence is LOW, gather more data or reconsider alternatives.

## Development

### Run self-tests

```bash
python3 server.py --selftest
```

All tests pass on clean state with zero external dependencies. The test covers:
- Decision recording
- Prediction linking
- Outcome validation with accuracy scoring
- Query filtering

### Testing via MCP client

If you have `mcp-cli` installed:

```bash
mcp-cli -- python3 server.py
# Then send JSON-RPC 2.0 messages via stdin
```

## Environment Variables

- `MCP_DECISIONS_LOG_PATH` — Override the default log file location (default: `~/.local/share/mcp-decisions/decisions_log.json`)

## License

MIT — See [LICENSE](LICENSE)
