/**
 * @vitest-environment jsdom
 */

import { afterEach, describe, expect, it } from "vitest";
import { createRoot } from "react-dom/client";
import { act } from "react-dom/test-utils";

import { ContextGraph } from "../src/components/context-graph";

afterEach(() => {
  document.body.innerHTML = "";
});

describe("context graph", () => {
  it("renders the empty-state copy when there are no projected entities", () => {
    const container = document.createElement("div");
    document.body.appendChild(container);
    const root = createRoot(container);

    act(() => {
      root.render(<ContextGraph nodes={[]} links={[]} />);
    });

    expect(container.textContent).toContain("No projected entities yet.");

    root.unmount();
  });

  it("renders nodes and links for a populated graph", async () => {
    const container = document.createElement("div");
    document.body.appendChild(container);
    const root = createRoot(container);

    await act(async () => {
      root.render(
        <ContextGraph
          nodes={[
            { id: "node-1", label: "API Gateway", kind: "service", confidence: 0.9 },
            { id: "node-2", label: "Policy Guard", kind: "policy", confidence: 0.7 },
          ]}
          links={[{ source: "node-1", target: "node-2", predicate: "enforces" }]}
        />
      );
    });

    expect(container.querySelector("svg")).not.toBeNull();
    expect(container.querySelectorAll("circle")).toHaveLength(2);
    expect(container.querySelectorAll("line")).toHaveLength(1);
    expect(container.textContent).toContain("API Gateway");
    expect(container.textContent).toContain("Policy Guard");

    root.unmount();
  });
});
