"""Meta Graph API client for Facebook Pages with mock mode."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class PagePostResult:
    """Result from a Facebook page post creation."""
    post_id: str
    post_url: str
    created_at: str
    mock: bool = False


class FacebookClient:
    """
    Meta Graph API client for Facebook Page management.

    Falls back to mock mode when FACEBOOK_ACCESS_TOKEN is not set.

    Environment:
        FACEBOOK_ACCESS_TOKEN  — Page access token from Meta developer portal
        FACEBOOK_PAGE_ID       — Target Facebook page ID
    """

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self) -> None:
        self.access_token = os.environ.get("FACEBOOK_ACCESS_TOKEN", "")
        self.page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
        self.mock_mode = not bool(self.access_token)

        if self.mock_mode:
            logger.warning("facebook_client_mock_mode", reason="ACCESS_TOKEN not configured")
        else:
            logger.info("facebook_client_initialized", page_id=self.page_id or "none")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_page_post(
        self,
        page_id: str | None,
        message: str,
        image_path: str | None = None,
        link: str | None = None,
    ) -> PagePostResult:
        """
        Create a post on a Facebook page.

        Args:
            page_id: Target page ID (defaults to FACEBOOK_PAGE_ID env var)
            message: Post body text
            image_path: Optional path to image to upload
            link: Optional link to attach

        Returns:
            PagePostResult with post_id, post_url, created_at
        """
        pid = page_id or self.page_id
        if self.mock_mode:
            return self._mock_page_post(pid, message, bool(image_path), bool(link))

        return self._create_page_post_live(pid, message, image_path, link)

    def get_page_posts(self, page_id: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch recent posts from a Facebook page.

        Args:
            page_id: Target page ID (defaults to FACEBOOK_PAGE_ID)
            limit: Max number of posts to return

        Returns:
            List of post objects with id, message, created_time, full_picture, etc.
        """
        pid = page_id or self.page_id
        if self.mock_mode:
            return self._mock_page_posts(pid, limit)

        return self._get_page_posts_live(pid, limit)

    def delete_post(self, post_id: str) -> bool:
        """
        Delete a page post by ID.

        Returns:
            True if deleted successfully
        """
        if self.mock_mode:
            logger.info("mock_delete_facebook_post", post_id=post_id)
            return True

        return self._delete_post_live(post_id)

    # -------------------------------------------------------------------------
    # Live implementations
    # -------------------------------------------------------------------------

    def _create_page_post_live(
        self,
        page_id: str,
        message: str,
        image_path: str | None,
        link: str | None,
    ) -> PagePostResult:
        """Create a page post via Meta Graph API."""
        import requests

        url = f"{self.BASE_URL}/{page_id}/feed"
        payload: dict[str, Any] = {
            "message": message,
            "access_token": self.access_token,
        }

        if link:
            payload["link"] = link

        if image_path:
            # Upload photo first, then attach to post
            photo_url = f"{self.BASE_URL}/{page_id}/photos"
            with open(image_path, "rb") as f:
                files = {"source": ("image.jpg", f, "image/jpeg")}
                photo_data = {"access_token": self.access_token}
                photo_resp = requests.post(photo_url, data=photo_data, files=files, timeout=60)

            if photo_resp.status_code == 429:
                time.sleep(30)
                photo_resp = requests.post(photo_url, data=photo_data, files=files, timeout=60)

            photo_resp.raise_for_status()
            photo_id = photo_resp.json().get("id")
            if photo_id:
                payload["attached_media"] = [photo_id]

        for attempt in range(3):
            resp = requests.post(url, data=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 30
                logger.warning("facebook_rate_limit", retry_after=wait)
                time.sleep(wait)
                continue
            if resp.status_code == 190:
                raise RuntimeError("Facebook access token expired or revoked")

            resp.raise_for_status()
            data = resp.json()
            post_id = data.get("id", f"mock-{uuid.uuid4().hex[:12]}")
            return PagePostResult(
                post_id=post_id,
                post_url=f"https://www.facebook.com/{page_id}/posts/{post_id}",
                created_at=data.get("created_time", "2026-05-14T12:00:00Z"),
            )

        raise RuntimeError("Facebook API rate limit exhausted after retries")

    def _get_page_posts_live(self, page_id: str, limit: int) -> list[dict[str, Any]]:
        """Fetch page posts via Meta Graph API."""
        import requests

        url = f"{self.BASE_URL}/{page_id}/feed"
        params = {
            "fields": "id,message,created_time,full_picture,link,shares,likes.summary(true),comments.summary(true)",
            "limit": min(limit, 25),
            "access_token": self.access_token,
        }

        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        return data.get("data", [])

    def _delete_post_live(self, post_id: str) -> bool:
        """Delete a post."""
        import requests

        url = f"{self.BASE_URL}/{post_id}"
        params = {"access_token": self.access_token}

        resp = requests.delete(url, params=params, timeout=30)
        if resp.status_code == 429:
            time.sleep(30)
            resp = requests.delete(url, params=params, timeout=30)

        return resp.status_code in (200, 204)

    # -------------------------------------------------------------------------
    # Mock implementations
    # -------------------------------------------------------------------------

    @staticmethod
    def _mock_page_post(page_id: str, message: str, has_image: bool, has_link: bool) -> PagePostResult:
        """Generate fake page post result for demo mode."""
        post_id = f"mock-{uuid.uuid4().hex[:12]}"
        logger.info(
            "mock_facebook_page_post",
            post_id=post_id,
            page_id=page_id,
            content=message[:60],
            has_image=has_image,
            has_link=has_link,
        )
        return PagePostResult(
            post_id=post_id,
            post_url=f"https://www.facebook.com/{page_id or 'page'}/posts/{post_id}",
            created_at="2026-05-14T12:00:00Z",
            mock=True,
        )

    @staticmethod
    def _mock_page_posts(page_id: str, limit: int) -> list[dict[str, Any]]:
        """Return fake posts for demo mode."""
        return [
            {
                "id": f"mock-post-{i}",
                "message": f"Sample Facebook post {i} for demo purposes.",
                "created_time": "2026-05-14T10:00:00Z",
                "full_picture": None,
                "link": None,
                "likes": {"summary": [{"total_count": 0}]},
                "comments": {"summary": [{"total_count": 0}]},
            }
            for i in range(min(limit, 5))
        ]