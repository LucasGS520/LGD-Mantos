import type { Money } from "../../shared/api/contracts";
import type { Photo } from "../photos/contracts";
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

export interface ProductInput {
  name: string;
  print_name: string;
  brand: string | null;
  model: string | null;
  category_id: string | null;
  notes: string | null;
  active: boolean;
  accept_similar: boolean;
  version?: number;
  reason?: string;
}
export interface VariantInput {
  size: string;
  color: string;
  reference_cost: string | null;
  reference_price: string | null;
  active: boolean;
  version?: number;
  reason?: string;
}
