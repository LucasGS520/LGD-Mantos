import { dateLabel } from "../../../shared/format/dates";
import { brl } from "../../../shared/format/money";
import { Card, Section } from "../../../shared/ui";
import type { ViewProps } from "./contracts";
export function ReceiptsView({
  data,
  sources,
  opLink,
}: Pick<ViewProps, "data" | "sources" | "opLink">) {
  return (
    <>
      <p>Vendido no intervalo: {brl(data.summary.sold)}</p>
      <p>
        Recebido no intervalo: {brl(data.summary.received)} · Saldo pendente
        atual: {brl(data.summary.pending)}
      </p>
      <Section title="Pagamentos do intervalo">
        {data.payments.map((p) => (
          <Card key={p.id}>
            <p>
              {brl(p.amount)} · {p.method_name} · {dateLabel(p.created_at)}
            </p>
            {sources([p.sale_id])}
          </Card>
        ))}
      </Section>
      <Section title="Vendas pendentes atuais">
        {data.pending_sales.map(opLink)}
      </Section>
    </>
  );
}
