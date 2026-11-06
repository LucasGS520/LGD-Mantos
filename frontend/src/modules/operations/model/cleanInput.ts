import { type Operation, type OperationInput } from "../contracts";
export function cleanInput(op: Operation): OperationInput {
  return {
    kind: op.kind,
    purchase_date: op.payload.purchase_date,
    supplier_id: op.payload.supplier_id,
    channel_id: op.payload.channel_id,
    direction: op.payload.direction,
    items: op.payload.items.map((i) => ({
      variant_id: i.variant_id,
      quantity: i.quantity,
      ...(op.kind === "sale"
        ? { unit_price: i.unit_price }
        : { unit_cost: i.unit_cost }),
    })),
    payments: op.payload.payments.map((p) => ({
      id: p.id,
      amount: p.amount,
      method_id: p.method_id,
    })),
    notes: op.payload.notes,
    version: op.version,
    reason: "",
    cancelled: false,
  };
}
