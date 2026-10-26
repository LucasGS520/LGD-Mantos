import { Ico } from '../../components/Icons'
import { SearchBar, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, FAB, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Supplier } from '../../services/types'
import { useState } from 'react'
import { useNav } from '../../nav'

function initials(name: string) {
  return name.split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

export default function Suppliers() {
  const { navigate } = useNav()
  const { data: suppliers, loading, error, reload } = useData<Supplier[]>(() => api.get('/suppliers'))
  const [search, setSearch] = useState('')

  const filtered = (suppliers ?? []).filter(s =>
    !search || s.name.toLowerCase().includes(search.toLowerCase())
  )

  const count = suppliers?.length ?? 0

  return (
    <>
      <AppBar back title="Fornecedores" subtitle={loading ? '…' : `${count} ${count === 1 ? 'ativo' : 'ativos'}`} />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <SearchBar placeholder="Buscar fornecedor…" value={search} onChange={setSearch} />
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 12 }}>
            {filtered.map(s => (
              <div
                key={s.id}
                onClick={() => navigate('supplier-form', { supplierId: s.id })}
                style={{ padding: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14, cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(212,168,71,0.1)', color: 'var(--gold-300)', display: 'grid', placeItems: 'center', fontWeight: 800, fontSize: 13, border: '1px solid rgba(212,168,71,0.2)', flexShrink: 0 }}>
                    {initials(s.name)}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 14, fontWeight: 700, marginBottom: 2 }}>{s.name}</div>
                    {s.contact
                      ? <div style={{ fontSize: 12, color: 'var(--text-3)' }}>{s.contact}</div>
                      : <div style={{ fontSize: 12, color: 'var(--text-4)', fontStyle: 'italic' }}>Sem contato</div>
                    }
                  </div>
                  <Ico.chevron size={16} stroke="var(--text-3)" />
                </div>

                {(s.phone || s.email) && (
                  <div style={{ display: 'flex', gap: 16, marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line-1)', flexWrap: 'wrap' }}>
                    {s.phone && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                        <Ico.phone size={12} stroke="var(--text-3)" />
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{s.phone}</span>
                      </div>
                    )}
                    {s.email && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                        <Ico.mail size={12} stroke="var(--text-3)" />
                        <span style={{ fontSize: 11, color: 'var(--text-2)' }}>{s.email}</span>
                      </div>
                    )}
                  </div>
                )}

                {s.notes && (
                  <div style={{ marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line-1)', fontSize: 12, color: 'var(--text-3)', lineHeight: 1.4, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                    {s.notes}
                  </div>
                )}
              </div>
            ))}

            {filtered.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>
                {search ? 'Nenhum fornecedor encontrado' : 'Nenhum fornecedor cadastrado'}
              </div>
            )}
          </div>
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Fornecedor" onClick={() => navigate('supplier-form')} />
    </>
  )
}
