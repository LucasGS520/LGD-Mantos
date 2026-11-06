import { http } from "../../shared/api/http";
import type { Report } from "./contracts";
export const api = {
  report: (filter: string) => http.get<Report>(`/analytics${filter}`),
};
