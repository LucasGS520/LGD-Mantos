import { Ico } from '../../components/Icons'
import { SearchBar } from '../../components/UI'
import { AppBar, FAB, ScreenBody } from '../../components/Chrome'
import { MOCK } from '../../data/mock'

export default function Suppliers() {
  return (
    <>
      <AppBar back title="Fornecedores" subtitle="4 ativos" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <SearchBar placeholder="Buscar fornecedor…" />
      </div>
      <ScreenBody>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 12 }}>
          {MOCK.suppliers.map(s => (
            <div key={s.name} style={{ padding: 14, background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 14 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(212,168,71,0.1)', color: 'var(--gold-300)', display: 'grid', placeItems: 'center', fontWeight: 800, fontSize: 13, border: '1px solid rgba(212,168,71,0.2)' }}>
                  {s.name.split(' ').map(w => w[0]).join('').slice(0, 2)}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 14, fontWeight: 700 }}>{s.name}</div>
                  <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>{s.city}</div>
                </div>
                <Ico.chevron size={18} stroke="var(--text-3)" />
              </div>
              <div style={{ display: 'flex', gap: 14, marginTop: 12, paddingTop: 12, borderTop: '1px solid var(--line-1)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                  <Ico.phone size={13} stroke="var(--text-3)" />
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--text-2)' }}>{s.phone}</span>
                </div>
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12, fontSize: 11, color: 'var(--text-3)' }}>
                  <span>{s.items} itens</span>
                  <span>· últ. {s.last}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </ScreenBody>
      <FAB icon={Ico.plus} label="Fornecedor" />
    </>
  )
}
