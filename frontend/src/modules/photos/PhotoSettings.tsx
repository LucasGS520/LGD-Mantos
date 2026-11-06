import { useState } from "react";
import { Button } from "../../shared/ui/Button";
import { Field } from "../../shared/ui/Field";
import { Select } from "../../shared/ui/Select";
import { type Product } from "../catalog/contracts";
import { type Photo, type PhotoInput } from "./contracts";
export function PhotoSettings({
  photo,
  product,
  disabled,
  onSave,
}: {
  photo: Photo;
  product: Product;
  disabled: boolean;
  onSave: (body: PhotoInput) => void;
}) {
  const [position, setPosition] = useState(String(photo.position));
  const [primary, setPrimary] = useState(photo.primary);
  const [variant, setVariant] = useState(photo.variant_id || "");
  const [color, setColor] = useState(photo.color || "");
  return (
    <form
      className="form"
      onSubmit={(e) => {
        e.preventDefault();
        onSave({
          position: Number(position),
          primary,
          variant_id: variant || null,
          color: color || null,
        });
      }}
    >
      <Field
        label="Ordem"
        value={position}
        onChange={setPosition}
        type="number"
      />
      <Select
        label="Variante (opcional)"
        value={variant}
        onChange={setVariant}
        options={product.variants.map((v) => ({
          id: v.id,
          name: `${v.size} / ${v.color}`,
        }))}
      />
      <Field
        label="Cor representada (opcional)"
        value={color}
        onChange={setColor}
      />
      <label>
        <input
          type="checkbox"
          checked={primary}
          onChange={(e) => setPrimary(e.target.checked)}
        />{" "}
        Principal
      </label>
      <Button type="submit" disabled={disabled}>
        Salvar organização
      </Button>
    </form>
  );
}
