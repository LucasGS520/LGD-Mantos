import { http, request } from "../../shared/api/http";
import type { Operation, OperationInput, Preview, State } from "./contracts";
export const api = {
  list: () => http.get<Operation[]>("/operations"),
  detail: (id: string) => http.get<Operation>(`/operations/${id}`),
  state: () => http.get<State>("/state"),
  preview: (data: OperationInput, id?: string) =>
    request<Preview>(
      id ? `/operations/${id}/preview` : "/operations/preview",
      "POST",
      data,
    ),
  confirm: (data: OperationInput, preview: Preview, key: string, id?: string) =>
    request<Preview>(
      id ? `/operations/${id}` : "/operations",
      id ? "PUT" : "POST",
      { data, preview_token: preview.preview_token },
      key,
    ),
};
