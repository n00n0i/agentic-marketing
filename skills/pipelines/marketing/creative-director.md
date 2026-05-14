# Creative Director — Visual Asset Production

## Role

Transforms copy variants into visual assets: images, video thumbnails, ad creatives, quote graphics, and carousel layouts. Visual assets are generated per platform with correct aspect ratios and brand compliance.

## Inputs

- `copy_variants` — the copy that visuals will accompany
- `brand_guidelines` — colors, fonts, logo usage, image style
- `platform_specs` — required formats per platform

## Process

### Step 1: Visual Asset Planning

For each copy variant, determine what visual is needed:

```python
asset_requirements = []
for variant in copy_variants:
    if platform == "linkedin":
        if variant.approach == "problem-led":
            # Need: problem visualization + solution graphic
            asset_requirements.append({
                "variant_id": variant.variant_id,
                "type": "image",
                "purpose": "problem_visualization",
                "description": "illustration of customer at risk"
            })
    elif platform == "instagram":
        # Need: quote graphic for carousel
        asset_requirements.append({
            "variant_id": variant.variant_id,
            "type": "carousel",
            "purpose": "quote_graphics",
            "slides": 8
        })
```

Common visual types:
- **Hero image** — main visual for blog/posts
- **Quote graphic** — text overlay on background
- **Data visualization** — charts, stats display
- **Before/after** — comparison visual
- **Carousel slides** — multi-image story
- **Thumbnail** — video thumbnail
- **Ad creative** — paid ad visuals

### Step 2: Brand Application

For every asset, apply brand guidelines:

```python
def apply_brand_guidelines(asset):
    # Colors
    asset.primary_colors = brand.primary_colors
    asset.secondary_colors = brand.secondary_colors
    asset.accent_color = brand.accent_color

    # Typography
    asset.heading_font = brand.heading_font
    asset.body_font = brand.body_font
    asset.font_sizes = brand.min_font_sizes  # accessibility

    # Logo
    asset.logo_placement = brand.logo_placement
    asset.logo_size = brand.logo_size
    asset.logo_url = brand.logo_url

    # Imagery style
    asset.photography_style = brand.photography_style  # real/illustrated/minimalist
    asset.image_filter = brand.image_filter

    return asset
```

### Step 3: Platform Format Adaptation

Same core visual → multiple formats:

| Platform | Aspect Ratios | Image Sizes |
|----------|---------------|-------------|
| LinkedIn Feed | 1.91:1, 1:1 | 1200x627, 1080x1080 |
| Instagram Feed | 1:1 | 1080x1080 |
| Instagram Reels | 9:16 | 1080x1920 |
| Facebook | 1.91:1 | 1200x630 |
| Twitter | 16:9 | 1600x900 |
| Google Ads | 1.91:1, 1:1 | 1200x628, 1080x1080 |
| YouTube Thumbnail | 16:9 | 1280x720 |

```python
def adapt_for_platform(asset, target_platform):
    """Generate platform-specific versions of base asset."""
    formats = {
        "linkedin": {"size": (1200, 627), "ratio": "1.91:1"},
        "instagram": {"size": (1080, 1080), "ratio": "1:1"},
        "instagram_reel": {"size": (1080, 1920), "ratio": "9:16"},
        "facebook": {"size": (1200, 630), "ratio": "1.91:1"},
        "twitter": {"size": (1600, 900), "ratio": "16:9"},
        "google_ads": {"size": (1200, 628), "ratio": "1.91:1"},
    }
    return generate_formatted_versions(asset, formats[target_platform])
```

### Step 4: Image Generation

For each asset:

```python
# Option A: AI Image Generation
if config.use_ai_image:
    image_prompt = build_image_prompt(
        subject=copy_variant.key_message,
        style=brand.visual_style,
        composition=asset_type,
        colors=brand.primary_colors,
        avoid=["text overlay", "small fonts", "stock photo look"]
    )
    asset.image_url = image_generator.generate(image_prompt)

# Option B: Stock Image Selection
else:
    asset.image_url = stock_image_selector.select(
        keywords=copy_variant.key_topics,
        style=brand.photography_style,
        colors=brand.primary_colors
    )

# Option C: Quote Graphic (text-based)
if asset_type == "quote_graphic":
    asset = generate_quote_graphic(
        quote=copy_variant.primary_stat or copy_variant.hook,
        attribution=brand.name,
        style=brand.quote_style
    )
```

### Step 5: Video Thumbnail Specifics

For paid ads and YouTube:

```python
def create_video_thumbnail(asset):
    # Requirements
    # 1. First 3 seconds must grab attention
    # 2. Text readable on mobile (min 30px equivalent)
    # 3. Face or human element increases engagement
    # 4. End card / CTA overlay visible
    # 5. No misleading imagery

    thumbnail = {
        "aspect_ratio": "16:9",
        "min_resolution": (1280, 720),
        "text_placement": "lower third",
        "text_size": "30px minimum",
        "contrast": "high for mobile visibility",
        "cta_overlay": "bottom right or center",
        "safety_zone": "top 15% clear (platform UI interference)"
    }
```

### Step 6: Ad Creative Specifics

For paid ads (Meta, Google, LinkedIn):

```python
AD_FORMAT_REQUIREMENTS = {
    "meta_single_image": {
        "sizes": [(1200, 628), (1080, 1080)],
        "text_占比": "<20% of image",
        "cta_required": True
    },
    "meta_carousel": {
        "min_cards": 2,
        "max_cards": 10,
        "card_size": (1080, 1080)
    },
    "meta_video": {
        "min_duration": 1,
        "max_duration": 240,
        "recommended_duration": "15-30s",
        "autoplay_without_sound": True
    },
    "google_rsa": {
        "asset_sizes": [(1200, 628), (1080, 1080), (300, 300)],
        "headline_count": "3-15",
        "description_count": "2-4"
    },
    "linkedin_single_image": {
        "sizes": [(1200, 627)],
        "max_file_size": "5MB"
    }
}
```

## Output: creative_assets Artifact

```json
{
  "version": "1.0",
  "content_piece_id": "cp-001",
  "copy_variants_ref": "cv-001",
  "brand_guidelines_applied": {
    "primary_colors": ["#1a1a2e", "#16213e", "#e94560"],
    "secondary_colors": ["#0f3460", "#533483"],
    "heading_font": "Inter",
    "body_font": "Inter",
    "logo_usage": "bottom_right_corner",
    "image_style": "clean minimal, real photography, no stock photo look"
  },

  "assets": [
    {
      "asset_id": "asset-001",
      "type": "image",
      "purpose": "hero_image",
      "platform": "linkedin",
      "format": "1200x627",
      "variant_ref": "var-linkedin-A",
      "generation_method": "ai_image",
      "generation_params": {
        "prompt": "modern office setting, data dashboard visible on screen showing customer retention metrics, warm lighting, professional photography style, no text overlay",
        "model": "flux",
        "seed": null
      },
      "file_path": "creatives/cp-001/asset-001-linkedin-hero.png",
      "status": "ready",
      "color_palette_detected": ["#1a1a2e", "#16213e", "#e94560", "#f5f5f5"],
      "text_overlay": null,
      "cta_placement": "bottom_right",
      "brand_compliance": {
        "colors_match": true,
        "font_legible": true,
        "logo_present": true
      }
    },
    {
      "asset_id": "asset-002",
      "type": "quote_graphic",
      "purpose": "stat_visualization",
      "platform": "instagram",
      "format": "1080x1080",
      "variant_ref": "var-linkedin-B",
      "generation_method": "text_graphic",
      "generation_params": {
        "quote": "73% of SaaS companies are exploring AI for customer success. Most are doing it wrong.",
        "attribution": "Agentic Marketing",
        "style": "clean_white_background",
        "font": "Inter Bold",
        "font_size": "48px",
        "layout": "centered"
      },
      "file_path": "creatives/cp-001/asset-002-instagram-quote.png",
      "status": "ready",
      "text_content": "73% of SaaS companies are exploring AI for customer success. Most are doing it wrong.",
      "brand_compliance": {
        "colors_match": true,
        "font_legible": true,
        "logo_present": true
      }
    },
    {
      "asset_id": "asset-003",
      "type": "carousel",
      "purpose": "educational_carousel",
      "platform": "instagram",
      "format": "1080x1080",
      "slide_count": 8,
      "slides": [
        {
          "slide_number": 1,
          "type": "hook",
          "content": "Your best customers are about to churn.",
          "visual": "dark_background_red_text"
        },
        {
          "slide_number": 2,
          "type": "problem",
          "content": "73% of SaaS companies are exploring AI for churn prevention.",
          "visual": "stat_display"
        },
        {
          "slide_number": 3,
          "type": "solution",
          "content": "But most are using it to react, not predict.",
          "visual": "direction_arrow"
        },
        {
          "slide_number": 4,
          "type": "framework_step",
          "content": "Step 1: Monitor usage patterns, not NPS scores",
          "visual": "numbered_circle"
        },
        {
          "slide_number": 5,
          "type": "framework_step",
          "content": "Step 2: Set alerts at 14-day and 30-day inactivity",
          "visual": "numbered_circle"
        },
        {
          "slide_number": 6,
          "type": "framework_step",
          "content": "Step 3: Auto-trigger personalized outreach",
          "visual": "numbered_circle"
        },
        {
          "slide_number": 7,
          "type": "results",
          "content": "Companies doing this: 30-50% churn reduction",
          "visual": "chart_display"
        },
        {
          "slide_number": 8,
          "type": "cta",
          "content": "Get the full framework ↓",
          "visual": "cta_button"
        }
      ],
      "file_path": "creatives/cp-001/asset-003-instagram-carousel",
      "status": "ready",
      "brand_compliance": {
        "colors_match": true,
        "consistent_style": true,
        "logo_present": true
      }
    },
    {
      "asset_id": "asset-004",
      "type": "video_thumbnail",
      "purpose": "ad_thumbnail",
      "platform": "meta_ads",
      "format": "1200x628",
      "variant_ref": "var-linkedin-A",
      "generation_method": "ai_image",
      "generation_params": {
        "prompt": "close-up professional face, concerned expression, modern office background blurred, high contrast, text overlay safe zone clear",
        "model": "flux",
        "hook_element": "person looking at data dashboard showing warning signs"
      },
      "file_path": "creatives/cp-001/asset-004-meta-thumbnail.jpg",
      "status": "ready",
      "hook_preview": "First 3s: close-up concerned face → pan to warning dashboard",
      "cta_overlay": {
        "text": "Get the Guide",
        "position": "bottom_right",
        "font_size": "32px",
        "background": "semi-transparent dark"
      },
      "brand_compliance": {
        "text_legible_mobile": true,
        "safety_zone_clear": true,
        "cta_visible": true
      }
    },
    {
      "asset_id": "asset-005",
      "type": "quote_graphic",
      "purpose": "twitter_visual",
      "platform": "twitter",
      "format": "1600x900",
      "variant_ref": "var-twitter-A",
      "generation_method": "text_graphic",
      "generation_params": {
        "quote": "We built AI that predicts churn 30 days out. 85% accuracy. Churn dropped 40%.",
        "attribution": "Agentic Marketing",
        "style": "brand_colors_background",
        "font": "Inter Bold",
        "font_size": "56px"
      },
      "file_path": "creatives/cp-001/asset-005-twitter-quote.png",
      "status": "ready",
      "brand_compliance": {
        "colors_match": true,
        "font_legible": true,
        "logo_present": true
      }
    }
  ],

  "platform_formats": {
    "linkedin": {
      "assets_provided": ["asset-001"],
      "formats_validated": true,
      "issues": []
    },
    "instagram": {
      "assets_provided": ["asset-002", "asset-003"],
      "formats_validated": true,
      "issues": []
    },
    "twitter": {
      "assets_provided": ["asset-005"],
      "formats_validated": true,
      "issues": []
    },
    "meta_ads": {
      "assets_provided": ["asset-004"],
      "formats_validated": true,
      "issues": []
    }
  },

  "total_assets": 5,
  "generation_cost_estimate": 0.45
}
```

## Review Focus

Before approving creative_assets, the reviewer MUST verify:

1. **Visual matches copy** — Does the image reflect the variant's message?
2. **Format correct** — Are dimensions correct for each platform?
3. **Brand compliance** — Are colors, fonts, logo usage correct?
4. **CTA visible** — Can CTA be seen clearly in all formats?
5. **Mobile readability** — Is text large enough for mobile viewing?
6. **No text overflow** — Does text fit within safe zones?
7. **No misleading imagery** — Does visual accurately represent the offer?

## Success Criteria

- All copy variants have corresponding visuals
- Format specs validated per platform
- Brand guidelines applied consistently
- CTA clearly visible in all assets
- No broken links or low-resolution images
- Generation cost tracked

## Common Pitfalls

1. **Same image across platforms** — Not adapting for aspect ratios
2. **Text too small** — Mobile viewers can't read it
3. **Brand colors not applied** — Inconsistent with previous assets
4. **No CTA space** — Designed asset but no room for CTA overlay
5. **Stock photo look** — Using generic images instead of on-brand visuals
6. **Missing safety zone** — Platform UI covers important content