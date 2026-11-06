import { Card } from "../../../shared/ui";
import { ProductForm, VariantForm } from "../../catalog";
import { useEditor } from "../hooks/EditorContext";
export function InlineProduct() {
  const {
    auxiliaries,
    reload,
    newProduct,
    setNewProduct,
    inlineProduct,
    setInlineProduct,
  } = useEditor();
  return (
    <>
      {newProduct && (
        <Card>
          <h3>Nova peça</h3>
          <ProductForm
            auxiliaries={auxiliaries}
            onSaved={(p) => {
              setInlineProduct(p);
              reload();
            }}
          />
          {inlineProduct && (
            <>
              <h4>Adicionar variante a {inlineProduct.name}</h4>
              <VariantForm
                product={inlineProduct}
                onSaved={() => {
                  setNewProduct(false);
                  setInlineProduct(null);
                  reload();
                }}
              />
            </>
          )}
        </Card>
      )}
    </>
  );
}
