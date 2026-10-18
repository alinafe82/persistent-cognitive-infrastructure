import { Activity, CheckCircle2 } from "lucide-react";
import type { Workload } from "@/types";

type Props = {
  workloads: Workload[];
};

function humanize(value: string): string {
  return value.replaceAll("_", " ");
}

export function WorkloadInspector({ workloads }: Props) {
  return (
    <section className="panel">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Execution Topology</h2>
        <Activity className="h-4 w-4 text-graphite" aria-hidden="true" />
      </div>
      <div className="divide-y divide-line">
        {workloads.length ? workloads.map((workload) => (
          <article key={workload.id} className="state-entry p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 break-words">
                <h3 className="font-mono text-sm font-semibold text-ink">{workload.id}</h3>
                <p className="mt-1 text-xs uppercase text-graphite">
                  {humanize(workload.className)} / {humanize(workload.depth)} / {humanize(workload.state)}
                </p>
              </div>
              <div className="shrink-0 text-right">
                <p className="metric-label">score</p>
                <p className="font-mono text-sm font-semibold text-ink">{workload.score.toFixed(2)}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {workload.primitives.map((primitive) => (
                <span
                  key={primitive}
                  className="inline-flex min-h-7 max-w-full break-words items-center gap-1 rounded border border-line bg-field px-2 font-mono text-xs text-ink"
                >
                  <CheckCircle2 className="h-3 w-3 shrink-0 text-signal" aria-hidden="true" />
                  <span className="min-w-0 break-words">{humanize(primitive)}</span>
                </span>
              ))}
            </div>
          </article>
        )) : (
          <div className="px-4 py-6 text-sm text-graphite">No workloads admitted yet.</div>
        )}
      </div>
    </section>
  );
}
