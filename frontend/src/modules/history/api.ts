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
    http.get<Movement[]>(
      `/movements?operation_id=${encodeURIComponent(operationId)}`,
    ),
};
