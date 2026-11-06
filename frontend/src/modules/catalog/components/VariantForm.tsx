import { useState, type FormEvent } from "react";
import { errorText } from "../../../shared/api/errors";
import { Button } from "../../../shared/ui/Button";
import { ErrorMessage } from "../../../shared/ui/ErrorMessage";
import { Field } from "../../../shared/ui/Field";
import { api } from "../api";
import { type Product, type Variant } from "../contracts";
export function VariantForm({
  product,
  variant,
  onSaved,
}: {
  product: Product;
  variant?: Variant;
  onSaved: () => void;
}) {
  const [size, setSize] = useState(variant?.size || "");
  const [color, setColor] = useState(variant?.color || "");
  const [cost, setCost] = useState(variant?.reference_cost || "");
  const [price, setPrice] = useState(variant?.reference_price || "");
  const [active, setActive] = useState(variant?.active ?? true);
  const [reason, setReason] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function save(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const body = {
        size,
        color,
        reference_cost: cost || null,
        reference_price: price || null,
        active,
        ...(variant ? { version: variant.version, reason } : {}),
      };
      if (variant) await api.updateVariant(product.id, variant.id, body);
      else await api.createVariant(product.id, body);
      onSaved();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form onSubmit={save} className="form">
      <div className="grid">
        <Field label="Tamanho" value={size} onChange={setSize} required />
        <Field label="Cor" value={color} onChange={setColor} required />
        <Field
          label="Custo de referência (opcional)"
          value={cost}
          onChange={setCost}
          type="number"
        />
        <Field
          label="Preço de referência (opcional)"
          value={price}
          onChange={setPrice}
          type="number"
        />
      </div>
      <label>
        <input
          type="checkbox"
          checked={active}
          onChange={(e) => setActive(e.target.checked)}
        />{" "}
        Disponível em novas operações
      </label>
      {variant && (
        <Field
          label="Motivo da alteração"
          value={reason}
          onChange={setReason}
          required
        />
      )}
      <ErrorMessage message={error} />
      <Button type="submit" disabled={busy}>
        Salvar variante
      </Button>
    </form>
  );
}
