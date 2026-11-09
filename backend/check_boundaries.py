"""Verifica dependências e responsabilidades sem carregar configuração/banco."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "app"
ALLOWED = {
    "management": {"catalog", "operations"},
    "operations": {"catalog", "auxiliaries"},
    "catalog": {"auxiliaries"},
}


def dependencies(name, node, known, package=False):
    """Resolve também imports relativos e aliases para o grafo de arquivos locais."""
    if isinstance(node, ast.Import):
        candidates = [alias.name for alias in node.names]
    elif isinstance(node, ast.ImportFrom):
        parts = name.split(".") if package else name.split(".")[:-1]
        base = parts[: len(parts) - node.level + 1] if node.level else []
        module = ".".join([*base, *([node.module] if node.module else [])])
        candidates = [module, *(module + "." + alias.name for alias in node.names)]
    else:
        return []
    return [candidate for candidate in candidates if candidate in known and candidate != name]


def violations():
    errors = []
    paths = list(ROOT.rglob("*.py"))
    names = {
        path: (
            "app." + path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
        ).removesuffix(".__init__")
        for path in paths
    }
    known = set(names.values())
    graph = {}
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"))
        targets = {
            target
            for node in ast.walk(tree)
            for target in dependencies(names[path], node, known, path.name == "__init__.py")
        }
        graph[names[path]] = targets
        owner = relative.split("/")[1] if relative.startswith("modules/") else None
        for target in targets:
            parts = target.split(".")
            if len(parts) > 3 and parts[1] == "modules" and owner and parts[2] != owner:
                if parts[2] not in ALLOWED.get(owner, set()) or parts[3:] != ["public"]:
                    errors.append(
                        f"{relative}: dependência entre capacidades não permitida: {target}"
                    )
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
    active, done = set(), set()

    def visit(name, trace):
        if name in active:
            errors.append("Ciclo: " + " -> ".join([*trace, name]))
            return
        if name in done:
            return
        active.add(name)
        for target in sorted(graph.get(name, [])):
            visit(target, [*trace, name])
        active.remove(name)
        done.add(name)

    for name in sorted(graph):
        visit(name, [])
    return errors


if __name__ == "__main__":
    errors = violations()
    if errors:
        raise SystemExit("\n".join(errors))
    print("Fronteiras de HTTP, aplicação e domínio verificadas.")
