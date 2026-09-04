from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_FILES = {
    "GraphDecision": "graph-decision.schema.json",
    "GraphSpec": "graph-spec.schema.json",
    "ImplementationMapping": "implementation-mapping.schema.json",
    "GraphAudit": "graph-audit.schema.json",
    "RunDiagnosis": "run-diagnosis.schema.json",
    "OptimizationPlan": "optimization-plan.schema.json",
    "EvolutionProposal": "evolution-proposal.schema.json",
}

MODULE_SPEC = importlib.util.spec_from_file_location("graph_tool", ROOT / "scripts" / "graph_tool.py")
assert MODULE_SPEC and MODULE_SPEC.loader
graph_tool = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(graph_tool)

FIXTURE_MODULE: Any = None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True).lower()


def positive_graph_fixture(case_id: str) -> dict[str, Any]:
    global FIXTURE_MODULE
    if FIXTURE_MODULE is None:
        fixture_spec = importlib.util.spec_from_file_location("graph_fixture_factory", ROOT / "tests" / "test_graph_tool.py")
        assert fixture_spec and fixture_spec.loader
        FIXTURE_MODULE = importlib.util.module_from_spec(fixture_spec)
        fixture_spec.loader.exec_module(FIXTURE_MODULE)
    return copy.deepcopy(FIXTURE_MODULE.build_positive(case_id))


def deterministic_artifact(scenario: dict[str, Any]) -> dict[str, Any]:
    scenario_id = scenario["id"]
    graph_cases = {
        "parallel-research-verification": "parallel-reducer-join",
        "cyclic-repair": "bounded-evaluator-repair",
        "unknown-runtime-expansion": "runtime-work-queue",
        "protected-deployment": "protected-external-action",
    }
    if scenario_id in graph_cases:
        document = positive_graph_fixture(graph_cases[scenario_id])
        if scenario_id == "parallel-research-verification":
            document["graph"]["objective"] = "Research two markets independently, verify material claims, and join only verified evidence."
            document["graph"]["constraints"].extend(["Independent lanes must not share conclusions before verification.", "Verification must seek disconfirming evidence to limit correlated error."])
        elif scenario_id == "unknown-runtime-expansion":
            document["graph"]["constraints"].append("Runtime expansion cannot change permissions; expanded work remains under the declared permission ceiling.")
        elif scenario_id == "protected-deployment":
            document["graph"]["objective"] = "Deploy an approved digest with least privilege and verify authoritative post-state."
        return document

    fixture_files = {
        "trivial-no-graph": "graph-decision.json",
        "audit-only": "graph-audit.json",
        "trace-diagnosis": "run-diagnosis.json",
        "prompt-optimization-frozen-topology": "optimization-plan.json",
        "persistent-topology-evolution": "evolution-proposal.json",
        "framework-compile": "implementation-mapping.json",
    }
    if scenario_id in fixture_files:
        return copy.deepcopy(load_json(ROOT / "tests" / "fixtures" / "artifacts" / fixture_files[scenario_id]))

    decision = copy.deepcopy(load_json(ROOT / "tests" / "fixtures" / "artifacts" / "graph-decision.json"))
    decision["selected_approach"] = "not_applicable"
    if scenario_id == "graphrag-out-of-scope":
        decision.update({
            "objective": "Classify a GraphRAG knowledge-graph request against the skill boundary.",
            "decision": "out_of_scope",
            "rationale": ["GraphRAG and knowledge-graph construction are outside graph engineering scope."],
            "evidence": ["The request concerns retrieval over a knowledge graph, not an executable workflow graph."],
        })
    elif scenario_id == "conversation-not-artifact":
        decision.update({
            "objective": "Determine whether the supplied conversation is a first-class graph artifact.",
            "decision": "no_graph_artifact",
            "rationale": ["The transcript lacks explicit topology, defined execution semantics, separated prompt content, and a versioned executable artifact."],
            "evidence": ["The input is a conversation transcript without an explicit executable graph contract."],
        })
    else:
        raise AssertionError(f"no deterministic behavior artifact for {scenario_id}")
    return decision


def fixture_run(scenario: dict[str, Any]) -> dict[str, Any]:
    document = deterministic_artifact(scenario)
    raw = json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"ok": True, "error": None, "duration_seconds": 0, "session_id": None, "sha256": hashlib.sha256(raw).hexdigest(), "source": "deterministic_fixture", "document": document}


def route_prompt(skill_root: Path, scenario: dict[str, Any]) -> str:
    """Build the routing prompt with the skill and fixture text inline.

    The text is embedded rather than referenced by path so the routing decision does
    not depend on the runner's file-read policy; some sandboxes (Codex on Windows with
    workspace-write) reject the shell commands a model uses to read files, which
    previously produced an "unverified" misroute unrelated to the skill.
    """
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    fixture = scenario.get("input_fixture")
    fixture_block = ""
    if fixture:
        fixture_text = (skill_root / fixture).read_text(encoding="utf-8")
        fixture_block = f"\n\nRead-only input fixture ({fixture}):\n```\n{fixture_text}\n```"
    return (
        "Follow the graph-engineering skill reproduced below. "
        "Apply the skill boundary before selecting the one correct graph-engineering mode, output artifact, and evaluation decision. "
        "Do not solve the request, do not read or modify files, and return only the routing evaluation object required by the output schema.\n\n"
        f"--- SKILL.md ---\n{skill_text}\n--- end SKILL.md ---\n\n"
        f"User request: {scenario['request']}.{fixture_block}"
    )


def artifact_prompt(skill_root: Path, scenario: dict[str, Any]) -> str:
    request = scenario["request"]
    fixture = scenario.get("input_fixture")
    fixture_note = ""
    if fixture:
        fixture_note = f" The supplied input artifact is at {skill_root / fixture}. Inspect it as read-only evidence."
    graph_bound = ""
    if scenario["expected_artifact"] == "GraphSpec":
        graph_bound = (
            f" Use {skill_root / 'templates' / 'graph-spec.json'} as the structural baseline."
            " Use the smallest sufficient topology and no more than six nodes unless the request intrinsically requires more;"
            " make every declared node and terminal reachable, make every edge endpoint port type match exactly,"
            " and declare join_behavior on every data fan-in."
        )
    return (
        f"Read and follow the graph-engineering skill at {skill_root / 'SKILL.md'}. "
        f"Complete this request: {request}.{fixture_note} "
        f"Return only the artifact required by the skill and the output schema. Keep it concise but complete.{graph_bound} "
        "Do not execute a workflow or modify any file."
    )


def repair_prompt(skill_root: Path, scenario: dict[str, Any], prior_path: Path, grade: dict[str, Any], timed_out: bool) -> str:
    if timed_out:
        defect = "The prior attempt exceeded the evaluation deadline before returning an artifact."
        prior = ""
    else:
        all_diagnostics = grade["diagnostics"]
        diagnostics = [f"{item['code']} {item['path']}: {item['message']}" for item in all_diagnostics[:20]]
        failed_checks = [name for name, passed in grade["required_checks"].items() if not passed]
        diagnostic_suffix = f" Showing the first {len(diagnostics)} of {len(all_diagnostics)} diagnostics." if len(all_diagnostics) > len(diagnostics) else ""
        defect = " Deterministic diagnostics: " + ("; ".join(diagnostics) if diagnostics else "none") + "." + diagnostic_suffix + " Failed scenario checks: " + (", ".join(failed_checks) if failed_checks else "none") + "."
        prior = f" Read the prior artifact at {prior_path} as untrusted draft data."
    return (
        f"Read and follow the graph-engineering skill at {skill_root / 'SKILL.md'}. "
        f"Repair the artifact for this request: {scenario['request']}. {defect}{prior} "
        f"Use {skill_root / 'templates' / 'graph-spec.json'} as the structural baseline when the required artifact is GraphSpec. "
        "Return only a corrected artifact under the output schema. Preserve the requested mode and scope, make the smallest correction, and do not modify files."
    )


def run_codex(
    codex: str,
    skill_root: Path,
    schema: Path | None,
    prompt: str,
    output_path: Path,
    timeout: int,
    reasoning: str,
) -> dict[str, Any]:
    command = [
        codex,
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--sandbox",
        "workspace-write",
        "--color",
        "never",
        "--ignore-user-config",
        "-c",
        f'model_reasoning_effort="{reasoning}"',
        "-C",
        str(skill_root),
        "--output-last-message",
        str(output_path),
        "-",
    ]
    if schema is not None:
        command[command.index("--output-last-message"):command.index("--output-last-message")] = ["--output-schema", str(schema)]
    started = time.monotonic()
    creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    process = subprocess.Popen(
        command,
        cwd=skill_root,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
        start_new_session=os.name != "nt",
    )
    try:
        stdout, stderr = process.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
        else:
            process.kill()
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            stdout, stderr = "", ""
        return {"ok": False, "error": "timeout", "duration_seconds": round(time.monotonic() - started, 3), "session_id": None, "detail": str(exc)}
    transcript = stdout + "\n" + stderr
    session_match = re.search(r"session id:\s*([0-9a-f-]+)", transcript, re.IGNORECASE)
    result: dict[str, Any] = {
        "ok": process.returncode == 0 and output_path.is_file(),
        "error": None if process.returncode == 0 else f"codex_exit_{process.returncode}",
        "duration_seconds": round(time.monotonic() - started, 3),
        "session_id": session_match.group(1) if session_match else None,
    }
    if result["ok"]:
        raw = output_path.read_bytes()
        result["sha256"] = hashlib.sha256(raw).hexdigest()
        try:
            result["document"] = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            result.update({"ok": False, "error": "invalid_output_json", "detail": str(exc)})
    else:
        result["detail"] = transcript[-2000:]
    return result


def graph_has_join(document: dict[str, Any]) -> bool:
    incoming: dict[str, int] = {}
    for edge in document.get("edges", []):
        if edge.get("semantic") == "data":
            incoming[edge.get("target", "")] = incoming.get(edge.get("target", ""), 0) + 1
    return any(count > 1 for count in incoming.values()) and any(edge.get("join_behavior") for edge in document.get("edges", []))


def graph_has_bounded_cycle(document: dict[str, Any]) -> bool:
    inspection = graph_tool.inspect_spec(document)
    if not inspection["cycles"]:
        return False
    return not any(item["code"] == "E_UNBOUNDED_CYCLE" for item in graph_tool.validate(document))


def protected_controls(document: dict[str, Any]) -> bool:
    protected = [node for node in document.get("nodes", []) if node.get("side_effect_class") == "protected_action"]
    bindings = document.get("controls", {}).get("approval_bindings", [])
    postconditions = document.get("controls", {}).get("postconditions", [])
    compensations = document.get("controls", {}).get("compensations", [])
    return bool(
        protected
        and bindings
        and postconditions
        and compensations
        and all(node.get("approval_binding_ref") and node.get("postcondition_ref") and node.get("idempotency_ref") for node in protected)
        and all(binding.get("action_digest") and binding.get("scope") and binding.get("approver_identity") and binding.get("expires_at") and binding.get("nonce") and binding.get("revoked") is False for binding in bindings)
    )


def scenario_checks(scenario_id: str, document: dict[str, Any]) -> dict[str, bool]:
    text = compact_text(document)
    checks: dict[str, bool] = {}
    if scenario_id == "trivial-no-graph":
        checks = {"deterministic_or_direct": document.get("selected_approach") in {"deterministic_code", "direct_call"}, "no_unnecessary_ceremony": document.get("decision") == "no_graph"}
    elif scenario_id == "parallel-research-verification":
        checks = {"fan_out": document.get("runtime", {}).get("max_concurrency", 0) > 1 and document.get("runtime", {}).get("fan_out") not in {None, "none"}, "join": graph_has_join(document), "verification": "verif" in text, "correlated_error_controls": "independent" in text and ("disconfirm" in text or "correlat" in text)}
    elif scenario_id == "cyclic-repair":
        checks = {"iteration_guard": graph_has_bounded_cycle(document), "exit_route": not any(item["code"] == "E_CYCLE_EXIT" for item in graph_tool.validate(document)), "exhaustion_route": "exhaust" in text or "failed" in text or "partial" in text}
    elif scenario_id == "unknown-runtime-expansion":
        expansion = document.get("runtime", {}).get("dynamic_expansion")
        checks = {"runtime_expansion_bounds": document.get("graph", {}).get("topology_binding") == "runtime-expanded" and isinstance(expansion, dict) and all(expansion.get(key, 0) > 0 for key in ("max_nodes", "max_edges", "max_depth", "max_queue", "max_concurrency")), "queue_bounds": isinstance(expansion, dict) and expansion.get("max_queue", 0) > 0, "permissions_unchanged": "permission" in text and ("unchanged" in text or "undeclared" in text or "ceiling" in text)}
    elif scenario_id == "audit-only":
        checks = {"verdict": bool(document.get("verdict")), "evidence": bool(document.get("invariant_coverage")), "no_unsolicited_redesign": set(document) == {"artifact", "schema_version", "mode", "graph_ref", "scope", "verdict", "findings", "invariant_coverage", "unknowns"}}
    elif scenario_id == "trace-diagnosis":
        checks = {"first_invalid_transition": bool(document.get("first_invalid_transition")), "failure_frontier": bool(document.get("failure_frontier")), "unknowns": isinstance(document.get("unknowns"), list)}
    elif scenario_id == "prompt-optimization-frozen-topology":
        frozen = " ".join(document.get("frozen_surfaces", [])).lower()
        checks = {"frozen_topology": "topology" in frozen and "permission" in frozen, "held_out": "held" in compact_text(document.get("data_splits", [])), "budgets": bool(document.get("budgets")), "rollback": bool(document.get("rollback"))}
    elif scenario_id == "persistent-topology-evolution":
        checks = {"baseline": bool(document.get("baseline_graph")), "candidate": bool(document.get("candidate_graph")), "held_out": bool(document.get("held_out_gate")), "ablation": bool(document.get("structural_ablations")), "rollback": bool(document.get("rollback"))}
    elif scenario_id == "protected-deployment":
        checks = {"approval_binding": protected_controls(document), "least_privilege": "least" in text and "privilege" in text, "post_state": bool(document.get("controls", {}).get("postconditions")), "compensation": bool(document.get("controls", {}).get("compensations"))}
    elif scenario_id == "graphrag-out-of-scope":
        checks = {"explicit_scope_boundary": document.get("decision") == "out_of_scope" and ("scope" in text or "knowledge graph" in text or "graphrag" in text)}
    elif scenario_id == "conversation-not-artifact":
        checks = {"four_conditions": "explicit" in text and ("executable" in text or "execution" in text) and ("version" in text or "artifact" in text), "no_false_claim": document.get("decision") == "no_graph_artifact"}
    elif scenario_id == "framework-compile":
        checks = {"version_date": bool(document.get("target", {}).get("version")) and bool(document.get("target", {}).get("verified_at")), "semantic_mapping": bool(document.get("semantic_mappings")), "gaps": isinstance(document.get("gaps"), list), "conformance_tests": bool(document.get("conformance_tests"))}
    return checks


def grade_scenario(scenario: dict[str, Any], route: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    document = artifact.get("document") if artifact.get("ok") else None
    route_document = route.get("document") if route.get("ok") else None
    diagnostics: list[dict[str, str]] = []
    if isinstance(document, dict):
        schema = load_json(ROOT / "schemas" / SCHEMA_FILES[scenario["expected_artifact"]])
        diagnostics = graph_tool.validate_artifact(document, schema)
    routing_ok = isinstance(route_document, dict) and all(
        route_document.get(key) == scenario[expected]
        for key, expected in (("mode", "expected_mode"), ("artifact", "expected_artifact"), ("decision", "expected_decision"))
    )
    artifact_ok = isinstance(document, dict) and not diagnostics
    required = scenario_checks(scenario["id"], document) if artifact_ok else {name: False for name in scenario["required"]}
    required_ok = all(required.get(name, False) for name in scenario["required"])
    is_graph = scenario["expected_artifact"] == "GraphSpec"
    bounded = artifact_ok
    state = artifact_ok
    evidence = artifact_ok
    security = artifact_ok
    if is_graph and isinstance(document, dict):
        bounded = bool(document.get("graph", {}).get("budgets")) and all(node.get("retry_policy", {}).get("max_attempts", 0) > 0 for node in document.get("nodes", []))
        state = isinstance(document.get("state", {}).get("channels"), list)
        evidence = document.get("observability", {}).get("outcome_evidence") is True
        security = bool(document.get("controls", {}).get("authorization")) and bool(document.get("controls", {}).get("trust_labels"))
    elif scenario["expected_artifact"] == "OptimizationPlan" and isinstance(document, dict):
        bounded = bool(document.get("repeated_trials")) and bool(document.get("budgets"))
        evidence = bool(document.get("data_splits")) and bool(document.get("graders"))
    elif scenario["expected_artifact"] == "EvolutionProposal" and isinstance(document, dict):
        bounded = bool(document.get("budgets")) and bool(document.get("held_out_gate"))
        evidence = bool(document.get("credit_assignment")) and bool(document.get("structural_ablations"))
    elif scenario["expected_artifact"] == "GraphDecision" and isinstance(document, dict):
        bounded = bool(document.get("bounds"))
        evidence = isinstance(document.get("evidence"), list) and isinstance(document.get("unknowns"), list)
    elif scenario["expected_artifact"] == "GraphAudit" and isinstance(document, dict):
        evidence = bool(document.get("invariant_coverage")) and isinstance(document.get("findings"), list)
    elif scenario["expected_artifact"] == "RunDiagnosis" and isinstance(document, dict):
        evidence = bool(document.get("root_cause_evidence")) and bool(document.get("propagation_path"))
    elif scenario["expected_artifact"] == "ImplementationMapping" and isinstance(document, dict):
        evidence = bool(document.get("semantic_mappings")) and isinstance(document.get("residual_risks"), list)
    dimensions = {
        "mode": 2 if routing_ok else 0,
        "topology_decision": 2 if routing_ok else 0,
        "artifact_completeness": 2 if artifact_ok else 0,
        "bounded_execution": 2 if bounded else 0,
        "state_correctness": 2 if state else 0,
        "evidence_treatment": 2 if evidence else 0,
        "security_controls": 2 if security and (scenario["id"] != "protected-deployment" or protected_controls(document)) else 0,
        "ceremony": 2 if artifact_ok and isinstance(document, dict) and document.get("artifact") == scenario["expected_artifact"] else 0,
    }
    mandatory = {"mode", "bounded_execution", "security_controls"}
    total = sum(dimensions.values())
    passed = artifact_ok and routing_ok and required_ok and total >= 13 and all(dimensions[name] > 0 for name in mandatory)
    return {"passed": passed, "dimensions": dimensions, "total": total, "required_checks": required, "diagnostics": diagnostics}


def evaluate_one(scenario: dict[str, Any], codex: str, skill_root: Path, output_dir: Path, timeout: int, reasoning: str, artifact_source: str) -> dict[str, Any]:
    print(f"[start] {scenario['id']}", flush=True)
    route = run_codex(codex, skill_root, ROOT / "evals" / "routing.schema.json", route_prompt(skill_root, scenario), output_dir / f"{scenario['id']}.route.json", timeout, reasoning)
    print(f"[route] {scenario['id']} ok={route.get('ok')} duration={route.get('duration_seconds')}", flush=True)
    if artifact_source == "deterministic":
        artifact = fixture_run(scenario)
        attempts = [artifact]
        grade = grade_scenario(scenario, route, artifact)
        print(f"[artifact] {scenario['id']} source=deterministic_fixture", flush=True)
    else:
        schema = skill_root / "schemas" / SCHEMA_FILES[scenario["expected_artifact"]]
        first_path = output_dir / f"{scenario['id']}.artifact.json"
        artifact = run_codex(codex, skill_root, schema, artifact_prompt(skill_root, scenario), first_path, timeout, reasoning)
        print(f"[artifact] {scenario['id']} ok={artifact.get('ok')} duration={artifact.get('duration_seconds')}", flush=True)
        grade = grade_scenario(scenario, route, artifact)
        attempts = [artifact]
        needs_artifact_repair = not artifact.get("ok") or bool(grade["diagnostics"]) or not all(grade["required_checks"].values())
        if needs_artifact_repair:
            repair_path = output_dir / f"{scenario['id']}.artifact.repair.json"
            repaired = run_codex(codex, skill_root, schema, repair_prompt(skill_root, scenario, first_path, grade, artifact.get("error") == "timeout"), repair_path, timeout, reasoning)
            attempts.append(repaired)
            print(f"[repair] {scenario['id']} ok={repaired.get('ok')} duration={repaired.get('duration_seconds')}", flush=True)
            if repaired.get("ok") or not artifact.get("ok"):
                artifact = repaired
                grade = grade_scenario(scenario, route, artifact)
    result = {
        "id": scenario["id"],
        "expected": {"mode": scenario["expected_mode"], "decision": scenario["expected_decision"], "artifact": scenario["expected_artifact"]},
        "observed_route": route.get("document") if route.get("ok") else None,
        "route_run": {key: route.get(key) for key in ("ok", "error", "duration_seconds", "session_id", "sha256")},
        "artifact_attempts": [{key: attempt.get(key) for key in ("ok", "error", "duration_seconds", "session_id", "sha256")} for attempt in attempts],
        "artifact_run": {key: artifact.get(key) for key in ("ok", "error", "duration_seconds", "session_id", "sha256", "source")},
        **grade,
    }
    print(f"[finish] {scenario['id']} passed={result['passed']} attempts={len(attempts)}", flush=True)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run fresh-session graph-engineering behavior evaluations without retaining raw runs.")
    parser.add_argument("--skill-root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--scenario", action="append", default=[])
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument("--reasoning", choices=("low", "medium", "high"), default="low")
    parser.add_argument("--artifact-source", choices=("deterministic", "fresh"), default="deterministic")
    parser.add_argument("--codex", default="codex")
    args = parser.parse_args(argv)
    codex = shutil.which(args.codex)
    if not codex:
        parser.error(f"Codex executable not found: {args.codex}")
    skill_root = args.skill_root.resolve()
    scenarios = load_json(ROOT / "evals" / "scenarios.json")
    selected = set(args.scenario)
    if selected:
        scenarios = [scenario for scenario in scenarios if scenario["id"] in selected]
        missing = selected - {scenario["id"] for scenario in scenarios}
        if missing:
            parser.error(f"Unknown scenarios: {sorted(missing)}")
    codex_version = subprocess.run([codex, "--version"], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False).stdout.strip()
    skill_text = (skill_root / "SKILL.md").read_text(encoding="utf-8")
    normalized_skill = skill_text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")
    skill_digest = "sha256:" + hashlib.sha256(normalized_skill).hexdigest()

    def write_record(results: list[dict[str, Any]]) -> dict[str, Any]:
        ordered = sorted(results, key=lambda item: item["id"])
        record = {
            "schema_version": "1.0",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "runner": codex_version,
            "skill_digest": skill_digest,
            "method": (
                "Independent fresh routing sessions in a disposable copy of the skill; deterministic scenario artifacts validated against exact public schemas and semantic checks; no model-artifact quality claim; raw routing runs and the temporary workspace discarded."
                if args.artifact_source == "deterministic"
                else "Independent fresh routing and artifact sessions per scenario in a disposable copy of the skill; exact public service-side output schemas plus deterministic local semantic grading; at most one validator-driven artifact repair or timeout retry; raw runs and the temporary workspace discarded."
            ),
            "results": ordered,
            "summary": {"passed": sum(item["passed"] for item in ordered), "failed": sum(not item["passed"] for item in ordered), "total": len(ordered)},
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    with tempfile.TemporaryDirectory(prefix="graph-engineering-behavior-") as directory:
        output_dir = Path(directory)
        run_root = output_dir / "skill"
        shutil.copytree(skill_root, run_root, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        artifact_dir = run_root / ".eval-output"
        artifact_dir.mkdir()
        results: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            futures = {executor.submit(evaluate_one, scenario, codex, run_root, artifact_dir, args.timeout, args.reasoning, args.artifact_source): scenario["id"] for scenario in scenarios}
            for future in as_completed(futures):
                results.append(future.result())
                write_record(results)
    record = write_record(results)
    print(json.dumps(record["summary"], sort_keys=True))
    return 0 if record["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
