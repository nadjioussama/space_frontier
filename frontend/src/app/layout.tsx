import "../styles/globals.css";
import type { Metadata, Viewport } from "next";
import { Nunito, Orbitron, JetBrains_Mono } from "next/font/google";
import { Providers } from "./providers";

const nunito = Nunito({
  subsets: ["latin"],
  variable: "--font-nunito",
  display: "swap",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  variable: "--font-orbitron",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

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
    <html lang="en" data-age="9-11" className={`${nunito.variable} ${orbitron.variable} ${jetbrainsMono.variable}`}>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
