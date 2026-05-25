from __future__ import annotations

from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from app.domain.models import ExecutionGraph, PrimitiveNode, PrimitiveType, Workload


@workflow.defn
class WorkloadWorkflow:
    @workflow.run
    async def run(self, workload: Workload, policy_bundle_version: str) -> ExecutionGraph:
        graph = self._assemble_graph(workload, policy_bundle_version)
        for node in graph.nodes:
            await workflow.execute_activity(
                "execute_primitive",
                args=[node.model_dump(mode="json")],
                start_to_close_timeout=timedelta(seconds=node.timeout_seconds),
            )
        return graph

    def _assemble_graph(self, workload: Workload, policy_bundle_version: str) -> ExecutionGraph:
        nodes = [
            PrimitiveNode(
                node_id="policy",
                primitive_type=PrimitiveType.EVALUATE_POLICY,
                input={
                    "workload_id": str(workload.workload_id),
                    "policy_tags": workload.policy_tags,
                },
            ),
            PrimitiveNode(
                node_id="context",
                primitive_type=PrimitiveType.RETRIEVE_CONTEXT,
                depends_on_node_ids=["policy"],
                input={
                    "event_ids": [str(event_id) for event_id in workload.input_event_ids],
                    "entity_ids": [str(entity_id) for entity_id in workload.input_entity_ids],
                },
            ),
            PrimitiveNode(
                node_id="evidence",
                primitive_type=PrimitiveType.RANK_EVIDENCE,
                depends_on_node_ids=["context"],
            ),
            PrimitiveNode(
                node_id="verify",
                primitive_type=PrimitiveType.VERIFY_CLAIMS,
                depends_on_node_ids=["evidence"],
            ),
            PrimitiveNode(
                node_id="emit",
                primitive_type=PrimitiveType.EMIT_SEMANTIC_EVENT,
                depends_on_node_ids=["verify"],
            ),
        ]
        return ExecutionGraph(
            workload_id=workload.workload_id,
            tenant_id=workload.tenant_id,
            nodes=nodes,
            policy_bundle_version=policy_bundle_version,
        )
