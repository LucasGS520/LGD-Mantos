import type { Payment } from "../contracts";
export const addPayment = (payments: Payment[]): Payment[] => [
  ...payments,
  { amount: "", method_id: "" },
];
export const editPayment = (
  payments: Payment[],
  index: number,
  value: Partial<Payment>,
): Payment[] =>
  payments.map((payment, i) =>
    i === index ? { ...payment, ...value } : payment,
  );
export const removePayment = (payments: Payment[], index: number): Payment[] =>
  payments.filter((_, i) => i !== index);
