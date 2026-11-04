import { test, expect } from "@playwright/test";

test("inventário, compra, venda parcial, recebimento, correção e histórico", async ({
  page,
  request,
}) => {
  const pageErrors: string[] = [];
  page.on("pageerror", (error) => pageErrors.push(error.message));
  await expect.poll(async () => {
    try { return (await request.get("http://127.0.0.1:8001/api/v1/health")).status(); }
    catch { return 0; }
  }).toBe(200);
  // A preparação usa somente a API isolada; os acontecimentos são feitos na UI.
  const login = await request.post("http://127.0.0.1:8001/api/v1/auth/login", {
    data: { password: "senha-testes" },
  });
  const headers = { Authorization: `Bearer ${(await login.json()).token}` };
  for (const kind of [
    "supplier",
    "purchase_channel",
    "sale_channel",
    "payment_method",
  ]) {
    const response = await request.post(
      "http://127.0.0.1:8001/api/v1/auxiliaries",
      { headers, data: { kind, name: `Navegador ${kind}` } },
    );
    expect(response.ok()).toBeTruthy();
  }
  await page.goto("/");
  await page.getByPlaceholder("Senha").fill("senha-testes");
  await page.getByRole("button", { name: "Entrar" }).click();
  await page.getByRole("button", { name: "Novo produto", exact: true }).click();
  await page.getByLabel("Nome da peça").fill("Camiseta navegador");
  await page.getByLabel("Estampa", { exact: true }).fill("Arte navegador");
  await page.getByLabel("Marca", { exact: true }).fill("LGD");
  await page.getByLabel("Modelo", { exact: true }).fill("Reta");
  await page
    .getByRole("button", { name: "Salvar produto", exact: true })
    .click();
  await page.getByLabel("Tamanho", { exact: true }).fill("M");
  await page.getByLabel("Cor", { exact: true }).fill("Preto");
  await page
    .getByLabel("Custo de referência (opcional)", { exact: true })
    .fill("10.00");
  await page
    .getByLabel("Preço de referência (opcional)", { exact: true })
    .fill("30.00");
  await page
    .getByRole("button", { name: "Salvar variante", exact: true })
    .click();
  await expect(page.getByText("M / Preto · 0 disponíveis")).toBeVisible();
  // A criação do produto possui uma entrada intermediária na pilha de navegação.
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await page.getByRole("button", { name: "Voltar", exact: true }).click();
  await page
    .getByRole("button", { name: "Inventário inicial", exact: true })
    .click();
  await page.getByRole("button", { name: "Preparar inventário" }).click();
  await page.getByLabel("Peça e variante").selectOption({ index: 1 });
  await page
    .getByRole("button", { name: "Adicionar item", exact: true })
    .click();
  await page.getByLabel("Quantidade inteira").fill("2");
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(
    page.getByText("Detalhe da operação", { exact: true }),
  ).toBeVisible();
  // Retorna ao catálogo sem reutilizar dados de outra instância da tela.
  await page.reload();
  await page.getByRole("button", { name: "Compras", exact: true }).click();
  await page
    .getByRole("button", { name: "Registrar compra", exact: true })
    .click();
  await page
    .getByLabel("Fornecedor", { exact: true })
    .selectOption({ index: 1 });
  await page
    .getByLabel("Canal de compra", { exact: true })
    .selectOption({ index: 1 });
  await page.getByLabel("Peça e variante").selectOption({ index: 1 });
  await page
    .getByRole("button", { name: "Adicionar item", exact: true })
    .click();
  await page.getByLabel("Custo unitário", { exact: true }).fill("20.00");
  const supplierBefore = await page.getByLabel("Fornecedor", { exact: true }).inputValue();
  await page.getByRole("button", { name: "Cadastrar peça durante a compra" }).click();
  await page.getByLabel("Nome da peça").fill("Regata solar");
  await page.getByLabel("Estampa", { exact: true }).fill("Sol azul");
  await page.getByRole("button", { name: "Salvar produto", exact: true }).click();
  await page.getByLabel("Tamanho", { exact: true }).fill("G");
  await page.getByLabel("Cor", { exact: true }).fill("Branco");
  await page.getByLabel("Custo de referência (opcional)", { exact: true }).fill("12.00");
  await page.getByLabel("Preço de referência (opcional)", { exact: true }).fill("35.00");
  await page.getByRole("button", { name: "Salvar variante", exact: true }).click();
  await expect(page.getByLabel("Fornecedor", { exact: true })).toHaveValue(supplierBefore);
  await expect(page.getByLabel("Custo unitário", { exact: true })).toHaveValue("20.00");
  await page.getByLabel("Peça e variante").selectOption({ label: "Regata solar · Sol azul · G / Branco · 0 disponíveis" });
  await page.getByRole("button", { name: "Adicionar item", exact: true }).click();
  await expect(page.getByLabel("Quantidade inteira")).toHaveCount(2);
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(
    page.getByText("Detalhe da operação", { exact: true }),
  ).toBeVisible();
  await page.reload();
  await page
    .getByRole("button", { name: "Vendas e recebimentos", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Registrar venda", exact: true })
    .click();
  await page
    .getByLabel("Canal de venda", { exact: true })
    .selectOption({ index: 1 });
  await page.getByLabel("Peça e variante").selectOption({ index: 1 });
  await page
    .getByRole("button", { name: "Adicionar item", exact: true })
    .click();
  await page.getByLabel("Preço negociado por unidade").fill("25.00");
  await page
    .getByRole("button", { name: "Adicionar pagamento", exact: true })
    .click();
  await page.getByLabel("Valor recebido", { exact: true }).fill("10.00");
  await page
    .getByLabel("Forma de pagamento", { exact: true })
    .selectOption({ index: 1 });
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(page.getByText(/Saldo:.*15,00.*pendente/)).toBeVisible();
  await page
    .getByRole("button", { name: "Corrigir venda ou pagamentos" })
    .click();
  await page
    .getByRole("button", { name: "Adicionar pagamento", exact: true })
    .click();
  await page.getByLabel("Valor recebido", { exact: true }).nth(1).fill("15.00");
  await page
    .getByLabel("Forma de pagamento", { exact: true })
    .nth(1)
    .selectOption({ index: 1 });
  await page.getByLabel("Motivo obrigatório").fill("Recebimento confirmado");
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(page.getByText(/Saldo:.*0,00.*concluída/)).toBeVisible();
  await expect(
    page.getByText(/Correção · Recebimento confirmado/),
  ).toBeVisible();
  await page.reload();
  await page.getByText("Gestão", { exact: true }).click();
  for (const view of [
    "stock",
    "sales",
    "receipts",
    "purchases",
    "buying",
    "overview",
  ]) {
    await page.getByLabel("Visão", { exact: true }).selectOption(view);
    await expect(page.getByRole("alert")).toHaveCount(0);
    await expect(page.getByLabel("Visão", { exact: true })).toBeVisible();
  }
  expect(pageErrors).toEqual([]);
  await page.screenshot({
    path: "test-results/gestao-mobile.png",
    fullPage: true,
  });
});
