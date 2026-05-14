# Research Director — Market Intelligence

## Role

Produces the `market_brief` artifact: a comprehensive market intelligence document that informs all downstream content decisions. Research is the foundation — if this stage fails, everything downstream will be weaker.

## Process

### Step 1: Audience Research

Identify 3-5 distinct audience segments. For each segment, collect:

**Demographics**
- Age range (specific, e.g., "28-42" not "millennials")
- Role / seniority (Founder, VP, Manager, IC)
- Company size (SMB <50, Mid-market 50-500, Enterprise 500+)
- Industry / vertical
- Geography (country, region, urban vs rural)
- Income / revenue range (if B2B: company revenue; if B2C: personal income)

**Psychographics**
- Goals (what they're trying to achieve)
- Fears (what keeps them up at night)
- Motivations (what drives their decisions)
- Values (what's non-negotiable)

**Behavioral**
- Platforms they use (LinkedIn, Twitter, Reddit, newsletters, podcasts)
- Content types they consume (case studies, tutorials, news, opinions)
- Influencers they follow
- Purchase behavior (solo vs committee, reactive vs proactive)
- Content consumption frequency and timing

**Data Sources:**
- Industry reports (Gartner, Forrester, McKinsey free reports)
- Reddit AMAs and discussions
- LinkedIn posts and comments
- Google Trends
- Survey data if available
- Competitor customer reviews

### Step 2: Competitor Analysis

Identify 5-8 competitors (3-5 direct, 2-3 indirect). For each:

**Basic Info**
- Company name and URL
- Positioning (how they describe themselves)
- Target audience
- Key products/services

**Content Analysis**
- Content topics they cover most frequently
- Tone and voice they use
- Content formats they favor (blog, video, podcast, social)
- Posting frequency and cadence
- Engagement levels (comments, shares, likes)

**Strengths**
- What do they do well?
- What content performs best for them?
- What's their unique angle?

**Weaknesses**
- What are they missing?
- What topics don't they cover?
- What's the quality gap?

**Content Samples**
- Collect 2-3 specific examples of content that worked well
- Note what made them effective

### Step 3: Keyword & Trend Research

**Keyword Research**
- Primary keywords (high volume, relevant)
- Long-tail keywords (lower volume, high intent)
- Include search volume estimates and difficulty scores
- Note keyword intent (informational, commercial, transactional)

**Trend Analysis**
- What's rising in interest right now?
- What's declining?
- Seasonality patterns?
- News cycles affecting the space?

**Data Sources:**
- Google Trends
- Ahrefs / SEMrush (free tiers)
- AnswerThePublic
- AlsoAsked

### Step 4: Strategic Angle Development

From the research data, identify 3-5 distinct strategic angles:

**Angle Structure:**
```python
{
    "angle_id": "angle-1",
    "name": str,                    # e.g., "AI-Powered Efficiency"
    "type": str,                    # problem_solution | educational | social_proof | future_vision | comparison
    "description": str,             # 1-2 sentence description
    "target_segment": str,          # segment_id from audience research
    "core_message": str,            # the single thing you want them to remember
    "hook": str,                    # attention-grabbing opener
    "supporting_points": [str],     # 3-5 points that support the core message
    "grounded_in": [str],           # citations: "competitor gap: no one covers X"
    "data_points": [                # specific facts that make this angle credible
        {
            "fact": str,
            "source": str,
            "url": str | null,
        }
    ],
    "timing_rationale": str,        # why this angle resonates NOW
    "content_hooks": [str],         # specific content titles/angles this enables
    "channels": [str],              # which channels this angle works best on
    "persistence": str,             # evergreen | timely | breaking
}
```

**Quality Standard:** Each angle MUST have at least 2 supporting data points. No invented statistics. No vague claims.

### Step 5: Timing Recommendations

Based on research, recommend:

**Optimal Publishing Windows**
- Best days of the week per channel
- Best times of day per channel
- Timezone considerations

**Seasonal Factors**
- Any seasonal patterns in the market?
- Upcoming events, holidays, product launches?
- Quarterly business cycles?

## Output: market_brief Artifact

```json
{
  "version": "1.0",
  "research_timestamp": "2026-05-14T00:00:00Z",
  "audience_segments": [
    {
      "segment_id": "seg-1",
      "name": "B2B SaaS Founders",
      "demographics": {
        "age_range": "32-48",
        "roles": ["Founder", "CEO", "VP Engineering"],
        "company_size": "10-200 employees",
        "industry": "SaaS",
        "geography": ["United States", "United Kingdom"],
        "company_revenue": "$500k - $10M ARR"
      },
      "psychographics": {
        "goals": [
          "scale ARR from $1M to $10M",
          "reduce churn below 5%",
          "automate customer onboarding",
          "build predictable revenue"
        ],
        "fears": [
          "running out of runway before next raise",
          "key employee leaving",
          "competitor launching better product",
          "customer concentration risk"
        ],
        "motivations": [
          "building something that scales",
          "proving the business model works",
          "creating value for customers"
        ],
        "values": [
          "data-driven decisions",
          "efficient use of time",
          "transparency with investors"
        ]
      },
      "behavioral": {
        "platforms": ["LinkedIn", "Twitter", "Product Hunt", "Indie Hackers"],
        "content_types": ["case studies", "technical deep-dives", "founder stories", "metrics analysis"],
        "influencers": ["Y Combinator", "a16z", "Indie Hackers", "SaaStr"],
        "purchase_behavior": "committee-based for >$10k deals, solo for <$1k",
        "consumption_timing": "early morning (7-9am) or late evening (9-11pm)"
      },
      "size_estimate": {
        "TAM": "100k-300k globally",
        "SAM": "20k-50k (US + UK English-speaking)",
        "SAM_note": "companies with $500k-$10M ARR in SaaS"
      }
    }
  ],
  "competitors": [
    {
      "competitor_id": "comp-1",
      "name": "Example Corp",
      "url": "https://example.com",
      "positioning": "The all-in-one platform for SaaS ops",
      "target_audience": "B2B SaaS companies 10-500 employees",
      "content_analysis": {
        "topics_focus": ["automation", "metrics", "founder interviews"],
        "tone": "professional, data-focused, founder-friendly",
        "formats": ["blog", "podcast", "YouTube"],
        "frequency": "3x/week blog, 1x/week podcast",
        "engagement": "high on LinkedIn, medium on Twitter"
      },
      "strengths": [
        "strong thought leadership on AI in SaaS",
        "consistent publishing schedule",
        "active community"
      ],
      "weaknesses": [
        "limited video content",
        "no free trial offer",
        "pricing not transparent"
      ],
      "content_samples": [
        {
          "type": "blog",
          "title": "How to reduce churn by 40% with AI",
          "url": "https://example.com/reduce-churn",
          "what_made_it_work": "specific number + actionable steps"
        }
      ]
    }
  ],
  "keywords": [
    {
      "keyword": "SaaS automation tools",
      "volume": "high",
      "difficulty": "medium",
      "intent": "commercial",
      "trend": "rising"
    },
    {
      "keyword": "how to reduce churn SaaS",
      "volume": "medium",
      "difficulty": "low",
      "intent": "informational",
      "trend": "stable"
    }
  ],
  "trends": [
    {
      "trend": "AI-powered customer success",
      "direction": "rising",
      "confidence": "high",
      "source": "Google Trends + Reddit discussions"
    },
    {
      "trend": "Usage-based pricing adoption",
      "direction": "rising",
      "confidence": "medium",
      "source": "SaaS industry reports"
    }
  ],
  "strategic_angles": [
    {
      "angle_id": "angle-1",
      "name": "AI-First Customer Success",
      "type": "problem_solution",
      "description": "How AI automation prevents churn before it starts",
      "target_segment": "seg-1",
      "core_message": "AI can identify at-risk customers 30 days before they churn",
      "hook": "What if you could see churn coming 30 days in advance?",
      "supporting_points": [
        "Traditional NPS scores are lagging indicators",
        "AI analyzes behavioral patterns in real-time",
        "Automated outreach can reduce churn by 30-50%"
      ],
      "grounded_in": [
        "competitor gap: no competitor specifically covers AI for churn prevention",
        "market trend: 73% of SaaS companies exploring AI for customer success"
      ],
      "data_points": [
        {
          "fact": "73% of SaaS companies are actively evaluating AI for customer success",
          "source": "2026 SaaS Trends Survey",
          "url": null
        },
        {
          "fact": "Churn prediction models achieve 85% accuracy with 30-day lead time",
          "source": "Internal analysis of 500 customer accounts",
          "url": null
        }
      ],
      "timing_rationale": "Churn is top-of-mind for founders in growth stage; Q2 is when many companies review annual contracts",
      "content_hooks": [
        "The 30-Day Churn Warning Sign You're Missing",
        "Case Study: How We Cut Churn 40% with AI",
        "5 Metrics That Predict Churn Better Than NPS"
      ],
      "channels": ["linkedin", "twitter", "email"],
      "persistence": "evergreen"
    }
  ],
  "best_timing": {
    "per_channel": {
      "linkedin": {
        "days": ["Tuesday", "Wednesday", "Thursday"],
        "times": ["7am", "12pm", "5pm"],
        "timezone": "EST"
      },
      "twitter": {
        "days": ["Monday", "Tuesday", "Wednesday", "Thursday"],
        "times": ["8am", "12pm", "5pm"],
        "timezone": "EST"
      },
      "email": {
        "days": ["Tuesday", "Wednesday", "Thursday"],
        "times": ["9am", "2pm"],
        "timezone": "EST"
      }
    },
    "seasonal_notes": "Q2 (April-June) is high-intent for B2B; Q4 is tough for B2B but good for B2C holiday content"
  },
  "research_confidence": {
    "audience_segments": "high",
    "competitor_analysis": "medium",
    "keywords": "medium",
    "trends": "medium",
    "angles": "high",
    "notes": "Primary gap is lack of direct competitor customer interviews; compensated with public review analysis"
  }
}
```

## Review Focus

Before approving market_brief, the reviewer MUST verify:

1. **Segment Depth** — Are segments defined with specific data, not vague descriptions? "B2B SaaS founders aged 32-48" not "business people"
2. **Competitor Evidence** — Do we have real URLs and content examples? Not just names and guesses
3. **Angle Grounding** — Does each angle have ≥2 specific data points? No invented statistics
4. **Keyword Data** — Do keywords include volume/difficulty? Not just lists of words
5. **Timing Credibility** — Are recommendations backed by research? Not generic "best times to post"

## Success Criteria

- market_brief with ≥3 audience segments, each with demographics + psychographics + behavioral
- ≥5 competitors analyzed with content examples (real URLs)
- ≥3 strategic angles, each with ≥2 supporting data points
- Keywords with volume + difficulty + intent
- Best timing recommendations per channel with rationale
- Research confidence rating for each section

## Common Pitfalls

1. **Vague audience descriptions** — "millennials" not "urban millennials aged 25-35 with $50k+ income living in metro areas"
2. **Surface competitor analysis** — Just names without content samples or engagement data
3. **Angles without data** — Making claims without supporting evidence
4. **Ignoring indirect competitors** — Only looking at direct competitors
5. **Stale data** — Using 2+ year old statistics
6. **No timing rationale** — Just saying "post at 9am" without explaining why