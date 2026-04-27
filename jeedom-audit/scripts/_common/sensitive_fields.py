"""Filtrage des champs sensibles à la sortie des wrappers db_query et api_call."""

import re

# Fragments de noms de champs sensibles — match insensible à la casse, partiel.
_SENSITIVE_PATTERNS: tuple[str, ...] = (
    "password",
    "passwd",
    "pwd",
    "pass",
    "apikey",
    "api_key",
    "token",
    "secret",
    "auth",
    "mqttpassword",
    "mqttpass",
    "credential",
)

_COMPILED = re.compile(
    "|".join(re.escape(p) for p in _SENSITIVE_PATTERNS),
    re.IGNORECASE,
)

REDACTED = "[FILTRÉ]"


def is_sensitive(field_name: str) -> bool:
    return bool(_COMPILED.search(field_name))


def filter_row(row: dict) -> tuple[dict, list[str]]:
    """Retourne (row_filtrée, liste_des_champs_filtrés)."""
    filtered: dict = {}
    redacted_fields: list[str] = []
    for key, value in row.items():
        if is_sensitive(key):
            filtered[key] = REDACTED
            redacted_fields.append(key)
        else:
            filtered[key] = value
    return filtered, redacted_fields


def filter_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Filtre une liste de rows, retourne (rows_filtrées, champs_filtrés_distincts)."""
    filtered_rows: list[dict] = []
    all_redacted: set[str] = set()
    for row in rows:
        filtered, redacted = filter_row(row)
        filtered_rows.append(filtered)
        all_redacted.update(redacted)
    return filtered_rows, sorted(all_redacted)
