# Decision Log — JSON Lines audit trail for all marketing pipeline decisions

## Concept

Every significant decision in the marketing pipeline is logged to a JSON Lines file. This creates a complete audit trail that can be:
- Queried to understand why a decision was made
- Used to debug issues
- Used to learn from past decisions
- Presented to human reviewers for approval

## Format

```json
{"decision_id": "dec-001", "stage": "strategy", "category": "channel_selection", ...}
{"decision_id": "dec-002", "stage": "copy", "category": "content_angle_selection", ...}
```

## Decision Categories

| Category | When Used |
|----------|-----------|
| `channel_selection` | Choosing which channels to activate |
| `audience_segmentation` | How to segment the audience |
| `content_angle_selection` | Which strategic angle to lead with |
| `budget_allocation` | How to distribute budget across channels |
| `platform_timing` | When to publish on each platform |
| `creative_direction` | Visual style decisions |
| `targeting_parameters` | Paid audience parameters |
| `ad_copy_variants` | Which copy variants to promote |
| `email_sequence_design` | Email sequence structure |
| `repurpose_strategy` | Which pieces to repurpose where |
| `compliance_decision` | Compliance approvals |
| `bid_strategy` | Paid bidding approach |
| `human_approval` | Human approved or rejected a recommendation |

## Decision Log Entry Schema

```json
{
  "decision_id": "dec-001",
  "execution_id": "exec-abc123",
  "stage": "strategy",
  "category": "channel_selection",
  "subject": "Selected LinkedIn as primary channel for awareness",
  "options_considered": [
    {
      "option_id": "opt-1",
      "name": "LinkedIn primary + Twitter secondary",
      "score": 0.85,
      "pros": ["Reaches B2B audience directly", "Lower competition than Meta"],
      "cons": ["Higher cost per engagement than Twitter"],
      "rejected_because": null
    },
    {
      "option_id": "opt-2",
      "name": "Meta primary + LinkedIn secondary",
      "score": 0.72,
      "pros": ["Lower CPM", "Broader reach"],
      "cons": ["B2B audience less active on Meta"],
      "rejected_because": "B2B decision-makers not active enough on Meta for our audience segment"
    }
  ],
  "selected": "opt-1",
  "reason": "Our audience (B2B SaaS founders) is most active on LinkedIn. Higher engagement rate justifies slightly higher cost.",
  "confidence": 0.82,
  "user_visible": true,
  "user_approved": false,
  "user_approved_at": null,
  "approved_by": null,
  "timestamp": "2026-05-14T10:30:00Z",
  "metadata": {
    "budget_impact_usd": 600,
    "expected_engagement_rate": 3.5,
    "competitor_activity": "medium"
  }
}
```

## Python Implementation

```python
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class DecisionLogger:
    """
    JSON Lines decision logger for marketing pipeline.

    Usage:
        logger = DecisionLogger("~/agentic-marketing/logs/decisions")
        logger.log(
            stage="strategy",
            category="channel_selection",
            subject="Selected LinkedIn as primary",
            options=[...],
            selected="opt-1",
            reason="...",
        )
    """

    def __init__(self, log_dir: str | Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.execution_id = f"exec-{uuid.uuid4().hex[:12]}"

    def _log_path(self) -> Path:
        """One log file per execution."""
        return self.log_dir / f"{self.execution_id}.jsonl"

    def log(
        self,
        stage: str,
        category: str,
        subject: str,
        options_considered: list[dict[str, Any]] | None = None,
        selected: str | None = None,
        reason: str | None = None,
        confidence: float | None = None,
        user_visible: bool = True,
        user_approved: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Write a decision entry to the JSONL log file."""
        entry = {
            "decision_id": f"dec-{uuid.uuid4().hex[:8]}",
            "execution_id": self.execution_id,
            "stage": stage,
            "category": category,
            "subject": subject,
            "options_considered": options_considered or [],
            "selected": selected,
            "reason": reason,
            "confidence": confidence,
            "user_visible": user_visible,
            "user_approved": user_approved,
            "user_approved_at": None,
            "approved_by": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata or {},
        }

        with open(self._log_path(), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        return entry

    def mark_approved(self, decision_id: str, approved_by: str = "human") -> None:
        """Mark a decision as approved by a human."""
        log_path = self._log_path()
        if not log_path.exists():
            return

        entries = []
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["decision_id"] == decision_id:
                    entry["user_approved"] = True
                    entry["user_approved_at"] = datetime.now(timezone.utc).isoformat()
                    entry["approved_by"] = approved_by
                entries.append(entry)

        with open(log_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def query(
        self,
        stage: str | None = None,
        category: str | None = None,
        execution_id: str | None = None,
        user_approved: bool | None = None,
    ) -> list[dict[str, Any]]:
        """Query decisions from the current execution log."""
        log_path = self._log_path()
        if not log_path.exists():
            return []

        results = []
        with open(log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if execution_id and entry.get("execution_id") != execution_id:
                    continue
                if stage and entry.get("stage") != stage:
                    continue
                if category and entry.get("category") != category:
                    continue
                if user_approved is not None and entry.get("user_approved") != user_approved:
                    continue
                results.append(entry)

        return results

    def get_decision(self, decision_id: str) -> dict[str, Any] | None:
        """Get a specific decision by ID."""
        log_path = self._log_path()
        if not log_path.exists():
            return None

        with open(log_path, encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                if entry["decision_id"] == decision_id:
                    return entry
        return None
```

## Usage in Pipeline

```python
# Before a decision
logger.log(
    stage="copy",
    category="content_angle_selection",
    subject="Selected 'AI-First Customer Success' angle for cp-001",
    options_considered=[
        {"option_id": "angle-1", "name": "AI-First Customer Success", "score": 0.9},
        {"option_id": "angle-2", "name": "Churn Cost Breakdown", "score": 0.75},
    ],
    selected="angle-1",
    reason="Higher grounding in market_brief data (73% of SaaS companies exploring AI)",
    confidence=0.85,
)

# For human approval decisions
approval_entry = logger.log(
    stage="strategy",
    category="channel_selection",
    subject="Human approval required for channel_strategy",
    user_visible=True,
)
# Present to human, then:
logger.mark_approved(approval_entry["decision_id"])
```

## Query Examples

```python
# Get all decisions for the strategy stage
strategy_decisions = logger.query(stage="strategy")

# Get all decisions not yet approved
pending_approvals = logger.query(user_approved=False)

# Get all channel selection decisions
channel_decisions = logger.query(category="channel_selection")

# Export to DataFrame for analysis
import pandas as pd
decisions = logger.query()
df = pd.DataFrame(decisions)
df.to_csv("decision_audit.csv", index=False)
```