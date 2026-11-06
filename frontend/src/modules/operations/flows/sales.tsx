import { Select } from "../../../shared/ui/Select";
import type { Variant } from "../../catalog/contracts";
import { useEditor } from "../hooks/EditorContext";
export const saleFlow = {
  note: "Confirmar retira as peças do estoque. Pagamentos são registrados separadamente; preço negociado é informado por item.",
  costLabel: "",
  initialValue: (variant: Variant) => ({
    unit_price: variant.reference_price || "",
  }),
};
export function SaleFields() {
  const { input, patch, options } = useEditor();
  return (
    <Select
      label="Canal de venda"
      value={input.channel_id || ""}
      required
      onChange={(value) => patch({ channel_id: value })}
      options={options("sale_channel", input.channel_id)}
    />
  );
}
