#!/usr/bin/env python3
"""Reject artifact contract vocabulary after each owning cutover activates."""

from __future__ import annotations

import re
import shlex
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


ROOT = Path(__file__).resolve().parents[1]

# ARTIFACT_CONTRACT_PHASE: foundation
ARTIFACT_CONTRACT_PHASE = "foundation"

PHASES = (
    "foundation",
    "artifact_store_cutover",
    "guide_source_cutover",
    "upload_admission",
    "submission_cutover",
    "checker_cutover",
)

HISTORICAL_PREFIXES = (
    "docs/internal_reviews/",
    "docs/reference_specs/",
)
AGENT_LOOP_INITIATIVE_PREFIX = ".agent-loop/initiatives/"
ACTIVE_LOOP_PATHS = {
    ".agent-loop/LOOP_STATE.md",
    ".agent-loop/MEMORY.md",
    ".agent-loop/REVIEW_LOG.md",
    ".agent-loop/WORK_QUEUE.md",
}
TEXT_SUFFIXES = {
    ".env",
    ".html",
    ".json",
    ".md",
    ".cfg",
    ".conf",
    ".ini",
    ".puml",
    ".py",
    ".rst",
    ".sh",
    ".tf",
    ".tfvars",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
}
TEXT_FILENAMES = {
    ".env",
    "Dockerfile",
}
FOUNDATION_INTERFACE_PATHS = {
    "backend/app/interfaces/artifacts.py",
    "backend/app/modules/artifacts/contracts.py",
}
FOUNDATION_INTERFACE_PREFIXES = ("contracts/artifact-store/",)
OBJECT_STORAGE_RULE_CODES = {
    "AMBIGUOUS_S3_ADAPTER_NAME",
    "R2_ONLY_PRODUCTION",
    "R2_STATIC_PRODUCTION_CREDENTIALS",
    "OBSOLETE_FLOW_NODE_PLAN",
    "OBSOLETE_ARTIFACT_CHUNK_DEPENDENCY",
    "PROJECT_MANAGER_SETUP_RESUME",
}
R2_CREDENTIAL_OWNER_PATHS = (
    "backend/app/core/",
    "backend/app/adapters/artifacts/",
    "docker-compose",
    "compose",
    ".github/workflows/",
    "deploy/",
    "deployment/",
    "infra/",
    "infrastructure/",
    "k8s/",
    "helm/",
    "charts/",
)

R2_STATIC_CREDENTIAL_KEYS = {
    "aws_access_key_id",
    "aws_secret_access_key",
    "access_key",
    "access_key_id",
    "secret_access_key",
    "secret_key",
}
R2_FORBIDDEN_CREDENTIAL_SOURCE_KEYS = {
    "aws_credential_file",
    "aws_shared_credentials_file",
    "aws_container_credentials_relative_uri",
    "aws_container_authorization_token",
    "aws_profile",
    "aws_default_profile",
    "aws_web_identity_token_file",
    "aws_role_arn",
    "aws_role_session_name",
    "aws_security_token",
    "aws_session_token",
    "aws_sso_session",
    "credential_process",
    "login_session",
    "r2_parent_secret",
    "shared_credentials_file",
}
R2_ISOLATED_CONFIG_SOURCE_KEYS = {
    "aws_config_file",
    "config_file",
    "boto_config",
}
R2_PROVIDER_SELECTOR_KEYS = {"profile", "provider", "backend", "store"}
CONFIG_SUFFIXES = {
    ".cfg",
    ".conf",
    ".ini",
    ".json",
    ".env",
    ".sh",
    ".tf",
    ".tfvars",
    ".toml",
    ".yaml",
    ".yml",
}


def active_initiative_prefixes(root: Path = ROOT) -> tuple[str, ...]:
    """Derive live initiative directories from every in-progress queue row."""
    queue_path = root / ".agent-loop/WORK_QUEUE.md"
    if not queue_path.is_file():
        return ()
    queue = queue_path.read_text(encoding="utf-8")
    in_progress = queue.split("## In Progress", maxsplit=1)[1].split(
        "## Planned Next",
        maxsplit=1,
    )[0]
    initiative_ids = {
        match.group(1)
        for chunk in re.findall(r"\| `([^`]+)` \|", in_progress)
        if (match := re.match(r"([A-Z]+-[A-Z]+-\d+)", chunk))
    }
    initiative_root = root / AGENT_LOOP_INITIATIVE_PREFIX
    if not initiative_root.is_dir():
        return ()
    return tuple(
        f"{AGENT_LOOP_INITIATIVE_PREFIX}{path.name}/"
        for path in sorted(initiative_root.iterdir())
        if path.is_dir() and any(path.name.startswith(item) for item in initiative_ids)
    )


ACTIVE_INITIATIVE_PREFIXES = active_initiative_prefixes()
LIVE_RULE_PATHS = {
    "LEGACY_FLOW_NODE_RUNTIME": (
        "backend/app/core/config.py",
        "backend/app/interfaces/",
        "backend/app/adapters/artifacts/",
    ),
    "LEGACY_GUIDE_CONTENT_CID": (
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
    ),
    "LEGACY_SUBMISSION_TRANSPORT": (
        "backend/app/modules/tasks/",
        "backend/app/modules/checkers/",
    ),
    "LEGACY_PROJECT_STORAGE_POLICY": (
        "backend/app/adapters/project_agents/",
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
        "backend/app/modules/checkers/",
        "backend/app/modules/tasks/",
    ),
    "LEGACY_STORAGE_COMPILER_PRIMITIVE": (
        "backend/app/adapters/project_agents/",
        "backend/app/interfaces/project_agents.py",
        "backend/app/modules/projects/",
        "backend/app/modules/checkers/",
        "backend/app/modules/tasks/",
    ),
    "LEGACY_CHECKER_ARTIFACT_COPY": (
        "backend/app/modules/tasks/",
        "backend/app/modules/checkers/",
    ),
}


@dataclass(frozen=True)
class Rule:
    """One obsolete term and the phase that begins rejecting it."""

    code: str
    active_from: str
    pattern: re.Pattern[str]


RULES = (
    Rule(
        "AMBIGUOUS_S3_ADAPTER_NAME",
        "foundation",
        re.compile(r"\bS3ArtifactStore\b"),
    ),
    Rule(
        "R2_ONLY_PRODUCTION",
        "foundation",
        re.compile(
            r"(?:R2 as (?:the )?intended production|"
            r"(?:only|sole|exclusive)\s+(?:Cloudflare\s+)?R2\s+is\s+supported\s+"
            r"for\s+production(?:\s+deployments?)?|"
            r"production[^.!?]{0,50}\bonly\b[^.!?]{0,30}(?:Cloudflare\s+)?R2|"
            r"(?:Cloudflare )?R2\s+(?:is|as|will be|remains?)\s+(?:the\s+)?"
            r"(?:(?:our|sole|only|exclusive|primary|default)\s+)?production\s+"
            r"(?:provider|backend|store|object storage)|"
            r"production\s+(?:provider|backend|store|object storage)\s+"
            r"(?:is|will be|remains?)\s+(?:Cloudflare\s+)?R2|"
            r"Cloudflare R2\s+intended production)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "R2_STATIC_PRODUCTION_CREDENTIALS",
        "foundation",
        re.compile(
            r"(?:"
            r"(?:Cloudflare\s+)?R2\s+(?:production\s+)?"
            r"(?:supports?|uses?|accepts?|relies\s+on)\s+"
            r"(?:injected\s+)?(?:static|long-lived)\s+"
            r"(?:credentials?|access\s+keys?|secrets?)|"
            r"(?:static|long-lived)\s+(?:credentials?|access\s+keys?|secrets?)\s+"
            r"(?:are\s+)?(?:supported|accepted|used|configured|enabled)\s+"
            r"(?:for|by|with)\s+(?:the\s+)?(?:Cloudflare\s+)?R2\s+"
            r"production(?:\s+profile)?|"
            r"(?:Cloudflare\s+)?R2\s+production\s+credentials?\s+"
            r"(?:are|remain)\s+(?:static|long-lived)|"
            r"configure\s+(?:static|long-lived)\s+credentials?\s+for\s+"
            r"(?:Cloudflare\s+)?R2\s+production|"
            r"(?:Cloudflare\s+)?R2[^.!?]{0,80}"
            r"(?:AWS_ACCESS_KEY_ID|AWS_SECRET_ACCESS_KEY)[^.!?]{0,80}production"
            r")",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "OBSOLETE_FLOW_NODE_PLAN",
        "foundation",
        re.compile(
            r"(?:FN-ART-001|WS-ART-001-02-flow-node-adapter|"
            r"Flow Node\s+(?:is|as)\s+(?:the\s+)?(?:v0\.1\s+)?production\s+"
            r"(?:provider|backend|store)|"
            r"(?:v0\.1\s+)?production[^.!?]{0,40}(?:uses?|handled?\s+by)\s+Flow Node|"
            r"Flow Node[^.!?]{0,40}(?:handles?|stores?)\s+(?:v0\.1\s+)?production\s+"
            r"(?:artifact\s+)?bytes|local/Flow Node interoperability)",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "OBSOLETE_ARTIFACT_CHUNK_DEPENDENCY",
        "foundation",
        re.compile(r"\bWS-ART-001-01C\b"),
    ),
    Rule(
        "PROJECT_MANAGER_SETUP_RESUME",
        "foundation",
        re.compile(
            r"Project Manager[^.!?]{0,120}(?:(?:setup-run|project setup)[^.!?]{0,40}"
            r"(?:continue|resume|retry|restart|re-?run)|"
            r"(?:continue|resume|retry|restart|re-?run)"
            r"[^.!?]{0,40}(?:setup-run|project setup))",
            re.IGNORECASE,
        ),
    ),
    Rule(
        "LEGACY_FLOW_NODE_RUNTIME",
        "artifact_store_cutover",
        re.compile(r"\bflow_node\b", re.IGNORECASE),
    ),
    Rule(
        "PROVIDER_SPECIFIC_GENERIC_INTERFACE",
        "foundation",
        re.compile(r"\b(?:cid|dag|pins?|pinned|pinning)\b", re.IGNORECASE),
    ),
    Rule("LEGACY_GUIDE_CONTENT_CID", "guide_source_cutover", re.compile(r"\bcontent_cid\b")),
    Rule(
        "LEGACY_SUBMISSION_TRANSPORT",
        "submission_cutover",
        re.compile(
            r"\b(?:package_uri|package_hash|artifact_hash_manifest|worker_attestation)\b"
        ),
    ),
    Rule(
        "LEGACY_PROJECT_STORAGE_POLICY",
        "submission_cutover",
        re.compile(
            r"\b(?:manifest_required|artifact_hash_required|artifact_hash_algorithm|"
            r"allowed_storage_schemes)\b"
        ),
    ),
    Rule(
        "LEGACY_CALLER_STORAGE_SCHEME",
        "submission_cutover",
        re.compile(r"\b(?:local|s3|r2)://", re.IGNORECASE),
    ),
    Rule(
        "LEGACY_STORAGE_COMPILER_PRIMITIVE",
        "submission_cutover",
        re.compile(r"\b(?:enforce_storage_scheme|verify_hash|require_manifest_field)\b"),
    ),
    Rule(
        "LEGACY_CHECKER_ARTIFACT_COPY",
        "checker_cutover",
        re.compile(r"\b(?:artifact_manifest_hash|checker_artifact_manifest)\b"),
    ),
)


def phase_index(phase: str) -> int:
    """Return the phase index or fail closed for an unknown marker."""
    if not isinstance(phase, str) or phase not in PHASES:
        raise ValueError(f"malformed artifact contract phase: {phase!r}")
    return PHASES.index(phase)


def rules_for_phase(phase: str) -> tuple[Rule, ...]:
    """Return rules whose owning phase is active at ``phase``."""
    current = phase_index(phase)
    return tuple(rule for rule in RULES if phase_index(rule.active_from) <= current)


def path_is_scannable(relative_path: str) -> bool:
    """Return whether an active source or document path should be scanned."""
    path = Path(relative_path)
    active_initiative = relative_path.startswith(ACTIVE_INITIATIVE_PREFIXES)
    active_loop_path = relative_path in ACTIVE_LOOP_PATHS
    agent_loop_history = (
        relative_path.startswith(AGENT_LOOP_INITIATIVE_PREFIX)
        and "/reviews/" in relative_path
    )
    extensionless_config = (
        not path.suffix
        and relative_path.startswith(R2_CREDENTIAL_OWNER_PATHS)
    )
    return (
        (
            path.suffix.lower() in TEXT_SUFFIXES
            or path.name in TEXT_FILENAMES
            or path.name.startswith(".env.")
            or path.name.startswith("Dockerfile.")
            or extensionless_config
        )
        and not relative_path.startswith(HISTORICAL_PREFIXES)
        and (
            not relative_path.startswith(".agent-loop/")
            or active_initiative
            or active_loop_path
        )
        and not agent_loop_history
        and relative_path != "scripts/check_stale_artifact_contracts.py"
    )


def path_is_active_artifact_contract(relative_path: str) -> bool:
    """Return whether a path carries current artifact architecture wording."""
    if relative_path in {"AGENTS.md", "README.md"}:
        return True
    if relative_path in ACTIVE_LOOP_PATHS:
        return True
    if relative_path.startswith("docs/"):
        return not relative_path.startswith(HISTORICAL_PREFIXES)
    return relative_path.startswith(ACTIVE_INITIATIVE_PREFIXES) and not (
        relative_path.startswith(AGENT_LOOP_INITIATIVE_PREFIX)
        and "/reviews/" in relative_path
    )


def rule_applies_to_path(rule: Rule, relative_path: str) -> bool:
    """Limit foundation neutrality checks to generic artifact contracts."""
    if rule.code == "R2_STATIC_PRODUCTION_CREDENTIALS":
        return path_is_active_artifact_contract(relative_path) or relative_path.startswith(
            R2_CREDENTIAL_OWNER_PATHS
        )
    if rule.code == "AMBIGUOUS_S3_ADAPTER_NAME":
        return path_is_active_artifact_contract(relative_path) or relative_path.startswith(
            "backend/app/adapters/artifacts/"
        )
    if rule.code in OBJECT_STORAGE_RULE_CODES:
        return path_is_active_artifact_contract(relative_path)
    if rule.code in LIVE_RULE_PATHS:
        active_document = relative_path.startswith(
            "docs/"
        ) and path_is_active_artifact_contract(relative_path)
        return active_document or relative_path.startswith(LIVE_RULE_PATHS[rule.code])
    if rule.code == "LEGACY_CALLER_STORAGE_SCHEME":
        return (
            relative_path.startswith("docs/")
            and path_is_active_artifact_contract(relative_path)
        ) or relative_path.startswith(
            (
                "backend/app/modules/projects/",
                "backend/app/modules/tasks/",
                "backend/app/modules/checkers/",
            )
        )
    if rule.code != "PROVIDER_SPECIFIC_GENERIC_INTERFACE":
        return True
    return relative_path in FOUNDATION_INTERFACE_PATHS or relative_path.startswith(
        FOUNDATION_INTERFACE_PREFIXES
    )


def scan_text(relative_path: str, text: str, phase: str) -> list[str]:
    """Return deterministic stale-contract failures for one text file."""
    failures: list[str] = []
    for rule in rules_for_phase(phase):
        if not rule_applies_to_path(rule, relative_path):
            continue
        for match in rule.pattern.finditer(text):
            if rule.code == "PROJECT_MANAGER_SETUP_RESUME" and project_manager_action_denied(
                match.group()
            ):
                continue
            line = text.count("\n", 0, match.start()) + 1
            failures.append(f"{relative_path}:{line}: {rule.code}")
    failures.extend(scan_structured_r2_credentials(relative_path, text))
    return failures


def scan_structured_r2_credentials(relative_path: str, text: str) -> list[str]:
    """Reject static R2 credentials within one structured configuration scope."""
    path = Path(relative_path)
    compose_file = path.name.startswith(("compose.", "docker-compose.")) and path.suffix in {
        ".yml",
        ".yaml",
    }
    config_filename = path.name.startswith(("Dockerfile", ".env"))
    extensionless_config = not path.suffix and relative_path.startswith(
        R2_CREDENTIAL_OWNER_PATHS
    )
    if (
        path.suffix.lower() not in CONFIG_SUFFIXES
        and not compose_file
        and not config_filename
        and not extensionless_config
        and not relative_path.startswith(R2_CREDENTIAL_OWNER_PATHS)
    ):
        return []

    if path.suffix.lower() in {".json", ".yaml", ".yml"}:
        try:
            documents = tuple(yaml.compose_all(text))
        except yaml.YAMLError:
            return [f"{relative_path}:0: R2_CONFIG_PARSE_ERROR"]
        scopes: list[tuple[str, list[tuple[int, str, str]]]] = []
        for document in documents:
            if document is not None:
                scopes.extend(structured_config_scopes(document))
        return r2_scope_failures(relative_path, text, scopes)

    if path.suffix.lower() == ".toml":
        try:
            document = tomllib.loads(text)
        except tomllib.TOMLDecodeError:
            return [f"{relative_path}:0: R2_CONFIG_PARSE_ERROR"]
        return r2_scope_failures(
            relative_path,
            text,
            toml_config_scopes(document, text),
        )

    if path.name.startswith("Dockerfile"):
        return r2_scope_failures(relative_path, text, dockerfile_config_scopes(text))
    if path.suffix.lower() == ".sh":
        return r2_scope_failures(relative_path, text, shell_config_scopes(text))
    if path.name.startswith(".env") or path.suffix.lower() == ".env":
        return r2_scope_failures(relative_path, text, env_config_scopes(text))
    return r2_scope_failures(relative_path, text, line_config_scopes(text))


def structured_config_scopes(
    node: Node,
    label: str = "root",
    inherited: tuple[tuple[int, str, str], ...] = (),
) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize YAML/JSON mappings into independently evaluated config scopes."""
    scopes: list[tuple[str, list[tuple[int, str, str]]]] = []
    if isinstance(node, MappingNode):
        direct: list[tuple[int, str, str]] = []
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode):
                direct.append(
                    (
                        key_node.start_mark.line + 1,
                        "unsupported_assignment_syntax",
                        "fail_closed",
                    )
                )
                continue
            key = normalized_config_key(key_node.value)
            if key in {"environment", "env"}:
                direct.extend(normalize_environment_node(value_node))
            elif key in {"envfrom", "env_from", "env_file", "envfile"}:
                direct.extend(environment_source_entries(key_node, value_node))
            elif isinstance(value_node, ScalarNode):
                direct.append((key_node.start_mark.line + 1, key, value_node.value.lower()))
        combined = merge_entries(inherited, direct)
        scopes.append((label.lower(), combined))
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode):
                continue
            key = normalized_config_key(key_node.value)
            if key not in {"environment", "env"} and isinstance(
                value_node, (MappingNode, SequenceNode)
            ):
                scopes.extend(
                    structured_config_scopes(
                        value_node,
                        f"{label}.{key}",
                        tuple(combined),
                    )
                )
    elif isinstance(node, SequenceNode):
        for index, value_node in enumerate(node.value):
            if isinstance(value_node, (MappingNode, SequenceNode)):
                scopes.extend(
                    structured_config_scopes(
                        value_node,
                        f"{label}[{index}]",
                        inherited,
                    )
                )
    return scopes


def environment_source_entries(
    key_node: ScalarNode,
    value_node: Node,
) -> list[tuple[int, str, str]]:
    """Fail closed on unresolved environment sources and retain R2 context."""
    values: list[str] = []
    if isinstance(value_node, ScalarNode):
        values.append(value_node.value)
    elif isinstance(value_node, SequenceNode):
        values.extend(
            item.value for item in value_node.value if isinstance(item, ScalarNode)
        )
    entries = [
        (
            key_node.start_mark.line + 1,
            "unresolved_environment_source",
            "fail_closed",
        )
    ]
    if any("r2" in value.lower() for value in values):
        entries.append(
            (
                key_node.start_mark.line + 1,
                "artifact_provider_profile",
                "r2",
            )
        )
    return entries


def toml_line_positions(text: str) -> dict[str, list[int]]:
    """Index TOML key occurrences so repeated table keys retain exact lines."""
    positions: dict[str, list[int]] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        for key in re.findall(r"[\"']?([A-Za-z_][A-Za-z0-9_.-]*)[\"']?\s*=", line):
            positions.setdefault(normalized_config_key(key), []).append(line_number)
    return positions


def take_source_line(positions: dict[str, list[int]], key: str) -> int:
    """Consume the next source position for a parsed TOML key."""
    candidates = positions.get(normalized_config_key(key), [])
    return candidates.pop(0) if candidates else 1


def toml_config_scopes(
    document: object,
    text: str,
    label: str = "root",
    inherited: tuple[tuple[int, str, str], ...] = (),
    positions: dict[str, list[int]] | None = None,
) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize TOML tables with parent inheritance and child overrides."""
    if positions is None:
        positions = toml_line_positions(text)
    if isinstance(document, list):
        scopes: list[tuple[str, list[tuple[int, str, str]]]] = []
        for index, item in enumerate(document):
            scopes.extend(
                toml_config_scopes(
                    item,
                    text,
                    f"{label}[{index}]",
                    inherited,
                    positions,
                )
            )
        return scopes
    if not isinstance(document, dict):
        return []
    direct = [
        (
            take_source_line(positions, str(key)),
            normalized_config_key(str(key)),
            str(value).lower(),
        )
        for key, value in document.items()
        if not isinstance(value, (dict, list))
    ]
    combined = merge_entries(inherited, direct)
    scopes = [(label.lower(), combined)]
    for key, value in document.items():
        if isinstance(value, (dict, list)):
            scopes.extend(
                toml_config_scopes(
                    value,
                    text,
                    f"{label}.{str(key).lower()}",
                    tuple(combined),
                    positions,
                )
            )
    return scopes


def line_config_scopes(text: str) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize brace/section configuration while preserving parent context."""
    scopes: dict[str, list[tuple[int, str, str]]] = {"root": []}
    stack = ["root"]
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("#", "//")):
            continue
        section_match = re.fullmatch(r"\[+([^\]]+)\]+", stripped)
        if section_match:
            label = section_match.group(1).strip().lower()
            scopes[label] = []
            stack = [label]
            continue
        block_match = re.match(
            r"([A-Za-z0-9_.-]+)((?:\s+\"[^\"]+\")*)\s*\{\s*$",
            stripped,
        )
        if block_match:
            block, qualifier_text = block_match.groups()
            qualifiers = re.findall(r'"([^\"]+)"', qualifier_text)
            suffix = ".".join([block.lower(), *(item.lower() for item in qualifiers)])
            label = f"{stack[-1]}.{suffix}"
            scopes[label] = list(scopes[stack[-1]])
            stack.append(label)
            continue
        if stripped == "}":
            if len(stack) > 1:
                stack.pop()
            continue
        assignment_text = stripped[2:].strip() if stripped.startswith("- ") else stripped
        assignment_text = re.sub(r"^(?:export|ENV)\s+", "", assignment_text)
        assignment = re.match(
            r"[\"']?([A-Za-z_][A-Za-z0-9_.-]*)[\"']?\s*[:=]\s*"
            r"(.*?)\s*,?\s*$",
            assignment_text,
        )
        if assignment:
            key, value = assignment.groups()
            entries = [
                (
                    line_number,
                    normalized_config_key(key),
                    value.strip("'\"").lower(),
                )
            ]
            entries.extend(
                (
                    line_number,
                    normalized_config_key(inline_key),
                    inline_value.strip("'\"").lower(),
                )
                for inline_key, inline_value in re.findall(
                    r"[\"']?([A-Za-z_][A-Za-z0-9_.-]*)[\"']?\s*=\s*"
                    r"([^,}\s]+)",
                    value,
                )
            )
            scopes[stack[-1]] = merge_entries(scopes[stack[-1]], entries)
            continue
        if "{" in stripped and "}" in stripped and re.search(
            r"(?:r2|credential|access.?key|secret.?key)", stripped, re.IGNORECASE
        ):
            scopes[stack[-1]] = merge_entries(
                scopes[stack[-1]],
                [
                    (line_number, "unsupported_assignment_syntax", "fail_closed"),
                    (
                        line_number,
                        "artifact_provider_profile",
                        "r2" if "r2" in stripped.lower() else "<inherited>",
                    ),
                ],
            )
            continue
        bare_key = assignment_text.strip("'\"").lower()
        if credential_key_is_forbidden(bare_key):
            scopes[stack[-1]] = merge_entries(
                scopes[stack[-1]],
                [(line_number, bare_key, "<inherited>")],
            )
    return list(scopes.items())


def normalize_environment_node(node: Node) -> list[tuple[int, str, str]]:
    """Normalize Compose and Kubernetes environment representations."""
    entries: list[tuple[int, str, str]] = []
    if isinstance(node, ScalarNode):
        return [
            (
                node.start_mark.line + 1,
                "unresolved_environment_source",
                "fail_closed",
            ),
            (
                node.start_mark.line + 1,
                "artifact_provider_profile",
                "r2" if "r2" in node.value.lower() else "<inherited>",
            ),
        ]
    if isinstance(node, MappingNode):
        for key_node, value_node in node.value:
            if not isinstance(key_node, ScalarNode):
                entries.append(
                    (
                        key_node.start_mark.line + 1,
                        "unsupported_assignment_syntax",
                        "fail_closed",
                    )
                )
                continue
            if key_node.value == "<<":
                entries.extend(normalize_environment_node(value_node))
                continue
            value = (
                value_node.value.lower()
                if isinstance(value_node, ScalarNode)
                and not value_node.tag.endswith(":null")
                else "<inherited>"
            )
            entries.append(
                (
                    key_node.start_mark.line + 1,
                    normalized_config_key(key_node.value),
                    value,
                )
            )
        return entries
    if not isinstance(node, SequenceNode):
        return entries
    for item in node.value:
        if isinstance(item, ScalarNode):
            key, separator, raw_value = item.value.partition("=")
            if not separator and ("${" in item.value or "{{" in item.value):
                entries.extend(
                    (
                        (
                            item.start_mark.line + 1,
                            "unresolved_environment_source",
                            "fail_closed",
                        ),
                        (
                            item.start_mark.line + 1,
                            "artifact_provider_profile",
                            "r2" if "r2" in item.value.lower() else "<inherited>",
                        ),
                    )
                )
                continue
            entries.append(
                (
                    item.start_mark.line + 1,
                    normalized_config_key(key),
                    raw_value.lower() if separator else "<inherited>",
                )
            )
        elif isinstance(item, MappingNode):
            values = {key.value: value for key, value in item.value}
            name_node = values.get("name")
            if isinstance(name_node, ScalarNode):
                value_node = values.get("value")
                value = (
                    value_node.value.lower()
                    if isinstance(value_node, ScalarNode)
                    else "<inherited>"
                )
                entries.append(
                    (
                        name_node.start_mark.line + 1,
                        normalized_config_key(name_node.value),
                        value,
                    )
                )
            else:
                entries.extend(normalize_environment_node(item))
    return entries


def merge_entries(
    inherited: tuple[tuple[int, str, str], ...] | list[tuple[int, str, str]],
    direct: list[tuple[int, str, str]],
) -> list[tuple[int, str, str]]:
    """Apply child override semantics while resolving inherited bare exports."""
    merged = {key: (line, key, value) for line, key, value in inherited}
    for line, key, value in direct:
        if value == "<inherited>" and key in merged:
            continue
        merged[key] = (line, key, value)
    return list(merged.values())


def logical_lines(text: str) -> list[tuple[int, str]]:
    """Join backslash continuations while retaining the first source line."""
    lines: list[tuple[int, str]] = []
    start = 1
    current = ""
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not current:
            start = line_number
        current += raw_line.rstrip().removesuffix("\\").strip() + " "
        if not raw_line.rstrip().endswith("\\"):
            lines.append((start, current.strip()))
            current = ""
    if current:
        lines.append((start, current.strip()))
    return lines


def assignment_tokens(text: str, line_number: int) -> list[tuple[int, str, str]]:
    """Parse shell-compatible assignment lists including inherited bare keys."""
    try:
        tokens = shlex.split(text, comments=True, posix=True)
    except ValueError:
        return [(line_number, "unsupported_assignment_syntax", "fail_closed")]
    entries: list[tuple[int, str, str]] = []
    if len(tokens) >= 2 and "=" not in tokens[0] and not all("=" in token for token in tokens):
        return [(line_number, tokens[0].lower(), " ".join(tokens[1:]).lower())]
    for token in tokens:
        key, separator, value = token.partition("=")
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", key):
            entries.append(
                (
                    line_number,
                    normalized_config_key(key),
                    value.lower() if separator else "<inherited>",
                )
            )
    return entries


def env_command_entries(text: str, line_number: int) -> list[tuple[int, str, str]]:
    """Parse leading assignments from an ``env`` command invocation."""
    try:
        tokens = shlex.split(text, comments=True, posix=True)
    except ValueError:
        return [(line_number, "unsupported_assignment_syntax", "fail_closed")]
    if not tokens or tokens[0] != "env":
        return []
    entries: list[tuple[int, str, str]] = []
    for token in tokens[1:]:
        if token.startswith("-"):
            continue
        if "=" not in token:
            break
        entries.extend(assignment_tokens(token, line_number))
    return entries


def docker_secret_mount_entries(
    text: str,
    line_number: int,
) -> list[tuple[int, str, str]]:
    """Expose Docker BuildKit secret IDs to the credential-policy scanner."""
    entries: list[tuple[int, str, str]] = []
    for match in re.finditer(r"--mount=(?:\"([^\"]+)\"|'([^']+)'|(\S+))", text):
        mount = next(value for value in match.groups() if value is not None)
        options = {}
        for option in mount.split(","):
            key, separator, value = option.partition("=")
            if separator:
                options[normalized_config_key(key)] = value
        if normalized_config_key(options.get("type", "")) != "secret":
            continue
        secret_id = options.get("id") or options.get("source")
        if secret_id:
            entries.append(
                (line_number, normalized_config_key(secret_id), "<secret-mount>")
            )
    return entries


def dockerfile_config_scopes(text: str) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize Docker ENV instructions independently for each build stage."""
    scopes: dict[str, list[tuple[int, str, str]]] = {"global": []}
    named_stages: dict[str, str] = {}
    stage = "global"
    stage_index = 0
    for line_number, line in logical_lines(text):
        if not line or line.startswith("#"):
            continue
        from_match = re.match(r"FROM\s+(\S+)(?:\s+AS\s+(\S+))?", line, re.IGNORECASE)
        if from_match:
            stage_index += 1
            source, alias = from_match.groups()
            stage_name = alias.lower() if alias else str(stage_index)
            stage = f"stage:{stage_name}"
            parent_stage = named_stages.get(source.lower())
            scopes[stage] = list(scopes.get(parent_stage or "", []))
            if alias:
                named_stages[alias.lower()] = stage
            continue
        env_match = re.match(r"ENV\s+(.+)$", line, re.IGNORECASE)
        if env_match:
            scopes[stage] = merge_entries(
                scopes[stage],
                assignment_tokens(env_match.group(1), line_number),
            )
            continue
        arg_match = re.match(r"ARG\s+(.+)$", line, re.IGNORECASE)
        if arg_match:
            scopes[stage] = merge_entries(
                scopes[stage],
                assignment_tokens(arg_match.group(1), line_number),
            )
            continue
        run_match = re.match(r"RUN\s+(.+)$", line, re.IGNORECASE)
        if run_match:
            scopes[stage] = merge_entries(
                scopes[stage],
                env_command_entries(run_match.group(1), line_number)
                + docker_secret_mount_entries(run_match.group(1), line_number),
            )
    return list(scopes.items())


def env_config_scopes(text: str) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize dotenv assignments, treating bare keys as inherited inputs."""
    entries: list[tuple[int, str, str]] = []
    for line_number, line in logical_lines(text):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        stripped = re.sub(r"^export\s+", "", stripped)
        parsed = assignment_tokens(stripped, line_number)
        entries = merge_entries(entries, parsed)
    return [("root", entries)]


def shell_config_scopes(text: str) -> list[tuple[str, list[tuple[int, str, str]]]]:
    """Normalize exported shell assignments independently for each function."""
    control_flow = next(
        (
            line_number
            for line_number, line in enumerate(text.splitlines(), start=1)
            if re.match(r"\s*(?:if|then|elif|else|fi|case|esac|for|while|until|do|done)\b", line)
        ),
        None,
    )
    if control_flow is not None and re.search(r"\br2\b", text, re.IGNORECASE):
        return [
            (
                "unsupported-control-flow",
                [
                    (control_flow, "unsupported_control_flow", "fail_closed"),
                    (control_flow, "artifact_provider_profile", "r2"),
                ],
            )
        ]
    scopes: dict[str, list[tuple[int, str, str]]] = {"root": []}
    functions: dict[str, list[tuple[int, str, str]]] = {}
    calls: list[str] = []
    scope = "root"
    pending_function: str | None = None
    for line_number, line in logical_lines(text):
        declaration_only = re.fullmatch(
            r"(?:function\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*\(\))?|"
            r"([A-Za-z_][A-Za-z0-9_]*)\s*\(\))",
            line,
        )
        if declaration_only:
            pending_function = (declaration_only.group(1) or declaration_only.group(2)).lower()
            continue
        if line == "{" and pending_function:
            scope = f"function:{pending_function}"
            scopes[scope] = []
            functions[pending_function] = scopes[scope]
            pending_function = None
            continue
        function_match = re.match(
            r"(?:function\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(\))?\s*\{",
            line,
        )
        if function_match:
            function_name = function_match.group(1).lower()
            scope = f"function:{function_name}"
            scopes[scope] = []
            functions[function_name] = scopes[scope]
            line = line[function_match.end() :].strip()
        closes_function = line.endswith("}")
        if closes_function:
            line = line[:-1].rstrip("; ")
        if not line and closes_function:
            function_name = scope.removeprefix("function:")
            functions[function_name] = list(scopes[scope])
            scope = "root"
            continue
        for statement in (part.strip() for part in re.split(r"[;&]+", line)):
            if not statement:
                continue
            export_match = re.fullmatch(r"export\s+(.+)", statement)
            if export_match:
                scopes[scope] = merge_entries(
                    scopes[scope],
                    assignment_tokens(export_match.group(1), line_number),
                )
                continue
            if re.match(r"[A-Za-z_][A-Za-z0-9_]*=", statement):
                scopes[scope] = merge_entries(
                    scopes[scope],
                    assignment_tokens(statement, line_number),
                )
                continue
            env_entries = env_command_entries(statement, line_number)
            if env_entries:
                scopes[scope] = merge_entries(scopes[scope], env_entries)
                continue
            source_match = re.match(r"(?:\.|source)\s+(.+)$", statement)
            if source_match:
                source = source_match.group(1)
                source_entries = [
                    (line_number, "unresolved_environment_source", "fail_closed")
                ]
                if "r2" in source.lower():
                    source_entries.append(
                        (line_number, "artifact_provider_profile", "r2")
                    )
                scopes[scope] = merge_entries(scopes[scope], source_entries)
                continue
            try:
                command = shlex.split(statement, comments=True, posix=True)
            except ValueError:
                command = []
            if scope == "root" and command and command[0] in functions:
                calls.append(command[0])
        if closes_function:
            function_name = scope.removeprefix("function:")
            functions[function_name] = list(scopes[scope])
            scope = "root"
    execution_state = list(scopes["root"])
    for index, function_name in enumerate(calls, start=1):
        execution_state = merge_entries(execution_state, functions[function_name])
        scopes[f"execution:{index}:{function_name}"] = list(execution_state)
    return list(scopes.items())


def normalized_config_key(key: str) -> str:
    """Normalize camelCase and common namespace separators to snake case."""
    snake = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", key)
    return re.sub(r"_+", "_", re.sub(r"[.\s-]+", "_", snake)).strip("_").lower()


def key_has_suffix(key: str, suffixes: set[str]) -> bool:
    """Match canonical and namespaced configuration keys."""
    normalized = normalized_config_key(key)
    return normalized in suffixes or any(
        normalized.endswith(f"_{suffix}") for suffix in suffixes
    )


def credential_key_is_forbidden(key: str) -> bool:
    """Return whether a key carries a forbidden R2 credential or source."""
    normalized = normalized_config_key(key)
    if normalized.startswith("minio_"):
        return False
    source_key = key_has_suffix(key, R2_FORBIDDEN_CREDENTIAL_SOURCE_KEYS)
    exact_static_key = normalized in R2_STATIC_CREDENTIAL_KEYS
    namespaced_static_key = (
        any(token in normalized.split("_") for token in {"artifact", "aws", "r2"})
        and key_has_suffix(key, R2_STATIC_CREDENTIAL_KEYS)
    )
    return source_key or exact_static_key or namespaced_static_key


def provider_selector_key(key: str) -> bool:
    """Return whether a key selects the artifact storage provider profile."""
    normalized = normalized_config_key(key)
    return normalized in R2_PROVIDER_SELECTOR_KEYS or normalized.endswith(
        tuple(f"_{suffix}" for suffix in R2_PROVIDER_SELECTOR_KEYS)
    )


def unresolved_artifact_provider(key: str, value: str) -> bool:
    """Recognize unresolved selectors only for the artifact/storage namespace."""
    normalized = normalized_config_key(key)
    selector = provider_selector_key(normalized)
    artifact_namespace = any(
        token in normalized.split("_") for token in {"artifact", "storage", "workstream"}
    )
    minio_default = bool(re.search(r":-\s*minio\s*}", value, re.IGNORECASE))
    unresolved = value == "<inherited>" or any(
        marker in value for marker in ("$", "{{", "var.")
    )
    return selector and artifact_namespace and unresolved and not minio_default


def static_credential_mode(key: str, value: str) -> bool:
    """Reject static mode only when the key actually controls credentials."""
    key = normalized_config_key(key)
    return (
        key == "credential_mode" or key.endswith("_credential_mode")
    ) and value in {"static", "local_static", "long_lived", "long-lived"}


def r2_scope_failures(
    relative_path: str,
    text: str,
    scopes: list[tuple[str, list[tuple[int, str, str]]]],
) -> list[str]:
    """Return one failure for each structured R2 scope using static credentials."""
    failures: list[str] = []
    seen: set[tuple[int, str]] = set()
    path_context = bool(
        re.search(r"(?:^|[/_.-])r2(?:[/_.-]|$)", relative_path, re.IGNORECASE)
    )
    path_is_issuer = "issuer" in re.split(r"[/_.-]+", relative_path.lower())
    for scope_name, entries in scopes:
        scope_text = " ".join(
            [scope_name, *(f"{key}={value}" for _, key, value in entries)]
        )
        explicit_non_r2 = any(
            (
                value in {"minio", "local"}
                or bool(re.search(r":-\s*(?:minio|local)\s*}", value, re.IGNORECASE))
            )
            and provider_selector_key(key)
            for _, key, value in entries
        )
        unresolved_provider = any(
            unresolved_artifact_provider(key, value)
            for _, key, value in entries
        )
        normalized_scope = normalized_config_key(scope_name)
        scope_is_issuer = path_is_issuer or "issuer" in normalized_scope.split("_")
        is_r2 = bool(
            (path_context and not explicit_non_r2)
            or
            re.search(r"\bcloudflare[_-]?r2\b", scope_text)
            or "r2" in normalized_scope.split("_")
            or ".r2.cloudflarestorage.com" in scope_text
            or any(
                value in {"r2", "cloudflare_r2", "cloudflare-r2"}
                and provider_selector_key(key)
                for _, key, value in entries
            )
            or unresolved_provider
            or any(
                "r2" in normalized_config_key(key).split("_")
                and credential_key_is_forbidden(key)
                for _, key, _ in entries
            )
        )
        if not is_r2:
            continue
        parse_entries = [
            (line_number, key)
            for line_number, key, value in entries
            if key in {"unsupported_assignment_syntax", "unsupported_control_flow"}
            and value == "fail_closed"
        ]
        if parse_entries:
            failure_line = parse_entries[0][0]
            key = (failure_line, "R2_CONFIG_PARSE_ERROR")
            if key not in seen:
                seen.add(key)
                failures.append(f"{relative_path}:{failure_line}: {key[1]}")
            continue
        static_entries = [
            (line_number, key, value)
            for line_number, key, value in entries
            if static_credential_mode(key, value)
            or (key == "unresolved_environment_source" and value == "fail_closed")
            or (
                credential_key_is_forbidden(key)
                and not (
                    key_has_suffix(key, {"r2_parent_secret"})
                    and scope_is_issuer
                )
                and value not in {"none", "null"}
            )
            or (
                key_has_suffix(key, R2_ISOLATED_CONFIG_SOURCE_KEYS)
                and value not in {"", "none", "null", "/dev/null"}
            )
        ]
        if static_entries:
            line = next(
                (
                    index
                    for index, raw_line in enumerate(text.splitlines(), start=1)
                    if static_entries[0][1].lower() in raw_line.lower()
                ),
                1,
            )
            failure_line = static_entries[0][0] or line
            key = (failure_line, "R2_STATIC_PRODUCTION_CREDENTIALS")
            if key not in seen:
                seen.add(key)
                failures.append(f"{relative_path}:{failure_line}: {key[1]}")
    return failures


def project_manager_action_denied(fragment: str) -> bool:
    """Return true only when negation directly removes retry authority."""
    if re.search(
        r"\b(?:may|can|is\s+(?:allowed|permitted)\s+to)\b[^.!?]{0,30}"
        r"(?:continue|resume|retry|restart|re-?run)",
        fragment,
        re.IGNORECASE,
    ) or re.search(r"\bnot\s+(?:prohibited|blocked)\b", fragment, re.IGNORECASE):
        return False
    return bool(
        re.search(
            r"Project Manager[^.!?]{0,40}"
            r"(?:cannot|can't|must\s+not|may\s+not|never|"
            r"is\s+(?:not\s+(?:allowed|permitted)|prohibited)\s+(?:to|from))"
            r"[^.!?]{0,40}(?:continue|resume|retry|restart|re-?run)",
            fragment,
            re.IGNORECASE,
        )
    )


def git_lines(root: Path, *args: str) -> list[str]:
    """Return non-empty path lines from Git."""
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if line]


def discover_paths(root: Path = ROOT) -> list[Path]:
    """Discover tracked and untracked active text files."""
    relative_paths = git_lines(root, "ls-files")
    relative_paths.extend(git_lines(root, "ls-files", "--others", "--exclude-standard"))
    paths: list[Path] = []
    for relative_path in dict.fromkeys(relative_paths):
        if not path_is_scannable(relative_path):
            continue
        path = root / relative_path
        if path.is_file():
            paths.append(path)
    return paths


def scan(root: Path = ROOT, phase: str | None = None) -> list[str]:
    """Scan the repository at an explicitly validated artifact phase."""
    if phase is None:
        phase = ARTIFACT_CONTRACT_PHASE
    phase_index(phase)
    failures: list[str] = []
    for path in discover_paths(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            failures.append(f"{path.relative_to(root).as_posix()}:0: UNREADABLE_TEXT")
            continue
        failures.extend(scan_text(path.relative_to(root).as_posix(), text, phase))
    return failures


def main() -> int:
    """Run the phased stale artifact contract check."""
    try:
        failures = scan()
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"Stale artifact contract check failed closed: {exc}", file=sys.stderr)
        return 1

    if failures:
        print(
            f"Stale artifact contract check failed at phase {ARTIFACT_CONTRACT_PHASE}:",
            file=sys.stderr,
        )
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"Stale artifact contract check passed at phase {ARTIFACT_CONTRACT_PHASE}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
