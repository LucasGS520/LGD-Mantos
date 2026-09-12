import { useCallback, useEffect, useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Card, Section, Btn } from '../../components/UI'
import { Ico } from '../../components/Icons'
import { api } from '../../services/api'
import { usePwaUpdate, applyServiceWorkerUpdate } from '../../services/pwa'
import type { HealthStatus } from '../../services/types'

// Tempo máximo de espera pelo /health antes de considerar o servidor fora do ar —
// evita a tela ficar travada "verificando…" indefinidamente numa queda real (RNF-01).
const PING_TIMEOUT_MS = 5000

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => setTimeout(() => reject(new Error('Tempo esgotado')), ms)),
  ])
}

export default function SystemStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [latencyMs, setLatencyMs] = useState<number | null>(null)
  const [checking, setChecking] = useState(true)
  const [online, setOnline] = useState(true)
  const [lastCheckedAt, setLastCheckedAt] = useState<Date | null>(null)
  const pwa = usePwaUpdate()

  const check = useCallback(async () => {
    setChecking(true)
    const started = performance.now()
    try {
      const h = await withTimeout(api.getHealth(), PING_TIMEOUT_MS)
      setHealth(h)
      setLatencyMs(Math.round(performance.now() - started))
      setOnline(true)
      setLastCheckedAt(new Date())
    } catch {
      setHealth(null)
      setLatencyMs(null)
      setOnline(false)
    } finally {
      setChecking(false)
    }
  }, [])

  useEffect(() => { check() }, [check])

  return (
    <>
      <AppBar back title="Status do sistema" />
      <ScreenBody>
        <Card padding={16}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 10, height: 10, borderRadius: 99, background: online ? '#5DD49E' : '#F5847B', flexShrink: 0 }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, fontWeight: 700 }}>{online ? 'Conectado ao servidor' : 'Sem conexão'}</div>
              <div style={{ fontSize: 11.5, color: 'var(--text-3)', marginTop: 2 }}>
                {online && latencyMs != null ? `Latência: ${latencyMs} ms` : 'Não foi possível falar com a API'}
              </div>
            </div>
            <div onClick={() => !checking && check()} style={{ cursor: checking ? 'default' : 'pointer', opacity: checking ? 0.4 : 1, padding: 4 }}>
              <Ico.refresh size={18} stroke="var(--text-2)" />
            </div>
          </div>
          {!online && (
            <div style={{ marginTop: 12 }}>
              <Btn kind="secondary" size="sm" full onClick={check}>Tentar novamente</Btn>
            </div>
          )}
        </Card>

        <Section title="Banco de dados" top={18}>
          <Card padding={14}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: 99, background: health?.database === 'ok' ? '#5DD49E' : '#F5847B', flexShrink: 0 }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>
                {health
                  ? (health.database === 'ok' ? 'Operando normalmente' : 'Com problema de conexão')
                  : 'Sem informação — servidor inacessível'}
              </span>
            </div>
          </Card>
        </Section>

        <Section title="Versões" top={18}>
          <Card padding={0}>
            {[
              { label: 'App', value: `v${__APP_VERSION__} · ${__BUILD_HASH__}` },
              { label: 'API', value: health ? `v${health.version}` : '—' },
            ].map((row, i) => (
              <div key={row.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 14px', borderTop: i === 0 ? undefined : '1px solid var(--line-1)' }}>
                <span style={{ fontSize: 13, color: 'var(--text-2)', fontWeight: 600 }}>{row.label}</span>
                <span style={{ fontSize: 13, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>{row.value}</span>
              </div>
            ))}
          </Card>
        </Section>

        <Section title="Atualização do app" top={18}>
          <Card padding={14}>
            {pwa.needsRefresh ? (
              <>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10 }}>Uma nova versão está disponível.</div>
                <Btn kind="primary" size="sm" full onClick={() => applyServiceWorkerUpdate()}>Atualizar agora</Btn>
              </>
            ) : (
              <div style={{ fontSize: 13, color: 'var(--text-3)' }}>Você está usando a versão mais recente.</div>
            )}
          </Card>
        </Section>

        {lastCheckedAt && (
          <div style={{ textAlign: 'center', fontSize: 11, color: 'var(--text-4)', marginTop: 18 }}>
            Última verificação: {lastCheckedAt.toLocaleTimeString('pt-BR')}
          </div>
        )}
      </ScreenBody>
    </>
  )
}
