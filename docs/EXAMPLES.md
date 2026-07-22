# Detailed Examples

Real-world scenarios with request/response pairs.

## Scenario 1: Record a Decision with Outcome Gate

### Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "record-decision",
    "arguments": {
      "problem": "P99 query latency exceeds 500ms SLA during peak traffic",
      "chosen_solution": "Add DuckDB materialized cache layer with hourly refresh",
      "rejected_alternatives": [
        "Upgrade to larger Redis cluster (cost prohibitive)",
        "Switch to ClickHouse (operational overhead too high)",
        "Implement distributed caching (added complexity)"
      ],
      "technologies": ["duckdb", "parquet", "arrow"],
      "domain": "data-engineering",
      "adr_ref": "docs/adr/adr-023-duckdb-caching.md",
      "predictions": [
        {
          "prediction_type": "LATENCY",
          "predicted_value": "p99 < 200ms with warm cache"
        },
        {
          "prediction_type": "COST",
          "predicted_value": "Storage < $50/month for 1TB snapshots"
        },
        {
          "prediction_type": "MAINTAINABILITY",
          "predicted_value": "< 2 hours for schema changes"
        }
      ]
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"decision_id\": \"DEC-2026-0042\",\n  \"prediction_ids\": [\n    \"PRD-2026-0051\",\n    \"PRD-2026-0052\",\n    \"PRD-2026-0053\"\n  ],\n  \"status\": \"OK\",\n  \"OUTCOME_GATE\": \"⚠️  3 prediction(s) from this session still lack outcomes: [PRD-2026-0051, PRD-2026-0052, PRD-2026-0053]. Record results via record-outcome before ending.\"\n}"
      }
    ]
  }
}
```

**Note**: The `OUTCOME_GATE` field reminds you to record outcomes for all 3 predictions later.

---

## Scenario 2: Query Prior Decisions

### Request: Search by Technology

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "query-decisions",
    "arguments": {
      "technology": "duckdb",
      "max_results": 5
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"results\": [\n    {\n      \"type\": \"decision\",\n      \"decision_id\": \"DEC-2026-0042\",\n      \"ts\": \"2026-07-22T14:30:45.123456\",\n      \"problem\": \"P99 query latency exceeds 500ms SLA\",\n      \"chosen_solution\": \"Add DuckDB materialized cache layer\",\n      \"rejected_alternatives\": [\"Redis cluster\", \"ClickHouse\", \"Distributed cache\"],\n      \"technologies\": [\"duckdb\", \"parquet\"],\n      \"status\": \"ACTIVE\",\n      \"domain\": \"data-engineering\",\n      \"adr_ref\": \"docs/adr/adr-023-duckdb-caching.md\"\n    },\n    {\n      \"type\": \"decision\",\n      \"decision_id\": \"DEC-2026-0038\",\n      \"ts\": \"2026-07-15T10:22:11.654321\",\n      \"problem\": \"Need fast aggregation on 100GB dataset\",\n      \"chosen_solution\": \"Use DuckDB for in-process OLAP\",\n      \"rejected_alternatives\": [\"Spark\", \"Pandas DataFrame\"],\n      \"technologies\": [\"duckdb\"],\n      \"status\": \"ACTIVE\",\n      \"domain\": \"data-engineering\",\n      \"adr_ref\": null\n    }\n  ],\n  \"OUTCOME_GATE\": \"⚠️  3 prediction(s) from this session still lack outcomes: [PRD-2026-0051, PRD-2026-0052, PRD-2026-0053]. Record results via record-outcome before ending.\"\n}"
      }
    ]
  }
}
```

**Interpretation**: Two decisions involving DuckDB. The OUTCOME_GATE still shows (from Scenario 1) because we haven't recorded outcomes yet.

---

## Scenario 3: Record Outcome (Closes Loop)

### Request

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "record-outcome",
    "arguments": {
      "prediction_id": "PRD-2026-0051",
      "actual_value": "p99 latency = 185ms (warm cache), 420ms (cold start)",
      "measurement_source": "MONITORING",
      "accuracy_score": 92
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"prediction_id\": \"PRD-2026-0051\",\n  \"validation_status\": \"SUCCESS\",\n  \"accuracy_score\": 92\n}"
      }
    ]
  }
}
```

**Note**: No OUTCOME_GATE (only this prediction was closed, 2 others pending). Success because accuracy ≥ 90.

---

## Scenario 4: Record Another Outcome (Partial Success)

### Request

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "tools/call",
  "params": {
    "name": "record-outcome",
    "arguments": {
      "prediction_id": "PRD-2026-0052",
      "actual_value": "Storage cost = $62/month (1.2TB, higher than expected)",
      "measurement_source": "MONITORING",
      "accuracy_score": 68
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"prediction_id\": \"PRD-2026-0052\",\n  \"validation_status\": \"PARTIAL_SUCCESS\",\n  \"accuracy_score\": 68,\n  \"lesson_recommended\": true,\n  \"lesson_hint\": \"Accuracy < 75%. Consider recording a lesson learned.\"\n}"
      }
    ]
  }
}
```

**Interpretation**:
- Accuracy 68 falls in PARTIAL_SUCCESS range (50-89)
- System recommends recording a lesson (cost was higher than predicted)
- Still 1 prediction pending → OUTCOME_GATE will appear on next query

---

## Scenario 5: Query After All Outcomes Recorded

### Request (after recording third outcome)

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "tools/call",
  "params": {
    "name": "query-decisions",
    "arguments": {
      "domain": "data-engineering",
      "max_results": 3
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"results\": [\n    {\n      \"type\": \"decision\",\n      \"decision_id\": \"DEC-2026-0042\",\n      \"ts\": \"2026-07-22T14:30:45.123456\",\n      \"problem\": \"P99 query latency exceeds 500ms SLA\",\n      \"chosen_solution\": \"Add DuckDB materialized cache layer\",\n      \"technologies\": [\"duckdb\", \"parquet\"],\n      \"status\": \"ACTIVE\",\n      \"domain\": \"data-engineering\"\n    }\n  ]\n}"
      }
    ]
  }
}
```

**Note**: No OUTCOME_GATE (all predictions from this session now have outcomes). Loop is closed. ✅

---

## Scenario 6: Technology Performance Report

### Command

```bash
python3 scripts/technology_performance_report.py
```

### Output

```
================================================================================
Technology Performance Registry
================================================================================

technology: duckdb           | successful_projects:  42 | failed_projects:   3 | total:  45 | average_accuracy:  89.1% | confidence: HIGH
technology: redis            | successful_projects:  28 | failed_projects:   8 | total:  36 | average_accuracy:  76.2% | confidence: HIGH
technology: elasticsearch    | successful_projects:   6 | failed_projects:   5 | total:  11 | average_accuracy:  52.3% | confidence: MEDIUM
technology: sqlite           | successful_projects:   4 | failed_projects:   0 | total:   4 | average_accuracy:  91.5% | confidence: LOW

================================================================================
Note: decisions count as 'successful' if >= 1 outcome SUCCESS and no FAILED
Confidence: LOW (<3 samples), MEDIUM (3-9), HIGH (>=10)
================================================================================
```

**Interpretation**:
- **DuckDB**: 89.1% average accuracy, HIGH confidence (42 successes, only 3 failures)
- **Redis**: 76.2% accuracy, but more failures than DuckDB (prefer DuckDB if similar use case)
- **Elasticsearch**: Only 52.3% accuracy, considered as backup only (52% ≈ coin flip)
- **SQLite**: 91.5% accuracy but LOW confidence (only 4 samples; more data needed)

**Decision**: For latency-critical decisions, prefer DuckDB (89.1%, 42 wins). For cost-sensitive, consider Redis if accuracy can tolerate 76%.

---

## Scenario 7: Error Handling (Decision Not Found)

### Request (with non-existent decision_id)

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "tools/call",
  "params": {
    "name": "record-prediction",
    "arguments": {
      "decision_id": "DEC-2026-9999",
      "prediction_type": "LATENCY",
      "predicted_value": "p99 < 100ms"
    }
  }
}
```

### Response

```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"error\": \"decision_id not found: DEC-2026-9999\"}"
      }
    ]
  }
}
```

**Handling**: Check that decision_id was recorded first (use query-decisions to verify).

---

## Common Patterns

### Pattern 1: Decision → Prediction → Outcome in Single Session

```
1. record-decision (returns DEC-2026-0042, [PRD-2026-0051, ...])
2. ... time passes, measurement happens ...
3. record-outcome (for each prediction)
4. query-decisions or exit (OUTCOME_GATE shows in step 2-3)
```

### Pattern 2: Decision Only (No Predictions Yet)

```
1. record-decision (with empty predictions=[])
2. Later: record-prediction (link new predictions)
3. Later: record-outcome
```

### Pattern 3: Technology Analysis Before Decision

```
1. query-decisions (technology="duckdb") → see prior decisions
2. Check performance registry
3. If accuracy is high, choose DuckDB
4. record-decision (chosen_solution="duckdb", ...)
```

### Pattern 4: Post-Incident Learning

```
1. Incident happened, latency spiked
2. record-decision (problem="latency spike", chosen_solution="rollback to V2")
3. record-outcome (actual_value="spike ended in 3min", accuracy_score=5)
4. Learn: V3 has issues, don't use this approach
```
