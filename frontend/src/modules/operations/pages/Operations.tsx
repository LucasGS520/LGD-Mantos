import { useNav } from "../../../app/nav";
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
  const { data, loading, error, reload } = useData(
    () => Promise.all([api.list(), api.state()]),
    kind,
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
      </ScreenBody>
    </>
  );
}
