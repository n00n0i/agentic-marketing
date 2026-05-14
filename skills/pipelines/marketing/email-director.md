# Email Director — Email Marketing Sequences

## Role

Transforms `market_brief` and `content_brief` into email sequences with personalization rules. Produces `email_sequence` artifact with full email templates, trigger conditions, and sequence flow.

## Input

- `market_brief` — audience segments, strategic angles
- `channel_strategy` — email budget, audience size
- `content_brief` — campaign topic and objectives

## Process

### Step 1: Sequence Design

Design email sequence flow:

```python
SEQUENCE_TYPES = {
    "welcome": {
        "emails": 3-5,
        "trigger": "new_subscriber",
        "purpose": "Onboard new subscribers, establish value",
        "time_between": "1-2 days"
    },
    "nurture": {
        "emails": 5-7,
        "trigger": "download_gated_content",
        "purpose": "Build consideration, demonstrate expertise",
        "time_between": "2-3 days"
    },
    "promotional": {
        "emails": 3-5,
        "trigger": "launch_or_promotion",
        "purpose": "Drive conversion for specific offer",
        "time_between": "2-4 days"
    },
    "reengagement": {
        "emails": 3,
        "trigger": "inactive_30_days",
        "purpose": "Win back inactive subscribers",
        "time_between": "5-7 days"
    },
    "retention": {
        "emails": 4-6,
        "trigger": "ongoing",
        "purpose": "Maintain engagement, upsell/cross-sell",
        "time_between": "weekly/biweekly"
    }
}
```

### Step 2: Segment Personalization

Define personalization rules per segment:

```python
PERSONALIZATION_RULES = {
    "segment_based": [
        {
            "segment_id": "seg-1",
            "segment_name": "B2B SaaS Founders",
            "greeting": "Hi {{first_name}}",
            "pain_point_reference": "scaling ARR",
            "tone": "direct, peer-to-peer"
        },
        {
            "segment_id": "seg-2",
            "segment_name": "Ops Managers",
            "greeting": "Hi {{first_name}}",
            "pain_point_reference": "team efficiency",
            "tone": "collaborative, practical"
        }
    ],
    "behavioral_triggers": [
        {
            "trigger": "downloaded_guide",
            "personalization": "Reference the specific guide downloaded",
            "timing": "Send within 24 hours"
        },
        {
            "trigger": "visited_pricing_page",
            "personalization": "Acknowledge pricing interest, address objections",
            "timing": "Send within 48 hours"
        }
    ]
}
```

### Step 3: Subject Line Strategy

```python
SUBJECT_LINE_VARIATIONS = {
    "curiosity": [
        "The 15-hour problem (and how to fix it)",
        "We analyzed 500 SaaS teams. Here's what we found.",
        "What's actually killing your SaaS team's productivity"
    ],
    "specificity": [
        "How to cut SaaS ops costs by 40% in 90 days",
        "The automation playbook 500+ SaaS teams are using",
        "Your free AI ops assessment is ready"
    ],
    "question": [
        "Is your SaaS team wasting 15 hours a week?",
        "Ready to cut ops costs 40%?",
        "What would you do with 15 extra hours per week?"
    ],
    "urgency": [
        "Limited time: Free AI ops assessment",
        "Last chance: AI ops automation guide",
        "Today only: Book your free strategy session"
    ]
}
```

### Step 4: Email Template Structure

```python
EMAIL_TEMPLATE_STRUCTURE = {
    "email_number": 1,
    "purpose": "hook",
    "timing": "Day 1",
    "subject": {
        "primary": "The 15-hour problem",
        "preview_text": "We analyzed your SaaS team's time. Here's what we found."
    },
    "structure": {
        "hook": "First 50 words — grab attention with problem statement",
        "body": "150-200 words — provide value and insight",
        "cta": "Final 50 words — clear next step"
    },
    "personalization_tokens": ["{{first_name}}", "{{company_name}}"],
    "trackable_links": ["primary_cta", "secondary_cta"]
}
```

### Step 5: GDPR/CAN-SPAM Compliance

```python
COMPLIANCE_CHECKLIST = {
    "gdpr": {
        "consent_recorded": True,
        "unsubscribe_link": True,
        "physical_address": True,
        "privacy_policy_link": True,
        "legitimate_interest_documented": True
    },
    "can_spam": {
        "sender_identity_clear": True,
        "physical_address": True,
        "unsubscribe_mechanism": True,
        "accurate_from_line": True,
        "subject_line_not_misleading": True
    }
}
```

## Output: email_sequence Artifact

```json
{
  "version": "1.0",
  "sequence_id": "seq-001",
  "sequence_name": "SaaS Ops AI Automation Nurture Sequence",
  "sequence_type": "nurture",
  "market_brief_ref": "mb-001",
  "trigger": "download_gated_content",
  "audience_segments": ["seg-1", "seg-2"],

  "emails": [
    {
      "email_number": 1,
      "name": "The Hook",
      "purpose": "Hook — establish problem",
      "timing": "Day 1 (immediate)",
      "delay_hours": 0,

      "subject": {
        "primary": "The 15-hour problem",
        "preview_text": "We analyzed your SaaS team's time. Here's what we found.",
        "variations": [
            "What's actually killing your SaaS team's productivity?",
            "We analyzed 500 SaaS teams. Here's what we found."
        ]
      },

      "from_name": "Agentic Marketing",
      "reply_to": "team@example.com",

      "body": {
        "greeting": "Hi {{first_name}},",
        "opening_hook": "Your SaaS team is probably wasting 15 hours a week on tasks that should be automated.\n\nWe know because we analyzed how SaaS teams actually spend their time. The pattern is the same everywhere: manual data entry, status update meetings, copy-paste between tools, manual reporting.\n\nThat time adds up fast.",
        "body_content": "For a 10-person SaaS team, 15 hours per person per week = 7,800 hours per year. That's nearly 4 full-time employees doing nothing but busywork.\n\nThe fix isn't hiring. It's automation.\n\nWe built an AI system that automates 70% of repetitive ops tasks. Results from our clients:\n\n• 40% reduction in ops costs\n• 70% of tasks automated\n• Data errors dropped to near zero\n• Teams focus on actual work again",
        "cta_section": "If you want to see exactly where your team is wasting time — and how to fix it — we built a free AI Ops Assessment.\n\nIt takes 5 minutes. You get a personalized report showing:\n\n✓ Your estimated wasted hours per week\n✓ The 3 biggest automation opportunities\n✓ A suggested automation roadmap\n\nGet your free assessment: [link]",
        "closing": "Talk soon,\nThe Agentic Marketing Team\n\nP.S. The assessment is free. No credit card. No sales pitch. Just data.",
        "signature": "Agentic Marketing | AI for SaaS Teams"
      },

      "personalization_tokens": ["{{first_name}}", "{{company_name}}"],
      "personalization_conditions": {
        "{{company_name}}": "Only if available, otherwise omit"
      },

      "trackable_links": [
        {
          "url": "https://example.com/ai-ops-assessment",
          "label": "Get free assessment",
          "cta_position": "body"
        }
      ],

      "formatting": {
        "line_length": "65 characters",
        "bullet_style": "✓ checkmarks",
        "bold_keywords": ["15 hours", "40%", "5 minutes"],
        "links_underlined": false
      },

      "compliance": {
        "unsubscribe_link": true,
        "physical_address": true,
        "privacy_policy_link": true
      },

      "metrics_target": {
        "open_rate_target": 35,
        "click_rate_target": 8,
        "reply_rate_target": 2
      }
    },
    {
      "email_number": 2,
      "name": "The Framework",
      "purpose": "Provide value — demonstrate expertise",
      "timing": "Day 3",
      "delay_hours": 48,

      "subject": {
        "primary": "The 3-step automation framework we use with SaaS clients",
        "preview_text": "Here's exactly how we approach AI ops automation",
        "variations": [
          "The automation framework that cut our clients' costs 40%",
          "3 steps to automate your SaaS ops"
        ]
      },

      "body": {
        "greeting": "Hi {{first_name}},",
        "opening_hook": "Last email, I mentioned we use a specific framework for AI ops automation. Here's exactly what that looks like.\n\nIt starts with finding the right tasks to automate.",
        "body_content": "Step 1: Find the 20%\n\nLook at your team's weekly tasks. Identify the 20% that are:\n✓ Repetitive (same format every time)\n✓ High-frequency (happening daily or weekly)\n✓ Error-prone (human mistakes are common)\n\nThese are your automation targets. The highest-impact, lowest-friction wins.\n\nStep 2: Map the Data Flow\n\nMost manual tasks have a hidden problem: data moving between tools without automation. Your team is acting as the integration layer.\n\nFind where data is being re-entered or copied. That's where the automation ROI is highest.\n\nStep 3: Start Small, Measure Everything\n\nDon't try to automate everything at once. Start with one task. Measure the impact. Then expand.\n\nThe teams we work with that follow this approach see ROI within 30 days. They also avoid the trap of automating the wrong things.",
        "cta_section": "Want us to analyze your team's automation opportunities? Our AI Ops Assessment does exactly that.\n\nIt identifies your highest-impact automation targets in 5 minutes.\n\nGet your free assessment: [link]",
        "closing": "More soon,\nThe Agentic Marketing Team",
        "signature": "Agentic Marketing | AI for SaaS Teams"
      },

      "personalization_tokens": ["{{first_name}}"],
      "trackable_links": [
        {
          "url": "https://example.com/ai-ops-assessment",
          "label": "Get your free assessment",
          "cta_position": "body"
        }
      ],

      "metrics_target": {
        "open_rate_target": 30,
        "click_rate_target": 10,
        "reply_rate_target": 3
      }
    },
    {
      "email_number": 3,
      "name": "The Case Study",
      "purpose": "Social proof — show it works",
      "timing": "Day 6",
      "delay_hours": 72,

      "subject": {
        "primary": "How we cut a SaaS team's ops costs by 40% in 90 days",
        "preview_text": "Real numbers from a real client engagement",
        "variations": [
          "Case study: 40% ops cost reduction in 90 days",
          "From 15 hours wasted to 5 — here's how"
        ]
      },

      "body": {
        "greeting": "Hi {{first_name}},",
        "opening_hook": "I want to share something specific. A client we worked with last quarter. SaaS company, 45 employees, $8M ARR.\n\nThey were spending 15+ hours per week per person on manual ops tasks. Revenue ops, customer success ops, financial ops — all manual.",
        "body_content": "Here's what we did:\n\nFirst, we identified their automation targets. The biggest wins were:\n✓ Revenue data entry from 6 different sources\n✓ Weekly KPI reporting (manual aggregation)\n✓ Customer health score updates\n\nThen we built AI automations for each. The result after 90 days:\n\n• Ops cost reduced by 40% ($180k annual savings)\n• 70% of manual tasks automated\n• Data errors near zero\n• The ops team now focuses on strategic work\n\nThe interesting part: we started with the smallest task first. Proved ROI quickly. Used that to build momentum for the bigger automations.",
        "cta_section": "If you're evaluating AI ops automation for your team, this might be useful to see:\n\n✓ The exact tasks we automated\n✓ How we measured ROI\n✓ What the 90-day timeline looked like\n\nGet the full case study: [link]",
        "closing": "Questions? Just reply to this email.\n\nMore soon,\nThe Agentic Marketing Team",
        "signature": "Agentic Marketing | AI for SaaS Teams"
      },

      "metrics_target": {
        "open_rate_target": 28,
        "click_rate_target": 12,
        "reply_rate_target": 4
      }
    },
    {
      "email_number": 4,
      "name": "The CTA",
      "purpose": "Drive conversion",
      "timing": "Day 10",
      "delay_hours": 96,

      "subject": {
        "primary": "Ready to see your automation opportunities?",
        "preview_text": "5-minute assessment. Real data. No sales pitch.",
        "variations": [
          "Your AI ops opportunities are waiting",
          "5 minutes to see your automation potential"
        ]
      },

      "body": {
        "greeting": "Hi {{first_name}},",
        "opening_hook": "If you've read the last 3 emails and thought 'this makes sense, but I want to see it applied to my specific situation' — that's exactly what the AI Ops Assessment is for.",
        "body_content": "It takes 5 minutes to complete. You answer questions about your current ops setup. Our AI analyzes your responses and produces a personalized report showing:\n\n✓ Your estimated wasted hours per week\n✓ The 3 biggest automation opportunities for your team\n✓ A suggested automation roadmap with estimated ROI\n\nNo fluff. No generic advice. Just specific insights based on your situation.\n\nPlus, after you complete it, one of our team will reach out to walk through your results. No obligation. No pressure.",
        "cta_section": "Get your free AI Ops Assessment: [link]\n\nIt takes 5 minutes. You'll get insights you can use immediately, whether you work with us or not.",
        "closing": "Talk soon,\nThe Agentic Marketing Team\n\nP.S. We've given this assessment to 500+ SaaS teams. Average result: 12 hours per week per person in wasted ops time identified. That's usually the starting point for their automation journey.",
        "signature": "Agentic Marketing | AI for SaaS Teams"
      },

      "personalization_tokens": ["{{first_name}}"],
      "trackable_links": [
        {
          "url": "https://example.com/ai-ops-assessment",
          "label": "Get your free assessment →",
          "cta_position": "body"
        }
      ],

      "compliance": {
        "unsubscribe_link": true,
        "physical_address": true,
        "privacy_policy_link": true,
        "legitimate_interest_note": "We've established legitimate interest as you downloaded content related to this sequence"
      },

      "metrics_target": {
        "open_rate_target": 25,
        "click_rate_target": 8,
        "conversion_rate_target": 3
      }
    }
  ],

  "sequence_settings": {
    "send_days": ["tuesday", "wednesday", "thursday"],
    "send_times": ["9am EST", "2pm EST"],
    "timezone": "EST",
    "ab_test_enabled": true,
    "ab_test_config": {
      "test_variable": "subject_line",
      "sample_size_pct": 20,
      "test_duration_hours": 4,
      "winner_metric": "open_rate"
    }
  },

  "trigger_conditions": {
    "primary_trigger": {
      "type": "download",
      "asset": "AI Ops Automation Guide",
      "delay": "immediate"
    },
    "exit_conditions": [
      {"type": "purchase", "delay": "0"},
      {"type": "unsubscribe", "delay": "0"},
      {"type": "complaint", "delay": "0"}
    ],
    "pause_conditions": [
      {"type": "clicked", "delay": "30 days"},
      {"type": "replied", "delay": "14 days"}
    ]
  },

  "personalization_rules": {
    "segment_based": [
      {
        "segment_id": "seg-1",
        "segment_name": "B2B SaaS Founders",
        "greeting": "Hi {{first_name}},",
        "pain_point_emphasis": "scaling ARR, team efficiency",
        "tone": "peer-to-peer, direct"
      },
      {
        "segment_id": "seg-2",
        "segment_name": "Ops Managers",
        "greeting": "Hi {{first_name}},",
        "pain_point_emphasis": "team efficiency, process improvement",
        "tone": "collaborative, practical"
      }
    ],
    "behavioral_triggers": [
      {
        "trigger": "downloaded_guide",
        "reference_content": true,
        "timing": "within_24_hours"
      },
      {
        "trigger": "opened_but_not_clicked",
        "reference_previous_email": true,
        "timing": "48_hours_after"
      }
    ]
  },

  "compliance_verified": true,
  "compliance_notes": [
    "GDPR: consent recorded at opt-in, legitimate interest documented for existing subscribers",
    "CAN-SPAM: sender identity clear, physical address included, unsubscribe mechanism functional",
    "Unsubscribe processed within 10 business days per CAN-SPAM requirement"
  ],

  "total_emails_in_sequence": 4,
  "sequence_duration_days": 10,
  "estimated_total_send_cost_usd": 0.04
}
```

## Review Focus

Before approving email_sequence, reviewer MUST verify:

1. **Sequence coherence** — Does the sequence tell a story across emails?
2. **Subject line variety** — Are subject lines compelling without being clickbait?
3. **Personalization appropriate** — Are tokens placed correctly and conditionally?
4. **Timing logical** — Is timing appropriate for buyer journey?
5. **GDPR/CAN-SPAM compliance** — Are all compliance requirements met?
6. **CTA appropriate** — Is CTA specific and action-oriented in each email?

## Success Criteria

- 4-7 email templates in sequence
- Each email has distinct subject line variations
- Personalization for ≥2 segments
- Trigger conditions defined
- All compliance requirements verified
- A/B test configuration included
- Metrics targets per email

## Common Pitfalls

1. **All emails same tone** — No variation in approach across sequence
2. **Clickbait subject lines** — Over-promising in subject, under-delivering in body
3. **Too frequent** — Sending too many emails too fast
4. **Generic personalization** — Tokens without real segment differentiation
5. **Missing exit conditions** — Not pausing sequence for purchasers/unsubscribes
6. **No compliance** — Missing unsubscribe links or physical address