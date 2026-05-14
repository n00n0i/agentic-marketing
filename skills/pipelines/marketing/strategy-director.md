# Strategy Director — Channel Strategy & Budget Allocation

## Role

Transforms `market_brief` into a comprehensive `channel_strategy` that defines which channels to activate, how to allocate budget, and what content mix to use per channel.

## Inputs

- `market_brief` — audience segments, competitors, strategic angles
- `total_budget_usd` — budget for this campaign/period
- `campaign_objectives` — awareness, consideration, conversion, retention
- `timeline` — campaign duration

## Process

### Step 1: Objective Mapping

Map campaign objectives to channel roles:

```python
OBJECTIVE_CHANNEL_MAP = {
    "awareness": {
        "primary": ["linkedin", "facebook", "youtube"],
        "secondary": ["twitter", "instagram"],
        "kpis": ["impressions", "reach", "video_views", "brand_search"]
    },
    "consideration": {
        "primary": ["linkedin", "google_search", "email"],
        "secondary": ["twitter", "facebook"],
        "kpis": ["engagement_rate", "time_on_page", "email_subscribers", "demo_requests"]
    },
    "conversion": {
        "primary": ["google_ads", "meta_ads", "linkedin_ads"],
        "secondary": ["email", "retargeting"],
        "kpis": ["ctr", "conversion_rate", "cost_per_conversion", "roas"]
    },
    "retention": {
        "primary": ["email", "linkedin"],
        "secondary": ["community", "webinar"],
        "kpis": ["churn_rate", "nps", "engagement", "ltv"]
    }
}
```

### Step 2: Audience-Channel Fit

For each audience segment, identify best channels:

```python
def score_channel_fit(segment, channel):
    """Score 0-10 how well a channel fits an audience segment."""
    scores = {
        "demographic_match": 0-3,      # Does channel's user base match segment demographics?
        "intent_match": 0-3,           # Are they in buying mode on this channel?
        "content_preference": 0-2,     # Does segment prefer this content format?
        "competition_level": 0-2,      # Is this channel less saturated for our category?
    }
    return sum(scores.values())
```

### Step 3: Channel Selection

Select channels based on:

```python
selection_criteria = {
    "audience_reach": "Does channel reach our target segments?",
    "intent_signal": "Are users actively looking for solutions?",
    "content_fit": "Can we create compelling content for this channel?",
    "budget_efficiency": "Can we achieve desired outcomes within budget?",
    "competitive_landscape": "Is there opportunity to stand out?",
}
```

### Step 4: Budget Allocation

Allocate budget across channels using weighted scoring:

```python
def allocate_budget(total_budget, channel_scores, objectives):
    """Allocate budget proportionally to channel scores + objective weights."""

    # Base allocation by score
    base_allocation = {}
    total_score = sum(channel_scores.values())

    for channel, score in channel_scores.items():
        base_allocation[channel] = (score / total_score) * total_budget

    # Adjust for objective fit
    for channel, objective_weight in objective_weights.items():
        base_allocation[channel] *= (1 + objective_weight)

    # Apply min/max constraints
    for channel in base_allocation:
        base_allocation[channel] = min(
            max(base_allocation[channel], MIN_CHANNEL_SPEND),
            MAX_CHANNEL_SPEND
        )

    # Normalize to match total budget
    total_allocated = sum(base_allocation.values())
    adjustment_factor = total_budget / total_allocated

    for channel in base_allocation:
        base_allocation[channel] *= adjustment_factor

    return base_allocation
```

### Step 5: Content Mix Planning

Define content types per channel:

```python
CONTENT_MIX = {
    "linkedin": {
        "formats": ["article", "native_post", "carousel"],
        "ratio": {"educational": 0.4, "case_study": 0.3, "thought_leadership": 0.2, "promotional": 0.1},
        "posting_frequency": "3-5x/week",
        "best_days": ["tue", "wed", "thu"],
        "best_times": ["7am", "12pm", "5pm"]
    },
    "twitter": {
        "formats": ["thread", "single_tweet", "poll"],
        "ratio": {"insights": 0.4, "engagement": 0.2, "news_jacking": 0.2, "promotional": 0.2},
        "posting_frequency": "5-10x/day",
        "best_days": ["mon", "tue", "wed", "thu"],
        "best_times": ["8am", "12pm", "5pm"]
    },
    "facebook": {
        "formats": ["post", "video", "live"],
        "ratio": {"community": 0.4, "behind_scenes": 0.3, "educational": 0.2, "promotional": 0.1},
        "posting_frequency": "1x/day",
        "best_days": ["wed", "thu", "sun"],
        "best_times": ["1pm", "4pm"]
    },
    "instagram": {
        "formats": ["feed_post", "story", "reel", "carousel"],
        "ratio": {"visual_education": 0.3, "quotes": 0.2, "behind_scenes": 0.2, "ugc": 0.15, "promotional": 0.15},
        "posting_frequency": "1x/day",
        "best_days": ["tue", "wed", "thu", "sat"],
        "best_times": ["11am", "1pm", "7pm"]
    },
    "google_ads": {
        "formats": ["search", "display", "shopping"],
        "ratio": {"brand": 0.2, "generic": 0.3, "competitor": 0.2, "remarketing": 0.3},
        "bid_strategy": "Based on objective (conversions vs visibility)"
    },
    "meta_ads": {
        "formats": ["single_image", "carousel", "video", "collection"],
        "ratio": {"awareness": 0.3, "consideration": 0.4, "conversion": 0.3},
        "optimization_goal": "Based on funnel stage"
    },
    "email": {
        "formats": ["newsletter", "promotional", "automated_sequence"],
        "ratio": {"value_add": 0.6, "promotional": 0.4},
        "frequency": "1-2x/week",
        "send_days": ["tue", "wed", "thu"]
    }
}
```

### Step 6: Cadence Planning

Create a content calendar:

```python
def plan_cadence(channel_strategy, timeline_days):
    """Generate content posting schedule."""

    calendar = []
    for day in range(timeline_days):
        for channel in channel_strategy["channels"]:
            if should_post_today(channel, day, channel_strategy):
                calendar.append({
                    "day": day,
                    "channel": channel,
                    "content_type": select_content_type(channel, calendar),
                    "notes": f"Post for {channel} - {content_type}"
                })

    return calendar
```

## Output: channel_strategy Artifact

```json
{
  "version": "1.0",
  "strategy_id": "strat-001",
  "market_brief_ref": "mb-001",
  "objectives": ["awareness", "consideration"],
  "timeline": {
    "start_date": "2026-05-20",
    "end_date": "2026-06-20",
    "duration_days": 31
  },

  "channels": [
    {
      "channel_id": "ch-linkedin",
      "platform": "linkedin",
      "role": "primary",
      "objective_fit": ["awareness", "consideration"],
      "audience_segments": ["seg-1", "seg-2"],
      "status": "active",
      "budget": {
        "allocated_usd": 600,
        "percentage": 30,
        "breakdown": {
          "organic_content": 200,
          "promoted_content": 300,
          "tools": 100
        }
      },
      "content_mix": {
        "formats": ["article", "native_post", "carousel"],
        "ratio": {"educational": 0.4, "case_study": 0.3, "thought_leadership": 0.2, "promotional": 0.1}
      },
      "cadence": {
        "posting_frequency": "4x/week",
        "best_days": ["tue", "wed", "thu"],
        "best_times": ["7am", "12pm", "5pm EST"]
      },
      "kpis": {
        "impressions_target": 50000,
        "engagement_rate_target": 3.5,
        "follower_growth_target": 500
      }
    },
    {
      "channel_id": "ch-twitter",
      "platform": "twitter",
      "role": "secondary",
      "objective_fit": ["awareness"],
      "audience_segments": ["seg-1", "seg-3"],
      "status": "active",
      "budget": {
        "allocated_usd": 200,
        "percentage": 10,
        "breakdown": {
          "tools": 100,
          "promoted_tweets": 100
        }
      },
      "content_mix": {
        "formats": ["thread", "single_tweet", "poll"],
        "ratio": {"insights": 0.4, "engagement": 0.2, "news_jacking": 0.2, "promotional": 0.2}
      },
      "cadence": {
        "posting_frequency": "7x/day",
        "best_days": ["mon", "tue", "wed", "thu"],
        "best_times": ["8am", "12pm", "5pm EST"]
      },
      "kpis": {
        "impressions_target": 100000,
        "engagement_rate_target": 2.0,
        "follower_growth_target": 300
      }
    },
    {
      "channel_id": "ch-meta",
      "platform": "meta_ads",
      "role": "primary",
      "objective_fit": ["conversion"],
      "audience_segments": ["seg-1"],
      "status": "active",
      "budget": {
        "allocated_usd": 800,
        "percentage": 40,
        "breakdown": {
          "awareness_ads": 240,
          "retargeting_ads": 400,
          "conversion_ads": 160
        }
      },
      "ad_formats": ["single_image", "carousel", "video"],
      "bid_strategy": {
        "awareness": "CPM optimized",
        "retargeting": "CPC optimized",
        "conversion": "CPA optimized"
      },
      "kpis": {
        "impressions_target": 200000,
        "ctr_target": 1.5,
        "conversion_target": 50,
        "cpa_target": 16
      }
    },
    {
      "channel_id": "ch-email",
      "platform": "email",
      "role": "primary",
      "objective_fit": ["consideration", "conversion", "retention"],
      "audience_segments": ["seg-1", "seg-2"],
      "status": "active",
      "budget": {
        "allocated_usd": 100,
        "percentage": 5,
        "breakdown": {
          "platform_cost": 50,
          "templates": 50
        }
      },
      "content_mix": {
        "formats": ["newsletter", "promotional", "automated_sequence"],
        "ratio": {"value_add": 0.6, "promotional": 0.4}
      },
      "cadence": {
        "frequency": "2x/week",
        "send_days": ["tue", "thu"]
      },
      "sequences": [
        {
          "name": "welcome_sequence",
          "emails": 5,
          "trigger": "new_subscriber"
        },
        {
          "name": "nurture_sequence",
          "emails": 7,
          "trigger": "download_gated_content"
        }
      ],
      "kpis": {
        "subscriber_growth_target": 200,
        "open_rate_target": 25,
        "ctr_target": 5,
        "conversion_target": 20
      }
    },
    {
      "channel_id": "ch-instagram",
      "platform": "instagram",
      "role": "secondary",
      "objective_fit": ["awareness", "consideration"],
      "audience_segments": ["seg-2", "seg-3"],
      "status": "passive",
      "budget": {
        "allocated_usd": 100,
        "percentage": 5,
        "breakdown": {
          "promoted_posts": 100
        }
      },
      "content_mix": {
        "formats": ["feed_post", "reel", "carousel"],
        "ratio": {"visual_education": 0.3, "quotes": 0.2, "behind_scenes": 0.2, "ugc": 0.15, "promotional": 0.15}
      },
      "cadence": {
        "posting_frequency": "1x/day",
        "best_days": ["tue", "wed", "thu", "sat"],
        "best_times": ["11am", "1pm", "7pm EST"]
      },
      "kpis": {
        "impressions_target": 30000,
        "engagement_rate_target": 4.0,
        "follower_growth_target": 200
      }
    }
  ],

  "budget_summary": {
    "total_budget_usd": 2000,
    "allocation": {
      "organic": {"usd": 1000, "percentage": 50},
      "paid": {"usd": 800, "percentage": 40},
      "email": {"usd": 100, "percentage": 5},
      "reserve": {"usd": 100, "percentage": 5}
    },
    "reserve_purpose": "Unexpected opportunities, A/B testing winner amplification"
  },

  "cross_channel_coherence": {
    "core_message": "AI automation cuts SaaS ops costs by 40%",
    "sequential_flow": "LinkedIn (awareness) → Email (consideration) → Meta (conversion) → Retargeting (close)",
    "consistency_check": "All channels reinforce same value proposition",
    "visual_identity": "Brand guidelines applied across all channels"
  },

  "risk_factors": [
    {
      "risk": "LinkedIn algorithm changes reduce organic reach",
      "mitigation": "Allocate 30% of LinkedIn budget to promoted content",
      "contingency": "Increase Twitter activity to compensate"
    },
    {
      "risk": "Meta ads cost inflation during high-competition periods",
      "mitigation": "Set bid caps and use flexible budget",
      "contingency": "Shift budget to LinkedIn if CPA exceeds $20"
    }
  ],

  "approval_required": true,
  "approval_deadline": "2026-05-15"
}
```

## Review Focus

Before approving channel_strategy, reviewer MUST verify:

1. **Channel selection justified** — Do we have audience overlap data for each channel?
2. **Budget allocation explained** — Is each channel's budget proportionate to expected ROI?
3. **Content mix realistic** — Can we actually produce the planned content?
4. **Timing plan feasible** — Is the posting cadence achievable with available resources?
5. **KPIs measurable** — Are targets specific and trackable?

## Success Criteria

- All target audience segments covered by at least one active channel
- Budget allocation balanced across channels
- Content mix defined per channel
- Cadence plan realistic and executable
- KPIs are specific and measurable
- Cross-channel coherence verified
- Risk factors identified with mitigations

## Common Pitfalls

1. **Channel overkill** — Trying to be on every platform
2. **Budget misallocation** — Spending too much on awareness when conversion is the goal
3. **Unbalanced mix** — Too much promotional, not enough value-add
4. **Unrealistic cadence** — Planning 10 posts/day with limited content team
5. **No reserve** — Spending entire budget with no buffer for opportunities