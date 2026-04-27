"""Lecture des credentials jeedom-audit depuis ~/.config/jeedom-audit/credentials.json."""

import json
import os
import stat
import sys
from pathlib import Path

CREDENTIALS_PATH = Path.home() / ".config" / "jeedom-audit" / "credentials.json"

DEFAULTS = {
    "preferred_mode": "auto",
    "ssh_alias": "Jeedom",
    "db_name": "jeedom",
    "db_user": "jeedom_audit_ro",
    "db_password_source": "remote_mycnf",
    "api_url": "",
    "api_key": "",
}

ENV_MAP = {
    "JEEDOM_SSH_ALIAS": "ssh_alias",
    "JEEDOM_DB_NAME": "db_name",
    "JEEDOM_DB_USER": "db_user",
    "JEEDOM_DB_PASSWORD_SOURCE": "db_password_source",
    "JEEDOM_API_URL": "api_url",
    "JEEDOM_API_KEY": "api_key",
    "JEEDOM_PREFERRED_MODE": "preferred_mode",
}


def _check_permissions(path: Path) -> None:
    mode = path.stat().st_mode
    if mode & (stat.S_IRGRP | stat.S_IROTH):
        print(
            f"[AVERTISSEMENT] {path} est lisible par d'autres utilisateurs (permissions {oct(mode & 0o777)}). "
            "Exécutez : chmod 600 ~/.config/jeedom-audit/credentials.json",
            file=sys.stderr,
        )


def load() -> dict:
    """Retourne le dict de credentials avec overrides env vars.

    Lance sys.exit si le fichier est absent (invite à lancer setup).
    """
    if not CREDENTIALS_PATH.exists():
        print(
            f"[ERREUR] Credentials introuvables : {CREDENTIALS_PATH}\n"
            "Lancez la configuration initiale : python3 scripts/setup.py",
            file=sys.stderr,
        )
        sys.exit(1)

    _check_permissions(CREDENTIALS_PATH)

    with CREDENTIALS_PATH.open() as f:
        creds = json.load(f)

    result = {**DEFAULTS, **creds}

    for env_key, cred_key in ENV_MAP.items():
        if value := os.environ.get(env_key):
            result[cred_key] = value

    return result
