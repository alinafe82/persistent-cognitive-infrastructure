import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "PCI Control Plane",
  description: "Persistent Cognitive Infrastructure control plane",
  icons: {
    icon: "/icon.svg",
  },
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
