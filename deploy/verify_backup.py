"""Ensaia restauração apenas em container rotulado e banco de teste vazio.

Não é o comando de restauração de produção. Arquivos são extraídos em destino
local novo, sem links, caminhos absolutos ou travessia de diretórios.
"""

import argparse
import hashlib
import json
import subprocess
import tarfile
import time
from pathlib import Path, PurePosixPath


def verify(source, container, photos):
    started = time.perf_counter()
    source, photos = Path(source).resolve(), Path(photos).resolve()
    if (source / "INCOMPLETE").exists() or photos.exists():
        raise RuntimeError("Backup incompleto ou destino de fotos já existente")
    manifest = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    tables = {
        "receipts": "requests",
        "operations": "operations",
        "revisions": "revisions",
        "movements": "movements",
        "photos": "photos",
        "products": "products",
        "variants": "variants",
        "auxiliaries": "auxiliaries",
        "control": "control",
    }
    if set(manifest["counts"]) != set(tables):
        raise RuntimeError("Manifesto com tabelas não reconhecidas")
    for name in ("database.dump", "uploads.tar"):
        with (source / name).open("rb") as file:
            if hashlib.file_digest(file, "sha256").hexdigest() != manifest["files"][name]:
                raise RuntimeError("Integridade do backup inválida")
    target = json.loads(subprocess.check_output(["docker", "inspect", container], text=True))[0]
    if target.get("Config", {}).get("Labels", {}).get("com.lgd.purpose") != "restore-drill":
        raise RuntimeError("Destino não é o container explicitamente rotulado restore-drill")
    command = ["docker", "exec", "-i", container]
    psql = [*command, "psql", "-U", "postgres", "-d", "lgd_mantos_alignment_test", "-Atc"]
    if (
        subprocess.check_output(
            [*psql, "SELECT count(*) FROM pg_tables WHERE schemaname='public'"], text=True
        ).strip()
        != "0"
    ):
        raise RuntimeError("A base de restauração deve estar vazia; nenhum dado foi alterado")
    # Validar todos os membros antes de escrever qualquer arquivo.
    with tarfile.open(source / "uploads.tar", "r:") as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
                raise RuntimeError("Membro inseguro no arquivo de fotos")
            if not photos.joinpath(*path.parts).resolve().is_relative_to(photos):
                raise RuntimeError("Arquivo fora do diretório de restauração")
        photos.mkdir(parents=True)
        for member in members:
            target_path = photos.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                target_path.mkdir(parents=True, exist_ok=True)
            else:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                with archive.extractfile(member) as incoming, target_path.open("xb") as outgoing:
                    import shutil

                    shutil.copyfileobj(incoming, outgoing)
    with (source / "database.dump").open("rb") as dump:
        subprocess.run(
            [
                *command,
                "pg_restore",
                "--exit-on-error",
                "--no-owner",
                "--no-privileges",
                "-U",
                "postgres",
                "-d",
                "lgd_mantos_alignment_test",
            ],
            stdin=dump,
            check=True,
        )
    counts = {}
    for key, table in tables.items():
        counts[key] = int(
            subprocess.check_output([*psql, f"SELECT count(*) FROM lgd_{table}"], text=True)
        )
    if counts != manifest["counts"]:
        raise RuntimeError("Contagens restauradas divergem do manifesto")
    filenames = subprocess.check_output(
        [*psql, "SELECT filename FROM lgd_photos ORDER BY filename"], text=True
    ).splitlines()
    for filename in filenames:
        if Path(filename).name != filename or not (photos / "products" / filename).is_file():
            raise RuntimeError("Foto referenciada ausente na restauração")
    revision = subprocess.check_output(
        [*psql, "SELECT version_num FROM alembic_version"], text=True
    ).strip()
    return {
        "counts": counts,
        "migration": revision,
        "photo_references_checked": len(filenames),
        "duration_seconds": round(time.perf_counter() - started, 2),
        "isolated": True,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--database-container", required=True)
    parser.add_argument("--photos-destination", required=True)
    args = parser.parse_args()
    print(
        json.dumps(verify(args.source, args.database_container, args.photos_destination), indent=2)
    )
