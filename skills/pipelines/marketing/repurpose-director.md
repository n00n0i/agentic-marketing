# Repurpose Director — Content Repurposing Engine

## Concept

1 content input → 10+ pieces across platforms. The repurposing director transforms a single piece of content (blog post, video script, podcast episode, webinar recording) into optimized content for each target platform.

**Core principle:** Adapt, don't copy-paste. Each output must feel native to its platform.

## Input Types

| Input Type | Processing |
|------------|------------|
| Blog post (1500-3000 words) | Parse → extract key points → reformat |
| Video script | Transcribe → extract hooks → generate description + clips |
| Podcast transcript | Same as video |
| Webinar recording | Auto-transcribe → extract insights → generate summary |
| Whitepaper / report | Extract executive summary → create slides |
| Case study | Extract narrative → create multiple formats |

## Output Framework

For each input, generate:

### Organic Social Outputs
1. **Twitter/X Thread** (5-7 tweets)
2. **LinkedIn Article** (expanded version)
3. **LinkedIn Post** (native format)
4. **Instagram Caption** (supports visual)
5. **Instagram Carousel** (8-10 slides)
6. **Instagram Reel Script** (60s)
7. **Facebook Post** (native format)
8. **YouTube Description** (summary + timestamps + links)

### Email Outputs
9. **Newsletter Snippet** (teaser + bullets)
10. **Email Forward-Copy** (story-style summary)

### Community & Engagement
11. **Quora Answer** (if relevant question exists)
12. **Reddit Post** (value-add contribution)
13. **TikTok Script** (30-60s)

### Paid Ad Variations
14. **Google RSA Headlines** (3-5)
15. **Meta Ad Copy** (headline + body)
16. **LinkedIn Ad Copy** (intro + description)

**Minimum: 10 outputs. Target: 12-16.**

## Process

### Step 1: Content Analysis

Parse the input and extract:

```python
content_analysis = {
    "main_argument": str,          # The single thesis
    "key_supporting_points": [str], # 3-5 main points
    "best_quotes": [str],           # 3-5 memorable lines
    "statistics": [str],            # Any numbers/facts
    "visual_opportunities": [str],  # Charts, diagrams needed
    "questions_addressed": [str],   # What the content answers
    "audience_pain_points": [str],  # Problems it solves
    "story_elements": [str],        # Narratives, examples
}
```

### Step 2: Platform Adaptation Rules

For each platform, transform the content:

```python
PLATFORM_RULES = {
    "twitter": {
        "max_length": 280,
        "format": "thread (5-7 tweets)",
        "structure": "hook_tweet → point_1 → point_2 → point_3 → link",
        "tone": "conversational, value-dense, no jargon",
        "hashtags": 1-3 (at end or first comment)",
        "media": "1 image or quote graphic"
    },
    "linkedin_article": {
        "max_length": 3000,
        "format": "expanded article",
        "structure": "hook → context → 3-5 key points → conclusion → CTA",
        "tone": "professional but personal, storytelling welcome",
        "cta": "comments, shares encouraged"
    },
    "linkedin_post": {
        "max_length": 3000,
        "format": "native post",
        "structure": "short hook → insight → call to action",
        "tone": "same as article but punchier"
    },
    "instagram_caption": {
        "max_length": 2200,
        "format": "caption",
        "structure": "hook (first line) → value → CTA in comments",
        "tone": "casual, visual-first, can use emojis",
        "hashtags": "in first comment"
    },
    "instagram_carousel": {
        "format": "slides",
        "slide_count": "8-10",
        "structure": "title → point_1 → point_2 → ... → CTA",
        "design": "text overlay on clean background"
    },
    "instagram_reel": {
        "format": "video script",
        "duration": "30-60s",
        "structure": "hook (0-3s) → point_1 (10-15s) → point_2 (10-15s) → CTA (5-10s)",
        "tone": "conversational, energetic, face-to-camera"
    },
    "facebook": {
        "max_length": 63206,
        "format": "native post",
        "structure": "short teaser → link → brief context",
        "tone": "casual, community-friendly"
    },
    "youtube_description": {
        "format": "description",
        "length": "200-400 words",
        "structure": "summary (200w) → timestamps → links → subscribe CTA"
    },
    "quora": {
        "format": "answer",
        "length": "300-800 words",
        "structure": "answer → source link",
        "tone": "helpful, educational, non-promotional"
    },
    "reddit": {
        "format": "post",
        "length": "500-1500 words",
        "structure": "context → insight → discussion prompt",
        "tone": "value-add, transparent about affiliation"
    },
    "email_newsletter": {
        "format": "snippet",
        "length": "100-200 words",
        "structure": "teaser paragraph → 3 bullet takeaways → link"
    }
}
```

### Step 3: Visual Repurposing

Transform visual elements:

```python
visual_transformations = {
    "quote_graphics": [
        # For each best_quote → generate quote graphic
        {
            "quote": "The best time to start was 6 months ago. The second best time is now.",
            "platform": "twitter",
            "format": "1200x675"
        }
    ],
    "stat_cards": [
        # For each statistic → generate stat card
        {
            "stat": "73%",
            "context": "of SaaS companies exploring AI for churn",
            "platform": "instagram",
            "format": "1080x1080"
        }
    ],
    "carousel_slides": [
        # For key points → generate carousel
        {
            "points": key_supporting_points,
            "platform": "instagram",
            "count": len(key_supporting_points) + 2  # + title + CTA
        }
    ]
}
```

### Step 4: Scheduling Recommendations

For each output, recommend optimal timing:

```python
def get_optimal_schedule(platform, content_type):
    schedules = {
        "twitter": {"day": "Tue/Wed/Thu", "time": "8am EST"},
        "linkedin_article": {"day": "Tue/Wed/Thu", "time": "7am EST"},
        "linkedin_post": {"day": "Tue/Wed/Thu", "time": "12pm EST"},
        "instagram": {"day": "Tue/Wed/Thu/Sat", "time": "11am EST"},
        "facebook": {"day": "Wed/Thu/Sun", "time": "1pm EST"},
        "email": {"day": "Tue/Wed/Thu", "time": "9am EST"},
        "youtube": {"day": "Tue or Thu", "time": "2pm EST"},
    }
    return schedules.get(platform, {"day": "Tue/Wed/Thu", "time": "10am EST"})
```

### Step 5: Quality Check

```python
def quality_check(output):
    """Ensure each output is platform-native, not copy-pasted."""
    issues = []

    # Check: Is it adapted, not copied?
    if output["word_count"] == input["word_count"] * 0.9:
        issues.append("Content appears copied, not adapted")

    # Check: Is tone appropriate?
    if output["platform"] == "twitter" and output["word_count"] > 250:
        issues.append("Twitter content exceeds character limit")

    # Check: Is the hook platform-appropriate?
    if output["platform"] == "linkedin" and not output["hook"]:
        issues.append("LinkedIn content missing hook")

    return issues
```

## Output: repurpose_plan Artifact

```json
{
  "version": "1.0",
  "input_content": {
    "type": "blog_post",
    "title": "How AI Automation Cuts SaaS Ops Costs by 40%",
    "url": "https://example.com/blog/ai-ops-costs",
    "word_count": 2147,
    "key_points_extracted": [
      "Manual ops waste 15 hrs/week per employee",
      "AI can automate 70% of repetitive ops tasks",
      "Companies see 40% cost reduction in 90 days",
      "Implementation takes 2-4 weeks",
      "ROI typically positive within 60 days"
    ],
    "best_quotes": [
      "The average SaaS team wastes 15 hours a week on tasks that should be automated.",
      "The first 20% of automation effort saves 80% of the wasted time."
    ],
    "statistics": [
      "15 hrs/week wasted on manual ops",
      "70% of tasks automatable",
      "40% cost reduction",
      "90 days to see full results"
    ]
  },

  "outputs": [
    {
      "output_id": "out-001",
      "platform": "twitter",
      "format": "thread",
      "piece_count": 7,
      "content": {
        "tweet_1": "The average SaaS team wastes 15 hours a week on manual ops tasks.\n\nThat's 780 hours/year per employee.\n\nFor a 10-person team, that's 7,800 hours. The cost? ↓",
        "tweet_2": "What are these 15 hours of waste?\n\n• Data entry from emails\n• Status update meetings\n• Manual reporting\n• Copy-paste between tools\n• Re-entering data after integrations break",
        "tweet_3": "The culprit: tools that don't talk to each other + humans doing what automation should handle.\n\nSound familiar?",
        "tweet_4": "Here's the pattern we see:\n\n1. App A has data\n2. Human copies to App B\n3. App C needs the same data\n4. Human copies again\n5. Errors accumulate\n6. Nobody knows what's real",
        "tweet_5": "The fix: AI automation that connects your tools and handles the busywork.\n\nWe implemented this with 3 clients last quarter.",
        "tweet_6": "Results:\n\n• 40% reduction in ops costs\n• 70% of repetitive tasks automated\n• Data errors dropped to near zero\n• Teams could focus on actual work",
        "tweet_7": "The first 20% of automation effort saves 80% of the wasted time.\n\nStart with your most repetitive task.\n\nFull breakdown + implementation guide ↓\nhttps://example.com/ai-ops-guide"
      },
      "scheduled_time": "2026-05-19T08:00:00Z",
      "status": "ready",
      "cta": "Link to blog post",
      "adaptation_notes": "Condensed to stat-led thread format; each tweet has single point; hook creates urgency"
    },
    {
      "output_id": "out-002",
      "platform": "linkedin",
      "format": "article",
      "piece_count": 1,
      "content": {
        "title": "How We Cut SaaS Ops Costs by 40% with AI Automation",
        "body": "Last quarter, I analyzed how our client teams spend their time.\n\nThe finding was uncomfortable: the average SaaS team wastes 15 hours per person per week on tasks that should be automated.\n\nThat's 780 hours per employee per year.\n\nFor a 10-person team, that's 7,800 hours. Equivalent to nearly 4 full-time employees doing nothing but busywork.\n\nThe pattern we found...\n\n[Full article body continues...]"
      },
      "scheduled_time": "2026-05-19T12:00:00Z",
      "status": "ready",
      "cta": "Engage with comments",
      "adaptation_notes": "Expanded with professional framing; storytelling approach; numbers put in context"
    },
    {
      "output_id": "out-003",
      "platform": "linkedin",
      "format": "post",
      "piece_count": 1,
      "content": {
        "hook": "15 hours a week. Per employee.\n\nThat's what the average SaaS team wastes on tasks that should be automated.",
        "body": "We analyzed 3 client teams last quarter.\n\nHere's the breakdown:\n• Data entry from emails: 4 hrs\n• Manual reporting: 3 hrs\n• Status update meetings: 3 hrs\n• Tool sync issues: 3 hrs\n• Re-entering data: 2 hrs\n\nTotal: 15 hours, every week.\n\nFor a 10-person team, that's 7,800 hours a year.\n\nThe fix isn't hiring. It's automation.\n\nWe automated 70% of these tasks. Cost dropped 40%.\n\nThe key insight: start with the most repetitive task, not the biggest.",
        "cta": "What's your biggest time sink? Comment below."
      },
      "scheduled_time": "2026-05-20T07:00:00Z",
      "status": "ready",
      "cta": "Engage with comments",
      "adaptation_notes": "Native format; short paragraphs; numbered breakdown; ends with question"
    },
    {
      "output_id": "out-004",
      "platform": "instagram",
      "format": "carousel",
      "piece_count": 8,
      "slides": [
        {"slide": 1, "content": "The 15-Hour Problem", "visual": "bold typography on dark background"},
        {"slide": 2, "content": "That's how much time the average SaaS team wastes weekly on manual ops tasks", "visual": "clock illustration"},
        {"slide": 3, "content": "Data entry from emails: 4 hrs", "visual": "email icon"},
        {"slide": 4, "content": "Manual reporting: 3 hrs", "visual": "document icon"},
        {"slide": 5, "content": "Status update meetings: 3 hrs", "visual": "meeting icon"},
        {"slide": 6, "content": "Tool sync issues: 3 hrs", "visual": "sync broken icon"},
        {"slide": 7, "content": "The fix: AI automation. 70% of tasks automated. 40% cost reduction.", "visual": "AI robot + chart"},
        {"slide": 8, "content": "Start with your most repetitive task → Link in bio", "visual": "CTA button"}
      ],
      "scheduled_time": "2026-05-20T11:00:00Z",
      "status": "ready",
      "cta": "Link in bio",
      "visual_assets_needed": ["carousel-slides-8.png"]
    },
    {
      "output_id": "out-005",
      "platform": "instagram",
      "format": "reel_script",
      "piece_count": 1,
      "content": {
        "script": "HOOK (0-3s): \"The average SaaS team wastes 15 hours a week on tasks that should be automated.\"\nPOINT 1 (3-15s): \"Here's what those 15 hours actually look like: data entry from emails, manual reporting, meetings about status updates...\"\nPOINT 2 (15-30s): \"The fix isn't hiring more people. It's automation. We did this for 3 client teams — 70% of tasks automated, costs dropped 40%.\"\nPOINT 3 (30-45s): \"The key insight: start with your most repetitive task. Not the biggest. The most repetitive.\"\nCTA (45-55s): \"Save this post. Start with that one task today.\""
      },
      "scheduled_time": "2026-05-21T19:00:00Z",
      "status": "ready",
      "cta": "Save + share",
      "adaptation_notes": "Script formatted for teleprompter; face-to-camera energy; hook must stop scroll"
    },
    {
      "output_id": "out-006",
      "platform": "email",
      "format": "newsletter",
      "piece_count": 1,
      "content": {
        "subject": "The 15-hour problem (and the AI fix)",
        "preview": "We analyzed 3 SaaS teams. Here's what we found.",
        "body": "Quick read: 3 min\n\nLast quarter we analyzed how SaaS teams spend their time.\n\nThe finding: the average team wastes 15 hours per person per week on tasks that should be automated.\n\nWhat those 15 hours look like:\n• Data entry: 4 hrs\n• Manual reporting: 3 hrs\n• Status meetings: 3 hrs\n• Tool sync issues: 3 hrs\n\nThe fix: AI automation that handles the repetitive work.\n\nFor the 3 teams we worked with:\n→ 70% of tasks automated\n→ Costs dropped 40%\n→ Data errors near zero\n\nFull breakdown + implementation guide: [link]"
      },
      "scheduled_time": "2026-05-21T09:00:00Z",
      "status": "ready",
      "cta": "Read full guide"
    },
    {
      "output_id": "out-007",
      "platform": "youtube",
      "format": "description",
      "piece_count": 1,
      "content": {
        "summary": "In this video, we break down how AI automation cut SaaS ops costs by 40% for three client teams. We cover: the 15-hour waste problem, what those hours actually cost, the 3-step automation framework, and real results from implementation.",
        "timestamps": "0:00 - Hook: The 15-hour problem\n0:45 - What the 15 hours actually look like\n2:30 - The cost impact\n4:15 - The automation framework\n7:00 - Results from 3 client implementations\n9:30 - How to get started\n11:00 - Resources and next steps",
        "links": "[Video description contains links to:\n- Full guide: example.com/ai-ops-guide\n- Automation template: example.com/templates\n- Free audit tool: example.com/audit]",
        "cta": "Subscribe for more content like this"
      },
      "scheduled_time": "2026-05-19T14:00:00Z",
      "status": "ready",
      "cta": "Subscribe + watch"
    },
    {
      "output_id": "out-008",
      "platform": "facebook",
      "format": "post",
      "piece_count": 1,
      "content": {
        "body": "15 hours a week. That's what the average SaaS team wastes on tasks that should be automated.\n\nWe analyzed 3 client teams last quarter. Here's the breakdown — does this match what you're seeing?\n\nDrop your biggest time sink in the comments 👇"
      },
      "scheduled_time": "2026-05-20T13:00:00Z",
      "status": "ready",
      "cta": "Engage in comments"
    },
    {
      "output_id": "out-009",
      "platform": "quora",
      "format": "answer",
      "piece_count": 1,
      "content": {
        "question": "How can AI reduce SaaS operational costs?",
        "body": "From our work with 3 SaaS teams last quarter: AI automation typically cuts ops costs 30-50%.\n\nHere's what that looks like in practice:\n\n1. Identify the 20% of tasks that are most repetitive\n2. Map the data flow between tools\n3. Implement AI to handle those tasks\n4. Measure and iterate\n\nThe key insight: start with the most repetitive task, not the biggest. The repetitive one has the clearest automation path.\n\nFor the teams we worked with, results were:\n→ 70% of repetitive tasks automated\n→ 40% cost reduction\n→ Near-zero data errors\n\nI've written a detailed guide on implementation: [link]"
      },
      "scheduled_time": null,
      "status": "ready",
      "cta": "Source attribution"
    },
    {
      "output_id": "out-010",
      "platform": "google_ads",
      "format": "rsa",
      "piece_count": 5,
      "content": {
        "headlines": [
          "SaaS Ops Cost Cut 40%",
          "AI Automation for SaaS",
          "Stop Wasting 15 hrs/week",
          "Free AI Ops Audit",
          "SaaS Team Efficiency"
        ],
        "descriptions": [
          "AI automation cuts SaaS ops costs by 40%. Free audit reveals your waste.",
          "70% of repetitive SaaS tasks automated. See your potential savings."
        ]
      },
      "scheduled_time": null,
      "status": "ready",
      "cta": "Book free audit"
    },
    {
      "output_id": "out-011",
      "platform": "meta_ads",
      "format": "single_image",
      "piece_count": 1,
      "content": {
        "headline": "SaaS Ops Are Broken",
        "body": "Your team is wasting 15 hrs/week on manual tasks. AI automation cuts that to zero.\n\n70% of repetitive tasks automated. 40% cost reduction.\n\nBook your free AI ops audit →",
        "cta": "Book Free Audit"
      },
      "scheduled_time": null,
      "status": "ready",
      "cta": "Book free audit"
    },
    {
      "output_id": "out-012",
      "platform": "tiktok",
      "format": "script",
      "piece_count": 1,
      "content": {
        "script": "HOOK (0-3s): \"POV: Your SaaS team is wasting 15 hours a week on tasks that should be automated.\"\n\nPOINT 1 (3-12s): Text overlay with the breakdown: data entry (4 hrs), manual reporting (3 hrs), status meetings (3 hrs), tool sync (3 hrs)\n\nPOINT 2 (12-25s): \"The fix isn't hiring. It's AI. We automated 70% of these tasks for 3 client teams — costs dropped 40%.\"\n\nCTA (25-30s): \"Save this. Start with your most repetitive task today.\""
      },
      "scheduled_time": "2026-05-21T19:00:00Z",
      "status": "ready",
      "cta": "Save this"
    }
  ],

  "cross_platform_consistency": {
    "core_message": "AI automation cuts SaaS ops costs by 40%",
    "key_stats": ["15 hrs/week wasted", "70% automatable", "40% cost reduction"],
    "all_platforms_aligned": true,
    "inconsistencies": []
  },

  "visual_assets_needed": [
    {"type": "quote_graphic", "content": "The first 20% of automation effort saves 80% of the wasted time.", "platform": "twitter"},
    {"type": "stat_card", "content": "15 hrs/week", "context": "wasted on manual ops", "platform": "instagram"},
    {"type": "stat_card", "content": "40%", "context": "cost reduction with AI", "platform": "linkedin"},
    {"type": "carousel_slides", "count": 8, "platform": "instagram"}
  ],

  "total_pieces": 12,
  "platforms_covered": ["twitter", "linkedin", "instagram", "facebook", "youtube", "email", "quora", "google_ads", "meta_ads", "tiktok"],
  "generation_cost_estimate": 0.30
}
```

## Review Focus

Before approving repurpose_plan, the reviewer MUST verify:

1. **Each output is adapted, not copy-pasted** — Does each piece feel native to its platform?
2. **Format correct per platform** — Are lengths and structures correct?
3. **Core message consistent** — Does all output reinforce the same core message?
4. **Scheduling optimized** — Are timing recommendations realistic?
5. **CTA appropriate** — Is CTA right for each platform?
6. **Visual assets defined** — Are all needed graphics listed?

## Success Criteria

- ≥10 output pieces from 1 input
- Each piece platform-optimized
- Core message consistent across all outputs
- All needed visual assets identified
- Scheduling optimized per platform
- No platform guideline violations

## Common Pitfalls

1. **Copy-paste approach** — Same content posted everywhere without adaptation
2. **Wrong format** — Posting blog-style content on Twitter
3. **Timing all the same** — Posting everything at once instead of staggered
4. **Forgetting CTAs** — Creating content without conversion path
5. **No visual planning** — Written content only, no graphics
6. **Over-promoting** — Every piece is a sales pitch instead of value