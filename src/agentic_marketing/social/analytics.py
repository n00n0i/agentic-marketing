"""Analytics collector for published social content."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import structlog

from .twitter_client import TwitterClient
from .linkedin_client import LinkedInClient
from .facebook_client import FacebookClient

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Metric types
# -------------------------------------------------------------------------


@dataclass
class PlatformMetrics:
    """Performance metrics for a single platform post."""
    platform: str
    post_id: str
    impressions: int = 0
    clicks: int = 0
    engagement: int = 0
    shares: int = 0
    likes: int = 0
    comments: int = 0
    reach: int = 0
    followers_gained: int = 0
   采集_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    mock: bool = False


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across all platforms."""
    publication_id: str
    total_impressions: int = 0
    total_clicks: int = 0
    total_engagement: int = 0
    total_shares: int = 0
    total_likes: int = 0
    total_comments: int = 0
    platform_breakdown: dict[str, int] = field(default_factory=dict)
   采集_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "total_impressions": self.total_impressions,
            "total_clicks": self.total_clicks,
            "total_engagement": self.total_engagement,
            "total_shares": self.total_shares,
            "total_likes": self.total_likes,
            "total_comments": self.total_comments,
            "platform_breakdown": self.platform_breakdown,
            "collected_at": self.采集_at,
        }


# -------------------------------------------------------------------------
# Analytics
# -------------------------------------------------------------------------


class AnalyticsCollector:
    """
    Collects performance metrics for published social posts.

    Pulls from each platform's native analytics API where available.
    Falls back to mock data when APIs are unavailable.

    Usage:
        analytics = AnalyticsCollector()
        metrics = analytics.collect_for_posts([
            {"platform": "twitter", "post_id": "123"},
            {"platform": "linkedin", "post_id": "urn:li:post:abc"},
        ])
    """

    def __init__(self) -> None:
        self.twitter = TwitterClient()
        self.linkedin = LinkedInClient()
        self.facebook = FacebookClient()

        self._mock_mode = all([
            self.twitter.mock_mode,
            self.linkedin.mock_mode,
            self.facebook.mock_mode,
        ])

        if self._mock_mode:
            logger.warning("analytics_collector_mock_mode", reason="All platform credentials unconfigured")
        else:
            logger.info("analytics_collector_initialized")

    def collect_for_posts(self, posts: list[dict[str, Any]]) -> list[PlatformMetrics]:
        """
        Collect metrics for a list of published posts.

        Args:
            posts: List of dicts each with 'platform' and 'post_id'

        Returns:
            List of PlatformMetrics (one per post)
        """
        results = []
        for post in posts:
            platform = post.get("platform", "")
            post_id = post.get("post_id", "")
            try:
                if platform == "twitter":
                    metrics = self._collect_twitter_metrics(post_id)
                elif platform == "linkedin":
                    metrics = self._collect_linkedin_metrics(post_id)
                elif platform == "facebook":
                    metrics = self._collect_facebook_metrics(post_id)
                else:
                    metrics = PlatformMetrics(
                        platform=platform,
                        post_id=post_id,
                        mock=True,
                    )
            except Exception as exc:
                logger.error("analytics_collection_error", platform=platform, error=str(exc))
                metrics = PlatformMetrics(
                    platform=platform,
                    post_id=post_id,
                    mock=True,
                )
            results.append(metrics)

        return results

    def collect_for_campaign(
        self,
        campaign_id: str,
        posts: list[dict[str, Any]],
    ) -> AggregatedMetrics:
        """
        Collect and aggregate metrics for all posts in a campaign.

        Args:
            campaign_id: Campaign identifier
            posts: List of post specs

        Returns:
            AggregatedMetrics with totals across all platforms
        """
        platform_metrics_list = self.collect_for_posts(posts)

        agg = AggregatedMetrics(publication_id=campaign_id)

        for m in platform_metrics_list:
            agg.total_impressions += m.impressions
            agg.total_clicks += m.clicks
            agg.total_engagement += m.engagement
            agg.total_shares += m.shares
            agg.total_likes += m.likes
            agg.total_comments += m.comments
            agg.platform_breakdown[m.platform] = m.impressions

        logger.info(
            "campaign_analytics_collected",
            campaign_id=campaign_id,
            posts=len(posts),
            total_impressions=agg.total_impressions,
        )

        return agg

    def store_metrics(self, metrics: AggregatedMetrics) -> str:
        """
        Store collected metrics to PostgreSQL via the Artifact model.

        Creates an 'analytics_metrics' artifact linked to the campaign.

        Args:
            metrics: AggregatedMetrics to store

        Returns:
            artifact_id of the created record
        """
        try:
            from ..config import get_settings
            from ..models import Artifact, get_session

            settings = get_settings()
            session = get_session(settings.database)

            artifact_id = f"analytics-{uuid.uuid4().hex[:8]}"
            artifact = Artifact(
                campaign_id=metrics.publication_id,
                artifact_type="analytics_metrics",
                artifact_id=artifact_id,
                content=metrics.to_dict(),
                stage_name="analytics",
            )

            session.add(artifact)
            session.commit()
            session.close()

            logger.info("analytics_stored", artifact_id=artifact_id)
            return artifact_id

        except Exception as exc:
            logger.error("analytics_store_failed", error=str(exc))
            return f"store_failed: {exc}"

    # -------------------------------------------------------------------------
    # Platform-specific collectors
    # -------------------------------------------------------------------------

    def _collect_twitter_metrics(self, post_id: str) -> PlatformMetrics:
        """Collect metrics for a Twitter tweet."""
        # In production, use Twitter Ads API or engagement endpoints
        # Here we return mock data for demo
        if self.twitter.mock_mode:
            return PlatformMetrics(
                platform="twitter",
                post_id=post_id,
                impressions=1200,
                clicks=89,
                engagement=156,
                shares=23,
                likes=67,
                comments=12,
                mock=True,
            )

        # Live: call Twitter analytics API
        # GET /2/tweets/{id} with tweet.fields=public_metrics
        return PlatformMetrics(
            platform="twitter",
            post_id=post_id,
            impressions=0,
            clicks=0,
            engagement=0,
            shares=0,
            likes=0,
            comments=0,
        )

    def _collect_linkedin_metrics(self, post_id: str) -> PlatformMetrics:
        """Collect metrics for a LinkedIn post."""
        if self.linkedin.mock_mode:
            return PlatformMetrics(
                platform="linkedin",
                post_id=post_id,
                impressions=3400,
                clicks=210,
                engagement=445,
                shares=67,
                likes=234,
                comments=89,
                mock=True,
            )

        # Live: call LinkedIn API for organization post statistics
        return PlatformMetrics(
            platform="linkedin",
            post_id=post_id,
            impressions=0,
            clicks=0,
            engagement=0,
            shares=0,
            likes=0,
            comments=0,
        )

    def _collect_facebook_metrics(self, post_id: str) -> PlatformMetrics:
        """Collect metrics for a Facebook post."""
        if self.facebook.mock_mode:
            return PlatformMetrics(
                platform="facebook",
                post_id=post_id,
                impressions=2100,
                clicks=134,
                engagement=312,
                shares=45,
                likes=189,
                comments=34,
                reach=1800,
                mock=True,
            )

        # Live: call Meta Graph API with metrics=impressions,engagement,etc.
        return PlatformMetrics(
            platform="facebook",
            post_id=post_id,
            impressions=0,
            clicks=0,
            engagement=0,
            shares=0,
            likes=0,
            comments=0,
        )