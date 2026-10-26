import { useEffect, useState } from 'react'
import { AppBar, ScreenBody } from '../../components/Chrome'
import { Card, Section, Btn, LoadingBody } from '../../components/UI'
import { Ico } from '../../components/Icons'
import { api } from '../../services/api'
import { Session } from '../../services/session'

const EXPORT_SETS: { key: string; label: string }[] = [
  { key: 'produtos',       label: 'Produtos' },
  { key: 'vendas',         label: 'Vendas' },
  { key: 'compras',        label: 'Compras' },
  { key: 'despesas',       label: 'Despesas' },
  { key: 'movimentacoes',  label: 'Movimentações de estoque' },
  { key: 'cadastros',      label: 'Cadastros (categorias, fornecedores, canais)' },
]

export default function Settings() {
  const [loading, setLoading] = useState(true)

  const [ruptureDays, setRuptureDays]     = useState('')
  const [stoppedDays, setStoppedDays]     = useState('')
  const [criticalStock, setCriticalStock] = useState('')
  const [saving, setSaving]   = useState(false)
  const [error, setError]     = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const [exportingKey, setExportingKey] = useState<string | null>(null)
  const [exportError, setExportError]   = useState<string | null>(null)

  useEffect(() => {
    api.getPreferences()
      .then(p => {
        setRuptureDays(String(p.rupture_days))
        setStoppedDays(String(p.stopped_days))
        setCriticalStock(String(p.critical_stock))
      })
      .catch(e => setError(e instanceof Error ? e.message : 'Erro ao carregar preferências'))
      .finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    if (saving) return
    const rupture = parseInt(ruptureDays, 10)
    const stopped = parseInt(stoppedDays, 10)
    const critical = parseInt(criticalStock, 10)

    if (!Number.isInteger(rupture) || rupture < 1 || rupture > 90) {
      setError('Dias para risco de ruptura deve ser um número entre 1 e 90'); return
    }
    if (!Number.isInteger(stopped) || stopped < 7 || stopped > 365) {
      setError('Dias para produto parado deve ser um número entre 7 e 365'); return
    }
    if (!Number.isInteger(critical) || critical < 0 || critical > 100) {
      setError('Estoque crítico deve ser um número entre 0 e 100'); return
    }

    setSaving(true)
    setError(null)
    try {
      await api.updatePreferences({ rupture_days: rupture, stopped_days: stopped, critical_stock: critical })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Erro ao salvar preferências')
    } finally {
      setSaving(false)
    }
  }

  const handleExport = async (key: string) => {
    if (exportingKey) return
    setExportError(null)
    setExportingKey(key)
    try {
      await api.exportDataset(key)
    } catch (e) {
      setExportError(e instanceof Error ? e.message : 'Erro ao exportar dados')
    } finally {
      setExportingKey(null)
    }
  }

  const handleBackup = async () => {
    if (exportingKey) return
    setExportError(null)
    setExportingKey('backup')
    try {
      await api.exportBackup()
    } catch (e) {
      setExportError(e instanceof Error ? e.message : 'Erro ao gerar relatórios')
    } finally {
      setExportingKey(null)
    }
  }

  const expiry = Session.getExpiry()

  if (loading) return <><AppBar back title="Configurações" /><LoadingBody /></>

  return (
    <>
      <AppBar back title="Configurações" />
      <ScreenBody>
        <Section title="Alertas" top={4}>
          <Card padding={14}>
            <div style={{ fontSize: 12, color: 'var(--text-3)', marginBottom: 14, lineHeight: 1.5 }}>
              Limiares usados pelas análises de risco de ruptura, produtos parados e reposição.
            </div>

            {error && (
              <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600 }}>
                {error}
              </div>
            )}
            {success && (
              <div style={{ marginBottom: 12, padding: '10px 14px', borderRadius: 10, background: 'rgba(63,184,124,0.12)', border: '1px solid rgba(63,184,124,0.3)', fontSize: 12.5, color: '#5DD49E', fontWeight: 600, textAlign: 'center' }}>
                Preferências salvas!
              </div>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <NumberField
                label="Dias para risco de ruptura"
                value={ruptureDays}
                onChange={setRuptureDays}
                hint="Variantes com menos dias de estoque restante entram no alerta de ruptura (1–90)."
              />
              <NumberField
                label="Dias para produto parado"
                value={stoppedDays}
                onChange={setStoppedDays}
                hint="Produtos sem venda por esse período entram na lista de parados (7–365)."
              />
              <NumberField
                label="Estoque crítico"
                value={criticalStock}
                onChange={setCriticalStock}
                suffix="un."
                hint="Estoque igual ou abaixo disso dispara alerta de reposição antes de postar (0–100)."
              />
            </div>

            <Btn kind="primary" size="md" full style={{ marginTop: 16 }} onClick={handleSave}>
              {saving ? 'Salvando…' : 'Salvar alertas'}
            </Btn>
          </Card>
        </Section>

        <Section title="Dados" top={20}>
          <Card padding={0}>
            {EXPORT_SETS.map((ds, i) => (
              <div
                key={ds.key}
                onClick={() => handleExport(ds.key)}
                style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '13px 16px', borderTop: i === 0 ? undefined : '1px solid var(--line-1)', cursor: exportingKey ? 'default' : 'pointer', opacity: exportingKey && exportingKey !== ds.key ? 0.5 : 1 }}
              >
                <div style={{ width: 32, height: 32, borderRadius: 9, background: 'var(--bg-3)', display: 'grid', placeItems: 'center', flexShrink: 0 }}>
                  <Ico.download size={16} stroke="var(--text-2)" />
                </div>
                <span style={{ flex: 1, fontSize: 13, fontWeight: 600 }}>{ds.label}</span>
                <span style={{ fontSize: 11, color: 'var(--text-3)' }}>{exportingKey === ds.key ? 'Baixando…' : 'CSV'}</span>
              </div>
            ))}
          </Card>

          {exportError && (
            <div style={{ marginTop: 10, padding: '10px 14px', borderRadius: 10, background: 'rgba(232,88,79,0.1)', border: '1px solid rgba(232,88,79,0.3)', fontSize: 12.5, color: '#F5847B', fontWeight: 600 }}>
              {exportError}
            </div>
          )}

          <Btn kind="secondary" icon={Ico.package} full style={{ marginTop: 12 }} onClick={handleBackup}>
            {exportingKey === 'backup' ? 'Gerando relatórios…' : 'Exportar relatórios (.zip)'}
          </Btn>
        </Section>

        <Section title="Segurança" top={20}>
          <Card padding={14}>
            <div style={{ display: 'flex', gap: 10 }}>
              <div style={{ flexShrink: 0, marginTop: 2 }}>
                <Ico.lock size={16} stroke="var(--text-3)" />
              </div>
              <div style={{ fontSize: 12.5, color: 'var(--text-3)', lineHeight: 1.5 }}>
                A senha de acesso é definida no servidor. Para trocá-la, altere <code>APP_PASSWORD</code> no <code>.env</code> da VPS e reinicie o container.
              </div>
            </div>
            {expiry && (
              <div style={{ fontSize: 12, color: 'var(--text-4)', marginTop: 10, paddingTop: 10, borderTop: '1px solid var(--line-1)' }}>
                Sessão válida até {expiry.toLocaleDateString('pt-BR')} às {expiry.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            )}
          </Card>
        </Section>
      </ScreenBody>
    </>
  )
}

interface NumberFieldProps { label: string; value: string; onChange: (v: string) => void; hint: string; suffix?: string }
function NumberField({ label, value, onChange, hint, suffix = 'dias' }: NumberFieldProps) {
  return (
    <div>
      <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-2)', marginBottom: 6, letterSpacing: 0.2, textTransform: 'uppercase' }}>{label}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, height: 46, padding: '0 14px', borderRadius: 12, background: 'var(--bg-4)', border: '1px solid var(--line-2)' }}>
        <input
          type="text"
          inputMode="numeric"
          value={value}
          onChange={e => onChange(e.target.value.replace(/[^0-9]/g, ''))}
          style={{ flex: 1, background: 'transparent', border: 0, outline: 'none', color: 'var(--text-1)', fontSize: 15, fontWeight: 500 }}
        />
        <span style={{ color: 'var(--text-3)', fontSize: 13, flexShrink: 0 }}>{suffix}</span>
      </div>
      <div style={{ fontSize: 11, color: 'var(--text-4)', marginTop: 4 }}>{hint}</div>
    </div>
  )
}
