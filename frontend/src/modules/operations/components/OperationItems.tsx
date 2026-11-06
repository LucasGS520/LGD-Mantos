import { Card, Section } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Field } from "../../../shared/ui/Field";
import { Options } from "../../../shared/ui/Options";
import { Select } from "../../../shared/ui/Select";
import { flows } from "../flows";
import { useEditor } from "../hooks/EditorContext";
export function OperationItems() {
  const {
    kind,
    input,
    selected,
    setSelected,
    setNewProduct,
    variants,
    patch,
    itemPatch,
  } = useEditor();
  return (
    <>
      <Section title="Itens">
        <Select
          label="Peça e variante"
          value={selected}
          onChange={setSelected}
          options={variants.filter(
            (v) =>
              v.active &&
              v.productActive &&
              !input.items.some((i) => i.variant_id === v.id),
          )}
        />
        <Options>
          <Button
            disabled={!selected}
            onClick={() => {
              const v = variants.find((v) => v.id === selected)!;
              patch({
                items: [
                  ...input.items,
                  {
                    variant_id: v.id,
                    quantity: 1,
                    ...flows[kind].initialValue(v),
                  },
                ],
              });
              setSelected("");
            }}
          >
            Adicionar item
          </Button>
          {kind === "purchase" && (
            <Button onClick={() => setNewProduct((value) => !value)}>
              Cadastrar peça durante a compra
            </Button>
          )}
        </Options>
        {input.items.map((item, index) => (
          <Card key={item.variant_id}>
            <p>
              {variants.find((v) => v.id === item.variant_id)?.name ||
                item.variant_id}
            </p>
            <div className="grid">
              <Field
                label="Quantidade inteira"
                type="number"
                value={String(item.quantity)}
                onChange={(value) =>
                  itemPatch(index, { quantity: Number(value) })
                }
                required
              />
              {kind === "sale" ? (
                <Field
                  label="Preço negociado por unidade"
                  type="number"
                  value={item.unit_price || ""}
                  onChange={(value) => itemPatch(index, { unit_price: value })}
                  required
                />
              ) : (
                (kind !== "adjustment" || input.direction === "in") && (
                  <Field
                    label={flows[kind].costLabel}
                    type="number"
                    value={item.unit_cost || ""}
                    onChange={(value) =>
                      itemPatch(index, { unit_cost: value || null })
                    }
                    required={kind === "purchase"}
                  />
                )
              )}
            </div>
            <Button
              danger
              onClick={() =>
                patch({ items: input.items.filter((_, i) => i !== index) })
              }
            >
              Retirar item
            </Button>
          </Card>
        ))}
      </Section>
    </>
  );
}
