import { http, request } from "../../shared/api/http";
import { Session } from "../auth";
import type { Photo, PhotoInput } from "./contracts";
const BASE = (
  (import.meta.env.VITE_API_URL as string | undefined)?.trim() || "/api/v1"
).replace(/\/+$/, "");
export const api = {
  organize: (id: string, input: PhotoInput) =>
    http.put<Photo>(`/photos/${id}`, input),
  remove: (id: string) => http.remove(`/photos/${id}`),
  upload: async (id: string, file: File) => {
    const data = new FormData();
    data.append("file", file);
    return request<Photo>(`/products/${id}/photos`, "POST", data);
  },
  photo: async (id: string) => {
    const res = await fetch(`${BASE}/photos/${id}/content`, {
      headers: { Authorization: `Bearer ${Session.load()}` },
    });
    if (res.status === 401) {
      Session.clear();
      window.dispatchEvent(new Event("session-expired"));
    }
    if (!res.ok) throw new Error("Foto indisponível");
    return URL.createObjectURL(await res.blob());
  },
};
