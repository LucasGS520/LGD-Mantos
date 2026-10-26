import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Btn, Input, Section } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { Supplier, Category, Product } from '../../services/types'
import { useNav } from '../../nav'

const SIZES = ['PP', 'P', 'M', 'G', 'GG', 'G1', 'G2', 'G3', 'Único']

type ProductMode = 'novo' | 'reposicao'

interface VariantRow {
  variant_id?: string
  size: string
  color: string
  qty: string
}

interface ProductCard {
  id: string
  mode: ProductMode
  supplier_id: string
  name: string
  description: string
  brand: string
  category_id: string
  cost_price: string
  sale_price: string
  existing_product_id: string
  variants: VariantRow[]
}

interface CardExtra {
  showNewCat: boolean; newCatName: string; newCatDesc: string
  showNewSup: boolean; newSupName: string
}

function blankVariant(): VariantRow {
  return { size: 'M', color: 'Unico', qty: '' }
}

function blankCard(): ProductCard {
  return {
    id: Math.random().toString(36).slice(2),
    mode: 'novo',
    supplier_id: '',
    name: '', description: '', brand: '', category_id: '',
    cost_price: '', sale_price: '',
    existing_product_id: '',
    variants: [blankVariant()],
  }
}

const today = () => new Date().toISOString().slice(0, 10)
const parseNum = (s: string) => parseFloat(s.replace(',', '.')) || 0

const selectStyle: React.CSSProperties = {
  width: '100%', height: 46, padding: '0 14px', borderRadius: 12,
  background: 'var(--bg-4)', border: '1px solid var(--line-2)',
  color: 'var(--text-1)', fontSize: 15, outline: 0, appearance: 'none',
}

const cellSelectStyle: React.CSSProperties = {
  height: 34, borderRadius: 8, background: 'var(--bg-4)',
  border: '1px solid var(--line-2)', color: 'var(--gold-300)',
  fontSize: 13, fontWeight: 700, textAlign: 'center',
  outline: 0, appearance: 'none', width: '100%', cursor: 'pointer',
}

const quickInputStyle: React.CSSProperties = {
  flex: 1, height: 36, borderRadius: 8,
  background: 'var(--bg-4)', border: '1px solid var(--line-2)',
  color: 'var(--text-1)', fontSize: 13, padding: '0 10px', outline: 0,
}

const quickBtnStyle: React.CSSProperties = {
  height: 36, padding: '0 14px', borderRadius: 8,
  background: 'var(--gold-500)', border: 0,
  color: '#000', fontSize: 12, fontWeight: 700, cursor: 'pointer',
}

const secTitle: React.CSSProperties = {
  fontSize: 13, fontWeight: 700, color: 'var(--text-2)',
  letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 10,
}

const fieldLabelRow: React.CSSProperties = {
  fontSize: 12, fontWeight: 600, color: 'var(--text-2)',
  letterSpacing: 0.2, textTransform: 'uppercase',
}

const blankExtra = (): CardExtra => ({
  showNewCat: false, newCatName: '', newCatDesc: '',
  showNewSup: false, newSupName: '',
})

export default function EntryForm() {
  const { back } = useNav()
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [allProducts, setAllProducts] = useState<Product[]>([])
  const [entryDate, setEntryDate] = useState(today())
  const [cards, setCards] = useState<ProductCard[]>([blankCard()])
  const [extras, setExtras] = useState<Record<string, CardExtra>>({})
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.get<Supplier[]>('/suppliers').then(setSuppliers).catch(() => {})
    api.get<Category[]>('/categories').then(setCategories).catch(() => {})
    api.get<Product[]>('/products').then(setAllProducts).catch(() => {})
  }, [])

  const getEx = (id: string): CardExtra => extras[id] ?? blankExtra()
  const setEx = (id: string, patch: Partial<CardExtra>) =>
    setExtras(prev => ({ ...prev, [id]: { ...getEx(id), ...patch } }))

  const updateCard = (id: string, patch: Partial<ProductCard>) =>
    setCards(prev => prev.map(c => c.id === id ? { ...c, ...patch } : c))

  const removeCard = (id: string) =>
    setCards(prev => prev.filter(c => c.id !== id))

  const selectExistingProduct = (cardId: string, productId: string) => {
    const prod = allProducts.find(p => p.id === productId)
    if (!prod) { updateCard(cardId, { existing_product_id: productId, variants: [blankVariant()] }); return }
    const rows: VariantRow[] = prod.variants.map(v => ({
      variant_id: v.id, size: v.size, color: v.color, qty: '',
    }))
    updateCard(cardId, {
      existing_product_id: productId,
      variants: rows.length > 0 ? rows : [blankVariant()],
    })
  }

  const addVariant = (cardId: string) =>
    setCards(prev => prev.map(c =>
      c.id === cardId ? { ...c, variants: [...c.variants, blankVariant()] } : c
    ))

  const removeVariant = (cardId: string, idx: number) =>
    setCards(prev => prev.map(c => {
      if (c.id !== cardId) return c
      return { ...c, variants: c.variants.filter((_, i) => i !== idx) }
    }))

  const updateVariant = (cardId: string, idx: number, field: keyof VariantRow, value: string) =>
    setCards(prev => prev.map(c => {
      if (c.id !== cardId) return c
      return { ...c, variants: c.variants.map((v, i) => i === idx ? { ...v, [field]: value } : v) }
    }))

  const createCategory = async (cardId: string) => {
    const ex = getEx(cardId)
    if (!ex.newCatName.trim() || !ex.newCatDesc.trim()) return
    try {
      const created = await api.post<Category>('/categories', { name: ex.newCatName.trim(), description: ex.newCatDesc.trim() })
      setCategories(prev => [...prev, created])
      updateCard(cardId, { category_id: created.id })
      setEx(cardId, { showNewCat: false, newCatName: '', newCatDesc: '' })
    } catch { setError('Erro ao criar categoria') }
  }

  const createSupplier = async (cardId: string) => {
    const ex = getEx(cardId)
    if (!ex.newSupName.trim()) return
    try {
      const created = await api.post<Supplier>('/suppliers', { name: ex.newSupName.trim() })
      setSuppliers(prev => [...prev, created])
      updateCard(cardId, { supplier_id: created.id })
      setEx(cardId, { showNewSup: false, newSupName: '' })
    } catch { setError('Erro ao criar fornecedor') }
  }

  const cardQty = (c: ProductCard) =>
    c.variants.reduce((s, v) => s + (parseInt(v.qty) || 0), 0)

  const cardCost = (c: ProductCard) =>
    cardQty(c) * parseNum(c.cost_price)

  const totalCost = cards.reduce((acc, c) => acc + cardCost(c), 0)
  const totalVariants = cards.reduce((acc, c) =>
    acc + c.variants.filter(v => (parseInt(v.qty) || 0) > 0).length, 0)

  const handleSubmit = async () => {
    for (const c of cards) {
      if (!c.supplier_id) { setError('Selecione um fornecedor para cada produto'); return }
      if (c.mode === 'novo' && !c.name.trim()) { setError('Informe o nome de todos os produtos'); return }
      if (c.mode === 'reposicao' && !c.existing_product_id) { setError('Selecione o produto para reposição'); return }
      if (!c.variants.some(v => (parseInt(v.qty) || 0) > 0)) {
        setError(`"${c.mode === 'novo' ? c.name || 'Produto' : 'Reposição'}" sem nenhuma variante com quantidade`)
        return
      }
    }
    setSaving(true)
    setError(null)
    try {
      const bySupplier = new Map<string, ProductCard[]>()
      for (const c of cards) {
        if (!bySupplier.has(c.supplier_id)) bySupplier.set(c.supplier_id, [])
        bySupplier.get(c.supplier_id)!.push(c)
      }
      for (const [supplierId, group] of bySupplier) {
        const items: object[] = []
        for (const c of group) {
          if (c.mode === 'novo') {
            items.push({
              new_product: {
                name: c.name.trim(),
                description: c.description.trim() || null,
                brand: c.brand.trim() || null,
                category_id: c.category_id || null,
                cost_price: parseNum(c.cost_price),
                sale_price: parseNum(c.sale_price),
                tags: [],
                variants: c.variants
                  .filter(v => (parseInt(v.qty) || 0) > 0)
                  .map(v => ({ size: v.size, color: v.color.trim() || 'Unico', quantity: parseInt(v.qty), unit_cost: parseNum(c.cost_price) })),
              },
            })
          } else {
            for (const v of c.variants) {
              if ((parseInt(v.qty) || 0) > 0 && v.variant_id) {
                items.push({ existing_variant: { variant_id: v.variant_id, quantity: parseInt(v.qty), unit_cost: parseNum(c.cost_price) } })
              }
            }
          }
        }
        await api.post('/entries', { supplier_id: supplierId, entry_date: entryDate, notes: null, items })
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar entrada')
      setSaving(false)
    }
  }

  return (
    <>
      <AppBar title="Nova Entrada" back action={
        <span onClick={handleSubmit} style={{ fontSize: 13, fontWeight: 700, color: saving ? 'var(--text-3)' : 'var(--gold-500)', cursor: 'pointer' }}>
          {saving ? 'Salvando…' : 'Registrar'}
        </span>
      } />
      <ScreenBody>

        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600 }}>{error}</div>
        )}

        <Section title="Informações" top={4}>
          <Input label="Data de entrada" type="date" value={entryDate} onChange={e => setEntryDate(e.target.value)} />
        </Section>

        <Section title="Produtos" top={20}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {cards.map((c, idx) => {
              const ex = getEx(c.id)
              const margin = c.cost_price && c.sale_price
                ? (((parseNum(c.sale_price) - parseNum(c.cost_price)) / parseNum(c.sale_price)) * 100).toFixed(0)
                : '—'

              return (
                <div key={c.id} style={{ background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 16, overflow: 'hidden' }}>

                  {/* Card header */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid var(--line-1)' }}>
                    <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)' }}>Produto {idx + 1}</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ display: 'flex', background: 'var(--bg-3)', borderRadius: 8, padding: 2, gap: 2 }}>
                        {(['novo', 'reposicao'] as ProductMode[]).map(m => (
                          <button key={m}
                            onClick={() => updateCard(c.id, { mode: m, variants: [blankVariant()], existing_product_id: '' })}
                            style={{ padding: '4px 10px', borderRadius: 6, border: 0, cursor: 'pointer', fontSize: 11, fontWeight: 600, background: c.mode === m ? 'var(--gold-500)' : 'transparent', color: c.mode === m ? '#000' : 'var(--text-3)' }}
                          >
                            {m === 'novo' ? 'Novo' : 'Reposição'}
                          </button>
                        ))}
                      </div>
                      {cards.length > 1 && (
                        <div onClick={() => removeCard(c.id)} style={{ cursor: 'pointer' }}>
                          <Ico.close size={16} stroke="var(--text-3)" />
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Card body */}
                  <div style={{ padding: 16, display: 'flex', flexDirection: 'column', gap: 20 }}>

                    {/* IDENTIFICAÇÃO */}
                    <div>
                      <div style={secTitle}>Identificação</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

                        {c.mode === 'novo' ? (
                          <>
                            <Input label="Nome" value={c.name} onChange={e => updateCard(c.id, { name: e.target.value })} placeholder="Nome do produto" />

                            <div>
                              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>Descrição</div>
                              <textarea
                                value={c.description}
                                onChange={e => updateCard(c.id, { description: e.target.value })}
                                placeholder="Descrição do produto…"
                                rows={3}
                                style={{ width: '100%', padding: '12px 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, resize: 'none', outline: 0, fontFamily: 'inherit', boxSizing: 'border-box' }}
                              />
                            </div>

                            <Input label="Marca" value={c.brand} onChange={e => updateCard(c.id, { brand: e.target.value })} placeholder="ex: Adidas, Nike, Umbro" />

                            {/* Categoria + Fornecedor em grid — idêntico ao ProductForm */}
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>

                              <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                  <span style={fieldLabelRow}>Categoria</span>
                                  <span onClick={() => setEx(c.id, { showNewCat: !ex.showNewCat, newCatName: '' })} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Nova</span>
                                </div>
                                {ex.showNewCat && (
                                  <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                                    <input value={ex.newCatName} onChange={e => setEx(c.id, { newCatName: e.target.value })} placeholder="Nome" autoFocus style={quickInputStyle} />
                                    <input value={ex.newCatDesc} onChange={e => setEx(c.id, { newCatDesc: e.target.value })} onKeyDown={e => e.key === 'Enter' && createCategory(c.id)} placeholder="Descrição" style={{ ...quickInputStyle, flex: 2 }} />
                                    <button onClick={() => createCategory(c.id)} style={quickBtnStyle}>Criar</button>
                                  </div>
                                )}
                                <select value={c.category_id} onChange={e => updateCard(c.id, { category_id: e.target.value })} style={{ ...selectStyle, color: c.category_id ? 'var(--text-1)' : 'var(--text-3)' }}>
                                  <option value="">Selecionar</option>
                                  {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                                </select>
                              </div>

                              <div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                  <span style={fieldLabelRow}>Fornecedor</span>
                                  <span onClick={() => setEx(c.id, { showNewSup: !ex.showNewSup, newSupName: '' })} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Novo</span>
                                </div>
                                {ex.showNewSup && (
                                  <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                                    <input value={ex.newSupName} onChange={e => setEx(c.id, { newSupName: e.target.value })} onKeyDown={e => e.key === 'Enter' && createSupplier(c.id)} placeholder="Nome do fornecedor" autoFocus style={quickInputStyle} />
                                    <button onClick={() => createSupplier(c.id)} style={quickBtnStyle}>Criar</button>
                                  </div>
                                )}
                                <select value={c.supplier_id} onChange={e => updateCard(c.id, { supplier_id: e.target.value })} style={{ ...selectStyle, color: c.supplier_id ? 'var(--text-1)' : 'var(--text-3)' }}>
                                  <option value="">Selecionar</option>
                                  {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                                </select>
                              </div>

                            </div>
                          </>
                        ) : (
                          <>
                            <div>
                              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>Produto existente</div>
                              <select value={c.existing_product_id} onChange={e => selectExistingProduct(c.id, e.target.value)} style={{ ...selectStyle, color: c.existing_product_id ? 'var(--text-1)' : 'var(--text-3)' }}>
                                <option value="">Selecionar</option>
                                {allProducts.map(p => <option key={p.id} value={p.id}>{p.name} — {p.sku}</option>)}
                              </select>
                            </div>
                            <div>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                                <span style={fieldLabelRow}>Fornecedor</span>
                                <span onClick={() => setEx(c.id, { showNewSup: !ex.showNewSup, newSupName: '' })} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Novo</span>
                              </div>
                              {ex.showNewSup && (
                                <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                                  <input value={ex.newSupName} onChange={e => setEx(c.id, { newSupName: e.target.value })} onKeyDown={e => e.key === 'Enter' && createSupplier(c.id)} placeholder="Nome do fornecedor" autoFocus style={quickInputStyle} />
                                  <button onClick={() => createSupplier(c.id)} style={quickBtnStyle}>Criar</button>
                                </div>
                              )}
                              <select value={c.supplier_id} onChange={e => updateCard(c.id, { supplier_id: e.target.value })} style={{ ...selectStyle, color: c.supplier_id ? 'var(--text-1)' : 'var(--text-3)' }}>
                                <option value="">Selecionar</option>
                                {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                              </select>
                            </div>
                          </>
                        )}
                      </div>
                    </div>

                    {/* PREÇO */}
                    <div>
                      <div style={secTitle}>Preço</div>
                      {c.mode === 'novo' ? (
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                          <Input label="Custo" prefix="R$" value={c.cost_price} onChange={e => updateCard(c.id, { cost_price: e.target.value.replace(/[^0-9.,]/g, '') })} placeholder="0.00" type="number" />
                          <Input label="Preço venda" prefix="R$" value={c.sale_price} onChange={e => updateCard(c.id, { sale_price: e.target.value.replace(/[^0-9.,]/g, '') })} placeholder="0.00" hint={`Margem ${margin}%`} type="number" />
                        </div>
                      ) : (
                        <Input label="Custo" prefix="R$" value={c.cost_price} onChange={e => updateCard(c.id, { cost_price: e.target.value.replace(/[^0-9.,]/g, '') })} placeholder="0.00" type="number" />
                      )}
                    </div>

                    {/* VARIANTES */}
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                        <div style={secTitle}>Variantes</div>
                        {c.mode === 'novo' && (
                          <span onClick={() => addVariant(c.id)} style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Linha</span>
                        )}
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr 56px 28px', gap: 8, fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', padding: '0 10px', letterSpacing: 0.4 }}>
                          <span>Tamanho</span><span>Cor</span><span>Qtd</span><span />
                        </div>
                        {c.variants.map((v, i) => (
                          <div key={i} style={{ display: 'grid', gridTemplateColumns: '80px 1fr 56px 28px', gap: 8, alignItems: 'center', padding: 10, background: 'var(--bg-3)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                            {c.mode === 'novo' ? (
                              <select value={v.size} onChange={e => updateVariant(c.id, i, 'size', e.target.value)} style={cellSelectStyle}>
                                {SIZES.map(s => <option key={s} value={s}>{s}</option>)}
                              </select>
                            ) : (
                              <div style={{ height: 34, borderRadius: 8, background: 'var(--bg-2)', border: '1px solid var(--line-1)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 700, color: 'var(--gold-300)' }}>
                                {v.size}
                              </div>
                            )}
                            <input
                              value={v.color}
                              onChange={e => updateVariant(c.id, i, 'color', e.target.value)}
                              readOnly={c.mode === 'reposicao'}
                              placeholder="Cor"
                              style={{ height: 34, borderRadius: 8, background: c.mode === 'reposicao' ? 'var(--bg-2)' : 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 13, textAlign: 'center', outline: 0, padding: '0 6px', width: '100%' }}
                            />
                            <input
                              value={v.qty}
                              onChange={e => updateVariant(c.id, i, 'qty', e.target.value.replace(/\D/g, ''))}
                              type="text" inputMode="numeric" placeholder="0"
                              style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, fontWeight: 700, textAlign: 'center', outline: 0 }}
                            />
                            <div
                              onClick={() => c.mode === 'novo' && c.variants.length > 1 ? removeVariant(c.id, i) : undefined}
                              style={{ cursor: c.mode === 'novo' && c.variants.length > 1 ? 'pointer' : 'default', display: 'grid', placeItems: 'center', opacity: c.mode === 'novo' && c.variants.length > 1 ? 1 : 0.15 }}
                            >
                              <Ico.close size={16} stroke="var(--text-3)" />
                            </div>
                          </div>
                        ))}
                      </div>
                      {cardQty(c) > 0 && (
                        <div style={{ fontSize: 12, color: 'var(--text-3)', textAlign: 'right', marginTop: 8 }}>
                          {cardQty(c)} unidades
                          {c.cost_price && <> · <span className="tnum" style={{ color: 'var(--gold-300)', fontWeight: 600 }}>{fmtBRL(cardCost(c))}</span></>}
                        </div>
                      )}
                    </div>

                  </div>
                </div>
              )
            })}

            <button
              onClick={() => setCards(prev => [...prev, blankCard()])}
              style={{ height: 44, border: '1.5px dashed var(--line-3)', background: 'transparent', color: 'var(--gold-500)', borderRadius: 12, fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, width: '100%', cursor: 'pointer' }}
            >
              <Ico.plus size={16} stroke="var(--gold-500)" /> Adicionar produto
            </button>
          </div>
        </Section>

        {totalVariants > 0 && (
          <div style={{ marginTop: 12, padding: '12px 14px', background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12.5 }}>
              <span style={{ color: 'var(--text-2)' }}>{cards.length} produto(s) · {totalVariants} variante(s)</span>
              <span className="tnum" style={{ fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRL(totalCost)}</span>
            </div>
          </div>
        )}

        <div style={{ marginTop: 8 }}>
          <Btn kind="primary" full size="lg" icon={Ico.check} onClick={handleSubmit}>
            {saving ? 'Salvando…' : 'Registrar entrada'}
          </Btn>
        </div>

      </ScreenBody>
    </>
  )
}
