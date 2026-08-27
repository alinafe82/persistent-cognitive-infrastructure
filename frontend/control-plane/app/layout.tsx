import "./globals.css";
import type { Metadata } from "next";
import Link from "next/link";
import {
  GOOGLE_ANALYTICS_ENABLED,
  GOOGLE_ANALYTICS_ID,
  GOOGLE_TAG_MANAGER_ENABLED,
  GOOGLE_TAG_MANAGER_ID,
  SITE_NAME,
  SITE_URL,
  VISIT_TRACKING_ENABLED,
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
        {GOOGLE_ANALYTICS_ENABLED ? (
          <>
            <script
              async
              src={`https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(
                GOOGLE_ANALYTICS_ID
              )}`}
            />
            <script
              dangerouslySetInnerHTML={{
                __html: `
                  window.dataLayer = window.dataLayer || [];
                  function gtag(){dataLayer.push(arguments);}
                  gtag("js", new Date());
                  gtag("config", ${JSON.stringify(GOOGLE_ANALYTICS_ID)});
                `,
              }}
            />
          </>
        ) : null}
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
        {VISIT_TRACKING_ENABLED ? (
          <script
            defer
            src="https://theusefulweb.app/visit-tracker.js"
            data-site="pci-control-plane"
          />
        ) : null}
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
        <a className="skip-link" href="#main-content">Skip to main content</a>
        {children}
        <footer className="mx-auto flex max-w-7xl flex-wrap gap-x-5 gap-y-2 px-5 py-8 text-sm text-graphite lg:px-8" aria-label="Site links">
          <Link href="/">Control plane</Link>
          <Link href="/privacy">Privacy</Link>
          <Link href="/terms">Terms</Link>
          <Link href="/disclosure">Disclosure</Link>
          <Link href="/sponsor">Sponsor</Link>
          <Link href="/contact">Contact</Link>
        </footer>
      </body>
    </html>
  );
}
