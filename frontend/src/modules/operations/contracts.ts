import type { Money } from "../../shared/api/contracts";
export type Kind = "inventory" | "purchase" | "sale" | "adjustment";

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
  sequence: number;
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
