import { http } from "../../shared/api/http";
import type { Auxiliary } from "./contracts";
export const api = { all: () => http.get<Auxiliary[]>("/auxiliaries") };
