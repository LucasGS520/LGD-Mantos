import { useState, type FormEvent } from "react";
import { errorText } from "../../../shared/api/errors";
import { Button } from "../../../shared/ui/Button";
import { ErrorMessage } from "../../../shared/ui/ErrorMessage";
import { Field } from "../../../shared/ui/Field";
import { Select } from "../../../shared/ui/Select";
import { type Auxiliary } from "../../auxiliaries/contracts";
import { api } from "../api";
import { type Product } from "../contracts";
export function ProductForm({
  product,
  auxiliaries,
  onSaved,
}: {
  product?: Product;
  auxiliaries: Auxiliary[];
  onSaved: (product: Product) => void;
}) {
  const [name, setName] = useState(product?.name || "");
  const [print, setPrint] = useState(product?.print_name || "");
  const [brand, setBrand] = useState(product?.brand || "");
  const [model, setModel] = useState(product?.model || "");
  const [category, setCategory] = useState(product?.category_id || "");
  const [notes, setNotes] = useState(product?.notes || "");
  const [reason, setReason] = useState("");
  const [active, setActive] = useState(product?.active ?? true);
  const [accept, setAccept] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function save(e: FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      const body = {
        name,
        print_name: print,
        brand: brand || null,
        model: model || null,
        category_id: category || null,
        notes: notes || null,
        active,
        accept_similar: accept,
        ...(product ? { version: product.version, reason } : {}),
      };
      onSaved(
        product
          ? await api.updateProduct(product.id, body)
          : await api.createProduct(body),
      );
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <form className="form" onSubmit={save}>
      <div className="grid">
        <Field label="Nome da peça" value={name} onChange={setName} required />
        <Field label="Estampa" value={print} onChange={setPrint} required />
        <Field label="Marca" value={brand} onChange={setBrand} />
        <Field label="Modelo" value={model} onChange={setModel} />
        <Select
          label="Categoria"
          value={category}
          onChange={setCategory}
          options={auxiliaries.filter(
            (a) => a.kind === "category" && (a.active || a.id === category),
          )}
        />
        <Field label="Observação" value={notes} onChange={setNotes} />
      </div>
      <label>
        <input
          type="checkbox"
          checked={active}
          onChange={(e) => setActive(e.target.checked)}
        />{" "}
        Produto ativo
      </label>
      <label>
        <input
          type="checkbox"
          checked={accept}
          onChange={(e) => setAccept(e.target.checked)}
        />{" "}
        Caso haja nome semelhante, confirmo que esta é uma peça distinta
      </label>
      {product && (
        <Field
          label="Motivo da alteração"
          value={reason}
          onChange={setReason}
          required
        />
      )}
      <ErrorMessage message={error} />
      <Button type="submit" disabled={busy}>
        Salvar produto
      </Button>
    </form>
  );
}
