import { useNav } from "../../../app/nav";
import { AppBar, ScreenBody } from "../../../components/Chrome";
import { useData } from "../../../shared/hooks/useData";
import { ErrorBody, LoadingBody } from "../../../shared/ui";
import { api as auxiliaryApi } from "../../auxiliaries/api";
import { api as catalogApi } from "../../catalog/api";
import { api } from "../api";
import { OperationEditor } from "../components/OperationEditor";
import { type Kind } from "../contracts";
import { kindLabel } from "../labels";
export function OperationForm() {
  const { params, navigate } = useNav();
  const kind = params.kind as Kind;
  const id = params.id as string | undefined;
  const { data, loading, error, reload } = useData(
    () =>
      Promise.all([
        catalogApi.products(),
        auxiliaryApi.all(),
        id ? api.detail(id) : Promise.resolve(null),
      ]),
    id || kind,
  );
  return (
    <>
      <AppBar
        title={`${id ? (params.cancel ? "Anular" : "Corrigir") : "Registrar"} ${kindLabel[kind].toLowerCase()}`}
        back
      />
      <ScreenBody>
        {error && data && <ErrorBody msg={error} onRetry={reload} />}
        {loading && !data ? (
          <LoadingBody />
        ) : error && !data ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          data && (
            <OperationEditor
              key={id || kind}
              kind={kind}
              original={data[2]}
              products={data[0]}
              auxiliaries={data[1]}
              cancel={!!params.cancel}
              reload={reload}
              onSaved={(op) => navigate("operation-detail", { id: op.id })}
            />
          )
        )}
      </ScreenBody>
    </>
  );
}
