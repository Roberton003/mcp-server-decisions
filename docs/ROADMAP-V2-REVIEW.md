# 🔎 Review of Roadmap v2

## Executive summary

Roadmap v2 contains a strong product insight: architectural decisions become more valuable when they are expressed as testable predictions and connected to reproducible evidence. The proposed sequence from decision to prediction, measurement, evidence, validation, and learning is the most compelling part of the project.

However, v2 currently reads more like an ambitious product manifesto than an execution-ready roadmap. It overstates differentiation, includes claims that are not supported by the repository, marks work as complete when it is not independently verified, and introduces too many high-risk surfaces before the core workflow has evidence of adoption.

**Overall impression:** promising thesis, useful strategic direction, but not yet credible as a public roadmap without removing unsupported claims and reducing the first milestone.

## What is genuinely strong

### 1. The central problem is real

The roadmap correctly identifies a gap between:

- ADRs that become static documents;
- agent recommendations that lose context between sessions;
- CI and telemetry results that are not connected back to the decisions they were meant to validate.

This is a coherent problem space rather than an arbitrary feature list.

### 2. Evidence-linked decisions are a meaningful wedge

The strongest differentiator is not MCP by itself or another decision log. It is the proposed relationship:

```text
Decision → Prediction → Evidence → Outcome
```

That relationship could produce durable engineering knowledge that chat history, issue trackers, and ordinary ADRs usually do not preserve in machine-evaluable form.

### 3. Structured predictions are the right first technical move

Replacing free-form claims such as `p99 < 200ms` with fields such as metric, operator, target, unit, tolerance, and time window is a sound direction. It makes validation deterministic and creates a foundation for later integrations.

### 4. The roadmap protects against premature enterprise complexity

The explicit rejection of hosted multi-tenancy, RBAC, distributed databases, and a large dashboard is good. The repository should preserve this discipline.

### 5. Cross-agent interoperability is a credible use case

MCP is a reasonable transport for making the same decision history available to multiple compatible clients. This is useful, but it is an interoperability benefit—not yet a defensible moat.

## Important credibility problems

### 1. The “world's first” claim is not supportable

The positioning says:

> “The world's first evidence-linked architectural decision substrate for AI agents.”

No market investigation is included to establish this. The claim is unnecessary and exposes the project to easy contradiction. Use a descriptive claim instead:

> “An evidence-linked MCP server for architectural decisions made by humans and AI agents.”

### 2. “Massive open-source adoption” is the wrong planning premise

The roadmap says the product must command massive open-source adoption. That is an outcome, not a design requirement. The immediate question should be whether one maintainer can reproduce the workflow and whether another developer finds it useful.

Replace scale aspirations with measurable learning milestones:

- one clean-checkout demonstration;
- one external reviewer;
- one external contributor or integration test;
- one project using the format with permission;
- one validated decision backed by a real artifact.

### 3. The roadmap reintroduces unsupported internal metrics

The architecture diagram includes:

```text
(3.8% ➔ 14.5% rate)
```

Those figures were previously identified as internal, non-reproducible evidence and removed from public documentation. Reintroducing them in v2 creates a direct public-scrub failure.

They should be removed entirely unless the underlying study can be published with methodology, data, scope, and a reproducible artifact.

### 4. Phase 0 marks work complete without reliable evidence

The roadmap marks the hero banner and conflict resolution as complete. It also marks metadata alignment as complete. These statuses should be independently checked before being shown as done. A roadmap must not be used as proof that a task was completed.

Recommended status vocabulary:

```text
PROPOSED · IN PROGRESS · VERIFIED · DEFERRED
```

Use `VERIFIED` only when a command, test, diff, release, or public URL supports it.

### 5. Vendor names make the “universal” claim weaker

Listing Claude, Codex, Antigravity, Cursor, and OpenCode is useful as an integration target, but it makes the project look coupled to a particular personal toolchain. The core proposal should be vendor-neutral. Client-specific examples belong in integration documentation.

## Scope and sequencing concerns

### 1. Too many products are being planned at once

V2 includes:

- a core MCP server;
- structured schema;
- evidence model;
- GitHub Action;
- multiple CI parsers;
- telemetry bridge;
- PR comment generator;
- Git hooks;
- deterministic redaction;
- circuit breakers;
- agent decision briefs;
- counterfactual recommendations;
- an open standard;
- exporters;
- OpenTelemetry traces;
- terminal dashboard;
- dynamic SVG generation.

This is too broad for a project that currently has no demonstrated external adoption. The likely result is many partially implemented surfaces and a weaker core.

### 2. Phase 2 should not precede proof of the evidence model

A GitHub Action is not the first product milestone. It is packaging around a model that must first be stable. Implementing harvesters before defining evidence provenance and validation semantics risks freezing a poor interface.

### 3. Telemetry is a later-stage feature

A webhook receiver for OpenTelemetry or Prometheus introduces:

- authentication;
- authorization;
- replay handling;
- schema drift;
- cardinality and sampling issues;
- privacy concerns;
- retention and deletion questions;
- deployment and operational burden.

It should be explicitly deferred until local artifact-based evidence proves useful.

### 4. Git hooks should be warnings, not blockers

A pre-commit or pre-push “guard” can interrupt legitimate work, create false positives, and make adoption unpleasant. Initially it should report possible missing outcomes without blocking commits. Blocking behavior should require strong evidence and an explicit opt-in policy.

### 5. The counterfactual engine is overpromised

A failed decision does not imply that a previously rejected alternative is the correct next choice. Rejected alternatives may have been rejected for constraints that still apply. The safe first version is a context-aware list of alternatives and their original rationale, not an “intelligent rollback” or automatic recommendation.

### 6. Accuracy scores are not enough

A 0–100 accuracy score hides the difference between:

- a precisely measured benchmark;
- a subjective developer estimate;
- an outcome measured under a different workload;
- a result that cannot be reproduced.

The evidence class and provenance should be implemented before any aggregate score is treated as intelligence.

### 7. ODER is premature as a named standard

Publishing a schema is reasonable. Calling it a standard or aiming to become the canonical reference implementation requires external review and independent adopters. First publish it as a versioned project format or proposal, then test whether another tool can consume it.

## Recommended product thesis

The strongest honest thesis is:

> `mcp-server-decisions` turns architectural decisions into structured, evidence-linked records that humans and AI agents can query later.

The strongest first proof is:

1. Record a decision.
2. Record a structured prediction.
3. Run a deterministic local benchmark.
4. Link the benchmark artifact to the prediction.
5. Compare expected and observed values.
6. Record a provenance-aware outcome.
7. Query the result with its original scope and evidence.

If this workflow is excellent, the project has a real foundation. If it is not excellent, additional integrations will only distribute the weakness.

## Revised priority order

### Priority 0 — Credibility

- Remove unsupported metrics and superlatives.
- Verify all “done” claims.
- Align versions and public release metadata.
- Keep examples executable.
- State limitations clearly.

### Priority 1 — Structured core

- Define Decision, Prediction, Evidence, and Outcome records.
- Add schema versioning.
- Preserve backward compatibility with current JSONL data.
- Validate operators, values, units, tolerances, and time windows.

### Priority 2 — Evidence proof

- Support local benchmark or test artifacts.
- Preserve path, commit, timestamp, and method.
- Distinguish `VERIFIED`, `SELF_REPORTED`, `CONTRADICTED`, and `UNVERIFIABLE`.
- Replace or demote subjective accuracy as the primary result.

### Priority 3 — One reproducible integration

- Build one minimal GitHub Actions example.
- Use one stable JSON evidence format.
- Include both passing and failing fixtures.
- Produce a readable validation report.

### Priority 4 — Repository-native workflow

- Add optional `.decisions/` storage.
- Export to Markdown.
- Make records deterministic and reviewable in Git.
- Document redaction boundaries without promising perfect automatic scrubbing.

### Priority 5 — Agent retrieval

- Query by technology, metric, workload, scope, and evidence status.
- Return provenance with every result.
- Generate a compact decision brief.
- Avoid universal recommendations from narrow evidence.

### Priority 6 — Ecosystem testing

- Publish a versioned schema.
- Ask external developers to review it.
- Test consumption by a second tool.
- Only then consider a broader standard proposal.

### Deferred

- Telemetry bridge;
- multiple CI parsers;
- PR automation as a reusable marketplace action;
- active circuit breakers;
- automatic rollback recommendations;
- hosted service;
- web dashboard;
- dynamic project telemetry visuals.

## Suggested success criteria

The current v2 success definition is too dependent on fame and scale. A better definition for the first release is:

- A clean checkout completes the full decision-to-evidence workflow.
- The validation result is deterministic for the same input.
- Evidence provenance is visible and scoped.
- Self-reported outcomes are clearly distinguished from reproducible artifacts.
- Existing records remain readable after schema evolution.
- At least one external developer can follow the quickstart without maintainer intervention.
- At least one external project or contributor tests the workflow before adoption claims are made.

## Final assessment

Roadmap v2 has the seed of a differentiated project, but the differentiation is still a hypothesis. The project becomes genuinely interesting when it proves that it can connect a technical decision to an artifact and later retrieve a scoped lesson from that evidence.

The roadmap should be treated as a **product exploration plan**, not as a promise to build every listed feature. The next objective should be a narrow, reproducible evidence loop—not a universal standard, telemetry platform, or autonomous rollback engine.

**Recommendation:** keep the core thesis, remove unsupported market and metric claims, change completed checkboxes to evidence-backed statuses, and reduce the first milestone to structured predictions plus one reproducible evidence integration.
