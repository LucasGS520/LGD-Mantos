import { Ico } from '../../components/Icons'
import { KPI, ChannelChip, Section, LoadingBody, ErrorBody } from '../../components/UI'
import { AppBar, BottomNav, FAB, OpSubNav, ScreenBody } from '../../components/Chrome'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { Sale } from '../../services/types'
import { useNav } from '../../nav'

function fmtDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' })
  } catch { return iso }
}

function fmtTime(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

function groupByDate(sales: Sale[]) {
  const map = new Map<string, Sale[]>()
  for (const s of sales) {
    const key = fmtDate(s.sold_at)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(s)
  }
  return Array.from(map.entries())
}

export default function SalesHistory() {
  const { navigate } = useNav()
  const { data: sales, loading, error, reload } = useData<Sale[]>(() => api.get('/sales?limit=200'))

  const totalRev = (sales ?? []).reduce((s, v) => s + v.total, 0)
  const groups = groupByDate(sales ?? [])

  return (
    <>
      <AppBar title="Vendas" subtitle={`Últimas ${(sales ?? []).length} vendas`} action={
        <button style={{ width: 38, height: 38, borderRadius: 12, border: '1px solid var(--line-2)', background: 'var(--bg-2)', display: 'grid', placeItems: 'center' }}>
          <Ico.calendar size={18} stroke="var(--text-1)" />
        </button>
      } />
      <OpSubNav active="sales-history" />

      {!loading && !error && (
        <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            <KPI label="Receita total" value={fmtBRL(totalRev)} big />
            <KPI label="Nº de vendas" value={String(sales?.length ?? 0)} big />
          </div>
        </div>
      )}

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {groups.map(([date, daySales], di) => (
            <Section title={date} top={di === 0 ? 14 : 18} key={date}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {daySales.map(s => (
                  <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 12, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12 }}>
                    <div style={{ width: 38, height: 38, borderRadius: 10, display: 'grid', placeItems: 'center', background: 'var(--bg-3)', border: '1px solid var(--line-2)' }}>
                      <Ico.cart size={18} stroke="var(--gold-500)" />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)', fontWeight: 600 }}>#{s.id.slice(0, 8)}</span>
                        <span style={{ fontSize: 11, color: 'var(--text-3)' }}>· {fmtTime(s.sold_at)}</span>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                        <ChannelChip ch={s.channel} />
                        <span style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{s.items.length} {s.items.length === 1 ? 'item' : 'itens'}</span>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: 'var(--gold-300)' }}>{fmtBRL(s.total)}</div>
                    </div>
                  </div>
                ))}
              </div>
            </Section>
          ))}
          {groups.length === 0 && (
            <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhuma venda registrada</div>
          )}
        </ScreenBody>
      )}

      <FAB icon={Ico.plus} label="Nova venda" onClick={() => navigate('sale-modal')} />
      <BottomNav active="op" />
    </>
  )
}
