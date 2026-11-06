import { useRef, useState, type FormEvent } from "react";
import { ApiError, errorText } from "../../../shared/api/errors";
import { localToday } from "../../../shared/format/dates";
import { type Auxiliary } from "../../auxiliaries/contracts";
import { type Product } from "../../catalog/contracts";
import { api } from "../api";
import {
  type Item,
  type Kind,
  type Operation,
  type OperationInput,
  type Payment,
  type Preview,
} from "../contracts";
import { cleanInput } from "../model/cleanInput";
import { editPayment } from "../model/payments";
export interface EditorProps {
  kind: Kind;
  original: Operation | null;
  products: Product[];
  auxiliaries: Auxiliary[];
  cancel: boolean;
  reload: () => void;
  onSaved: (operation: Operation) => void;
}
export function useOperationEditor({
  kind,
  original,
  products,
  auxiliaries,
  cancel,
  reload,
  onSaved,
}: EditorProps) {
  const [input, setInput] = useState<OperationInput>(() =>
    original
      ? { ...cleanInput(original), cancelled: cancel }
      : {
          kind,
          items: [],
          payments: [],
          notes: null,
          ...(kind === "purchase" ? { purchase_date: localToday() } : {}),
          ...(kind === "adjustment" ? { direction: "in" } : {}),
        },
  );
  const [selected, setSelected] = useState("");
  const [preview, setPreview] = useState<Preview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [newProduct, setNewProduct] = useState(false);
  const [inlineProduct, setInlineProduct] = useState<Product | null>(null);
  const inFlight = useRef(false);
  const requestKey = useRef(crypto.randomUUID());
  const variants = products.flatMap((p) =>
    p.variants.map((v) => ({
      ...v,
      name: `${p.name} · ${p.print_name} · ${v.size} / ${v.color} · ${v.stock} disponíveis`,
      productActive: p.active,
    })),
  );
  const patch = (value: Partial<OperationInput>) => {
    setInput((prev) => ({ ...prev, ...value }));
    setPreview(null);
    requestKey.current = crypto.randomUUID();
  };
  const itemPatch = (index: number, value: Partial<Item>) =>
    patch({
      items: input.items.map((item, i) =>
        i === index ? { ...item, ...value } : item,
      ),
    });
  const paymentPatch = (index: number, value: Partial<Payment>) =>
    patch({
      payments: editPayment(input.payments, index, value),
    });
  const options = (group: string, current?: string | null) =>
    auxiliaries.filter(
      (a) => a.kind === group && (a.active || a.id === current),
    );
  async function review(e: FormEvent) {
    e.preventDefault();
    if (inFlight.current) return;
    inFlight.current = true;
    setBusy(true);
    setError(null);
    try {
      setPreview(await api.preview(input, original?.id));
    } catch (e) {
      setError(errorText(e));
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }
  async function confirm() {
    if (!preview || inFlight.current) return;
    inFlight.current = true;
    setBusy(true);
    setError(null);
    try {
      onSaved(
        (await api.confirm(input, preview, requestKey.current, original?.id))
          .operation,
      );
    } catch (e) {
      if (e instanceof ApiError && e.status === 409) {
        setPreview(null);
        requestKey.current = crypto.randomUUID();
        setError(
          errorText(e) + ". Revise os efeitos novamente antes de confirmar.",
        );
      } else {
        setError(
          errorText(e) +
            ". Se a resposta foi interrompida, tente confirmar novamente.",
        );
      }
    } finally {
      inFlight.current = false;
      setBusy(false);
    }
  }
  return {
    kind,
    original,
    products,
    auxiliaries,
    cancel,
    reload,
    onSaved,
    input,
    selected,
    setSelected,
    preview,
    error,
    busy,
    newProduct,
    setNewProduct,
    inlineProduct,
    setInlineProduct,
    variants,
    patch,
    itemPatch,
    paymentPatch,
    options,
    review,
    confirm,
  };
}
