import { useData } from "../../../shared/hooks/useData";
import { api as auxiliaryApi } from "../../auxiliaries/api";
import { api as operationApi } from "../../operations/api";
import { api } from "../api";
export function useSources(productId?: string) {
  return useData(
    () =>
      Promise.all([
        productId ? api.product(productId).then((p) => [p]) : api.products(),
        auxiliaryApi.all(),
        operationApi.state(),
      ]),
    productId,
  );
}
