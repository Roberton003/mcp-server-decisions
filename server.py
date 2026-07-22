#!/usr/bin/env python3
"""MCP server for tracking architectural decisions, predictions, and outcomes.

Tracks the decision → prediction → outcome feedback loop, enabling iterative
improvement of technical decision-making through validated results.

Tools provided:
  - record-decision: Register a technical decision with problem, solution, alternatives, and technologies
  - record-prediction: Link a measurable prediction to a decision
  - record-outcome: Close the loop with actual results and accuracy score
  - query-decisions: Search prior decisions by keyword, technology, or domain
"""

import json
import os
import sys
import tempfile
from datetime import datetime
from typing import Any

LOG_PATH = os.path.expanduser(
    os.environ.get("MCP_DECISIONS_LOG_PATH", "~/.local/share/mcp-decisions/decisions_log.json")
)
_SERVER_START_TS = datetime.now().isoformat()


def _read_log() -> list[dict]:
    """Read all JSONL lines from the log. Returns [] if file does not exist."""
    if not os.path.exists(LOG_PATH):
        return []
    entries = []
    try:
        with open(LOG_PATH) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError:
        pass
    return entries


def _append(entry: dict) -> None:
    """Append JSONL entry with automatic directory creation."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    try:
        with open(LOG_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except OSError as e:
        print(f"WARNING: failed to write log: {e}", file=sys.stderr)


def _next_id(prefix: str, entries: list[dict], id_field: str) -> str:
    """Generate next sequential DEC-YYYY-NNNN or PRD-YYYY-NNNN ID.

    Filters entries from current year with prefix, gets max NNNN, increments.
    """
    year = datetime.now().year
    year_prefix = f"{prefix}-{year}-"
    max_num = 0
    for e in entries:
        entry_id = e.get(id_field, "")
        if entry_id.startswith(year_prefix):
            try:
                num = int(entry_id.replace(year_prefix, ""))
                max_num = max(max_num, num)
            except ValueError:
                pass
    return f"{year_prefix}{max_num + 1:04d}"


def record_decision(problem: str, chosen_solution: str, rejected_alternatives: list,
                    technologies: list, status: str = "ACTIVE", adr_ref: str | None = None,
                    domain: str | None = None, predictions: list | None = None) -> dict:
    """Create and store a decision record.

    If predictions are provided, also creates linked prediction records.
    Returns decision_id, prediction_ids, and status.
    """
    entries = _read_log()
    decision_id = _next_id("DEC", entries, "decision_id")

    entry = {
        "type": "decision",
        "decision_id": decision_id,
        "ts": datetime.now().isoformat(),
        "problem": problem,
        "chosen_solution": chosen_solution,
        "rejected_alternatives": rejected_alternatives or [],
        "technologies": technologies or [],
        "status": status,
        "adr_ref": adr_ref,
        "domain": domain,
    }
    _append(entry)

    prediction_ids = []
    if predictions:
        for pred in predictions:
            pred_id = record_prediction(decision_id, pred["prediction_type"], pred["predicted_value"])
            prediction_ids.append(pred_id["prediction_id"])

    return {
        "decision_id": decision_id,
        "prediction_ids": prediction_ids,
        "status": "OK"
    }


def record_prediction(decision_id: str, prediction_type: str, predicted_value: str) -> dict:
    """Validate decision_id exists, create and store a prediction record.

    Returns prediction_id or error.
    """
    entries = _read_log()

    if not any(e["type"] == "decision" and e["decision_id"] == decision_id for e in entries):
        return {"error": f"decision_id not found: {decision_id}"}

    prediction_id = _next_id("PRD", entries, "prediction_id")

    entry = {
        "type": "prediction",
        "prediction_id": prediction_id,
        "decision_id": decision_id,
        "ts": datetime.now().isoformat(),
        "prediction_type": prediction_type,
        "predicted_value": predicted_value,
    }
    _append(entry)

    return {"prediction_id": prediction_id}


def record_outcome(prediction_id: str, actual_value: str, measurement_source: str,
                   accuracy_score: int) -> dict:
    """Validate prediction_id exists, record actual results, calculate accuracy.

    Score mapping: >=90 SUCCESS, 50-89 PARTIAL_SUCCESS, <50 FAILED.
    Returns validation_status, accuracy_score, and optional lesson_recommended nudge.
    """
    entries = _read_log()

    if not any(e["type"] == "prediction" and e["prediction_id"] == prediction_id for e in entries):
        return {"error": f"prediction_id not found: {prediction_id}"}

    if accuracy_score >= 90:
        validation_status = "SUCCESS"
    elif accuracy_score >= 50:
        validation_status = "PARTIAL_SUCCESS"
    else:
        validation_status = "FAILED"

    entry = {
        "type": "outcome",
        "prediction_id": prediction_id,
        "ts": datetime.now().isoformat(),
        "actual_value": actual_value,
        "measurement_source": measurement_source,
        "accuracy_score": accuracy_score,
        "validation_status": validation_status,
    }
    _append(entry)

    result = {
        "prediction_id": prediction_id,
        "validation_status": validation_status,
        "accuracy_score": accuracy_score,
    }

    if accuracy_score < 75:
        result["lesson_recommended"] = True
        result["lesson_hint"] = "Accuracy < 75%. Consider recording a lesson learned."

    return result


def query_decisions(keyword: str | None = None, technology: str | None = None,
                   domain: str | None = None, max_results: int = 5) -> list[dict]:
    """Search stored decisions by keyword, technology, or domain (AND logic).

    keyword: case-insensitive match in problem + solution + alternatives.
    technology: exact (case-insensitive) match against technologies list.
    domain: partial match in domain field.
    Results sorted by timestamp descending (newest first).
    """
    entries = _read_log()
    decisions = [e for e in entries if e["type"] == "decision"]

    matched = []
    for d in decisions:
        if keyword:
            haystack = (
                d.get("problem", "").lower() + " " +
                d.get("chosen_solution", "").lower() + " " +
                " ".join(d.get("rejected_alternatives", [])).lower()
            )
            if keyword.lower() not in haystack:
                continue

        if technology:
            if technology.lower() not in [t.lower() for t in d.get("technologies", [])]:
                continue

        if domain:
            if domain.lower() not in d.get("domain", "").lower():
                continue

        matched.append(d)

    matched.sort(key=lambda x: x.get("ts", ""), reverse=True)
    return matched[:max_results]


def _pending_from_this_session() -> list[str]:
    """Return prediction IDs from current session without recorded outcomes.

    Predictions created in this session (ts >= _SERVER_START_TS) that lack
    a corresponding outcome entry.
    """
    entries = _read_log()
    predictions_this_session = [
        e["prediction_id"] for e in entries
        if e["type"] == "prediction" and e.get("ts", "") >= _SERVER_START_TS
    ]
    outcome_ids = {e["prediction_id"] for e in entries if e["type"] == "outcome"}

    return [pid for pid in predictions_this_session if pid not in outcome_ids]


TOOL_DEFINITIONS = [
    {
        "name": "record-decision",
        "description": "Register a technical decision with problem, solution, alternatives, and technologies",
        "inputSchema": {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "The problem or technical opportunity identified",
                },
                "chosen_solution": {
                    "type": "string",
                    "description": "The solution that was chosen",
                },
                "rejected_alternatives": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Alternatives considered and rejected",
                },
                "technologies": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Technologies involved in this decision (e.g., ['duckdb', 'parquet'])",
                },
                "status": {
                    "type": "string",
                    "enum": ["ACTIVE", "SUPERSEDED", "DEPRECATED"],
                    "default": "ACTIVE",
                    "description": "Decision status",
                },
                "adr_ref": {
                    "type": "string",
                    "description": "Reference to an associated ADR, if any (e.g., 'docs/adr/adr-012-duckdb.md')",
                },
                "domain": {
                    "type": "string",
                    "description": "Technical domain (e.g., 'data-engineering', 'backend', 'ai')",
                },
                "predictions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "prediction_type": {
                                "type": "string",
                                "enum": ["LATENCY", "COST", "SCALABILITY", "DATA_QUALITY", "RELIABILITY", "MAINTAINABILITY", "BUSINESS_IMPACT"],
                            },
                            "predicted_value": {
                                "type": "string",
                                "description": "Expected result (e.g., 'p99 latency < 200ms')",
                            },
                        },
                        "required": ["prediction_type", "predicted_value"],
                    },
                    "description": "Initial predictions known at decision time (optional)",
                },
            },
            "required": ["problem", "chosen_solution", "rejected_alternatives", "technologies"],
        },
    },
    {
        "name": "record-prediction",
        "description": "Register a measurable prediction linked to a decision",
        "inputSchema": {
            "type": "object",
            "properties": {
                "decision_id": {
                    "type": "string",
                    "description": "Decision ID (e.g., 'DEC-2026-0001')",
                },
                "prediction_type": {
                    "type": "string",
                    "enum": ["LATENCY", "COST", "SCALABILITY", "DATA_QUALITY", "RELIABILITY", "MAINTAINABILITY", "BUSINESS_IMPACT"],
                    "description": "Type of prediction",
                },
                "predicted_value": {
                    "type": "string",
                    "description": "Expected result (e.g., 'latency p99 < 200ms', 'cost < $100/month')",
                },
            },
            "required": ["decision_id", "prediction_type", "predicted_value"],
        },
    },
    {
        "name": "record-outcome",
        "description": "Close the prediction loop: record actual results and calculate accuracy",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prediction_id": {
                    "type": "string",
                    "description": "Prediction ID (e.g., 'PRD-2026-0001')",
                },
                "actual_value": {
                    "type": "string",
                    "description": "Observed result (e.g., 'latency p99 = 180ms')",
                },
                "measurement_source": {
                    "type": "string",
                    "enum": ["HEURISTIC", "LOGS", "MONITORING", "BENCHMARK", "USER_FEEDBACK", "PRODUCTION_METRICS"],
                    "description": "Where the measurement came from",
                },
                "accuracy_score": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100,
                    "description": "Accuracy of prediction (0-100). >=90 excellent, 50-89 acceptable, <50 failed",
                },
            },
            "required": ["prediction_id", "actual_value", "measurement_source", "accuracy_score"],
        },
    },
    {
        "name": "query-decisions",
        "description": "Search prior decisions by keyword, technology, or domain",
        "inputSchema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search in problem + solution + alternatives (case-insensitive)",
                },
                "technology": {
                    "type": "string",
                    "description": "Exact technology filter (e.g., 'duckdb')",
                },
                "domain": {
                    "type": "string",
                    "description": "Partial domain filter",
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "description": "Maximum results to return",
                },
            },
        },
    },
]


def handle_tool_call(tool_name: str, arguments: dict) -> str:
    """Dispatch MCP tool calls to their handlers."""
    if tool_name == "record-decision":
        result = record_decision(
            problem=arguments.get("problem"),
            chosen_solution=arguments.get("chosen_solution"),
            rejected_alternatives=arguments.get("rejected_alternatives", []),
            technologies=arguments.get("technologies", []),
            status=arguments.get("status", "ACTIVE"),
            adr_ref=arguments.get("adr_ref"),
            domain=arguments.get("domain"),
            predictions=arguments.get("predictions"),
        )
        payload = result
        pending = _pending_from_this_session()
        if pending:
            payload["OUTCOME_GATE"] = (
                f"⚠️  {len(pending)} prediction(s) from this session still lack outcomes: {pending}. "
                f"Record results via record-outcome before ending."
            )
        return json.dumps(payload, indent=2, default=str)

    elif tool_name == "record-prediction":
        result = record_prediction(
            decision_id=arguments.get("decision_id"),
            prediction_type=arguments.get("prediction_type"),
            predicted_value=arguments.get("predicted_value"),
        )
        return json.dumps(result, indent=2, default=str)

    elif tool_name == "record-outcome":
        result = record_outcome(
            prediction_id=arguments.get("prediction_id"),
            actual_value=arguments.get("actual_value"),
            measurement_source=arguments.get("measurement_source"),
            accuracy_score=arguments.get("accuracy_score"),
        )
        return json.dumps(result, indent=2, default=str)

    elif tool_name == "query-decisions":
        results = query_decisions(
            keyword=arguments.get("keyword"),
            technology=arguments.get("technology"),
            domain=arguments.get("domain"),
            max_results=arguments.get("max_results", 5),
        )
        payload = {"results": results}
        pending = _pending_from_this_session()
        if pending:
            payload["OUTCOME_GATE"] = (
                f"⚠️  {len(pending)} prediction(s) from this session still lack outcomes: {pending}. "
                f"Record results via record-outcome before ending."
            )
        return json.dumps(payload, indent=2, default=str)

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _selftest():
    """Self-check: record-decision → record-prediction → record-outcome → query-decisions."""
    global LOG_PATH, _SERVER_START_TS

    with tempfile.TemporaryDirectory() as tmpdir:
        LOG_PATH = os.path.join(tmpdir, "test_decisions_log.json")
        _SERVER_START_TS = datetime.now().isoformat()

        result = record_decision(
            problem="slow cache queries",
            chosen_solution="duckdb",
            rejected_alternatives=["sqlite", "pandas"],
            technologies=["duckdb", "parquet"],
            domain="data-engineering",
            predictions=[{"prediction_type": "LATENCY", "predicted_value": "p99 < 200ms"}],
        )
        assert result["status"] == "OK", f"record-decision failed: {result}"
        assert result["decision_id"].startswith("DEC-"), f"decision_id format wrong: {result['decision_id']}"
        assert len(result["prediction_ids"]) == 1, f"prediction_ids wrong: {result['prediction_ids']}"
        decision_id = result["decision_id"]
        prediction_id = result["prediction_ids"][0]

        results = query_decisions(technology="duckdb")
        assert len(results) == 1, f"query-decisions returned {len(results)}, expected 1"
        assert results[0]["decision_id"] == decision_id

        result = record_outcome(
            prediction_id=prediction_id,
            actual_value="p99 = 180ms",
            measurement_source="MONITORING",
            accuracy_score=95,
        )
        assert result["validation_status"] == "SUCCESS", f"validation_status wrong: {result['validation_status']}"
        assert result["accuracy_score"] == 95

        pending = _pending_from_this_session()
        assert len(pending) == 0, f"_pending_from_this_session not empty: {pending}"

        print("✅ All self-tests passed")


def main():
    """MCP server loop: read JSON-RPC from stdin, write responses to stdout."""
    if len(sys.argv) > 1 and sys.argv[1] == "--selftest":
        _selftest()
        return

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            method = request.get("method", "")
            req_id = request.get("id")

            if method == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2025-03-26",
                        "serverInfo": {
                            "name": "decisions",
                            "version": "1.0.0",
                        },
                        "capabilities": {
                            "tools": {
                                "list": True,
                                "call": True,
                            },
                        },
                    },
                }
            elif method == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"tools": TOOL_DEFINITIONS},
                }
            elif method == "tools/call":
                params = request.get("params", {})
                result = handle_tool_call(
                    params.get("name"),
                    params.get("arguments", {}),
                )
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {"content": [{"type": "text", "text": result}]},
                }
            elif req_id is None:
                continue
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if "request" in dir() else None,
                "error": {"code": -32603, "message": str(e)},
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
