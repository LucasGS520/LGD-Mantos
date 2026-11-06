import { http } from "../../shared/api/http";
import type { Product, ProductInput, Variant, VariantInput } from "./contracts";
export const api = {
  products: () => http.get<Product[]>("/products"),
  createProduct: (input: ProductInput) =>
    http.post<Product>("/products", input),
  updateProduct: (id: string, input: ProductInput) =>
    http.put<Product>(`/products/${id}`, input),
  createVariant: (id: string, input: VariantInput) =>
    http.post<Variant>(`/products/${id}/variants`, input),
  updateVariant: (id: string, variantId: string, input: VariantInput) =>
    http.put<Variant>(`/products/${id}/variants/${variantId}`, input),
};
