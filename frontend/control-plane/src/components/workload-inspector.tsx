import { Activity, CheckCircle2 } from "lucide-react";
import type { Workload } from "@/types";

type Props = {
  workloads: Workload[];
};

export function WorkloadInspector({ workloads }: Props) {
  return (
    <section className="panel">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Execution Topology</h2>
        <Activity className="h-4 w-4 text-graphite" aria-hidden="true" />
      </div>
      <div className="divide-y divide-line">
        {workloads.length ? workloads.map((workload) => (
          <article key={workload.id} className="p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="font-mono text-sm font-semibold text-ink">{workload.id}</h3>
                <p className="mt-1 text-xs uppercase text-graphite">
                  {workload.className} / {workload.depth} / {workload.state}
                </p>
              </div>
              <div className="text-right">
                <p className="metric-label">score</p>
                <p className="font-mono text-sm font-semibold text-ink">{workload.score.toFixed(2)}</p>
              </div>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {workload.primitives.map((primitive) => (
                <span
                  key={primitive}
                  className="inline-flex h-7 items-center gap-1 rounded border border-line bg-field px-2 font-mono text-xs text-ink"
                >
                  <CheckCircle2 className="h-3 w-3 text-signal" aria-hidden="true" />
                  {primitive}
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
