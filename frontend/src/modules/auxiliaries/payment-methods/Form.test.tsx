import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { PaymentMethodsForm } from "./Form";
it("cadastra payment_method com tipo fixo e campos estruturados", async () => {
  const fetch = vi
    .fn()
    .mockResolvedValue(
      new Response(JSON.stringify({ id: "new" }), { status: 200 }),
    );
  vi.stubGlobal("fetch", fetch);
  const saved = vi.fn();
  render(<PaymentMethodsForm editing={null} onSaved={saved} />);
  await userEvent.type(screen.getByLabelText("Novo nome"), "Registro de teste");
  await userEvent.click(screen.getByRole("button", { name: "Cadastrar" }));
  await waitFor(() => expect(saved).toHaveBeenCalledTimes(1));
  expect(fetch.mock.calls[0][0]).toContain("/auxiliaries");
  expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({
    kind: "payment_method",
    name: "Registro de teste",
    notes: null,
    active: true,
  });
  vi.unstubAllGlobals();
});
