import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
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
      registerType: 'autoUpdate',
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
