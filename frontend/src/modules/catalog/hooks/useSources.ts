import { useData } from "../../../shared/hooks/useData";
import { api as auxiliaryApi } from "../../auxiliaries/api";
import { api as operationApi } from "../../operations/api";
import { api } from "../api";
export function useSources() {
  return useData(() =>
    Promise.all([api.products(), auxiliaryApi.all(), operationApi.state()]),
  );
}
