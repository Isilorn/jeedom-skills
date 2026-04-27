"""Détection de version Jeedom et application de la politique de compatibilité."""

import json
import sys
import urllib.request
import urllib.error
from functools import lru_cache

from . import credentials as _creds
from . import ssh as _ssh

# Cache de session — une seule détection par processus.
_cached_version: str | None = None


class VersionError(RuntimeError):
    pass


class VersionWarning(UserWarning):
    pass


def _parse(version_str: str) -> tuple[int, int]:
    """Extrait (majeur, mineur) depuis '4.5.2' ou '4.5'."""
    parts = version_str.strip().split(".")
    return int(parts[0]), int(parts[1])


def _via_api_jsonrpc(creds: dict) -> str | None:
    url = creds.get("api_url", "").rstrip("/") + "/core/api/jeeApi.php"
    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "version",
        "params": {"apikey": creds.get("api_key", "")},
        "id": 1,
    }).encode()
    try:
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get("result")
    except Exception:
        return None


def _via_mysql(creds: dict) -> str | None:
    result = _ssh.mysql(
        alias=creds["ssh_alias"],
        db=creds["db_name"],
        query="SELECT value FROM config WHERE plugin='core' AND `key`='version' LIMIT 1;",
        timeout=10,
    )
    if result.ok and result.stdout.strip():
        return result.stdout.strip()
    return None


def detect(creds: dict | None = None) -> str:
    """Retourne la version Jeedom sous forme de string (ex: '4.5.2').

    Ordre de tentative : API JSON-RPC → MySQL.
    Résultat mis en cache pour la session.
    """
    global _cached_version
    if _cached_version is not None:
        return _cached_version

    if creds is None:
        creds = _creds.load()

    version = _via_api_jsonrpc(creds) or _via_mysql(creds)

    if not version:
        raise VersionError(
            "Impossible de détecter la version Jeedom (API et MySQL inaccessibles). "
            "Vérifiez vos credentials dans ~/.config/jeedom-audit/credentials.json"
        )

    _cached_version = version
    return version


def check(creds: dict | None = None) -> str:
    """Détecte et applique la politique de version. Retourne la version si OK.

    Politique :
    - < 4.4  → VersionError (refus explicite)
    - 4.4    → VersionError (refus avec mention)
    - 4.5.x  → OK
    - ≥ 4.6  → VersionWarning + continue
    """
    version = detect(creds)
    major, minor = _parse(version)

    if major < 4 or (major == 4 and minor < 4):
        raise VersionError(
            f"Jeedom {version} non supporté. Cette skill requiert Jeedom ≥ 4.5. "
            "Mettez à jour votre installation."
        )

    if major == 4 and minor == 4:
        raise VersionError(
            f"Jeedom {version} non supporté. Cette skill requiert Jeedom 4.5. "
            "La version 4.4 présente des différences de schéma incompatibles."
        )

    if major > 4 or (major == 4 and minor >= 6):
        import warnings
        warnings.warn(
            f"Jeedom {version} détecté (schéma testé sur 4.5). "
            "Des divergences mineures sont possibles.",
            VersionWarning,
            stacklevel=2,
        )

    return version


def reset_cache() -> None:
    global _cached_version
    _cached_version = None
