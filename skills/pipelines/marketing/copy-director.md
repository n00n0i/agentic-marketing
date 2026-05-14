# Copy Director — Content Generation with A/B Variant Support

## Role

Transforms a `content_brief` into 3-5 distinct copy variants per platform, each scored for engagement potential. Copy is the core content that drives engagement across all channels.

## Inputs

- `market_brief` — audience segments, strategic angles, competitor analysis
- `content_brief` — what this specific piece should achieve
- `brand_voice` — tone, vocabulary, formatting guidelines from marketing state

## Process

### Step 1: Angle Selection

From `market_brief`, select the strategic angle for this content piece:

- **Primary angle** — the main message (must be present in ALL variants)
- **Secondary angle** — supporting proof or alternative framing (1-2 variants)
- **Hook angle** — attention-grabbing opener (1 variant for testing)

Document the selection in decision_log:
```python
{
    "decision_id": "dec-copy-001",
    "stage": "copy",
    "category": "content_angle_selection",
    "subject": f"Selected angle '{primary_angle}' for content piece {content_id}",
    "options_considered": [
        {"option_id": a["angle_id"], "score": 0.9, "pros": [...], "cons": [...]}
        for a in available_angles
    ],
    "selected": primary_angle,
    "reason": "...",
    "confidence": 0.85
}
```

### Step 2: Platform Analysis

For each target platform, analyze:

| Platform | Max Length | Tone | Best Format | Peak Times |
|----------|-----------|------|-------------|------------|
| Twitter/X | 280 chars | Conversational, value-dense | Hook + link | 8am, 12pm, 5pm EST |
| LinkedIn | 3,000 chars | Professional but personal | Hook + body + CTA | 7am, 12pm, 5pm EST |
| Facebook | 63,206 chars | Casual, community-focused | Short hook + link | 1pm, 4pm EST |
| Instagram | 2,200 chars | Visual-first, caption supports image | Caption + CTA in comments | 11am, 1pm, 7pm EST |
| Email Subject | 50 chars | Curiosity + urgency | Question or number | N/A |
| Email Body | 150-300 words | Personal, helpful | Story + value + CTA | N/A |

### Step 3: Variant Generation

Generate 3-5 variants for each platform using distinct approaches:

**Approach A: Problem-Led**
- Start with the pain point
- Show how it affects them specifically
- Transition to solution
- End with CTA

**Approach B: Outcome-Led**
- Start with the desired state
- Quantify the benefit
- Provide proof
- End with CTA

**Approach C: Question-Led**
- Start with engaging question
- Let them imagine the answer
- Reveal solution
- End with CTA

**Approach D: Stat-Led**
- Lead with surprising/compelling number
- Explain the implication
- Show the solution
- End with CTA

**Approach E: Story-Led**
- Brief narrative or example
- Pivot to lesson/insight
- Connect to solution
- End with CTA

### Step 4: CTA Integration

Every variant needs a CTA. Types:

| CTA Type | Example | Best For |
|----------|---------|----------|
| Resource download | "Get the free guide →" | Lead generation |
| Tool/Trial | "Start free trial" | SaaS, services |
| Consultation | "Book a 15-min call" | High-ticket |
| Content consumption | "Read the full guide" | Engagement |
| Social engagement | "Share your experience" | Community |

CTA Rules:
- NEVER use "click here" or "learn more" — too generic
- Be specific: "Get the 2026 AI Marketing Report" not "get our report"
- Match commitment level to awareness level

### Step 5: Engagement Scoring

Score each variant on:

```python
engagement_factors = {
    "hook_strength": 0-10,        # Does the first line grab attention?
    "clarity": 0-10,              # Is the message immediately understood?
    "relevance": 0-10,            # Does it resonate with target segment?
    "specificity": 0-10,          # Are claims backed with specifics?
    "cta_strength": 0-10,         # Is the CTA specific and compelling?
    "word_count_fit": 0-10,      # Is length appropriate for platform?
}

# Overall score is weighted average
weights = {
    "hook_strength": 0.25,
    "clarity": 0.15,
    "relevance": 0.20,
    "specificity": 0.15,
    "cta_strength": 0.15,
    "word_count_fit": 0.10,
}
```

## Output: copy_variants Artifact

```json
{
  "version": "1.0",
  "content_piece_id": "cp-001",
  "content_brief_ref": "cb-001",
  "market_brief_ref": "mb-001",
  "strategic_angle": "angle-1",
  "target_segment": "seg-1",
  "primary_message": "AI can identify at-risk customers 30 days before they churn",
  "platforms": ["linkedin", "twitter", "email"],

  "variants": [
    {
      "variant_id": "var-linkedin-A",
      "platform": "linkedin",
      "approach": "problem-led",
      "headline": "Your best customers are about to churn. Here's how to stop them.",
      "body": "Last quarter, 23% of our ARR came from just 5 accounts.\n\nIf any of them left, we'd be in trouble.\n\nSo we built an AI system that predicts churn 30 days in advance — with 85% accuracy.\n\nNow we reach out at day 15, not day 45. Churn dropped 40%.\n\nThe pattern we found: customers who stop using feature X within 14 days almost always churn within 60.\n\nSimple intervention — just one email with a personalized walkthrough — recovers 60% of at-risk accounts.\n\nThe data is in the guide. Link in comments.",
      "word_count": 187,
      "character_count": 1247,
      "cta": {
        "type": "resource_download",
        "text": "Get the Churn Prevention Guide",
        "url": "https://example.com/churn-guide",
        "placement": "inline"
      },
      "hashtags": ["#SaaS", "#CustomerSuccess", "#AI", "#ChurnPrevention"],
      "engagement_score": {
        "overall": 8.5,
        "hook_strength": 9,
        "clarity": 8,
        "relevance": 9,
        "specificity": 8,
        "cta_strength": 8,
        "word_count_fit": 9
      },
      "engagement_rationale": "Specific number (23% from 5 accounts) creates curiosity; real story makes it relatable; actionable takeaway (feature X pattern) gives immediate value",
      "posting_time": {
        "day": "Wednesday",
        "time": "7am EST"
      }
    },
    {
      "variant_id": "var-linkedin-B",
      "platform": "linkedin",
      "approach": "stat-led",
      "headline": "73% of SaaS companies are exploring AI for customer success.\n\nMost are doing it wrong.",
      "body": "Everyone's jumping on AI for churn prevention.\n\nThe problem: they're using it to react, not predict.\n\nHere's what actually works:\n\n1. Monitor usage patterns, not just NPS scores\n2. Set up alerts at 14-day and 30-day inactivity thresholds\n3. Auto-trigger personalized outreach based on usage gaps\n\nCompanies doing this cut churn 30-50%.\n\nCompanies using generic AI chatbots see almost no improvement.\n\nThe difference is in the data setup, not the AI model.\n\nWant the exact framework we use? Comment 'FRAMEWORK' and I'll send it over.",
      "word_count": 153,
      "character_count": 1048,
      "cta": {
        "type": "engagement",
        "text": "Comment 'FRAMEWORK' for the playbook",
        "placement": "end"
      },
      "hashtags": ["#AI", "#SaaS", "#CustomerSuccess", "#Growth"],
      "engagement_score": {
        "overall": 8.2,
        "hook_strength": 9,
        "clarity": 8,
        "relevance": 8,
        "specificity": 8,
        "cta_strength": 9,
        "word_count_fit": 8
      },
      "engagement_rationale": "Contrarian angle (most are doing it wrong) + numbered list format + low-commitment CTA (comment vs click)"
    },
    {
      "variant_id": "var-twitter-A",
      "platform": "twitter",
      "approach": "problem-led",
      "body": "Last quarter, 23% of our ARR came from 5 accounts.\n\nIf any left, we'd be in trouble.\n\nSo we built AI that predicts churn 30 days out. 85% accuracy.\n\nNow we intervene at day 15, not day 45.\n\nChurn dropped 40%.\n\nOne pattern we found: customers who stop using feature X in 14 days almost always churn in 60.\n\nSimple email with personalized walkthrough recovers 60% of at-risk accounts.\n\nFull breakdown + data ↓",
      "word_count": 102,
      "character_count": 687,
      "cta": {
        "type": "resource_download",
        "text": "Churn Prevention Guide ↓",
        "url": "https://example.com/churn-guide"
      },
      "engagement_score": {
        "overall": 8.8,
        "hook_strength": 9,
        "clarity": 9,
        "relevance": 9,
        "specificity": 8,
        "cta_strength": 9,
        "word_count_fit": 8
      },
      "engagement_rationale": "Hook (23% from 5 accounts) creates urgency; specific pattern gives actionable value; arrow emoji signals downward content"
    },
    {
      "variant_id": "var-email-subject",
      "platform": "email",
      "approach": "question-led",
      "subject": "Are your best customers about to leave?",
      "preview_text": "We built AI that predicts churn 30 days out. Here's what we found.",
      "body_section": {
        "hook": "Last month, we almost lost our biggest customer.\n\nThey'd stopped using our product for 14 days. We had no idea.\n\nWhen we finally reached out at day 30, they were already in talks with a competitor.",
        "value": "So we built an AI system that predicts churn risk in real-time.\n\nNow we know within 24 hours when a key account goes dark.\n\nWe've used it to save 8 accounts in the last quarter. Total ARR protected: $2.4M.",
        "cta": "If you want the exact framework we use — including the 3 signals that predict churn — I've put it all in a guide.\n\nGet it free here: [link]\n\nNo fluff. Just the exact steps and data."
      },
      "word_count": 167,
      "cta": {
        "type": "resource_download",
        "text": "Get the Churn Prevention Framework",
        "url": "https://example.com/churn-framework"
      },
      "engagement_score": {
        "overall": 9.0,
        "hook_strength": 10,
        "clarity": 9,
        "relevance": 9,
        "specificity": 8,
        "cta_strength": 9,
        "word_count_fit": 9
      },
      "engagement_rationale": "Story format creates emotional investment; 'almost lost biggest customer' creates urgency without being alarmist; specific dollar amount ($2.4M protected) adds credibility"
    }
  ],

  "brand_voice_check": {
    "tone": "professional but approachable — VERIFIED",
    "vocabulary_compliant": true,
    "formatting_compliant": true,
    "notes": "Used contractions ('we've') appropriately for conversational professional tone"
  },

  "platform_compliance": {
    "linkedin": {"compliant": true, "issues": []},
    "twitter": {"compliant": true, "issues": []},
    "email": {"compliant": true, "issues": []}
  }
}
```

## Review Focus

Before approving copy_variants, the reviewer MUST verify:

1. **Each variant has distinct angle** — Are variants actually different approaches, not just rewording?
2. **CTA specificity** — Is every CTA specific and action-oriented? No generic "click here" or "learn more"
3. **Platform compliance** — Does length fit platform? Are formatting guidelines followed?
4. **Brand voice consistency** — Does all copy follow brand guidelines?
5. **Data grounding** — Are claims backed by market_brief data?
6. **Engagement score honesty** — Are scores realistic? Check if rationale matches score.

## Success Criteria

- ≥3 variants per content piece
- Each variant has distinct approach (problem/outcome/question/stat/story)
- Each variant scored with engagement factors
- All variants pass brand voice check
- All variants pass platform compliance
- All CTAs are specific and action-oriented
- Total character count within platform limits

## Common Pitfalls

1. **Same approach across variants** — Just rewording, not changing framing
2. **Generic CTAs** — "Click here to learn more" instead of specific action
3. **Over-promotional** — All pitch, no value
4. **Too long** — Not adapting length for platform
5. **Inconsistent brand voice** — Different tones across variants
6. **Ungrounded claims** — Making statistics up without market_brief backing