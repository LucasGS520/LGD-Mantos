"""Captura consistente de banco e fotos com API comprovadamente parada.

Não reinicia serviços, não apaga dados e não restaura sobre uma base existente.
O diretório criado deve ser copiado para destino externo seguro pelo operador.
"""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def capture(compose, destination, database="lgd_mantos"):
    if database not in {"lgd_mantos", "lgd_mantos_alignment_test"}:
        raise RuntimeError("Banco não reconhecido")
    destination = Path(destination).resolve()
    if destination.exists():
        raise RuntimeError("Use um destino novo; nenhum backup existente será sobrescrito")
    backend = subprocess.check_output([*compose, "ps", "-a", "-q", "backend"], text=True).strip()
    if not backend or len(backend.splitlines()) != 1:
        raise RuntimeError("É necessário identificar exatamente um container backend")
    state = json.loads(subprocess.check_output(["docker", "inspect", backend], text=True))[0]
    if state["State"]["Running"]:
        raise RuntimeError("Pare o backend antes da captura para suspender banco e fotos")
    destination.mkdir(parents=True)
    try:
        with (destination / "database.dump").open("wb") as output:
            subprocess.run(
                [*compose, "exec", "-T", "db", "pg_dump", "-U", "postgres", "-d", database, "-Fc"],
                stdout=output,
                check=True,
            )
        # docker cp funciona com o backend parado, sem iniciar API ou migração.
        with (destination / "uploads.tar").open("wb") as output:
            subprocess.run(
                ["docker", "cp", backend + ":/app/app/static/uploads/.", "-"],
                stdout=output,
                check=True,
            )
        digests = {}
        for name in ("database.dump", "uploads.tar"):
            with (destination / name).open("rb") as source:
                digests[name] = hashlib.file_digest(source, "sha256").hexdigest()
        counts = json.loads(
            subprocess.check_output(
                [
                    *compose,
                    "exec",
                    "-T",
                    "db",
                    "psql",
                    "-U",
                    "postgres",
                    "-d",
                    database,
                    "-Atc",
                    "SELECT json_build_object('operations',(SELECT count(*) FROM lgd_operations),'revisions',(SELECT count(*) FROM lgd_revisions),'movements',(SELECT count(*) FROM lgd_movements),'receipts',(SELECT count(*) FROM lgd_requests),'photos',(SELECT count(*) FROM lgd_photos),'products',(SELECT count(*) FROM lgd_products),'variants',(SELECT count(*) FROM lgd_variants),'auxiliaries',(SELECT count(*) FROM lgd_auxiliaries),'control',(SELECT count(*) FROM lgd_control))",
                ],
                text=True,
            )
        )
        manifest = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "backend_image": state["Image"],
            "writes_suspended": True,
            "database": database,
            "counts": counts,
            "files": digests,
        }
        (destination / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    except BaseException:
        (destination / "INCOMPLETE").write_text(
            "Captura incompleta; não usar para restauração", encoding="utf-8"
        )
        raise
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compose-file", default="docker-compose.prod.yml")
    parser.add_argument("--destination", required=True)
    parser.add_argument(
        "--database", default="lgd_mantos", choices=["lgd_mantos", "lgd_mantos_alignment_test"]
    )
    args = parser.parse_args()
    print(
        json.dumps(
            capture(
                ["docker", "compose", "-f", args.compose_file], args.destination, args.database
            ),
            indent=2,
        )
    )
