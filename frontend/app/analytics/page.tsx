"use client";

import { useState } from "react";
import { MetricCard } from "@/components/analytics/MetricCard";
import { PlatformBarChart } from "@/components/analytics/PlatformBarChart";
import { PostsTable } from "@/components/analytics/PostsTable";
import { fetchAnalyticsSummary, fetchPlatformBreakdown, fetchCampaignPerformance } from "@/lib/analytics";

type DateRange = "7d" | "30d" | "90d";

export default function AnalyticsPage() {
  const [dateRange, setDateRange] = useState<DateRange>("30d");
  const [platformFilter, setPlatformFilter] = useState<string>("all");
  const [loading, setLoading] = useState(false);

  const summary = {
    total_posts: 147,
    total_impressions: 84200,
    avg_engagement: 4.7,
    top_platform: "LinkedIn",
  };

  const platforms = [
    { platform: "LinkedIn", posts: 52, impressions: 38400, clicks: 1820, engagement_rate: 5.8 },
    { platform: "Twitter/X", posts: 61, impressions: 29300, clicks: 1240, engagement_rate: 4.9 },
    { platform: "Facebook", posts: 22, impressions: 12100, clicks: 380, engagement_rate: 3.2 },
    { platform: "Instagram", posts: 12, impressions: 4400, clicks: 160, engagement_rate: 5.1 },
  ];

  const campaigns = [
    {
      campaign_id: "cmp_001",
      name: "AI Automation Q2",
      posts: 42,
      impressions: 52100,
      engagement: 4.9,
      cost: 420.00,
      roi: 312,
    },
    {
      campaign_id: "cmp_002",
      name: "SaaS Lead Gen",
      posts: 38,
      impressions: 28700,
      engagement: 4.1,
      cost: 310.00,
      roi: 198,
    },
    {
      campaign_id: "cmp_003",
      name: "Brand Awareness",
      posts: 67,
      impressions: 3400,
      engagement: 3.8,
      cost: 180.00,
      roi: 87,
    },
  ];

  const topPosts = [
    {
      id: "post_001",
      content: "The future of AI agents isn't about replacement — it's about amplification...",
      platform: "LinkedIn",
      impressions: 12400,
      engagement_rate: 7.2,
      clicks: 890,
    },
    {
      id: "post_002",
      content: "5 workflow automations that saved our team 20 hours this week...",
      platform: "Twitter/X",
      impressions: 8900,
      engagement_rate: 6.1,
      clicks: 543,
    },
    {
      id: "post_003",
      content: "We tested 12 AI tools for content creation. Here's what actually worked...",
      platform: "LinkedIn",
      impressions: 7200,
      engagement_rate: 5.8,
      clicks: 420,
    },
  ];

  const filteredPlatforms = platformFilter === "all"
    ? platforms
    : platforms.filter(p => p.platform.toLowerCase() === platformFilter);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Analytics</h1>
            <p className="text-gray-400 mt-1">Campaign performance across all platforms</p>
          </div>
          <div className="flex gap-3">
            <select
              value={platformFilter}
              onChange={e => setPlatformFilter(e.target.value)}
              className="bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              <option value="all">All Platforms</option>
              <option value="linkedin">LinkedIn</option>
              <option value="twitter">Twitter/X</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
            </select>
            <select
              value={dateRange}
              onChange={e => setDateRange(e.target.value as DateRange)}
              className="bg-gray-800 border border-gray-700 text-gray-200 rounded-lg px-3 py-2 text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="Total Posts"
            value={summary.total_posts.toLocaleString()}
            trend={+12}
            icon="📝"
          />
          <MetricCard
            label="Total Impressions"
            value={(summary.total_impressions / 1000).toFixed(1) + "K"}
            trend={+8}
            icon="👁️"
          />
          <MetricCard
            label="Avg Engagement"
            value={summary.avg_engagement + "%"}
            trend={+0.4}
            icon="📈"
          />
          <MetricCard
            label="Top Platform"
            value={summary.top_platform}
            trend={null}
            icon="🏆"
          />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h2 className="text-lg font-semibold text-white mb-4">Platform Breakdown</h2>
            <PlatformBarChart platforms={filteredPlatforms} />
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <h2 className="text-lg font-semibold text-white mb-4">Top Performing Posts</h2>
            <div className="space-y-3">
              {topPosts.map((post) => (
                <div
                  key={post.id}
                  className="flex items-start gap-3 p-3 bg-gray-800 rounded-lg"
                >
                  <span className="text-lg">{post.platform === "LinkedIn" ? "💼" : "🐦"}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-gray-300 text-sm line-clamp-2">{post.content}</p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-500">
                      <span>👁️ {post.impressions.toLocaleString()}</span>
                      <span>📈 {post.engagement_rate}%</span>
                      <span>🖱️ {post.clicks}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Campaign Performance Table */}
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Campaign Performance</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-gray-800">
                  <th className="text-left py-3 px-4 font-medium">Campaign</th>
                  <th className="text-right py-3 px-4 font-medium">Posts</th>
                  <th className="text-right py-3 px-4 font-medium">Impressions</th>
                  <th className="text-right py-3 px-4 font-medium">Engagement</th>
                  <th className="text-right py-3 px-4 font-medium">Cost</th>
                  <th className="text-right py-3 px-4 font-medium">Est. ROI</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((cmp) => (
                  <tr
                    key={cmp.campaign_id}
                    className="text-gray-300 border-b border-gray-800/50 hover:bg-gray-800/50"
                  >
                    <td className="py-3 px-4 font-medium text-white">{cmp.name}</td>
                    <td className="py-3 px-4 text-right">{cmp.posts}</td>
                    <td className="py-3 px-4 text-right">{(cmp.impressions / 1000).toFixed(1)}K</td>
                    <td className="py-3 px-4 text-right">{cmp.engagement}%</td>
                    <td className="py-3 px-4 text-right">${cmp.cost.toFixed(2)}</td>
                    <td className={`py-3 px-4 text-right font-medium ${cmp.roi > 200 ? "text-green-400" : "text-gray-400"}`}>
                      {cmp.roi}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}