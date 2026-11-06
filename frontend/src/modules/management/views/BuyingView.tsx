import { dateLabel } from "../../../shared/format/dates";
import { Note } from "../../../shared/ui/Note";
import { Select } from "../../../shared/ui/Select";
import { attrLabels } from "../labels";
import type { ViewProps } from "./contracts";
export function BuyingView({
  data,
  attribute,
  setAttribute,
  groups,
}: Pick<ViewProps, "data" | "sort" | "attribute" | "setAttribute" | "groups">) {
  return (
    <>
      <Note>{data.evidence.message}</Note>
      <p>
        Controle iniciado em {dateLabel(data.evidence.observed_since)} ·{" "}
        {data.evidence.sale_count} vendas e {data.evidence.purchase_count}{" "}
        compras no intervalo.
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
        Estampas não precisam ser recompradas. Use estas evidências para
        escolher novas peças com características relevantes. Nenhuma ação
        comercial é executada automaticamente.
      </Note>
    </>
  );
}
