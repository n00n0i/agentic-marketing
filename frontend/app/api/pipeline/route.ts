import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function POST(req: NextRequest) {
  try {
    const { topic, platform } = await req.json();

    const response = await fetch(`${API_BASE}/api/v1/pipeline/run`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": process.env.API_KEY || "dev-key",
      },
      body: JSON.stringify({ topic, platform }),
      // timeout: 10 minutes for full pipeline (6 stages, each ~60-90s)
      signal: AbortSignal.timeout(600_000),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json({ error }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("Pipeline API error:", error);

    // If backend unreachable, return clear error
    if (error?.cause?.code === "ECONNREFUSED" || error?.message?.includes("fetch")) {
      return NextResponse.json(
        {
          error: "Backend unavailable",
          message: "Make sure the backend server is running on port 8000",
          hint: "Run: cd ~/agentic-marketing && uvicorn agentic_marketing.server:app --reload",
        },
        { status: 503 }
      );
    }

    return NextResponse.json(
      { error: "Internal server error", detail: error?.message },
      { status: 500 }
    );
  }
}