import { useState, useEffect } from 'react'
import { Ico } from '../../components/Icons'
import { Badge, PhotoPlaceholder, SearchBar, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Product, Category } from '../../services/types'
import { useNav } from '../../nav'

function totalStock(p: Product) {
  return p.variants.reduce((s, v) => s + v.stock_quantity, 0)
}
function isLowStock(p: Product) {
  return p.variants.some(v => v.stock_quantity <= v.min_stock_alert)
}

export default function ProductList() {
  const { navigate } = useNav()
  const { data: products, loading, error, reload } = useData<Product[]>(() => api.get('/products'))
  const [search, setSearch] = useState('')
  const [activeCatId, setActiveCatId] = useState<string | null>(null)
  const [catMap, setCatMap] = useState<Record<string, string>>({})

  useEffect(() => {
    api.get<Category[]>('/categories')
      .then(cats => setCatMap(Object.fromEntries(cats.map(c => [c.id, c.name]))))
      .catch(() => {})
  }, [])

  // Chips de categoria: IDs presentes nos produtos carregados
  const usedCatIds = Array.from(new Set((products ?? []).map(p => p.category_id).filter(Boolean))) as string[]
  const hasUncategorized = (products ?? []).some(p => !p.category_id)

  const filtered = (products ?? []).filter(p => {
    const matchSearch = !search
      || p.name.toLowerCase().includes(search.toLowerCase())
      || p.sku.toLowerCase().includes(search.toLowerCase())
    const matchCat = activeCatId === null
      || (activeCatId === '__none__' ? !p.category_id : p.category_id === activeCatId)
    return matchSearch && matchCat
  })

  const count = products?.length ?? 0

  const chipStyle = (active: boolean): React.CSSProperties => ({
    padding: '7px 14px', borderRadius: 999, fontSize: 12.5, fontWeight: 600,
    whiteSpace: 'nowrap', cursor: 'pointer',
    background: active ? 'var(--gold-500)' : 'var(--bg-2)',
    color: active ? '#1A1408' : 'var(--text-2)',
    border: active ? '1px solid var(--gold-500)' : '1px solid var(--line-1)',
  })

  return (
    <>
      <AppBar title="Produtos" subtitle={`${count} ${count === 1 ? 'item' : 'itens'}`} action={
        <button style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center' }}>
          <Ico.filter size={18} stroke="var(--text-1)" />
        </button>
      } />
      <OpSubNav active="product-list" />
      <div style={{ padding: '0 18px 12px', flexShrink: 0 }}>
        <SearchBar placeholder="Buscar por nome ou SKU…" value={search} onChange={setSearch} />
        <div style={{ display: 'flex', gap: 8, marginTop: 12, overflowX: 'auto' }} className="lgd-scroll">
          <div onClick={() => setActiveCatId(null)} style={chipStyle(activeCatId === null)}>Todos</div>
          {usedCatIds.map(id => (
            <div key={id} onClick={() => setActiveCatId(id)} style={chipStyle(activeCatId === id)}>
              {catMap[id] ?? id}
            </div>
          ))}
          {hasUncategorized && (
            <div onClick={() => setActiveCatId('__none__')} style={chipStyle(activeCatId === '__none__')}>
              Sem categoria
            </div>
          )}
        </div>
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {filtered.map(p => (
              <div key={p.id} onClick={() => navigate('product-detail', { productId: p.id })} style={{
                display: 'flex', gap: 12, padding: 12, borderRadius: 14,
                background: 'var(--bg-1)', border: '1px solid var(--line-1)', cursor: 'pointer',
              }}>
                <PhotoPlaceholder size={64} label={p.sku.slice(-3)} radius={10} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-3)' }}>{p.sku}</span>
                    {isLowStock(p) && <Badge tone="danger" dot>Estoque baixo</Badge>}
                  </div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', marginBottom: 6, lineHeight: 1.25, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {p.name}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 8 }}>
                    <span className="tnum" style={{ fontSize: 15, fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRL(p.sale_price)}</span>
                    <span style={{ fontSize: 11.5, color: isLowStock(p) ? '#F5847B' : 'var(--text-3)', fontWeight: 600 }}>{totalStock(p)} em estoque</span>
                  </div>
                </div>
              </div>
            ))}
            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>
                Nenhum produto encontrado
              </div>
            )}
          </div>
        </ScreenBody>
      )}

      <FAB label="Novo produto" onClick={() => navigate('product-form')} />
      <BottomNav active="op" />
    </>
  )
}
