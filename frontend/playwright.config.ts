import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  timeout: 120_000,
  use: {
    baseURL: "http://127.0.0.1:5174",
    viewport: { width: 390, height: 844 },
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 5174 --strictPort",
    url: "http://127.0.0.1:5174",
    reuseExistingServer: false,
    env: { VITE_API_URL: "http://127.0.0.1:8001/api/v1" },
  },
});
