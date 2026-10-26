import { useState } from 'react'
import { Ico } from '../../components/Icons'
import { LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, FAB, ScreenBody } from '../../components/Chrome'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { SaleChannel } from '../../services/types'
import { useNav } from '../../nav'

export default function SaleChannels() {
  const { navigate } = useNav()
  const { data: channels, loading, error, reload } = useData<SaleChannel[]>(() => api.get('/channels'))
  const [togglingId, setTogglingId] = useState<string | null>(null)

  const handleToggle = async (ch: SaleChannel) => {
    setTogglingId(ch.id)
    try {
      await api.patch(`/channels/${ch.id}/toggle`, {})
      reload()
    } finally {
      setTogglingId(null)
    }
  }

  const active   = (channels ?? []).filter(c => c.is_active)
  const inactive = (channels ?? []).filter(c => !c.is_active)
  const count    = channels?.length ?? 0

  return (
    <>
      <AppBar back title="Canais de venda" subtitle={loading ? '…' : `${active.length} ativos · ${count} total`} />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {[
            { label: 'Ativos', items: active },
            { label: 'Inativos', items: inactive },
          ].map(({ label, items }) => items.length === 0 ? null : (
            <div key={label} style={{ marginTop: label === 'Ativos' ? 12 : 24 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8 }}>{label}</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {items.map(ch => (
                  <div
                    key={ch.id}
                    style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 14px', background: 'var(--bg-1)', border: `1px solid ${ch.is_active ? 'var(--line-1)' : 'var(--line-1)'}`, borderRadius: 12, opacity: ch.is_active ? 1 : 0.55 }}
                  >
                    <div style={{ width: 38, height: 38, borderRadius: 10, background: `${ch.color}1A`, display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                      <div style={{ width: 14, height: 14, borderRadius: 99, background: ch.color }} />
                    </div>
                    <div
                      style={{ flex: 1, minWidth: 0, cursor: 'pointer' }}
                      onClick={() => navigate('channel-form', { channelId: ch.id })}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ fontSize: 14, fontWeight: 700 }}>{ch.name}</div>
                        {ch.fee_pct > 0 && (
                          <span style={{ fontSize: 10, fontWeight: 700, color: '#F5BF7A', background: 'rgba(245,191,122,0.12)', borderRadius: 5, padding: '1px 6px', flexShrink: 0 }}>
                            Taxa {ch.fee_pct}%
                          </span>
                        )}
                      </div>
                      {ch.description
                        ? <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 2, overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis' }}>{ch.description}</div>
                        : <div style={{ fontSize: 12, color: 'var(--text-4)', marginTop: 2, fontStyle: 'italic' }}>Sem descrição</div>
                      }
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div
                        onClick={() => navigate('channel-form', { channelId: ch.id })}
                        style={{ cursor: 'pointer', opacity: 0.5, padding: 4 }}
                      >
                        <Ico.edit size={14} stroke="var(--text-2)" />
                      </div>
                      <button
                        onClick={() => handleToggle(ch)}
                        disabled={togglingId === ch.id}
                        style={{
                          width: 44, height: 26, borderRadius: 99, border: 0, cursor: 'pointer',
                          background: ch.is_active ? ch.color : 'var(--bg-3)',
                          position: 'relative', transition: 'background 0.2s',
                          opacity: togglingId === ch.id ? 0.5 : 1,
                        }}
                        title={ch.is_active ? 'Desativar canal' : 'Ativar canal'}
                      >
                        <span style={{
                          position: 'absolute', top: 3, borderRadius: 99, width: 20, height: 20,
                          background: '#fff', transition: 'left 0.2s',
                          left: ch.is_active ? 21 : 3,
                        }} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {count === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>
              Nenhum canal cadastrado
            </div>
          )}
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Canal" onClick={() => navigate('channel-form')} />
    </>
  )
}
