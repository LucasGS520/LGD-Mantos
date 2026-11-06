"""Executa a suíte somente no banco PostgreSQL dedicado à verificação.

Uso local: python backend/check.py. O banco lgd_mantos_alignment_test precisa
existir. Credenciais são lidas do ambiente/.env sem aparecer na linha de comando.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from dotenv import dotenv_values


def main():
    root = Path(__file__).resolve().parent.parent
    config = {**dotenv_values(root / ".env"), **os.environ}
    configured = config.get("TEST_DATABASE_URL")
    if not configured:
        source = urlsplit(config["DATABASE_URL"])
        host = "localhost:55432" if source.hostname == "db" else source.netloc.split("@")[-1]
        credentials = source.netloc.rsplit("@", 1)[0]
        configured = urlunsplit((source.scheme, credentials + "@" + host, "/lgd_mantos_alignment_test", "", ""))
    if urlsplit(configured).path != "/lgd_mantos_alignment_test":
        raise RuntimeError("Banco de testes inválido")
    env = {**os.environ, "TEST_DATABASE_URL": configured}
    if "--serve" in sys.argv:
        env.update(DATABASE_URL=configured, APP_PASSWORD="senha-testes", APP_SECRET="segredo-exclusivo-de-testes",
                   CORS_ORIGINS="http://127.0.0.1:5174,http://localhost:5174")
        with tempfile.TemporaryDirectory(prefix="lgd-browser-photos-") as folder:
            env["PHOTO_ROOT"] = folder
            result = subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8001"], cwd=root / "backend", env=env)
        raise SystemExit(result.returncode)
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", *sys.argv[1:]], cwd=root / "backend", env=env)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
