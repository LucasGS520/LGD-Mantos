import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { execSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const rootDir = fileURLToPath(new URL('.', import.meta.url))

// Versão do app: fonte única no package.json — evita "v1.0.0" hardcoded repetido
// nas telas (Sobre o app, Status do sistema). Ver RF-19/RF-21 da spec do bloco App.
const pkg = JSON.parse(readFileSync(rootDir + 'package.json', 'utf-8')) as { version: string }

// Hash do commit exibido junto da versão. Aceita override via VITE_BUILD_HASH para
// builds sem acesso ao histórico Git. Sem override, tenta `git rev-parse` local e,
// se não estiver disponível, usa "dev" sem interromper o build.
function resolveBuildHash(): string {
  if (process.env.VITE_BUILD_HASH) return process.env.VITE_BUILD_HASH
  try {
    return execSync('git rev-parse --short HEAD', { cwd: rootDir, stdio: ['ignore', 'pipe', 'ignore'] })
      .toString()
      .trim()
  } catch {
    return 'dev'
  }
}

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
    __BUILD_HASH__: JSON.stringify(resolveBuildHash()),
  },
  server: {
    watch: {
      usePolling: true,
      interval: 500,
    },
    // Em desenvolvimento, encaminha chamadas de API e arquivos estáticos para o
    // backend local, permitindo que o frontend use caminhos relativos (/api/v1).
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
  plugins: [react()],
})
