import { defineConfig } from "@playwright/test";

// Isola resultados/cache por execução, inclusive em diretórios sincronizados.
const runId = `${Date.now()}-${process.pid}`;

export default defineConfig({
  testDir: "./e2e",
  outputDir: `./test-results/${runId}`,
  workers: 1,
  timeout: 120_000,
  use: {
    baseURL: "http://127.0.0.1:5174",
    viewport: { width: 390, height: 844 },
    // No Windows sincronizado, a limpeza dos traces pode prender o encerramento.
    // CI Linux mantém o diagnóstico; localmente é possível ativar com E2E_TRACE=1.
    trace: process.platform !== "win32" || process.env.E2E_TRACE === "1"
      ? "retain-on-failure"
      : "off",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort",
    url: "http://127.0.0.1:5174",
    reuseExistingServer: false,
    env: {
      VITE_API_URL: "http://127.0.0.1:8001/api/v1",
      VITE_CACHE_DIR: `.cache/vite-e2e-${runId}`,
    },
  },
});
