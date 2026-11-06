import { OperationSummary } from "../operations";
import { type Operation } from "../operations/contracts";
export function HistoryVersion({
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
