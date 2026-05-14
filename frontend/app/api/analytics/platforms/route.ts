import { NextResponse } from "next/server";

// Mock platform breakdown data
const MOCK_PLATFORMS = [
  { platform: "linkedin", posts: 312, impressions: 124500, clicks: 8340, engagement_rate: 5.8 },
  { platform: "twitter", posts: 285, impressions: 89200, clicks: 5120, engagement_rate: 4.2 },
  { platform: "instagram", posts: 156, impressions: 48100, clicks: 2980, engagement_rate: 3.9 },
  { platform: "facebook", posts: 94, impressions: 22700, clicks: 1450, engagement_rate: 3.1 },
];

export async function GET() {
  try {
    // In production: aggregate from social_analytics table grouped by platform
    await new Promise((resolve) => setTimeout(resolve, 100));
    return NextResponse.json({ platforms: MOCK_PLATFORMS });
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch platform analytics" }, { status: 500 });
  }
}