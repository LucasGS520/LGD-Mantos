import { Button } from "../../../shared/ui/Button";
import { Field } from "../../../shared/ui/Field";
import { Note } from "../../../shared/ui/Note";
export function DateFilter({
  start,
  end,
  setStart,
  setEnd,
  setFilter,
}: {
  start: string;
  end: string;
  setStart: (value: string) => void;
  setEnd: (value: string) => void;
  setFilter: (value: string) => void;
}) {
  return (
    <form
      className="form"
      onSubmit={(e) => {
        e.preventDefault();
        const query = new URLSearchParams();
        if (start) query.set("start", start);
        if (end) query.set("end", end);
        setFilter(query.size ? "?" + query : "");
      }}
    >
      <div className="grid">
        <Field
          label="Data inicial (opcional)"
          type="date"
          value={start}
          onChange={setStart}
        />
        <Field
          label="Data final (opcional)"
          type="date"
          value={end}
          onChange={setEnd}
        />
      </div>
      <Button type="submit">Consultar intervalo</Button>
      <Note>
        Sem filtro, todo o histórico confiável. Recebimentos usam a data do
        pagamento; saldos pendentes são a situação atual.
      </Note>
    </form>
  );
}
