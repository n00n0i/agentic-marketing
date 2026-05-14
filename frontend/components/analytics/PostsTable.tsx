"use client";

import { useState } from "react";

interface Post {
  post_id: string;
  platform: string;
  content: string;
  impressions: number;
  clicks: number;
  engagement: number;
  engagement_rate: number;
  posted_at: string;
}

interface PostsTableProps {
  posts: Post[];
}

type SortKey = "impressions" | "clicks" | "engagement" | "engagement_rate";
type SortDir = "asc" | "desc";

export default function PostsTable({ posts }: PostsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("impressions");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir(sortDir === "asc" ? "desc" : "asc");
    } else {
      setSortKey(key);
      setSortDir("desc");
    }
  };

  const sortedPosts = [...posts].sort((a, b) => {
    const aVal = a[sortKey];
    const bVal = b[sortKey];
    return sortDir === "asc" ? aVal - bVal : bVal - aVal;
  });

  const SortIcon = ({ active, dir }: { active: boolean; dir: SortDir }) => (
    <span style={{ marginLeft: "0.25rem", opacity: active ? 1 : 0.3 }}>
      {dir === "asc" ? "↑" : "↓"}
    </span>
  );

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid #27272a" }}>
            <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500 }}>Platform</th>
            <th style={{ textAlign: "left", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500 }}>Content</th>
            <th
              style={{ textAlign: "right", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500, cursor: "pointer" }}
              onClick={() => handleSort("impressions")}
            >
              Impressions <SortIcon active={sortKey === "impressions"} dir={sortDir} />
            </th>
            <th
              style={{ textAlign: "right", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500, cursor: "pointer" }}
              onClick={() => handleSort("clicks")}
            >
              Clicks <SortIcon active={sortKey === "clicks"} dir={sortDir} />
            </th>
            <th
              style={{ textAlign: "right", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500, cursor: "pointer" }}
              onClick={() => handleSort("engagement")}
            >
              Engagement <SortIcon active={sortKey === "engagement"} dir={sortDir} />
            </th>
            <th
              style={{ textAlign: "right", padding: "0.75rem 1rem", color: "#71717a", fontSize: "0.75rem", fontWeight: 500, cursor: "pointer" }}
              onClick={() => handleSort("engagement_rate")}
            >
              Rate <SortIcon active={sortKey === "engagement_rate"} dir={sortDir} />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedPosts.map((post) => (
            <tr key={post.post_id} style={{ borderBottom: "1px solid #1f1f23" }}>
              <td style={{ padding: "0.75rem 1rem" }}>
                <span style={{
                  background: "#27272a",
                  color: "#a1a1aa",
                  padding: "0.125rem 0.5rem",
                  borderRadius: "4px",
                  fontSize: "0.75rem",
                  textTransform: "capitalize"
                }}>
                  {post.platform}
                </span>
              </td>
              <td style={{ padding: "0.75rem 1rem", color: "#a1a1aa", fontSize: "0.875rem", maxWidth: "300px", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                {post.content}
              </td>
              <td style={{ padding: "0.75rem 1rem", textAlign: "right", color: "#fafafa", fontSize: "0.875rem" }}>
                {post.impressions.toLocaleString()}
              </td>
              <td style={{ padding: "0.75rem 1rem", textAlign: "right", color: "#fafafa", fontSize: "0.875rem" }}>
                {post.clicks.toLocaleString()}
              </td>
              <td style={{ padding: "0.75rem 1rem", textAlign: "right", color: "#fafafa", fontSize: "0.875rem" }}>
                {post.engagement.toLocaleString()}
              </td>
              <td style={{ padding: "0.75rem 1rem", textAlign: "right", color: "#22c55e", fontSize: "0.875rem", fontWeight: 500 }}>
                {post.engagement_rate.toFixed(1)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}