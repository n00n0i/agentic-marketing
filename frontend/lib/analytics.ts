export interface AnalyticsSummary {
  total_posts: number;
  total_impressions: number;
  avg_engagement: number;
  top_platform: string;
  period: string;
  trend: {
    posts_change: number;
    impressions_change: number;
    engagement_change: number;
  };
}

export interface PlatformMetrics {
  platform: string;
  posts: number;
  impressions: number;
  clicks: number;
  engagement_rate: number;
}

export interface CampaignMetrics {
  campaign_id: string;
  name: string;
  posts: number;
  impressions: number;
  engagement: number;
  cost: number;
  roi: number;
}

export interface PostMetrics {
  post_id: string;
  platform: string;
  content: string;
  impressions: number;
  clicks: number;
  engagement: number;
  engagement_rate: number;
  posted_at: string;
}

const API_BASE = "/api/analytics";

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const res = await fetch(`${API_BASE}/summary`);
  if (!res.ok) throw new Error("Failed to fetch analytics summary");
  return res.json();
}

export async function fetchPlatformBreakdown(): Promise<{ platforms: PlatformMetrics[] }> {
  const res = await fetch(`${API_BASE}/platforms`);
  if (!res.ok) throw new Error("Failed to fetch platform breakdown");
  return res.json();
}

export async function fetchCampaignPerformance(): Promise<{ campaigns: CampaignMetrics[] }> {
  const res = await fetch(`${API_BASE}/campaigns`);
  if (!res.ok) throw new Error("Failed to fetch campaign performance");
  return res.json();
}