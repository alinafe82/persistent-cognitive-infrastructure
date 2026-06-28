import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Disclosure",
  description:
    "Affiliate, sponsorship, advertising, and editorial independence disclosures for PCI Control Plane.",
  path: "/disclosure",
});

export default function DisclosurePage() {
  return (
    <main className="min-h-[100dvh] px-5 py-8 lg:px-8">
      <article className="panel mx-auto max-w-3xl px-5 py-5">
        <p className="font-mono text-xs uppercase text-graphite">Disclosure</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Revenue disclosure</h1>
        <p className="mt-3 text-sm leading-6 text-graphite">
          PCI Control Plane may earn revenue from architecture reviews, implementation planning, sponsorships,
          affiliate links, and consulting inquiries. Recommendations should remain editorially independent.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Sponsored placements</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Sponsored placements may appear on sponsor pages, resource pages, newsletters, or research writeups. Paid
          placement should be labeled.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Affiliate links</h2>
        <p className="mt-2 text-sm leading-6 text-graphite">
          Affiliate links may generate commission when visitors click or buy through them.
        </p>
      </article>
    </main>
  );
}
