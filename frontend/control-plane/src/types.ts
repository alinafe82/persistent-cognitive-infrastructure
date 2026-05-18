export type GraphNode = {
  id: string;
  label: string;
  kind: "service" | "policy" | "incident" | "deployment" | "memory" | "repository";
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

