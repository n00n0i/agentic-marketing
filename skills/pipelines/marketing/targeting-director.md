# Targeting Director — Paid Audience Targeting

## Role

Transforms `market_brief` into detailed targeting profiles for paid advertising campaigns. Produces `targeting_profile` artifact that defines demographics, interests, lookalike audiences, and bid strategy.

## Input

- `market_brief` — audience segments with demographics/psychographics
- `channel_strategy` — budget allocation and campaign objectives
- `content_brief` — the ad creative this targeting supports

## Process

### Step 1: Segment Prioritization

From `market_brief`, prioritize audience segments for paid targeting:

```python
def score_segment_for_paid(segment):
    """Score how well a segment fits paid advertising."""
    score = 0

    # Size matters for paid — need enough reach
    if segment.get("size_estimate", {}).get("SAM"):
        score += 2

    # Digital natives easier to target online
    if "digital" in segment.get("behavioral", {}).get("platforms", []):
        score += 2

    # B2B decision makers have high LTV for paid
    if segment.get("demographics", {}).get("role") in ["Founder", "VP", "Director"]:
        score += 2

    # Clear pain points = easier ad messaging
    if len(segment.get("psychographics", {}).get("fears", [])) >= 2:
        score += 1

    return score
```

### Step 2: Platform Targeting Parameters

For each paid platform, define targeting:

**Meta Ads:**
```python
meta_targeting = {
    "demographics": {
        "age_min": 28,
        "age_max": 48,
        "locations": ["United States", "United Kingdom"],
        "languages": ["English"],
    },
    "interests": [
        "SaaS",
        "Business Intelligence",
        "Cloud Computing",
        "Startup",
        "Business Software",
    ],
    "behaviors": [
        "Business decision makers",
        "Technology users",
    ],
    "exclusions": {
        "age_max": 24,
        "interests": ["Gaming", "Entertainment"],
    }
}
```

**Google Ads:**
```python
google_targeting = {
    "keywords": [
        "SaaS ops automation",
        "reduce SaaS costs",
        "automate SaaS workflows",
        "AI for SaaS",
    ],
    "audience_signals": ["in-market for business software"],
    "demographics": {
        "age_range": "28-48",
        "company_sizes": ["11-200", "201-1000"],
    }
}
```

**LinkedIn Ads:**
```python
linkedin_targeting = {
    "demographics": {
        "company_sizes": ["11-200", "201-1000"],
        "job_titles": ["VP Engineering", "Director of Operations", "CEO", "CTO"],
        "industries": ["Software", "Technology", "Internet"],
        "seniority": ["Director", "VP", "C-Suite"],
    },
    "targeting_audience_size_estimate": "50k-150k",
    "match_rate_estimate": 0.15,  # 15% of audience will match
}
```

### Step 3: Lookalike Audience

Define lookalike audience sourcing:

```python
lookalike_config = {
    "source": "website_visitors" | "email_list" | "customer_list" | "engaged_audience",
    "platform": "meta" | "google" | "linkedin",
    "audience_size_tier": "1% (closest)" | "2%" | "3%" | "5% (widest)",
    "confidence": "high" | "medium" | "low",
}
```

### Step 4: Bid Strategy

```python
BID_STRATEGIES = {
    "awareness": {
        "objective": "reach",
        "bid_method": "CPM",
        "target_cost": 10-15,
        "notes": "Optimize for impressions, not clicks"
    },
    "consideration": {
        "objective": "engagement",
        "bid_method": "CPC",
        "target_cost": 1.5-3.0,
        "notes": "Optimize for website clicks or video views"
    },
    "conversion": {
        "objective": "conversion",
        "bid_method": "CPA",
        "target_cost": 15-30,
        "notes": "Optimize for leads or purchases"
    },
    "retargeting": {
        "objective": "conversion",
        "bid_method": "CPM or CPA",
        "target_cost": 5-10,
        "notes": "Warm audience, higher intent"
    }
}
```

### Step 5: Budget Split

```python
def allocate_paid_budget(total_paid_budget, targeting_profiles):
    """Split budget across targeting profiles and campaign types."""
    allocation = {
        "awareness": total_paid_budget * 0.30,
        "remarketing": total_paid_budget * 0.30,
        "conversion": total_paid_budget * 0.40,
    }

    per_profile = {}
    for profile_id, profile in targeting_profiles.items():
        audience_size = profile.get("estimated_audience_size", 100000)
        # Proportional allocation based on audience size
        total_audience = sum(p.get("estimated_audience_size", 100000) for p in targeting_profiles.values())
        per_profile[profile_id] = (audience_size / total_audience) * allocation[profile.get("objective", "conversion")]

    return allocation, per_profile
```

## Output: targeting_profile Artifact

```json
{
  "version": "1.0",
  "profile_id": "tgt-001",
  "market_brief_ref": "mb-001",
  "content_brief_ref": "cb-001",
  "campaign_objective": "conversion",

  "audience_segments": [
    {
      "segment_ref": "seg-1",
      "name": "B2B SaaS Founders",
      "priority": 1,
      "allocation_pct": 60
    },
    {
      "segment_ref": "seg-2",
      "name": "Ops Managers at SaaS",
      "priority": 2,
      "allocation_pct": 40
    }
  ],

  "platforms": [
    {
      "platform": "meta_ads",
      "status": "active",
      "targeting": {
        "demographics": {
          "age_min": 28,
          "age_max": 48,
          "locations": ["United States", "United Kingdom"],
          "languages": ["English"]
        },
        "interests": [
          {"name": "SaaS", "type": "interest", "audience_size": "50M+"},
          {"name": "Business Intelligence", "type": "interest", "audience_size": "20M+"},
          {"name": "Cloud Computing", "type": "interest", "audience_size": "30M+"},
          {"name": "Startup", "type": "interest", "audience_size": "15M+"}
        ],
        "behaviors": ["Business decision makers", "Technology users"],
        "exclusions": {
          "age_max": 24,
          "interests": ["Gaming", "Entertainment", "Politics"]
        }
      },
      "estimated_audience_size": 150000,
      "match_rate_estimate": 0.12,
      "reach_estimate": 18000,
      "budget_allocation_usd": 320
    },
    {
      "platform": "google_ads",
      "status": "active",
      "targeting": {
        "keywords": [
          {"keyword": "SaaS ops automation", "match_type": "exact", "bid": 8.50},
          {"keyword": "reduce SaaS costs", "match_type": "phrase", "bid": 6.00},
          {"keyword": "automate SaaS workflows", "match_type": "phrase", "bid": 5.50},
          {"keyword": "AI for SaaS ops", "match_type": "broad", "bid": 4.00}
        ],
        "in_market_segments": ["Business Software Buyers"],
        "demographics": {
          "company_sizes": ["11-200", "201-1000"]
        }
      },
      "estimated_audience_size": 45000,
      "match_rate_estimate": 0.08,
      "reach_estimate": 3600,
      "budget_allocation_usd": 240
    },
    {
      "platform": "linkedin_ads",
      "status": "active",
      "targeting": {
        "demographics": {
          "job_titles": ["VP Engineering", "Director of Operations", "CEO", "CTO", "Head of Product"],
          "company_sizes": ["11-200", "201-1000"],
          "industries": ["Software", "Technology", "Internet", "Computer & Network Security"],
          "seniority": ["Director", "VP", "C-Suite"]
        },
        "targeting_dimension": "Audience Network"
      },
      "estimated_audience_size": 35000,
      "match_rate_estimate": 0.05,
      "reach_estimate": 1750,
      "budget_allocation_usd": 240
    }
  ],

  "lookalike_audiences": [
    {
      "platform": "meta",
      "source": "email_list",
      "tier": "2%",
      "confidence": "medium",
      "estimated_size": 50000
    },
    {
      "platform": "google",
      "source": "website_visitors",
      "tier": "similar_segments",
      "confidence": "medium",
      "estimated_size": 30000
    }
  ],

  "bid_strategies": {
    "meta_ads": {
      "primary_objective": "conversions",
      "bid_method": "CPA_target",
      "target_cpa_usd": 25,
      "bid_ceiling_usd": 40,
      "strategy_notes": "Start with CPA bidding, switch to manual CPC for testing"
    },
    "google_ads": {
      "primary_objective": "conversions",
      "bid_method": "target_cpa",
      "target_cpa_usd": 30,
      "campaign_types": ["Search", "Display", "YouTube"]
    },
    "linkedin_ads": {
      "primary_objective": "lead_generation",
      "bid_method": "CPC",
      "target_cpc_usd": 12,
      "bid_ceiling_usd": 20,
      "strategy_notes": "Higher CPC for decision-maker targeting is expected; optimize for lead quality not quantity"
    }
  },

  "budget_summary": {
    "total_paid_budget_usd": 800,
    "allocation": {
      "meta_ads": {"usd": 320, "pct": 40},
      "google_ads": {"usd": 240, "pct": 30},
      "linkedin_ads": {"usd": 240, "pct": 30}
    },
    "estimated_cpa_avg": 22.50,
    "estimated_total_conversions": 35
  },

  "compliance_check": {
    "gdpr_compliant": true,
    "ccpa_compliant": true,
    "platform_policies_verified": true,
    "notes": "All targeting excludes sensitive categories per GDPR; age minimum 28 applied"
  },

  "creative_direction_hints": {
    "tone": "Professional, data-driven, not salesy",
    "cta_directives": [
      "Demo request (high-intent, lower volume)",
      "Free audit offer (medium-intent, higher volume)"
    ],
    "visual_preferences": ["Clean, modern, tech-forward imagery", "Charts/graphs showing ROI", "Real people, not stock photos"]
  }
}
```

## Review Focus

Before approving targeting_profile, reviewer MUST verify:

1. **Demographics backed by data** — Are age/location/role selections justified by market_brief?
2. **Budget proportional to audience** — Is budget allocation proportionate to estimated reach?
3. **Bid strategy appropriate** — Does bid strategy match campaign objective?
4. **Lookalike sourcing defined** — Is there a clear source for lookalike audiences?
5. **Compliance verified** — Are GDPR/CCPA requirements met?
6. **CPA targets realistic** — Are CPA targets achievable given competition?

## Success Criteria

- ≥1 targeting profile per active paid channel
- Audience size estimates are data-backed
- Budget split proportional to reach potential
- Bid strategy appropriate for campaign objective
- Compliance requirements verified
- Creative direction hints included for ad creative director

## Common Pitfalls

1. **Too broad targeting** — Casting too wide reduces relevance and wastes budget
2. **Too narrow targeting** — Can't achieve scale or reach targets
3. **Ignoring exclusions** — Not excluding irrelevant audiences
4. **Bid strategy mismatch** — Using awareness bid strategy for conversion campaign
5. **No lookalike plan** — Missing opportunity to scale with proven audiences
6. **Unrealistic CPA targets** — Setting CPA too low for competitive categories