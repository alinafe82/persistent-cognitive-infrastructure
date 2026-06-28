import "./globals.css";
import type { Metadata } from "next";
import { SITE_NAME, SITE_URL } from "@/lib/site";

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: SITE_NAME,
    template: `%s | ${SITE_NAME}`,
  },
  description:
    "Persistent Cognitive Infrastructure control plane for context graphs, confidence scoring, workload scheduling, and source-of-truth reconciliation.",
  alternates: { canonical: "/" },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
      "max-video-preview": -1,
    },
  },
  openGraph: {
    title: SITE_NAME,
    description:
      "Control-plane UI for codebase intelligence, confidence scoring, and verification workloads.",
    url: SITE_URL,
    siteName: SITE_NAME,
    type: "website",
  },
  twitter: {
    card: "summary",
    title: SITE_NAME,
    description:
      "Control-plane UI for codebase intelligence, confidence scoring, and verification workloads.",
  },
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
      <head>
        <script
          defer
          src="https://theusefulweb.app/visit-tracker.js"
          data-site="pci-control-plane"
        />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "SoftwareApplication",
              name: SITE_NAME,
              applicationCategory: "DeveloperApplication",
              operatingSystem: "Web",
              url: SITE_URL,
              description:
                "Persistent Cognitive Infrastructure control plane for context graphs, confidence scoring, and verification workloads.",
            }),
          }}
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
