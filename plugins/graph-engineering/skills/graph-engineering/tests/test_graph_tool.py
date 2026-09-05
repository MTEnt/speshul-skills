from __future__ import annotations

import copy
import io
import importlib.util
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_SPEC = importlib.util.spec_from_file_location("graph_tool", ROOT / "scripts" / "graph_tool.py")
assert MODULE_SPEC and MODULE_SPEC.loader
graph_tool = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(graph_tool)


def base_spec() -> dict:
    return json.loads((ROOT / "templates" / "graph-spec.json").read_text(encoding="utf-8"))


def deterministic_node(node_id: str, inputs: list[dict] | None = None, outputs: list[dict] | None = None) -> dict:
    return {
        "id": node_id,
        "execution_kind": "deterministic",
        "semantic_role": node_id,
        "ports": {"inputs": inputs or [], "outputs": outputs or []},
        "context_policy_ref": "minimal-context",
        "state_reads": [],
        "state_writes": [],
        "permissions": [],
        "timeout_ms": 1000,
        "retry_policy": {"max_attempts": 1, "on_exhausted": "failed"},
        "side_effect_class": "none",
        "outcomes": ["success", "failed"],
        "acceptance_conditions": ["Contract passes."],
    }


def complete_graph_contract(spec: dict) -> dict:
    node_defaults = {
        "prompt_ref": None,
        "model_ref": None,
        "tool_ref": None,
        "capability_ref": None,
        "output_schema_ref": None,
        "idempotency_ref": None,
        "approval_binding_ref": None,
        "postcondition_ref": None,
        "long_running": False,
    }
    edge_defaults = {"condition": None, "routed_outcome": None, "join_behavior": None, "iteration_guard": None, "default": False}
    for node in spec["nodes"]:
        for key, value in node_defaults.items():
            node.setdefault(key, value)
    for edge in spec["edges"]:
        for key, value in edge_defaults.items():
            edge.setdefault(key, value)
    for channel in spec["state"]["channels"]:
        channel.setdefault("owner", None)
        channel.setdefault("reducer", None)
    for binding in spec["controls"]["approval_bindings"]:
        binding["scope"].setdefault("environment", None)
        binding["scope"].setdefault("payload_ref", None)
    evolution_budgets = spec["evolution"]["budgets"]
    evolution_budgets.setdefault("max_trials_per_case", 0)
    evolution_budgets.setdefault("max_cost_usd", 0)
    spec["evolution"]["promotion_criteria"].setdefault("mandatory_safety", "pass")
    return spec


def control_edge(edge_id: str, source: str, target: str, **extra: object) -> dict:
    edge = {"id": edge_id, "source": source, "source_port": "$control", "target": target, "target_port": "$control", "semantic": "control"}
    edge.update(extra)
    return edge


def reset_topology(spec: dict, nodes: list[dict], edges: list[dict], entries: list[str], terminals: list[str]) -> dict:
    spec["nodes"] = nodes
    spec["edges"] = edges
    spec["graph"]["entry_points"] = entries
    spec["graph"]["terminals"] = terminals
    spec["state"]["channels"] = []
    return complete_graph_contract(spec)


def build_positive(case_id: str) -> dict:
    spec = base_spec()
    spec["graph"]["id"] = case_id
    if case_id == "direct-chain":
        return complete_graph_contract(spec)
    if case_id == "conditional-router":
        route, left, right, finish = (deterministic_node(name) for name in ("route", "left", "right", "finish"))
        edges = [
            control_edge("route-left", "route", "left", condition={"eq": ["state.route", "left"]}),
            control_edge("route-right", "route", "right", default=True),
            control_edge("left-finish", "left", "finish"),
            control_edge("right-finish", "right", "finish"),
        ]
        return reset_topology(spec, [route, left, right, finish], edges, ["route"], ["finish"])
    if case_id == "parallel-reducer-join":
        item = {"name": "item", "type": "ItemV1", "required": True}
        split = deterministic_node("split", outputs=[item])
        left = deterministic_node("left", inputs=[item], outputs=[item])
        right = deterministic_node("right", inputs=[item], outputs=[item])
        join = deterministic_node("join", inputs=[item])
        left["state_writes"] = ["results"]
        right["state_writes"] = ["results"]
        spec["state"]["channels"] = [{"id": "results", "type": "ItemListV1", "source_of_truth": "run-state", "allowed_writers": ["left", "right"], "reducer": "append-ordered-by-node-id", "concurrent_write": "reduce", "sensitivity": "internal", "visibility": ["left", "right", "join"], "persistence": "checkpointed", "checkpoint_policy": "after-join", "provenance": "required"}]
        spec["nodes"] = [split, left, right, join]
        spec["edges"] = [
            {"id": "split-left", "source": "split", "source_port": "item", "target": "left", "target_port": "item", "semantic": "data"},
            {"id": "split-right", "source": "split", "source_port": "item", "target": "right", "target_port": "item", "semantic": "data"},
            {"id": "left-join", "source": "left", "source_port": "item", "target": "join", "target_port": "item", "semantic": "data", "join_behavior": "all"},
            {"id": "right-join", "source": "right", "source_port": "item", "target": "join", "target_port": "item", "semantic": "data", "join_behavior": "all"},
        ]
        spec["graph"]["entry_points"] = ["split"]
        spec["graph"]["terminals"] = ["join"]
        spec["runtime"]["scheduler"] = "parallel-superstep"
        spec["runtime"]["max_concurrency"] = 2
        spec["runtime"]["fan_out"] = "split-to-left-right"
        spec["runtime"]["fan_in"] = "all-at-join"
        return complete_graph_contract(spec)
    if case_id == "bounded-evaluator-repair":
        draft, evaluate, repair, finish = (deterministic_node(name) for name in ("draft", "evaluate", "repair", "finish"))
        guard = {"max_iterations": 3, "exit_condition": "accepted-or-exhausted"}
        edges = [
            control_edge("draft-evaluate", "draft", "evaluate"),
            control_edge("evaluate-repair", "evaluate", "repair", condition={"eq": ["state.accepted", False]}),
            control_edge("repair-evaluate", "repair", "evaluate", iteration_guard=guard),
            control_edge("evaluate-finish", "evaluate", "finish", default=True),
        ]
        return reset_topology(spec, [draft, evaluate, repair, finish], edges, ["draft"], ["finish"])
    if case_id == "planner-executor":
        spec["nodes"][0]["semantic_role"] = "planner"
        spec["nodes"][1]["semantic_role"] = "bounded executor"
        return complete_graph_contract(spec)
    if case_id == "runtime-work-queue":
        spec["graph"]["topology_binding"] = "runtime-expanded"
        spec["runtime"]["dynamic_expansion"] = {"max_nodes": 20, "max_edges": 40, "max_depth": 2, "max_queue": 20, "max_concurrency": 4}
        return complete_graph_contract(spec)
    if case_id == "subgraph-composition":
        spec["nodes"][0]["execution_kind"] = "subgraph"
        spec["nodes"][0].pop("prompt_ref")
        spec["nodes"][0].pop("model_ref")
        spec["nodes"][0].pop("output_schema_ref")
        spec["nodes"][0]["capability_ref"] = "subgraphs/producer@1.0.0"
        return complete_graph_contract(spec)
    if case_id == "agent-handoff":
        spec["nodes"][0]["execution_kind"] = "agent"
        spec["nodes"][0]["semantic_role"] = "handoff sender"
        spec["edges"][0]["semantic"] = "control"
        spec["edges"][0]["source_port"] = "$control"
        spec["edges"][0]["target_port"] = "$control"
        return complete_graph_contract(spec)
    if case_id == "human-interrupt-resume":
        spec["nodes"][1]["execution_kind"] = "human"
        spec["runtime"]["interrupts"] = [{"id": "review", "checkpoint": "before-interrupt", "resume_node": "finish", "resume_validation": "identity-and-input-schema", "expiry": "PT24H", "cancel_route": "cancelled"}]
        spec["edges"][0]["semantic"] = "interrupt"
        return complete_graph_contract(spec)
    if case_id == "protected-external-action":
        node = spec["nodes"][0]
        node["execution_kind"] = "tool"
        node.pop("prompt_ref")
        node.pop("model_ref")
        node.pop("output_schema_ref")
        node["side_effect_class"] = "protected_action"
        node["approval_binding_ref"] = "deploy-approval"
        node["postcondition_ref"] = "deploy-state"
        node["idempotency_ref"] = "deploy-key"
        node["permissions"] = ["deploy:service-a"]
        spec["graph"]["assurance_profile"] = "protected_action"
        spec["controls"]["approval_bindings"] = [{"id": "deploy-approval", "action_digest": "sha256:00", "scope": {"operation": "deploy", "target": "service-a"}, "approver_identity": "release-manager", "expires_at": "2030-01-01T00:00:00Z", "nonce": "n-1", "revoked": False}]
        spec["controls"]["idempotency_policies"] = [{"id": "deploy-key", "scope": "service-a deployment", "key_source": "approved action digest", "reconciliation": "query control-plane deployment by key"}]
        spec["controls"]["postconditions"] = [{"id": "deploy-state", "authoritative_source": "control-plane", "expected": "digest active"}]
        spec["controls"]["compensations"] = [{"id": "deploy-rollback", "action_ref": "produce", "requires_new_approval": True, "outcome_verification_ref": "deploy-state"}]
        return complete_graph_contract(spec)
    if case_id == "high-assurance-evidence":
        spec["graph"]["assurance_profile"] = "high_assurance"
        spec["observability"]["immutable_evidence"] = True
        spec["observability"]["integrity_hashes"] = True
        return complete_graph_contract(spec)
    if case_id == "prompt-only-optimization":
        spec["evolution"]["mutable_surfaces"] = ["prompt:produce-prompt", "model:produce"]
        spec["evaluation"]["held_out"] = "data/held-out.jsonl"
        return complete_graph_contract(spec)
    if case_id == "topology-evolution":
        spec["evolution"].update({"status": "candidate", "candidate_version": "1.1.0-candidate.1", "held_out_evaluation_ref": "evals/held-out.json", "budgets": {"max_candidates": 4}, "promotion_criteria": {"success_delta": 0.05}, "rollback": "restore 1.0.0"})
        return complete_graph_contract(spec)
    raise AssertionError(f"unknown positive case {case_id}")


def mutate_negative(case_id: str) -> dict:
    spec = base_spec()
    if case_id == "duplicate-node":
        spec["nodes"].append(copy.deepcopy(spec["nodes"][0]))
    elif case_id == "missing-entry":
        spec["graph"]["entry_points"] = ["missing"]
    elif case_id == "unreachable-node":
        spec["nodes"].append(deterministic_node("orphan"))
    elif case_id == "invalid-edge-endpoint":
        spec["edges"][0]["target"] = "missing"
    elif case_id == "no-terminal-path":
        spec["edges"] = []
    elif case_id in {"unbounded-cycle", "cycle-without-exit"}:
        spec["edges"].append(control_edge("finish-produce", "finish", "produce"))
        if case_id == "cycle-without-exit":
            guard = {"max_iterations": 2, "exit_condition": "never"}
            for edge in spec["edges"]:
                edge["iteration_guard"] = guard
            spec["graph"]["terminals"] = []
    elif case_id == "unbounded-dynamic-fanout":
        spec["graph"]["topology_binding"] = "runtime-expanded"
    elif case_id == "incompatible-ports":
        spec["nodes"][1]["ports"]["inputs"][0]["type"] = "OtherV1"
    elif case_id == "undeclared-state-access":
        spec["nodes"][0]["state_reads"] = ["missing"]
    elif case_id == "concurrent-write":
        spec["nodes"][1]["state_writes"] = ["result"]
        spec["state"]["channels"][0].pop("owner", None)
    elif case_id == "non-exhaustive-routing":
        spec["edges"][0]["condition"] = {"eq": ["state.route", "finish"]}
    elif case_id == "unbounded-retry":
        spec["nodes"][0]["retry_policy"]["max_attempts"] = None
    elif case_id == "unsafe-effect-retry":
        spec["nodes"][0]["side_effect_class"] = "non_idempotent"
        spec["nodes"][0]["retry_policy"]["max_attempts"] = 2
    elif case_id in {"protected-without-binding", "protected-without-post-state", "protected-without-idempotency", "protected-without-compensation"}:
        node = spec["nodes"][0]
        node["side_effect_class"] = "protected_action"
        node["idempotency_ref"] = "key"
        node["approval_binding_ref"] = "approval"
        node["postcondition_ref"] = "post"
        spec["controls"]["approval_bindings"] = [{"id": "approval", "action_digest": "sha256:00", "scope": {}, "approver_identity": "a", "expires_at": "2030", "nonce": "n", "revoked": False}]
        spec["controls"]["idempotency_policies"] = [{"id": "key"}]
        spec["controls"]["postconditions"] = [{"id": "post"}]
        spec["controls"]["compensations"] = [{"id": "rollback", "action_ref": "produce", "requires_new_approval": True, "outcome_verification_ref": "post"}]
        if case_id == "protected-without-binding":
            spec["controls"]["approval_bindings"] = []
        elif case_id == "protected-without-post-state":
            spec["controls"]["postconditions"] = []
        elif case_id == "protected-without-idempotency":
            spec["controls"]["idempotency_policies"] = []
        else:
            spec["controls"]["compensations"] = []
    elif case_id == "unsafe-interrupt":
        spec["runtime"]["interrupts"] = [{"id": "pause", "resume_node": "missing"}]
    elif case_id == "model-contract-missing":
        spec["nodes"][0].pop("prompt_ref")
        spec["nodes"][0].pop("output_schema_ref")
    elif case_id == "evolution-gate-missing":
        spec["evolution"] = {"status": "candidate"}
    elif case_id == "predicate-code-injection":
        spec["edges"][0]["condition"] = {"eval": "__import__('os').system('echo pwned')"}
    else:
        raise AssertionError(f"unknown negative case {case_id}")
    return spec


class GraphToolTests(unittest.TestCase):
    def test_all_machine_schemas_are_strict_output_compatible(self) -> None:
        def inspect(value: object, path: str = "$") -> list[str]:
            issues: list[str] = []
            if isinstance(value, dict):
                if value.get("type") == "object":
                    properties = value.get("properties")
                    if not isinstance(properties, dict):
                        issues.append(f"{path}: object schema lacks explicit properties")
                    else:
                        if value.get("additionalProperties") is not False:
                            issues.append(f"{path}: additionalProperties must be false")
                        missing = sorted(set(properties) - set(value.get("required", [])))
                        if missing:
                            issues.append(f"{path}: required omits {missing}")
                for key, child in value.items():
                    issues.extend(inspect(child, f"{path}.{key}"))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    issues.extend(inspect(child, f"{path}[{index}]"))
            return issues

        for schema_path in (ROOT / "schemas").glob("*.schema.json"):
            with self.subTest(schema=schema_path.name):
                schema = json.loads(schema_path.read_text(encoding="utf-8"))
                self.assertEqual([], inspect(schema))

    def test_template_is_valid(self) -> None:
        self.assertEqual([], graph_tool.validate(base_spec()))

    def test_all_artifact_examples_match_their_schemas(self) -> None:
        samples = {
            "GraphDecision": ROOT / "tests" / "fixtures" / "artifacts" / "graph-decision.json",
            "GraphSpec": ROOT / "templates" / "graph-spec.json",
            "ImplementationMapping": ROOT / "tests" / "fixtures" / "artifacts" / "implementation-mapping.json",
            "GraphAudit": ROOT / "tests" / "fixtures" / "artifacts" / "graph-audit.json",
            "RunDiagnosis": ROOT / "tests" / "fixtures" / "artifacts" / "run-diagnosis.json",
            "OptimizationPlan": ROOT / "tests" / "fixtures" / "artifacts" / "optimization-plan.json",
            "EvolutionProposal": ROOT / "tests" / "fixtures" / "artifacts" / "evolution-proposal.json",
        }
        self.assertEqual(set(graph_tool.ARTIFACT_SCHEMAS), set(samples))
        for artifact, sample_path in samples.items():
            with self.subTest(artifact=artifact):
                document = json.loads(sample_path.read_text(encoding="utf-8"))
                schema = json.loads(graph_tool.artifact_schema_path(artifact).read_text(encoding="utf-8"))
                self.assertEqual(artifact, schema["title"])
                self.assertEqual([], graph_tool.validate_artifact(document, schema))

    def test_applicable_templates_match_their_schemas(self) -> None:
        samples = {
            "GraphSpec": ROOT / "templates" / "graph-spec.json",
            "EvolutionProposal": ROOT / "templates" / "evolution-proposal.json",
        }
        for artifact, sample_path in samples.items():
            with self.subTest(artifact=artifact):
                document = json.loads(sample_path.read_text(encoding="utf-8"))
                schema = json.loads(graph_tool.artifact_schema_path(artifact).read_text(encoding="utf-8"))
                self.assertEqual([], graph_tool.validate_artifact(document, schema))

    def test_artifact_schema_rejects_missing_and_additional_fields(self) -> None:
        document = json.loads((ROOT / "tests" / "fixtures" / "artifacts" / "graph-decision.json").read_text(encoding="utf-8"))
        schema = json.loads(graph_tool.artifact_schema_path("GraphDecision").read_text(encoding="utf-8"))
        document.pop("evidence")
        document["task"] = "wrong alias"
        codes = {item["code"] for item in graph_tool.validate_artifact(document, schema)}
        self.assertEqual({"E_ARTIFACT_ADDITIONAL", "E_ARTIFACT_REQUIRED"}, codes)

    def test_validate_artifact_cli_auto_selects_schema(self) -> None:
        sample = ROOT / "tests" / "fixtures" / "artifacts" / "graph-decision.json"
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = graph_tool.main(["validate-artifact", str(sample)])
        self.assertEqual(0, exit_code)
        self.assertEqual("VALID GraphDecision 1.0\n", output.getvalue())

    def test_all_positive_fixtures_validate(self) -> None:
        cases = json.loads((ROOT / "tests" / "fixtures" / "positive-cases.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "schemas" / "graph-spec.schema.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                document = build_positive(case["id"])
                self.assertEqual([], graph_tool.validate_artifact(document, schema))
                self.assertEqual([], graph_tool.validate(document))

    def test_all_negative_fixtures_emit_exact_expected_codes(self) -> None:
        cases = json.loads((ROOT / "tests" / "fixtures" / "negative-cases.json").read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                codes = {item["code"] for item in graph_tool.validate(mutate_negative(case["id"]))}
                self.assertEqual(set(case["expected_codes"]), codes)

    def test_normalized_json_matches_golden(self) -> None:
        expected = (ROOT / "tests" / "golden" / "direct-chain.normalized.json").read_text(encoding="utf-8")
        self.assertEqual(expected, graph_tool.normalized_json(base_spec()))

    def test_mermaid_matches_golden(self) -> None:
        expected = (ROOT / "tests" / "golden" / "direct-chain.mmd").read_text(encoding="utf-8")
        self.assertEqual(expected, graph_tool.mermaid(base_spec()))

    def test_semantic_diff_classification(self) -> None:
        old = base_spec()
        old["graph"]["assurance_profile"] = "high_assurance"
        new = copy.deepcopy(old)
        new["graph"]["version"] = "2.0.0"
        new["graph"]["assurance_profile"] = "standard"
        new["prompts"][0]["digest"] = "sha256:11"
        new["nodes"][0]["model_ref"] = "model-policy/new"
        new["nodes"][0]["permissions"] = ["network:example.com"]
        new["nodes"][0]["ports"]["outputs"][0]["type"] = "ResultV2"
        new["state"]["migration_version"] = "2"
        new["evaluation"]["baseline"] = "new baseline"
        new["edges"][0]["routed_outcome"] = "new-outcome"
        result = graph_tool.diff_specs(old, new)
        expected = json.loads((ROOT / "tests" / "golden" / "semantic-diff.json").read_text(encoding="utf-8"))
        self.assertEqual(expected, result)

    def test_untrusted_strings_are_data_not_code(self) -> None:
        spec = base_spec()
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "executed.txt"
            payload = f"<script>__import__('pathlib').Path({str(marker)!r}).write_text('bad')</script>"
            spec["edges"][0]["routed_outcome"] = payload
            rendered = graph_tool.mermaid(spec)
            normalized = graph_tool.normalized_json(spec)
            self.assertIn("__import__", rendered)
            self.assertIn("__import__", normalized)
            self.assertNotIn("<script>", rendered)
            self.assertFalse(marker.exists())

    def test_inspect_reports_structure_and_digest(self) -> None:
        result = graph_tool.inspect_spec(base_spec())
        self.assertEqual(["produce"], result["entries"])
        self.assertEqual(["finish"], result["terminals"])
        self.assertEqual([], result["cycles"])
        self.assertTrue(result["digest"].startswith("sha256:"))


if __name__ == "__main__":
    unittest.main()
