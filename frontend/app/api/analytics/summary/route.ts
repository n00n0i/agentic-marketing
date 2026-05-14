import { NextResponse } from "next/server";

// Mock data for analytics summary
const MOCK_SUMMARY = {
  total_posts: 847,
  total_impressions: 284500,
  avg_engagement: 4.2,
  top_platform: "linkedin",
  period: "last_30_days",
  trend: {
    posts_change: 12.5,
    impressions_change: 8.3,
    engagement_change: -2.1,
  },
};

export async function GET() {
  try {
    // In production: query PostgreSQL for real aggregated data
    // For now, return mock data with a small delay to simulate API
    await new Promise((resolve) => setTimeout(resolve, 100));
    return NextResponse.json(MOCK_SUMMARY);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch analytics summary" }, { status: 500 });
  }
}