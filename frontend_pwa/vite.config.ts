import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { execSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

const rootDir = fileURLToPath(new URL('.', import.meta.url))

// Versão do app: fonte única no package.json — evita "v1.0.0" hardcoded repetido
// nas telas (Sobre o app, Status do sistema). Ver RF-19/RF-21 da spec do bloco App.
const pkg = JSON.parse(readFileSync(rootDir + 'package.json', 'utf-8')) as { version: string }

// Hash do commit exibido junto da versão. Aceita override via VITE_BUILD_HASH (útil
// no build de produção via Docker — Dockerfile.web copia só frontend_pwa/, sem .git,
// então o CI/host pode injetar o hash real como build-arg/env). Sem override, tenta
// `git rev-parse` local (funciona em dev); se nada disso funcionar, cai para 'dev'
// em vez de quebrar o build (RF-20).
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
    // backend local — espelha o comportamento do reverse proxy (Caddy) em produção,
    // permitindo que o frontend use caminhos relativos (/api/v1) em todo ambiente.
    proxy: {
      '/api': 'http://localhost:8000',
      '/uploads': 'http://localhost:8000',
      '/static': 'http://localhost:8000',
    },
  },
  plugins: [
    react(),
    VitePWA({
      // 'prompt' em vez de 'autoUpdate': a troca de versão do Service Worker fica
      // pendente até o operador confirmar em "Atualizar agora" (tela Status do
      // sistema) — 'autoUpdate' recarregaria a página sozinho, sem aviso.
      registerType: 'prompt',
      manifest: {
        name: 'LGD Mantos',
        short_name: 'LGD Mantos',
        description: 'Streetwear ops — controle total da sua loja',
        theme_color: '#0A0A0B',
        background_color: '#0A0A0B',
        display: 'standalone',
        orientation: 'portrait',
        start_url: '/',
        icons: [
          { src: '/favicon.png', sizes: '192x192', type: 'image/png' },
          { src: '/favicon.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
    }),
  ],
})
