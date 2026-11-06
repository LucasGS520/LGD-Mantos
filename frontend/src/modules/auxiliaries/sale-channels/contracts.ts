import type { Auxiliary } from "../contracts";
export type SaleChannelsRecord = Omit<Auxiliary, "kind"> & {
  kind: "sale_channel";
};
