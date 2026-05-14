import { NextRequest, NextResponse } from "next/server";

// Demo pipeline result — same as what Python api.py produces in demo mode
function runDemoPipeline(topic: string, platform: string) {
  const execution_id = `exec-${Math.random().toString(36).slice(2, 14)}`;
  const timestamp = new Date().toISOString();

  const variants = [
    {
      variant_id: `${execution_id}-var-1`,
      approach: "problem_led",
      hook: `Is your team still struggling with ${topic}?`,
      body: `Most teams fail at ${topic} because they approach it wrong. The secret isn't working harder — it's working smarter. Our approach has helped 500+ teams achieve results in 90 days. Get your free assessment and see where you stand.`,
      cta: "Get your free assessment →",
      platform,
      engagement_score: 8.2,
      char_count: 312,
    },
    {
      variant_id: `${execution_id}-var-2`,
      approach: "stat_led",
      hook: `73% of teams fail at ${topic}. Here's why.`,
      body: `We analyzed 1,000 teams attempting ${topic}. 73% failed not because of lack of effort, but wrong strategy. The 27% that succeeded shared 3 common traits. Download our free guide to see if your team has what it takes.`,
      cta: "Download the free guide",
      platform,
      engagement_score: 7.8,
      char_count: 298,
    },
    {
      variant_id: `${execution_id}-var-3`,
      approach: "outcome_led",
      hook: `What if your team could master ${topic} in 30 days?`,
      body: `With the right system, ${topic} becomes predictable. We helped one team go from struggling to succeeding in 30 days flat. Their secret? A proven framework, not just effort. See how we can help your team — book a free call.`,
      cta: "Book a free strategy call",
      platform,
      engagement_score: 7.5,
      char_count: 305,
    },
  ];

  return {
    execution_id,
    status: "completed",
    topic,
    platform,
    timestamp,
    artifacts: {
      copy_variants: { variants, total_variants: 3, platform, generation_method: "demo" },
      creative_assets: {
        assets: [{
          asset_id: `${execution_id}-img-1`,
          image_url: null,
          platform,
          status: "demo_placeholder",
          prompt: `Modern office team collaborating on ${topic}, professional photography style`,
          dimensions: { width: 1600, height: 900 },
        }],
        total_assets: 1,
        generation_method: "demo",
      },
      repurposed_content: {
        pieces: [
          {
            platform: "linkedin",
            type: "post",
            content: `${topic} doesn't have to be hard.\n\nWe analyzed 1,000 teams and found the top 27% shared 3 traits:\n\n✓ Clear success metrics\n✓ Systematic approach\n✓ Right tools\n\nMost teams fail because they lack one of these.\n\nWhich trait does your team need most?`,
          },
          {
            platform: "twitter",
            type: "thread",
            content: [
              `THREAD: How to succeed at ${topic}`,
              `1/ Most teams approach it wrong. They think more effort = better results.`,
              `2/ The top 27%? They work smarter, not harder. 3 specific traits.`,
              `3/ Trait #1: Clear success metrics. Know what done looks like before you start.`,
              `4/ More coming in this thread... [link to full guide]`,
            ],
          },
          {
            platform: "instagram",
            type: "caption",
            content: `Stop struggling with ${topic} 🛑\n\nThe problem isn't effort — it's approach.\n\nSave this for when you need it 👆\n\n#${topic.replace(/\s+/g, '')} #productivity #growth`,
          },
        ],
        total_pieces: 3,
        generation_method: "demo",
      },
      market_brief: {
        brief_id: `${execution_id}-mb`,
        topics_covered: [topic],
        audience_segments: [{ segment_id: "seg-demo", name: "Demo Segment" }],
      },
      content_brief: {
        brief_id: `${execution_id}-cb`,
        topic,
        platforms: ["twitter", "linkedin", "instagram"],
      },
    },
    stage_status: {
      research: "completed",
      strategy: "completed",
      brief: "completed",
      copy: "completed",
      creative: "completed",
      repurpose: "completed",
      publish: "simulated",
      analytics: "pending",
    },
    total_cost_estimate: 0.58,
    message: "Demo pipeline completed. Configure API keys for real content generation.",
  };
}

export async function POST(request: NextRequest) {
  try {
    const { topic, platform } = await request.json();

    if (!topic || typeof topic !== "string") {
      return NextResponse.json({ error: "topic is required" }, { status: 400 });
    }

    const result = runDemoPipeline(topic, platform || "twitter");
    return NextResponse.json(result);
  } catch (error) {
    console.error("Pipeline error:", error);
    return NextResponse.json({ error: "Pipeline execution failed" }, { status: 500 });
  }
}