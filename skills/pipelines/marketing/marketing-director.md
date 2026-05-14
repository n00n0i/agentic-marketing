# Marketing Director — Executive Producer for Agentic Marketing

## Role

Top-level orchestrator that runs the entire marketing pipeline. Like OpenMontage's Executive Producer, this director:

1. Reads channel_strategy to know which sub-pipelines to activate
2. Coordinates cross-channel consistency
3. Maintains cumulative brand state across all stages
4. Enforces budget governance across channels
5. Performs cross-stage quality checks
6. Can send work back to previous stages for revision
7. Maintains decision log for audit trail

## Marketing State (EP_STATE)

Throughout pipeline execution, the Marketing Director maintains:

```python
marketing_state = {
    # Brand consistency
    "brand_voice": {
        "tone": str,           # e.g., "professional but approachable"
        "vocabulary": [str],    # words to use / avoid
        "formatting": [str],   # e.g., "use emojis sparingly"
        "storytelling_style": str,
    },
    "visual_guidelines": {
        "color_palette": [str],
        "typography": str,
        "logo_usage": str,
        "image_style": str,    # e.g., "clean minimal, real photos"
    },

    # Research output
    "audience_segments": [dict],   # from market_brief
    "strategic_angles": [dict],    # from market_brief
    "competitors": [dict],         # from market_brief

    # Content produced
    "content_briefs": {content_id: dict},
    "copy_variants": {content_id: [variant, ...]},
    "creative_assets": {content_id: [asset, ...]},

    # Channel-specific state
    "organic": {
        "published": [],
        "scheduled": [],
        "platform_credentials": {},
    },
    "paid": {
        "campaigns": [],
        "targeting_profiles": [],
        "ad_creatives": [],
        "budget_allocated": {},
        "budget_spent": {},
    },
    "email": {
        "sequences": [],
        "subscribers": [],
        "personalization_rules": {},
    },

    # Pipeline tracking
    "revision_counts": {stage_name: int},
    "send_back_history": [(from_stage, to_stage, reason), ...],
    "decision_log": [DecisionLogEntry, ...],
    "warnings": [],
}
```

## Execution Protocol

```
EXECUTE_MARKETING_PIPELINE:

  ## PREPARE
  1. Load marketing-director skill (this file)
  2. Load project config (channels enabled, budget, brand guidelines)
  3. Initialize marketing_state with brand guidelines from config
  4. Initialize CostTracker with budget_default_usd

  ## PHASE 1: RESEARCH
  5. Run research-director:
     - Execute research process
     - Validate market_brief against schema
     - If invalid → REVISE with specific feedback
     - If valid → APPROVE
  6. Store audience_segments, strategic_angles, competitors in marketing_state
  7. Log decision: research director output approved

  ## PHASE 2: STRATEGY
  8. Run strategy-director:
     - Generate channel_strategy
     - Perform cost estimation
     - If budget exceeded → REVISE allocation
  9. PRESENT channel_strategy to human (human_approval_default=true)
     - If rejected → REVISE with feedback, max 3 revisions
     - If approved → continue
  10. Activate channels based on channel_strategy

  ## PHASE 3: CONTENT CREATION
  11. For each content piece requested:
      a. Run brief-director → content_brief
      b. Run copy-director → copy_variants
         - If review fails → REVISE, max 2 rounds, then PASS_WITH_WARNINGS
      c. Run creative-director → creative_assets
         - If review fails → REVISE

  ## PHASE 4: CHANNEL DELIVERY
  12. For organic channel (if enabled):
      a. Run repurpose-director → repurpose_plan
      b. Run publish-director → schedule posts
  13. For paid channel (if enabled):
      a. Run targeting-director → targeting_profile
         - PRESENT to human for approval
      b. Run ad-creative-director → ad_creative
         - PRESENT to human for approval
      c. Reserve budget for ad spend
  14. For email channel (if enabled):
      a. Run email-director → email_sequence
         - PRESENT to human for approval

  ## PHASE 5: CROSS-CHANNEL CHECK
  15. Verify message consistency across all channels
  16. Verify visual consistency (colors, fonts, imagery)
  17. Verify timing coherence (social → email → retargeting flow)
  18. Verify budget balance (no channel overspent vs. allocation)

  ## PHASE 6: FINALIZE
  19. Reconcile all costs
  20. Generate publish_log
  21. Present final report to human
  22. Log all decisions with reasoning
```

## Cross-Channel Consistency Checks

The Marketing Director performs these checks AFTER content creation but BEFORE publishing:

### Message Consistency
```python
def check_message_consistency(marketing_state):
    """Ensure core message is consistent across all channels."""
    core_message = marketing_state["strategic_angles"][0]["name"]
    issues = []

    for content_id, variants in marketing_state["copy_variants"].items():
        for variant in variants:
            if core_message not in variant["body"]:
                issues.append({
                    "content_id": content_id,
                    "variant_id": variant["variant_id"],
                    "issue": "Core message not present",
                    "suggestion": f"Include '{core_message}' in this variant"
                })

    return issues
```

### Visual Consistency
```python
def check_visual_consistency(marketing_state, brand_guidelines):
    """Ensure visuals follow brand guidelines across all assets."""
    issues = []
    expected_colors = set(brand_guidelines["color_palette"])

    for content_id, assets in marketing_state["creative_assets"].items():
        for asset in assets:
            asset_colors = set(asset.get("color_palette", []))
            if not asset_colors.intersection(expected_colors):
                issues.append({
                    "content_id": content_id,
                    "asset_id": asset["asset_id"],
                    "issue": "No brand colors detected",
                    "suggestion": f"Apply {expected_colors} to this asset"
                })

    return issues
```

### Timing Coherence
```python
def check_timing_coherence(publish_log, channel_strategy):
    """Ensure social → email → retargeting flow is logical."""
    issues = []

    # Check: email should follow social engagement, not precede it
    social_first = any(p["channel"] == "organic" for p in publish_log["entries"])
    email_pieces = [p for p in publish_log["entries"] if p["channel"] == "email"]

    if email_pieces and not social_first:
        issues.append({
            "issue": "Email sequence scheduled before organic content",
            "suggestion": "Consider publishing organic content first to build awareness"
        })

    return issues
```

## Budget Governance

### Pre-Execution Budget Check
```python
def pre_execution_budget_check(total_budget_usd, channel_strategy):
    """Estimate and reserve budget before execution."""
    estimated_costs = {
        "organic": 0.15 * total_budget_usd,    # AI tools only
        "paid": 0.80 * total_budget_usd,       # media spend
        "email": 0.05 * total_budget_usd,      # platform cost
    }

    for channel, cost in estimated_costs.items():
        CostTracker.reserve(channel, cost)

    return {
        "total_budget": total_budget_usd,
        "allocated": estimated_costs,
        "reserve_holdback": total_budget_usd * 0.10,
    }
```

### Per-Stage Cost Tracking
```python
def track_stage_cost(stage_name, estimated, actual):
    """Track cost at each stage."""
    entry = CostTracker.log(stage_name, estimated, actual)

    if actual > estimated * 1.1:
        MarketingDirector.emit_warning(
            f"Stage {stage_name} exceeded estimate by {((actual/estimated)-1)*100:.1f}%"
        )

    return entry
```

### Post-Execution Reconciliation
```python
def reconcile_budget():
    """Final budget reconciliation after all stages complete."""
    report = CostTracker.reconcile_all()

    if report["overspent"]:
        MarketingDirector.emit_warning(
            f"Budget overspent by ${report['overspent']:.2f}"
        )
        # In CAP mode, this would block publishing

    return report
```

## Revision and Send-Back Protocol

### When to Revise
- Stage review fails with ≥1 critical finding
- Artifact fails schema validation
- Budget estimate exceeded by >10%

### When to Send Back
- Cross-stage check detects inconsistency
- Downstream stage cannot work with upstream output
- Brand guidelines violated

### Revision Limits
- Max revisions per stage: 3
- Max send-backs per stage pair: 1
- Max total send-backs: 3

### Revision Protocol
```
REVISE(stage_name, findings):
  1. Increment revision_counts[stage_name]
  2. If revision_counts[stage_name] > max_revisions:
       → PASS_WITH_WARNINGS and continue
  3. Package findings as feedback for director
  4. Re-run director with feedback
  5. Re-review output
  6. If still failing after 3 revisions → PASS_WITH_WARNINGS
```

## Decision Log

All major decisions must be logged:

```python
DecisionLogEntry = {
    "decision_id": str,        # "dec-001"
    "stage": str,              # e.g., "strategy"
    "category": str,           # see categories below
    "subject": str,            # what was decided
    "options_considered": [
        {
            "option_id": str,
            "score": float,    # 0.0 - 1.0
            "pros": [str],
            "cons": [str],
            "rejected_because": str | null,
        }
    ],
    "selected": str,           # option_id
    "reason": str,
    "confidence": float,       # 0.0 - 1.0
    "user_visible": bool,
    "user_approved": bool,
    "timestamp": str,          # ISO 8601
}
```

### Decision Categories
- `channel_selection` — which channels to activate
- `audience_segmentation` — how to segment audience
- `content_angle_selection` — which strategic angle to lead with
- `budget_allocation` — how to distribute budget across channels
- `platform_timing` — when to publish on each platform
- `creative_direction` — visual style decisions
- `targeting_parameters` — paid audience parameters
- `ad_copy_variants` — which copy variants to promote
- `email_sequence_design` — email sequence structure
- `repurpose_strategy` — which pieces to repurpose where
- `compliance_decision` — compliance approvals
- `bid_strategy` — paid bidding approach

## Quality Gates

| Gate | After Stage | Check | Fail Action |
|------|-------------|-------|------------|
| G1 | research | market_brief valid + ≥3 angles + ≥2 data points per angle | Revise research |
| G2 | strategy | channel_strategy approved | Revise or abort |
| G3 | brief | content_brief complete | Revise brief |
| G4 | copy | ≥3 variants, all on-brand, CTAs specific | Revise copy |
| G5 | creative | assets exist + format-valid | Revise creative |
| G6 | targeting | audience size fits budget | Revise targeting |
| G7 | ad_creative | ≥3 headlines, compliance passed | Revise ads |
| G8 | email_sequence | 5-7 emails, personalization valid | Revise sequence |
| G9 | repurpose | ≥10 pieces, platform-correct | Revise repurposing |
| G10 | publish | all channels scheduled, budget current | Revise schedule |

## Common Pitfalls

1. **Skipping cross-channel checks** — Always verify message + visual consistency before publishing
2. **Not tracking budget in real-time** — Emit warnings early, not after overspending
3. **Not logging decisions** — Without decision log, debugging and improvement are impossible
4. **Over-revising** — After 3 revisions, proceed with warnings rather than infinite loops
5. **Ignoring sub-stage conditions** — Sub-stages exist for a reason; respect their conditions
6. **Not enforcing human approval gates** — Creative stages always require human approval