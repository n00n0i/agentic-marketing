# Reviewer Meta Skill — CHAI Quality Gate

## Role

Every artifact in the marketing pipeline must pass through this reviewer before proceeding to the next stage. The reviewer enforces quality standards and can send artifacts back for revision.

## CHAI Framework

Each review is scored on 5 dimensions:

| Letter | Dimension | What It Means |
|--------|-----------|--------------|
| **C** | **Consistent** | Consistent with previous artifacts, brand guidelines, and core message |
| **H** | **Helpful** | Provides genuine value to the target audience |
| **A** | **Accurate** | Facts are verifiable, claims are backed by data |
| **I** | **Insightful** | Offers genuine insight, not generic advice anyone could say |
| **C** | **Constructive** | Leads to actionable next steps |

## Review Process

### Step 1: Load Review Context

```python
review_context = {
    "artifact_type": "copy_variants",
    "artifact_version": "1.0",
    "stage": "copy",
    "market_brief_ref": "mb-001",
    "content_brief_ref": "cb-001",
    "brand_guidelines_ref": "bg-001",
    "review_round": 1,
}
```

### Step 2: Artifact-Specific Checks

**For market_brief:**
```python
checks = [
    {
        "check_id": "mb-audience-depth",
        "criterion": "≥3 audience segments with specific demographics, psychographics, behavioral",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "mb-competitor-evidence",
        "criterion": "≥5 competitors with real URLs and content examples",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "mb-angle-grounding",
        "criterion": "Each angle has ≥2 supporting data points",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "mb-keyword-data",
        "criterion": "Keywords include volume, difficulty, intent",
        "severity": "major",
        "findings": [],
    },
    {
        "check_id": "mb-timing-rationale",
        "criterion": "Timing recommendations backed by research",
        "severity": "major",
        "findings": [],
    },
]
```

**For copy_variants:**
```python
checks = [
    {
        "check_id": "cv-variant-distinctness",
        "criterion": "Each variant has distinct approach (not just rewording)",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "cv-cta-specificity",
        "criterion": "Every CTA is specific and action-oriented",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "cv-platform-compliance",
        "criterion": "Length and format appropriate for each platform",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "cv-brand-voice",
        "criterion": "All variants follow brand voice guidelines",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "cv-data-grounding",
        "criterion": "Claims backed by market_brief data",
        "severity": "major",
        "findings": [],
    },
    {
        "check_id": "cv-engagement-honesty",
        "criterion": "Engagement scores are realistic",
        "severity": "minor",
        "findings": [],
    },
]
```

**For creative_assets:**
```python
checks = [
    {
        "check_id": "ca-visual-copy-match",
        "criterion": "Visual reflects the variant's message",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "ca-format-correct",
        "criterion": "Dimensions correct for each platform",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "ca-brand-compliance",
        "criterion": "Colors, fonts, logo usage correct",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "ca-cta-visible",
        "criterion": "CTA clearly visible in all formats",
        "severity": "critical",
        "findings": [],
    },
    {
        "check_id": "ca-mobile-readability",
        "criterion": "Text large enough for mobile viewing",
        "severity": "major",
        "findings": [],
    },
]
```

### Step 3: Severity Classification

| Severity | Meaning | Action |
|----------|---------|--------|
| **critical** | Must fix before approval | Send back for revision |
| **major** | Should fix | Can approve with warnings |
| **minor** | Nice to fix | Can approve as-is |

### Step 4: Scoring

```python
def calculate_chai_score(findings):
    if not findings:
        return {"C": 10, "H": 10, "A": 10, "I": 10, "C": 10}

    score = {"C": 10, "H": 10, "A": 10, "I": 10, "C": 10}

    for finding in findings:
        severity = finding["severity"]
        dimension = finding["dimension"]

        if severity == "critical":
            score[dimension] -= 4
        elif severity == "major":
            score[dimension] -= 2
        elif severity == "minor":
            score[dimension] -= 1

    # Clamp to 0-10
    for k in score:
        score[k] = max(0, min(10, score[k]))

    return score
```

### Step 5: Decision

```python
def make_review_decision(checks, chai_score):
    critical_issues = [c for c in checks if c["severity"] == "critical" and c["findings"]]

    if critical_issues:
        return {
            "decision": "REVISE",
            "reason": f"{len(critical_issues)} critical issue(s) must be addressed",
            "can_approve_with_warnings": False,
            "feedback": format_feedback(critical_issues),
        }

    major_issues = [c for c in checks if c["severity"] == "major" and c["findings"]]

    if major_issues:
        return {
            "decision": "APPROVE_WITH_WARNINGS",
            "reason": f"{len(major_issues)} major issue(s) noted",
            "can_approve_with_warnings": True,
            "warnings": format_feedback(major_issues),
        }

    return {
        "decision": "APPROVE",
        "reason": "All critical and major checks passed",
        "warnings": []
    }
```

## Review Output Format

```json
{
  "version": "1.0",
  "review_id": "rev-copy-001",
  "artifact_type": "copy_variants",
  "artifact_ref": "cv-001",
  "stage": "copy",
  "review_round": 1,
  "review_timestamp": "2026-05-14T10:30:00Z",

  "chai_score": {
    "C": 8,
    "H": 9,
    "A": 8,
    "I": 7,
    "C": 8,
    "overall": 8.0
  },

  "checks": [
    {
      "check_id": "cv-cta-specificity",
      "criterion": "Every CTA is specific and action-oriented",
      "status": "fail",
      "severity": "critical",
      "findings": [
        {
          "variant_id": "var-twitter-B",
          "issue": "CTA is generic 'learn more'",
          "suggestion": "Change to 'Get the Churn Prevention Guide'"
        }
      ]
    },
    {
      "check_id": "cv-variant-distinctness",
      "criterion": "Each variant has distinct approach",
      "status": "pass",
      "severity": "critical",
      "findings": []
    }
  ],

  "decision": {
    "outcome": "REVISE",
    "reason": "1 critical issue(s) must be addressed",
    "can_approve_with_warnings": false
  },

  "feedback": [
    {
      "priority": 1,
      "variant_id": "var-twitter-B",
      "issue": "CTA is generic 'learn more'",
      "suggestion": "Change to 'Get the Churn Prevention Guide' — be specific about what they get"
    }
  ],

  "revision_round_limit": 3,
  "revision_round_current": 1
}
```

## Revision Protocol

```python
REVISION_PROTOCOL = {
    "max_rounds": 3,
    "escalation_after_3": "PASS_WITH_WARNINGS",

    "feedback_package": {
        "must_fix": [],    # Critical findings — must address
        "should_fix": [],  # Major findings — try to address
        "consider_fix": [] # Minor findings — if easy
    },

    "director_response": {
        "addressed": [],    # Feedback addressed
        "not_addressed": [], # Feedback not addressed with reasoning
        "new_issues": []    # New issues discovered during revision
    }
}
```

## Decision Rules

1. **0 critical findings** → APPROVE
2. **1+ critical findings** → REVISE (unless round ≥ 3, then PASS_WITH_WARNINGS)
3. **0 critical, 1+ major** → APPROVE_WITH_WARNINGS
4. **Round ≥ 3 with unresolved criticals** → PASS_WITH_WARNINGS (block only if safety issue)

## CHAI Dimension Guide

### Consistent
- Aligns with brand voice and guidelines
- Reinforces core message from market_brief
- Follows format and length guidelines
- Consistent terminology throughout

### Helpful
- Provides value to the target audience segment
- Answers a real question or solves a real problem
- Actionable insights, not just information
- Relevant to where they are in their journey

### Accurate
- Facts are verifiable with sources cited
- Statistics match cited sources
- No overgeneralization or false claims
- Claims are appropriately qualified

### Insightful
- Offers perspective not commonly available
- Goes beyond generic advice
- Connects dots in a new way
- Challenges assumptions constructively

### Constructive
- Leads to clear next steps
- CTA is specific and actionable
- Provides path to learn more
- Empowers the audience to act