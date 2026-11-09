import { beforeEach, expect, it, vi } from "vitest";
import { api } from "../api";
import { replacePhoto } from "./replace";
vi.mock("../api", () => ({ api: { replace: vi.fn() } }));
const old = {
  id: "old",
  product_id: "p",
  position: 3,
  primary: true,
  variant_id: "v",
  color: "Preto",
};
beforeEach(() => vi.resetAllMocks());
it("envia a substituição ao mesmo ID e permite repetir após resposta perdida", async () => {
  const file = new File(["image"], "a.png");
  vi.mocked(api.replace).mockRejectedValueOnce(new Error("Conexão perdida"));
  await expect(replacePhoto("p", old, file)).rejects.toThrow("Conexão perdida");
  await replacePhoto("p", old, file);
  expect(api.replace).toHaveBeenNthCalledWith(1, "old", file);
  expect(api.replace).toHaveBeenNthCalledWith(2, "old", file);
});
it("recusa foto de outro produto antes de enviar", async () => {
  await expect(
    replacePhoto("outro", old, new File([], "a.png")),
  ).rejects.toThrow("outro produto");
  expect(api.replace).not.toHaveBeenCalled();
});
