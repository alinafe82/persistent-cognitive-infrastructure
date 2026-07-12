import "./globals.css";
import type { Metadata } from "next";
import {
  GOOGLE_TAG_MANAGER_ENABLED,
  GOOGLE_TAG_MANAGER_ID,
  SITE_NAME,
  SITE_URL,
} from "@/lib/site";

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
        {GOOGLE_TAG_MANAGER_ENABLED ? (
          <script
            dangerouslySetInnerHTML={{
              __html: `
                (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
                new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
                j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
                'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
                })(window,document,'script','dataLayer',${JSON.stringify(GOOGLE_TAG_MANAGER_ID)});
              `,
            }}
          />
        ) : null}
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
      <body>
        {GOOGLE_TAG_MANAGER_ENABLED ? (
          <noscript>
            <iframe
              src={`https://www.googletagmanager.com/ns.html?id=${encodeURIComponent(
                GOOGLE_TAG_MANAGER_ID
              )}`}
              height="0"
              width="0"
              style={{ display: "none", visibility: "hidden" }}
              title="Google Tag Manager"
            />
          </noscript>
        ) : null}
        {children}
      </body>
    </html>
  );
}
