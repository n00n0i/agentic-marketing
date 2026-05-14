# Publish Director — Content Publishing & Scheduling

## Role

Executes the publishing workflow: validates content, formats for each platform, submits to scheduling tools, and confirms publication. Produces `publish_log` artifact that confirms publication details.

## Input

- `copy_variants` — approved copy variants
- `creative_assets` — generated images/creatives
- `content_brief` — timing and platform requirements
- `schedule` — approved publishing schedule

## Process

### Step 1: Platform-Specific Formatting

```python
PLATFORM_FORMAT_RULES = {
    "twitter": {
        "max_length": 280,
        "hashtag_placement": "end",
        "link_placement": "end",
        "image_max": 1,
        "image_format": ["jpg", "png", "gif"],
        "image_max_size_mb": 5,
        "thread_format": "numbered tweets with ↳"
    },
    "linkedin": {
        "max_length": 3000,
        "image_max": 1,
        "image_format": ["jpg", "png"],
        "image_max_size_mb": 8,
        "line_breaks": 3 per paragraph,
        "emoji_allowed": True,
        "cta_allowed": True
    },
    "facebook": {
        "max_length": 63206,
        "image_max": 10,
        "video_allowed": True,
        "hashtag_placement": "end or omit"
    },
    "instagram": {
        "max_length": 2200,
        "image_max": 10,
        "image_format": ["jpg", "png"],
        "image_aspect_ratio": "1:1, 4:5, or 9:16",
        "hashtag_max": 30,
        "hashtag_placement": "first comment or end"
    },
    "email": {
        "max_length": 500,
        "html_supported": True,
        "inline_images": True,
        "cta_format": "button or text link"
    }
}
```

### Step 2: Asset Validation

```python
def validate_assets(assets, platform):
    """Validate assets for platform compatibility."""
    errors = []
    warnings = []

    for asset in assets:
        # Check file size
        if asset.size_mb > PLATFORM_FORMAT_RULES[platform]["image_max_size_mb"]:
            errors.append(f"Image {asset.asset_id} exceeds size limit for {platform}")

        # Check format
        if asset.format not in PLATFORM_FORMAT_RULES[platform]["image_format"]:
            errors.append(f"Image {asset.asset_id} format {asset.format} not supported on {platform}")

        # Check aspect ratio
        if asset.aspect_ratio not in ACCEPTABLE_RATIOS.get(platform, []):
            warnings.append(f"Image {asset.asset_id} has non-standard aspect ratio {asset.aspect_ratio} for {platform}")

    return errors, warnings
```

### Step 3: Scheduling Logic

```python
def calculate_optimal_times(platform, audience_timezones):
    """Calculate optimal posting times for platform and audience."""
    BASE_TIMES = {
        "twitter": {
            "best": ["8am EST", "12pm EST", "5pm EST", "6pm EST"],
            "good": ["7am EST", "9am EST", "1pm EST", "4pm EST", "7pm EST"],
            "avoid": ["10pm EST", "11pm EST", "12am EST", "1am EST", "2am EST"]
        },
        "linkedin": {
            "best": ["7am EST", "8am EST", "12pm EST", "5pm EST"],
            "good": ["6am EST", "9am EST", "10am EST", "3pm EST", "4pm EST"],
            "avoid": ["6pm EST onwards"]
        },
        "facebook": {
            "best": ["9am EST", "1pm EST", "3pm EST"],
            "good": ["8am EST", "10am EST", "2pm EST", "4pm EST"],
            "avoid": ["10pm EST", "11pm EST", "12am EST"]
        },
        "instagram": {
            "best": ["11am EST", "7pm EST", "8pm EST"],
            "good": ["10am EST", "1pm EST", "3pm EST", "6pm EST", "9pm EST"],
            "avoid": ["2am EST", "3am EST", "4am EST", "5am EST"]
        }
    }

    return BASE_TIMES[platform]
```

### Step 4: Publishing Methods

```python
PUBLISHING_METHODS = {
    "buffer": {
        "supports": ["twitter", "linkedin", "facebook", "instagram"],
        "api": BufferAPI,
        "rate_limits": {
            "posts_per_day": 10,
            "scheduled_ahead_days": 14
        }
    },
    "hootsuite": {
        "supports": ["twitter", "linkedin", "facebook", "instagram"],
        "api": HootsuiteAPI,
        "rate_limits": {
            "posts_per_day": 50,
            "scheduled_ahead_days": 30
        }
    },
    "direct_api": {
        "twitter": TwitterAPI,
        "linkedin": LinkedInAPI,
        "facebook": MetaGraphAPI,
        "instagram": MetaGraphAPI,
        "email": MailchimpAPI
    }
}
```

## Output: publish_log Artifact

```json
{
  "version": "1.0",
  "publish_log_id": "pub-001",
  "content_brief_ref": "cb-001",
  "copy_variant_ref": "cv-001",
  "creative_asset_refs": ["asset-001", "asset-002"],

  "publications": [
    {
      "publication_id": "pub-twitter-001",
      "platform": "twitter",
      "content_type": "single_tweet",
      "status": "scheduled",
      "scheduled_at": "2026-05-14T12:00:00Z",
      "scheduled_timezone": "EST",
      "formatted_content": "Your SaaS team is probably wasting 15 hours a week on tasks that should be automated.\n\nWe analyzed how 500 SaaS teams spend their time. Here's what we found:\n\n✓ 15 hrs/week in manual ops\n✓ 70% of tasks automatable\n✓ 40% cost reduction with AI\n\nFree AI Ops Assessment → [link]\n\n#SaaS #Automation #AIOps",
      "character_count": 276,
      "hashtag_count": 3,
      "link_included": true,
      "asset_refs": ["asset-001"],
      "publishing_method": "buffer",
      "buffer_profile_id": "prof-001",
      "buffer_post_id": "bf-post-abc123",
      "buffer_post_url": "https://buffer.com/queue/prof-001/bf-post-abc123",
      "approval_status": "approved",
      "approval_source": "automated",
      "errors": [],
      "warnings": []
    },
    {
      "publication_id": "pub-linkedin-001",
      "platform": "linkedin",
      "content_type": "article_post",
      "status": "scheduled",
      "scheduled_at": "2026-05-14T08:00:00Z",
      "scheduled_timezone": "EST",
      "formatted_content": "Your SaaS team is probably wasting 15 hours a week on tasks that should be automated.\n\nWe know because we analyzed how SaaS teams actually spend their time. The pattern is the same everywhere: manual data entry, status update meetings, copy-paste between tools, manual reporting.\n\nFor a 10-person SaaS team, 15 hours per person per week = 7,800 hours per year. That's nearly 4 full-time employees doing nothing but busywork.\n\nThe fix isn't hiring. It's automation.\n\nWe built an AI system that automates 70% of repetitive ops tasks. Results from our clients:\n\n• 40% reduction in ops costs\n• 70% of tasks automated\n• Data errors dropped to near zero\n• Teams focus on actual work again\n\nIf you want to see exactly where your team is wasting time — and how to fix it — we built a free AI Ops Assessment.\n\nIt takes 5 minutes. You get a personalized report showing:\n\n✓ Your estimated wasted hours per week\n✓ The 3 biggest automation opportunities\n✓ A suggested automation roadmap\n\nGet your free assessment: [link]\n\n#SaaS #AIOps #Automation #Startup",
      "character_count": 1482,
      "image_included": true,
      "asset_refs": ["asset-002"],
      "publishing_method": "buffer",
      "buffer_profile_id": "prof-002",
      "buffer_post_id": "bf-post-def456",
      "approval_status": "approved",
      "approval_source": "automated",
      "errors": [],
      "warnings": []
    },
    {
      "publication_id": "pub-email-001",
      "platform": "email",
      "content_type": "email_campaign",
      "status": "scheduled",
      "scheduled_at": "2026-05-14T09:00:00Z",
      "scheduled_timezone": "EST",
      "subject": "The 15-hour problem",
      "preview_text": "We analyzed your SaaS team's time. Here's what we found.",
      "recipients": {
        "segment": "seg-1",
        "count": 1250,
        "filters_applied": ["subscribed", "has_downloaded_content"]
      },
      "publishing_method": "klaviyo",
      "klaviyo_campaign_id": "camp-xyz789",
      "approval_status": "approved",
      "approval_source": "automated",
      "errors": [],
      "warnings": []
    }
  ],

  "batch_summary": {
    "total_publications": 3,
    "by_platform": {
      "twitter": 1,
      "linkedin": 1,
      "email": 1
    },
    "by_status": {
      "scheduled": 3,
      "published": 0,
      "failed": 0
    },
    "first_publication_at": "2026-05-14T08:00:00Z",
    "last_publication_at": "2026-05-14T12:00:00Z"
  },

  "publishing_cost": {
    "buffer_cost_usd": 0.00,
    "klaviyo_cost_usd": 0.01,
    "total_cost_usd": 0.01
  },

  "metadata": {
    "published_by": "publish-director",
    "automation_level": "full",
    "human_review_required": false
  }
}
```

## Publishing Flow

```
Content Approved
      ↓
Format for Platform
      ↓
Validate Assets
      ↓
Check Rate Limits
      ↓
Select Publishing Method (Buffer / Direct API)
      ↓
Submit to Scheduler / Publish Directly
      ↓
Confirm Publication
      ↓
Log to publish_log
      ↓
Notify Analytics Director
```

## Error Handling

```python
ERROR_HANDLING = {
    "rate_limit_hit": {
        "action": "reschedule",
        "fallback_times": ["+1 hour", "+4 hours", "+1 day"]
    },
    "asset_upload_failed": {
        "action": "retry_without_asset",
        "fallback": "post_without_image"
    },
    "api_auth_failed": {
        "action": "alert_human",
        "fallback": "manual_publish_required"
    },
    "scheduling_conflict": {
        "action": "reschedule",
        "fallback_times": ["+30 min", "+2 hours"]
    }
}
```

## Review Focus

Before approving publication, reviewer MUST verify:

1. **Format compliance** — Character counts within limits per platform?
2. **Asset compatibility** — Images/videos compatible with platform specs?
3. **Timing appropriate** — Scheduled at optimal time for audience?
4. **Rate limits respected** — Not exceeding platform limits?
5. **CTA functional** — All links and CTAs working?
6. **Compliance met** — Required disclosures, hashtags within limits?

## Success Criteria

- All publications scheduled successfully
- No format violations
- Assets uploaded correctly
- Rate limits respected
- Publication log complete
- Analytics notified

## Common Pitfalls

1. **Character limit violations** — Content too long for platform
2. **Image format errors** — Wrong format or size for platform
3. **Rate limit conflicts** — Scheduling too many posts at once
4. **Timezone errors** — Scheduling at wrong timezone
5. **Broken links** — CTAs not validated before publishing
6. **Missing hashtags** — No hashtags on platforms where they're beneficial