# 🛣️ Roadmap: Evidence-Linked Engineering Decisions

This roadmap defines the evolution of `mcp-server-decisions` from a lightweight decision log into an evidence-linked memory substrate for decisions made by humans and AI agents.

> **Positioning:** An evidence-linked MCP server for architectural decisions made by humans and AI agents.  
> **Core Thesis:** Turn technical choices into testable hypotheses, link them to reproducible repository evidence, and learn from validated outcomes.

The project remains lightweight, MIT-licensed, stdlib-only Python, and zero-dependency at runtime. The goal is to answer, with reproducible evidence, whether a technical decision achieved its intended outcome.

---

## 🧭 Principles

1. **Evidence over narrative** — Claims about technical impact must link to reproducible machine artifacts or be explicitly marked as self-reported.
2. **Structured where validation matters** — Metrics, operators, targets, units, tolerances, and evaluation windows must be machine-readable.
3. **Git-friendly by default** — Support repository-native versioning (`.decisions/`) so architectural decisions evolve alongside code.
4. **Smallest useful surface** — Prioritize one complete, reliable workflow over multiple shallow integrations.
5. **Human responsibility remains explicit** — The server records and validates evidence against contracts; it does not claim autonomous infallibility.
6. **Zero-dependency runtime** — Operate strictly with Python's standard library. No databases, background daemons, or mandatory cloud services.
7. **Honest maturity signals** — No unsubstantiated adoption claims or unverified internal metrics in public documentation.

---

## 🔄 The Closed Evidence Loop

```text
Decision ➔ Prediction ➔ Measurement ➔ Evidence Artifact ➔ Validation ➔ Scoped Learning
```

1. **Record a Decision:** Capture the problem, chosen solution, rejected alternatives, and technologies.
2. **State Structured Predictions:** Formulate testable, machine-evaluable claims (metric, operator, target, tolerance).
3. **Measure in Code / CI:** Run a deterministic test, benchmark, or profiler during implementation.
4. **Link Evidence Artifact:** Attach the resulting machine-readable artifact (JSON, log) with timestamp, commit, and method.
5. **Deterministic Validation:** The server compares expected vs. observed values and computes status (`VERIFIED`, `PARTIAL`, `FAILED`).
6. **Retrieve Scoped Memory:** Future agent queries retrieve validated results within their original scope before proposing new choices.

---

## 📊 Status Vocabulary

- 🟢 **VERIFIED:** Implemented, tested, and validated with deterministic artifacts or commands.
- 🟡 **IN PROGRESS:** Active implementation or open review.
- ⚪ **PROPOSED:** Planned direction, subject to feedback and adoption signals.
- ⏸️ **DEFERRED:** Explicitly postponed until the core evidence workflow proves useful.

---

## 🗺️ Phased Roadmap

### 📍 Phase 0: Credibility & Release Readiness
*Goal: Ensure the public repository is clean, reliable, and strictly backed by reproducible evidence.*

- [x] **VERIFIED** — Clean git history with zero merge artifacts and aligned PyPI metadata (`1.0.2`).
- [x] **VERIFIED** — Bespoke animated SVG hero banner at `docs/images/project-hero.svg` adhering to domain semantics and accessibility (`prefers-reduced-motion`).
- [x] **VERIFIED** — Matrix CI workflow in `.github/workflows/ci.yml` covering Python 3.10, 3.11, 3.12, and 3.13.
- [x] **VERIFIED** — Built-in selftest suite passes cleanly (`python server.py --selftest`).
- [x] **VERIFIED** — All unverified internal metrics and superlatives scrubbed from documentation.
- [ ] **IN PROGRESS** — Single end-to-end reproducible quickstart example in `README.md`.

---

### 📍 Phase 1: Structured Core Data Model
*Goal: Formalize machine-evaluable contracts for predictions and evidence.*

- [ ] **PROPOSED** — Formalize four distinct entities:
  - `Decision`: Context, chosen technology, rejected alternatives, rationale.
  - `Prediction`: Structured hypothesis tied to a decision.
  - `Evidence`: Reference to a reproducible artifact, execution command, commit hash, and timestamp.
  - `Outcome`: Deterministic comparison result, score, and scope boundaries.
- [ ] **PROPOSED** — Structured Prediction Schema:
  ```json
  {
    "prediction_id": "PRD-2026-0001",
    "decision_id": "DEC-2026-0001",
    "metric_name": "p99_latency",
    "operator": "LESS_THAN",
    "target_value": 200,
    "unit": "ms",
    "tolerance_pct": 5.0,
    "time_window": "1h"
  }
  ```
- [ ] **PROPOSED** — Maintain strict backward compatibility with existing append-only JSONL files.

---

### 📍 Phase 2: Evidence Classes & Deterministic Scoring
*Goal: Replace subjective 0–100 estimates with verifiable evidence tiers.*

- [ ] **PROPOSED** — Define clear evidence tiers:
  - `VERIFIED`: Backed by a local benchmark JSON, CI test artifact, or profiler trace.
  - `SOURCED`: Backed by public official documentation, academic paper, or vendor benchmark.
  - `PROJECTED`: Analytical calculation with documented assumptions.
  - `SELF_REPORTED`: Subjective developer input (cannot equate to machine-verified evidence).
- [ ] **PROPOSED** — Deterministic evaluation engine:
  - Evaluate `LESS_THAN`, `GREATER_THAN`, `EQUALS`, and `RANGE` operators.
  - Mark status as `SUCCESS`, `PARTIAL_SUCCESS`, `FAILED`, or `CONTRADICTED`.
- [ ] **PROPOSED** — Provide inspectable evidence references: link to artifact file path, SHA-256 hash, and generating command.

---

### 📍 Phase 3: One Reproducible CI Integration
*Goal: Prove the complete loop in a single, transparent GitHub Actions workflow.*

- [ ] **PROPOSED** — Provide a minimal benchmark example in `examples/benchmark_sample/`.
- [ ] **PROPOSED** — Standardize a simple, stable evidence JSON format.
- [ ] **PROPOSED** — Provide a CLI command (`mcp-decisions validate-evidence`) to evaluate an artifact against a prediction.
- [ ] **PROPOSED** — Include both a passing fixture and a failing fixture in test coverage.
- [ ] **PROPOSED** — Generate a clean, readable Markdown validation summary in the CI job step.

---

### 📍 Phase 4: Repository-Native Storage (`.decisions/`) & Git Workflow
*Goal: Make decision history reviewable and version-controlled with project code.*

- [ ] **PROPOSED** — Dual storage support:
  - User-level default: `~/.local/share/mcp-decisions/decisions_log.json` (zero configuration).
  - Repository-level: `.decisions/decisions.jsonl` (team versioning in Git).
- [ ] **PROPOSED** — Deterministic Markdown export for human review during pull requests.
- [ ] **PROPOSED** — Non-blocking git hook warnings for unclosed session predictions (advisory only; no workflow blockage).
- [ ] **PROPOSED** — Redaction guidance to prevent committing credentials or sensitive tokens.

---

### 📍 Phase 5: Agent Decision Memory & Context-Aware Retrieval
*Goal: Provide historical evidence to agents before new architectural choices are made.*

- [ ] **PROPOSED** — Context-aware querying:
  - Filter by technology, metric, domain, and evidence tier.
  - Query example: *"Retrieve validated latency outcomes for DuckDB under batch workloads."*
- [ ] **PROPOSED** — Provenance-rich Decision Brief:
  - Deliver compact summaries with explicit scope limits to prevent applying narrow findings to universal contexts.
- [ ] **PROPOSED** — Contextual Alternative Recall:
  - When a prior decision failed to meet its target metric, surface the recorded `rejected_alternatives` and original rationales as context for the next architectural spike.

---

### 📍 Phase 6: Open Schema & Ecosystem Testing
*Goal: Share the format with external developers for independent review.*

- [ ] **PROPOSED** — Publish a versioned JSON Schema for the decision-evidence model.
- [ ] **PROPOSED** — Test consumption by an external tool or script without importing server internals.
- [ ] **PROPOSED** — Solicit feedback from open-source maintainers before proposing broader standards.

---

## ⏸️ Explicitly Deferred Items

To maintain a disciplined, high-velocity core, these items are deferred until the primary evidence loop has demonstrated adoption:

- Live telemetry bridges (OpenTelemetry / Prometheus webhook listeners).
- Multiple third-party benchmark parsers (start with one clean format).
- Reusable GitHub Marketplace Action packaging (start with a simple shell/python step).
- Commit-blocking enforcement hooks.
- Multi-tenant web UI or hosted services.
- Distributed storage backends.

---

## 🏁 Definition of the First Major Milestone

The project achieves its first major product milestone when a clean repository checkout demonstrates:

1. An AI agent or developer records a decision with `record-decision`.
2. The decision contains a structured prediction contract.
3. A local benchmark runs and produces a machine-readable JSON artifact.
4. The artifact is linked to the prediction via `record-outcome`.
5. The system computes a deterministic status based on expected vs. observed values.
6. The record distinguishes machine-verified evidence from self-reported claims.
7. A subsequent `query-decisions` call retrieves the result with full provenance and scope limits.
