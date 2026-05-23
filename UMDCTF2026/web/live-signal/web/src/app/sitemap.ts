import type { MetadataRoute } from "next";

const BASE_URL = process.env.NEXT_PUBLIC_SITE_URL ?? "https://livesignal.example";

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${BASE_URL}/`, changeFrequency: "daily", priority: 1 },
    { url: `${BASE_URL}/analysts`, changeFrequency: "daily", priority: 0.8 },
    { url: `${BASE_URL}/insiders`, changeFrequency: "monthly", priority: 0.5 },
    { url: `${BASE_URL}/llms.txt`, changeFrequency: "monthly", priority: 0.3 },
  ];
}
