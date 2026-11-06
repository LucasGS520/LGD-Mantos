import { Button } from "../../../shared/ui/Button";
import { ErrorMessage } from "../../../shared/ui/ErrorMessage";
import { Field } from "../../../shared/ui/Field";
import { Note } from "../../../shared/ui/Note";
import { flows } from "../flows";
import { EditorContext } from "../hooks/EditorContext";
import {
  useOperationEditor,
  type EditorProps,
} from "../hooks/useOperationEditor";
import { InlineProduct } from "./InlineProduct";
import { OperationFields } from "./OperationFields";
import { OperationItems } from "./OperationItems";
import { OperationPayments } from "./OperationPayments";
import { OperationPreview } from "./OperationPreview";
export function OperationEditor(props: EditorProps) {
  const editor = useOperationEditor(props);
  const { kind, original, cancel, input, error, busy, patch, review } = editor;
  return (
    <EditorContext.Provider value={editor}>
      <Note>{flows[kind].note}</Note>
      {cancel && (
        <Note>
          A anulação preservará o histórico e retirará os efeitos desta
          operação. Revise o impacto antes de confirmar.
        </Note>
      )}
      <form onSubmit={review} className="form">
        <fieldset disabled={busy || cancel}>
          <OperationFields />
          <OperationItems />
          <OperationPayments />
          <Field
            label="Observação (opcional)"
            value={input.notes || ""}
            onChange={(value) => patch({ notes: value || null })}
          />
        </fieldset>
        {(original || kind === "adjustment") && (
          <Field
            label="Motivo obrigatório"
            value={input.reason || ""}
            onChange={(value) => patch({ reason: value })}
            required
          />
        )}
        <ErrorMessage message={error} />
        <Button
          type="submit"
          disabled={busy || (!input.items.length && kind !== "inventory")}
        >
          Revisar efeitos antes de confirmar
        </Button>
      </form>
      <InlineProduct />
      <OperationPreview />
    </EditorContext.Provider>
  );
}
