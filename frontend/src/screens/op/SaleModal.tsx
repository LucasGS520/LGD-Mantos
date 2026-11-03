import { useState, useEffect, useMemo } from 'react'
import { Ico } from '../../components/Icons'
import { Btn, PhotoPlaceholder, Section } from '../../components/UI'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import type { Product, Variant, SaleChannel, Category } from '../../services/types'
import { useNav } from '../../nav'

interface CartItem {
  variant: Variant & { productName: string; productSku: string; costPrice: number; salePrice: number }
  quantity: number
  unitPrice: number
}

export default function SaleModal() {
  const { back } = useNav()
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [channels, setChannels] = useState<SaleChannel[]>([])
  const [cart, setCart] = useState<CartItem[]>([])
  const [channel, setChannel] = useState<SaleChannel | null>(null)
  const [discount, setDiscount] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPicker, setShowPicker] = useState(false)
  const [search, setSearch] = useState('')
  const [filterCategory, setFilterCategory] = useState<string | null>(null)
  const [addedVariantId, setAddedVariantId] = useState<string | null>(null)

  useEffect(() => {
    api.get<Product[]>('/products').then(setProducts).catch(() => {})
    api.get<Category[]>('/categories').then(setCategories).catch(() => {})
  }, [])

  useEffect(() => {
    api.get<SaleChannel[]>('/channels?active_only=true')
      .then(list => {
        setChannels(list)
        if (list.length > 0) setChannel(list[0])
      })
      .catch(() => {})
  }, [])

  const filteredProducts = useMemo(() => {
    const q = search.toLowerCase()
    return products
      .filter(p => filterCategory == null || p.category_id === filterCategory)
      .filter(p =>
        q === '' ||
        p.name.toLowerCase().includes(q) ||
        p.sku.toLowerCase().includes(q)
      )
      .filter(p => p.variants.some(v => v.stock_quantity > 0))
  }, [products, filterCategory, search])

  const addToCart = (product: Product, variant: Variant) => {
    setCart(prev => {
      const existing = prev.findIndex(i => i.variant.id === variant.id)
      if (existing >= 0) {
        return prev.map((i, idx) => idx === existing ? { ...i, quantity: i.quantity + 1 } : i)
      }
      return [...prev, {
        variant: { ...variant, productName: product.name, productSku: product.sku, costPrice: product.cost_price, salePrice: product.sale_price },
        quantity: 1,
        unitPrice: variant.price_override ?? product.sale_price,
      }]
    })
    setAddedVariantId(variant.id)
    setTimeout(() => setAddedVariantId(null), 900)
  }

  const updateQty = (variantId: string, qty: number) => {
    if (qty <= 0) setCart(prev => prev.filter(i => i.variant.id !== variantId))
    else setCart(prev => prev.map(i => i.variant.id === variantId ? { ...i, quantity: qty } : i))
  }

  const feePct = channel?.fee_pct ?? 0
  const subtotal = cart.reduce((s, i) => s + i.unitPrice * i.quantity, 0)
  const discountAmt = Math.min(parseFloat(discount.replace(',', '.')) || 0, subtotal)
  const net = subtotal - discountAmt
  const feeAmt = net * (feePct / 100)
  const total = net - feeAmt
  const totalCost = cart.reduce((s, i) => s + i.variant.costPrice * i.quantity, 0)
  const profit = total - totalCost

  const handleConfirm = async () => {
    if (cart.length === 0) return
    setSaving(true)
    setError(null)
    try {
      const ratio = subtotal > 0 ? net / subtotal : 1
      await api.post('/sales', {
        sale_channel_id: channel?.id ?? null,
        items: cart.map(i => ({
          variant_id: i.variant.id,
          quantity: i.quantity,
          unit_price: parseFloat((i.unitPrice * ratio).toFixed(2)),
          unit_cost: i.variant.costPrice,
        })),
      })
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao registrar venda')
      setSaving(false)
    }
  }

  return (
    <div style={{ flex: 1, position: 'relative', background: 'rgba(0,0,0,0.6)' }} onClick={back}>
      <div style={{
        position: 'absolute', left: 0, right: 0, bottom: 0,
        background: 'var(--bg-1)', borderRadius: '24px 24px 0 0',
        padding: '14px 18px', paddingBottom: 'calc(24px + env(safe-area-inset-bottom, 0px))',
        maxHeight: '92%', overflow: 'auto',
        borderTop: '1px solid var(--line-2)',
      }} className="lgd-scroll" onClick={e => e.stopPropagation()}>
        <div style={{ width: 44, height: 5, borderRadius: 4, background: 'var(--line-3)', margin: '0 auto 14px' }} />
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
          <div style={{ fontSize: 19, fontWeight: 700, letterSpacing: -0.3 }}>Registrar venda</div>
          <div onClick={back} style={{ cursor: 'pointer' }}><Ico.close size={22} stroke="var(--text-2)" /></div>
        </div>

        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B' }}>{error}</div>
        )}

        <Section title="Itens" top={4}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {cart.map(item => (
              <div key={item.variant.id} style={{ display: 'flex', gap: 10, padding: 10, background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                <PhotoPlaceholder size={48} label={item.variant.productSku.slice(-3)} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{item.variant.productName}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-3)', marginTop: 2 }}>
                    {item.variant.size} · {item.variant.color}
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 6 }}>
                    <button onClick={() => updateQty(item.variant.id, item.quantity - 1)} style={{ width: 24, height: 24, borderRadius: 7, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, display: 'grid', placeItems: 'center' }}>−</button>
                    <span className="tnum" style={{ fontSize: 14, fontWeight: 700, minWidth: 20, textAlign: 'center' }}>{item.quantity}</span>
                    <button onClick={() => updateQty(item.variant.id, item.quantity + 1)} style={{ width: 24, height: 24, borderRadius: 7, background: 'var(--bg-3)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, display: 'grid', placeItems: 'center' }}>+</button>
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRL(item.unitPrice * item.quantity)}</div>
                  <div style={{ fontSize: 11, color: 'var(--text-3)', marginTop: 2 }}>{item.quantity} × {fmtBRL(item.unitPrice)}</div>
                </div>
              </div>
            ))}

            {showPicker ? (
              <div style={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 14, overflow: 'hidden' }}>
                {/* Barra de busca */}
                <div style={{ padding: '10px 12px', borderBottom: '1px solid var(--line-1)', display: 'flex', gap: 8, alignItems: 'center' }}>
                  <Ico.search size={16} stroke="var(--text-3)" />
                  <input
                    autoFocus
                    type="text"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                    placeholder="Buscar por nome ou SKU…"
                    style={{ flex: 1, background: 'transparent', border: 0, outline: 'none', color: 'var(--text-1)', fontSize: 13 }}
                  />
                  <div onClick={() => setShowPicker(false)} style={{ cursor: 'pointer', padding: 2 }}>
                    <Ico.close size={16} stroke="var(--text-3)" />
                  </div>
                </div>

                {/* Chips de categoria */}
                {categories.length > 0 && (
                  <div style={{ display: 'flex', gap: 6, padding: '8px 12px', overflowX: 'auto', borderBottom: '1px solid var(--line-1)' }} className="lgd-scroll">
                    <button
                      onClick={() => setFilterCategory(null)}
                      style={{
                        padding: '4px 12px', borderRadius: 99, fontSize: 11.5, fontWeight: 600, border: '1px solid', flexShrink: 0,
                        background: filterCategory == null ? 'rgba(212,168,71,0.12)' : 'transparent',
                        borderColor: filterCategory == null ? 'var(--gold-500)' : 'var(--line-2)',
                        color: filterCategory == null ? 'var(--gold-300)' : 'var(--text-2)',
                      }}
                    >Todos</button>
                    {categories.map(c => (
                      <button
                        key={c.id}
                        onClick={() => setFilterCategory(filterCategory === c.id ? null : c.id)}
                        style={{
                          padding: '4px 12px', borderRadius: 99, fontSize: 11.5, fontWeight: 600, border: '1px solid', flexShrink: 0,
                          background: filterCategory === c.id ? 'rgba(212,168,71,0.12)' : 'transparent',
                          borderColor: filterCategory === c.id ? 'var(--gold-500)' : 'var(--line-2)',
                          color: filterCategory === c.id ? 'var(--gold-300)' : 'var(--text-2)',
                        }}
                      >{c.name}</button>
                    ))}
                  </div>
                )}

                {/* Lista de produtos com chips de tamanho */}
                <div style={{ maxHeight: 280, overflowY: 'auto' }} className="lgd-scroll">
                  {filteredProducts.length === 0 ? (
                    <div style={{ padding: 20, textAlign: 'center', fontSize: 12.5, color: 'var(--text-3)' }}>
                      Nenhum produto com estoque encontrado
                    </div>
                  ) : filteredProducts.map(p => (
                    <div key={p.id} style={{ padding: '10px 12px', borderTop: '1px solid var(--line-1)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 7 }}>
                        <div style={{ fontSize: 12.5, fontWeight: 600, flex: 1, marginRight: 8 }}>{p.name}</div>
                        <span className="tnum" style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-300)', flexShrink: 0 }}>{fmtBRL(p.sale_price)}</span>
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 5 }}>
                        {p.variants.map(v => {
                          const inCart = cart.find(c => c.variant.id === v.id)?.quantity ?? 0
                          const isAdded = addedVariantId === v.id
                          const hasStock = v.stock_quantity > 0
                          return (
                            <button
                              key={v.id}
                              onClick={() => hasStock ? addToCart(p, v) : undefined}
                              disabled={!hasStock}
                              style={{
                                padding: '4px 9px', borderRadius: 8, fontSize: 11.5, fontWeight: 700,
                                border: '1px solid',
                                borderColor: isAdded ? '#5DD49E' : inCart > 0 ? 'var(--gold-500)' : hasStock ? 'var(--line-2)' : 'transparent',
                                background: isAdded ? 'rgba(93,212,158,0.15)' : inCart > 0 ? 'rgba(212,168,71,0.10)' : hasStock ? 'var(--bg-3)' : 'transparent',
                                color: isAdded ? '#5DD49E' : inCart > 0 ? 'var(--gold-300)' : hasStock ? 'var(--text-1)' : 'var(--text-3)',
                                opacity: hasStock ? 1 : 0.38,
                                cursor: hasStock ? 'pointer' : 'default',
                              }}
                            >
                              {v.size}
                              {inCart > 0 && <span style={{ marginLeft: 3, fontWeight: 400 }}>×{inCart}</span>}
                              {hasStock && <span style={{ marginLeft: 3, fontWeight: 400, opacity: 0.6 }}>{v.stock_quantity}</span>}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <button onClick={() => setShowPicker(true)} style={{ height: 42, border: '1.5px dashed var(--line-3)', background: 'transparent', color: 'var(--gold-500)', borderRadius: 12, fontWeight: 600, fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6, width: '100%' }}>
                <Ico.plus size={16} stroke="var(--gold-500)" /> Adicionar item
              </button>
            )}
          </div>
        </Section>

        <Section title="Canal de venda">
          {channels.length === 0 ? (
            <div style={{ fontSize: 12, color: 'var(--text-3)', padding: '8px 0' }}>Nenhum canal ativo cadastrado</div>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {channels.map(o => (
                <div key={o.id} onClick={() => setChannel(o)} style={{
                  padding: '8px 14px', borderRadius: 99, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6,
                  background: channel?.id === o.id ? 'rgba(212,168,71,0.10)' : 'var(--bg-2)',
                  border: `1px solid ${channel?.id === o.id ? 'var(--gold-500)' : 'var(--line-1)'}`,
                  fontSize: 12, fontWeight: 700, color: channel?.id === o.id ? 'var(--gold-300)' : 'var(--text-2)',
                }}>
                  <span style={{ width: 8, height: 8, borderRadius: 99, background: o.color, flexShrink: 0 }} />
                  {o.name}
                </div>
              ))}
            </div>
          )}
        </Section>

        <Section title="Resumo">
          <div style={{ background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12, padding: 14 }}>
            {[
              { l: 'Subtotal', v: fmtBRL(subtotal), c: undefined as string | undefined },
              discountAmt > 0 ? { l: 'Desconto', v: `− ${fmtBRL(discountAmt)}`, c: '#F5847B' } : null,
              feeAmt > 0 ? { l: `Taxa canal (${feePct}%)`, v: `− ${fmtBRL(feeAmt)}`, c: '#F5847B' } : null,
              { l: 'Custo total', v: fmtBRL(totalCost), c: 'var(--text-3)' },
              { l: 'Lucro estimado', v: fmtBRL(profit), c: '#5DD49E' },
            ].filter((x): x is { l: string; v: string; c: string | undefined } => x !== null).map((row, i) => (
              <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', fontSize: 13 }}>
                <span style={{ color: 'var(--text-2)' }}>{row.l}</span>
                <span className="tnum" style={{ fontWeight: 600, color: row.c || 'var(--text-1)' }}>{row.v}</span>
              </div>
            ))}
            <div style={{ height: 1, background: 'var(--line-1)', margin: '8px 0' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
              <span style={{ fontSize: 13, fontWeight: 700 }}>Total</span>
              <span className="tnum" style={{ fontSize: 22, fontWeight: 800, color: 'var(--gold-300)' }}>{fmtBRL(total)}</span>
            </div>
          </div>
        </Section>

        <Section title="Desconto">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 46, padding: '0 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)' }}>
            <span style={{ color: 'var(--text-3)', fontSize: 14 }}>R$</span>
            <input
              type="text"
              inputMode="decimal"
              value={discount}
              onChange={e => setDiscount(e.target.value.replace(/[^0-9.,]/g, ''))}
              placeholder="0,00  (opcional)"
              style={{ flex: 1, background: 'transparent', border: 0, outline: 'none', color: 'var(--text-1)', fontSize: 15, fontWeight: 500 }}
            />
          </div>
        </Section>

        <Btn kind="primary" full size="lg" icon={Ico.check} onClick={handleConfirm} style={{ marginTop: 14 }}>
          {saving ? 'Registrando…' : 'Confirmar venda'}
        </Btn>
      </div>
    </div>
  )
}
