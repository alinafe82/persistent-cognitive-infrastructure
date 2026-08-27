/**
 * @vitest-environment jsdom
 */

import { act } from "react";
import { createRoot } from "react-dom/client";
import { afterEach, describe, expect, it } from "vitest";

import { RefreshControl } from "../src/components/refresh-control";

afterEach(() => {
  document.body.innerHTML = "";
});

describe("refresh control", () => {
  it("submits a no-JavaScript refresh and announces the pending state", async () => {
    const container = document.createElement("div");
    document.body.appendChild(container);
    const root = createRoot(container);

    await act(async () => {
      root.render(<RefreshControl />);
    });

    const button = container.querySelector("button");
    const form = container.querySelector("form");
    expect(button?.textContent).toContain("Refresh state");
    expect(form?.getAttribute("method")).toBe("get");
    expect(form?.getAttribute("action")).toBe("/");

    await act(async () => {
      form?.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
    });

    expect(button?.getAttribute("aria-busy")).toBe("true");
    expect(container.querySelector("[role='status']")?.textContent).toContain(
      "Requesting latest state…"
    );

    root.unmount();
  });
});
