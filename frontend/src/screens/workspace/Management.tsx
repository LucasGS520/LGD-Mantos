import {
useEffect,
useState
} from "react";
import { AppBar,BottomNav,ScreenBody } from "../../components/Chrome";
import { Card,ErrorBody,LoadingBody,Section } from "../../components/UI";
import { useData } from "../../hooks/useData";
import { useNav } from "../../nav";
import {
api,
brl,
dateLabel,
type Auxiliary,
type Group,
type Operation,
type Report
} from "../../services/domain";
import "../../styles/workspace.css";

import {
Button,
Field,
Note,
OperationSummary,
Options,
Select,
attrLabels
} from "./Shared";

const views = [
  { id: "overview", name: "Visão geral" },
  { id: "stock", name: "Estoque e giro" },
  { id: "sales", name: "Vendas e margens" },
  { id: "receipts", name: "Recebimentos" },
  { id: "purchases", name: "Compras e fornecedores" },
  { id: "buying", name: "Apoio à próxima compra" },
];
export function Management() {
  const { navigate } = useNav();
  const [view, setView] = useState("overview");
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [filter, setFilter] = useState("");
  const [attribute, setAttribute] = useState("brand");
  const [sort, setSort] = useState("stock");
  const [supplier, setSupplier] = useState("");
  const { data, loading, error, reload } = useData(
    () => api.get<Report>(`/analytics${filter}`),
    filter,
  );
  const [suppliers, setSuppliers] = useState<Auxiliary[]>([]);
  useEffect(() => {
    api
      .get<Auxiliary[]>("/auxiliaries")
      .then((a) => setSuppliers(a.filter((x) => x.kind === "supplier")))
      .catch(() => {});
  }, []);
  const opLink = (op: Operation) => (
    <Card
      key={op.id}
      onClick={() => navigate("operation-detail", { id: op.id })}
    >
      <OperationSummary operation={op} />
      <span>Consultar origem →</span>
    </Card>
  );
  function sources(ids: string[]) {
    return (
      <Options>
        {ids.map((id) => (
          <Button key={id} onClick={() => navigate("operation-detail", { id })}>
            Registro {id.slice(0, 8)}
          </Button>
        ))}
      </Options>
    );
  }
  function groups(rows: Group[]) {
    return rows.map((g) => (
      <Card key={g.attribute + g.label}>
        <h3>{g.label}</h3>
        <p>
          {g.sold} vendidos · {g.stock} em estoque · {brl(g.revenue)} vendidos
        </p>
        <p>
          Resultado bruto: {brl(g.gross_result)} · Margem:{" "}
          {g.gross_margin === null
            ? "Incompleta ou sem vendas"
            : `${g.gross_margin}%`}
        </p>
        {!!g.unknown_cost_units && (
          <Note>
            {g.unknown_cost_units} unidades vendidas sem custo conhecido.
          </Note>
        )}
        {sources(g.sale_ids)}
      </Card>
    ));
  }
  return (
    <>
      <AppBar title="Gestão" subtitle="Informações e suas origens" />
      <ScreenBody>
        <Select label="Visão" value={view} onChange={setView} options={views} />
        {view !== "stock" && (
          <form
            className="form"
            onSubmit={(e) => {
              e.preventDefault();
              const query = new URLSearchParams();
              if (start) query.set("start", start);
              if (end) query.set("end", end);
              setFilter(query.size ? "?" + query : "");
            }}
          >
            <div className="grid">
              <Field
                label="Data inicial (opcional)"
                type="date"
                value={start}
                onChange={setStart}
              />
              <Field
                label="Data final (opcional)"
                type="date"
                value={end}
                onChange={setEnd}
              />
            </div>
            <Button type="submit">Consultar intervalo</Button>
            <Note>
              Sem filtro, todo o histórico confiável. Recebimentos usam a data
              do pagamento; saldos pendentes são a situação atual.
            </Note>
          </form>
        )}
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <>
              {!data.started_at && (
                <Note>
                  Confirme o inventário inicial para estabelecer o início do
                  controle.
                </Note>
              )}
              {view === "overview" && (
                <>
                  <div className="grid">
                    <Metric
                      label="Estoque disponível"
                      value={`${data.summary.stock_units} unidades`}
                      onClick={() => setView("stock")}
                    />
                    <Metric
                      label="Vendido"
                      value={brl(data.summary.sold)}
                      onClick={() => setView("sales")}
                    />
                    <Metric
                      label="Recebido no intervalo"
                      value={brl(data.summary.received)}
                      onClick={() => setView("receipts")}
                    />
                    <Metric
                      label="Saldo pendente atual"
                      value={brl(data.summary.pending)}
                      onClick={() => setView("receipts")}
                    />
                    <Metric
                      label="Margem bruta realizada"
                      value={
                        data.summary.gross_margin === null
                          ? "Incompleta ou sem vendas"
                          : data.summary.gross_margin + "%"
                      }
                      onClick={() => setView("sales")}
                    />
                  </div>
                  <Section title="Pontos de atenção">
                    {data.issues.map((issue, index) => (
                      <p key={index}>
                        <button
                          className="text-link"
                          onClick={() =>
                            navigate("product", { id: issue.product_id })
                          }
                        >
                          {
                            data.stock.find(
                              (s) => s.variant_id === issue.variant_id,
                            )?.name
                          }
                          : {issue.message}
                        </button>
                      </p>
                    ))}
                    {!data.issues.length && (
                      <p>
                        Nenhuma lacuna identificada nos cadastros consultados.
                      </p>
                    )}
                  </Section>
                </>
              )}
              {view === "stock" && (
                <>
                  <Note>
                    Estado atual, independente do intervalo. O tempo representa
                    dias desde a primeira entrada conhecida; não há rastreio
                    individual das peças.
                  </Note>
                  <Select
                    label="Ordenar evidências"
                    value={sort}
                    onChange={setSort}
                    options={[
                      { id: "stock", name: "Quantidade disponível" },
                      {
                        id: "days_since_first_entry",
                        name: "Tempo desde a primeira entrada",
                      },
                      {
                        id: "days_since_last_sale",
                        name: "Tempo desde a última venda",
                      },
                      { id: "stock_value", name: "Valor conhecido em estoque" },
                    ]}
                  />
                  <p>
                    Valor conhecido: {brl(data.summary.stock_value)} ·{" "}
                    {data.summary.unknown_stock_units} unidades sem custo
                    conhecido
                  </p>
                  {[...data.stock]
                    .sort(
                      (a, b) =>
                        Number(b[sort as keyof typeof b] ?? -1) -
                        Number(a[sort as keyof typeof a] ?? -1),
                    )
                    .map((s) => (
                      <Card key={s.variant_id}>
                        <h3>
                          <button
                            className="text-link"
                            onClick={() =>
                              navigate("product", { id: s.product_id })
                            }
                          >
                            {s.name} · {s.size} / {s.color}
                          </button>
                        </h3>
                        <p>
                          {s.stock} disponíveis · {s.sold} vendidos ·{" "}
                          {s.situation}
                        </p>
                        <p>
                          Primeira entrada há {s.days_since_first_entry ?? "—"}{" "}
                          dias · última venda há {s.days_since_last_sale ?? "—"}{" "}
                          dias
                        </p>
                        <p>
                          Custo médio {brl(s.average_cost)} · valor{" "}
                          {brl(s.stock_value)}
                        </p>
                        {!!s.unknown && <Note>Parcela conhecida: {brl(s.known_stock_value)}; {s.unknown} unidades sem custo.</Note>}
                        {sources(s.operation_ids)}
                      </Card>
                    ))}
                </>
              )}
              {view === "sales" && (
                <>
                  <p>
                    Vendido {brl(data.summary.sold)} · {data.summary.sold_units}{" "}
                    unidades
                  </p>
                  <p>
                    Custo histórico: {brl(data.summary.historical_cost)} ·
                    Resultado bruto: {brl(data.summary.gross_result)}
                  </p>
                  {!!data.summary.unknown_cost_units && (
                    <Note>
                      {data.summary.unknown_cost_units} unidades sem custo.
                      Parcela de custo conhecida: {brl(data.summary.known_cost)}
                      . A margem total não está completa.
                    </Note>
                  )}
                  {data.sales.map(opLink)}
                  <Select
                    label="Agrupar desempenho"
                    value={attribute}
                    onChange={setAttribute}
                    options={Object.entries(attrLabels).map(([id, name]) => ({
                      id,
                      name,
                    }))}
                  />
                  {groups(data.groups.filter((g) => g.attribute === attribute))}
                  <Section title="Vendas por canal">
                    {Array.from(
                      new Set(data.sales.map((op) => op.payload.channel_id)),
                    ).map((id) => (
                      <div key={id}>
                        <h3>
                          {
                            data.sales.find(
                              (op) => op.payload.channel_id === id,
                            )?.payload.labels.channel_id
                          }
                        </h3>
                        {data.sales
                          .filter((op) => op.payload.channel_id === id)
                          .map(opLink)}
                      </div>
                    ))}
                  </Section>
                </>
              )}
              {view === "receipts" && (
                <>
                  <p>Vendido no intervalo: {brl(data.summary.sold)}</p>
                  <p>
                    Recebido no intervalo: {brl(data.summary.received)} · Saldo
                    pendente atual: {brl(data.summary.pending)}
                  </p>
                  <Section title="Pagamentos do intervalo">
                    {data.payments.map((p) => (
                      <Card key={p.id}>
                        <p>
                          {brl(p.amount)} · {p.method_name} ·{" "}
                          {dateLabel(p.created_at)}
                        </p>
                        {sources([p.sale_id])}
                      </Card>
                    ))}
                  </Section>
                  <Section title="Vendas pendentes atuais">
                    {data.pending_sales.map(opLink)}
                  </Section>
                </>
              )}
              {view === "purchases" && (
                <>
                  <Select
                    label="Fornecedor (opcional)"
                    value={supplier}
                    onChange={setSupplier}
                    options={suppliers}
                  />
                  <p>
                    {data.purchase_totals[supplier || "all"]?.units || 0}{" "}
                    unidades compradas ·{" "}
                    {brl(
                      data.purchase_totals[supplier || "all"]?.total || "0.00",
                    )}
                  </p>
                  {data.purchases
                    .filter(
                      (op) => !supplier || op.payload.supplier_id === supplier,
                    )
                    .map(opLink)}
                  <Note>{data.evidence.supplier_limitation}</Note>
                  {supplier && (
                    <Section title="Produtos adquiridos e situação atual">
                      {data.stock
                        .filter((s) =>
                          data.purchases.some(
                            (op) =>
                              op.payload.supplier_id === supplier &&
                              op.result.items.some(
                                (i) => i.variant_id === s.variant_id,
                              ),
                          ),
                        )
                        .map((s) => (
                          <p key={s.variant_id}>
                            {s.name} · {s.size} / {s.color}: {s.stock} em
                            estoque, {s.sold} vendidos no histórico completo
                          </p>
                        ))}
                    </Section>
                  )}
                </>
              )}
              {view === "buying" && (
                <>
                  <Note>{data.evidence.message}</Note>
                  <p>
                    Controle iniciado em{" "}
                    {dateLabel(data.evidence.observed_since)} ·{" "}
                    {data.evidence.sale_count} vendas e{" "}
                    {data.evidence.purchase_count} compras no intervalo.
                  </p>
                  <Select
                    label="Característica observada"
                    value={attribute}
                    onChange={setAttribute}
                    options={Object.entries(attrLabels).map(([id, name]) => ({
                      id,
                      name,
                    }))}
                  />
                  {groups(
                    data.groups
                      .filter((g) => g.attribute === attribute)
                      .sort((a, b) => b.sold - a.sold),
                  )}
                  <Note>
                    Estampas não precisam ser recompradas. Use estas evidências
                    para escolher novas peças com características relevantes.
                    Nenhuma ação comercial é executada automaticamente.
                  </Note>
                </>
              )}
            </>
          )
        )}
      </ScreenBody>
      <BottomNav active="intel" />
    </>
  );
}

function Metric({
  label,
  value,
  onClick,
}: {
  label: string;
  value: string;
  onClick: () => void;
}) {
  return (
    <Card onClick={onClick}>
      <p>{label}</p>
      <strong className="metric">{value}</strong>
      <p>Ver registros →</p>
    </Card>
  );
}
