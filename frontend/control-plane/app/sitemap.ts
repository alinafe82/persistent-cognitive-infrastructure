import type { MetadataRoute } from "next";

import { siteUrl } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  const entries = [
    { path: "/", changeFrequency: "weekly" as const, priority: 1 },
    { path: "/privacy", changeFrequency: "yearly" as const, priority: 0.2 },
    { path: "/terms", changeFrequency: "yearly" as const, priority: 0.2 },
    { path: "/disclosure", changeFrequency: "yearly" as const, priority: 0.2 },
    { path: "/sponsor", changeFrequency: "monthly" as const, priority: 0.4 },
    { path: "/contact", changeFrequency: "monthly" as const, priority: 0.4 },
  ];

  return entries.map((entry) => ({
    url: siteUrl(entry.path),
    lastModified: now,
    changeFrequency: entry.changeFrequency,
    priority: entry.priority,
  }));
}
