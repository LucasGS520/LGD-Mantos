import { AppBar, ScreenBody } from '../../components/Chrome'
import { Card } from '../../components/UI'

export default function About() {
  return (
    <>
      <AppBar back title="Sobre o app" />
      <ScreenBody>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '32px 0 24px' }}>
          <div style={{ width: 80, height: 80, borderRadius: 24, background: '#0A0A0B', display: 'grid', placeItems: 'center', border: '1px solid rgba(212,168,71,0.3)' }}>
            <img src="/logo_lgd.png" style={{ width: 64, height: 64, objectFit: 'contain' }} alt="LGD" />
          </div>
          <div style={{ fontSize: 20, fontWeight: 800, marginTop: 16, letterSpacing: -0.3 }}>LGD Mantos</div>
          <div style={{ fontSize: 12, color: 'var(--text-3)', marginTop: 4 }}>Sistema de gestão interno</div>
        </div>

        <Card padding={0}>
          {[
            { label: 'Versão',     value: 'v1.0.0'         },
            { label: 'Plataforma', value: 'PWA / Web'       },
            { label: 'Backend',    value: 'FastAPI + PostgreSQL' },
          ].map((row, i) => (
            <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px 16px', borderTop: i === 0 ? undefined : '1px solid var(--line-1)' }}>
              <span style={{ fontSize: 13, color: 'var(--text-2)', fontWeight: 600 }}>{row.label}</span>
              <span style={{ fontSize: 13, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>{row.value}</span>
            </div>
          ))}
        </Card>
      </ScreenBody>
    </>
  )
}
