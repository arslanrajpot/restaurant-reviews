import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReviewPulse",
  description: "Ask me about any restaurant and I’ll dish out what people are saying",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}