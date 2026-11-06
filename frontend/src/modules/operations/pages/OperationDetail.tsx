import { useNav } from "../../../app/nav";
import { AppBar, ScreenBody } from "../../../components/Chrome";
import { dateLabel } from "../../../shared/format/dates";
import { useData } from "../../../shared/hooks/useData";
import { Card, ErrorBody, LoadingBody, Section } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Options } from "../../../shared/ui/Options";
import { History } from "../../history";
import { api as historyApi } from "../../history/api";
import { api } from "../api";
import { OperationSummary } from "../components/OperationSummary";
export function OperationDetail() {
  const { params, navigate } = useNav();
  const id = params.id as string;
  const { data, loading, error, reload } = useData(() => api.detail(id), id);
  const movementQuery = useData(() => historyApi.movements(id), id);
  const movements = movementQuery.data || [];
  return (
    <>
      <AppBar title="Detalhe da operação" back />
      <ScreenBody>
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <>
              <Card>
                <OperationSummary operation={data} />
              </Card>
              {!data.cancelled && (
                <Options>
                  <Button
                    onClick={() =>
                      navigate("operation-form", { id, kind: data.kind })
                    }
                  >
                    {data.kind === "sale"
                      ? "Corrigir venda ou pagamentos"
                      : "Corrigir registro"}
                  </Button>
                  {data.kind !== "inventory" && (
                    <Button
                      danger
                      onClick={() =>
                        navigate("operation-form", {
                          id,
                          kind: data.kind,
                          cancel: true,
                        })
                      }
                    >
                      Anular registro
                    </Button>
                  )}
                </Options>
              )}
              <Section title="Movimentações vinculadas">
                {movementQuery.loading && <p>Carregando movimentos…</p>}
                {movementQuery.error && (
                  <ErrorBody
                    msg={movementQuery.error}
                    onRetry={movementQuery.reload}
                  />
                )}
                {movements.map((m) => (
                  <p key={m.id}>
                    {m.delta > 0 ? "+" : ""}
                    {m.delta} unidades · versão {m.version} ·{" "}
                    {dateLabel(m.created_at)} · {m.reason}
                  </p>
                ))}
              </Section>
              <History id={id} />
            </>
          )
        )}
      </ScreenBody>
    </>
  );
}
