import type { Auxiliary } from "../contracts";
export type PurchaseChannelsRecord = Omit<Auxiliary, "kind"> & {
  kind: "purchase_channel";
};
