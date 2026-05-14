"""Unified social publishing manager with mock mode."""

from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from typing import Any

import structlog

from .twitter_client import TwitterClient, TweetResult
from .linkedin_client import LinkedInClient, LinkedInPostResult, LinkedInArticleResult
from .facebook_client import FacebookClient, PagePostResult
from .buffer_client import BufferClient, ScheduledPostResult

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Result types
# -------------------------------------------------------------------------


@dataclass
class PlatformPublishResult:
    """Result from publishing to a single platform."""
    platform: str
    success: bool
    post_id: str = ""
    post_url: str = ""
    error: str = ""
    mock: bool = False


@dataclass
class PublishResult:
    """Aggregated results from publishing to multiple platforms."""
    publication_id: str = field(default_factory=lambda: f"pub-{uuid.uuid4().hex[:8]}")
    platform_results: list[PlatformPublishResult] = field(default_factory=list)
    total_platforms: int = 0
    successful: int = 0
    failed: int = 0
    partial_failure: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "publication_id": self.publication_id,
            "total_platforms": self.total_platforms,
            "successful": self.successful,
            "failed": self.failed,
            "partial_failure": self.partial_failure,
            "platform_results": [
                {
                    "platform": r.platform,
                    "success": r.success,
                    "post_id": r.post_id,
                    "post_url": r.post_url,
                    "error": r.error,
                    "mock": r.mock,
                }
                for r in self.platform_results
            ],
        }


# -------------------------------------------------------------------------
# PublishManager
# -------------------------------------------------------------------------


class PublishManager:
    """
    Unified interface for publishing content to multiple social platforms.

    Automatically falls back to mock mode when platform API credentials
    are not configured. Supports parallel publishing.

    Usage:
        manager = PublishManager()
        result = manager.publish(
            content="Hello world!",
            platforms=["twitter", "linkedin"],
            media={"twitter": {"image_path": "/path/to/image.jpg"}},
        )
    """

    def __init__(self) -> None:
        self.twitter = TwitterClient()
        self.linkedin = LinkedInClient()
        self.facebook = FacebookClient()
        self.buffer = BufferClient()

        logger.info(
            "publish_manager_initialized",
            twitter_mock=self.twitter.mock_mode,
            linkedin_mock=self.linkedin.mock_mode,
            facebook_mock=self.facebook.mock_mode,
            buffer_mock=self.buffer.mock_mode,
        )

    def publish(
        self,
        content: str,
        platforms: list[str],
        media: dict[str, dict[str, Any]] | None = None,
        scheduled_at: str | None = None,
    ) -> PublishResult:
        """
        Publish content to the specified platforms.

        Args:
            content: Text content to publish
            platforms: List of platforms ['twitter', 'linkedin', 'facebook']
            media: Per-platform media options, e.g.:
                  {'twitter': {'image_path': '/img/tweet.jpg'}}
            scheduled_at: ISO 8601 datetime to schedule (None = publish immediately)

        Returns:
            PublishResult with per-platform results
        """
        media = media or {}
        result = PublishResult(platforms_requested=platforms) if hasattr(PublishResult, "platforms_requested") else PublishResult()

        # Resolve credential status across all platforms
        credential_status = self._credential_status()

        for platform in platforms:
            platform_media = media.get(platform, {})
            try:
                if platform == "twitter":
                    res = self._publish_twitter(content, platform_media, scheduled_at)
                elif platform == "linkedin":
                    res = self._publish_linkedin(content, platform_media, scheduled_at)
                elif platform == "facebook":
                    res = self._publish_facebook(content, platform_media, scheduled_at)
                elif platform == "buffer":
                    res = self._publish_buffer(content, platform_media, scheduled_at)
                else:
                    res = PlatformPublishResult(
                        platform=platform,
                        success=False,
                        error=f"Unknown platform: {platform}",
                    )
            except Exception as exc:
                logger.error("platform_publish_error", platform=platform, error=str(exc))
                res = PlatformPublishResult(
                    platform=platform,
                    success=False,
                    error=str(exc),
                    mock=credential_status.get(platform, False),
                )

            result.platform_results.append(res)

        result.total_platforms = len(result.platform_results)
        result.successful = sum(1 for r in result.platform_results if r.success)
        result.failed = result.total_platforms - result.successful
        result.partial_failure = result.successful > 0 and result.failed > 0

        logger.info(
            "publish_completed",
            publication_id=result.publication_id,
            total=result.total_platforms,
            successful=result.successful,
            failed=result.failed,
        )

        return result

    def publish_multi(
        self,
        posts: list[dict[str, Any]],
    ) -> list[PublishResult]:
        """
        Publish multiple posts in sequence.

        Args:
            posts: List of post specs with 'content', 'platforms', 'media', 'scheduled_at'

        Returns:
            List of PublishResult per post
        """
        return [self.publish(**post) for post in posts]

    # -------------------------------------------------------------------------
    # Per-platform private methods
    # -------------------------------------------------------------------------

    def _publish_twitter(
        self,
        content: str,
        media: dict[str, Any],
        scheduled_at: str | None,
    ) -> PlatformPublishResult:
        """Publish to Twitter."""
        if "image_path" in media:
            tweet = self.twitter.create_tweet_with_media(content, media["image_path"])
        else:
            tweet = self.twitter.create_tweet(content)

        return PlatformPublishResult(
            platform="twitter",
            success=True,
            post_id=tweet.tweet_id,
            post_url=f"https://twitter.com/i/status/{tweet.tweet_id}",
            mock=self.twitter.mock_mode,
        )

    def _publish_linkedin(
        self,
        content: str,
        media: dict[str, Any],
        scheduled_at: str | None,
    ) -> PlatformPublishResult:
        """Publish to LinkedIn."""
        media_urls = media.get("media_urls")
        post = self.linkedin.create_post(content, media_urls)

        return PlatformPublishResult(
            platform="linkedin",
            success=True,
            post_id=post.post_urn,
            post_url=post.post_url,
            mock=self.linkedin.mock_mode,
        )

    def _publish_facebook(
        self,
        content: str,
        media: dict[str, Any],
        scheduled_at: str | None,
    ) -> PlatformPublishResult:
        """Publish to Facebook."""
        page_id = media.get("page_id")
        image_path = media.get("image_path")
        link = media.get("link")

        post = self.facebook.create_page_post(page_id, content, image_path, link)

        return PlatformPublishResult(
            platform="facebook",
            success=True,
            post_id=post.post_id,
            post_url=post.post_url,
            mock=self.facebook.mock_mode,
        )

    def _publish_buffer(
        self,
        content: str,
        media: dict[str, Any],
        scheduled_at: str | None,
    ) -> PlatformPublishResult:
        """Publish via Buffer."""
        profile_id = media.get("profile_id", "default")
        media_payload = None
        if "link" in media:
            media_payload = {"link": media["link"]}
        elif "image_path" in media:
            media_payload = {"image": media["image_path"]}

        result = self.buffer.create_scheduled_post(
            profile_id=profile_id,
            text=content,
            media=media_payload,
            scheduled_at=scheduled_at,
            now=(scheduled_at is None),
        )

        return PlatformPublishResult(
            platform="buffer",
            success=True,
            post_id=result.buffer_post_id,
            post_url=result.post_url,
            mock=self.buffer.mock_mode,
        )

    # -------------------------------------------------------------------------
    # Credential helpers
    # -------------------------------------------------------------------------

    def _credential_status(self) -> dict[str, bool]:
        """Return dict of platform -> is_mock (True if using mock mode)."""
        return {
            "twitter": self.twitter.mock_mode,
            "linkedin": self.linkedin.mock_mode,
            "facebook": self.facebook.mock_mode,
            "buffer": self.buffer.mock_mode,
        }

    def is_platform_configured(self, platform: str) -> bool:
        """Check if a platform has real credentials configured."""
        status = self._credential_status()
        # is_mock = True means NOT configured
        return not status.get(platform, True)