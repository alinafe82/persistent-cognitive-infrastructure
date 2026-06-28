import { CONTACT_EMAIL } from "@/lib/site";
import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Privacy",
  description:
    "Privacy notice for the PCI Control Plane website, analytics, cookies, sponsorship, and contact data.",
  path: "/privacy",
});

export default function PrivacyPage() {
  return (
    <main className="min-h-[100dvh] px-5 py-8 lg:px-8">
      <article className="panel mx-auto max-w-3xl px-5 py-5">
        <p className="font-mono text-xs uppercase text-graphite">Privacy</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Privacy notice</h1>
        <p className="mt-3 text-sm leading-6 text-graphite">
          The public website may count page visits through the Useful Web tracker. It should not collect repository
          source, secrets, tenant data, workload payloads, or control-plane records.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Analytics</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Public page analytics may include page URL, path, referrer, and timestamp. Product telemetry for private
          control-plane deployments needs separate customer approval.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Ads and sponsors</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          The default monetization path is lead generation, architecture review, and sponsorship. Display ads are not
          enabled by default.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Contact</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Questions can be sent to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
        </p>
      </article>
    </main>
  );
}
