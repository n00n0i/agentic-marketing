# Analytics Director — Engagement Tracking & Performance Metrics

## Role

Tracks engagement metrics across all published content, calculates ROI, identifies top-performing content, and generates performance reports. Produces `performance_report` artifact that feeds back into future content decisions.

## Input

- `publish_log` — what was published, when, where
- `platform_analytics` — native analytics data from each platform
- `budget_transactions` — cost data for ROI calculation

## Process

### Step 1: Data Collection

```python
PLATFORM_ANALYTICS_APIS = {
    "twitter": {
        "api": TwitterAnalyticsAPI,
        "metrics": ["impressions", "engagements", "profile_visits", "mentions", "retweets", "likes", "replies", "url_clicks"],
        "delay_hours": 24
    },
    "linkedin": {
        "api": LinkedInAnalyticsAPI,
        "metrics": ["impressions", "clicks", "engagement_rate", "reactions", "comments", "shares"],
        "delay_hours": 24
    },
    "facebook": {
        "api": MetaInsightsAPI,
        "metrics": ["reach", "impressions", "engagements", "clicks", "shares", "comments", "reactions"],
        "delay_hours": 24
    },
    "instagram": {
        "api": MetaInsightsAPI,
        "metrics": ["reach", "impressions", "engagements", "profile_visits", "website_clicks"],
        "delay_hours": 24
    },
    "email": {
        "api": KlaviyoAPI,
        "metrics": ["sent", "delivered", "opened", "clicked", "bounced", "unsubscribed"],
        "delay_hours": 2
    },
    "google_ads": {
        "api": GoogleAdsAPI,
        "metrics": ["impressions", "clicks", "cpc", "ctr", "conversions", "cost", "roas"],
        "delay_hours": 6
    },
    "meta_ads": {
        "api": MetaAdsAPI,
        "metrics": ["impressions", "reach", "clicks", "cpc", "ctr", "conversions", "cost", "frequency"],
        "delay_hours": 6
    }
}

def collect_analytics(publish_log, platforms):
    """Collect analytics data from all active platforms."""
    results = {}
    for platform, api_class in PLATFORM_ANALYTICS_APIS.items():
        if platform not in platforms:
            continue

        api = api_class()
        for publication in publish_log.publications:
            if publication.platform != platform:
                continue

            try:
                metrics = api.get_metrics(
                    post_id=publication.post_id,
                    date_range="7_days"
                )
                results[publication.publication_id] = {
                    "platform": platform,
                    "metrics": metrics,
                    "collected_at": datetime.now(timezone.utc)
                }
            except Exception as e:
                logger.warning("analytics_collection_failed", platform=platform, error=str(e))

    return results
```

### Step 2: Performance Scoring

```python
def calculate_engagement_rate(publication, metrics):
    """Calculate engagement rate for a publication."""
    if publication.platform == "email":
        # Email engagement = opens + clicks / delivered
        opens = metrics.get("opened", 0)
        clicks = metrics.get("clicked", 0)
        delivered = metrics.get("delivered", 1)
        return (opens + clicks) / delivered * 100
    else:
        # Social engagement = engagements / impressions
        engagements = metrics.get("engagements", 0)
        impressions = metrics.get("impressions", 1)
        return engagements / impressions * 100


def score_content_performance(publication, metrics, benchmarks):
    """Score content performance relative to platform benchmarks."""
    engagement_rate = calculate_engagement_rate(publication, metrics)

    platform_benchmark = benchmarks.get(publication.platform, {})
    benchmark_rate = platform_benchmark.get("engagement_rate", 2.0)

    # Normalize to 0-100 scale
    if engagement_rate >= benchmark_rate * 2:
        return 90  # exceptional
    elif engagement_rate >= benchmark_rate * 1.5:
        return 75  # above average
    elif engagement_rate >= benchmark_rate:
        return 60  # average
    elif engagement_rate >= benchmark_rate * 0.5:
        return 40  # below average
    else:
        return 20  # poor


ENGAGEMENT_BENCHMARKS = {
    "twitter": {"engagement_rate": 0.5, "ctr": 2.0},
    "linkedin": {"engagement_rate": 2.0, "ctr": 0.5},
    "facebook": {"engagement_rate": 1.0, "ctr": 1.0},
    "instagram": {"engagement_rate": 3.0, "ctr": 1.5},
    "email": {"open_rate": 20.0, "click_rate": 2.5},
    "google_ads": {"ctr": 5.0, "conversion_rate": 3.0},
    "meta_ads": {"ctr": 1.0, "conversion_rate": 2.0}
}
```

### Step 3: A/B Performance Analysis

```python
def analyze_ab_performance(copy_variants, analytics_data):
    """Analyze which copy variant performed better."""
    results = {}

    for variant_id, variant_analytics in analytics_data.items():
        variant = next(v for v in copy_variants if v.variant_id == variant_id)
        variant_engagement = calculate_engagement_rate(variant, variant_analytics["metrics"])
        results[variant_id] = {
            "variant_id": variant_id,
            "engagement_rate": variant_engagement,
            "metrics": variant_analytics["metrics"],
            "winner": False
        }

    # Find winner
    if results:
        winner_id = max(results, key=lambda k: results[k]["engagement_rate"])
        results[winner_id]["winner"] = True

    return results
```

### Step 4: ROI Calculation

```python
def calculate_content_roi(publish_log, budget_transactions, conversion_data):
    """Calculate ROI for content and channels."""
    total_cost = sum(tx.amount_usd for tx in budget_transactions)
    total_conversions = sum(conversion_data.values())
    average_order_value = 100  # Would come from actual data

    revenue = total_conversions * average_order_value
    roi = (revenue - total_cost) / total_cost * 100 if total_cost > 0 else 0

    cost_per_channel = {}
    for channel in ["organic", "paid", "email"]:
        channel_cost = sum(
            tx.amount_usd for tx in budget_transactions
            if tx.channel == channel
        )
        channel_conversions = sum(
            v for k, v in conversion_data.items()
            if k.startswith(channel)
        )
        cost_per_channel[channel] = {
            "cost": channel_cost,
            "conversions": channel_conversions,
            "cpa": channel_cost / channel_conversions if channel_conversions > 0 else 0
        }

    return {
        "total_cost": total_cost,
        "total_conversions": total_conversions,
        "revenue": revenue,
        "roi_pct": roi,
        "by_channel": cost_per_channel
    }
```

### Step 5: Content Recommendations

```python
def generate_content_recommendations(analytics_data, ab_analysis):
    """Generate recommendations for future content based on performance data."""
    recommendations = []

    # Find top performing content
    for pub_id, metrics in analytics_data.items():
        score = score_content_performance(pub_id, metrics)
        if score >= 75:
            recommendations.append({
                "type": "replicate_success",
                "content_id": pub_id,
                "reason": f"High engagement score: {score}/100",
                "suggestion": "Create similar content with same angle/format"
            })

    # Find underperforming content
    for pub_id, metrics in analytics_data.items():
        score = score_content_performance(pub_id, metrics)
        if score < 40:
            recommendations.append({
                "type": "improve_underperformers",
                "content_id": pub_id,
                "reason": f"Low engagement score: {score}/100",
                "suggestion": "A/B test different angles or formats"
            })

    # A/B winner recommendations
    for variant_id, result in ab_analysis.items():
        if result["winner"]:
            recommendations.append({
                "type": "use_winning_variant",
                "variant_id": variant_id,
                "reason": f"Highest engagement: {result['engagement_rate']:.2f}%",
                "suggestion": "Use this variant as control for future A/B tests"
            })

    return recommendations
```

## Output: performance_report Artifact

```json
{
  "version": "1.0",
  "report_id": "perf-001",
  "report_period": {
    "start": "2026-05-07T00:00:00Z",
    "end": "2026-05-14T00:00:00Z",
    "days": 7
  },
  "publish_log_refs": ["pub-001", "pub-002"],

  "summary": {
    "total_content_pieces": 6,
    "total_impressions": 45230,
    "total_engagements": 1847,
    "overall_engagement_rate": 4.08,
    "total_conversions": 47,
    "total_cost_usd": 8.50,
    "calculated_roi_pct": 235
  },

  "by_platform": {
    "twitter": {
      "content_count": 2,
      "impressions": 12450,
      "engagements": 487,
      "engagement_rate": 3.91,
      "top_post": "pub-twitter-001",
      "benchmark_engagement_rate": 0.5,
      "vs_benchmark": "+682%"
    },
    "linkedin": {
      "content_count": 2,
      "impressions": 8500,
      "engagements": 425,
      "engagement_rate": 5.0,
      "top_post": "pub-linkedin-001",
      "benchmark_engagement_rate": 2.0,
      "vs_benchmark": "+150%"
    },
    "email": {
      "content_count": 1,
      "sent": 1250,
      "delivered": 1238,
      "opened": 433,
      "clicked": 86,
      "open_rate": 35.0,
      "click_rate": 6.95,
      "benchmark_open_rate": 20.0,
      "benchmark_click_rate": 2.5,
      "vs_benchmark_open": "+75%",
      "vs_benchmark_click": "+178%"
    },
    "google_ads": {
      "content_count": 1,
      "impressions": 18000,
      "clicks": 720,
      "ctr": 4.0,
      "conversions": 18,
      "cost_usd": 6.00,
      "cpc": 0.008,
      "cpa": 0.33,
      "benchmark_ctr": 5.0,
      "vs_benchmark": "-20%"
    },
    "meta_ads": {
      "content_count": 1,
      "impressions": 6280,
      "clicks": 215,
      "ctr": 3.42,
      "conversions": 29,
      "cost_usd": 2.50,
      "cpc": 0.011,
      "cpa": 0.08,
      "benchmark_ctr": 1.0,
      "vs_benchmark": "+242%"
    }
  },

  "top_performing_content": [
    {
      "rank": 1,
      "publication_id": "pub-email-001",
      "platform": "email",
      "headline": "The 15-hour problem",
      "engagement_rate": 41.9,
      "open_rate": 35.0,
      "click_rate": 6.95,
      "score": 88
    },
    {
      "rank": 2,
      "publication_id": "pub-linkedin-001",
      "platform": "linkedin",
      "headline": "Your SaaS team is probably wasting 15 hours...",
      "engagement_rate": 5.0,
      "impressions": 4800,
      "engagements": 240,
      "score": 85
    }
  ],

  "underperforming_content": [
    {
      "rank": 1,
      "publication_id": "pub-google-001",
      "platform": "google_ads",
      "headline": "Reduce SaaS Ops Costs 40%",
      "ctr": 4.0,
      "benchmark_ctr": 5.0,
      "score": 35,
      "reason": "CTR below benchmark",
      "recommendation": "Test different headline variations with stronger value propositions"
    }
  ],

  "ab_test_results": {
    "test_name": "headline_angle_ab",
    "test_content": ["pub-twitter-001", "pub-twitter-002"],
    "winner": "pub-twitter-001",
    "winner_headline": "Your SaaS team is probably wasting 15 hours...",
    "loser_headline": "Stop Wasting 15 Hours a Week on SaaS Ops",
    "engagement_difference_pct": 23.5,
    "statistical_significance": 0.94,
    "recommendation": "Use winning headline as control for future tests"
  },

  "roi_analysis": {
    "total_cost_usd": 8.50,
    "total_conversions": 47,
    "conversion_value_assumption_usd": 50,
    "estimated_revenue_usd": 2350,
    "roi_pct": 27529,
    "by_channel": {
      "organic": {"cost": 0.00, "conversions": 18, "cpa": 0.00},
      "paid": {"cost": 8.50, "conversions": 29, "cpa": 0.29},
      "email": {"cost": 0.00, "conversions": 0, "cpa": 0.00}
    }
  },

  "content_recommendations": [
    {
      "type": "replicate_success",
      "priority": "high",
      "content_id": "pub-email-001",
      "reason": "Highest engagement score: 88/100",
      "action": "Create similar email sequences with problem-solution framing"
    },
    {
      "type": "improve_underperformers",
      "priority": "medium",
      "content_id": "pub-google-001",
      "reason": "CTR 20% below benchmark",
      "action": "A/B test headline variations emphasizing specific results"
    },
    {
      "type": "channel_focus",
      "priority": "high",
      "content": "Email",
      "reason": "Highest ROI channel in this period",
      "action": "Increase email send frequency from weekly to 2x/week"
    },
    {
      "type": "budget_reallocation",
      "priority": "medium",
      "content": "Meta Ads",
      "reason": "242% above benchmark CTR, low CPA ($0.08)",
      "action": "Increase Meta Ads budget by 30%"
    }
  ],

  "data_quality": {
    "completeness_pct": 95,
    "missing_data_platforms": [],
    "estimated_accuracy": "high",
    "notes": ["Google Ads data has 6-hour delay", "Conversion attribution is last-touch model"]
  }
}
```

## Review Focus

Before approving performance_report, reviewer MUST verify:

1. **Data completeness** — Are all publications included in analytics?
2. **Benchmarks appropriate** — Are platform benchmarks current and relevant?
3. **A/B significance** — Is statistical significance threshold met (>0.95)?
4. **Recommendations actionable** — Are recommendations specific and actionable?
5. **ROI assumptions stated** — Are conversion values and attribution models documented?
6. **Data quality noted** — Are data gaps and estimation methods documented?

## Success Criteria

- All published content has analytics data
- Engagement rates calculated and benchmarked
- A/B test results statistically valid
- ROI calculation with documented assumptions
- Content recommendations specific and actionable
- Data quality assessment included

## Common Pitfalls

1. **Missing analytics** — Publications not tracked due to API issues
2. **Wrong benchmarks** — Using outdated or wrong platform benchmarks
3. **Insufficient sample size** — A/B test results not statistically significant
4. **Attribution errors** — Wrong attribution model for conversions
5. **Vanity metrics focus** — Focusing on impressions instead of conversions
6. **No recommendations** — Reporting data but not generating insights