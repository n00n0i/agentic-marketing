# Brief Director — Content Brief Generation

## Role

Transforms `market_brief` and `channel_strategy` into specific content briefs for each piece of content to be created. A content brief is the bridge between strategy and execution.

## Input

- `market_brief` — audience segments, strategic angles, competitors, keywords
- `channel_strategy` — which channels to activate, content mix per channel
- `content_request` — what content piece is needed (topic, format, channel)

## Process

### Step 1: Content Piece Definition

For each content piece, determine:

```python
content_piece = {
    "piece_id": f"cp-{uuid.uuid4().hex[:8]}",
    "title": str,                  # e.g., "How AI Cuts SaaS Churn by 40%"
    "topic": str,                 # core topic/keyword
    "format": str,                 # blog, social_post, ad, email, video_script
    "channel": str,               # linkedin, twitter, email, etc.
    "strategic_angle": str,       # angle_id from market_brief
    "target_segment": str,        # segment_id from market_brief
}
```

### Step 2: Angle Selection

Select the strategic angle that best fits this content piece:

- Match angle's target segment with content's target audience
- Match angle's persistence (evergreen vs timely) with content's purpose
- Match angle's channel fit with the content's channel

Document the selection:
```python
{
    "decision_id": "dec-brief-001",
    "stage": "brief",
    "category": "content_angle_selection",
    "subject": f"Selected angle '{angle.name}' for {content_piece.piece_id}",
    "options_considered": [...],
    "selected": angle.angle_id,
    "reason": "..."
}
```

### Step 3: Content Objective

Define what this piece should achieve:

```python
objectives = {
    "primary": "awareness" | "consideration" | "conversion" | "retention",
    "secondary": [...],  # Can have multiple secondary objectives
    "kpi": str,         # What metric defines success
    "target_value": float,  # What value of the KPI we're targeting
}
```

### Step 4: Content Parameters

For each platform, define content parameters:

```python
PLATFORM_PARAMS = {
    "twitter": {
        "max_length": 280,
        "include_hashtags": True,
        "include_link": True,
        "best_practices": [
            "Lead with the hook in first 100 chars",
            "Use 1-2 relevant hashtags at end",
            "Include a single clear CTA"
        ]
    },
    "linkedin": {
        "max_length": 3000,
        "include_image": True,
        "best_practices": [
            "Start with a question or bold statement",
            "Use 3-4 short paragraphs max",
            "Include a CTA that encourages comments"
        ]
    },
    "email": {
        "max_length": 300,
        "subject_line_required": True,
        "preview_text_required": True,
        "best_practices": [
            "Subject under 50 chars",
            "Preview text under 100 chars",
            "Body in 3 paragraphs max"
        ]
    }
}
```

### Step 5: CTA Definition

```python
cta_strategy = {
    "type": "resource_download" | "trial" | "demo" | "subscribe" | "engagement",
    "specific_text": str,      # "Get the free guide" not "click here"
    "destination": str,       # URL or action description
    "placement": str,         # "inline" | "end" | "both"
    "commitment_level": "low" | "medium" | "high"  # Match to awareness level
}
```

## Output: content_brief Artifact

```json
{
  "version": "1.0",
  "brief_id": "cb-001",
  "market_brief_ref": "mb-001",
  "channel_strategy_ref": "strat-001",

  "content_piece": {
    "piece_id": "cp-001",
    "title": "How AI Automation Cuts SaaS Ops Costs by 40%",
    "topic": "SaaS operations automation ROI",
    "format": "linkedin_article",
    "channel": "linkedin",
    "strategic_angle_ref": "angle-1",
    "target_segment_ref": "seg-1"
  },

  "objectives": {
    "primary": "awareness",
    "secondary": ["consideration"],
    "kpi": "engagement_rate",
    "target_value": 3.5
  },

  "content_parameters": {
    "word_count_target": "1800-2200 words",
    "reading_time": "4-5 minutes",
    "structure": "problem_hook → data_support → solution → case_example → CTA",
    "key_points": [
      "Problem: Manual ops waste 15 hrs/week",
      "Data: 73% of SaaS companies exploring AI",
      "Solution: AI automation framework",
      "Example: 40% cost reduction in 90 days"
    ],
    "visual_requirements": ["hero_image", "data_visualization", "quote_card"],
    "platform_compliance": {
      "linkedin": {
        "max_length": 3000,
        "best_times": ["7am EST", "12pm EST", "5pm EST"],
        "engagement_tips": ["Use 2-3 line breaks", "End with question for comments"]
      }
    }
  },

  "brand_voice": {
    "tone": "professional but approachable",
    "vocabulary_use": ["we", "SaaS teams", "automation", "efficiency"],
    "vocabulary_avoid": ["cutting-edge", "synergy", "leverage"],
    "formatting": ["short paragraphs", "numbered lists for processes", "bold for key stats"]
  },

  "cta": {
    "type": "resource_download",
    "specific_text": "Get the AI Ops Automation Playbook",
    "destination": "https://example.com/ai-ops-playbook",
    "placement": "end",
    "commitment_level": "low"
  },

  "seo_notes": {
    "primary_keyword": "SaaS ops automation",
    "secondary_keywords": ["AI automation ROI", "reduce SaaS costs", "ops efficiency"],
    "keyword_density": "2-3%",
    "meta_description": "How SaaS teams reduce ops costs 40% with AI automation"
  },

  "timing": {
    "publish_date": "2026-05-21",
    "publish_time": "7am EST",
    "promotion_plan": {
      "twitter_promotion": true,
      "email_list_promotion": true,
      "linkedin_community_post": false
    }
  },

  "success_criteria": {
    "engagement_rate_target": 3.5,
    "impressions_target": 10000,
    "click_through_target": 150
  }
}
```

## Review Focus

Before approving content_brief, reviewer MUST verify:

1. **Angle grounded in market_brief** — Does the selected angle have data backing from market_brief?
2. **CTA specific** — Is the CTA specific and action-oriented, not generic?
3. **Parameters realistic** — Are word count, timing targets achievable?
4. **Brand voice clear** — Are vocabulary_use/avoid clearly defined?
5. **SEO integrated** — Are keywords naturally integrated, not stuffed?

## Success Criteria

- Brief has clear alignment with market_brief strategic angle
- CTA is specific and appropriate for awareness level
- Content parameters are achievable and platform-appropriate
- Brand voice guidelines are clear
- Success metrics are measurable

## Common Pitfalls

1. **Vague CTA** — "Click here" instead of specific action
2. **Wrong angle for segment** — Not matching angle's target segment
3. **Overly long requirements** — Too many key points for format
4. **Unrealistic timing** — Not accounting for review cycles
5. **Missing SEO** — No keywords or meta description for blog content