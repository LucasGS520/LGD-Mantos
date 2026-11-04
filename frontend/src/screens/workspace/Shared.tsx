import {
type ReactNode
} from "react";
import { ErrorBody,Section } from "../../components/UI";
import { useData } from "../../hooks/useData";
import {
api,
brl,
dateLabel,
kindLabel,
type Auxiliary,
type Operation,
type Product,
type Revision,
type State
} from "../../services/domain";
import "../../styles/workspace.css";

export const auxLabels: Record<string, string> = {
  supplier: "Fornecedores",
  category: "Categorias",
  purchase_channel: "Canais de compra",
  sale_channel: "Canais de venda",
  payment_method: "Formas de pagamento",
};
export const attrLabels: Record<string, string> = {
  brand: "Marca",
  model: "Modelo",
  category: "Categoria",
  size: "Tamanho",
  color: "Cor",
};
export function Button({
  children,
  onClick,
  disabled = false,
  type = "button",
  danger = false,
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  type?: "button" | "submit";
  danger?: boolean;
}) {
  return (
    <button
      type={type}
      className={`action ${danger ? "danger" : ""}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
export function Field({
  label,
  value,
  onChange,
  type = "text",
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <label className="field">
      {label}
      <input
        type={type}
        value={value}
        required={required}
        min={type === "number" ? 0 : undefined}
        step={type === "number" ? ".01" : undefined}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}
export function Select({
  label,
  value,
  onChange,
  options,
  required = false,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { id: string; name: string }[];
  required?: boolean;
}) {
  return (
    <label className="field">
      {label}
      <select
        aria-label={label}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
      >
        <option value="">Selecione</option>
        {options.map((o) => (
          <option key={o.id} value={o.id}>
            {o.name}
          </option>
        ))}
      </select>
    </label>
  );
}
export function ErrorMessage({ message }: { message: string | null }) {
  return message ? (
    <p role="alert" className="message danger">
      {message}
    </p>
  ) : null;
}
export function Note({ children }: { children: ReactNode }) {
  return <p className="message">{children}</p>;
}
export const errorText = (e: unknown) =>
  e instanceof Error ? e.message : "Não foi possível concluir";
export function useSources() {
  return useData(() =>
    Promise.all([
      api.get<Product[]>("/products"),
      api.get<Auxiliary[]>("/auxiliaries"),
      api.get<State>("/state"),
    ]),
  );
}
export function Options({ children }: { children: ReactNode }) {
  return <div className="actions">{children}</div>;
}

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

export function History({ id }: { id: string }) {
  const { data, loading, error, reload } = useData(
    () => api.get<Revision[]>(`/history/${id}`),
    id,
  );
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

function HistoryVersion({
  label,
  value,
}: {
  label: string;
  value: Record<string, unknown> | null;
}) {
  const labels: Record<string, string> = {
    name: "Nome",
    print_name: "Estampa",
    brand: "Marca",
    model: "Modelo",
    category_id: "Categoria",
    size: "Tamanho",
    color: "Cor",
    reference_cost: "Custo de referência",
    reference_price: "Preço de referência",
    active: "Ativo",
    notes: "Observação",
  };
  return (
    <div>
      <h4>{label}</h4>
      {!value ? (
        <p>Sem versão</p>
      ) : value.payload ? (
        <OperationSummary operation={value as unknown as Operation} />
      ) : (
        <dl>
          {Object.entries(labels)
            .filter(([key]) => key in value)
            .map(([key, title]) => (
              <div key={key}>
                <dt>{title}</dt>
                <dd>
                  {value[key] === null ? "Não informado" : String(value[key])}
                </dd>
              </div>
            ))}
        </dl>
      )}
    </div>
  );
}
