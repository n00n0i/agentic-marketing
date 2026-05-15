import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/analytics/campaigns?workspace_id=default`, {
      headers: {
        "X-API-Key": process.env.API_KEY || "dev-key",
      },
      signal: AbortSignal.timeout(10_000),
    });

    if (!response.ok) {
      return NextResponse.json({ error: "Failed to fetch campaigns" }, { status: response.status });
    }

    return NextResponse.json(await response.json());
  } catch (error: any) {
    if (error?.cause?.code === "ECONNREFUSED") {
      return NextResponse.json({ error: "Backend unavailable" }, { status: 503 });
    }
    return NextResponse.json({ error: "Internal server error" }, { status: 500 });
  }
}