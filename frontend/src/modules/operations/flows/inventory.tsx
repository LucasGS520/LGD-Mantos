import type { Variant } from "../../catalog/contracts";
export const inventoryFlow = {
  note: "Informe somente o estoque físico conhecido. Variantes não incluídas começam zeradas. Custos desconhecidos podem ficar em branco.",
  costLabel: "Custo conhecido (opcional)",
  initialValue: (variant: Variant) => ({ unit_cost: variant.reference_cost }),
};
export function InventoryFields() {
  return null;
}
