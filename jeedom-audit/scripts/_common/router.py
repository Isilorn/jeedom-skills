"""Couche de routage transparent MySQL/API pour jeedom-audit.

Choisit le vecteur d'accès (mysql, api, ssh) selon l'opération,
le preferred_mode configuré et les capacités détectées (lazy, mis en cache).
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _common import ssh as _ssh
import api_call as _api_call

# Cache session — clé (ssh_alias, api_url) → {"mysql": bool, "api": bool}
_CAPS_CACHE: dict[tuple[str, str], dict[str, bool]] = {}

# Routage par opération : vecteur préféré + fallback éventuel
_ROUTING_TABLE: dict[str, dict[str, str | None]] = {
    "structural_audit": {"preferred": "mysql", "fallback": "api"},
    "runtime_state":    {"preferred": "api",   "fallback": None},
    "history":          {"preferred": "api",   "fallback": "mysql"},
    "statistics":       {"preferred": "api",   "fallback": None},
    "logs":             {"preferred": "ssh",   "fallback": None},
    "version_check":    {"preferred": "api",   "fallback": "mysql"},
    "plugin_list":      {"preferred": "api",   "fallback": "mysql"},
    "resolve_refs":     {"preferred": "mysql", "fallback": "api"},
}

# Opérations intrinsèquement API-only (données absentes de MySQL)
_API_ONLY_OPS: frozenset[str] = frozenset({"runtime_state", "statistics"})


def detect_capabilities(creds: dict) -> dict[str, bool]:
    """Retourne {"mysql": bool, "api": bool} — résultat mis en cache session."""
    key = (creds.get("ssh_alias", ""), creds.get("api_url", ""))
    if key in _CAPS_CACHE:
        return _CAPS_CACHE[key]

    mysql_ok = False
    try:
        result = _ssh.mysql_json(
            alias=creds.get("ssh_alias", "Jeedom"),
            db=creds.get("db_name", "jeedom"),
            query="SELECT 1 AS ok",
            timeout=10,
        )
        mysql_ok = result.ok
    except Exception:
        mysql_ok = False

    api_ok = False
    try:
        response = _api_call.run("ping", creds=creds, timeout=5)
        api_ok = "error" not in response
    except Exception:
        api_ok = False

    caps = {"mysql": mysql_ok, "api": api_ok}
    _CAPS_CACHE[key] = caps
    return caps


def _cap_available(vector: str, caps: dict[str, bool]) -> bool:
    """mysql et ssh requièrent tous deux l'accès SSH."""
    if vector == "api":
        return caps.get("api", False)
    return caps.get("mysql", False)


def route(operation: str, creds: dict) -> str:
    """Retourne "mysql" | "api" | "ssh" selon l'opération et les capabilities."""
    preferred_mode = creds.get("preferred_mode", "auto")

    if preferred_mode == "api":
        return "ssh" if operation == "logs" else "api"

    if preferred_mode == "mysql":
        # Données runtime absentes de MySQL → API obligatoire
        if operation in _API_ONLY_OPS:
            return "api"
        if operation == "logs":
            return "ssh"
        return "mysql"

    # auto : routing table + capabilities détectées
    entry = _ROUTING_TABLE.get(operation, {"preferred": "mysql", "fallback": None})
    preferred = entry["preferred"]
    fallback = entry.get("fallback")
    caps = detect_capabilities(creds)

    if _cap_available(preferred, caps):
        return preferred
    if fallback and _cap_available(fallback, caps):
        return fallback
    # Retourner preferred même si indisponible — le caller gère l'erreur
    return preferred


def with_fallback(
    primary_fn: Callable[[], Any],
    fallback_fn: Callable[[], Any],
    mention: str,
) -> tuple[Any, str | None]:
    """Exécute primary_fn ; si échec → fallback_fn + retourne mention."""
    try:
        result = primary_fn()
    except Exception as exc:
        result = {"error": str(exc)}

    if isinstance(result, dict) and "error" in result:
        try:
            fallback_result = fallback_fn()
        except Exception as exc:
            fallback_result = {"error": str(exc)}
        return fallback_result, mention

    return result, None
