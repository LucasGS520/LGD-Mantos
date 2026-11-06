import { dateLabel } from "../../shared/format/dates";
import { useData } from "../../shared/hooks/useData";
import { ErrorBody, Section } from "../../shared/ui";
import { api } from "./api";
import { HistoryVersion } from "./HistoryVersion";
export function History({ id }: { id: string }) {
  const { data, loading, error, reload } = useData(() => api.history(id), id);
  const actionLabels: Record<string, string> = {
    create: "Registro",
    edit: "Correção",
    cancel: "Anulação",
    recalculate: "Recálculo",
    remove: "Remoção",
  };
  return (
    <Section title="Histórico preservado">
      {loading ? (
        <p>Carregando…</p>
      ) : error ? (
        <ErrorBody msg={error} onRetry={reload} />
      ) : (
        data?.map((revision) => (
          <details key={revision.id}>
            <summary>
              {dateLabel(revision.created_at)} ·{" "}
              {actionLabels[revision.action] || revision.action} ·{" "}
              {revision.reason}
            </summary>
            <div className="grid">
              <HistoryVersion label="Antes" value={revision.before} />
              <HistoryVersion label="Depois" value={revision.after} />
            </div>
          </details>
        ))
      )}
    </Section>
  );
}
