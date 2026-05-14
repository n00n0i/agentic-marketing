"use client";

import { useState } from "react";

interface CopyVariant {
  variant_id: string;
  approach: string;
  hook: string;
  body: string;
  cta: string;
  platform: string;
  engagement_score: number;
  char_count: number;
}

interface CopyVariantsResult {
  variants: CopyVariant[];
  total_variants: number;
  platform: string;
  generation_method: string;
}

interface PipelineResult {
  execution_id: string;
  status: string;
  topic: string;
  platform: string;
  timestamp: string;
  artifacts: {
    copy_variants: CopyVariantsResult;
    creative_assets: {
      assets: { asset_id: string; status: string; platform: string }[];
    };
    repurposed_content: {
      pieces: { platform: string; type: string; content: string | string[] }[];
    };
  };
  stage_status: Record<string, string>;
  total_cost_estimate: number;
  message?: string;
}

export default function MarketingDashboard() {
  const [topic, setTopic] = useState("");
  const [platform, setPlatform] = useState("twitter");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      // In production, this would call the FastAPI backend
      // For now, we'll use a demo mode via fetch
      const response = await fetch("/api/pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic, platform }),
      });

      if (!response.ok) {
        throw new Error("Pipeline failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      // Fallback to demo mode if API is not available
      const demoResult = await runDemoPipeline(topic, platform);
      setResult(demoResult);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0a0f", color: "#e4e4e7", fontFamily: "system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid #27272a", padding: "1.5rem 2rem" }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 600, margin: 0, color: "#fff" }}>
          Agentic Marketing Pipeline
        </h1>
        <p style={{ margin: "0.25rem 0 0", color: "#71717a", fontSize: "0.875rem" }}>
          AI-powered content generation → publishing → analytics
        </p>
      </header>

      <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem" }}>
        {/* Input Form */}
        <section style={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "12px", padding: "1.5rem", marginBottom: "2rem" }}>
          <h2 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 1rem", color: "#fff" }}>
            Start New Campaign
          </h2>
          <form onSubmit={handleSubmit} style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "flex-end" }}>
            <div style={{ flex: "2", minWidth: "280px" }}>
              <label style={{ display: "block", fontSize: "0.875rem", color: "#a1a1aa", marginBottom: "0.5rem" }}>
                Campaign Topic
              </label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., AI Automation for SaaS Teams"
                style={{
                  width: "100%",
                  padding: "0.625rem 0.875rem",
                  background: "#09090b",
                  border: "1px solid #3f3f46",
                  borderRadius: "8px",
                  color: "#fafafa",
                  fontSize: "0.875rem",
                  outline: "none",
                }}
              />
            </div>
            <div style={{ flex: "1", minWidth: "140px" }}>
              <label style={{ display: "block", fontSize: "0.875rem", color: "#a1a1aa", marginBottom: "0.5rem" }}>
                Primary Platform
              </label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                style={{
                  width: "100%",
                  padding: "0.625rem 0.875rem",
                  background: "#09090b",
                  border: "1px solid #3f3f46",
                  borderRadius: "8px",
                  color: "#fafafa",
                  fontSize: "0.875rem",
                  outline: "none",
                }}
              >
                <option value="twitter">Twitter/X</option>
                <option value="linkedin">LinkedIn</option>
                <option value="instagram">Instagram</option>
                <option value="email">Email</option>
              </select>
            </div>
            <button
              type="submit"
              disabled={isLoading || !topic.trim()}
              style={{
                padding: "0.625rem 1.5rem",
                background: isLoading ? "#3f3f46" : "#2563eb",
                border: "none",
                borderRadius: "8px",
                color: "#fff",
                fontSize: "0.875rem",
                fontWeight: 500,
                cursor: isLoading ? "not-allowed" : "pointer",
                transition: "background 0.15s",
              }}
            >
              {isLoading ? "Generating..." : "Run Pipeline"}
            </button>
          </form>
        </section>

        {/* Error State */}
        {error && (
          <div style={{ background: "#7f1d1d", border: "1px solid #b91c1c", borderRadius: "8px", padding: "1rem", marginBottom: "2rem", color: "#fecaca" }}>
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div style={{ textAlign: "center", padding: "4rem 2rem", color: "#71717a" }}>
            <div style={{ fontSize: "2rem", marginBottom: "1rem" }}>⏳</div>
            <p>Running marketing pipeline...</p>
            <p style={{ fontSize: "0.875rem" }}>Research → Copy → Creative → Repurpose → Publish</p>
          </div>
        )}

        {/* Results */}
        {result && !isLoading && (
          <div style={{ display: "grid", gap: "1.5rem" }}>
            {/* Pipeline Status */}
            <section style={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "12px", padding: "1.5rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
                <h2 style={{ fontSize: "1.125rem", fontWeight: 600, margin: 0, color: "#fff" }}>
                  Pipeline Status
                </h2>
                <span style={{ background: "#166534", color: "#bbf7d0", padding: "0.25rem 0.75rem", borderRadius: "9999px", fontSize: "0.75rem", fontWeight: 500 }}>
                  {result.status}
                </span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                {Object.entries(result.stage_status).map(([stage, status]) => (
                  <div
                    key={stage}
                    style={{
                      padding: "0.375rem 0.75rem",
                      background: status === "completed" ? "#166534" : status === "pending" ? "#854d0e" : "#1e1e1e",
                      borderRadius: "6px",
                      fontSize: "0.75rem",
                      color: status === "completed" ? "#bbf7d0" : "#fef08a",
                      textTransform: "capitalize",
                    }}
                  >
                    {stage}: {status}
                  </div>
                ))}
              </div>
              <p style={{ margin: "1rem 0 0", fontSize: "0.75rem", color: "#71717a" }}>
                Execution ID: {result.execution_id} · Cost: ${result.total_cost_estimate.toFixed(2)}
              </p>
            </section>

            {/* Copy Variants */}
            <section style={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "12px", padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 1rem", color: "#fff" }}>
                Copy Variants — {result.artifacts.copy_variants.total_variants} Generated
              </h2>
              <div style={{ display: "grid", gap: "1rem" }}>
                {result.artifacts.copy_variants.variants.map((variant, idx) => (
                  <div
                    key={variant.variant_id}
                    style={{ background: "#09090b", border: "1px solid #27272a", borderRadius: "8px", padding: "1rem" }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.75rem" }}>
                      <span style={{ background: "#1e3a5f", color: "#93c5fd", padding: "0.125rem 0.5rem", borderRadius: "4px", fontSize: "0.75rem", textTransform: "capitalize" }}>
                        {variant.approach.replace("_", " ")}
                      </span>
                      <span style={{ color: "#71717a", fontSize: "0.75rem" }}>
                        Score: {variant.engagement_score}/10 · {variant.char_count} chars
                      </span>
                    </div>
                    <p style={{ margin: "0 0 0.75rem", fontWeight: 600, color: "#fafafa", fontSize: "0.9375rem" }}>
                      {variant.hook}
                    </p>
                    <p style={{ margin: "0 0 0.75rem", color: "#a1a1aa", fontSize: "0.875rem", lineHeight: 1.5 }}>
                      {variant.body}
                    </p>
                    <p style={{ margin: 0, color: "#60a5fa", fontSize: "0.875rem", fontWeight: 500 }}>
                      {variant.cta}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Repurposed Content */}
            <section style={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "12px", padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 1rem", color: "#fff" }}>
                Repurposed Content — {result.artifacts.repurposed_content.pieces.length} Pieces
              </h2>
              <div style={{ display: "grid", gap: "0.75rem" }}>
                {result.artifacts.repurposed_content.pieces.map((piece, idx) => (
                  <div
                    key={idx}
                    style={{ background: "#09090b", border: "1px solid #27272a", borderRadius: "8px", padding: "1rem" }}
                  >
                    <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
                      <span style={{ background: "#1e1e1e", color: "#a1a1aa", padding: "0.125rem 0.5rem", borderRadius: "4px", fontSize: "0.75rem", textTransform: "capitalize" }}>
                        {piece.platform}
                      </span>
                      <span style={{ color: "#52525b", fontSize: "0.75rem" }}>{piece.type}</span>
                    </div>
                    <p style={{ margin: 0, color: "#a1a1aa", fontSize: "0.875rem", lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                      {Array.isArray(piece.content) ? piece.content.join("\n") : piece.content}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Creative Assets */}
            <section style={{ background: "#18181b", border: "1px solid #27272a", borderRadius: "12px", padding: "1.5rem" }}>
              <h2 style={{ fontSize: "1.125rem", fontWeight: 600, margin: "0 0 1rem", color: "#fff" }}>
                Creative Assets
              </h2>
              <p style={{ margin: 0, color: "#71717a", fontSize: "0.875rem" }}>
                {result.artifacts.creative_assets.assets.length} asset(s) generated
              </p>
              {result.artifacts.creative_assets.assets.map((asset) => (
                <div key={asset.asset_id} style={{ marginTop: "0.75rem", padding: "1rem", background: "#09090b", border: "1px solid #27272a", borderRadius: "8px" }}>
                  <span style={{ color: "#f59e0b", fontSize: "0.875rem" }}>🖼️</span>{" "}
                  <span style={{ color: "#a1a1aa", fontSize: "0.875rem" }}>
                    {asset.status === "demo_placeholder" ? "Demo placeholder (FLUX image generation in production)" : asset.status}
                  </span>
                </div>
              ))}
            </section>

            {/* Message */}
            {result.message && (
              <div style={{ background: "#1e1e1e", border: "1px solid #3f3f46", borderRadius: "8px", padding: "1rem", color: "#a1a1aa", fontSize: "0.875rem" }}>
                💡 {result.message}
              </div>
            )}
          </div>
        )}

        {/* Empty State */}
        {!result && !isLoading && !error && (
          <div style={{ textAlign: "center", padding: "4rem 2rem", color: "#52525b" }}>
            <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📊</div>
            <p style={{ fontSize: "1.125rem", color: "#71717a", margin: "0 0 0.5rem" }}>No campaign yet</p>
            <p style={{ fontSize: "0.875rem", margin: 0 }}>Enter a topic above to generate content</p>
          </div>
        )}
      </main>
    </div>
  );
}

// Demo mode function — runs when API is not available
async function runDemoPipeline(topic: string, platform: string): Promise<PipelineResult> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1500));

  const execution_id = `exec-${Math.random().toString(36).substring(2, 14)}`;
  const timestamp = new Date().toISOString();

  const variants: CopyVariant[] = [
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
        assets: [
          {
            asset_id: `${execution_id}-img-1`,
            status: "demo_placeholder",
            platform,
          },
        ],
      },
      repurposed_content: {
        pieces: [
          {
            platform: "linkedin",
            type: "post",
            content: `${topic} doesn't have to be hard.\n\nWe analyzed 1,000 teams and found the top 27% shared 3 traits:\n\n✓ Clear success metrics\n✓ Systematic approach\n✓ Right tools\n\nMost teams fail because they lack one of these.\n\nWhat trait does your team need most?`,
          },
          {
            platform: "twitter",
            type: "thread",
            content: [
              `THREAD: How to succeed at ${topic}`,
              "1/ Most teams approach it wrong. They think more effort = better results.",
              "2/ The top 27%? They work smarter, not harder. 3 specific traits.",
              "3/ Trait #1: Clear success metrics. Know what done looks like before you start.",
              "4/ More coming in this thread... [link to full guide]",
            ],
          },
          {
            platform: "instagram",
            type: "caption",
            content: `Stop struggling with ${topic} 🛑\n\nThe problem isn't effort — it's approach.\n\nSave this for when you need it 👆\n\n#${topic.replace(/\s+/g, "")} #productivity #growth`,
          },
        ],
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
    message: "Demo mode: In production, this would generate real copy via Claude, real images via FLUX on Modal.",
  };
}