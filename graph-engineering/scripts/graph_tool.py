#!/usr/bin/env python3
"""Deterministic graph-artifact validation, inspection, normalization, rendering, and diffing.

This tool performs no model calls, network calls, imports of user code, or workflow execution.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


ALLOWED_PROFILES = {"standard", "protected_action", "high_assurance"}
ALLOWED_KINDS = {"deterministic", "model", "agent", "tool", "human", "subgraph"}
ALLOWED_SEMANTICS = {"control", "data", "error", "interrupt", "compensation"}
ALLOWED_OPERATORS = {"all", "any", "not", "eq", "ne", "exists", "in", "gt", "gte", "lt", "lte"}
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")
ARTIFACT_SCHEMAS = {
    "GraphDecision": "graph-decision.schema.json",
    "GraphSpec": "graph-spec.schema.json",
    "ImplementationMapping": "implementation-mapping.schema.json",
    "GraphAudit": "graph-audit.schema.json",
    "RunDiagnosis": "run-diagnosis.schema.json",
    "OptimizationPlan": "optimization-plan.schema.json",
    "EvolutionProposal": "evolution-proposal.schema.json",
}


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("GraphSpec root must be a JSON object")
    return value


def diagnostic(code: str, path: str, message: str, severity: str = "error") -> dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "message": message}


def resolve_local_ref(root_schema: dict[str, Any], reference: str) -> dict[str, Any]:
    if not reference.startswith("#/"):
        raise ValueError(f"only local JSON Schema references are supported: {reference}")
    value: Any = root_schema
    for raw_part in reference[2:].split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(value, dict) or part not in value:
            raise ValueError(f"unresolved JSON Schema reference: {reference}")
        value = value[part]
    if not isinstance(value, dict):
        raise ValueError(f"JSON Schema reference is not an object: {reference}")
    return value


def matches_json_type(value: Any, expected: str) -> bool:
    if expected == "null":
        return value is None
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "string":
        return isinstance(value, str)
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    raise ValueError(f"unsupported JSON Schema type: {expected}")


def validate_against_schema(
    value: Any,
    schema: dict[str, Any],
    root_schema: dict[str, Any] | None = None,
    path: str = "$",
) -> list[dict[str, str]]:
    """Validate the deterministic JSON Schema subset used by this package."""
    root = root_schema or schema
    if "$ref" in schema:
        return validate_against_schema(value, resolve_local_ref(root, schema["$ref"]), root, path)
    if "anyOf" in schema:
        branches = [validate_against_schema(value, branch, root, path) for branch in schema["anyOf"]]
        if any(not diagnostics for diagnostics in branches):
            return []
        return [diagnostic("E_ARTIFACT_ANY_OF", path, "value does not match any allowed schema branch")]
    out: list[dict[str, str]] = []
    expected_type = schema.get("type")
    if expected_type is not None:
        options = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(matches_json_type(value, option) for option in options):
            return [diagnostic("E_ARTIFACT_TYPE", path, f"expected type {options}, got {type(value).__name__}")]
    if "const" in schema and value != schema["const"]:
        out.append(diagnostic("E_ARTIFACT_CONST", path, f"expected constant {schema['const']!r}"))
    if "enum" in schema and value not in schema["enum"]:
        out.append(diagnostic("E_ARTIFACT_ENUM", path, f"value is not one of {schema['enum']!r}"))
    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                out.append(diagnostic("E_ARTIFACT_REQUIRED", f"{path}.{key}", "required field is missing"))
        properties = schema.get("properties", {})
        for key, child in value.items():
            if key in properties:
                out.extend(validate_against_schema(child, properties[key], root, f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                out.append(diagnostic("E_ARTIFACT_ADDITIONAL", f"{path}.{key}", "additional field is not allowed"))
            elif isinstance(schema.get("additionalProperties"), dict):
                out.extend(validate_against_schema(child, schema["additionalProperties"], root, f"{path}.{key}"))
    if isinstance(value, list):
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            out.append(diagnostic("E_ARTIFACT_MIN_ITEMS", path, f"requires at least {minimum} items"))
        maximum = schema.get("maxItems")
        if isinstance(maximum, int) and len(value) > maximum:
            out.append(diagnostic("E_ARTIFACT_MAX_ITEMS", path, f"allows at most {maximum} items"))
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                out.extend(validate_against_schema(item, item_schema, root, f"{path}[{index}]"))
    if isinstance(value, (int, float)) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        out.append(diagnostic("E_ARTIFACT_MINIMUM", path, f"must be at least {schema['minimum']}"))
    if isinstance(value, str) and "pattern" in schema and re.search(schema["pattern"], value) is None:
        out.append(diagnostic("E_ARTIFACT_PATTERN", path, "string does not match the required pattern"))
    return sorted(out, key=lambda item: (item["path"], item["code"], item["message"]))


def artifact_schema_path(artifact: str) -> Path:
    filename = ARTIFACT_SCHEMAS.get(artifact)
    if filename is None:
        raise ValueError(f"unknown artifact type {artifact!r}; expected one of {sorted(ARTIFACT_SCHEMAS)}")
    return Path(__file__).resolve().parents[1] / "schemas" / filename


def validate_artifact(document: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, str]]:
    out = validate_against_schema(document, schema)
    if document.get("artifact") == "GraphSpec" and not out:
        out.extend(validate(document))
    return sorted(out, key=lambda item: (item["path"], item["code"], item["message"]))


def stable_list(values: list[Any]) -> list[Any]:
    normalized = [normalize_value(value) for value in values]
    return sorted(normalized, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


def normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: normalize_value(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return stable_list(value)
    return value


def normalized_json(spec: dict[str, Any]) -> str:
    return json.dumps(normalize_value(spec), ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def indexed(items: Any, key: str = "id") -> tuple[dict[str, dict[str, Any]], list[str]]:
    result: dict[str, dict[str, Any]] = {}
    duplicates: list[str] = []
    if not isinstance(items, list):
        return result, duplicates
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get(key), str):
            continue
        item_id = item[key]
        if item_id in result:
            duplicates.append(item_id)
        else:
            result[item_id] = item
    return result, duplicates


def validate_predicate(value: Any, path: str, out: list[dict[str, str]]) -> None:
    if not isinstance(value, dict) or len(value) != 1:
        out.append(diagnostic("E_PREDICATE_LANGUAGE", path, "condition must be a one-operator object"))
        return
    operator, operand = next(iter(value.items()))
    if operator not in ALLOWED_OPERATORS:
        out.append(diagnostic("E_PREDICATE_LANGUAGE", path, f"operator {operator!r} is not allowed"))
        return
    if operator in {"all", "any"}:
        if not isinstance(operand, list) or not operand:
            out.append(diagnostic("E_PREDICATE_LANGUAGE", path, f"{operator} requires a non-empty list"))
            return
        for index, child in enumerate(operand):
            validate_predicate(child, f"{path}.{operator}[{index}]", out)
    elif operator == "not":
        validate_predicate(operand, f"{path}.not", out)
    elif operator == "exists":
        if not isinstance(operand, str):
            out.append(diagnostic("E_PREDICATE_LANGUAGE", path, "exists requires a state path string"))
    elif operator in {"eq", "ne", "in", "gt", "gte", "lt", "lte"}:
        if not isinstance(operand, list) or len(operand) != 2:
            out.append(diagnostic("E_PREDICATE_LANGUAGE", path, f"{operator} requires a two-item list"))


def adjacency(nodes: Iterable[str], edges: list[dict[str, Any]]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    forward = {node: [] for node in nodes}
    reverse = {node: [] for node in nodes}
    for edge in edges:
        source, target = edge.get("source"), edge.get("target")
        if source in forward and target in reverse:
            forward[source].append(target)
            reverse[target].append(source)
    return forward, reverse


def reachable_from(starts: Iterable[str], graph: dict[str, list[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque(node for node in starts if node in graph)
    while queue:
        node = queue.popleft()
        if node in seen:
            continue
        seen.add(node)
        queue.extend(graph[node])
    return seen


def strongly_connected(graph: dict[str, list[str]]) -> list[set[str]]:
    index = 0
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[set[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = low[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in graph[node]:
            if target not in indices:
                visit(target)
                low[node] = min(low[node], low[target])
            elif target in on_stack:
                low[node] = min(low[node], indices[target])
        if low[node] == indices[node]:
            component: set[str] = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            components.append(component)

    for node in sorted(graph):
        if node not in indices:
            visit(node)
    return components


def has_cycle(component: set[str], graph: dict[str, list[str]]) -> bool:
    return len(component) > 1 or any(node in graph[node] for node in component)


def validate(spec: dict[str, Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if spec.get("schema_version") != "1.0":
        out.append(diagnostic("E_SCHEMA_VERSION", "$.schema_version", "schema_version must equal '1.0'"))

    graph_meta = spec.get("graph")
    if not isinstance(graph_meta, dict):
        out.append(diagnostic("E_REQUIRED", "$.graph", "graph object is required"))
        graph_meta = {}
    for field in ("id", "version", "objective", "success_criteria", "partial_success_criteria", "constraints", "non_goals", "risk_profile", "assurance_profile", "entry_points", "terminals", "budgets", "representation", "topology_binding"):
        if field not in graph_meta:
            out.append(diagnostic("E_REQUIRED", f"$.graph.{field}", "required field is missing"))
    if graph_meta.get("assurance_profile") not in ALLOWED_PROFILES:
        out.append(diagnostic("E_ASSURANCE_PROFILE", "$.graph.assurance_profile", "unknown assurance profile"))
    graph_id = graph_meta.get("id")
    if isinstance(graph_id, str) and not ID_RE.fullmatch(graph_id):
        out.append(diagnostic("E_ID", "$.graph.id", "invalid graph identifier"))

    raw_nodes = spec.get("nodes")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        out.append(diagnostic("E_REQUIRED", "$.nodes", "nodes must be a non-empty list"))
        raw_nodes = []
    nodes, duplicate_nodes = indexed(raw_nodes)
    for node_id in duplicate_nodes:
        out.append(diagnostic("E_DUPLICATE_NODE", "$.nodes", f"duplicate node id {node_id!r}"))

    raw_edges = spec.get("edges")
    if not isinstance(raw_edges, list):
        out.append(diagnostic("E_REQUIRED", "$.edges", "edges must be a list"))
        raw_edges = []
    edges, duplicate_edges = indexed(raw_edges)
    for edge_id in duplicate_edges:
        out.append(diagnostic("E_DUPLICATE_EDGE", "$.edges", f"duplicate edge id {edge_id!r}"))

    prompts, duplicate_prompts = indexed(spec.get("prompts", []))
    contexts, duplicate_contexts = indexed(spec.get("context_policies", []))
    for item_id in duplicate_prompts:
        out.append(diagnostic("E_DUPLICATE_PROMPT", "$.prompts", f"duplicate prompt id {item_id!r}"))
    for item_id in duplicate_contexts:
        out.append(diagnostic("E_DUPLICATE_CONTEXT", "$.context_policies", f"duplicate context policy id {item_id!r}"))

    state = spec.get("state")
    if not isinstance(state, dict):
        out.append(diagnostic("E_REQUIRED", "$.state", "state object is required"))
        state = {}
    channels, duplicate_channels = indexed(state.get("channels", []))
    for channel_id in duplicate_channels:
        out.append(diagnostic("E_DUPLICATE_STATE", "$.state.channels", f"duplicate state channel id {channel_id!r}"))

    node_ports: dict[str, dict[str, dict[str, str]]] = {}
    writers: dict[str, list[str]] = defaultdict(list)
    for index, node in enumerate(raw_nodes):
        path = f"$.nodes[{index}]"
        if not isinstance(node, dict):
            out.append(diagnostic("E_NODE_CONTRACT", path, "node must be an object"))
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not ID_RE.fullmatch(node_id):
            out.append(diagnostic("E_ID", f"{path}.id", "node requires a valid id"))
            continue
        required = ("execution_kind", "semantic_role", "ports", "context_policy_ref", "state_reads", "state_writes", "permissions", "timeout_ms", "retry_policy", "side_effect_class", "outcomes", "acceptance_conditions")
        for field in required:
            if field not in node:
                out.append(diagnostic("E_NODE_CONTRACT", f"{path}.{field}", "required node contract field is missing"))
        if node.get("execution_kind") not in ALLOWED_KINDS:
            out.append(diagnostic("E_NODE_CONTRACT", f"{path}.execution_kind", "unknown execution kind"))
        if node.get("context_policy_ref") not in contexts:
            out.append(diagnostic("E_CONTEXT_CONTRACT", f"{path}.context_policy_ref", "context policy reference is missing"))
        kind = node.get("execution_kind")
        if kind in {"model", "agent"}:
            if node.get("prompt_ref") not in prompts:
                out.append(diagnostic("E_MODEL_CONTRACT", f"{path}.prompt_ref", "model/agent node requires a declared prompt"))
            if not node.get("output_schema_ref"):
                out.append(diagnostic("E_MODEL_CONTRACT", f"{path}.output_schema_ref", "model/agent node requires structured output"))
        ports = node.get("ports") if isinstance(node.get("ports"), dict) else {}
        port_map: dict[str, dict[str, str]] = {"inputs": {}, "outputs": {}}
        for direction in ("inputs", "outputs"):
            values = ports.get(direction, [])
            if not isinstance(values, list):
                out.append(diagnostic("E_PORT_CONTRACT", f"{path}.ports.{direction}", "ports must be a list"))
                continue
            seen_ports: set[str] = set()
            for port_index, port in enumerate(values):
                if not isinstance(port, dict) or not isinstance(port.get("name"), str) or not isinstance(port.get("type"), str):
                    out.append(diagnostic("E_PORT_CONTRACT", f"{path}.ports.{direction}[{port_index}]", "port requires name and type"))
                    continue
                if port["name"] in seen_ports:
                    out.append(diagnostic("E_PORT_CONTRACT", f"{path}.ports.{direction}", f"duplicate port {port['name']!r}"))
                seen_ports.add(port["name"])
                port_map[direction][port["name"]] = port["type"]
        node_ports[node_id] = port_map
        for operation, key in (("read", "state_reads"), ("write", "state_writes")):
            values = node.get(key, [])
            if not isinstance(values, list):
                out.append(diagnostic("E_STATE_ACCESS", f"{path}.{key}", f"state {operation}s must be a list"))
                continue
            for channel_id in values:
                if channel_id not in channels:
                    out.append(diagnostic("E_STATE_ACCESS", f"{path}.{key}", f"undeclared state channel {channel_id!r}"))
                elif operation == "write":
                    writers[channel_id].append(node_id)
        retry = node.get("retry_policy")
        if not isinstance(retry, dict) or not isinstance(retry.get("max_attempts"), int) or retry.get("max_attempts", 0) < 1:
            out.append(diagnostic("E_UNBOUNDED_RETRY", f"{path}.retry_policy", "max_attempts must be a positive integer"))
        elif retry["max_attempts"] > 1 and node.get("side_effect_class") in {"non_idempotent", "protected_action"} and not node.get("idempotency_ref"):
            out.append(diagnostic("E_UNSAFE_RETRY", f"{path}.retry_policy", "retrying this effect requires idempotency_ref"))

    for index, edge in enumerate(raw_edges):
        path = f"$.edges[{index}]"
        if not isinstance(edge, dict):
            out.append(diagnostic("E_EDGE_CONTRACT", path, "edge must be an object"))
            continue
        source, target = edge.get("source"), edge.get("target")
        if source not in nodes or target not in nodes:
            out.append(diagnostic("E_EDGE_ENDPOINT", path, "edge source and target must reference declared nodes"))
            continue
        if edge.get("semantic") not in ALLOWED_SEMANTICS:
            out.append(diagnostic("E_EDGE_CONTRACT", f"{path}.semantic", "unknown edge semantic"))
        source_port, target_port = edge.get("source_port"), edge.get("target_port")
        if source_port == "$control" or target_port == "$control":
            if source_port != target_port:
                out.append(diagnostic("E_PORT_TYPE", path, "control edges must use $control at both ends"))
        else:
            source_type = node_ports.get(source, {}).get("outputs", {}).get(source_port)
            target_type = node_ports.get(target, {}).get("inputs", {}).get(target_port)
            if source_type is None or target_type is None or source_type != target_type:
                out.append(diagnostic("E_PORT_TYPE", path, "edge ports are missing or have incompatible types"))
        if edge.get("condition") is not None:
            validate_predicate(edge["condition"], f"{path}.condition", out)

    valid_edges = [edge for edge in raw_edges if isinstance(edge, dict) and edge.get("source") in nodes and edge.get("target") in nodes]
    forward, reverse = adjacency(nodes, valid_edges)
    entries = graph_meta.get("entry_points", []) if isinstance(graph_meta.get("entry_points"), list) else []
    terminals = graph_meta.get("terminals", []) if isinstance(graph_meta.get("terminals"), list) else []
    missing_entries = [node for node in entries if node not in nodes]
    missing_terminals = [node for node in terminals if node not in nodes]
    if missing_entries or missing_terminals:
        out.append(diagnostic("E_MISSING_NODE", "$.graph", f"unknown entries/terminals: {sorted(missing_entries + missing_terminals)}"))
    reached = reachable_from(entries, forward)
    runtime = spec.get("runtime", {}) if isinstance(spec.get("runtime"), dict) else {}
    cancellation = runtime.get("cancellation", {}) if isinstance(runtime.get("cancellation"), dict) else {}
    cancel_route = cancellation.get("cancel_route")
    if cancel_route is not None:
        if cancel_route not in nodes:
            out.append(diagnostic("E_CANCELLATION_ROUTE", "$.runtime.cancellation.cancel_route", "cancel route must reference a declared node"))
        else:
            reached.add(cancel_route)
    for node_id in sorted(set(nodes) - reached):
        out.append(diagnostic("E_UNREACHABLE_NODE", f"$.nodes.{node_id}", "node is unreachable from every entry point"))
    can_reach_terminal = reachable_from(terminals, reverse)
    for node_id, node in sorted(nodes.items()):
        if node_id not in can_reach_terminal and not node.get("long_running", False):
            out.append(diagnostic("E_NO_TERMINAL_PATH", f"$.nodes.{node_id}", "node cannot reach a terminal"))

    for component in strongly_connected(forward):
        if not has_cycle(component, forward):
            continue
        component_edges = [edge for edge in valid_edges if edge["source"] in component and edge["target"] in component]
        unguarded_edges = [
            edge
            for edge in component_edges
            if not isinstance(edge.get("iteration_guard"), dict)
            or not isinstance(edge["iteration_guard"].get("max_iterations"), int)
            or edge["iteration_guard"].get("max_iterations", 0) < 1
        ]
        unguarded_forward, _ = adjacency({node_id: nodes[node_id] for node_id in component}, unguarded_edges)
        if any(has_cycle(residual, unguarded_forward) for residual in strongly_connected(unguarded_forward)):
            out.append(diagnostic("E_UNBOUNDED_CYCLE", "$.edges", f"cycle {sorted(component)} contains a traversal with no finite iteration guard"))
        exit_edges = [edge for edge in valid_edges if edge["source"] in component and edge["target"] not in component]
        if not exit_edges and not component.intersection(terminals):
            out.append(diagnostic("E_CYCLE_EXIT", "$.edges", f"cycle {sorted(component)} has no exit route"))

    outgoing: dict[str, list[dict[str, Any]]] = defaultdict(list)
    incoming: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in valid_edges:
        outgoing[edge["source"]].append(edge)
        incoming[edge["target"]].append(edge)
    for node_id, node_edges in outgoing.items():
        conditional = [edge for edge in node_edges if edge.get("condition") is not None]
        if conditional and not any(edge.get("default", False) or edge.get("semantic") == "error" for edge in node_edges):
            out.append(diagnostic("E_NON_EXHAUSTIVE_ROUTE", f"$.nodes.{node_id}", "conditional routing requires a default or error route"))
    for node_id, node_edges in incoming.items():
        data_edges = [edge for edge in node_edges if edge.get("semantic") == "data"]
        if len(data_edges) > 1 and not all(edge.get("join_behavior") for edge in data_edges):
            out.append(diagnostic("E_JOIN_BEHAVIOR", f"$.nodes.{node_id}", "fan-in data edges require join_behavior"))

    for channel_id, node_ids in writers.items():
        if len(set(node_ids)) > 1:
            channel = channels.get(channel_id, {})
            safe = channel.get("reducer") or channel.get("concurrent_write") == "serialized" or (channel.get("owner") in set(node_ids) and set(node_ids) == {channel.get("owner")})
            if not safe:
                out.append(diagnostic("E_CONCURRENT_WRITE", f"$.state.channels.{channel_id}", f"multiple writers {sorted(set(node_ids))} need a reducer or serialization"))

    runtime = spec.get("runtime")
    if not isinstance(runtime, dict):
        out.append(diagnostic("E_REQUIRED", "$.runtime", "runtime object is required"))
        runtime = {}
    for field in ("scheduler", "ready_rule", "max_concurrency", "cancellation", "resume", "node_state_transitions"):
        if field not in runtime:
            out.append(diagnostic("E_RUNTIME_CONTRACT", f"$.runtime.{field}", "required runtime field is missing"))
    if graph_meta.get("topology_binding") in {"runtime-expanded", "bounded-agent-selected"}:
        expansion = runtime.get("dynamic_expansion")
        required_bounds = ("max_nodes", "max_edges", "max_depth", "max_queue", "max_concurrency")
        if not isinstance(expansion, dict) or any(not isinstance(expansion.get(key), int) or expansion.get(key, 0) < 1 for key in required_bounds):
            out.append(diagnostic("E_UNBOUNDED_EXPANSION", "$.runtime.dynamic_expansion", "dynamic topology requires finite node, edge, depth, queue, and concurrency bounds"))
    interrupts = runtime.get("interrupts", [])
    if isinstance(interrupts, list):
        for index, interrupt in enumerate(interrupts):
            if not isinstance(interrupt, dict) or not all(interrupt.get(key) for key in ("id", "checkpoint", "resume_node", "resume_validation", "expiry", "cancel_route")) or interrupt.get("resume_node") not in nodes:
                out.append(diagnostic("E_UNSAFE_INTERRUPT", f"$.runtime.interrupts[{index}]", "interrupt requires durable checkpoint, valid resume, validation, expiry, and cancel route"))

    controls = spec.get("controls")
    if not isinstance(controls, dict):
        out.append(diagnostic("E_REQUIRED", "$.controls", "controls object is required"))
        controls = {}
    bindings, _ = indexed(controls.get("approval_bindings", []))
    idempotency_policies, _ = indexed(controls.get("idempotency_policies", []))
    postconditions, _ = indexed(controls.get("postconditions", []))
    compensations = [item for item in controls.get("compensations", []) if isinstance(item, dict)] if isinstance(controls.get("compensations", []), list) else []
    for node_id, node in nodes.items():
        if node.get("side_effect_class") == "protected_action":
            binding = bindings.get(node.get("approval_binding_ref"))
            idempotency_policy = idempotency_policies.get(node.get("idempotency_ref"))
            postcondition = postconditions.get(node.get("postcondition_ref"))
            required_binding = ("action_digest", "scope", "approver_identity", "expires_at", "nonce", "revoked")
            if not binding or any(key not in binding for key in required_binding):
                out.append(diagnostic("E_PROTECTED_APPROVAL", f"$.nodes.{node_id}", "protected action requires a complete ApprovalBinding"))
            if not postcondition:
                out.append(diagnostic("E_POST_STATE_VERIFY", f"$.nodes.{node_id}", "protected action requires authoritative post-state verification"))
            if not idempotency_policy:
                out.append(diagnostic("E_PROTECTED_IDEMPOTENCY", f"$.nodes.{node_id}", "protected action requires a referenced idempotency policy"))
            compensation = next((item for item in compensations if item.get("action_ref") == node_id), None)
            if not compensation or compensation.get("outcome_verification_ref") not in postconditions:
                out.append(diagnostic("E_PROTECTED_COMPENSATION", f"$.nodes.{node_id}", "protected action requires a compensation policy with authoritative outcome verification"))

    for field in ("observability", "evaluation", "evolution"):
        if not isinstance(spec.get(field), dict):
            out.append(diagnostic("E_REQUIRED", f"$.{field}", f"{field} object is required"))

    evolution = spec.get("evolution") if isinstance(spec.get("evolution"), dict) else {}
    if evolution.get("status") == "candidate":
        required = ("baseline_version", "candidate_version", "held_out_evaluation_ref", "budgets", "promotion_criteria", "rollback")
        for field in required:
            if not evolution.get(field):
                out.append(diagnostic("E_EVOLUTION_GATE", f"$.evolution.{field}", "candidate evolution field is required"))

    return sorted(out, key=lambda item: (item["path"], item["code"], item["message"]))


def inspect_spec(spec: dict[str, Any]) -> dict[str, Any]:
    nodes, _ = indexed(spec.get("nodes", []))
    raw_edges = [edge for edge in spec.get("edges", []) if isinstance(edge, dict)]
    forward, _ = adjacency(nodes, raw_edges)
    components = [sorted(component) for component in strongly_connected(forward) if has_cycle(component, forward)]
    risks = sorted({node.get("side_effect_class", "none") for node in nodes.values()} - {"none", "read_only"})
    joins = sorted(node_id for node_id in nodes if sum(1 for edge in raw_edges if edge.get("target") == node_id) > 1)
    normalized = normalized_json(spec).encode("utf-8")
    return {
        "graph_id": spec.get("graph", {}).get("id"),
        "graph_version": spec.get("graph", {}).get("version"),
        "digest": "sha256:" + hashlib.sha256(normalized).hexdigest(),
        "entries": sorted(spec.get("graph", {}).get("entry_points", [])),
        "terminals": sorted(spec.get("graph", {}).get("terminals", [])),
        "node_count": len(nodes),
        "edge_count": len(raw_edges),
        "reachable": sorted(reachable_from(spec.get("graph", {}).get("entry_points", []), forward)),
        "cycles": sorted(components),
        "joins": joins,
        "risk_classes": risks,
        "budgets": normalize_value(spec.get("graph", {}).get("budgets", {})),
        "required_controls": sorted({"approval_binding", "post_state_verification"} if "protected_action" in risks else set()),
        "diagnostics": validate(spec),
    }


def mermaid(spec: dict[str, Any]) -> str:
    nodes, _ = indexed(spec.get("nodes", []))
    lines = ["flowchart TD"]
    terminals = set(spec.get("graph", {}).get("terminals", []))
    entries = set(spec.get("graph", {}).get("entry_points", []))
    aliases = {node_id: f"n{index}" for index, node_id in enumerate(sorted(nodes))}
    for node_id in sorted(nodes):
        alias = aliases[node_id]
        label = html.escape(node_id.replace('"', "'"), quote=False)
        if node_id in entries:
            lines.append(f'  {alias}(["{label}"])')
        elif node_id in terminals:
            lines.append(f'  {alias}[["{label}"]]')
        else:
            lines.append(f'  {alias}["{label}"]')
    for edge in sorted((edge for edge in spec.get("edges", []) if isinstance(edge, dict)), key=lambda edge: str(edge.get("id", ""))):
        source, target = edge.get("source"), edge.get("target")
        if source not in nodes or target not in nodes:
            continue
        label = html.escape(str(edge.get("routed_outcome") or edge.get("semantic") or "edge").replace('"', "'").replace("\n", " "), quote=False)
        lines.append(f'  {aliases[source]} -->|"{label}"| {aliases[target]}')
    return "\n".join(lines) + "\n"


def dot(spec: dict[str, Any]) -> str:
    nodes, _ = indexed(spec.get("nodes", []))
    lines = ["digraph GraphSpec {"]
    for node_id in sorted(nodes):
        lines.append(f"  {json.dumps(node_id)};")
    for edge in sorted((edge for edge in spec.get("edges", []) if isinstance(edge, dict)), key=lambda edge: str(edge.get("id", ""))):
        if edge.get("source") in nodes and edge.get("target") in nodes:
            label = edge.get("routed_outcome") or edge.get("semantic") or "edge"
            lines.append(f"  {json.dumps(edge['source'])} -> {json.dumps(edge['target'])} [label={json.dumps(str(label))}];")
    lines.append("}")
    return "\n".join(lines) + "\n"


def section_changed(old: dict[str, Any], new: dict[str, Any], key: str) -> bool:
    return normalize_value(old.get(key)) != normalize_value(new.get(key))


def diff_specs(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    categories: set[str] = set()
    breaking: list[str] = []
    risk: list[str] = []
    old_nodes, _ = indexed(old.get("nodes", []))
    new_nodes, _ = indexed(new.get("nodes", []))
    if set(old_nodes) != set(new_nodes):
        categories.add("node")
        removed = sorted(set(old_nodes) - set(new_nodes))
        if removed:
            breaking.append(f"removed nodes: {removed}")
    if section_changed(old, new, "edges"):
        categories.add("edge")
    if section_changed(old, new, "prompts"):
        categories.add("prompt")
    if section_changed(old, new, "state"):
        categories.add("state")
    if section_changed(old, new, "evaluation"):
        categories.add("evaluation")
    old_profile = old.get("graph", {}).get("assurance_profile")
    new_profile = new.get("graph", {}).get("assurance_profile")
    if old_profile != new_profile:
        categories.add("assurance")
        rank = {"standard": 0, "protected_action": 1, "high_assurance": 2}
        if rank.get(new_profile, -1) < rank.get(old_profile, -1):
            risk.append(f"assurance downgraded: {old_profile} -> {new_profile}")
    for node_id in sorted(set(old_nodes).intersection(new_nodes)):
        before, after = old_nodes[node_id], new_nodes[node_id]
        if normalize_value(before.get("model_ref")) != normalize_value(after.get("model_ref")):
            categories.add("model")
        if normalize_value(before.get("prompt_ref")) != normalize_value(after.get("prompt_ref")):
            categories.add("prompt")
        if normalize_value(before.get("permissions")) != normalize_value(after.get("permissions")):
            categories.add("permission")
            old_permissions = set(before.get("permissions", []))
            new_permissions = set(after.get("permissions", []))
            added = sorted(new_permissions - old_permissions)
            if added:
                risk.append(f"node {node_id} added permissions: {added}")
        old_ports = normalize_value(before.get("ports"))
        new_ports = normalize_value(after.get("ports"))
        if old_ports != new_ports:
            categories.add("node")
            breaking.append(f"node {node_id} ports changed")
        if before.get("side_effect_class") != after.get("side_effect_class") and after.get("side_effect_class") in {"non_idempotent", "protected_action"}:
            risk.append(f"node {node_id} side-effect risk expanded")
    if old.get("evaluation") and not new.get("evaluation"):
        breaking.append("evaluation contract removed")
    return {
        "old": {"id": old.get("graph", {}).get("id"), "version": old.get("graph", {}).get("version")},
        "new": {"id": new.get("graph", {}).get("id"), "version": new.get("graph", {}).get("version")},
        "categories": sorted(categories),
        "breaking": bool(breaking),
        "risk_expanding": bool(risk),
        "breaking_reasons": sorted(breaking),
        "risk_reasons": sorted(risk),
    }


def write_output(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8", newline="\n")
    else:
        sys.stdout.write(content)


def command_validate(args: argparse.Namespace) -> int:
    diagnostics = validate(load_json(args.graph))
    if args.format == "json":
        payload = {"valid": not diagnostics, "diagnostics": diagnostics}
        write_output(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.output)
    else:
        if diagnostics:
            write_output("\n".join(f"{item['severity'].upper()} {item['code']} {item['path']}: {item['message']}" for item in diagnostics) + "\n", args.output)
        else:
            write_output("VALID GraphSpec 1.0\n", args.output)
    return 1 if diagnostics else 0


def command_validate_artifact(args: argparse.Namespace) -> int:
    document = load_json(args.artifact_file)
    artifact = args.artifact_type or document.get("artifact")
    if args.schema:
        schema_path = Path(args.schema)
    else:
        if not isinstance(artifact, str):
            raise ValueError("artifact type is required through --type or the document's artifact field")
        schema_path = artifact_schema_path(artifact)
    schema = load_json(schema_path)
    diagnostics = validate_artifact(document, schema)
    artifact_name = artifact if isinstance(artifact, str) else schema.get("title", "artifact")
    if args.format == "json":
        payload = {"valid": not diagnostics, "artifact": artifact_name, "schema": str(schema_path), "diagnostics": diagnostics}
        write_output(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.output)
    elif diagnostics:
        write_output("\n".join(f"{item['severity'].upper()} {item['code']} {item['path']}: {item['message']}" for item in diagnostics) + "\n", args.output)
    else:
        write_output(f"VALID {artifact_name} 1.0\n", args.output)
    return 1 if diagnostics else 0


def command_inspect(args: argparse.Namespace) -> int:
    result = inspect_spec(load_json(args.graph))
    write_output(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", args.output)
    return 1 if result["diagnostics"] else 0


def command_normalize(args: argparse.Namespace) -> int:
    write_output(normalized_json(load_json(args.graph)), args.output)
    return 0


def command_render(args: argparse.Namespace) -> int:
    spec = load_json(args.graph)
    diagnostics = validate(spec)
    if diagnostics and not args.allow_invalid:
        sys.stderr.write("GraphSpec is invalid; use --allow-invalid to render declared nodes/edges anyway.\n")
        return 1
    write_output(mermaid(spec) if args.format == "mermaid" else dot(spec), args.output)
    return 0


def command_diff(args: argparse.Namespace) -> int:
    result = diff_specs(load_json(args.old), load_json(args.new))
    if args.format == "json":
        content = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    else:
        lines = [f"categories: {', '.join(result['categories']) or 'none'}", f"breaking: {str(result['breaking']).lower()}", f"risk_expanding: {str(result['risk_expanding']).lower()}"]
        lines.extend(f"breaking: {reason}" for reason in result["breaking_reasons"])
        lines.extend(f"risk: {reason}" for reason in result["risk_reasons"])
        content = "\n".join(lines) + "\n"
    write_output(content, args.output)
    return 2 if result["breaking"] or result["risk_expanding"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a GraphSpec")
    validate_parser.add_argument("graph")
    validate_parser.add_argument("--format", choices=("text", "json"), default="text")
    validate_parser.add_argument("--output")
    validate_parser.set_defaults(func=command_validate)
    artifact_parser = subparsers.add_parser("validate-artifact", help="validate one of the seven output artifacts against JSON Schema")
    artifact_parser.add_argument("artifact_file")
    artifact_parser.add_argument("--type", dest="artifact_type", choices=tuple(ARTIFACT_SCHEMAS))
    artifact_parser.add_argument("--schema")
    artifact_parser.add_argument("--format", choices=("text", "json"), default="text")
    artifact_parser.add_argument("--output")
    artifact_parser.set_defaults(func=command_validate_artifact)
    inspect_parser = subparsers.add_parser("inspect", help="inspect graph structure and risks")
    inspect_parser.add_argument("graph")
    inspect_parser.add_argument("--output")
    inspect_parser.set_defaults(func=command_inspect)
    normalize_parser = subparsers.add_parser("normalize", help="emit stable canonical JSON")
    normalize_parser.add_argument("graph")
    normalize_parser.add_argument("--output")
    normalize_parser.set_defaults(func=command_normalize)
    render_parser = subparsers.add_parser("render", help="render deterministic Mermaid or DOT")
    render_parser.add_argument("graph")
    render_parser.add_argument("--format", choices=("mermaid", "dot"), default="mermaid")
    render_parser.add_argument("--output")
    render_parser.add_argument("--allow-invalid", action="store_true")
    render_parser.set_defaults(func=command_render)
    diff_parser = subparsers.add_parser("diff", help="classify semantic graph changes")
    diff_parser.add_argument("old")
    diff_parser.add_argument("new")
    diff_parser.add_argument("--format", choices=("text", "json"), default="text")
    diff_parser.add_argument("--output")
    diff_parser.set_defaults(func=command_diff)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"ERROR E_INPUT $: {exc}\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
