import { brl } from "../../../shared/format/money";
import { Card } from "../../../shared/ui";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import type { ViewProps } from "./contracts";
export function StockView({
  data,
  navigate,
  sort,
  setSort,
  sources,
}: Pick<ViewProps, "data" | "navigate" | "sort" | "setSort" | "sources">) {
  return (
    <>
      <Note>
        Estado atual, independente do intervalo. O tempo representa dias desde a
        primeira entrada conhecida; não há rastreio individual das peças.
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
        {data.summary.unknown_stock_units} unidades sem custo conhecido
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
                onClick={() => navigate("product", { id: s.product_id })}
              >
                {s.name} · {s.size} / {s.color}
              </button>
            </h3>
            <p>
              {s.stock} disponíveis · {s.sold} vendidos · {s.situation}
            </p>
            <p>
              Primeira entrada há {s.days_since_first_entry ?? "—"} dias ·
              última venda há {s.days_since_last_sale ?? "—"} dias
            </p>
            <p>
              Custo médio {brl(s.average_cost)} · valor {brl(s.stock_value)}
            </p>
            {!!s.unknown && (
              <Note>
                Parcela conhecida: {brl(s.known_stock_value)}; {s.unknown}{" "}
                unidades sem custo.
              </Note>
            )}
            {sources(s.operation_ids)}
          </Card>
        ))}
    </>
  );
}
