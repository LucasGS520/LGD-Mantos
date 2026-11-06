import type { Auxiliary } from "../contracts";
export type SuppliersRecord = Omit<Auxiliary, "kind"> & { kind: "supplier" };
