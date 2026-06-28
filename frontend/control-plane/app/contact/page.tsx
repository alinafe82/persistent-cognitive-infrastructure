import { CONTACT_EMAIL } from "@/lib/site";
import { pageMetadata } from "@/lib/seo";

export const metadata = pageMetadata({
  title: "Contact",
  description: "Contact PCI Control Plane for architecture reviews, sponsorship, privacy, and support questions.",
  path: "/contact",
});

export default function ContactPage() {
  return (
    <main className="min-h-[100dvh] px-5 py-8 lg:px-8">
      <article className="panel mx-auto max-w-3xl px-5 py-5">
        <p className="font-mono text-xs uppercase text-graphite">Contact</p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">Contact PCI Control Plane</h1>
        <p className="mt-3 text-sm leading-6 text-graphite">
          For architecture reviews, sponsorship, privacy questions, or deployment planning, email{" "}
          <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.
        </p>
        <p className="mt-4 text-sm leading-6 text-graphite">
          Do not send secrets, private repository contents, customer records, or production incident data through an
          unapproved channel.
        </p>
      </article>
    </main>
  );
}
