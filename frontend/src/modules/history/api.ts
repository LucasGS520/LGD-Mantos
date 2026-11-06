import { http } from "../../shared/api/http";
import type { Revision } from "./contracts";
export interface Movement {
  id: string;
  operation_id: string;
  variant_id: string;
  delta: number;
  version: number;
  reason: string;
  created_at: string;
}
export const api = {
  history: (id: string) => http.get<Revision[]>(`/history/${id}`),
  movements: async (operationId: string) =>
    (await http.get<Movement[]>("/movements")).filter(
      (row) => row.operation_id === operationId,
    ),
};
