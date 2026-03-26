import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "F1bot",
  description: "Find and score Reddit lead opportunities with Gemini + FastAPI"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
