// Reescrita mecânica dos imports com o serviço oficial do TypeScript.
import ts from 'typescript';
import fs from 'node:fs';
import path from 'node:path';
const configPath = ts.findConfigFile('.', ts.sys.fileExists, 'tsconfig.app.json');
const config = ts.readConfigFile(configPath, ts.sys.readFile);
const parsed = ts.parseJsonConfigFileContent(config.config, ts.sys, '.');
const host = {
  getScriptFileNames: () => parsed.fileNames,
  getScriptVersion: () => '0',
  getScriptSnapshot: name => ts.sys.fileExists(name) ? ts.ScriptSnapshot.fromString(ts.sys.readFile(name)) : undefined,
  getCurrentDirectory: () => process.cwd(),
  getCompilationSettings: () => parsed.options,
  getDefaultLibFileName: opts => ts.getDefaultLibFilePath(opts),
  fileExists: ts.sys.fileExists, readFile: ts.sys.readFile, readDirectory: ts.sys.readDirectory,
};
const service = ts.createLanguageService(host);
for (const name of parsed.fileNames.filter(name => !name.endsWith('.d.ts'))) {
  const edits = service.organizeImports({type: 'file', fileName: name}, {}, {});
  for (const edit of edits) {
    let source = fs.readFileSync(edit.fileName, 'utf8');
    for (const change of [...edit.textChanges].sort((a,b) => b.span.start-a.span.start)) {
      source = source.slice(0,change.span.start) + change.newText + source.slice(change.span.start+change.span.length);
    }
    fs.writeFileSync(path.resolve(edit.fileName), source);
  }
}
