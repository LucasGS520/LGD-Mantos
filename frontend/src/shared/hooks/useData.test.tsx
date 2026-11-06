import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { useData } from "./useData";

describe("carregamento de dados", () => {
  it("descarta resposta antiga quando o filtro muda", async () => {
    let finish!: (value: string) => void;
    const old = new Promise<string>((resolve) => {
      finish = resolve;
    });
    const { result, rerender } = renderHook(
      ({ key }) =>
        useData(() => (key === "old" ? old : Promise.resolve("novo")), key),
      { initialProps: { key: "old" } },
    );
    await act(async () => {});
    rerender({ key: "new" });
    await waitFor(() => expect(result.current.data).toBe("novo"));
    await act(async () => finish("antigo"));
    expect(result.current.data).toBe("novo");
  });
  it("oferece retry depois de uma falha sem transformar erro em lista vazia", async () => {
    let failed = true;
    const { result } = renderHook(() =>
      useData(async () => {
        if (failed) throw new Error("Falha de rede");
        return ["registro"];
      }),
    );
    await waitFor(() => expect(result.current.error).toBe("Falha de rede"));
    failed = false;
    act(() => result.current.reload());
    await waitFor(() => expect(result.current.data).toEqual(["registro"]));
    expect(result.current.error).toBeNull();
  });
  it("ignora conclusão depois de desmontar", async () => {
    let finish!: (value: string) => void;
    const pending = new Promise<string>((resolve) => {
      finish = resolve;
    });
    const { result, unmount } = renderHook(() => useData(() => pending));
    await act(async () => {});
    unmount();
    await act(async () => finish("tarde"));
    expect(result.current.data).toBeNull();
  });
});
