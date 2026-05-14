"""Content moderation — profanity, brand safety, platform-specific rules."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# -------------------------------------------------------------------------
# Enums
# -------------------------------------------------------------------------


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# -------------------------------------------------------------------------
# Ban lists (simple in-memory — replace with external service in prod)
# -------------------------------------------------------------------------


# Profanity and offensive language
PROFANITY_WORDS = {
    # Basic placeholder list — replace with commercial service (e.g. WebPurify, AWS Rekognition)
    "fuck", "shit", "ass", "damn", "bitch", "bastard",
    "crap", "piss", "dick", "cock", "pussy", "CNM", "F-word",
}

# Competitive disparagement (brand safety)
COMPETITOR_DISPARAGEMENT = {
    # Phrases that directly disparage named competitors
    " competitor ", " competitor's", "rival ", " rivals ",
}

# Dangerous / harmful content
HARMFUL_CONTENT = {
    "how to hack", "how to crack", "how to doxx",
    "buy followers", "buy likes", "fake engagement",
    "spam ", "scam", "phishing", "pyramid scheme",
}

# Vague superlatives that violate advertising policies
VAGUE_SUPERLATIVES = {
    # Platform-advertising policy violations
    r"\bbest ever\b", r"\b#1\b", r"\bworld's best\b",
    r"\bproven\b", r"\bguaranteed\b", r"\b100%\b",
}

# Banned CTA patterns
BANNED_CTAS = {
    "click here", "click this", "act now", "buy now",
    "order now", "sign up free", "free sign up",
    "limited time offer", "only today",
}


# -------------------------------------------------------------------------
# Platform-specific rules
# -------------------------------------------------------------------------


PLATFORM_RULES: dict[str, dict[str, Any]] = {
    "twitter": {
        "max_length": 280,
        "disallowed_patterns": [
            r"@\w{15,}",  # @handle over 14 chars (old limit)
        ],
        "brand_safety": ["political", "religious", "financial_advice"],
    },
    "linkedin": {
        "max_length": 3000,
        "disallowed_patterns": [
            r"<script", r"javascript:",  # XSS
        ],
        "brand_safety": ["political", "religious"],
    },
    "facebook": {
        "max_length": 63206,
        "disallowed_patterns": [
            r"<script", r"javascript:",
        ],
        "brand_safety": ["political", "religious", "health_claims"],
    },
    "instagram": {
        "max_length": 2200,
        "disallowed_patterns": [],
        "brand_safety": ["political", "religious", "body_image"],
    },
    "email": {
        "max_length": 15000,
        "disallowed_patterns": [
            r"unsubscribe", r"click here to unsubscribe",  # CAN-SPAM violation
        ],
        "brand_safety": [],
    },
}


# -------------------------------------------------------------------------
# Data classes
# -------------------------------------------------------------------------


@dataclass
class ModerationFlag:
    """A single moderation flag."""

    flag_type: str  # profanity | brand_safety | harmful | platform | vague_superlative | banned_cta
    matched_text: str
    severity: Severity
    message: str


@dataclass
class ContentModerationResult:
    """
    Result of content moderation.

    Attributes:
        is_safe: True if content passes all checks
        flags: List of ModerationFlag objects
        severity: Overall severity (max of all flags)
        warnings: Human-readable warning strings
        platform: Platform the content is for (if specified)
        checked_at: Timestamp of the check
    """

    is_safe: bool = True
    flags: list[ModerationFlag] = field(default_factory=list)
    severity: Severity = Severity.LOW
    warnings: list[str] = field(default_factory=list)
    platform: str = "general"
    checked_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_safe": self.is_safe,
            "flags": [
                {
                    "flag_type": f.flag_type,
                    "matched_text": f.matched_text,
                    "severity": f.severity.value,
                    "message": f.message,
                }
                for f in self.flags
            ],
            "severity": self.severity.value,
            "warnings": self.warnings,
            "platform": self.platform,
            "checked_at": self.checked_at,
        }


# -------------------------------------------------------------------------
# Moderator
# -------------------------------------------------------------------------


class ContentModerator:
    """
    Content moderation with profanity, brand safety, and platform-specific checks.

    Supports demo/mock mode — returns safe by default when no LLM is configured.
    """

    def __init__(self, mock_mode: bool | None = None):
        """
        Initialize the moderator.

        Args:
            mock_mode: Force mock mode. None = auto-detect.
        """
        self.mock_mode = mock_mode if mock_mode is not None else self._detect_mock_mode()
        logger.info("content_moderator_initialized", mock_mode=self.mock_mode)

    def moderate(
        self,
        text: str,
        platform: str = "general",
        artifact_type: str | None = None,
    ) -> ContentModerationResult:
        """
        Moderate text content.

        Args:
            text: Text content to check
            platform: Target platform (twitter, linkedin, facebook, instagram, email)
            artifact_type: Optional artifact type for contextual checks

        Returns:
            ContentModerationResult with flags, severity, and warnings
        """
        if self.mock_mode:
            return self._mock_result(platform)

        return self._real_moderation(text, platform, artifact_type)

    # ---------------------------------------------------------------------
    # Real moderation
    # ---------------------------------------------------------------------

    def _real_moderation(
        self,
        text: str,
        platform: str,
        artifact_type: str | None,
    ) -> ContentModerationResult:
        """Run real moderation checks."""
        flags: list[ModerationFlag] = []
        warnings: list[str] = []

        text_lower = text.lower()
        text_raw = text  # preserve original for pattern matching

        # 1. Profanity check
        profanity_flags = self._check_profanity(text_lower)
        flags.extend(profanity_flags)

        # 2. Brand safety — competitor disparagement
        competitor_flags = self._check_competitor_disparagement(text_lower)
        flags.extend(competitor_flags)

        # 3. Harmful content
        harmful_flags = self._check_harmful_content(text_lower)
        flags.extend(harmful_flags)

        # 4. Platform-specific rules
        platform_flags = self._check_platform_rules(text, platform)
        flags.extend(platform_flags)

        # 5. Banned CTAs
        cta_flags = self._check_banned_ctas(text_lower)
        flags.extend(cta_flags)

        # 6. Vague superlatives
        vague_flags = self._check_vague_superlatives(text)
        flags.extend(vague_flags)

        # Determine overall severity
        severity = Severity.LOW
        for flag in flags:
            if flag.severity == Severity.HIGH:
                severity = Severity.HIGH
            elif flag.severity == Severity.MEDIUM and severity != Severity.HIGH:
                severity = Severity.MEDIUM

        is_safe = severity == Severity.LOW and len(flags) == 0

        warnings = [f.message for f in flags]

        return ContentModerationResult(
            is_safe=is_safe,
            flags=flags,
            severity=severity,
            warnings=warnings,
            platform=platform,
        )

    def _check_profanity(self, text: str) -> list[ModerationFlag]:
        """Check for profanity words."""
        flags = []
        # Simple word boundary split
        words = re.findall(r"\b\w+\b", text)
        for word in words:
            if word in PROFANITY_WORDS:
                flags.append(ModerationFlag(
                    flag_type="profanity",
                    matched_text=word,
                    severity=Severity.HIGH,
                    message=f"Profanity detected: '{word}'",
                ))
        return flags

    def _check_competitor_disparagement(self, text: str) -> list[ModerationFlag]:
        """Check for competitor disparagement."""
        flags = []
        for phrase in COMPETITOR_DISPARAGEMENT:
            if phrase in text:
                flags.append(ModerationFlag(
                    flag_type="brand_safety",
                    matched_text=phrase.strip(),
                    severity=Severity.MEDIUM,
                    message=f"Competitor disparagement: contains '{phrase.strip()}'",
                ))
        return flags

    def _check_harmful_content(self, text: str) -> list[ModerationFlag]:
        """Check for harmful content patterns."""
        flags = []
        for phrase in HARMFUL_CONTENT:
            if phrase in text:
                flags.append(ModerationFlag(
                    flag_type="harmful_content",
                    matched_text=phrase,
                    severity=Severity.HIGH,
                    message=f"Harmful content: '{phrase}'",
                ))
        return flags

    def _check_platform_rules(
        self,
        text: str,
        platform: str,
    ) -> list[ModerationFlag]:
        """Check platform-specific rules."""
        flags = []
        rules = PLATFORM_RULES.get(platform, {})
        disallowed = rules.get("disallowed_patterns", [])

        for pattern in disallowed:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(ModerationFlag(
                    flag_type="platform_violation",
                    matched_text=pattern,
                    severity=Severity.MEDIUM,
                    message=f"Platform violation ({platform}): pattern '{pattern}'",
                ))

        # Brand safety per platform
        brand_safety = rules.get("brand_safety", [])
        text_lower = text.lower()
        for category in brand_safety:
            if category in text_lower:
                flags.append(ModerationFlag(
                    flag_type="brand_safety",
                    matched_text=category,
                    severity=Severity.MEDIUM,
                    message=f"Brand safety ({platform}): sensitive category '{category}'",
                ))

        return flags

    def _check_banned_ctas(self, text: str) -> list[ModerationFlag]:
        """Check for banned CTA patterns."""
        flags = []
        for cta in BANNED_CTAS:
            if cta in text:
                flags.append(ModerationFlag(
                    flag_type="banned_cta",
                    matched_text=cta,
                    severity=Severity.MEDIUM,
                    message=f"Banned CTA detected: '{cta}'",
                ))
        return flags

    def _check_vague_superlatives(self, text: str) -> list[ModerationFlag]:
        """Check for vague superlatives that violate advertising policies."""
        flags = []
        for pattern in VAGUE_SUPERLATIVES:
            if re.search(pattern, text, re.IGNORECASE):
                flags.append(ModerationFlag(
                    flag_type="vague_superlative",
                    matched_text=pattern,
                    severity=Severity.LOW,
                    message=f"Vague superlative/advertising policy: pattern '{pattern}'",
                ))
        return flags

    # ---------------------------------------------------------------------
    # Mock moderation (demo mode)
    # ---------------------------------------------------------------------

    def _mock_result(self, platform: str) -> ContentModerationResult:
        """Return safe mock result for demo/dev mode."""
        logger.debug("moderation_mock_mode", platform=platform)
        return ContentModerationResult(
            is_safe=True,
            flags=[],
            severity=Severity.LOW,
            warnings=[],
            platform=platform,
        )

    # ---------------------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------------------

    @staticmethod
    def _detect_mock_mode() -> bool:
        return not bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    def is_mock(self) -> bool:
        return self.mock_mode


# -------------------------------------------------------------------------
# Convenience function
# -------------------------------------------------------------------------


def moderate_content(
    text: str,
    platform: str = "general",
    artifact_type: str | None = None,
    mock_mode: bool | None = None,
) -> ContentModerationResult:
    """
    Moderate text content (convenience function).

    Args:
        text: Text content to check
        platform: Target platform
        artifact_type: Optional artifact type
        mock_mode: Force mock mode

    Returns:
        ContentModerationResult
    """
    if mock_mode is None:
        mock_mode = not bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY"))

    moderator = ContentModerator(mock_mode=mock_mode)
    return moderator.moderate(text, platform, artifact_type)