import { AlertTriangle, GitBranch, ShieldCheck } from "lucide-react";
import type { SemanticEvent } from "@/types";

type Props = {
  events: SemanticEvent[];
};

const severityStyles: Record<SemanticEvent["severity"], string> = {
  normal: "text-signal",
  warning: "text-warning",
  critical: "text-danger"
};

export function EventTimeline({ events }: Props) {
  return (
    <section className="panel">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Semantic Events</h2>
        <GitBranch className="h-4 w-4 text-graphite" aria-hidden="true" />
      </div>
      <div className="divide-y divide-line">
        {events.length ? events.map((event) => (
          <div key={event.id} className="grid grid-cols-[52px_1fr_24px] items-center gap-3 px-4 py-3">
            <span className="font-mono text-xs text-graphite">{event.time}</span>
            <div>
              <p className="text-sm font-medium leading-5 text-ink">{event.label}</p>
              <p className="font-mono text-xs text-graphite">{event.topic}</p>
            </div>
            {event.severity === "critical" ? (
              <AlertTriangle className={`h-4 w-4 ${severityStyles[event.severity]}`} aria-hidden="true" />
            ) : (
              <ShieldCheck className={`h-4 w-4 ${severityStyles[event.severity]}`} aria-hidden="true" />
            )}
          </div>
        )) : (
          <div className="px-4 py-6 text-sm text-graphite">No semantic events ingested yet.</div>
        )}
      </div>
    </section>
  );
}
