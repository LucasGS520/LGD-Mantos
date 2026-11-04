import {
useEffect,
useRef,
useState,
type FormEvent
} from "react";
import { AppBar,ScreenBody } from "../../components/Chrome";
import { Card,ErrorBody,LoadingBody,Section } from "../../components/UI";
import { useData } from "../../hooks/useData";
import { useNav } from "../../nav";
import {
api,
brl,
dateLabel,
kindLabel,
localToday,
type Auxiliary,
type Item,
type Kind,
type Operation,
type OperationInput,
type Payment,
type Preview,
type Product,
type State
} from "../../services/domain";
import "../../styles/workspace.css";

import {
Button,
ErrorMessage,
Field,
History,
Note,
OperationSummary,
Options,
Select,
errorText
} from "./Shared";

import { ProductForm,VariantForm } from "./Catalog";

export function Operations() {
  const { params, navigate } = useNav();
  const kind = (params.kind || "sale") as Kind;
  const { data, loading, error, reload } = useData(
    () =>
      Promise.all([
        api.get<Operation[]>("/operations"),
        api.get<State>("/state"),
      ]),
    kind,
  );
  const [ops, state] = data || [[], null];
  const visible = ops.filter((op) => op.kind === kind);
  const canCreate =
    state && (kind === "inventory" ? !state.started_at : !!state.started_at);
  return (
    <>
      <AppBar
        title={
          kind === "sale"
            ? "Vendas e recebimentos"
            : kind === "purchase"
              ? "Compras"
              : kindLabel[kind]
        }
        back
      />
      <ScreenBody>
        <Options>
          {canCreate && (
            <Button onClick={() => navigate("operation-form", { kind })}>
              {kind === "inventory"
                ? "Preparar inventário"
                : `Registrar ${kindLabel[kind].toLowerCase()}`}
            </Button>
          )}
        </Options>
        {state && !state.started_at && kind !== "inventory" && (
          <Note>
            Confirme o inventário inicial antes de registrar operações.
          </Note>
        )}
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          visible.map((op) => (
            <Card
              key={op.id}
              onClick={() => navigate("operation-detail", { id: op.id })}
            >
              <OperationSummary operation={op} />
              <span>Ver detalhes e histórico →</span>
            </Card>
          ))
        )}
        {!loading && !visible.length && (
          <Note>Nenhum registro neste grupo.</Note>
        )}
      </ScreenBody>
    </>
  );
}

export function OperationDetail() {
  const { params, navigate } = useNav();
  const id = params.id as string;
  const { data, loading, error, reload } = useData(
    () => api.get<Operation>(`/operations/${id}`),
    id,
  );
  const [movements, setMovements] = useState<
    {
      id: string;
      operation_id: string;
      variant_id: string;
      delta: number;
      version: number;
      reason: string;
      created_at: string;
    }[]
  >([]);
  useEffect(() => {
    api
      .get<typeof movements>("/movements")
      .then((m) => setMovements(m.filter((row) => row.operation_id === id)))
      .catch(() => {});
  }, [id]);
  return (
    <>
      <AppBar title="Detalhe da operação" back />
      <ScreenBody>
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <>
              <Card>
                <OperationSummary operation={data} />
              </Card>
              {!data.cancelled && (
                <Options>
                  <Button
                    onClick={() =>
                      navigate("operation-form", { id, kind: data.kind })
                    }
                  >
                    {data.kind === "sale"
                      ? "Corrigir venda ou pagamentos"
                      : "Corrigir registro"}
                  </Button>
                  {data.kind !== "inventory" && (
                    <Button
                      danger
                      onClick={() =>
                        navigate("operation-form", {
                          id,
                          kind: data.kind,
                          cancel: true,
                        })
                      }
                    >
                      Anular registro
                    </Button>
                  )}
                </Options>
              )}
              <Section title="Movimentações vinculadas">
                {movements.map((m) => (
                  <p key={m.id}>
                    {m.delta > 0 ? "+" : ""}
                    {m.delta} unidades · versão {m.version} ·{" "}
                    {dateLabel(m.created_at)} · {m.reason}
                  </p>
                ))}
              </Section>
              <History id={id} />
            </>
          )
        )}
      </ScreenBody>
    </>
  );
}

function cleanInput(op: Operation): OperationInput {
  return {
    kind: op.kind,
    purchase_date: op.payload.purchase_date,
    supplier_id: op.payload.supplier_id,
    channel_id: op.payload.channel_id,
    direction: op.payload.direction,
    items: op.payload.items.map((i) => ({
      variant_id: i.variant_id,
      quantity: i.quantity,
      ...(op.kind === "sale"
        ? { unit_price: i.unit_price }
        : { unit_cost: i.unit_cost }),
    })),
    payments: op.payload.payments.map((p) => ({
      id: p.id,
      amount: p.amount,
      method_id: p.method_id,
    })),
    notes: op.payload.notes,
    version: op.version,
    reason: "",
    cancelled: false,
  };
}

export function OperationForm() {
  const { params, navigate } = useNav();
  const kind = params.kind as Kind;
  const id = params.id as string | undefined;
  const { data, loading, error, reload } = useData(
    () =>
      Promise.all([
        api.get<Product[]>("/products"),
        api.get<Auxiliary[]>("/auxiliaries"),
        id ? api.get<Operation>(`/operations/${id}`) : Promise.resolve(null),
      ]),
    id || kind,
  );
  return (
    <>
      <AppBar
        title={`${id ? (params.cancel ? "Anular" : "Corrigir") : "Registrar"} ${kindLabel[kind].toLowerCase()}`}
        back
      />
      <ScreenBody>
        {error && data && <ErrorMessage message={error} />}
        {loading && !data ? (
          <LoadingBody />
        ) : error && !data ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <OperationEditor
              key={id || kind}
              kind={kind}
              original={data[2]}
              products={data[0]}
              auxiliaries={data[1]}
              cancel={!!params.cancel}
              reload={reload}
              onSaved={(op) => navigate("operation-detail", { id: op.id })}
            />
          )
        )}
      </ScreenBody>
    </>
  );
}

function OperationEditor({
  kind,
  original,
  products,
  auxiliaries,
  cancel,
  reload,
  onSaved,
}: {
  kind: Kind;
  original: Operation | null;
  products: Product[];
  auxiliaries: Auxiliary[];
  cancel: boolean;
  reload: () => void;
  onSaved: (op: Operation) => void;
}) {
  const [input, setInput] = useState<OperationInput>(() =>
    original
      ? { ...cleanInput(original), cancelled: cancel }
      : {
          kind,
          items: [],
          payments: [],
          notes: null,
          ...(kind === "purchase" ? { purchase_date: localToday() } : {}),
          ...(kind === "adjustment" ? { direction: "in" } : {}),
        },
  );
  const [selected, setSelected] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [newProduct, setNewProduct] = useState(false);
  const [inlineProduct, setInlineProduct] = useState<Product | null>(null);
  const requestKey = useRef(crypto.randomUUID());
  const variants = products.flatMap((p) =>
    p.variants.map((v) => ({
      ...v,
      name: `${p.name} · ${p.print_name} · ${v.size} / ${v.color} · ${v.stock} disponíveis`,
      productActive: p.active,
    })),
  );
  const patch = (value: Partial<OperationInput>) => {
    setInput((prev) => ({ ...prev, ...value }));
    setPreview(null);
    requestKey.current = crypto.randomUUID();
  };
  const itemPatch = (index: number, value: Partial<Item>) =>
    patch({
      items: input.items.map((item, i) =>
        i === index ? { ...item, ...value } : item,
      ),
    });
  const paymentPatch = (index: number, value: Partial<Payment>) =>
    patch({
      payments: input.payments.map((p, i) =>
        i === index ? { ...p, ...value } : p,
      ),
    });
  const options = (group: string, current?: string | null) =>
    auxiliaries.filter(
      (a) => a.kind === group && (a.active || a.id === current),
    );
  async function review(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      setPreview(await api.preview(input, original?.id));
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  async function confirm() {
    if (!preview || busy) return;
    setBusy(true);
    setError(null);
    try {
      onSaved(
        (await api.confirm(input, preview, requestKey.current, original?.id))
          .operation,
      );
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <Note>
        {kind === "inventory"
          ? "Informe somente o estoque físico conhecido. Variantes não incluídas começam zeradas. Custos desconhecidos podem ficar em branco."
          : kind === "purchase"
            ? "Uma compra reúne os itens de um fornecedor. Seu salvamento atualiza estoque e custo médio."
            : kind === "sale"
              ? "Confirmar retira as peças do estoque. Pagamentos são registrados separadamente; preço negociado é informado por item."
              : "Ajustes registram diferenças físicas com um motivo. Não substituem correções de compra ou venda."}
      </Note>
      {cancel && (
        <Note>
          A anulação preservará o histórico e retirará os efeitos desta
          operação. Revise o impacto antes de confirmar.
        </Note>
      )}
      <form onSubmit={review} className="form">
        <fieldset disabled={busy || cancel}>
          {kind === "purchase" && (
            <>
              <Field
                label="Data da compra"
                value={input.purchase_date || ""}
                onChange={(value) => patch({ purchase_date: value })}
                type="date"
                required
              />
              <Select
                label="Fornecedor"
                value={input.supplier_id || ""}
                onChange={(value) => patch({ supplier_id: value })}
                options={options("supplier", input.supplier_id)}
                required
              />
            </>
          )}
          {(kind === "purchase" || kind === "sale") && (
            <Select
              label={`Canal de ${kind === "purchase" ? "compra" : "venda"}`}
              value={input.channel_id || ""}
              onChange={(value) => patch({ channel_id: value })}
              options={options(
                kind === "purchase" ? "purchase_channel" : "sale_channel",
                input.channel_id,
              )}
              required
            />
          )}
          {kind === "adjustment" && (
            <Select
              label="Direção"
              value={input.direction || "in"}
              onChange={(value) => patch({ direction: value as "in" | "out" })}
              options={[
                { id: "in", name: "Entrada" },
                { id: "out", name: "Saída" },
              ]}
              required
            />
          )}
          <Section title="Itens">
            <Select
              label="Peça e variante"
              value={selected}
              onChange={setSelected}
              options={variants.filter(
                (v) =>
                  v.active &&
                  v.productActive &&
                  !input.items.some((i) => i.variant_id === v.id),
              )}
            />
            <Options>
              <Button
                disabled={!selected}
                onClick={() => {
                  const v = variants.find((v) => v.id === selected)!;
                  patch({
                    items: [
                      ...input.items,
                      {
                        variant_id: v.id,
                        quantity: 1,
                        ...(kind === "sale"
                          ? { unit_price: v.reference_price || "" }
                          : {
                              unit_cost:
                                kind === "inventory"
                                  ? v.reference_cost
                                  : kind === "adjustment"
                                    ? v.average_cost
                                    : v.reference_cost || "",
                            }),
                      },
                    ],
                  });
                  setSelected("");
                }}
              >
                Adicionar item
              </Button>
              {kind === "purchase" && (
                <Button onClick={() => setNewProduct((value) => !value)}>
                  Cadastrar peça durante a compra
                </Button>
              )}
            </Options>
            {input.items.map((item, index) => (
              <Card key={item.variant_id}>
                <p>
                  {variants.find((v) => v.id === item.variant_id)?.name ||
                    item.variant_id}
                </p>
                <div className="grid">
                  <Field
                    label="Quantidade inteira"
                    type="number"
                    value={String(item.quantity)}
                    onChange={(value) =>
                      itemPatch(index, { quantity: Number(value) })
                    }
                    required
                  />
                  {kind === "sale" ? (
                    <Field
                      label="Preço negociado por unidade"
                      type="number"
                      value={item.unit_price || ""}
                      onChange={(value) =>
                        itemPatch(index, { unit_price: value })
                      }
                      required
                    />
                  ) : (
                    (kind !== "adjustment" || input.direction === "in") && (
                      <Field
                        label={
                          kind === "inventory"
                            ? "Custo conhecido (opcional)"
                            : kind === "adjustment"
                              ? "Custo se ainda desconhecido"
                              : "Custo unitário"
                        }
                        type="number"
                        value={item.unit_cost || ""}
                        onChange={(value) =>
                          itemPatch(index, { unit_cost: value || null })
                        }
                        required={kind === "purchase"}
                      />
                    )
                  )}
                </div>
                <Button
                  danger
                  onClick={() =>
                    patch({ items: input.items.filter((_, i) => i !== index) })
                  }
                >
                  Retirar item
                </Button>
              </Card>
            ))}
          </Section>
          {kind === "sale" && (
            <Section title="Pagamentos recebidos">
              <Note>
                Sem pagamento inicial, a venda ficará pendente. Não há
                vencimento nem agenda de parcelas.
              </Note>
              {input.payments.map((payment, index) => (
                <Card key={payment.id || index}>
                  <Field
                    label="Valor recebido"
                    type="number"
                    value={payment.amount}
                    onChange={(value) => paymentPatch(index, { amount: value })}
                    required
                  />
                  <Select
                    label="Forma de pagamento"
                    value={payment.method_id}
                    onChange={(value) =>
                      paymentPatch(index, { method_id: value })
                    }
                    options={options("payment_method", payment.method_id)}
                    required
                  />
                  <Button
                    danger
                    onClick={() =>
                      patch({
                        payments: input.payments.filter((_, i) => i !== index),
                      })
                    }
                  >
                    Remover pagamento
                  </Button>
                </Card>
              ))}
              <Button
                onClick={() =>
                  patch({
                    payments: [
                      ...input.payments,
                      { amount: "", method_id: "" },
                    ],
                  })
                }
              >
                Adicionar pagamento
              </Button>
            </Section>
          )}
          <Field
            label="Observação (opcional)"
            value={input.notes || ""}
            onChange={(value) => patch({ notes: value || null })}
          />
        </fieldset>
        {(original || kind === "adjustment") && (
          <Field
            label="Motivo obrigatório"
            value={input.reason || ""}
            onChange={(value) => patch({ reason: value })}
            required
          />
        )}
        <ErrorMessage message={error} />
        <Button
          type="submit"
          disabled={busy || (!input.items.length && kind !== "inventory")}
        >
          Revisar efeitos antes de confirmar
        </Button>
      </form>
      {newProduct && (
        <Card>
          <h3>Nova peça</h3>
          <ProductForm
            auxiliaries={auxiliaries}
            onSaved={(p) => {
              setInlineProduct(p);
              reload();
            }}
          />
          {inlineProduct && (
            <>
              <h4>Adicionar variante a {inlineProduct.name}</h4>
              <VariantForm
                product={inlineProduct}
                onSaved={() => {
                  setNewProduct(false);
                  setInlineProduct(null);
                  reload();
                }}
              />
            </>
          )}
        </Card>
      )}
      {preview && (
        <Section title="Confirmação">
          <Card>
            <OperationSummary operation={preview.operation} />
            <h4>Efeitos no estoque</h4>
            {input.items.map((i) => {
              const state = preview.stock[i.variant_id];
              return (
                <p key={i.variant_id}>
                  {variants.find((v) => v.id === i.variant_id)?.name}: ficará
                  com {state?.stock} · custo médio {brl(state?.average_cost)}
                </p>
              );
            })}
            <h4>Registros posteriores afetados: {preview.affected.length}</h4>
            {preview.affected.map((row) => (
              <div key={row.id}>
                <p>
                  {kindLabel[row.kind]} · {row.id.slice(0, 8)}
                </p>
                <p>
                  Custo histórico: {brl(row.before.historical_cost)} →{" "}
                  {brl(row.after.historical_cost)}
                </p>
                <p>
                  Resultado bruto: {brl(row.before.gross_result)} →{" "}
                  {brl(row.after.gross_result)}
                </p>
              </div>
            ))}
            <Button disabled={busy} danger={cancel} onClick={confirm}>
              {busy
                ? "Salvando…"
                : cancel
                  ? "Confirmar anulação"
                  : "Confirmar operação e efeitos apresentados"}
            </Button>
          </Card>
        </Section>
      )}
    </>
  );
}
