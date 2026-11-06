import fs from "node:fs";
import path from "node:path";
import ts from "typescript";
const root = path.resolve("src");
function walk(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) =>
      entry.isDirectory()
        ? walk(path.join(dir, entry.name))
        : /\.tsx?$/.test(entry.name)
          ? [path.join(dir, entry.name)]
          : [],
    );
}
const files = walk(root),
  graph = new Map(),
  errors = [];
for (const file of files) {
  const code = fs.readFileSync(file, "utf8"),
    source = ts.createSourceFile(file, code, ts.ScriptTarget.Latest, true);
  const edges = [];
  for (const statement of source.statements) {
    if (
      !ts.isImportDeclaration(statement) &&
      !ts.isExportDeclaration(statement)
    )
      continue;
    if (
      !statement.moduleSpecifier ||
      !ts.isStringLiteral(statement.moduleSpecifier)
    )
      continue;
    const specifier = statement.moduleSpecifier.text;
    if (specifier.endsWith(".css")) continue;
    if (!specifier.startsWith(".")) continue;
    const resolved = ts.resolveModuleName(
      specifier,
      file,
      { moduleResolution: ts.ModuleResolutionKind.Bundler },
      ts.sys,
    ).resolvedModule?.resolvedFileName;
    if (!resolved) {
      errors.push(`Import não resolvido: ${file}: ${specifier}`);
      continue;
    }
    const target = path.resolve(resolved),
      rel = path.relative(root, file).replaceAll("\\", "/"),
      dest = path.relative(root, target).replaceAll("\\", "/");
    if (rel.startsWith("shared/ui/") && dest.startsWith("modules/"))
      errors.push(`UI genérica depende de negócio: ${rel} -> ${dest}`);
    const fromModule = rel.match(/^modules\/([^/]+)/)?.[1],
      toModule = dest.match(/^modules\/([^/]+)/)?.[1];
    if (
      fromModule &&
      toModule &&
      fromModule !== toModule &&
      !/\/(contracts|api|index)\.tsx?$/.test(dest)
    )
      errors.push(`Use interface pública entre módulos: ${rel} -> ${dest}`);
    if (
      !ts.isImportDeclaration(statement) ||
      !statement.importClause?.isTypeOnly
    )
      edges.push(target);
  }
  if (!file.includes(".test."))
    graph.set(
      file,
      edges.filter((target) => !target.includes(".test.")),
    );
}
const active = new Set(),
  done = new Set();
function visit(file, trace = []) {
  if (active.has(file)) {
    errors.push(
      "Ciclo: " +
        [...trace, file].map((f) => path.relative(root, f)).join(" -> "),
    );
    return;
  }
  if (done.has(file)) return;
  active.add(file);
  for (const target of graph.get(file) || []) visit(target, [...trace, file]);
  active.delete(file);
  done.add(file);
}
for (const file of graph.keys()) visit(file);
if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log(`Fronteiras e ciclos verificados em ${files.length} arquivos.`);
