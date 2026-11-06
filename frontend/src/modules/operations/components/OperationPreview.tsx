import { brl } from "../../../shared/format/money";
import { Card, Section } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { useEditor } from "../hooks/EditorContext";
import { kindLabel } from "../labels";
import { OperationSummary } from "./OperationSummary";
export function OperationPreview() {
  const { cancel, input, preview, busy, variants, confirm } = useEditor();
  return (
    <>
      {preview && (
        <Section title="Confirmação">
          <Card>
            <OperationSummary operation={preview.operation} />
            <h4>Efeitos no estoque</h4>
            {input.items.map((i) => {
              const state = preview.stock[i.variant_id];
              return (
                <p key={i.variant_id}>
                  {variants.find((v) => v.id === i.variant_id)?.name}: ficará
                  com {state?.stock} · custo médio {brl(state?.average_cost)}
                </p>
              );
            })}
            <h4>Registros posteriores afetados: {preview.affected.length}</h4>
            {preview.affected.map((row) => (
              <div key={row.id}>
                <p>
                  {kindLabel[row.kind]} · {row.id.slice(0, 8)}
                </p>
                <p>
                  Custo histórico: {brl(row.before.historical_cost)} →{" "}
                  {brl(row.after.historical_cost)}
                </p>
                <p>
                  Resultado bruto: {brl(row.before.gross_result)} →{" "}
                  {brl(row.after.gross_result)}
                </p>
              </div>
            ))}
            <Button disabled={busy} danger={cancel} onClick={confirm}>
              {busy
                ? "Salvando…"
                : cancel
                  ? "Confirmar anulação"
                  : "Confirmar operação e efeitos apresentados"}
            </Button>
          </Card>
        </Section>
      )}
    </>
  );
}
