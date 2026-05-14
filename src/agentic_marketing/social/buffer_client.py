"""Buffer API v1 client with mock mode."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ScheduledPostResult:
    """Result from a scheduled Buffer post creation."""
    buffer_post_id: str
    post_url: str
    scheduled_at: str
    profile_id: str
    mock: bool = False


@dataclass
class QueuedPost:
    """A post currently in the Buffer queue."""
    id: str
    text: str
    scheduled_at: str | None
    profile_id: str
    status: str  # "pending", "sent", "draft"


class BufferClient:
    """
    Buffer API v1 client for cross-platform scheduling.

    Falls back to mock mode when BUFFER_ACCESS_TOKEN is not set.

    Buffer API v1 docs: https://buffer.com/developers/api

    Environment:
        BUFFER_ACCESS_TOKEN  — OAuth 2.0 access token
        BUFFER_CLIENT_ID     — Application client ID
        BUFFER_CLIENT_SECRET — Application client secret
    """

    BASE_URL = "https://api.bufferapp.com/1"

    def __init__(self) -> None:
        self.access_token = os.environ.get("BUFFER_ACCESS_TOKEN", "")
        self.client_id = os.environ.get("BUFFER_CLIENT_ID", "")
        self.client_secret = os.environ.get("BUFFER_CLIENT_SECRET", "")
        self.mock_mode = not bool(self.access_token)

        if self.mock_mode:
            logger.warning("buffer_client_mock_mode", reason="ACCESS_TOKEN not configured")
        else:
            logger.info("buffer_client_initialized")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_scheduled_post(
        self,
        profile_id: str,
        text: str,
        media: dict[str, Any] | None = None,
        scheduled_at: str | None = None,
        now: bool = False,
    ) -> ScheduledPostResult:
        """
        Create a scheduled post via Buffer.

        Args:
            profile_id: Buffer profile ID for the channel
            text: Post text content
            media: Optional media dict {'link': str} or {'image': str, 'thumbnail': str}
            scheduled_at: ISO 8601 datetime to publish (None = add to queue now)
            now: If True, post immediately (overrides scheduled_at)

        Returns:
            ScheduledPostResult with buffer_post_id, post_url, scheduled_at
        """
        if self.mock_mode:
            return self._mock_scheduled_post(profile_id, text, media, scheduled_at, now)

        return self._create_scheduled_post_live(profile_id, text, media, scheduled_at, now)

    def get_queued_posts(self, profile_id: str) -> list[QueuedPost]:
        """
        Get pending posts in a profile's queue.

        Args:
            profile_id: Buffer profile ID

        Returns:
            List of QueuedPost objects
        """
        if self.mock_mode:
            return self._mock_queued_posts(profile_id)

        return self._get_queued_posts_live(profile_id)

    def get_profiles(self) -> list[dict[str, Any]]:
        """
        Fetch all Buffer profiles (social accounts).

        Returns:
            List of profile objects with id, service, username, etc.
        """
        if self.mock_mode:
            return self._mock_profiles()

        return self._get_profiles_live()

    # -------------------------------------------------------------------------
    # Live implementations
    # -------------------------------------------------------------------------

    def _create_scheduled_post_live(
        self,
        profile_id: str,
        text: str,
        media: dict[str, Any] | None,
        scheduled_at: str | None,
        now: bool,
    ) -> ScheduledPostResult:
        """Create a scheduled post via Buffer API v1."""
        import requests

        url = f"{self.BASE_URL}/updates/create.json"
        payload: dict[str, Any] = {
            "access_token": self.access_token,
            "profile_id": profile_id,
            "text": text,
            "now": "true" if now else "false",
        }

        if scheduled_at and not now:
            # Buffer accepts "at" as UTC timestamp
            payload["scheduled_at"] = scheduled_at

        if media:
            if "link" in media:
                payload["media[link]"] = media["link"]
            if "image" in media:
                payload["media[photo]"] = media["image"]

        for attempt in range(3):
            resp = requests.post(url, data=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 15
                logger.warning("buffer_rate_limit", retry_after=wait)
                time.sleep(wait)
                continue
            if resp.status_code == 401:
                raise RuntimeError("Buffer access token invalid or expired")

            resp.raise_for_status()
            data = resp.json()
            updates = data.get("updates", [])
            post_id = updates[0]["id"] if updates else f"buf-{uuid.uuid4().hex[:12]}"
            return ScheduledPostResult(
                buffer_post_id=post_id,
                post_url=f"https://buffer.com/queue/profile/{profile_id}",
                scheduled_at=scheduled_at or "now",
                profile_id=profile_id,
            )

        raise RuntimeError("Buffer API rate limit exhausted after retries")

    def _get_queued_posts_live(self, profile_id: str) -> list[QueuedPost]:
        """Fetch queued posts from Buffer API v1."""
        import requests

        url = f"{self.BASE_URL}/updates/sent.json"
        params = {
            "access_token": self.access_token,
            "profile_id": profile_id,
            "count": 10,
        }

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        return [
            QueuedPost(
                id=upd["id"],
                text=upd.get("text", ""),
                scheduled_at=upd.get("scheduled_at"),
                profile_id=profile_id,
                status=upd.get("status", "pending"),
            )
            for upd in data.get("updates", [])
        ]

    def _get_profiles_live(self) -> list[dict[str, Any]]:
        """Fetch all Buffer profiles."""
        import requests

        url = f"{self.BASE_URL}/profiles.json"
        params = {"access_token": self.access_token}

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------------------------------------------------
    # Mock implementations
    # -------------------------------------------------------------------------

    @staticmethod
    def _mock_scheduled_post(
        profile_id: str,
        text: str,
        media: dict[str, Any] | None,
        scheduled_at: str | None,
        now: bool,
    ) -> ScheduledPostResult:
        """Generate fake scheduled post result for demo mode."""
        post_id = f"buf-{uuid.uuid4().hex[:12]}"
        logger.info(
            "mock_buffer_scheduled_post",
            post_id=post_id,
            profile_id=profile_id,
            content=text[:60],
            scheduled_at=scheduled_at or "now",
            now=now,
        )
        return ScheduledPostResult(
            buffer_post_id=post_id,
            post_url=f"https://buffer.com/queue/profile/{profile_id}",
            scheduled_at=scheduled_at or "2026-05-14T12:00:00Z",
            profile_id=profile_id,
            mock=True,
        )

    @staticmethod
    def _mock_queued_posts(profile_id: str) -> list[QueuedPost]:
        """Return fake queued posts for demo mode."""
        return [
            QueuedPost(
                id=f"buf-queued-{i}",
                text=f"Demo queued post {i} for profile {profile_id}",
                scheduled_at="2026-05-14T14:00:00Z",
                profile_id=profile_id,
                status="pending",
            )
            for i in range(3)
        ]

    @staticmethod
    def _mock_profiles() -> list[dict[str, Any]]:
        """Return fake Buffer profiles for demo mode."""
        return [
            {
                "id": "prof-twitter-001",
                "service": "twitter",
                "username": "democampaign",
                "avatar": "https://buffer.com/avatar/twitter.png",
            },
            {
                "id": "prof-linkedin-001",
                "service": "linkedin",
                "username": "Demo Company",
                "avatar": "https://buffer.com/avatar/linkedin.png",
            },
            {
                "id": "prof-facebook-001",
                "service": "facebook",
                "username": "Demo Campaign",
                "avatar": "https://buffer.com/avatar/facebook.png",
            },
        ]