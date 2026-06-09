import { AppBar, ScreenBody } from '../../components/Chrome'
import { Card, Section } from '../../components/UI'

export default function Settings() {
  return (
    <>
      <AppBar back title="Configurações" />
      <ScreenBody>
        <Section title="Conta" top={12}>
          <Card padding={14}>
            <div style={{ fontSize: 13, color: 'var(--text-3)', textAlign: 'center', padding: '16px 0' }}>
              Configurações disponíveis em breve.
            </div>
          </Card>
        </Section>

        <Section title="Sincronização" top={18}>
          <Card padding={14}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div style={{ width: 10, height: 10, borderRadius: 99, background: '#5DD49E', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: 13, fontWeight: 700 }}>Conectado ao servidor</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>Dados sincronizados automaticamente</div>
              </div>
            </div>
          </Card>
        </Section>
      </ScreenBody>
    </>
  )
}
