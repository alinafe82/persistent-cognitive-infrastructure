import type { ControlPlaneState } from "@/types";

const EMPTY_STATE: ControlPlaneState = {
  graphNodes: [],
  graphLinks: [],
  semanticEvents: [],
  workloads: []
};

function controlPlaneUrl(): string {
  return (process.env.PCI_CONTROL_PLANE_URL || "http://127.0.0.1:8080").replace(/\/+$/, "");
}

export async function loadControlPlaneState(): Promise<ControlPlaneState> {
  const baseUrl = controlPlaneUrl();
  try {
    const response = await fetch(`${baseUrl}/v1/control-plane/ui-state`, {
      cache: "no-store"
    });
    if (!response.ok) {
      return {
        ...EMPTY_STATE,
        error: `Control plane returned HTTP ${response.status}`
      };
    }

    const payload = (await response.json()) as Partial<ControlPlaneState>;
    return {
      graphNodes: payload.graphNodes ?? [],
      graphLinks: payload.graphLinks ?? [],
      semanticEvents: payload.semanticEvents ?? [],
      workloads: payload.workloads ?? []
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return {
      ...EMPTY_STATE,
      error: `Control plane unavailable at ${baseUrl}: ${message}`
    };
  }
}
