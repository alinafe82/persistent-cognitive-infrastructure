import { ConfidenceHeatmap } from "@/components/confidence-heatmap";
import { ContextGraph } from "@/components/context-graph";
import { EventTimeline } from "@/components/event-timeline";
import { WorkloadInspector } from "@/components/workload-inspector";
import { loadControlPlaneState } from "@/lib/control-plane";
import { DatabaseZap, Gauge, RadioTower, Shield } from "lucide-react";

export default async function Home() {
  const { graphLinks, graphNodes, semanticEvents, workloads, error } = await loadControlPlaneState();
  const averageConfidence = graphNodes.length
    ? Math.round((graphNodes.reduce((total, node) => total + node.confidence, 0) / graphNodes.length) * 100)
    : 0;
  const metrics = [
    { label: "events", value: String(semanticEvents.length), icon: RadioTower },
    { label: "entities", value: String(graphNodes.length), icon: DatabaseZap },
    { label: "avg confidence", value: `${averageConfidence}%`, icon: Gauge },
    { label: "workloads", value: String(workloads.length), icon: Shield }
  ];

  return (
    <main className="min-h-screen px-5 py-5 lg:px-8">
      <header className="mb-5 flex flex-col gap-4 border-b border-line pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-mono text-xs uppercase text-graphite">Persistent Cognitive Infrastructure</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink lg:text-3xl">Control Plane</h1>
        </div>
        <div className="grid grid-cols-2 gap-2 lg:grid-cols-4">
          {metrics.map((metric) => (
            <div key={metric.label} className="panel min-w-[132px] px-3 py-2">
              <div className="flex items-center justify-between gap-3">
                <span className="metric-label">{metric.label}</span>
                <metric.icon className="h-4 w-4 text-graphite" aria-hidden="true" />
              </div>
              <p className="mt-2 font-mono text-lg font-semibold text-ink">{metric.value}</p>
            </div>
          ))}
        </div>
      </header>

      {error ? (
        <div className="mb-5 rounded-md border border-danger/30 bg-white px-4 py-3 text-sm text-danger">{error}</div>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
        <ContextGraph nodes={graphNodes} links={graphLinks} />
        <div className="grid gap-5">
          <EventTimeline events={semanticEvents} />
          <ConfidenceHeatmap nodes={graphNodes} />
        </div>
      </div>

      <div className="mt-5">
        <WorkloadInspector workloads={workloads} />
      </div>
    </main>
  );
}
