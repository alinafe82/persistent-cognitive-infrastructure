import type { GraphNode } from "@/types";

type Props = {
  nodes: GraphNode[];
};

function confidenceColor(score: number): string {
  if (score >= 0.9) return "bg-signal";
  if (score >= 0.75) return "bg-blue-600";
  if (score >= 0.55) return "bg-warning";
  return "bg-danger";
}

export function ConfidenceHeatmap({ nodes }: Props) {
  return (
    <section className="panel">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Confidence</h2>
        <span className="font-mono text-xs text-graphite">
          {Math.round((nodes.reduce((total, node) => total + node.confidence, 0) / nodes.length) * 100)}%
        </span>
      </div>
      <div className="grid grid-cols-2 gap-2 p-4">
        {nodes.map((node) => (
          <div key={node.id} className="min-h-[72px] rounded-md border border-line bg-white p-3">
            <div className="flex items-center justify-between gap-3">
              <span className="truncate text-sm font-semibold text-ink">{node.label}</span>
              <span className="font-mono text-xs text-graphite">{Math.round(node.confidence * 100)}%</span>
            </div>
            <div className="mt-3 h-2 rounded-full bg-field">
              <div
                className={`h-2 rounded-full ${confidenceColor(node.confidence)}`}
                style={{ width: `${node.confidence * 100}%` }}
              />
            </div>
            <p className="mt-2 font-mono text-[11px] text-graphite">{node.kind}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

