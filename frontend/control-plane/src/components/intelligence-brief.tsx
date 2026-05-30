import { AlertTriangle, CheckCircle2, Route, ShieldAlert, type LucideIcon } from "lucide-react";
import type { DecisionInsight } from "@/types";

type Props = {
  insights: DecisionInsight[];
};

const severityStyles: Record<
  DecisionInsight["severity"],
  {
    accent: string;
    border: string;
    icon: LucideIcon;
    label: string;
  }
> = {
  critical: {
    accent: "text-danger",
    border: "border-danger/40",
    icon: ShieldAlert,
    label: "requires review",
  },
  warning: {
    accent: "text-warning",
    border: "border-warning/40",
    icon: AlertTriangle,
    label: "watch",
  },
  normal: {
    accent: "text-signal",
    border: "border-signal/40",
    icon: CheckCircle2,
    label: "clear",
  },
};

function formatConfidence(value: number): string {
  return `${Math.round(Math.max(0, Math.min(1, value)) * 100)}%`;
}

export function IntelligenceBrief({ insights }: Props) {
  const primary = insights[0];
  const rest = insights.slice(1);

  return (
    <section className="panel overflow-hidden">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <div>
          <h2 className="text-sm font-semibold text-ink">Decision Intelligence</h2>
          <p className="mt-0.5 font-mono text-xs text-graphite">{insights.length} findings</p>
        </div>
        <Route className="h-4 w-4 text-graphite" aria-hidden="true" />
      </div>

      {primary ? (
        <div className="p-4">
          <article className={`rounded-md border bg-white p-4 ${severityStyles[primary.severity].border}`}>
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <div className="flex items-center gap-2">
                  {(() => {
                    const Icon = severityStyles[primary.severity].icon;
                    return <Icon className={`h-4 w-4 ${severityStyles[primary.severity].accent}`} aria-hidden="true" />;
                  })()}
                  <span className="metric-label">{severityStyles[primary.severity].label}</span>
                </div>
                <h3 className="mt-3 text-base font-semibold leading-6 text-ink">{primary.title}</h3>
                <p className="mt-2 text-sm leading-6 text-graphite">{primary.detail}</p>
              </div>
              <div className="shrink-0 text-right">
                <p className="metric-label">confidence</p>
                <p className="mt-1 font-mono text-lg font-semibold tabular-nums text-ink">
                  {formatConfidence(primary.confidence)}
                </p>
              </div>
            </div>
            <div className="mt-4 border-t border-line pt-3">
              <p className="metric-label">next action</p>
              <p className="mt-1 text-sm font-medium leading-5 text-ink">{primary.action}</p>
            </div>
          </article>

          {rest.length ? (
            <div className="mt-3 divide-y divide-line rounded-md border border-line bg-white">
              {rest.map((insight) => {
                const Icon = severityStyles[insight.severity].icon;
                return (
                  <article key={insight.id} className="grid grid-cols-[20px_1fr_auto] gap-3 px-3 py-3">
                    <Icon className={`mt-0.5 h-4 w-4 ${severityStyles[insight.severity].accent}`} aria-hidden="true" />
                    <div>
                      <h3 className="text-sm font-semibold leading-5 text-ink">{insight.title}</h3>
                      <p className="mt-1 text-xs leading-5 text-graphite">{insight.detail}</p>
                    </div>
                    <span className="font-mono text-xs tabular-nums text-graphite">
                      {insight.signalCount}
                    </span>
                  </article>
                );
              })}
            </div>
          ) : null}
        </div>
      ) : (
        <div className="px-4 py-6 text-sm text-graphite">No runtime signals are available.</div>
      )}
    </section>
  );
}
