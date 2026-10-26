import { useState } from 'react'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, ErrorBody, Card, Badge, Btn } from '../../components/UI'
import { MetricInfo, ScoreBar, SectionChart } from '../../components/Analytics'
import { fmtBRL } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type { DataQuality, ProductAnalysis } from '../../services/types'
import { useNav } from '../../nav'
import { Ico } from '../../components/Icons'

export default function Alertas() {
  const { navigate } = useNav()
  const { data: dq, loading: loadDQ, error: errDQ, reload: reloadDQ } = useData<DataQuality>(api.getDataQuality)
  const { data: analysis } = useData<ProductAnalysis>(() => api.getProductAnalysis('current_month'))

  const loading = loadDQ
  const error = errDQ

  return (
    <>
      <AppBar title="Alertas & Saúde" back />

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reloadDQ} /> : (
        <ScreenBody>
          {/* Score de qualidade de dados */}
          {dq && (
            <Card padding={16} style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', letterSpacing: 0.1 }}>Score de qualidade</span>
                  <MetricInfo
                    what="Mede o percentual de completude dos dados do sistema: preços, fotos, fornecedores, categorias, etc."
                    good="Acima de 80% indica que os dados estão bem preenchidos. 100% é o ideal."
                    action="Resolva cada problema listado abaixo para aumentar o score e melhorar a precisão das análises."
                  />
                </div>
                <span className="tnum" style={{ fontSize: 28, fontWeight: 800, color: dq.score >= 80 ? '#5DD49E' : dq.score >= 50 ? '#F5BF7A' : '#F5847B' }}>
                  {dq.score.toFixed(0)}
                </span>
              </div>
              <ScoreBar value={dq.score} />
              {dq.total_issues > 0 && (
                <div style={{ marginTop: 10, fontSize: 13, color: 'var(--text-3)' }}>
                  {dq.total_issues} problema{dq.total_issues > 1 ? 's' : ''} encontrado{dq.total_issues > 1 ? 's' : ''}
                </div>
              )}
            </Card>
          )}

          {/* Problemas de dados */}
          {dq && dq.total_issues > 0 && (
            <SectionChart title="Problemas de dados">
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <IssueGroup
                  label="Produtos sem preço de custo"
                  items={dq.issues.no_cost_price}
                  renderItem={p => `${p.name} (${p.sku})`}
                  tone="danger"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Produtos sem preço de venda"
                  items={dq.issues.no_sale_price}
                  renderItem={p => `${p.name} (${p.sku})`}
                  tone="danger"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Produtos sem categoria"
                  items={dq.issues.no_category}
                  renderItem={p => `${p.name} (${p.sku})`}
                  tone="warn"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Produtos sem fornecedor"
                  items={dq.issues.no_supplier}
                  renderItem={p => `${p.name} (${p.sku})`}
                  tone="warn"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Produtos ativos sem foto"
                  items={dq.issues.active_no_photo}
                  renderItem={p => `${p.name} (${p.sku})`}
                  tone="warn"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Variantes sem informação"
                  items={dq.issues.variants_without_info}
                  renderItem={v => `${v.name} — ${v.size ?? '?'} ${v.color ?? ''}`.trim()}
                  tone="warn"
                  cta="Corrigir"
                  onCta={() => navigate('product-list')}
                />
                <IssueGroup
                  label="Vendas sem canal (últ. 90d)"
                  items={dq.issues.sales_without_channel}
                  renderItem={s => `${new Date(s.sold_at).toLocaleDateString('pt-BR')} — ${fmtBRL(s.total)}`}
                  tone="warn"
                  cta="Ver vendas"
                  onCta={() => navigate('sales-history')}
                />
                <IssueGroup
                  label="Despesas sem categoria"
                  items={dq.issues.expenses_without_category}
                  renderItem={e => `${new Date(e.date).toLocaleDateString('pt-BR')} — ${fmtBRL(e.amount)}${e.description ? ` (${e.description})` : ''}`}
                  tone="warn"
                  cta="Ver despesas"
                  onCta={() => navigate('expenses')}
                />
              </div>
            </SectionChart>
          )}

          {dq && dq.total_issues === 0 && (
            <Card padding={16} style={{ marginBottom: 16, textAlign: 'center' }}>
              <div style={{ fontSize: 28, marginBottom: 8 }}>✓</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#5DD49E', marginBottom: 4 }}>Dados completos!</div>
              <div style={{ fontSize: 13, color: 'var(--text-3)' }}>Todos os campos estão preenchidos. Suas análises estão precisas.</div>
            </Card>
          )}

          {/* Alertas operacionais */}
          <SectionChart title="Alertas operacionais">
            {/* Risco de ruptura */}
            {(analysis?.rupture_risk?.length ?? 0) > 0 && (
              <div style={{ marginBottom: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    <Ico.warning size={15} stroke="#F5847B" />
                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', letterSpacing: 0.3 }}>Risco de ruptura</span>
                  </div>
                  <Badge tone="danger">{analysis!.rupture_risk.length}</Badge>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {analysis!.rupture_risk.map((r, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 12, background: 'rgba(232,88,79,0.06)', border: '1px solid rgba(232,88,79,0.18)' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)', marginBottom: 2 }}>
                          {r.product_name}{r.size ? ` — ${r.size}` : ''}
                        </div>
                        <div style={{ fontSize: 11, color: 'var(--text-3)' }}>
                          {r.stock} un em estoque · {r.sold_30d} vendidos/30d
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', flexShrink: 0 }}>
                        <div className="tnum" style={{ fontSize: 16, fontWeight: 800, color: r.days_remaining < 7 ? '#F5847B' : '#F5BF7A' }}>
                          {r.days_remaining}d
                        </div>
                        <div style={{ fontSize: 10, color: 'var(--text-4)' }}>restantes</div>
                      </div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 10 }}>
                  <Btn kind="ghost" size="sm" icon={Ico.truck} full onClick={() => navigate('purchase-form')}>
                    Registrar entrada de mercadoria
                  </Btn>
                </div>
              </div>
            )}

            {/* Produtos parados */}
            {(analysis?.stopped?.length ?? 0) > 0 && (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                    <Ico.alert size={15} stroke="#F5BF7A" />
                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-2)', textTransform: 'uppercase', letterSpacing: 0.3 }}>Produtos parados</span>
                  </div>
                  <Badge tone="warn">{analysis!.stopped.length}</Badge>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {analysis!.stopped.map((p, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 12, background: 'rgba(232,160,74,0.06)', border: '1px solid rgba(232,160,74,0.18)' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{p.name}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-3)', fontFamily: 'var(--font-mono)' }}>{p.sku}</div>
                      </div>
                      <div className="tnum" style={{ fontSize: 14, fontWeight: 700, color: '#F5BF7A', flexShrink: 0 }}>{p.total_stock} un</div>
                    </div>
                  ))}
                </div>
                <div style={{ marginTop: 10 }}>
                  <Btn kind="ghost" size="sm" icon={Ico.sparkle} full onClick={() => navigate('an-marketing-intel')}>
                    Ver sugestões de marketing
                  </Btn>
                </div>
              </div>
            )}

            {!analysis && <div style={{ color: 'var(--text-3)', fontSize: 13 }}>Carregando alertas…</div>}
            {analysis && !analysis.rupture_risk.length && !analysis.stopped.length && (
              <div style={{ textAlign: 'center', padding: '20px 0', color: 'var(--text-3)', fontSize: 13 }}>
                Nenhum alerta operacional no momento.
              </div>
            )}
          </SectionChart>
        </ScreenBody>
      )}
      <BottomNav active="an" />
    </>
  )
}

function IssueGroup<T>({ label, items, renderItem, tone, cta, onCta }: {
  label: string
  items: T[]
  renderItem: (item: T) => string
  tone: 'danger' | 'warn'
  cta: string
  onCta: () => void
}) {
  const [open, setOpen] = useState(false)
  if (!items.length) return null
  const colors = {
    danger: { bg: 'rgba(232,88,79,0.06)', bd: 'rgba(232,88,79,0.18)', fg: '#F5847B', badgeTone: 'danger' as const },
    warn:   { bg: 'rgba(232,160,74,0.06)', bd: 'rgba(232,160,74,0.18)', fg: '#F5BF7A', badgeTone: 'warn' as const },
  }
  const c = colors[tone]
  return (
    <div style={{ borderRadius: 12, background: c.bg, border: `1px solid ${c.bd}`, overflow: 'hidden' }}>
      <div onClick={() => setOpen(v => !v)} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '11px 14px', cursor: 'pointer' }}>
        <span style={{ flex: 1, fontSize: 13, fontWeight: 600, color: 'var(--text-1)' }}>{label}</span>
        <Badge tone={c.badgeTone}>{items.length}</Badge>
        <Ico.chevronDown size={14} stroke="var(--text-3)" />
      </div>
      {open && (
        <div style={{ padding: '0 14px 12px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 10 }}>
            {items.slice(0, 10).map((item, i) => (
              <div key={i} style={{ fontSize: 12, color: 'var(--text-2)', padding: '4px 0', borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                {renderItem(item)}
              </div>
            ))}
            {items.length > 10 && (
              <div style={{ fontSize: 12, color: 'var(--text-4)' }}>+ {items.length - 10} mais…</div>
            )}
          </div>
          <Btn kind="ghost" size="sm" onClick={onCta}>{cta} →</Btn>
        </div>
      )}
    </div>
  )
}
