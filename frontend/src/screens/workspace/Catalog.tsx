import {
useEffect,
useState,
type FormEvent
} from "react";
import { AppBar,BottomNav,ScreenBody } from "../../components/Chrome";
import { Card,ErrorBody,LoadingBody,Section } from "../../components/UI";
import { useNav } from "../../nav";
import {
api,
brl,
type Auxiliary,
type Photo,
type Product,
type Variant
} from "../../services/domain";
import "../../styles/workspace.css";

import {
Button,
ErrorMessage,
Field,
History,
Note,
Options,
Select,
errorText,
useSources
} from "./Shared";

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
      if (variant)
        await api.put(`/products/${product.id}/variants/${variant.id}`, body);
      else await api.post(`/products/${product.id}/variants`, body);
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
          ? await api.put<Product>(`/products/${product.id}`, body)
          : await api.post<Product>("/products", body),
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

export function ProductScreen() {
  const { params, navigate } = useNav();
  const id = params.id as string | undefined;
  const { data, loading, error, reload } = useSources();
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

function PhotoImage({ id }: { id: string }) {
  const [url, setUrl] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let alive = true;
    let objectUrl = "";
    api
      .photo(id)
      .then((value) => {
        objectUrl = value;
        if (alive) setUrl(value);
        else URL.revokeObjectURL(value);
      })
      .catch((e) => {
        if (alive) setError(errorText(e));
      });
    return () => {
      alive = false;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [id]);
  return url ? (
    <img className="photo" src={url} alt="Foto do produto" />
  ) : (
    <p>{error || "Carregando foto…"}</p>
  );
}

function Photos({ product, reload }: { product: Product; reload: () => void }) {
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
            onSave={(body) =>
              action(() => api.put(`/photos/${photo.id}`, body))
            }
          />
          <Options>
            <Button
              danger
              disabled={busy}
              onClick={() => {
                if (window.confirm("Remover esta foto?"))
                  action(() => api.remove(`/photos/${photo.id}`));
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
                  if (file)
                    action(async () => {
                      const added = await api.upload(product.id, file);
                      await api.put(`/photos/${added.id}`, {
                        position: photo.position,
                        primary: photo.primary,
                        variant_id: photo.variant_id,
                        color: photo.color,
                      });
                      await api.remove(`/photos/${photo.id}`);
                    });
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

function PhotoSettings({
  photo,
  product,
  disabled,
  onSave,
}: {
  photo: Photo;
  product: Product;
  disabled: boolean;
  onSave: (body: unknown) => void;
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
