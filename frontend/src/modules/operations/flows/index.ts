import { AdjustmentFields, adjustmentFlow } from "./adjustments";
import { InventoryFields, inventoryFlow } from "./inventory";
import { PurchaseFields, purchaseFlow } from "./purchases";
import { SaleFields, saleFlow } from "./sales";
export const flows = {
  inventory: { ...inventoryFlow, Fields: InventoryFields },
  purchase: { ...purchaseFlow, Fields: PurchaseFields },
  sale: { ...saleFlow, Fields: SaleFields },
  adjustment: { ...adjustmentFlow, Fields: AdjustmentFields },
};
