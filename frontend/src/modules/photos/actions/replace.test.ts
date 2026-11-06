import { beforeEach, expect, it, vi } from "vitest";
import { api } from "../api";
import { replacePhoto } from "./replace";
vi.mock("../api", () => ({
  api: { upload: vi.fn(), organize: vi.fn(), remove: vi.fn() },
}));
const old = {
  id: "old",
  product_id: "p",
  position: 3,
  primary: true,
  variant_id: "v",
  color: "Preto",
};
beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.upload).mockResolvedValue({ ...old, id: "new" });
});
it("preserva a foto anterior quando a organização da substituta falha", async () => {
  vi.mocked(api.organize).mockRejectedValue(new Error("Falha ao organizar"));
  await expect(
    replacePhoto("p", old, new File(["image"], "a.png")),
  ).rejects.toThrow("Falha ao organizar");
  expect(api.remove).not.toHaveBeenCalled();
});
it("preserva os metadados antes de remover a foto antiga", async () => {
  await replacePhoto("p", old, new File(["image"], "a.png"));
  expect(api.organize).toHaveBeenCalledWith("new", {
    position: 3,
    primary: true,
    variant_id: "v",
    color: "Preto",
  });
  expect(api.remove).toHaveBeenCalledWith("old");
  expect(vi.mocked(api.organize).mock.invocationCallOrder[0]).toBeLessThan(
    vi.mocked(api.remove).mock.invocationCallOrder[0],
  );
});
