import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { NavProvider } from "../../app/nav";
import { AuxiliaryScreen } from "./Page";

it("alterna entre os cinco cadastros sem expor uma página vazia inválida", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockImplementation(async () => new Response("[]", { status: 200 })),
  );
  render(
    <NavProvider>
      <AuxiliaryScreen />
    </NavProvider>,
  );
  const selector = screen.getByLabelText("Cadastro");
  expect(selector.querySelector('option[value=""]')).toBeNull();
  for (const kind of [
    "supplier",
    "category",
    "purchase_channel",
    "sale_channel",
    "payment_method",
  ]) {
    await userEvent.selectOptions(selector, kind);
    expect(screen.getByLabelText("Novo nome")).toBeDefined();
    expect(screen.getByRole("button", { name: "Cadastrar" })).toBeDefined();
  }
  vi.unstubAllGlobals();
});
