import type { GraphLink, GraphNode, SemanticEvent, Workload } from "@/types";

export const graphNodes: GraphNode[] = [
  { id: "repo-api", label: "api-service", kind: "repository", confidence: 0.92 },
  { id: "svc-payments", label: "payments", kind: "service", confidence: 0.84 },
  { id: "deploy-prod", label: "prod rollout", kind: "deployment", confidence: 0.63 },
  { id: "policy-dual", label: "dual approval", kind: "policy", confidence: 0.96 },
  { id: "incident-421", label: "incident 421", kind: "incident", confidence: 0.71 },
  { id: "memory-release", label: "release memory", kind: "memory", confidence: 0.78 }
];

export const graphLinks: GraphLink[] = [
  { source: "repo-api", target: "svc-payments", predicate: "IMPLEMENTS" },
  { source: "deploy-prod", target: "svc-payments", predicate: "DEPLOYED_TO" },
  { source: "policy-dual", target: "deploy-prod", predicate: "GOVERNS" },
  { source: "incident-421", target: "deploy-prod", predicate: "AFFECTS" },
  { source: "memory-release", target: "svc-payments", predicate: "SUMMARIZES" }
];

export const semanticEvents: SemanticEvent[] = [
  {
    id: "evt-1004",
    topic: "pci.world.deploy",
    label: "production deployment drifted from graph claim",
    time: "07:42",
    severity: "critical"
  },
  {
    id: "evt-1003",
    topic: "pci.graph.claim",
    label: "ownership confidence recalculated",
    time: "07:40",
    severity: "warning"
  },
  {
    id: "evt-1002",
    topic: "pci.workload.workload",
    label: "deep reconciliation workload admitted",
    time: "07:38",
    severity: "normal"
  },
  {
    id: "evt-1001",
    topic: "pci.memory",
    label: "release episode promoted to memory",
    time: "07:32",
    severity: "normal"
  }
];

export const workloads: Workload[] = [
  {
    id: "wrk-rec-382",
    className: "reconciliation",
    state: "admitted",
    depth: "deep",
    score: 0.74,
    primitives: ["retrieve", "policy", "verify", "reconcile", "emit"]
  },
  {
    id: "wrk-mem-118",
    className: "compression",
    state: "waiting_review",
    depth: "standard",
    score: 0.58,
    primitives: ["retrieve", "rank", "compress", "verify", "emit"]
  }
];

