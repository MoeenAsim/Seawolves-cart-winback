import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Seawolves Cart Win-Back",
  description:
    "AI-assisted cart win-back review for Seattle Seawolves marketers",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}