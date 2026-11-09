import { afterEach, expect, it, vi } from "vitest";
import {
  configureAuthentication,
  request,
  setUnauthorizedHandler,
} from "./http";
afterEach(() => {
  configureAuthentication({ load: () => null, clear: () => {} });
  setUnauthorizedHandler(() => {});
  vi.unstubAllGlobals();
});
it("recebe a autenticação pela composição sem conhecer o módulo auth", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValue(new Response(JSON.stringify({ ok: true })));
  vi.stubGlobal("fetch", fetch);
  configureAuthentication({ load: () => "test-token", clear: () => {} });
  expect(await request("/state")).toEqual({ ok: true });
  expect(fetch.mock.calls[0][1].headers.Authorization).toBe(
    "Bearer test-token",
  );
});
it("401 limpa a sessão e notifica a aplicação", async () => {
  const clear = vi.fn(),
    expired = vi.fn();
  configureAuthentication({ load: () => "expired", clear });
  setUnauthorizedHandler(expired);
  vi.stubGlobal(
    "fetch",
    vi
      .fn()
      .mockResolvedValue(
        new Response('{"detail":"Não autorizado"}', { status: 401 }),
      ),
  );
  await expect(request("/state")).rejects.toThrow("Não autorizado");
  expect(clear).toHaveBeenCalledOnce();
  expect(expired).toHaveBeenCalledOnce();
});
it("resposta incerta não repete automaticamente a confirmação", async () => {
  const fetch = vi
    .fn()
    .mockRejectedValue(new TypeError("Conexão interrompida"));
  vi.stubGlobal("fetch", fetch);
  await expect(
    request("/operations", "POST", { test: true }, "same-key"),
  ).rejects.toThrow("Conexão interrompida");
  expect(fetch).toHaveBeenCalledOnce();
  expect(fetch.mock.calls[0][1].headers["Idempotency-Key"]).toBe("same-key");
});
