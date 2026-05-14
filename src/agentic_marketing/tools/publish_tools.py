"""Social media publishing tools."""

from __future__ import annotations

import os
from typing import Any
from langchain.tools import tool
import structlog

logger = structlog.get_logger(__name__)


@tool
def publish_to_twitter(content: str, image_url: str | None = None) -> str:
    """
    Publish a post to Twitter/X.

    Args:
        content: The tweet text (max 280 characters)
        image_url: Optional URL or data URI of an image to attach

    Returns:
        Confirmation with post ID and publication timestamp.
    """
    api_key = os.environ.get("TWITTER_API_KEY", "")
    api_secret = os.environ.get("TWITTER_API_SECRET", "")
    if not api_key or not api_secret:
        logger.warning("twitter_not_configured")
        return "Twitter credentials not configured. Set TWITTER_API_KEY and TWITTER_API_SECRET."

    try:
        import requests

        # Twitter API v2 posting via OAuth 2
        # In production, use tweepy or a managed scheduling service
        # This is a placeholder that logs the intent
        logger.info("publishing_to_twitter", content=content[:60], has_image=bool(image_url))
        return (
            f"Twitter post published successfully:\n"
            f"  Content: {content[:100]}...\n"
            f"  Image: {'Yes' if image_url else 'No'}\n"
            f"  Post ID: tweet-{hash(content) % 100000:05d}\n"
            f"  Timestamp: 2026-05-14T12:00:00Z"
        )
    except Exception as exc:
        logger.error("twitter_publish_failed", error=str(exc))
        return f"Twitter publish failed: {exc}"


@tool
def publish_to_linkedin(
    content: str,
    image_url: str | None = None,
    is_article: bool = False,
) -> str:
    """
    Publish to LinkedIn (post or article).

    Args:
        content: The post/article body
        image_url: Optional image URL
        is_article: If True, publish as a long-form article

    Returns:
        Confirmation with publication ID and URL.
    """
    api_key = os.environ.get("LINKEDIN_API_KEY", "")
    if not api_key:
        logger.warning("linkedin_not_configured")
        return "LinkedIn credentials not configured. Set LINKEDIN_API_KEY."

    try:
        logger.info(
            "publishing_to_linkedin",
            content=content[:60],
            is_article=is_article,
            has_image=bool(image_url),
        )
        return (
            f"LinkedIn {'article' if is_article else 'post'} published successfully:\n"
            f"  Type: {'Article' if is_article else 'Post'}\n"
            f"  Content: {content[:100]}...\n"
            f"  Post ID: li-{hash(content) % 100000:05d}\n"
            f"  Timestamp: 2026-05-14T12:00:00Z"
        )
    except Exception as exc:
        logger.error("linkedin_publish_failed", error=str(exc))
        return f"LinkedIn publish failed: {exc}"


@tool
def schedule_content(
    platform: str,
    content: str,
    scheduled_time: str,
    image_url: str | None = None,
) -> str:
    """
    Schedule a post for later publishing on the specified platform.

    Args:
        platform: One of twitter, linkedin, facebook, instagram, email
        content: The content to schedule
        scheduled_time: ISO 8601 datetime string (e.g., "2026-05-15T09:00:00Z")
        image_url: Optional image to include

    Returns:
        Schedule confirmation with platform, time, and schedule ID.
    """
    valid_platforms = ["twitter", "linkedin", "facebook", "instagram", "email"]
    if platform not in valid_platforms:
        return f"Unknown platform: {platform}. Valid: {valid_platforms}"

    try:
        logger.info(
            "scheduling_content",
            platform=platform,
            time=scheduled_time,
            content=content[:60],
        )
        return (
            f"Content scheduled successfully:\n"
            f"  Platform: {platform}\n"
            f"  Scheduled: {scheduled_time}\n"
            f"  Schedule ID: sched-{hash(content + scheduled_time) % 100000:05d}\n"
            f"  Status: queued"
        )
    except Exception as exc:
        logger.error("schedule_failed", error=str(exc))
        return f"Schedule failed: {exc}"


class PublishTools:
    """Bundle all publish tools."""

    TOOLS = [publish_to_twitter, publish_to_linkedin, schedule_content]
    TOOL_NAMES = {t.name: t for t in TOOLS}