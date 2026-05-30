"use client";

import { useEffect, useMemo, useRef } from "react";
import * as d3 from "d3";
import type { GraphLink, GraphNode } from "@/types";

type Props = {
  nodes: GraphNode[];
  links: GraphLink[];
};

type SimNode = GraphNode & d3.SimulationNodeDatum;
type SimLink = d3.SimulationLinkDatum<SimNode> & {
  predicate: string;
};

const nodeColors: Record<string, string> = {
  service: "#0F766E",
  policy: "#5B4DB7",
  incident: "#B91C1C",
  deployment: "#B45309",
  memory: "#2563EB",
  repository: "#3F4148"
};
const fallbackNodeColor = "#3F4148";

export function ContextGraph({ nodes, links }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const simulationNodes = useMemo<SimNode[]>(() => nodes.map((node) => ({ ...node })), [nodes]);
  const simulationLinks = useMemo<SimLink[]>(
    () => links.map((link) => ({ ...link }) as SimLink),
    [links]
  );

  useEffect(() => {
    if (!svgRef.current || !simulationNodes.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 720;
    const height = 420;
    const linkForce = d3
      .forceLink<SimNode, SimLink>(simulationLinks)
      .id((node) => node.id)
      .distance(118);

    const simulation = d3
      .forceSimulation<SimNode>(simulationNodes)
      .force("link", linkForce)
      .force("charge", d3.forceManyBody().strength(-360))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(42));

    const link = svg
      .append("g")
      .attr("stroke", "#A8ABA2")
      .attr("stroke-width", 1)
      .selectAll<SVGLineElement, SimLink>("line")
      .data(simulationLinks)
      .join("line");

    const node = svg
      .append("g")
      .selectAll<SVGGElement, SimNode>("g")
      .data(simulationNodes)
      .join("g")
      .call(
        d3
          .drag<SVGGElement, SimNode>()
          .on("start", (event, datum) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            datum.fx = datum.x;
            datum.fy = datum.y;
          })
          .on("drag", (event, datum) => {
            datum.fx = event.x;
            datum.fy = event.y;
          })
          .on("end", (event, datum) => {
            if (!event.active) simulation.alphaTarget(0);
            datum.fx = null;
            datum.fy = null;
          })
      );

    node
      .append("circle")
      .attr("r", (datum) => 16 + datum.confidence * 10)
      .attr("fill", (datum) => nodeColors[datum.kind] ?? fallbackNodeColor)
      .attr("fill-opacity", 0.88);

    node
      .append("text")
      .text((datum) => datum.label)
      .attr("x", 0)
      .attr("y", 38)
      .attr("text-anchor", "middle")
      .attr("font-size", 11)
      .attr("fill", "#171717");

    simulation.on("tick", () => {
      link
        .attr("x1", (datum) => (datum.source as GraphNode & d3.SimulationNodeDatum).x ?? 0)
        .attr("y1", (datum) => (datum.source as GraphNode & d3.SimulationNodeDatum).y ?? 0)
        .attr("x2", (datum) => (datum.target as GraphNode & d3.SimulationNodeDatum).x ?? 0)
        .attr("y2", (datum) => (datum.target as GraphNode & d3.SimulationNodeDatum).y ?? 0);

      node.attr("transform", (datum) => `translate(${datum.x ?? 0},${datum.y ?? 0})`);
    });

    return () => {
      simulation.stop();
    };
  }, [simulationLinks, simulationNodes]);

  return (
    <div className="panel h-full min-h-[420px] overflow-hidden">
      <div className="flex h-12 items-center justify-between border-b border-line px-4">
        <h2 className="text-sm font-semibold text-ink">Context Graph</h2>
        <span className="font-mono text-xs text-graphite">{nodes.length} entities</span>
      </div>
      {nodes.length ? (
        <svg
          ref={svgRef}
          viewBox="0 0 720 420"
          className="h-[420px] w-full"
          role="img"
          aria-label="Projected context graph"
        />
      ) : (
        <div className="flex h-[420px] items-center justify-center px-4 text-center text-sm text-graphite">
          No projected entities yet.
        </div>
      )}
    </div>
  );
}
