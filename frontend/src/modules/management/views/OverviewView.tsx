import { brl } from "../../../shared/format/money";
import { Section } from "../../../shared/ui";
import { Metric } from "../components/Metric";
import type { ViewProps } from "./contracts";
export function OverviewView({
  data,
  setView,
  navigate,
}: Pick<ViewProps, "data" | "setView" | "navigate">) {
  return (
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
              onClick={() => navigate("product", { id: issue.product_id })}
            >
              {data.stock.find((s) => s.variant_id === issue.variant_id)?.name}:{" "}
              {issue.message}
            </button>
          </p>
        ))}
        {!data.issues.length && (
          <p>Nenhuma lacuna identificada nos cadastros consultados.</p>
        )}
      </Section>
    </>
  );
}
