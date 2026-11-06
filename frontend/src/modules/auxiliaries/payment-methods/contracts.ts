import type { Auxiliary } from "../contracts";
export type PaymentMethodsRecord = Omit<Auxiliary, "kind"> & {
  kind: "payment_method";
};
