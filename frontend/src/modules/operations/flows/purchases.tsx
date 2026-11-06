import { Field } from "../../../shared/ui/Field";
import { Select } from "../../../shared/ui/Select";
import type { Variant } from "../../catalog/contracts";
import { useEditor } from "../hooks/EditorContext";
export const purchaseFlow = {
  note: "Uma compra reúne os itens de um fornecedor. Seu salvamento atualiza estoque e custo médio.",
  costLabel: "Custo unitário",
  initialValue: (variant: Variant) => ({
    unit_cost: variant.reference_cost || "",
  }),
};
export function PurchaseFields() {
  const { input, patch, options } = useEditor();
  return (
    <>
      <Field
        label="Data da compra"
        value={input.purchase_date || ""}
        type="date"
        required
        onChange={(value) => patch({ purchase_date: value })}
      />
      <Select
        label="Fornecedor"
        value={input.supplier_id || ""}
        required
        onChange={(value) => patch({ supplier_id: value })}
        options={options("supplier", input.supplier_id)}
      />
      <Select
        label="Canal de compra"
        value={input.channel_id || ""}
        required
        onChange={(value) => patch({ channel_id: value })}
        options={options("purchase_channel", input.channel_id)}
      />
    </>
  );
}
