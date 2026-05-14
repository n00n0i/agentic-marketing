import { NextRequest, NextResponse } from "next/server";
import { run_pipeline } from "../../../src/agentic_marketing/api";

export async function POST(request: NextRequest) {
  try {
    const { topic, platform } = await request.json();

    if (!topic || typeof topic !== "string") {
      return NextResponse.json(
        { error: "topic is required" },
        { status: 400 }
      );
    }

    const result = run_pipeline(topic, platform || "twitter");
    return NextResponse.json(result);
  } catch (error) {
    console.error("Pipeline error:", error);
    return NextResponse.json(
      { error: "Pipeline execution failed" },
      { status: 500 }
    );
  }
}