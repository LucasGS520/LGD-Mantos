import { Session } from "./session";

export type Money = string | null;
export type Kind = "inventory" | "purchase" | "sale" | "adjustment";
export interface Auxiliary {
  id: string;
  kind: string;
  name: string;
  notes: string | null;
  active: boolean;
  version: number;
}
export interface Variant {
  id: string;
  product_id: string;
  code: string;
  size: string;
  color: string;
  reference_cost: Money;
  reference_price: Money;
  stock: number;
  average_cost: Money;
  active: boolean;
  version: number;
}
export interface Photo {
  id: string;
  product_id: string;
  position: number;
  primary: boolean;
  variant_id: string | null;
  color: string | null;
}
export interface Product {
  id: string;
  name: string;
  print_name: string;
  brand: string | null;
  model: string | null;
  category_id: string | null;
  notes: string | null;
  active: boolean;
  version: number;
  variants: Variant[];
  photos: Photo[];
}
export interface Item {
  variant_id: string;
  quantity: number;
  unit_cost?: Money;
  unit_price?: Money;
  product_name?: string;
  print_name?: string;
  size?: string;
  color?: string;
  reference_price?: Money;
  known_cost?: Money;
  unknown_cost_units?: number;
}
export interface Payment {
  id?: string;
  amount: string;
  method_id: string;
  method_name?: string;
  created_at?: string;
}
export interface OperationInput {
  kind: Kind;
  purchase_date?: string | null;
  supplier_id?: string | null;
  channel_id?: string | null;
  direction?: "in" | "out" | null;
  items: Item[];
  payments: Payment[];
  notes: string | null;
  reason?: string | null;
  version?: number;
  cancelled?: boolean;
}
export interface Result {
  items: Item[];
  effects: Record<string, number>;
  total?: string;
  received?: string;
  balance?: string;
  financial_status?: string;
  historical_cost?: Money;
  gross_result?: Money;
  gross_margin?: Money;
  commercial_difference?: Money;
  unknown_cost_units?: number;
}
export interface Operation {
  id: string;
  kind: Kind;
  effective_at: string;
  created_at: string;
  version: number;
  cancelled: boolean;
  payload: OperationInput & { labels: Record<string, string> };
  result: Result;
}
export interface Preview {
  operation: Operation;
  affected: { id: string; kind: Kind; before: Result; after: Result }[];
  stock: Record<string, { stock: number; average_cost: Money }>;
  preview_token: string;
}
export interface State {
  revision: number;
  started_at: string | null;
}
export interface Revision {
  id: string;
  action: string;
  reason: string;
  created_at: string;
  before: Record<string, unknown> | null;
  after: Record<string, unknown> | null;
}
export interface StockRow {
  variant_id: string;
  product_id: string;
  name: string;
  print_name: string;
  brand: string | null;
  model: string | null;
  category: string | null;
  size: string;
  color: string;
  stock: number;
  sold: number;
  unknown: number;
  average_cost: Money;
  stock_value: Money;
  days_since_first_entry: number | null;
  days_since_last_sale: number | null;
  situation: string;
  operation_ids: string[];
}
export interface Group {
  attribute: string;
  label: string;
  sold: number;
  stock: number;
  revenue: Money;
  gross_result: Money;
  gross_margin: Money;
  unknown_cost_units: number;
  sale_ids: string[];
  product_ids: string[];
}
export interface Report {
  started_at: string | null;
  summary: {
    stock_units: number;
    sold_units: number;
    sold: string;
    received: string;
    pending: string;
    historical_cost: Money;
    known_cost: string;
    unknown_cost_units: number;
    gross_result: Money;
    gross_margin: Money;
    stock_value: string;
    unknown_stock_units: number;
  };
  stock: StockRow[];
  sales: Operation[];
  purchases: Operation[];
  payments: (Payment & { sale_id: string })[];
  pending_sales: Operation[];
  groups: Group[];
  issues: {
    product_id: string;
    variant_id: string;
    message: string;
    optional?: boolean;
  }[];
  evidence: {
    observed_since: string | null;
    sale_count: number;
    purchase_count: number;
    message: string;
    supplier_limitation: string;
  };
}

const BASE = (
  (import.meta.env.VITE_API_URL as string | undefined)?.trim() || "/api/v1"
).replace(/\/+$/, "");
let onUnauthorized: (() => void) | null = null;
export function setUnauthorizedHandler(fn: () => void) {
  onUnauthorized = fn;
}

async function request<T>(
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
    throw new Error(
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

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) => request<T>(path, "POST", body),
  put: <T>(path: string, body: unknown) => request<T>(path, "PUT", body),
  remove: (path: string) => request(path, "DELETE"),
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
      onUnauthorized?.();
    }
    if (!res.ok) throw new Error("Foto indisponível");
    return URL.createObjectURL(await res.blob());
  },
  login: async (password: string) => {
    const data = await request<{ token: string }>("/auth/login", "POST", {
      password,
    });
    Session.save(data.token);
    return data.token;
  },
};
export const brl = (value: Money | number | undefined) =>
  value === null || value === undefined
    ? "Não informado"
    : Number(value).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
      });
export const dateLabel = (value?: string | null) =>
  value
    ? new Date(value).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo" })
    : "Não informado";
export const kindLabel: Record<Kind, string> = {
  inventory: "Inventário inicial",
  purchase: "Compra",
  sale: "Venda",
  adjustment: "Ajuste",
};
export const localToday = () =>
  new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Sao_Paulo",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());

export interface Report {
  purchase_totals: Record<string, { units: number; total: string }>;
}
export interface StockRow {
  known_stock_value: Money;
}
