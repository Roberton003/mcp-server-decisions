<!-- mcp-name: io.github.Roberton003/mcp-server-decisions -->

<div align="center">

# 🧠 MCP Server: Decisions

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Registry](https://img.shields.io/badge/MCP_Registry-io.github.Roberton003%2Fmcp--server--decisions-purple?style=for-the-badge&logo=modelcontextprotocol)](https://registry.modelcontextprotocol.io/)
[![GitHub](https://img.shields.io/badge/GitHub-Roberton003%2Fmcp--server--decisions-black?style=for-the-badge&logo=github)](https://github.com/Roberton003/mcp-server-decisions)

<p align="center">
  <b>Architectural decision tracking with prediction validation and outcome gates.</b><br />
  Record choices, state testable predictions, measure outcomes, and close the feedback loop for AI agents & teams.
</p>

---

</div>

> ⚡ **Zero External Dependencies** • Stdlib-only Python • Append-only JSONL storage • Fully portable

---

## 📌 Key Features

* **🎯 Decision Recording** — Capture architectural choices with problem statement, solution, rejected alternatives, and target technologies.
* **📈 Prediction Linking** — Attach testable claims (latency, cost, scalability, reliability) tied to decisions.
* **✅ Outcome Validation** — Record measured results and automatically compute accuracy scores (0–100 scale).
* **📊 Technology Performance Registry** — Aggregate success rates and confidence metrics per technology over time.
* **🚪 Outcome Gate Pattern** — In-band nudges inside tool responses prevent decision feedback loops from leaking (**3.8% → 14.5%** closure rate).
* **⚡ Zero Dependencies** — Portable append-only JSONL log. No database servers, no migrations, no background daemons.

---

## ⚡ Quick Example

### 1️⃣ Record a Decision

```bash
# Agent or user records a choice:
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
# ➔ Returns: DEC-2026-0001, PRD-2026-0001, PRD-2026-0002
```

### 2️⃣ Record an Outcome

```bash
record-outcome(
  prediction_id="PRD-2026-0001",
  actual_value="p99 = 180ms",
  measurement_source="MONITORING",
  accuracy_score=95
)
# ➔ Returns: SUCCESS ✅ (95% accuracy)
```

### 3️⃣ Query Prior Decisions & Technology Stats

```bash
# Search past decisions before choosing a technology:
query-decisions(technology="duckdb", max_results=5)

# View aggregated technology performance:
python3 scripts/technology_performance_report.py
# ➔ Output:
# technology: duckdb  | successful: 12 | failed: 1 | avg_accuracy: 91.2% | confidence: HIGH
```

---

## 🚀 Quick Start & Setup

### 📦 Installation

```bash
# From PyPI (once published) or local editable install:
pip install -e .
```

### 🛠️ Client Configuration

Add to your MCP client configuration (e.g. Claude Desktop, Claude Code, Cursor, OpenCode):

```json
{
  "mcpServers": {
    "mcp-server-decisions": {
      "type": "stdio",
      "command": "mcp-server-decisions"
    }
  }
}
```

For client-specific setup guides (Claude, OpenCode, Codex, Antigravity), see 📖 **[docs/INTEGRATIONS.md](docs/INTEGRATIONS.md)**.

---

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

**Real Example**: After recording a decision with 3 predictions, the response includes:

```json
{
  "decision_id": "DEC-2026-0042",
  "prediction_ids": ["PRD-2026-0051", "PRD-2026-0052", "PRD-2026-0053"],
  "status": "OK",
  "OUTCOME_GATE": "⚠️  3 prediction(s) from this session still lack outcomes: [PRD-2026-0051, PRD-2026-0052, PRD-2026-0053]. Record results via record-outcome before ending."
}
```

Next query still shows the gate until all 3 outcomes are recorded. Once they are, the gate disappears automatically.

For the full pattern explanation, see [`docs/OUTCOME-GATE-PATTERN.md`](docs/OUTCOME-GATE-PATTERN.md).

## 🏛️ Architecture & Tech Stack

* **Storage**: Single append-only `JSONL` file (no database setup, no migrations, portable & git-friendly).
* **IDs**: Sequential per calendar year (`DEC-2026-0001`, `PRD-2026-0002`, `OUT-2026-0003`).
* **Accuracy Scoring**: Automatic classification (`≥90` SUCCESS, `50–89` PARTIAL_SUCCESS, `<50` FAILED).
* **Runtime**: Stdlib-only Python 3.10+ (zero external pip runtime dependencies).
* **Protocol**: Model Context Protocol (JSON-RPC 2.0 over stdio).

---

## ⚙️ Environment Variables

| Variable | Description | Default Path |
|---|---|---|
| `MCP_DECISIONS_LOG_PATH` | Path to the append-only JSONL log file | `~/.local/share/mcp-decisions/decisions_log.json` |

---

## 📚 Documentation & Resources

| Document | Purpose |
|---|---|
| ⚡ **[Quick Start](QUICKSTART.md)** | 5-minute setup guide & first decision |
| 🔌 **[Client Integrations](docs/INTEGRATIONS.md)** | Setup configs for Claude, OpenCode, Codex, Antigravity |
| 📐 **[Architecture & Design](docs/ARCHITECTURE.md)** | Core design rationale & data models |
| 💡 **[Detailed Examples](docs/EXAMPLES.md)** | Real JSON-RPC request/response payloads |
| 🚪 **[Outcome Gate Pattern](docs/OUTCOME-GATE-PATTERN.md)** | In-band feedback loop design philosophy |
| 📖 **[Wiki](https://github.com/Roberton003/mcp-server-decisions/wiki)** | FAQ and advanced topics |

---

## 🧪 Development & Testing

Run unit & selftests locally:

```bash
python3 server.py --selftest
# ➔ ✅ All self-tests passed
```

See 📝 **[CONTRIBUTING.md](CONTRIBUTING.md)** to contribute features or fixes.

---

## 🗺️ Roadmap

- [x] Core decision / prediction / outcome tracking
- [x] Outcome Gate in-band nudges
- [x] Technology Performance Registry
- [ ] Web UI for browsing & searching decisions
- [ ] Webhooks / notifications on low prediction accuracy
- [ ] Pre-built decision templates & domain patterns

---

## 📄 License & Disclaimer

MIT © 2026 Roberton003 — See [LICENSE](LICENSE).

*This project is community-built and independent. It is not affiliated with any organization or standard-setting body.*

---

<div align="center">
  <b>Made for AI agents. Built for teams. Learn from every decision.</b>
</div>

