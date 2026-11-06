import { Select } from "../../../shared/ui/Select";
import type { Variant } from "../../catalog/contracts";
import { useEditor } from "../hooks/EditorContext";
export const adjustmentFlow = {
  note: "Ajustes registram diferenças físicas com um motivo. Não substituem correções de compra ou venda.",
  costLabel: "Custo se ainda desconhecido",
  initialValue: (variant: Variant) => ({ unit_cost: variant.average_cost }),
};
export function AdjustmentFields() {
  const { input, patch } = useEditor();
  return (
    <Select
      label="Direção"
      value={input.direction || "in"}
      required
      onChange={(value) => patch({ direction: value as "in" | "out" })}
      options={[
        { id: "in", name: "Entrada" },
        { id: "out", name: "Saída" },
      ]}
    />
  );
}
