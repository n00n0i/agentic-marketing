"""LinkedIn API v2 client with OAuth 2.0 and mock mode."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class LinkedInPostResult:
    """Result from a LinkedIn post creation."""
    post_urn: str
    post_url: str
    created_at: str
    mock: bool = False


@dataclass
class LinkedInArticleResult:
    """Result from a LinkedIn article creation."""
    article_urn: str
    article_url: str
    created_at: str
    mock: bool = False


class LinkedInClient:
    """
    LinkedIn API v2 client using OAuth 2.0 bearer token.

    Falls back to mock mode when LINKEDIN_ACCESS_TOKEN is not set.

    Environment:
        LINKEDIN_ACCESS_TOKEN  — OAuth 2.0 access token (required for live mode)
        LINKEDIN_CLIENT_ID     — Application client ID
        LINKEDIN_CLIENT_SECRET — Application client secret
        LINKEDIN_COMPANY_ID    — Default company URN for page posts
    """

    BASE_URL = "https://api.linkedin.com/rest"
    VERSION = "202304"

    def __init__(self) -> None:
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN", "")
        self.client_id = os.environ.get("LINKEDIN_CLIENT_ID", "")
        self.client_secret = os.environ.get("LINKEDIN_CLIENT_SECRET", "")
        self.company_id = os.environ.get("LINKEDIN_COMPANY_ID", "")
        self.mock_mode = not bool(self.access_token)

        if self.mock_mode:
            logger.warning("linkedin_client_mock_mode", reason="ACCESS_TOKEN not configured")
        else:
            logger.info("linkedin_client_initialized", company_id=self.company_id or "none")

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_post(self, content: str, media_urls: list[str] | None = None) -> LinkedInPostResult:
        """
        Create a LinkedIn text post or post with images.

        Args:
            content: Post body text
            media_urls: Optional list of image URLs to attach

        Returns:
            LinkedInPostResult with post_urn, post_url, created_at
        """
        if self.mock_mode:
            return self._mock_post(content, media_urls)

        return self._create_post_live(content, media_urls)

    def create_article(
        self,
        title: str,
        content: str,
        media: dict[str, str] | None = None,
    ) -> LinkedInArticleResult:
        """
        Publish a LinkedIn long-form article.

        Args:
            title: Article title
            content: Article body (HTML allowed)
            media: Optional hero image {'url': str, 'alt': str}

        Returns:
            LinkedInArticleResult with article_urn, article_url, created_at
        """
        if self.mock_mode:
            return self._mock_article(title, content, media)

        return self._create_article_live(title, content, media)

    def get_profile(self, urn: str | None = None) -> dict[str, Any]:
        """
        Fetch a LinkedIn member or organization profile.

        Args:
            urn: Person or organization URN (defaults to authenticated user)

        Returns:
            Profile data dict
        """
        if self.mock_mode:
            return self._mock_profile(urn)

        return self._get_profile_live(urn)

    def create_company_post(self, company_urn: str, content: str, media_urls: list[str] | None = None) -> LinkedInPostResult:
        """
        Post to a company page.

        Args:
            company_urn: Organization URN (urn:li:organization:{id})
            content: Post body
            media_urls: Optional image URLs

        Returns:
            LinkedInPostResult
        """
        if self.mock_mode:
            return self._mock_post(content, media_urls, f"company:{company_urn}")

        return self._create_company_post_live(company_urn, content, media_urls)

    # -------------------------------------------------------------------------
    # Live implementations
    # -------------------------------------------------------------------------

    def _create_post_live(self, content: str, media_urls: list[str] | None = None) -> LinkedInPostResult:
        """Create a post via LinkedIn API v2."""
        import requests

        url = f"{self.BASE_URL}/posts"
        headers = self._auth_headers()
        author = self.company_id or "me"

        payload: dict[str, Any] = {
            "author": author,
            "commentary": content,
            "visibility": "PUBLIC",
        }

        if media_urls:
            payload["media"] = [{"status": "READY", "originalUrl": u} for u in media_urls]

        for attempt in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 30
                logger.warning("linkedin_rate_limit", retry_after=wait)
                time.sleep(wait)
                continue
            if resp.status_code == 401:
                raise RuntimeError("LinkedIn OAuth token expired or invalid")

            resp.raise_for_status()
            data = resp.json()
            post_urn = data.get("id", f"urn:li:post:{uuid.uuid4().hex[:12]}")
            return LinkedInPostResult(
                post_urn=post_urn,
                post_url=f"https://www.linkedin.com/feed/update/{post_urn}",
                created_at=data.get("createdAt", "2026-05-14T12:00:00Z"),
            )

        raise RuntimeError("LinkedIn API rate limit exhausted after retries")

    def _create_company_post_live(self, company_urn: str, content: str, media_urls: list[str] | None) -> LinkedInPostResult:
        """Post to a company page."""
        import requests

        url = f"{self.BASE_URL}/posts"
        headers = self._auth_headers()

        payload: dict[str, Any] = {
            "author": company_urn,
            "commentary": content,
            "visibility": "PUBLIC",
        }

        if media_urls:
            payload["media"] = [{"status": "READY", "originalUrl": u} for u in media_urls]

        for attempt in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 30
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            post_urn = data.get("id", f"urn:li:post:{uuid.uuid4().hex[:12]}")
            return LinkedInPostResult(
                post_urn=post_urn,
                post_url=f"https://www.linkedin.com/feed/update/{post_urn}",
                created_at=data.get("createdAt", "2026-05-14T12:00:00Z"),
            )

        raise RuntimeError("LinkedIn API rate limit exhausted after retries")

    def _create_article_live(self, title: str, content: str, media: dict[str, str] | None = None) -> LinkedInArticleResult:
        """Publish a long-form article."""
        import requests

        url = f"{self.BASE_URL}/articles"
        headers = self._auth_headers()

        payload: dict[str, Any] = {
            "author": self.company_id or "me",
            "title": title,
            "body": content,
            "visibility": "PUBLIC",
        }

        if media:
            payload["media"] = [media]

        for attempt in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 30
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            article_urn = data.get("id", f"urn:li:article:{uuid.uuid4().hex[:12]}")
            return LinkedInArticleResult(
                article_urn=article_urn,
                article_url=f"https://www.linkedin.com/pulse/{article_urn}",
                created_at=data.get("createdAt", "2026-05-14T12:00:00Z"),
            )

        raise RuntimeError("LinkedIn API rate limit exhausted after retries")

    def _get_profile_live(self, urn: str | None = None) -> dict[str, Any]:
        """Fetch a profile."""
        import requests

        target = urn or "me"
        url = f"{self.BASE_URL}/profiles/{target}"
        headers = self._auth_headers()
        params = {"projection": "(id,firstName,lastName,headline,publicProfileUrl)"}

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # -------------------------------------------------------------------------
    # Mock implementations
    # -------------------------------------------------------------------------

    @staticmethod
    def _mock_post(content: str, media_urls: list[str] | None = None, author: str = "me") -> LinkedInPostResult:
        """Generate fake post result for demo mode."""
        post_id = uuid.uuid4().hex[:12]
        logger.info("mock_linkedin_post", post_id=post_id, content=content[:60], media=bool(media_urls))
        return LinkedInPostResult(
            post_urn=f"urn:li:post:{post_id}",
            post_url=f"https://www.linkedin.com/feed/update/urn:li:post:{post_id}",
            created_at="2026-05-14T12:00:00Z",
            mock=True,
        )

    @staticmethod
    def _mock_article(title: str, content: str, media: dict[str, str] | None = None) -> LinkedInArticleResult:
        """Generate fake article result for demo mode."""
        article_id = uuid.uuid4().hex[:12]
        logger.info("mock_linkedin_article", article_id=article_id, title=title[:60])
        return LinkedInArticleResult(
            article_urn=f"urn:li:article:{article_id}",
            article_url=f"https://www.linkedin.com/pulse/{article_id}",
            created_at="2026-05-14T12:00:00Z",
            mock=True,
        )

    @staticmethod
    def _mock_profile(urn: str | None = None) -> dict[str, Any]:
        """Return fake profile for demo mode."""
        return {
            "id": "mock-profile-001",
            "firstName": {"localized": {"en_US": "Demo"}},
            "lastName": {"localized": {"en_US": "User"}},
            "headline": "Demo LinkedIn Profile",
            "publicProfileUrl": "https://www.linkedin.com/in/demo-user",
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        """Build authorization headers."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "LinkedIn-Version": self.VERSION,
            "Content-Type": "application/json",
        }