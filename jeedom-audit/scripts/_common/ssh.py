"""Wrapper SSH unifié — jamais de password en argument CLI."""

import subprocess
from dataclasses import dataclass


@dataclass
class SSHResult:
    stdout: str
    stderr: str
    returncode: int

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(
    alias: str,
    command: str,
    timeout: int = 30,
    retries: int = 1,
) -> SSHResult:
    """Exécute une commande sur l'hôte SSH `alias`.

    Le `~/.my.cnf` côté serveur fournit les credentials MySQL —
    aucun password n'est passé en argument.
    """
    last_result = None
    for attempt in range(retries + 1):
        try:
            proc = subprocess.run(
                ["ssh", alias, command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            last_result = SSHResult(
                stdout=proc.stdout,
                stderr=proc.stderr.strip(),
                returncode=proc.returncode,
            )
            if last_result.ok:
                return last_result
        except subprocess.TimeoutExpired:
            last_result = SSHResult(
                stdout="",
                stderr=f"Timeout après {timeout}s (tentative {attempt + 1}/{retries + 1})",
                returncode=124,
            )

    return last_result


def mysql(
    alias: str,
    db: str,
    query: str,
    timeout: int = 30,
    retries: int = 1,
) -> SSHResult:
    """Exécute une requête MySQL via SSH.

    Utilise le format `--batch --skip-column-names` pour un output parseable,
    et `2>/dev/null` pour supprimer les warnings MySQL bénins.
    """
    escaped = query.replace("'", "'\\''")
    command = f"mysql {db} --batch --skip-column-names -e '{escaped}' 2>/dev/null"
    return run(alias, command, timeout=timeout, retries=retries)


def mysql_json(
    alias: str,
    db: str,
    query: str,
    timeout: int = 30,
) -> SSHResult:
    """Exécute une requête MySQL et retourne les résultats en JSON via python3 côté serveur."""
    escaped = query.replace('"', '\\"').replace("'", "'\\''")
    command = (
        f"mysql {db} --batch -e '{escaped}' 2>/dev/null "
        f"| python3 -c \""
        f"import sys, json, csv; "
        f"rows = list(csv.DictReader(sys.stdin, delimiter='\\t')); "
        f"print(json.dumps(rows))\""
    )
    return run(alias, command, timeout=timeout)
