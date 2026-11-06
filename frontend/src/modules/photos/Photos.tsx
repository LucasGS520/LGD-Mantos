import { useState } from "react";
import { errorText } from "../../shared/api/errors";
import { Card, Section } from "../../shared/ui";
import { Button } from "../../shared/ui/Button";
import { ErrorMessage } from "../../shared/ui/ErrorMessage";
import { Note } from "../../shared/ui/Note";
import { Options } from "../../shared/ui/Options";
import { type Product } from "../catalog/contracts";
import { replacePhoto } from "./actions/replace";
import { api } from "./api";
import { PhotoImage } from "./PhotoImage";
import { PhotoSettings } from "./PhotoSettings";
export function Photos({
  product,
  reload,
}: {
  product: Product;
  reload: () => void;
}) {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  async function action(fn: () => Promise<unknown>) {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      await fn();
      reload();
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Section title="Fotos opcionais">
      <Note>
        JPEG, PNG ou WebP, até 10 MB. A substituição só remove a foto anterior
        depois que a nova estiver salva.
      </Note>
      <ErrorMessage message={error} />
      <label className="field">
        Adicionar foto
        <input
          disabled={busy}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) action(() => api.upload(product.id, file));
            e.target.value = "";
          }}
        />
      </label>
      {product.photos.map((photo) => (
        <Card key={photo.id}>
          <PhotoImage id={photo.id} />
          <PhotoSettings
            photo={photo}
            product={product}
            disabled={busy}
            onSave={(body) => action(() => api.organize(photo.id, body))}
          />
          <Options>
            <Button
              danger
              disabled={busy}
              onClick={() => {
                if (window.confirm("Remover esta foto?"))
                  action(() => api.remove(photo.id));
              }}
            >
              Remover foto
            </Button>
            <label className="field">
              Substituir
              <input
                disabled={busy}
                type="file"
                accept="image/jpeg,image/png,image/webp"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) action(() => replacePhoto(product.id, photo, file));
                  e.target.value = "";
                }}
              />
            </label>
          </Options>
        </Card>
      ))}
    </Section>
  );
}
