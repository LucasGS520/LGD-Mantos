import type { Money } from "../../shared/api/contracts";
import type { Operation, Payment } from "../operations/contracts";
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
export interface StockRow {
  known_stock_value: Money;
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
export interface Report {
  purchase_totals: Record<string, { units: number; total: string }>;
}
