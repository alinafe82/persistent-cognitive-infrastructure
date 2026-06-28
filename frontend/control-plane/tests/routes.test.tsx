import { renderToStaticMarkup } from "react-dom/server";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";

process.env.NEXT_PUBLIC_SITE_URL = "https://pci-control-plane.example";
process.env.NEXT_PUBLIC_CONTACT_EMAIL = "ops@pci-control-plane.example";
process.env.PCI_CONTROL_PLANE_URL = "http://127.0.0.1:8080";

let site: typeof import("../src/lib/site");
let seo: typeof import("../src/lib/seo");
let controlPlane: typeof import("../src/lib/control-plane");
let layout: typeof import("../app/layout");
let home: typeof import("../app/page");
let contactPage: typeof import("../app/contact/page");
let privacyPage: typeof import("../app/privacy/page");
let disclosurePage: typeof import("../app/disclosure/page");
let sponsorPage: typeof import("../app/sponsor/page");
let termsPage: typeof import("../app/terms/page");
let robots: typeof import("../app/robots");
let sitemap: typeof import("../app/sitemap");

beforeAll(async () => {
  site = await import("../src/lib/site");
  seo = await import("../src/lib/seo");
  controlPlane = await import("../src/lib/control-plane");
  layout = await import("../app/layout");
  home = await import("../app/page");
  contactPage = await import("../app/contact/page");
  privacyPage = await import("../app/privacy/page");
  disclosurePage = await import("../app/disclosure/page");
  sponsorPage = await import("../app/sponsor/page");
  termsPage = await import("../app/terms/page");
  robots = await import("../app/robots");
  sitemap = await import("../app/sitemap");
});

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("site helpers", () => {
  it("builds canonical URLs and metadata from the configured site URL", () => {
    expect(site.SITE_URL).toBe("https://pci-control-plane.example");
    expect(site.CONTACT_EMAIL).toBe("ops@pci-control-plane.example");
    expect(site.siteUrl("/contact")).toBe("https://pci-control-plane.example/contact");

    const metadata = seo.pageMetadata({
      title: "Contact",
      description: "Contact PCI Control Plane",
      path: "/contact",
    });

    expect(metadata.alternates?.canonical).toBe("https://pci-control-plane.example/contact");
    expect(metadata.openGraph?.url).toBe("https://pci-control-plane.example/contact");
    expect(metadata.openGraph?.siteName).toBe("PCI Control Plane");
    expect(metadata.twitter?.title).toBe("Contact | PCI Control Plane");
  });

  it("returns robots and sitemap metadata for the public routes", () => {
    expect(robots.default()).toEqual({
      rules: {
        userAgent: "*",
        allow: "/",
        disallow: ["/api"],
      },
      sitemap: "https://pci-control-plane.example/sitemap.xml",
    });

    const entries = sitemap.default();
    expect(entries).toHaveLength(6);
    expect(entries.map((entry) => entry.url)).toEqual([
      "https://pci-control-plane.example/",
      "https://pci-control-plane.example/privacy",
      "https://pci-control-plane.example/terms",
      "https://pci-control-plane.example/disclosure",
      "https://pci-control-plane.example/sponsor",
      "https://pci-control-plane.example/contact",
    ]);
    expect(entries[0]?.priority).toBe(1);
    expect(entries[0]?.changeFrequency).toBe("weekly");
    expect(entries[1]?.lastModified).toBeInstanceOf(Date);
  });
});

describe("control plane loader", () => {
  it("normalizes successful responses and fills missing arrays", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        graphNodes: [
          { id: "node-1", label: "API Gateway", kind: "service", confidence: 0.82 },
        ],
        insights: [
          {
            id: "insight-1",
            severity: "warning",
            title: "Review pending",
            detail: "A review is pending.",
            action: "Schedule the review",
            confidence: 0.73,
            signalCount: 4,
          },
        ],
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const state = await controlPlane.loadControlPlaneState();

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8080/v1/control-plane/ui-state", {
      cache: "no-store",
    });
    expect(state.graphNodes).toHaveLength(1);
    expect(state.graphLinks).toEqual([]);
    expect(state.semanticEvents).toEqual([]);
    expect(state.workloads).toEqual([]);
    expect(state.insights).toHaveLength(1);
    expect(state.error).toBeUndefined();
  });

  it("reports non-OK responses as an error state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({}),
      })
    );

    const state = await controlPlane.loadControlPlaneState();

    expect(state.error).toBe("Control plane returned HTTP 503");
    expect(state.graphNodes).toEqual([]);
  });

  it("reports network failures with the trimmed base URL", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));

    const state = await controlPlane.loadControlPlaneState();

    expect(state.error).toBe("Control plane unavailable at http://127.0.0.1:8080: offline");
  });
});

describe("public routes", () => {
  it("renders the root layout with tracker and structured data", () => {
    const markup = renderToStaticMarkup(
      layout.default({
        children: <div>child</div>,
      })
    );

    expect(markup).toContain('lang="en"');
    expect(markup).toContain("visit-tracker.js");
    expect(markup).toContain('data-site="pci-control-plane"');
    expect(markup).toContain("SoftwareApplication");
    expect(markup).toContain("PCI Control Plane");
    expect(markup).toContain("<div>child</div>");
  });

  it("renders the dashboard with populated state", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          graphNodes: [
            { id: "service-1", label: "API Gateway", kind: "service", confidence: 0.94 },
            { id: "policy-1", label: "Policy Guard", kind: "policy", confidence: 0.88 },
          ],
          graphLinks: [
            { source: "service-1", target: "policy-1", predicate: "enforces" },
          ],
          semanticEvents: [
            {
              id: "event-1",
              topic: "ingest",
              label: "Ingest completed",
              time: "09:30",
              severity: "normal",
            },
          ],
          workloads: [
            {
              id: "job-1",
              className: "sync",
              state: "running",
              depth: "core",
              score: 0.91,
              primitives: ["fetch", "merge"],
            },
          ],
          insights: [
            {
              id: "insight-1",
              severity: "critical",
              title: "Schema drift",
              detail: "The graph schema changed.",
              action: "Run the reconciliation job",
              confidence: 0.84,
              signalCount: 7,
            },
          ],
        }),
      })
    );

    const markup = renderToStaticMarkup(await home.default());

    expect(markup).toContain("Persistent Cognitive Infrastructure");
    expect(markup).toContain("Control Plane");
    expect(markup).toContain("Decision Intelligence");
    expect(markup).toContain("Context Graph");
    expect(markup).toContain("Semantic Events");
    expect(markup).toContain("Execution Topology");
    expect(markup).toContain("Consulting surface");
    expect(markup).toContain("Sponsor");
    expect(markup).toContain("Contact");
    expect(markup).toContain("API Gateway");
    expect(markup).toContain("Policy Guard");
    expect(markup).toContain("Schema drift");
    expect(markup).toContain("91%");
  });

  it("renders the empty dashboard state when the backend has no data", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          graphNodes: [],
          graphLinks: [],
          semanticEvents: [],
          workloads: [],
          insights: [],
        }),
      })
    );

    const markup = renderToStaticMarkup(await home.default());

    expect(markup).toContain("No projected entities yet.");
    expect(markup).toContain("No confidence records yet.");
    expect(markup).toContain("No semantic events ingested yet.");
    expect(markup).toContain("No workloads admitted yet.");
    expect(markup).toContain("No runtime signals are available.");
  });

  it("renders an error banner when the backend responds with a failure", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({}),
      })
    );

    const markup = renderToStaticMarkup(await home.default());

    expect(markup).toContain("Control plane returned HTTP 503");
  });

  it.each([
    ["Contact", () => contactPage, "Contact PCI Control Plane", "ops@pci-control-plane.example"],
    [
      "Privacy",
      () => privacyPage,
      "Privacy notice",
      "The public website may count page visits through the Useful Web tracker.",
    ],
    ["Disclosure", () => disclosurePage, "Revenue disclosure", "Sponsored placements"],
    [
      "Sponsor",
      () => sponsorPage,
      "Sponsor codebase intelligence research.",
      "Developer-tooling affiliate partnership",
    ],
    ["Terms", () => termsPage, "Prototype terms", "Questions can be sent to"],
  ])("renders the %s page", (_name, getPage, expectedHeading, expectedBody) => {
    const { metadata, default: Page } = getPage();

    expect(metadata.alternates?.canonical).toMatch(/^https:\/\/pci-control-plane\.example\//);

    const markup = renderToStaticMarkup(Page());

    expect(markup).toContain(expectedHeading);
    expect(markup).toContain(expectedBody);
  });
});
