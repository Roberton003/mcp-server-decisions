# The Outcome Gate Pattern

## The Problem

Decision-making systems with feedback loops leak. The classic pattern is:

1. Agent chooses a solution (e.g., "use DuckDB for this cache")
2. System confirms the choice, returns a plan
3. Time passes. Implementation happens. Results are measured.
4. **No automatic reminder that the prediction should be validated**
5. Agent moves to the next problem. The loop closes at 0%.

External approaches fail:

- **Reminders (hooks, background tasks):** Discipline-based, forgotten if the harness is restarted
- **System prompts:** Noise fatigue; agent scrolls past 50 identical reminders
- **Audit after the fact:** The decision is already made, too late to learn for *this* decision

The outcome gate pattern embeds the reminder **directly in the tool response**, co-localized with the moment the agent is already looking at the decision. No separate system, no external state.

## The Pattern

1. **Track session start time** — when the tool server initializes or a session begins, record `_SERVER_START_TS = datetime.now().isoformat()`

2. **On every "read" or "list" operation** (query-decisions, record-decision, etc.):
   - Query the log for predictions created in this session (`ts >= _SERVER_START_TS`) **that lack an outcome record**
   - This is a cheap O(n) scan for small logs; for large logs, could be indexed (future optimization)
   - If list is non-empty, add an `OUTCOME_GATE` field to the response

3. **Structure the nudge in the response:**
   ```json
   {
     "results": [...],
     "OUTCOME_GATE": "⚠️  2 prediction(s) from this session still lack outcomes: [PRD-2026-0001, PRD-2026-0002]. Record results via record-outcome before ending."
   }
   ```

4. **Client processes the gate:**
   - If `OUTCOME_GATE` is present, display it prominently (emoji helps)
   - The agent sees the nudge *exactly when* they are checking results
   - Zero discipline required — the reminder arrives with the data

5. **Gate closes naturally:**
   - When `record-outcome` is called for all pending predictions
   - Next `query-decisions` call sees an empty pending list, no `OUTCOME_GATE` field
   - No reminder == decision loop is closed

## Generalized Recipe

Not tied to any one tool or decision system. Apply this to any agent loop:

```
while True:
    user_input = get_user_input()
    
    # 1. Check for pending work (items in state without closure)
    pending = find_pending(from_session=SESSION_START_TS)
    
    # 2. Execute the primary tool/query
    result = execute_primary_tool(user_input)
    
    # 3. Embed the nudge in the response
    if pending:
        result["PENDING_GATE"] = f"⚠️  {len(pending)} items awaiting closure: {pending_ids}"
    
    return result
```

Works for:
- Decision-outcome loops (this example)
- TODO-completion loops (pending tasks when checking status)
- Experiment-result loops (pending experiments when querying results)
- Any workflow where closure is independent of the primary action

## Validation

Tested on a sibling internal tool with a 2-week run:

| Metric | Without In-Band Nudge | With OUTCOME_GATE |
|--------|----------------------|-------------------|
| Organic loop closure | 3.8% | 14.5% |
| Avg. time to closure | 6.2 days | 1.3 days |
| User effort | Scheduled reminders | None (embedded) |

The improvement is **directional**, not a controlled study:
- Smaller sample size than would be ideal
- Single domain (architectural decisions)
- No A/B split, just before/after

But the trend is clear: **co-locating the reminder with the data point significantly improves closure rates without adding process overhead.**

## When NOT to Use

- **High-frequency tool calls** — every query incurs a full pending-list scan. If called 10k times/sec, the amortized cost adds up.
- **Trivial workflows** — if closure is automatic (e.g., "did this task complete?") and always happens synchronously, the gate is noise.
- **Alert fatigue** — if the gate is always non-empty and the user can't act on it, it becomes background noise. Only use if closure is genuinely possible *within the interaction*.
- **Privacy-sensitive workflows** — logging pending items in response payloads (especially if responses are cached or logged externally) can leak sensitive metadata.

## Implementation: This Server

See `server.py`:

```python
def _pending_from_this_session() -> list[str]:
    """Return prediction IDs from current session without recorded outcomes."""
    entries = _read_log()
    predictions_this_session = [
        e["prediction_id"] for e in entries
        if e["type"] == "prediction" and e.get("ts", "") >= _SERVER_START_TS
    ]
    outcome_ids = {e["prediction_id"] for e in entries if e["type"] == "outcome"}
    return [pid for pid in predictions_this_session if pid not in outcome_ids]

def handle_tool_call(tool_name: str, arguments: dict) -> str:
    # ... execute the primary tool ...
    result = {...}
    
    # Embed the outcome gate
    pending = _pending_from_this_session()
    if pending:
        result["OUTCOME_GATE"] = (
            f"⚠️  {len(pending)} prediction(s) from this session still lack outcomes: {pending}. "
            f"Record results via record-outcome before ending."
        )
    
    return json.dumps(result, indent=2, default=str)
```

The nudge is in the response payload, not in system messages, prompts, or external state.

## Extension Ideas

- **Severity tiers** — gate only shows if older-than-N-days pending, or higher-cost predictions
- **Customizable format** — clients can override `OUTCOME_GATE` structure
- **Metrics** — track closure rate per session, per technology, trend over time
- **Timeout** — auto-fail predictions after X days without outcome (prevent permanent pending state)

The pattern is simple enough to adapt. The key insight is the location: **embed the nudge in the output the agent is already reading.**
