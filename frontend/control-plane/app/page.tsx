import { ConfidenceHeatmap } from "@/components/confidence-heatmap";
import { ContextGraph } from "@/components/context-graph";
import { EventTimeline } from "@/components/event-timeline";
import { IntelligenceBrief } from "@/components/intelligence-brief";
import { RefreshControl } from "@/components/refresh-control";
import { WorkloadInspector } from "@/components/workload-inspector";
import { loadControlPlaneState } from "@/lib/control-plane";
import { DatabaseZap, Gauge, RadioTower, Shield } from "lucide-react";

function clampConfidence(score: number): number {
  return Math.max(0, Math.min(1, score));
}

export default async function Home() {
  const { graphLinks, graphNodes, semanticEvents, workloads, insights, error } =
    await loadControlPlaneState();
  const averageConfidence = graphNodes.length
    ? Math.round(
        (graphNodes.reduce((total, node) => total + clampConfidence(node.confidence), 0) /
          graphNodes.length) *
          100
      )
    : 0;
  const attentionCount = insights.filter((insight) => insight.severity !== "normal").length;
  const hasRuntimeData = graphNodes.length > 0 || semanticEvents.length > 0 || workloads.length > 0;
  const metrics = [
    { label: "events", value: String(semanticEvents.length), icon: RadioTower },
    { label: "entities", value: String(graphNodes.length), icon: DatabaseZap },
    { label: "avg confidence", value: `${averageConfidence}%`, icon: Gauge },
    { label: "attention", value: String(attentionCount), icon: Shield },
  ];

  return (
    <main id="main-content" className="min-h-[100dvh] px-5 py-5 lg:px-8">
      <header className="mb-5 flex flex-col gap-4 border-b border-line pb-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="font-mono text-xs uppercase text-graphite">Persistent Cognitive Infrastructure</p>
          <h1 className="mt-1 text-2xl font-semibold text-ink lg:text-3xl">Control Plane</h1>
        </div>
        <div className="flex flex-col items-end gap-2 lg:flex-row lg:items-start">
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
          <RefreshControl />
        </div>
      </header>

      {error ? (
        <div className="state-entry mb-5 rounded-md border border-danger/30 bg-white px-4 py-3 text-sm text-danger" role="alert">
          <p className="font-medium">The dashboard could not reach the control plane.</p>
          <p className="mt-1 text-graphite">
            Start the API on port 8080, then choose Refresh state. Technical detail: {error}
          </p>
        </div>
      ) : null}

      {!error && !hasRuntimeData ? (
        <section className="state-entry panel mb-5 px-4 py-4" aria-labelledby="waiting-for-events">
          <h2 id="waiting-for-events" className="text-sm font-semibold text-ink">Waiting for semantic events</h2>
          <p className="mt-1 text-sm leading-6 text-graphite">
            Load the included sample from the repository root, then choose Refresh state:
          </p>
          <code className="mt-2 block w-fit rounded bg-field px-2 py-1 font-mono text-xs text-ink">
            scripts/load-demo.sh
          </code>
        </section>
      ) : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.65fr)]">
        <div className="order-2 xl:order-1">
          <ContextGraph nodes={graphNodes} links={graphLinks} />
        </div>
        <div className="order-1 grid gap-5 xl:order-2">
          <IntelligenceBrief insights={insights} />
          <EventTimeline events={semanticEvents} />
        </div>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[minmax(360px,0.42fr)_minmax(0,0.58fr)]">
        <ConfidenceHeatmap nodes={graphNodes} />
        <WorkloadInspector workloads={workloads} />
      </div>

      <section className="panel mt-5 grid gap-4 px-5 py-4 lg:grid-cols-[1fr_auto] lg:items-center">
        <div>
          <p className="font-mono text-xs uppercase text-graphite">Consulting surface</p>
          <h2 className="mt-1 text-xl font-semibold text-ink">
            Need this pattern reviewed for your platform?
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-graphite">
            The practical revenue path is lead generation for architecture reviews, implementation planning, and
            sponsored developer-tooling research. Display ads are not part of the control-plane UI by default.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a className="rounded-md border border-line px-3 py-2 text-sm font-medium text-ink" href="/contact">
            Contact
          </a>
          <a className="rounded-md bg-signal px-3 py-2 text-sm font-medium text-white" href="/sponsor">
            Sponsor
          </a>
        </div>
      </section>
    </main>
  );
}
