import { dateLabel } from "../../../shared/format/dates";
import { brl } from "../../../shared/format/money";
import { Note } from "../../../shared/ui/Note";
import { type Operation } from "../contracts";
import { kindLabel } from "../labels";
export function OperationSummary({ operation }: { operation: Operation }) {
  const { result, payload } = operation;
  return (
    <>
      <p>
        {kindLabel[operation.kind]} · {dateLabel(operation.effective_at)} ·
        versão {operation.version}
        {operation.cancelled ? " · ANULADA" : ""}
      </p>
      <p>{Object.values(payload.labels || {}).join(" · ")}</p>
      {operation.cancelled && (
        <Note>
          Registro preservado; seus efeitos não entram nos totais válidos.
        </Note>
      )}
      <table>
        <thead>
          <tr>
            <th>Peça / variante</th>
            <th>Quantidade</th>
            <th>
              {operation.kind === "sale" ? "Preço praticado" : "Custo unitário"}
            </th>
            {operation.kind === "sale" && <th>Referência / custo histórico</th>}
          </tr>
        </thead>
        <tbody>
          {(result.items || payload.items).map((i, index) => (
            <tr key={index}>
              <td>
                {i.product_name || i.variant_id}
                <br />
                {i.size} / {i.color}
              </td>
              <td>{i.quantity}</td>
              <td>
                {brl(operation.kind === "sale" ? i.unit_price : i.unit_cost)}
              </td>
              {operation.kind === "sale" && (
                <td>
                  {brl(i.reference_price)} / {brl(i.unit_cost)}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
      {result.total !== undefined && (
        <p>
          Total: <strong>{brl(result.total)}</strong>
        </p>
      )}
      {operation.kind === "sale" && !operation.cancelled && (
        <>
          <p>
            Recebido: {brl(result.received)} · Saldo: {brl(result.balance)} ·{" "}
            {result.financial_status}
          </p>
          <p>
            Resultado bruto: {brl(result.gross_result)} · Diferença comercial:{" "}
            {brl(result.commercial_difference)}
          </p>
          {!!result.unknown_cost_units && (
            <Note>
              {result.unknown_cost_units} unidades sem custo conhecido.
              Resultado e margem estão incompletos.
            </Note>
          )}
          <h4>Pagamentos</h4>
          {payload.payments.map((p) => (
            <p key={p.id}>
              {brl(p.amount)} · {p.method_name} · {dateLabel(p.created_at)}
            </p>
          ))}
          {payload.payments.length === 0 && <p>Nenhum pagamento registrado.</p>}
        </>
      )}
      {payload.notes && <p>Observação: {payload.notes}</p>}
    </>
  );
}
