/// <reference types="vite/client" />

// Injetadas em build time por vite.config.ts (fonte única: package.json + git).
// Usadas nas telas de status do sistema e informações sobre o app.
declare const __APP_VERSION__: string
declare const __BUILD_HASH__: string
