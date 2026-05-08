import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Input, Section, LoadingBody } from '../../components/UI'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import type { Product, Supplier, Category } from '../../services/types'
import { useNav } from '../../nav'

interface VariantRow { size: string; color: string; qty: string }

const SIZES = ['P', 'M', 'G', 'GG', 'G1', 'G2', 'G3']

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

export default function ProductForm() {
  const { back, params } = useNav()
  const productId = params.productId as string | undefined

  const [loading, setLoading] = useState(!!productId)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [categories, setCategories] = useState<Category[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])

  // quick-create state
  const [showNewCat, setShowNewCat] = useState(false)
  const [newCatName, setNewCatName] = useState('')
  const [showNewSup, setShowNewSup] = useState(false)
  const [newSupName, setNewSupName] = useState('')

  const [sku, setSku] = useState('')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [supplierId, setSupplierId] = useState('')
  const [costPrice, setCostPrice] = useState('')
  const [salePrice, setSalePrice] = useState('')
  const [variants, setVariants] = useState<VariantRow[]>([
    { size: 'P', color: 'Preto', qty: '0' },
  ])

  useEffect(() => {
    api.get<Category[]>('/categories').then(setCategories).catch(() => {})
    api.get<Supplier[]>('/suppliers').then(setSuppliers).catch(() => {})

    if (productId) {
      api.get<Product>(`/products/${productId}`)
        .then(p => {
          setSku(p.sku)
          setName(p.name)
          setDescription(p.description ?? '')
          setCategoryId(p.category_id ?? '')
          setSupplierId(p.supplier_id ?? '')
          setCostPrice(String(p.cost_price))
          setSalePrice(String(p.sale_price))
          setVariants(p.variants.map(v => ({
            size: v.size,
            color: v.color,
            qty: String(v.stock_quantity),
          })))
        })
        .catch(e => setError(e instanceof Error ? e.message : 'Erro'))
        .finally(() => setLoading(false))
    }
  }, [productId])

  const createCategory = async () => {
    if (!newCatName.trim()) return
    try {
      const created = await api.post<Category>('/categories', { name: newCatName.trim() })
      setCategories(prev => [...prev, created])
      setCategoryId(created.id)
      setNewCatName('')
      setShowNewCat(false)
    } catch {
      setError('Erro ao criar categoria')
    }
  }

  const createSupplier = async () => {
    if (!newSupName.trim()) return
    try {
      const created = await api.post<Supplier>('/suppliers', { name: newSupName.trim() })
      setSuppliers(prev => [...prev, created])
      setSupplierId(created.id)
      setNewSupName('')
      setShowNewSup(false)
    } catch {
      setError('Erro ao criar fornecedor')
    }
  }

  const parsePrice = (v: string) => parseFloat(v.replace(',', '.')) || 0
  const margin = costPrice && salePrice
    ? (((parsePrice(salePrice) - parsePrice(costPrice)) / parsePrice(salePrice)) * 100).toFixed(0)
    : '—'

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    try {
      const body = {
        name: name.trim(),
        description: description.trim() || null,
        category_id: categoryId || null,
        supplier_id: supplierId || null,
        cost_price: parsePrice(costPrice),
        sale_price: parsePrice(salePrice),
        variants: variants.map(v => ({
          size: v.size.trim(),
          color: v.color.trim(),
          stock_quantity: Math.max(0, parseInt(v.qty) || 0),
          min_stock_alert: 3,
        })),
      }
      if (productId) {
        await api.put(`/products/${productId}`, body)
      } else {
        await api.post('/products', body)
      }
      back()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar')
    } finally {
      setSaving(false)
    }
  }

  const addVariant = () => setVariants(prev => [...prev, { size: 'P', color: '', qty: '0' }])
  const removeVariant = (i: number) => setVariants(prev => prev.filter((_, j) => j !== i))
  const updateVariant = (i: number, key: keyof VariantRow, val: string) =>
    setVariants(prev => prev.map((v, j) => j === i ? { ...v, [key]: val } : v))

  if (loading) return <><AppBar back title={productId ? 'Editar produto' : 'Novo produto'} /><LoadingBody /></>

  return (
    <>
      <AppBar back title={productId ? 'Editar produto' : 'Novo produto'} action={
        <span onClick={handleSave} style={{ fontSize: 13, fontWeight: 700, color: saving ? 'var(--text-3)' : 'var(--gold-500)', cursor: 'pointer' }}>
          {saving ? 'Salvando…' : 'Salvar'}
        </span>
      } />
      <ScreenBody>
        {error && (
          <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600 }}>
            {error}
          </div>
        )}

        <Section title="Identificação" top={4}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {productId && (
              <Input label="SKU" value={sku} readOnly />
            )}
            <Input label="Nome" value={name} onChange={e => setName(e.target.value)} placeholder="Nome do produto" />
            <div>
              <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>Descrição</div>
              <textarea
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Descrição do produto…"
                rows={3}
                style={{ width: '100%', padding: '12px 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 14, resize: 'none', outline: 0, fontFamily: 'inherit' }}
              />
            </div>

            {/* Categoria e Fornecedor com atalho de criação rápida */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>

              {/* Categoria */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', letterSpacing: 0.2, textTransform: 'uppercase' }}>Categoria</span>
                  <span onClick={() => { setShowNewCat(v => !v); setNewCatName('') }} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Nova</span>
                </div>
                {showNewCat && (
                  <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                    <input
                      value={newCatName}
                      onChange={e => setNewCatName(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && createCategory()}
                      placeholder="Nome da categoria"
                      autoFocus
                      style={quickInputStyle}
                    />
                    <button onClick={createCategory} style={quickBtnStyle}>Criar</button>
                  </div>
                )}
                <select value={categoryId} onChange={e => setCategoryId(e.target.value)} style={{ ...selectStyle, color: categoryId ? 'var(--text-1)' : 'var(--text-3)' }}>
                  <option value="">Selecionar</option>
                  {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>

              {/* Fornecedor */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', letterSpacing: 0.2, textTransform: 'uppercase' }}>Fornecedor</span>
                  <span onClick={() => { setShowNewSup(v => !v); setNewSupName('') }} style={{ fontSize: 11, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Novo</span>
                </div>
                {showNewSup && (
                  <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                    <input
                      value={newSupName}
                      onChange={e => setNewSupName(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && createSupplier()}
                      placeholder="Nome do fornecedor"
                      autoFocus
                      style={quickInputStyle}
                    />
                    <button onClick={createSupplier} style={quickBtnStyle}>Criar</button>
                  </div>
                )}
                <select value={supplierId} onChange={e => setSupplierId(e.target.value)} style={{ ...selectStyle, color: supplierId ? 'var(--text-1)' : 'var(--text-3)' }}>
                  <option value="">Selecionar</option>
                  {suppliers.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                </select>
              </div>

            </div>
          </div>
        </Section>

        <Section title="Preço" top={20}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <Input label="Custo" prefix="R$" value={costPrice} onChange={e => setCostPrice(e.target.value.replace(/[^0-9.,]/g, ''))} placeholder="0.00" type="number" />
            <Input label="Preço venda" prefix="R$" value={salePrice} onChange={e => setSalePrice(e.target.value.replace(/[^0-9.,]/g, ''))} placeholder="0.00" hint={`Margem ${margin}%`} type="number" />
          </div>
        </Section>

        <Section title="Variantes" action={<span onClick={addVariant} style={{ fontSize: 12, fontWeight: 700, color: 'var(--gold-500)', cursor: 'pointer' }}>+ Linha</span>} top={20}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '80px 1fr 56px 28px', gap: 8, fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', padding: '0 10px', letterSpacing: 0.4 }}>
              <span>Tamanho</span><span>Cor</span><span>Qtd</span><span />
            </div>
            {variants.map((v, i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '80px 1fr 56px 28px', gap: 8, alignItems: 'center', padding: 10, background: 'var(--bg-2)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                <select
                  value={v.size}
                  onChange={e => updateVariant(i, 'size', e.target.value)}
                  style={cellSelectStyle}
                >
                  {SIZES.map(s => <option key={s} value={s}>{s}</option>)}
                </select>
                <input
                  value={v.color}
                  onChange={e => updateVariant(i, 'color', e.target.value)}
                  placeholder="Cor"
                  style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-2)', fontSize: 13, textAlign: 'center', outline: 0, padding: '0 6px', width: '100%' }}
                />
                <input
                  value={v.qty}
                  onChange={e => updateVariant(i, 'qty', e.target.value.replace(/[^0-9]/g, ''))}
                  type="text"
                  inputMode="numeric"
                  style={{ height: 34, borderRadius: 8, background: 'var(--bg-4)', border: '1px solid var(--line-2)', color: 'var(--text-1)', fontSize: 13, fontWeight: 700, textAlign: 'center', outline: 0 }}
                />
                <div onClick={() => removeVariant(i)} style={{ cursor: 'pointer', display: 'grid', placeItems: 'center' }}>
                  <Ico.close size={16} stroke="var(--text-3)" />
                </div>
              </div>
            ))}
          </div>
        </Section>
      </ScreenBody>
    </>
  )
}
