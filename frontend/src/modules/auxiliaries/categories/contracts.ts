import type { Auxiliary } from "../contracts";
export type CategoriesRecord = Omit<Auxiliary, "kind"> & { kind: "category" };
