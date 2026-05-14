import { NextResponse } from "next/server";

// Mock campaign performance data
const MOCK_CAMPAIGNS = [
  {
    campaign_id: "camp-001",
    name: "Product Launch Q1",
    posts: 45,
    impressions: 67400,
    engagement: 2890,
    cost: 320.0,
    roi: 3.2,
  },
  {
    campaign_id: "camp-002",
    name: "Brand Awareness",
    posts: 78,
    impressions: 98300,
    engagement: 4120,
    cost: 580.0,
    roi: 2.8,
  },
  {
    campaign_id: "camp-003",
    name: "Lead Gen Campaign",
    posts: 32,
    impressions: 42100,
    engagement: 1980,
    cost: 245.0,
    roi: 4.1,
  },
  {
    campaign_id: "camp-004",
    name: "Holiday Promo",
    posts: 24,
    impressions: 38700,
    engagement: 1650,
    cost: 180.0,
    roi: 3.8,
  },
  {
    campaign_id: "camp-005",
    name: "Thought Leadership",
    posts: 56,
    impressions: 38200,
    engagement: 2240,
    cost: 410.0,
    roi: 2.4,
  },
];

export async function GET() {
  try {
    // In production: query campaigns table with aggregated metrics
    await new Promise((resolve) => setTimeout(resolve, 100));
    return NextResponse.json({ campaigns: MOCK_CAMPAIGNS });
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch campaign analytics" }, { status: 500 });
  }
}