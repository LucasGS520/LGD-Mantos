import { useState } from "react";
import { useNav } from "../../../app/nav";
import { AppBar, ScreenBody } from "../../../components/Chrome";
import { brl } from "../../../shared/format/money";
import { Card, ErrorBody, LoadingBody, Section } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Note } from "../../../shared/ui/Note";
import { History } from "../../history";
import { Photos } from "../../photos";
import { ProductForm } from "../components/ProductForm";
import { VariantForm } from "../components/VariantForm";
import { useSources } from "../hooks/useSources";
export function ProductScreen() {
  const { params, navigate } = useNav();
  const id = params.id as string | undefined;
  const { data, loading, error, reload } = useSources(id);
  const [editingVariant, setEditingVariant] = useState<string | null>(null);
  const [products, aux] = data || [[], [], null];
  const product = products.find((p) => p.id === id);
  return (
    <>
      <AppBar title={product?.name || "Novo produto"} back />
      <ScreenBody>
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          <>
            <ProductForm
              key={product ? `${product.id}-${product.version}` : "new"}
              product={product}
              auxiliaries={aux}
              onSaved={(p) => {
                if (!id) navigate("product", { id: p.id });
                else reload();
              }}
            />
            {product && (
              <>
                <Note>
                  O saldo é atualizado pelos acontecimentos. Alterar referências
                  não muda o custo médio nem o histórico.
                </Note>
                <Section title="Variantes">
                  {product.variants.map((v) => (
                    <Card key={v.id}>
                      <h3>
                        {v.size} / {v.color} · {v.stock} disponíveis
                      </h3>
                      <p>{v.code}</p>
                      <p>
                        Custo médio: {brl(v.average_cost)} · Preço de
                        referência: {brl(v.reference_price)}
                      </p>
                      <Button
                        onClick={() =>
                          setEditingVariant(
                            editingVariant === v.id ? null : v.id,
                          )
                        }
                      >
                        Editar variante
                      </Button>
                      {editingVariant === v.id && (
                        <VariantForm
                          key={`${v.id}-${v.version}`}
                          product={product}
                          variant={v}
                          onSaved={() => {
                            setEditingVariant(null);
                            reload();
                          }}
                        />
                      )}
                      <History id={v.id} />
                    </Card>
                  ))}
                </Section>
                <Section title="Adicionar variante">
                  <VariantForm
                    key={product.variants.length}
                    product={product}
                    onSaved={reload}
                  />
                </Section>
                <Photos product={product} reload={reload} />
                <History id={product.id} />
              </>
            )}
          </>
        )}
      </ScreenBody>
    </>
  );
}
