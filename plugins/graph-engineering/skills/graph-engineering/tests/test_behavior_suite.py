from __future__ import annotations

import json
import hashlib
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_SPEC = importlib.util.spec_from_file_location("run_behavior_suite", ROOT / "evals" / "run_behavior_suite.py")
assert RUNNER_SPEC and RUNNER_SPEC.loader
run_behavior_suite = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(run_behavior_suite)


class BehaviorSuiteContractTests(unittest.TestCase):
    def test_every_mode_has_a_machine_schema(self) -> None:
        expected = {"graph-decision.schema.json", "graph-spec.schema.json", "implementation-mapping.schema.json", "graph-audit.schema.json", "run-diagnosis.schema.json", "optimization-plan.schema.json", "evolution-proposal.schema.json"}
        self.assertEqual(expected, {path.name for path in (ROOT / "schemas").glob("*.schema.json")})

    def test_required_scenarios_and_modes(self) -> None:
        scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
        self.assertEqual(12, len(scenarios))
        self.assertEqual({"select", "design", "compile", "audit", "diagnose", "optimize", "evolve"}, {item["expected_mode"] for item in scenarios})
        self.assertEqual(len(scenarios), len({item["id"] for item in scenarios}))
        for scenario in scenarios:
            self.assertTrue(scenario["required"])
            self.assertIn(scenario["expected_artifact"], {"GraphDecision", "GraphSpec", "ImplementationMapping", "GraphAudit", "RunDiagnosis", "OptimizationPlan", "EvolutionProposal"})
            if "input_fixture" in scenario:
                self.assertTrue((ROOT / scenario["input_fixture"]).is_file())

    def test_routing_evaluation_schema_accepts_all_expected_routes(self) -> None:
        schema = json.loads((ROOT / "evals" / "routing.schema.json").read_text(encoding="utf-8"))
        scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
        for scenario in scenarios:
            route = {"mode": scenario["expected_mode"], "artifact": scenario["expected_artifact"], "decision": scenario["expected_decision"], "rationale": "Evaluation fixture."}
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual([], run_behavior_suite.graph_tool.validate_against_schema(route, schema))

    def test_behavior_grader_passes_complete_no_graph_artifact(self) -> None:
        scenario = next(item for item in json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8")) if item["id"] == "trivial-no-graph")
        document = json.loads((ROOT / "tests" / "fixtures" / "artifacts" / "graph-decision.json").read_text(encoding="utf-8"))
        route = {"ok": True, "document": {"mode": "select", "artifact": "GraphDecision", "decision": "no_graph", "rationale": "Deterministic work."}}
        artifact = {"ok": True, "document": document}
        grade = run_behavior_suite.grade_scenario(scenario, route, artifact)
        self.assertTrue(grade["passed"])

    def test_behavior_grader_reports_malformed_graph_without_crashing(self) -> None:
        scenario = next(item for item in json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8")) if item["id"] == "cyclic-repair")
        route = {"ok": True, "document": {"mode": "design", "artifact": "GraphSpec", "decision": "graph", "rationale": "Graph requested."}}
        artifact = {"ok": True, "document": {"artifact": "GraphSpec", "schema_version": "1.0", "graph": {"terminals": [{"id": "done"}]}}}
        grade = run_behavior_suite.grade_scenario(scenario, route, artifact)
        self.assertFalse(grade["passed"])
        self.assertTrue(grade["diagnostics"])

    def test_all_deterministic_behavior_artifacts_pass(self) -> None:
        scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
        for scenario in scenarios:
            route = {"ok": True, "document": {"mode": scenario["expected_mode"], "artifact": scenario["expected_artifact"], "decision": scenario["expected_decision"], "rationale": "Deterministic fixture route."}}
            with self.subTest(scenario=scenario["id"]):
                grade = run_behavior_suite.grade_scenario(scenario, route, run_behavior_suite.fixture_run(scenario))
                self.assertTrue(grade["passed"])
                self.assertEqual(16, grade["total"])
                self.assertEqual([], grade["diagnostics"])

    def test_scope_and_no_graph_negatives_exist(self) -> None:
        scenarios = {item["id"]: item for item in json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))}
        self.assertEqual("no_graph", scenarios["trivial-no-graph"]["expected_decision"])
        self.assertEqual("out_of_scope", scenarios["graphrag-out-of-scope"]["expected_decision"])
        self.assertEqual("no_graph_artifact", scenarios["conversation-not-artifact"]["expected_decision"])

    def test_rubric_grades_all_required_dimensions(self) -> None:
        rubric = json.loads((ROOT / "evals" / "rubric.json").read_text(encoding="utf-8"))
        self.assertEqual({"mode", "topology_decision", "artifact_completeness", "bounded_execution", "state_correctness", "evidence_treatment", "security_controls", "ceremony"}, set(rubric["dimensions"]))
        self.assertEqual({"mode", "bounded_execution", "security_controls"}, set(rubric["mandatory_zero_fail"]))

    def test_regression_record_is_truthfully_scoped(self) -> None:
        record = json.loads((ROOT / "evals" / "regression-record.json").read_text(encoding="utf-8"))
        self.assertIn("no model-artifact quality claim", record["method"])
        self.assertEqual(7, record["new_skill"]["public_artifact_schemas"])
        self.assertEqual([], record["observed_regressions_within_recorded_scope"])

    def test_behavior_result_is_complete_current_and_truthfully_scoped(self) -> None:
        record = json.loads((ROOT / "evals" / "behavior-results.json").read_text(encoding="utf-8"))
        scenarios = json.loads((ROOT / "evals" / "scenarios.json").read_text(encoding="utf-8"))
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        normalized_skill = skill_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
        expected_digest = "sha256:" + hashlib.sha256(normalized_skill).hexdigest()
        self.assertEqual(expected_digest, record["skill_digest"])
        self.assertEqual({"passed": 12, "failed": 0, "total": 12}, record["summary"])
        self.assertEqual({item["id"] for item in scenarios}, {item["id"] for item in record["results"]})
        self.assertIn("no model-artifact quality claim", record["method"])
        for result in record["results"]:
            with self.subTest(scenario=result["id"]):
                self.assertTrue(result["passed"])
                self.assertEqual(16, result["total"])
                self.assertTrue(result["route_run"]["ok"])
                self.assertTrue(result["route_run"]["session_id"])
                self.assertEqual("deterministic_fixture", result["artifact_run"]["source"])


if __name__ == "__main__":
    unittest.main()
