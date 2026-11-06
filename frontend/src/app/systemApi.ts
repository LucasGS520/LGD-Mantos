import { http } from "../shared/api/http";
export const systemApi = {
  health: () => http.get<{ database: string; version: string }>("/health"),
};
