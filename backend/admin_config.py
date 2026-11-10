"""Configuração administrativa sem importar a aplicação ou criar engine de API."""

import os
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url


def environment():
    return {**dotenv_values(Path(__file__).resolve().parent.parent / ".env"), **os.environ}


def migration_url():
    config = environment()
    url = config.get("MIGRATION_DATABASE_URL")
    if not url:
        raise RuntimeError("Defina MIGRATION_DATABASE_URL com a credencial administrativa")
    parsed = make_url(url)
    if parsed.database not in {"lgd_mantos", "lgd_mantos_alignment_test"}:
        raise RuntimeError("Banco administrativo não reconhecido como LGD")
    runtime = config.get("DATABASE_URL")
    if runtime:
        target = make_url(runtime)
        if (parsed.host, parsed.port, parsed.database) != (
            target.host,
            target.port,
            target.database,
        ):
            raise RuntimeError("API e migração apontam para destinos diferentes")
    return url
