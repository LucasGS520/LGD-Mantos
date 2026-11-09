import {
  test,
  expect,
  type APIRequestContext,
  type Page,
} from "@playwright/test";

const base = "http://127.0.0.1:8001/api/v1";
async function prepare(request: APIRequestContext, page: Page) {
  const login = await request.post(base + "/auth/login", {
    data: { password: "senha-testes" },
  });
  const headers = { Authorization: "Bearer " + (await login.json()).token };
  const post = async (path: string, data: unknown) => {
    const response = await request.post(base + path, { headers, data });
    expect(response.ok()).toBeTruthy();
    return response.json();
  };
  const state = await (await request.get(base + "/state", { headers })).json();
  if (!state.started_at) {
    const data = { kind: "inventory", items: [] };
    const preview = await post("/operations/preview", data);
    expect(
      (
        await request.post(base + "/operations", {
          headers: { ...headers, "Idempotency-Key": crypto.randomUUID() },
          data: { data, preview_token: preview.preview_token },
        })
      ).ok(),
    ).toBeTruthy();
  }
  const name = "Recuperação " + crypto.randomUUID();
  const channel = await post("/auxiliaries", { kind: "sale_channel", name });
  const product = await post("/products", {
    name,
    print_name: crypto.randomUUID(),
    variants: [{ size: "M", color: "Preto", reference_price: "30.00" }],
    accept_similar: true,
  });
  const vid = product.variants[0].id;
  const incoming = {
    kind: "adjustment",
    direction: "in",
    reason: "Preparação isolada",
    items: [{ variant_id: vid, quantity: 3, unit_cost: "10.00" }],
  };
  const preview = await post("/operations/preview", incoming);
  expect(
    (
      await request.post(base + "/operations", {
        headers: { ...headers, "Idempotency-Key": crypto.randomUUID() },
        data: { data: incoming, preview_token: preview.preview_token },
      })
    ).ok(),
  ).toBeTruthy();
  await page.goto("/");
  await page.getByPlaceholder("Senha").fill("senha-testes");
  await page.getByRole("button", { name: "Entrar" }).click();
  return { headers, name, vid, channel, product, post };
}
async function fillSale(page: Page, vid: string, channel: string) {
  await page
    .getByRole("button", { name: "Vendas e recebimentos", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Registrar venda", exact: true })
    .click();
  await page
    .getByLabel("Canal de venda", { exact: true })
    .selectOption(channel);
  await page.getByLabel("Peça e variante").selectOption(vid);
  await page
    .getByRole("button", { name: "Adicionar item", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
}

test("prévia obsoleta mantém o formulário e exige revisão humana", async ({
  page,
  request,
}) => {
  const fixture = await prepare(request, page);
  await fillSale(page, fixture.vid, fixture.channel.id);
  await fixture.post("/auxiliaries", {
    kind: "category",
    name: crypto.randomUUID(),
  });
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "Revise os efeitos novamente",
  );
  await expect(page.getByLabel("Canal de venda", { exact: true })).toHaveValue(
    fixture.channel.id,
  );
  await expect(page.getByLabel("Preço negociado por unidade")).toHaveValue(
    "30.00",
  );
  await expect(
    page.getByRole("button", {
      name: "Confirmar operação e efeitos apresentados",
    }),
  ).toHaveCount(0);
  await page
    .getByRole("button", { name: "Revisar efeitos antes de confirmar" })
    .click();
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(
    page.getByText("Detalhe da operação", { exact: true }),
  ).toBeVisible();
});

test("resposta interrompida repete a confirmação sem duplicar a venda", async ({
  page,
  request,
}) => {
  const fixture = await prepare(request, page);
  await fillSale(page, fixture.vid, fixture.channel.id);
  const keys: string[] = [],
    ids: string[] = [];
  await page.route("**/api/v1/operations", async (route) => {
    if (route.request().method() !== "POST") return route.continue();
    keys.push(route.request().headers()["idempotency-key"]);
    const response = await route.fetch();
    ids.push((await response.json()).operation.id);
    if (ids.length === 1) await route.abort("failed");
    else await route.fulfill({ response });
  });
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(page.getByRole("alert")).toContainText(
    "tente confirmar novamente",
  );
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(
    page.getByText("Detalhe da operação", { exact: true }),
  ).toBeVisible();
  expect(keys).toHaveLength(2);
  expect(keys[0]).toBe(keys[1]);
  expect(ids[0]).toBe(ids[1]);
  const products = await (
    await request.get(base + "/products", { headers: fixture.headers })
  ).json();
  expect(
    products.find((p: { id: string }) => p.id === fixture.product.id)
      .variants[0].stock,
  ).toBe(2);
});

test("falha nos movimentos é visível e permite tentar novamente", async ({
  page,
  request,
}) => {
  const fixture = await prepare(request, page);
  await fillSale(page, fixture.vid, fixture.channel.id);
  let fail = true;
  await page.route("**/api/v1/movements*", async (route) => {
    if (fail) {
      await route.fulfill({
        status: 503,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Movimentos indisponíveis" }),
      });
    } else await route.continue();
  });
  await page
    .getByRole("button", { name: "Confirmar operação e efeitos apresentados" })
    .click();
  await expect(
    page.getByText("Movimentos indisponíveis", { exact: true }),
  ).toBeVisible();
  fail = false;
  await page
    .getByRole("button", { name: "Tentar novamente", exact: true })
    .click();
  await expect(
    page.getByText("Movimentos indisponíveis", { exact: true }),
  ).toHaveCount(0);
  await expect(page.getByText(/-1 unidades/)).toBeVisible();
});

test("substituição de foto repete após resposta perdida preservando a identidade", async ({
  page,
  request,
}) => {
  const fixture = await prepare(request, page);
  await page.getByRole("heading", { name: fixture.name, exact: true }).click();
  const red = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAEUlEQVR4nGP8z4ACmBgo4wMAUJEBCfBOwRcAAAAASUVORK5CYII=",
    "base64",
  );
  const blue = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAFElEQVR4nGNkYPjPgASYGFABqXwATpMBCb/kZHAAAAAASUVORK5CYII=",
    "base64",
  );
  await page
    .getByLabel("Adicionar foto", { exact: true })
    .setInputFiles({ name: "red.png", mimeType: "image/png", buffer: red });
  await expect(page.getByAltText("Foto do produto")).toBeVisible();
  const product = await (
    await request.get(base + "/products/" + fixture.product.id, {
      headers: fixture.headers,
    })
  ).json();
  const id = product.photos[0].id;
  let loseResponse = true;
  await page.route(`**/api/v1/photos/${id}/content`, async (route) => {
    if (route.request().method() === "PUT" && loseResponse) {
      loseResponse = false;
      const response = await route.fetch();
      expect(response.ok()).toBeTruthy();
      await route.abort("failed");
    } else await route.continue();
  });
  const file = { name: "blue.png", mimeType: "image/png", buffer: blue };
  await page.getByLabel("Substituir", { exact: true }).setInputFiles(file);
  await expect(
    page.getByText(/Failed to fetch|NetworkError|Load failed/),
  ).toBeVisible();
  await page.getByLabel("Substituir", { exact: true }).setInputFiles(file);
  await expect(page.getByAltText("Foto do produto")).toBeVisible();
  await expect
    .poll(async () => {
      const current = await (
        await request.get(base + "/products/" + product.id, {
          headers: fixture.headers,
        })
      ).json();
      return current.photos.map((p: { id: string }) => p.id);
    })
    .toEqual([id]);
  const content = await request.get(base + `/photos/${id}/content`, {
    headers: fixture.headers,
  });
  expect(await content.body()).toEqual(blue);
});
