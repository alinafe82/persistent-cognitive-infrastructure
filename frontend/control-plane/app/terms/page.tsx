import { CONTACT_EMAIL } from "@/lib/site";
import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Terms",
  description: "Terms for the PCI Control Plane website and prototype UI.",
  path: "/terms",
});

export default function TermsPage() {
  return (
    <main className="min-h-[100dvh] px-5 py-8 lg:px-8">
      <article className="panel mx-auto max-w-3xl px-5 py-5">
        <p className="font-mono text-xs uppercase text-graphite">Terms</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Prototype terms</h1>
        <p className="mt-3 text-sm leading-6 text-graphite">
          PCI Control Plane is a prototype interface for codebase intelligence, confidence scoring, and verification
          workload planning. It is not a hosted production service unless a separate agreement says so.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">No operational guarantee</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Dashboard metrics depend on the configured control-plane API. Empty, stale, or unavailable data should be
          treated as a signal to verify the backend, not as a production assurance.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Contact</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Questions can be sent to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
        </p>
      </article>
    </main>
  );
}
