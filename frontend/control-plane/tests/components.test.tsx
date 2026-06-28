import { renderToStaticMarkup } from "react-dom/server";
import { beforeAll, describe, expect, it } from "vitest";

let intelligenceBrief: typeof import("../src/components/intelligence-brief");
let confidenceHeatmap: typeof import("../src/components/confidence-heatmap");
let eventTimeline: typeof import("../src/components/event-timeline");
let workloadInspector: typeof import("../src/components/workload-inspector");

beforeAll(async () => {
  intelligenceBrief = await import("../src/components/intelligence-brief");
  confidenceHeatmap = await import("../src/components/confidence-heatmap");
  eventTimeline = await import("../src/components/event-timeline");
  workloadInspector = await import("../src/components/workload-inspector");
});

describe("dashboard components", () => {
  it("renders confidence bands across the heatmap", () => {
    const markup = renderToStaticMarkup(
      <confidenceHeatmap.ConfidenceHeatmap
        nodes={[
          { id: "signal", label: "Signal", kind: "service", confidence: 0.95 },
          { id: "blue", label: "Blue", kind: "policy", confidence: 0.8 },
          { id: "warning", label: "Warning", kind: "incident", confidence: 0.6 },
          { id: "danger", label: "Danger", kind: "repository", confidence: 0.2 },
        ]}
      />
    );

    expect(markup).toContain("Signal");
    expect(markup).toContain("Blue");
    expect(markup).toContain("Warning");
    expect(markup).toContain("Danger");
    expect(markup).toContain("bg-signal");
    expect(markup).toContain("bg-blue-600");
    expect(markup).toContain("bg-warning");
    expect(markup).toContain("bg-danger");
  });

  it("renders all intelligence brief severities and follow-on findings", () => {
    const markup = renderToStaticMarkup(
      <intelligenceBrief.IntelligenceBrief
        insights={[
          {
            id: "critical",
            severity: "critical",
            title: "Critical signal",
            detail: "Critical detail",
            action: "Escalate immediately",
            confidence: 0.91,
            signalCount: 9,
          },
          {
            id: "warning",
            severity: "warning",
            title: "Warning signal",
            detail: "Warning detail",
            action: "Review before release",
            confidence: 0.64,
            signalCount: 4,
          },
          {
            id: "normal",
            severity: "normal",
            title: "Normal signal",
            detail: "Normal detail",
            action: "Continue monitoring",
            confidence: 0.82,
            signalCount: 1,
          },
        ]}
      />
    );

    expect(markup).toContain("requires review");
    expect(markup).toContain("Critical signal");
    expect(markup).toContain("Warning signal");
    expect(markup).toContain("Normal signal");
    expect(markup).toContain("Escalate immediately");
    expect(markup).toContain("9");
    expect(markup).toContain("4");
    expect(markup).toContain("1");
  });

  it("renders event severity and workload state details", () => {
    const timelineMarkup = renderToStaticMarkup(
      <eventTimeline.EventTimeline
        events={[
          {
            id: "event-normal",
            topic: "ingest",
            label: "Ingest completed",
            time: "09:15",
            severity: "normal",
          },
          {
            id: "event-critical",
            topic: "runtime",
            label: "Runtime failure",
            time: "09:30",
            severity: "critical",
          },
        ]}
      />
    );
    const workloadMarkup = renderToStaticMarkup(
      <workloadInspector.WorkloadInspector
        workloads={[
          {
            id: "job-1",
            className: "sync",
            state: "running",
            depth: "core",
            score: 0.91,
            primitives: ["fetch", "merge"],
          },
        ]}
      />
    );

    expect(timelineMarkup).toContain("Ingest completed");
    expect(timelineMarkup).toContain("Runtime failure");
    expect(timelineMarkup).toContain("text-signal");
    expect(timelineMarkup).toContain("text-danger");
    expect(workloadMarkup).toContain("job-1");
    expect(workloadMarkup).toContain("sync / core / running");
    expect(workloadMarkup).toContain("0.91");
    expect(workloadMarkup).toContain("fetch");
    expect(workloadMarkup).toContain("merge");
  });
});
