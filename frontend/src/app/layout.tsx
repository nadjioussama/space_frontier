import "../styles/globals.css";
import type { Metadata, Viewport } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "NASA Space Explorer",
  description: "Learn real space science through play — for ages 6-14.",
  keywords: ["NASA", "space", "education", "kids", "science", "game"],
};

export const viewport: Viewport = {
  themeColor: "#0B0D17",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" data-age="9-11">
      <head>
        {/* PLAN §17: Orbitron (display), Nunito (body), JetBrains Mono (data).
            Production will self-host; dev uses Google Fonts CDN. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&family=Orbitron:wght@500;700&family=JetBrains+Mono:wght@400;500&display=swap"
        />
      </head>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
