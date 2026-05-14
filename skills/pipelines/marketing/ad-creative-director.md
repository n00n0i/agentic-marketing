# Ad Creative Director — Paid Ad Creative Production

## Role

Transforms `targeting_profile` and `copy_variants` into platform-specific ad creatives. Produces `ad_creative` artifact with headlines, descriptions, images, and format specifications for each paid channel.

## Input

- `targeting_profile` — audience, bid strategy, budget
- `copy_variants` — copy variants (or adapted from organic copy)
- `brand_guidelines` — visual guidelines for consistency
- `campaign_objective` — conversion, awareness, consideration

## Process

### Step 1: Ad Format Requirements

For each platform, understand format requirements:

**Google RSA (Responsive Search Ads):**
```python
GOOGLE_RSA = {
    "headlines": {
        "count": "3-15",
        "length": "30 chars each",
        "recommendation": "At least 10 for learning"
    },
    "descriptions": {
        "count": "2-4",
        "length": "90 chars each",
        "recommendation": "All 4 for learning"
    },
    "path1/path2": "Optional URL components"
}
```

**Meta Ads:**
```python
META_ADS = {
    "primary_text": {"max_length": 125, "count": 1-5},
    "headline": {"max_length": 40, "count": 1-5},
    "description": {"max_length": 20, "count": 1-2},
    "call_to_action": {"choices": ["Learn More", "Shop Now", "Sign Up", "Book Demo", "Download"]},
    "image_specs": {
        "aspect_ratios": ["1:1", "4:5", "9:16", "16:9"],
        "min_resolution": "1080x1080"
    }
}
```

**LinkedIn Ads:**
```python
LINKEDIN_ADS = {
    "introductory_text": {"max_length": 70, "count": 1},
    "headline": {"max_length": 70, "count": 1-5},
    "description": {"max_length": 200, "count": 1-5},
    "cta": {"choices": ["Learn More", "Register", "Sign Up", "Download", "Get Quote"]},
    "image_specs": {
        "aspect_ratios": ["1:1", "1.91:1"],
        "max_file_size": "5MB"
    }
}
```

### Step 2: Headline Variations

Generate headline variations that:

1. **Include primary keyword** — Match targeting keywords
2. **Show value proposition** — What's the benefit?
3. **Add urgency** — Time-limited or scarcity
4. **Social proof** — Numbers, testimonials, authority

```python
HEADLINE_VARIATIONS = [
    {
        "headline": "Reduce SaaS Ops Costs 40% with AI",
        "type": "value_prop",
        "includes_keyword": True,
        "platforms": ["google", "linkedin"]
    },
    {
        "headline": "Join 500+ SaaS Teams Using AI Automation",
        "type": "social_proof",
        "includes_keyword": False,
        "platforms": ["meta", "linkedin"]
    },
    {
        "headline": "Free AI Ops Assessment — Book in 5 Minutes",
        "type": "urgency_cta",
        "includes_keyword": False,
        "platforms": ["google", "meta"]
    }
]
```

### Step 3: Body Copy Adaptation

Adapt copy_variants for ad format:

```python
def adapt_for_ad(copy_variant, ad_format):
    """Adapt a copy variant into ad body."""
    if ad_format == "google_rsa_description":
        # 90 chars max
        return copy_variant.body[:87] + "..."
    elif ad_format == "meta_primary_text":
        # 125 chars max
        return copy_variant.body[:122] + "..."
    elif ad_format == "linkedin_description":
        # 200 chars max
        return copy_variant.body[:197] + "..."
```

### Step 4: Image/Visual Selection

For each ad creative:

```python
image_requirements = {
    "google_display": {
        "aspect_ratio": "1.91:1",
        "sizes": ["1200x628", "300x250", "300x600"],
        "text_policy": "≤20% text overlay"
    },
    "meta_feed": {
        "aspect_ratio": "1:1 or 4:5",
        "sizes": ["1080x1080", "1080x1350"],
        "text_policy": "No text on image (or minimal)"
    },
    "linkedin_feed": {
        "aspect_ratio": "1.91:1",
        "sizes": ["1200x627"],
        "text_policy": "Minimal text overlay"
    }
}
```

### Step 5: CTA Selection

```python
CTA_STRENGTH_BY_STAGE = {
    "awareness": ["Learn More", "Find Out More", "Discover"],
    "consideration": ["Get Started", "Try Free", "Book Demo", "Get Your Guide"],
    "conversion": ["Get Started Free", "Start Now", "Get Your Demo"],
    "retargeting": ["Complete Your Setup", "Finish Signup", "Claim Your Offer"]
}
```

### Step 6: Compliance Check

```python
COMPLIANCE_CHECKS = {
    "google": {
        "prohibited": ["free", "best", "#1", "lowest price guaranteed"],
        "required": ["visible landing page URL"],
        "trademark": "Cannot use competitor trademarks in ads"
    },
    "meta": {
        "prohibited": ["guaranteed results", "as seen on", "testimonials without disclosure"],
        "required": ["privacy policy link for apps"],
        "format": "Must match selected call-to-action type"
    },
    "linkedin": {
        "prohibited": ["personal attributes (age, gender, religion)"],
        "required": ["professional tone"],
        "format": "Career-related messaging appropriate"
    }
}
```

## Output: ad_creative Artifact

```json
{
  "version": "1.0",
  "ad_id": "ad-001",
  "targeting_profile_ref": "tgt-001",
  "copy_variant_ref": "cv-001",
  "campaign_objective": "conversion",

  "platforms": [
    {
      "platform": "google_ads",
      "format": "responsive_search_ad",
      "status": "ready",
      "headlines": [
        {"text": "Reduce SaaS Ops Costs 40%", "pin": null, "status": "active"},
        {"text": "AI Automation for SaaS Teams", "pin": null, "status": "active"},
        {"text": "Free AI Ops Assessment", "pin": null, "status": "active"},
        {"text": "Cut Ops Costs — No Setup Fee", "pin": null, "status": "active"},
        {"text": "SaaS Ops Automation Platform", "pin": null, "status": "active"},
        {"text": "Automate Your SaaS Workflows", "pin": null, "status": "active"},
        {"text": "Stop Wasting 15 hrs/week on Ops", "pin": null, "status": "active"},
        {"text": "AI That Actually Works for SaaS", "pin": null, "status": "active"},
        {"text": "40% Cost Reduction Guaranteed", "pin": null, "status": "active"},
        {"text": "SaaS Teams Use AI for Ops", "pin": null, "status": "active"}
      ],
      "descriptions": [
        {"text": "Join 500+ SaaS teams using AI to automate ops. Cut costs 40%. Book free assessment today.", "pin": null},
        {"text": "AI ops automation that actually works. No lengthy setup. See ROI in 30 days. Book demo.", "pin": null},
        {"text": "Stop manual ops from draining resources. AI automation handles the busywork. Free audit.", "pin": null},
        {"text": "The AI ops platform that SaaS teams trust. 40% cost reduction. Start free trial.", "pin": null}
      ],
      "path1": "ai-ops",
      "path2": "automation",
      "final_url": "https://example.com/ai-ops-automation",
      "call_to_action": "Get Your Free Assessment",
      "compliance_passed": true,
      "compliance_notes": []
    },
    {
      "platform": "meta_ads",
      "format": "single_image",
      "status": "ready",
      "components": {
        "primary_text": "Your SaaS team is wasting 15 hours a week on tasks that should be automated.\n\nWe built AI that fixes this. Results:\n\n✓ 70% of ops tasks automated\n✓ 40% cost reduction\n✓ ROI in 30 days\n\nJoin 500+ SaaS teams. Book your free AI ops assessment.",
        "headline": "Cut SaaS Ops Costs 40%",
        "description": "Free Assessment · No Setup Fee",
        "call_to_action": "Book Free Assessment"
      },
      "image_specs": {
        "format": "1:1",
        "sizes": ["1080x1080"],
        "file_path": "creatives/ad-001/meta-1080x1080.png",
        "text_overlay_pct": 8,
        "face_detection": "1 face detected (professional photo)"
      },
      "image_generation_params": {
        "prompt": "modern SaaS office, professional team working at computers with data dashboards visible, clean minimal style, warm natural lighting, no text overlay",
        "model": "flux",
        "style": "professional, approachable"
      },
      "ad_set_name": "SaaS Ops - Conversion - Meta",
      "campaign_name": "AI Ops Automation - May 2026",
      "compliance_passed": true,
      "compliance_notes": []
    },
    {
      "platform": "linkedin_ads",
      "format": "single_image",
      "status": "ready",
      "components": {
        "introductory_text": "AI Automation for SaaS Operations",
        "headline": "Cut SaaS Ops Costs 40% with AI",
        "description": "Join 500+ SaaS teams using AI to automate ops. 70% of tasks automated. 40% cost reduction. Book your free assessment.",
        "call_to_action": "Book Free Assessment"
      },
      "image_specs": {
        "format": "1.91:1",
        "sizes": ["1200x627"],
        "file_path": "creatives/ad-001/linkedin-1200x627.png",
        "text_overlay_pct": 5
      },
      "image_generation_params": {
        "prompt": "professional B2B SaaS setting, senior executives in modern office, data screens showing efficiency metrics, executive attire, clean corporate style",
        "model": "flux",
        "style": "professional, executive-focused"
      },
      "ad_set_name": "SaaS Founders - LinkedIn - Conversion",
      "campaign_name": "AI Ops Automation - May 2026",
      "compliance_passed": true,
      "compliance_notes": ["LinkedIn requires professional tone - verified"]
    }
  ],

  "compliance_summary": {
    "google_ads": {
      "passed": true,
      "issues": []
    },
    "meta_ads": {
      "passed": true,
      "issues": []
    },
    "linkedin_ads": {
      "passed": true,
      "issues": []
    }
  },

  "creative_test_plan": {
    "test_type": "creative_variations",
    "test_variable": "headline_angle",
    "variants": [
      {
        "variant_name": "Value Prop Lead",
        "headline": "Reduce SaaS Ops Costs 40%",
        "expected_ctr_increase": "+15% vs control"
      },
      {
        "variant_name": "Social Proof Lead",
        "headline": "Join 500+ SaaS Teams",
        "expected_ctr_increase": "+8% vs control"
      },
      {
        "variant_name": "Problem Lead",
        "headline": "Stop Wasting 15 hrs/week",
        "expected_ctr_increase": "+12% vs control"
      }
    ],
    "test_duration_days": 14,
    "minimum_sample_size": 1000,
    "winner_criteria": "ctr_increase ≥ 10%"
  },

  "asset_files": {
    "google_ads": "creatives/ad-001/google-assets.zip",
    "meta_ads": ["creatives/ad-001/meta-1080x1080.png", "creatives/ad-001/meta-4x5-1080x1350.png"],
    "linkedin_ads": ["creatives/ad-001/linkedin-1200x627.png"]
  },

  "total_creative_cost_estimate": 0.25
}
```

## Review Focus

Before approving ad_creative, reviewer MUST verify:

1. **Format compliance** — Are headlines/descriptions within character limits?
2. **CTA specific** — Is CTA action-oriented and appropriate for objective?
3. **Image specs correct** — Are dimensions and file sizes correct per platform?
4. **Compliance passed** — No prohibited claims or trademark violations?
5. **Keyword alignment** — Do headlines include targeting keywords?
6. **A/B test plan** — Is there a structured test plan with clear winner criteria?

## Success Criteria

- ≥3 headline variations per platform
- ≥2 description variations per platform
- All format specs correct per platform
- Compliance checks passed for all platforms
- Image assets generated or sourced
- A/B test plan documented
- Creative cost tracked

## Common Pitfalls

1. **Character limit violations** — Headlines/descriptions too long
2. **Generic CTAs** — "Learn More" instead of specific action
3. **No image variation** — Same image across all formats
4. **Missing compliance** — Prohibited claims included
5. **No test plan** — No structure for learning from creative
6. **Keyword mismatch** — Headlines don't include targeting keywords