import { CONTACT_EMAIL } from "@/lib/site";
import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Sponsor",
  description:
    "Sponsor PCI Control Plane research and reach developer-tooling, AI infrastructure, and codebase intelligence audiences.",
  path: "/sponsor",
});

export default function SponsorPage() {
  return (
    <main className="min-h-[100dvh] px-5 py-8 lg:px-8">
      <article className="panel mx-auto max-w-3xl px-5 py-5">
        <p className="font-mono text-xs uppercase text-graphite">Sponsor</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Sponsor codebase intelligence research.</h1>
        <p className="mt-3 text-sm leading-6 text-graphite">
          The audience is developer-tooling teams, AI infrastructure builders, platform engineers, and organizations
          evaluating durable context graphs or source-of-truth reconciliation.
        </p>
        <h2 className="mt-6 text-lg font-semibold text-ink">Available placements</h2>
        <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-6 text-graphite">
          <li>Sponsored research note</li>
          <li>Newsletter sponsorship</li>
          <li>Resource page sponsorship</li>
          <li>Developer-tooling affiliate partnership</li>
          <li>Display placement if explicitly enabled later</li>
        </ul>
        <p className="mt-6 text-sm leading-6 text-graphite">
          Contact <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a> with the audience fit and placement type.
        </p>
      </article>
    </main>
  );
}
