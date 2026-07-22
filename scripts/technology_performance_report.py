#!/usr/bin/env python3
"""Technology Performance Registry — aggregate decisions log by technology.

Computes successful vs. failed projects per technology, average accuracy,
and confidence tier based on sample size.

Usage:
  python3 technology_performance_report.py
  python3 technology_performance_report.py --log-file ~/.local/share/mcp-decisions/decisions_log.json
"""

import argparse
import json
import os
from collections import defaultdict
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Compute Technology Performance Registry from decisions log"
    )
    parser.add_argument(
        "--log-file",
        default=os.path.expanduser(
            os.environ.get("MCP_DECISIONS_LOG_PATH", "~/.local/share/mcp-decisions/decisions_log.json")
        ),
        help="Path to decisions_log.json (default: env MCP_DECISIONS_LOG_PATH or ~/.local/share/mcp-decisions/decisions_log.json)",
    )
    args = parser.parse_args()

    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"❌ Log file not found: {log_path}")
        return 1

    entries = []
    try:
        with open(log_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    except OSError as e:
        print(f"❌ Error reading log: {e}")
        return 1

    decisions = {e["decision_id"]: e for e in entries if e["type"] == "decision"}
    predictions = {e["prediction_id"]: e for e in entries if e["type"] == "prediction"}
    outcomes = {e["prediction_id"]: e for e in entries if e["type"] == "outcome"}

    if not decisions:
        print("⚠️  No decisions found in log")
        return 0

    tech_stats = defaultdict(lambda: {"success": 0, "fail": 0, "accuracy_scores": []})

    for decision_id, decision in decisions.items():
        preds = [p for p in predictions.values() if p["decision_id"] == decision_id]
        if not preds:
            continue

        outcomes_for_decision = [
            outcomes[p["prediction_id"]]
            for p in preds
            if p["prediction_id"] in outcomes
        ]
        if not outcomes_for_decision:
            continue

        statuses = {o["validation_status"] for o in outcomes_for_decision}
        is_success = "SUCCESS" in statuses and "FAILED" not in statuses

        for tech in decision.get("technologies", []):
            bucket = tech_stats[tech]
            bucket["success" if is_success else "fail"] += 1
            bucket["accuracy_scores"].extend(
                o["accuracy_score"] for o in outcomes_for_decision
            )

    if not tech_stats:
        print("⚠️  No technology outcomes found (decisions without validated outcomes)")
        return 0

    print("\n" + "=" * 80)
    print("Technology Performance Registry")
    print("=" * 80 + "\n")

    for tech in sorted(tech_stats.keys()):
        s = tech_stats[tech]
        total = s["success"] + s["fail"]
        avg_accuracy = sum(s["accuracy_scores"]) / len(s["accuracy_scores"]) if s["accuracy_scores"] else 0

        if len(s["accuracy_scores"]) >= 10:
            confidence = "HIGH"
        elif len(s["accuracy_scores"]) >= 3:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        print(
            f"technology: {tech:20} | "
            f"successful_projects: {s['success']:3} | "
            f"failed_projects: {s['fail']:3} | "
            f"total: {total:3} | "
            f"average_accuracy: {avg_accuracy:5.1f}% | "
            f"confidence: {confidence}"
        )

    print("\n" + "=" * 80)
    print("Note: decisions count as 'successful' if >= 1 outcome SUCCESS and no FAILED")
    print("Confidence: LOW (<3 samples), MEDIUM (3-9), HIGH (>=10)")
    print("=" * 80 + "\n")

    return 0


if __name__ == "__main__":
    exit(main())
