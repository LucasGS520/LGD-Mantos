import { Session } from "../../modules/auth/session";
import { ApiError } from "./errors";
const BASE = (
  (import.meta.env.VITE_API_URL as string | undefined)?.trim() || "/api/v1"
).replace(/\/+$/, "");
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(fn: () => void) {
  onUnauthorized = fn;
}

export async function request<T>(
  path: string,
  method = "GET",
  body?: unknown,
  key?: string,
): Promise<T> {
  const headers: Record<string, string> = {};
  const token = Session.load();
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined && !(body instanceof FormData))
    headers["Content-Type"] = "application/json";
  if (key) headers["Idempotency-Key"] = key;
  const res = await fetch(BASE + path, {
    method,
    headers,
    body:
      body instanceof FormData
        ? body
        : body !== undefined
          ? JSON.stringify(body)
          : undefined,
  });
  if (res.status === 401) {
    Session.clear();
    onUnauthorized?.();
  }
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    throw new ApiError(
      res.status,
      detail,
      typeof detail === "string"
        ? detail
        : detail?.message ||
            (detail ? JSON.stringify(detail) : `Erro ${res.status}`),
    );
  }
  if (data === null)
    throw new Error("Resposta inválida. Confira a conexão com a API.");
  return data as T;
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, "POST", body),
  put: <T>(path: string, body: unknown) => request<T>(path, "PUT", body),
  remove: (path: string) => request(path, "DELETE"),
};
