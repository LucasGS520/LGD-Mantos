import { useState } from "react";
import { useNav } from "../../../app/nav";
import { AppBar, BottomNav, ScreenBody } from "../../../components/Chrome";
import { Card, ErrorBody, LoadingBody } from "../../../shared/ui";
import { Button } from "../../../shared/ui/Button";
import { Field } from "../../../shared/ui/Field";
import { Note } from "../../../shared/ui/Note";
import { Options } from "../../../shared/ui/Options";
import { useSources } from "../hooks/useSources";
export function Catalog() {
  const { navigate } = useNav();
  const { data, loading, error, reload } = useSources();
  const [search, setSearch] = useState("");
  const [products, , state] = data || [[], [], null];
  return (
    <>
      <AppBar title="Operação" subtitle="Catálogo e estoque disponível" />
      <ScreenBody>
        <Options>
          <Button onClick={() => navigate("product")}>Novo produto</Button>
          <Button onClick={() => navigate("operations", { kind: "purchase" })}>
            Compras
          </Button>
          <Button onClick={() => navigate("operations", { kind: "sale" })}>
            Vendas e recebimentos
          </Button>
          <Button
            onClick={() => navigate("operations", { kind: "adjustment" })}
          >
            Ajustes
          </Button>
          <Button onClick={() => navigate("operations", { kind: "inventory" })}>
            Inventário inicial
          </Button>
        </Options>
        {state && !state.started_at && (
          <Note>
            Cadastre as peças e confirme o inventário inicial para começar
            compras, vendas e ajustes. Fornecedores, canais e formas de
            pagamento ficam em Mais.
          </Note>
        )}
        <Field
          label="Buscar produto, estampa, marca, modelo ou código"
          value={search}
          onChange={setSearch}
        />
        {loading ? (
          <LoadingBody />
        ) : error ? (
          <ErrorBody msg={error} onRetry={reload} />
        ) : (
          products
            .filter((p) =>
              JSON.stringify([
                p.name,
                p.print_name,
                p.brand,
                p.model,
                p.variants.map((v) => v.code),
              ])
                .toLocaleLowerCase()
                .includes(search.toLocaleLowerCase()),
            )
            .map((p) => (
              <Card
                key={p.id}
                onClick={() => navigate("product", { id: p.id })}
              >
                <h3>
                  {p.name} {!p.active && "· desativado"}
                </h3>
                <p>
                  {p.print_name} · {p.brand || "Marca não informada"} ·{" "}
                  {p.model || "Modelo não informado"}
                </p>
                <div className="rows">
                  {p.variants.map((v) => (
                    <span key={v.id}>
                      {v.size} / {v.color}: <strong>{v.stock}</strong>
                      {!v.active && " (desativada)"}
                    </span>
                  ))}
                </div>
              </Card>
            ))
        )}
        {!loading && products.length === 0 && (
          <Note>
            O catálogo está vazio. Comece cadastrando as peças conhecidas.
          </Note>
        )}
      </ScreenBody>
      <BottomNav active="op" />
    </>
  );
}
