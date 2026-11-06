"""Verifica dependências e responsabilidades sem carregar configuração/banco."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "app"


def violations():
    errors = []
    for path in ROOT.rglob("*.py"):
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.ImportFrom, ast.Import)):
                modules = (
                    [node.module or ""]
                    if isinstance(node, ast.ImportFrom)
                    else [alias.name for alias in node.names]
                )
                for module in modules:
                    if "/domain/" in relative and (
                        module.split(".")[0] in {"fastapi", "sqlalchemy", "PIL", "os", "pathlib"}
                        or module in {"app.core.config", "app.shared.models.entities"}
                    ):
                        errors.append(f"{relative}: domínio puro importa {module}")
                    if (
                        relative.startswith("modules/")
                        and not relative.endswith(("router.py", "routes.py", "schemas.py"))
                        and module.startswith("fastapi")
                    ):
                        errors.append(f"{relative}: aplicação depende de HTTP")
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("app.domain"):
                    errors.append(f"{relative}: dependência do módulo antigo")
                if module.endswith(".router") or module.endswith(".routes"):
                    errors.append(f"{relative}: módulo importa router de outro módulo")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if relative.endswith(("router.py", "routes.py")) and node.func.attr in {
                    "commit",
                    "rollback",
                    "execute",
                    "scalar",
                    "scalars",
                    "flush",
                    "write_bytes",
                    "unlink",
                }:
                    errors.append(f"{relative}:{node.lineno}: infraestrutura na borda HTTP")
    return errors


if __name__ == "__main__":
    errors = violations()
    if errors:
        raise SystemExit("\n".join(errors))
    print("Fronteiras de HTTP, aplicação e domínio verificadas.")
