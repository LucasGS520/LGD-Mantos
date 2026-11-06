import { brl } from "../../../shared/format/money";
import { Section } from "../../../shared/ui";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import { attrLabels } from "../labels";
import type { ViewProps } from "./contracts";
export function SalesView({
  data,
  attribute,
  setAttribute,
  groups,
  opLink,
}: Pick<
  ViewProps,
  "data" | "attribute" | "setAttribute" | "groups" | "opLink"
>) {
  return (
    <>
      <p>
        Vendido {brl(data.summary.sold)} · {data.summary.sold_units} unidades
      </p>
      <p>
        Custo histórico: {brl(data.summary.historical_cost)} · Resultado bruto:{" "}
        {brl(data.summary.gross_result)}
      </p>
      {!!data.summary.unknown_cost_units && (
        <Note>
          {data.summary.unknown_cost_units} unidades sem custo. Parcela de custo
          conhecida: {brl(data.summary.known_cost)}. A margem total não está
          completa.
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
        {Array.from(new Set(data.sales.map((op) => op.payload.channel_id))).map(
          (id) => (
            <div key={id}>
              <h3>
                {
                  data.sales.find((op) => op.payload.channel_id === id)?.payload
                    .labels.channel_id
                }
              </h3>
              {data.sales
                .filter((op) => op.payload.channel_id === id)
                .map(opLink)}
            </div>
          ),
        )}
      </Section>
    </>
  );
}
