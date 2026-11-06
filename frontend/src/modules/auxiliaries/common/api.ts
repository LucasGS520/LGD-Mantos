import { http } from "../../../shared/api/http";
import type { Auxiliary, RecordValues } from "../contracts";

/** Reutiliza o transporte dos cadastros e fixa seu tipo em cada capacidade. */
export function createAuxiliaryApi<K extends string>(kind: K) {
  type Record = Auxiliary & { kind: K };
  return {
    list: async () =>
      (await http.get<Auxiliary[]>("/auxiliaries")).filter(
        (record): record is Record => record.kind === kind,
      ),
    save: (values: RecordValues, editing: Record | null) =>
      editing
        ? http.put<Record>(`/auxiliaries/${editing.id}`, { ...values, kind })
        : http.post<Record>("/auxiliaries", { ...values, kind }),
  };
}
