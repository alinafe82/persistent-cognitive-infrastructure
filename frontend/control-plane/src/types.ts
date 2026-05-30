export type GraphNode = {
  id: string;
  label: string;
  kind: string;
  confidence: number;
};

export type GraphLink = {
  source: string;
  target: string;
  predicate: string;
};

export type SemanticEvent = {
  id: string;
  topic: string;
  label: string;
  time: string;
  severity: "normal" | "warning" | "critical";
};

export type Workload = {
  id: string;
  className: string;
  state: string;
  depth: string;
  score: number;
  primitives: string[];
};

export type ControlPlaneState = {
  graphNodes: GraphNode[];
  graphLinks: GraphLink[];
  semanticEvents: SemanticEvent[];
  workloads: Workload[];
  error?: string;
};
