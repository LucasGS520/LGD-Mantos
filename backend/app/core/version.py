"""Versão da API — fonte única de verdade.

Usada tanto em `FastAPI(version=...)` (main.py) quanto na resposta de `/health`,
evitando que a API relate versões diferentes de si mesma em lugares diferentes.
"""

API_VERSION = "3.0"
SCHEMA_REVISION = "0006"
