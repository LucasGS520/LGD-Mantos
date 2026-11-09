import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError } from "../../../shared/api/errors";
import { api } from "../api";
import type { Preview } from "../contracts";
import { useOperationEditor, type EditorProps } from "./useOperationEditor";
vi.mock("../api", () => ({ api: { preview: vi.fn(), confirm: vi.fn() } }));
const preview: Preview = {
  operation: {
    id: "sale",
    sequence: 1,
    kind: "sale",
    effective_at: "2026-01-01",
    created_at: "2026-01-01",
    version: 1,
    cancelled: false,
    payload: { kind: "sale", items: [], payments: [], notes: null, labels: {} },
    result: { items: [], effects: {} },
  },
  affected: [],
  stock: {},
  preview_token: "signed",
};
const event = { preventDefault() {} } as React.FormEvent;
const props = (): EditorProps => ({
  kind: "sale",
  original: null,
  products: [],
  auxiliaries: [],
  cancel: false,
  reload: vi.fn(),
  onSaved: vi.fn(),
});
beforeEach(() => {
  vi.mocked(api.preview).mockResolvedValue(preview);
  vi.mocked(api.confirm).mockReset();
});
describe("editor de operação", () => {
  it("mantém a mesma chave e conteúdo após resposta incerta", async () => {
    vi.mocked(api.confirm)
      .mockRejectedValueOnce(new TypeError("Conexão interrompida"))
      .mockResolvedValueOnce(preview);
    const settings = props();
    const { result } = renderHook(() => useOperationEditor(settings));
    await act(async () => result.current.review(event));
    await act(async () => result.current.confirm());
    expect(result.current.preview).toBe(preview);
    await act(async () => result.current.confirm());
    const calls = vi.mocked(api.confirm).mock.calls;
    expect(calls[1]).toEqual(calls[0]);
    expect(settings.onSaved).toHaveBeenCalledExactlyOnceWith(preview.operation);
  });
  it("invalida prévia obsoleta e mantém os dados preenchidos", async () => {
    vi.mocked(api.confirm).mockRejectedValue(
      new ApiError(409, null, "A base mudou"),
    );
    const { result } = renderHook(() => useOperationEditor(props()));
    act(() => result.current.patch({ notes: "Preservar meu registro" }));
    await act(async () => result.current.review(event));
    await act(async () => result.current.confirm());
    expect(result.current.preview).toBeNull();
    expect(result.current.input.notes).toBe("Preservar meu registro");
    expect(result.current.error).toContain("Revise os efeitos");
  });
  it("editar um campo invalida a revisão anterior", async () => {
    const { result } = renderHook(() => useOperationEditor(props()));
    await act(async () => result.current.review(event));
    act(() => result.current.patch({ notes: "alterado" }));
    expect(result.current.preview).toBeNull();
  });
  it("bloqueia duplo clique antes de uma nova renderização", async () => {
    let finish!: (value: Preview) => void;
    vi.mocked(api.confirm).mockImplementation(
      () =>
        new Promise((resolve) => {
          finish = resolve;
        }),
    );
    const { result } = renderHook(() => useOperationEditor(props()));
    await act(async () => result.current.review(event));
    let pending!: Promise<void>;
    act(() => {
      pending = result.current.confirm();
      void result.current.confirm();
    });
    expect(api.confirm).toHaveBeenCalledTimes(1);
    await act(async () => {
      finish(preview);
      await pending;
    });
  });
  it("preserva rascunho e prévia ao atualizar fontes do cadastro inline", async () => {
    const { result, rerender } = renderHook(
      (settings) => useOperationEditor(settings),
      { initialProps: props() },
    );
    act(() =>
      result.current.patch({
        channel_id: "channel",
        notes: "Compra em edição",
      }),
    );
    await act(async () => result.current.review(event));
    rerender({ ...props(), products: [] });
    expect(result.current.input.channel_id).toBe("channel");
    expect(result.current.input.notes).toBe("Compra em edição");
    expect(result.current.preview).toBe(preview);
  });
});
