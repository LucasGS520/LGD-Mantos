import type { ReactNode } from 'react'
import { Ico, type IcoProps } from '../../components/Icons'
import { Card, Section } from '../../components/UI'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { useNav } from '../../nav'

interface ItemProps {
  icon: (p: IcoProps) => JSX.Element
  label: string
  hint?: string
  end?: ReactNode
  accent?: boolean
  danger?: boolean
  onClick?: () => void
}
function Item({ icon, label, hint, end, accent, danger, onClick }: ItemProps) {
  const I = icon
  return (
    <div onClick={onClick} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderTop: '1px solid var(--line-1)', cursor: onClick ? 'pointer' : undefined }}>
      <div style={{ width: 36, height: 36, borderRadius: 10, background: danger ? 'rgba(232,88,79,0.1)' : accent ? 'rgba(212,168,71,0.1)' : 'var(--bg-3)', display: 'grid', placeItems: 'center' }}>
        <I size={18} stroke={danger ? '#F5847B' : accent ? 'var(--gold-500)' : 'var(--text-2)'} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 14, fontWeight: 600, color: danger ? '#F5847B' : 'var(--text-1)' }}>{label}</div>
        {hint && <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>{hint}</div>}
      </div>
      {end ?? <Ico.chevron size={16} stroke="var(--text-3)" />}
    </div>
  )
}

export default function More() {
  const { navigate, logout } = useNav()
  return (
    <>
      <AppBar title="Mais" />
      <ScreenBody>
        <div style={{ padding: 18, borderRadius: 16, background: 'linear-gradient(140deg, rgba(212,168,71,0.12), rgba(212,168,71,0.02))', border: '1px solid rgba(212,168,71,0.2)', display: 'flex', alignItems: 'center', gap: 14 }}>
          <div style={{ width: 56, height: 56, borderRadius: 16, background: '#0A0A0B', display: 'grid', placeItems: 'center', border: '1px solid rgba(212,168,71,0.3)' }}>
            <img src="/logo_lgd.png" style={{ width: 44, height: 44, objectFit: 'contain' }} alt="LGD" />
          </div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 800, letterSpacing: -0.2 }}>LGD Mantos</div>
            <div style={{ fontSize: 11.5, color: 'var(--gold-300)', marginTop: 2, fontWeight: 600 }}>Loja única · 1 operador</div>
          </div>
        </div>

        <Section title="Cadastros" top={20}>
          <Card padding={0}>
            <Item icon={Ico.users} label="Fornecedores" accent onClick={() => navigate('suppliers')} />
            <Item icon={Ico.tag}   label="Categorias" />
            <Item icon={Ico.store} label="Canais de venda" />
          </Card>
        </Section>

        <Section title="App" top={18}>
          <Card padding={0}>
            <Item icon={Ico.settings} label="Configurações"  hint="Senha, backup, notificações" />
            <Item icon={Ico.refresh}  label="Sincronização"  hint="Dados sincronizados com o servidor" />
            <Item icon={Ico.doc}      label="Sobre o app"    end={<span style={{ fontSize: 11, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>v1.0.0</span>} />
          </Card>
        </Section>

        <Section title="" top={18}>
          <Card padding={0}>
            <Item icon={Ico.logout} label="Sair" danger onClick={logout} />
          </Card>
        </Section>
      </ScreenBody>
      <BottomNav active="mais" />
    </>
  )
}
