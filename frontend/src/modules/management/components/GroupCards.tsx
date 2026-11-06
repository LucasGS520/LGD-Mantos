import { brl } from "../../../shared/format/money";
import { Card } from "../../../shared/ui";
import { Note } from "../../../shared/ui/Note";
import type { Group } from "../contracts";
import { SourceLinks } from "./SourceLinks";
export function GroupCards({ rows }: { rows: Group[] }) {
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
      {<SourceLinks ids={g.sale_ids} />}
    </Card>
  ));
}
