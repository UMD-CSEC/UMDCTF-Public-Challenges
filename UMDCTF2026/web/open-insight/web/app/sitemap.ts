import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://openinsight.example";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${BASE_URL}/`, changeFrequency: "daily", priority: 1 },
    { url: `${BASE_URL}/login`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/signup`, changeFrequency: "yearly", priority: 0.3 },
    { url: `${BASE_URL}/sheets/new`, changeFrequency: "monthly", priority: 0.6 },
    { url: `${BASE_URL}/llms.txt`, changeFrequency: "monthly", priority: 0.3 },
  ];
}
