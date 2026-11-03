import { useState } from 'react'
import { Ico } from '../../components/Icons'
import { SearchBar, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, FAB, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Category } from '../../services/types'
import { useNav } from '../../nav'

export default function Categories() {
  const { navigate } = useNav()
  const { data: categories, loading, error, reload } = useData<Category[]>(() => api.get('/categories'))
  const [search, setSearch] = useState('')

  const filtered = (categories ?? []).filter(c =>
    !search || c.name.toLowerCase().includes(search.toLowerCase())
  )

  const count = categories?.length ?? 0

  return (
    <>
      <AppBar back title="Categorias" subtitle={loading ? '…' : `${count} ${count === 1 ? 'categoria' : 'categorias'}`} />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <SearchBar placeholder="Buscar categoria…" value={search} onChange={setSearch} />
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
            {filtered.map(c => (
              <div
                key={c.id}
                onClick={() => navigate('category-form', { categoryId: c.id })}
                style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, cursor: 'pointer' }}
              >
                <div style={{ width: 38, height: 38, borderRadius: 10, background: 'rgba(212,168,71,0.1)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                  <Ico.tag size={16} stroke="var(--gold-500)" />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 600 }}>{c.name}</div>
                  {c.description
                    ? <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{c.description}</div>
                    : <div style={{ fontSize: 12, color: 'var(--text-4)', marginTop: 2, fontStyle: 'italic' }}>Sem descrição</div>
                  }
                </div>
                <Ico.chevron size={16} stroke="var(--text-3)" />
              </div>
            ))}
            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>
                {search ? 'Nenhuma categoria encontrada' : 'Nenhuma categoria cadastrada'}
              </div>
            )}
          </div>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Categoria" onClick={() => navigate('category-form')} />
    </>
  )
}
