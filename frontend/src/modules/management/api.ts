import { http } from "../../shared/api/http";
import type { Report } from "./contracts";
export const api = {
  report: (
    filter: string,
    options?: { view: string; offset: number; supplier: string; sort: string },
  ) => {
    const query = new URLSearchParams(filter.replace(/^\?/, ""));
    if (options) {
      Object.entries(options).forEach(([key, value]) =>
        query.set(key, String(value)),
      );
      query.set("limit", "50");
    }
    return http.get<Report>(`/analytics?${query}`);
  },
};
