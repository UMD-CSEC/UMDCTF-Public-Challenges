import "./globals.css";
import type { Metadata } from "next";
import { Nav } from "@/components/Nav";
import { getSessionUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "OpenInsight — shared models for forecasters",
  description:
    "Collaborative spreadsheets for prediction-market analysts. Live data, shared models, a research desk in the browser.",
};

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const user = await getSessionUser();
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..800,30..100&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen antialiased">
        <Nav user={user} />
        <main>{children}</main>
        <footer className="mx-auto mt-24 max-w-6xl border-t border-[color:var(--color-rule)] px-6 py-10">
          <div className="flex flex-wrap items-baseline justify-between gap-6 text-[11px] text-[color:var(--color-paper-faint)]">
            <span className="eyebrow">OpenInsight · Research Desk · 2026</span>
            <span className="eyebrow">
              Shared models are provided as-is · No trading advice
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}
