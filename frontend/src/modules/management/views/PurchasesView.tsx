import { brl } from "../../../shared/format/money";
import { Section } from "../../../shared/ui";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import type { ViewProps } from "./contracts";
export function PurchasesView({
  data,
  opLink,
  supplier,
  setSupplier,
  suppliers,
}: Pick<
  ViewProps,
  "data" | "opLink" | "supplier" | "setSupplier" | "suppliers"
>) {
  return (
    <>
      <Select
        label="Fornecedor (opcional)"
        value={supplier}
        onChange={setSupplier}
        options={suppliers}
      />
      <p>
        {data.purchase_totals[supplier || "all"]?.units || 0} unidades compradas
        · {brl(data.purchase_totals[supplier || "all"]?.total || "0.00")}
      </p>
      {data.purchases
        .filter((op) => !supplier || op.payload.supplier_id === supplier)
        .map(opLink)}
      <Note>{data.evidence.supplier_limitation}</Note>
      {supplier && (
        <Section title="Produtos adquiridos e situação atual">
          {data.stock
            .filter((s) =>
              data.purchases.some(
                (op) =>
                  op.payload.supplier_id === supplier &&
                  op.result.items.some((i) => i.variant_id === s.variant_id),
              ),
            )
            .map((s) => (
              <p key={s.variant_id}>
                {s.name} · {s.size} / {s.color}: {s.stock} em estoque, {s.sold}{" "}
                vendidos no histórico completo
              </p>
            ))}
        </Section>
      )}
    </>
  );
}
