"""Twitter API v2 client with OAuth 2.0 and mock mode."""

from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class TweetResult:
    """Result from a tweet creation."""
    tweet_id: str
    text: str
    created_at: str
    mock: bool = False


class TwitterClient:
    """
    Twitter API v2 client.

    Uses OAuth 2.0 with user context. Falls back to mock mode when
    TWITTER_API_KEY / TWITTER_API_SECRET are not set.

    Environment:
        TWITTER_API_KEY       — OAuth client ID
        TWITTER_API_SECRET    — OAuth client secret
        TWITTER_BEARER_TOKEN  — App-only bearer token (optional)
        TWITTER_ACCESS_TOKEN  — User access token (optional, for user-context calls)
    """

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self) -> None:
        self.api_key = os.environ.get("TWITTER_API_KEY", "")
        self.api_secret = os.environ.get("TWITTER_API_SECRET", "")
        self.bearer_token = os.environ.get("TWITTER_BEARER_TOKEN", "")
        self.access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "")
        self.mock_mode = not (self.api_key and self.api_secret)

        if self.mock_mode:
            logger.warning("twitter_client_mock_mode", reason="API credentials not configured")
        else:
            logger.info("twitter_client_initialized", bearer=bool(self.bearer_token), user_context=bool(self.access_token))

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def create_tweet(self, text: str) -> TweetResult:
        """
        Post a text-only tweet.

        Args:
            text: Tweet content (max 280 characters)

        Returns:
            TweetResult with tweet_id, text, created_at
        """
        if self.mock_mode:
            return self._mock_tweet(text)

        return self._create_tweet_live(text)

    def create_tweet_with_media(self, text: str, image_path: str) -> TweetResult:
        """
        Post a tweet with an attached image.

        Args:
            text: Tweet content
            image_path: Path to local image file

        Returns:
            TweetResult with tweet_id, text, created_at
        """
        if self.mock_mode:
            logger.info("mock_tweet_with_media", image_path=image_path)
            return self._mock_tweet(text, has_media=True)

        return self._create_tweet_with_media_live(text, image_path)

    def get_user_tweets(self, username: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch recent tweets from a user timeline.

        Args:
            username: Twitter handle (without @)
            limit: Max number of tweets to return

        Returns:
            List of tweet objects
        """
        if self.mock_mode:
            return self._mock_user_tweets(username, limit)

        return self._get_user_tweets_live(username, limit)

    def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet by ID.

        Returns:
            True if deleted successfully
        """
        if self.mock_mode:
            logger.info("mock_delete_tweet", tweet_id=tweet_id)
            return True

        return self._delete_tweet_live(tweet_id)

    # -------------------------------------------------------------------------
    # Live implementations (real API)
    # -------------------------------------------------------------------------

    def _create_tweet_live(self, text: str) -> TweetResult:
        """Post tweet via Twitter API v2."""
        import requests

        if len(text) > 280:
            raise ValueError("Tweet exceeds 280 character limit")

        url = f"{self.BASE_URL}/tweets"
        headers = self._auth_headers()
        payload = {"text": text}

        for attempt in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 15
                logger.warning("twitter_rate_limit", retry_after=wait)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return TweetResult(
                tweet_id=data["data"]["id"],
                text=text,
                created_at=data["data"]["created_at"],
            )

        raise RuntimeError("Twitter API rate limit exhausted after retries")

    def _create_tweet_with_media_live(self, text: str, image_path: str) -> TweetResult:
        """Post tweet with image using Twitter API v2 media upload."""
        import requests
        from pathlib import Path

        if len(text) > 280:
            raise ValueError("Tweet exceeds 280 character limit")

        # Step 1: Upload media
        media_path = Path(image_path)
        if not media_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        media_url = f"{self.BASE_URL}/media/upload"
        headers = {**self._auth_headers(), "Content-Type": "multipart/form-data"}
        with media_path.open("rb") as f:
            files = {"file": (media_path.name, f, "image/jpeg")}
            media_resp = requests.post(media_url, headers=headers, files=files, timeout=60)

        if media_resp.status_code == 429:
            time.sleep(15)
            media_resp = requests.post(media_url, headers=headers, files=files, timeout=60)

        media_resp.raise_for_status()
        media_id = media_resp.json()["media_id_string"]

        # Step 2: Post tweet with media
        url = f"{self.BASE_URL}/tweets"
        payload = {"text": text, "media": {"media_ids": [media_id]}}

        for attempt in range(3):
            resp = requests.post(url, headers=self._auth_headers(), json=payload, timeout=30)
            if resp.status_code == 429:
                wait = 2 ** attempt * 15
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            return TweetResult(
                tweet_id=data["data"]["id"],
                text=text,
                created_at=data["data"]["created_at"],
            )

        raise RuntimeError("Twitter API rate limit exhausted after retries")

    def _get_user_tweets_live(self, username: str, limit: int) -> list[dict[str, Any]]:
        """Fetch user timeline via Twitter API v2."""
        import requests

        headers = self._auth_headers()
        params = {"max_results": min(limit, 10), "tweet.fields": "created_at,public_metrics"}

        url = f"{self.BASE_URL}/users/by/username/{username}/tweets"
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()

        return resp.json().get("data", [])

    def _delete_tweet_live(self, tweet_id: str) -> bool:
        """Delete a tweet."""
        import requests

        url = f"{self.BASE_URL}/tweets/{tweet_id}"
        resp = requests.delete(url, headers=self._auth_headers(), timeout=30)

        if resp.status_code == 429:
            time.sleep(15)
            resp = requests.delete(url, headers=self._auth_headers(), timeout=30)

        return resp.status_code in (200, 204)

    # -------------------------------------------------------------------------
    # Mock implementations
    # -------------------------------------------------------------------------

    @staticmethod
    def _mock_tweet(text: str, has_media: bool = False) -> TweetResult:
        """Generate a fake tweet result for demo mode."""
        tweet_id = f"mock-{uuid.uuid4().hex[:12]}"
        logger.info("mock_tweet_created", tweet_id=tweet_id, text=text[:60], has_media=has_media)
        return TweetResult(
            tweet_id=tweet_id,
            text=text,
            created_at="2026-05-14T12:00:00Z",
            mock=True,
        )

    @staticmethod
    def _mock_user_tweets(username: str, limit: int) -> list[dict[str, Any]]:
        """Return fake tweets for demo mode."""
        return [
            {
                "id": f"mock-{uuid.uuid4().hex[:8]}",
                "text": f"This is a sample tweet from @{username} for demo purposes.",
                "created_at": "2026-05-14T10:00:00Z",
                "public_metrics": {"retweet_count": 0, "like_count": 0, "reply_count": 0},
            }
            for _ in range(min(limit, 5))
        ]

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        """Build authorization headers."""
        if self.access_token:
            return {"Authorization": f"Bearer {self.access_token}"}
        if self.bearer_token:
            return {"Authorization": f"Bearer {self.bearer_token}"}
        raise RuntimeError("No Twitter auth credentials configured")