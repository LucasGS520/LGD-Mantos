/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

// Injetadas em build time por vite.config.ts (fonte única: package.json + git).
// Ver services/pwa.ts (Status do sistema) e telas mais/About.tsx.
declare const __APP_VERSION__: string
declare const __BUILD_HASH__: string
