import { useNav } from "../../../app/nav";
import { useState } from "react";
import { AppBar, ScreenBody } from "../../../components/Chrome";
import { useData } from "../../../shared/hooks/useData";
import { Card, ErrorBody, LoadingBody } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Note } from "../../../shared/ui/Note";
import { Options } from "../../../shared/ui/Options";
import { api } from "../api";
import { OperationSummary } from "../components/OperationSummary";
import { type Kind } from "../contracts";
import { kindLabel } from "../labels";
export function Operations() {
  const { params, navigate } = useNav();
  const kind = (params.kind || "sale") as Kind;
  const [paging, setPaging] = useState<{
    kind: string;
    cursors: (number | undefined)[];
  }>({ kind, cursors: [undefined] });
  const cursors = paging.kind === kind ? paging.cursors : [undefined];
  const cursor = cursors[cursors.length - 1];
  const { data, loading, error, reload } = useData(
    () => Promise.all([api.page(kind, cursor), api.state()]),
    `${kind}:${cursor}`,
  );
  const [ops, state] = data || [[], null];
  const visible = ops.filter((op) => op.kind === kind);
  const canCreate =
    state && (kind === "inventory" ? !state.started_at : !!state.started_at);
  return (
    <>
      <AppBar
        title={
          kind === "sale"
            ? "Vendas e recebimentos"
            : kind === "purchase"
              ? "Compras"
              : kindLabel[kind]
        }
        back
      />
      <ScreenBody>
        <Options>
          {canCreate && (
            <Button onClick={() => navigate("operation-form", { kind })}>
              {kind === "inventory"
                ? "Preparar inventário"
                : `Registrar ${kindLabel[kind].toLowerCase()}`}
            </Button>
          )}
        </Options>
        {state && !state.started_at && kind !== "inventory" && (
          <Note>
            Confirme o inventário inicial antes de registrar operações.
          </Note>
        )}
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          visible.map((op) => (
            <Card
              key={op.id}
              onClick={() => navigate("operation-detail", { id: op.id })}
            >
              <OperationSummary operation={op} />
              <span>Ver detalhes e histórico →</span>
            </Card>
          ))
        )}
        {!loading && !visible.length && (
          <Note>Nenhum registro neste grupo.</Note>
        )}
        {!loading && !error && (
          <div className="options">
            <Button
              disabled={cursors.length === 1}
              onClick={() => setPaging({ kind, cursors: cursors.slice(0, -1) })}
            >
              Anteriores
            </Button>
            <span>Página {cursors.length} · mais recentes primeiro</span>
            <Button
              disabled={visible.length < 50}
              onClick={() =>
                setPaging({
                  kind,
                  cursors: [...cursors, visible[visible.length - 1].sequence],
                })
              }
            >
              Próximos registros
            </Button>
          </div>
        )}
      </ScreenBody>
    </>
  );
}
