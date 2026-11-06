import { useState } from "react";
import { errorText } from "../../../shared/api/errors";
import { Button } from "../../../shared/ui/Button";
import { ErrorMessage } from "../../../shared/ui/ErrorMessage";
import { Field } from "../../../shared/ui/Field";
import { type Auxiliary, type RecordValues } from "../contracts";

export function RecordForm<R extends Auxiliary>({
  save,
  editing,
  onSaved,
}: {
  save: (values: RecordValues, editing: R | null) => Promise<unknown>;
  editing: R | null;
  onSaved: () => void;
}) {
  const [name, setName] = useState(editing?.name || "");
  const [notes, setNotes] = useState(editing?.notes || "");
  const [active, setActive] = useState(editing?.active ?? true);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="form"
      onSubmit={async (e) => {
        e.preventDefault();
        if (busy) return;
        setBusy(true);
        setError(null);
        try {
          const body = {
            name,
            notes: notes || null,
            active,
            ...(editing ? { version: editing.version, reason } : {}),
          };
          await save(body, editing);
          setName("");
          setNotes("");
          onSaved();
        } catch (e) {
          setError(errorText(e));
        } finally {
          setBusy(false);
        }
      }}
    >
      <Field
        label={editing ? "Nome" : "Novo nome"}
        value={name}
        onChange={setName}
        required
      />
      <Field label="Observação opcional" value={notes} onChange={setNotes} />
      <label>
        <input
          type="checkbox"
          checked={active}
          onChange={(e) => setActive(e.target.checked)}
        />{" "}
        Ativo para novas operações
      </label>
      {editing && (
        <Field label="Motivo" value={reason} onChange={setReason} required />
      )}
      <ErrorMessage message={error} />
      <Button type="submit" disabled={busy}>
        {editing ? "Salvar alteração" : "Cadastrar"}
      </Button>
    </form>
  );
}
