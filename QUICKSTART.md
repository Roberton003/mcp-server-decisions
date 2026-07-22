# Quick Start

## 5-Minute Setup

### 1. Install

```bash
pip install mcp-server-decisions
```

### 2. Configure (Claude or compatible client)

Add to your MCP client configuration:

```json
{
  "mcp-server-decisions": {
    "type": "stdio",
    "command": "mcp-server-decisions"
  }
}
```

Or if using a non-standard log location:

```json
{
  "mcp-server-decisions": {
    "type": "stdio",
    "command": "mcp-server-decisions",
    "env": {
      "MCP_DECISIONS_LOG_PATH": "/path/to/decisions_log.json"
    }
  }
}
```

### 3. Record your first decision

Ask your agent to:

> Record this decision: we're using DuckDB for query caching because it's fast, portable, and requires no external infrastructure. Alternatives we considered: Redis, Elasticsearch, SQLite. Predict that p99 latency will drop below 200ms.

The agent will call:
```
record-decision(
  problem="Query latency exceeds SLA",
  chosen_solution="DuckDB for query caching",
  rejected_alternatives=["Redis", "Elasticsearch", "SQLite"],
  technologies=["duckdb"],
  predictions=[{"prediction_type": "LATENCY", "predicted_value": "p99 < 200ms"}]
)
```

### 4. Later: Record the outcome

Once you've measured results:

> We measured query latency at p99=180ms with DuckDB. Record this outcome for the latency prediction.

The agent calls:
```
record-outcome(
  prediction_id="PRD-2026-0001",
  actual_value="p99 = 180ms",
  measurement_source="MONITORING",
  accuracy_score=95
)
```

### 5. Generate performance report

```bash
python3 -m pip install mcp-server-decisions
python3 -c "from scripts.technology_performance_report import main; exit(main())"
```

Or if installed separately:

```bash
technology-performance-report
```

## What Happens Next

- Decisions are logged in JSONL format (queryable, inspectable, versionable)
- Predictions are linked to decisions automatically
- Outcomes update the accuracy score
- Technology Performance Registry aggregates success rates by technology
- **Outcome Gate nudges** appear in tool responses if you have open predictions, keeping the loop on track

## Common Flows

### Check if a technology has worked before

```
query-decisions(technology="duckdb")
```

Returns all decisions involving DuckDB, sorted by recency. See average accuracy in the Technology Performance Registry.

### Find decisions in a specific domain

```
query-decisions(domain="data-engineering", max_results=10)
```

### Search by problem keyword

```
query-decisions(keyword="latency", max_results=5)
```

## Troubleshooting

**Log file not found**

Check `MCP_DECISIONS_LOG_PATH` env var. Default: `~/.local/share/mcp-decisions/decisions_log.json`

**Entry point not working**

Ensure pip-installed version: `which mcp-server-decisions` should return a path. If not:

```bash
pip install -e .
```

**Outcome not recording**

Verify the `prediction_id` matches a prediction from `record-decision` or `record-prediction`. Check the JSONL log:

```bash
grep prediction_id ~/.local/share/mcp-decisions/decisions_log.json | tail
```

## Next Steps

- Read [`docs/OUTCOME-GATE-PATTERN.md`](docs/OUTCOME-GATE-PATTERN.md) for the design philosophy
- See [`README.md`](README.md) for full tool reference
- Open an issue if something breaks
