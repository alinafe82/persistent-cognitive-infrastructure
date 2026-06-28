import { beforeEach, describe, expect, it, vi } from "vitest";

describe("default configuration fallbacks", () => {
  beforeEach(() => {
    vi.resetModules();
    delete process.env.NEXT_PUBLIC_SITE_URL;
    delete process.env.NEXT_PUBLIC_CONTACT_EMAIL;
    delete process.env.NEXT_PUBLIC_MONETIZATION_MODE;
    delete process.env.PCI_CONTROL_PLANE_URL;
  });

  it("uses the repo-local defaults when environment variables are absent", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => ({}),
    });
    vi.stubGlobal("fetch", fetchMock);

    const site = await import("../src/lib/site");
    const controlPlane = await import("../src/lib/control-plane");

    expect(site.SITE_URL).toBe("https://pci-control-plane.local");
    expect(site.CONTACT_EMAIL).toBe("security@pci-control-plane.example");
    expect(site.MONETIZATION_MODE).toBe("leadgen");
    expect(site.siteUrl("/terms")).toBe("https://pci-control-plane.local/terms");

    await controlPlane.loadControlPlaneState();

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8080/v1/control-plane/ui-state", {
      cache: "no-store",
    });
  });
});
