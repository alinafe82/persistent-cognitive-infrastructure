import { ConfidenceHeatmap } from "@/components/confidence-heatmap";
import { ContextGraph } from "@/components/context-graph";
import { EventTimeline } from "@/components/event-timeline";
import { WorkloadInspector } from "@/components/workload-inspector";
import { graphLinks, graphNodes, semanticEvents, workloads } from "@/lib/demo-data";
import { DatabaseZap, Gauge, RadioTower, Shield } from "lucide-react";

const averageConfidence = Math.round(
  (graphNodes.reduce((total, node) => total + node.confidence, 0) / graphNodes.length) * 100
);

const metrics = [
  { label: "demo events", value: String(semanticEvents.length), icon: RadioTower },
  { label: "demo entities", value: String(graphNodes.length), icon: DatabaseZap },
  { label: "avg confidence", value: `${averageConfidence}%`, icon: Gauge },
  { label: "demo workloads", value: String(workloads.length), icon: Shield }
];

export default function Home() {
  return (
    <main className="min-h-screen px-5 py-5 lg:px-8">
      <header className="mb-5 flex flex-col gap-4 border-b border-line pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-mono text-xs uppercase text-graphite">Persistent Cognitive Infrastructure</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink lg:text-3xl">Control Plane Demo</h1>
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
