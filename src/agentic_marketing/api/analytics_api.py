"""Analytics API — FastAPI routes for analytics dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="Agentic Marketing Analytics API")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AnalyticsSummary(BaseModel):
    total_posts: int
    total_impressions: int
    avg_engagement: float
    top_platform: str
    period: str


class PlatformMetrics(BaseModel):
    platform: str
    posts: int
    impressions: int
    clicks: int
    engagement_rate: float


class CampaignMetrics(BaseModel):
    campaign_id: str
    name: str
    posts: int
    impressions: int
    engagement: float
    cost: float
    roi: float


# ---------------------------------------------------------------------------
# Mock data (replace with DB queries in production)
# ---------------------------------------------------------------------------

_MOCK_PLATFORMS: list[PlatformMetrics] = [
    PlatformMetrics(platform="LinkedIn", posts=52, impressions=38400, clicks=1820, engagement_rate=5.8),
    PlatformMetrics(platform="Twitter/X", posts=61, impressions=29300, clicks=1240, engagement_rate=4.9),
    PlatformMetrics(platform="Facebook", posts=22, impressions=12100, clicks=380, engagement_rate=3.2),
    PlatformMetrics(platform="Instagram", posts=12, impressions=4400, clicks=160, engagement_rate=5.1),
]

_MOCK_CAMPAIGNS: list[CampaignMetrics] = [
    CampaignMetrics(campaign_id="cmp_001", name="AI Automation Q2", posts=42, impressions=52100, engagement=4.9, cost=420.00, roi=312),
    CampaignMetrics(campaign_id="cmp_002", name="SaaS Lead Gen", posts=38, impressions=28700, engagement=4.1, cost=310.00, roi=198),
    CampaignMetrics(campaign_id="cmp_003", name="Brand Awareness", posts=67, impressions=3400, engagement=3.8, cost=180.00, roi=87),
]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/analytics/summary", response_model=AnalyticsSummary)
def get_analytics_summary(period: str = Query(default="30d")):
    """Return overall analytics summary."""
    total_posts = sum(p.posts for p in _MOCK_PLATFORMS)
    total_impressions = sum(p.impressions for p in _MOCK_PLATFORMS)
    total_engagement = sum(p.engagement_rate * p.posts for p in _MOCK_PLATFORMS)
    avg_engagement = total_engagement / total_posts if total_posts else 0

    top = max(_MOCK_PLATFORMS, key=lambda p: p.impressions)

    return AnalyticsSummary(
        total_posts=total_posts,
        total_impressions=total_impressions,
        avg_engagement=round(avg_engagement, 2),
        top_platform=top.platform,
        period=period,
    )


@app.get("/api/analytics/platforms", response_model=list[PlatformMetrics])
def get_platform_breakdown(platform: Optional[str] = None):
    """Return per-platform breakdown."""
    if platform:
        filtered = [p for p in _MOCK_PLATFORMS if p.platform.lower() == platform.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="Platform not found")
        return filtered
    return _MOCK_PLATFORMS


@app.get("/api/analytics/campaigns", response_model=list[CampaignMetrics])
def get_campaign_performance():
    """Return campaign performance metrics."""
    return _MOCK_CAMPAIGNS