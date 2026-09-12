import { useState } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { AppBar, BottomNav, ScreenBody } from '../../components/Chrome'
import { LoadingBody, ErrorBody, Tabs, PhotoPlaceholder, Card, Section } from '../../components/UI'
import { SectionChart, CovBadge } from '../../components/Analytics'
import { fmtBRLshort, fmtNum } from '../../fmt'
import { api } from '../../services/api'
import { useData } from '../../hooks/useData'
import type {
  CategoryPerformance, CategoryCoverage, TopProduct, BySizeItem,
  ProductClassification, ProductAnalysis,
} from '../../services/types'
import { useNav } from '../../nav'
import { Ico } from '../../components/Icons'

// Três seções da tela: mix por categoria, ranking por receita e distribuição por tamanho.
const SECOES = ['Categorias', 'Ranking', 'Tamanhos'] as const

export default function Products() {
  const { navigate } = useNav()
  const [secao, setSecao] = useState<string>('Categorias')

  // Período fixo no mês corrente — a tela de origem (Categorias) já usava esse
  // período como padrão. Seletor de período configurável é assunto da Fase 2.
  const period = 'current_month'

  const { data: categorias, loading, error, reload } = useData<CategoryPerformance[]>(
    () => api.getCategoryPerformance(period), period
  )
  const { data: coverage } = useData<CategoryCoverage[]>(api.getCategoryStockCoverage)
  const { data: ranking } = useData<TopProduct[]>(() => api.get('/analytics/top-products?days=30'))
  const { data: tamanhos } = useData<BySizeItem[]>(() => api.get('/analytics/by-size?days=30'))
  const { data: classificacao } = useData<ProductClassification>(api.getProductClassification)
  // A sexta situação (produto parado) vem daqui, não da classificação — ver a
  // nota de interfaces da Task 5 do brief.
  const { data: analise } = useData<ProductAnalysis>(() => api.getProductAnalysis('current_month'))

  const coverageMap = Object.fromEntries((coverage ?? []).map(c => [c.category_name, c.coverage_days]))

  const chartData = (categorias ?? []).slice(0, 8).map(c => ({
    name: c.category_name.length > 14 ? c.category_name.slice(0, 13) + '…' : c.category_name,
    fullName: c.category_name,
    value: c.revenue,
  }))

  const maxTamanho = tamanhos ? Math.max(...tamanhos.map(s => s.qty), 1) : 1

  return (
    <>
      <AppBar back title="Produtos" subtitle="Mix, ranking e situação" />
      <div style={{ padding: '0 18px 6px', flexShrink: 0 }}>
        <Tabs items={[...SECOES]} active={secao} onChange={setSecao} />
      </div>

      {loading ? <LoadingBody /> : error ? <ErrorBody msg={error} onRetry={reload} /> : (
        <ScreenBody>
          {/* ─── Seção Categorias (ex-Categorias.tsx) ─────────────────────── */}
          {secao === 'Categorias' && (
            <>
              {/* Gráfico de receita */}
              <SectionChart title="Receita por categoria" loading={!categorias} empty={chartData.length === 0}>
                <div style={{ height: 200 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} layout="vertical" margin={{ top: 0, right: 8, left: 4, bottom: 0 }}>
                      <XAxis type="number" hide />
                      <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 11, fill: 'var(--text-2)' }} axisLine={false} tickLine={false} />
                      <Tooltip
                        cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                        contentStyle={{ background: 'var(--bg-2)', border: '1px solid var(--line-2)', borderRadius: 8, fontSize: 12 }}
                        formatter={(v) => [fmtBRLshort(Number(v ?? 0)), 'Receita']}
                        labelFormatter={(_, payload: any) => payload?.[0]?.payload?.fullName ?? ''}
                      />
                      <Bar dataKey="value" radius={[0, 6, 6, 0]}>
                        {chartData.map((_, i) => (
                          <Cell key={i} fill={i === 0 ? '#D4A847' : i === 1 ? '#B68B2E' : 'rgba(212,168,71,0.35)'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </SectionChart>

              {/* Lista de categorias */}
              <SectionChart title="Desempenho detalhado" loading={!categorias} empty={(categorias?.length ?? 0) === 0}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                  {(categorias ?? []).map((cat, i) => {
                    const covDays = coverageMap[cat.category_name] ?? null
                    return (
                      <div
                        key={cat.category_id}
                        onClick={() => navigate('intel-category-detail', { categoryId: cat.category_id, categoryName: cat.category_name, period })}
                        style={{
                          padding: '14px 0', borderBottom: '1px solid var(--line-1)',
                          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12,
                        }}
                      >
                        {/* Rank */}
                        <div style={{ width: 24, textAlign: 'center', fontSize: 12, fontWeight: 700, color: i < 3 ? 'var(--gold-400)' : 'var(--text-4)', flexShrink: 0 }}>
                          {i + 1}
                        </div>

                        {/* Dados */}
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', marginBottom: 6 }}>{cat.category_name}</div>
                          <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                            <Pill label="Receita" value={fmtBRLshort(cat.revenue)} color="var(--gold-300)" />
                            <Pill label="Margem" value={`${cat.margin_pct.toFixed(0)}%`} color={cat.margin_pct >= 30 ? '#5DD49E' : cat.margin_pct >= 15 ? '#F5BF7A' : '#F5847B'} />
                            <Pill label="Unid." value={String(cat.units)} color="var(--text-2)" />
                          </div>
                        </div>

                        {/* Cobertura + chevron */}
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                            <span style={{ fontSize: 9.5, color: 'var(--text-4)', textTransform: 'uppercase', letterSpacing: 0.3 }}>Cob.</span>
                            <CovBadge days={covDays} />
                          </div>
                          <Ico.chevron size={14} stroke="var(--text-3)" />
                        </div>
                      </div>
                    )
                  })}
                </div>
              </SectionChart>
            </>
          )}

          {/* ─── Seção Ranking (ex-TopProducts.tsx) ───────────────────────── */}
          {/* O seletor de 7/30/90 dias da tela original não é reproduzido aqui —
              período configurável fica para a Fase 2; 30 dias fixos bastam agora. */}
          {secao === 'Ranking' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12 }}>
              {(ranking ?? []).map((t, idx) => {
                const rank = idx + 1
                return (
                  <div key={t.sku} style={{
                    display: 'flex', alignItems: 'center', gap: 12, padding: 12,
                    background: 'var(--bg-1)', borderRadius: 12,
                    border: `1px solid ${rank <= 3 ? 'rgba(212,168,71,0.25)' : 'var(--line-1)'}`,
                  }}>
                    <div style={{
                      width: 30, height: 30, borderRadius: 8, display: 'grid', placeItems: 'center',
                      background: rank === 1 ? 'var(--gold-500)' : rank <= 3 ? 'rgba(212,168,71,0.15)' : 'var(--bg-3)',
                      color: rank === 1 ? '#1A1408' : rank <= 3 ? 'var(--gold-300)' : 'var(--text-3)',
                      fontWeight: 800, fontSize: 13, fontFamily: 'var(--font-mono)',
                    }}>{rank}</div>
                    <PhotoPlaceholder size={42} label={t.sku.slice(-3)} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{t.name}</div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--text-3)', marginTop: 2 }}>{t.sku}</div>
                      <div style={{ fontSize: 11, color: '#5DD49E', marginTop: 4, fontWeight: 600 }}>
                        {t.qty} vendas · +{fmtBRLshort(t.profit)} lucro
                      </div>
                    </div>
                    <div className="tnum" style={{ fontSize: 14, fontWeight: 800, color: 'var(--gold-300)', textAlign: 'right' }}>
                      {fmtBRLshort(t.revenue)}
                    </div>
                  </div>
                )
              })}
              {(ranking ?? []).length === 0 && (
                <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 32 }}>Nenhum dado disponível</div>
              )}
            </div>
          )}

          {/* ─── Seção Tamanhos (ex-BySize.tsx) ───────────────────────────── */}
          {secao === 'Tamanhos' && (
            <>
              <Card padding={16} style={{ marginTop: 4 }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {(tamanhos ?? []).map(s => {
                    const w = (s.qty / maxTamanho) * 100
                    const isMax = s.qty === maxTamanho
                    return (
                      <div key={s.size}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 5 }}>
                          <span style={{ fontSize: 12.5, fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{s.size}</span>
                          <span className="tnum" style={{ fontSize: 11.5, color: 'var(--text-3)' }}>{s.qty} un</span>
                        </div>
                        <div style={{ height: 14, borderRadius: 7, background: 'var(--bg-3)', overflow: 'hidden' }}>
                          <div style={{ width: `${w}%`, height: '100%', borderRadius: 7, background: isMax ? 'linear-gradient(90deg, var(--gold-500), var(--gold-400))' : 'rgba(212,168,71,0.5)' }} />
                        </div>
                      </div>
                    )
                  })}
                  {(tamanhos ?? []).length === 0 && (
                    <div style={{ textAlign: 'center', color: 'var(--text-3)', fontSize: 13, padding: 16 }}>Nenhum dado disponível</div>
                  )}
                </div>
              </Card>

              {(tamanhos ?? []).length > 0 && (
                <Section title="Tabela detalhada" top={18}>
                  <div style={{ background: 'var(--bg-1)', border: '1px solid var(--line-1)', borderRadius: 12, overflow: 'hidden' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '60px 1fr', padding: '10px 14px', background: 'var(--bg-2)', fontSize: 10, color: 'var(--text-3)', fontWeight: 700, letterSpacing: 0.5, textTransform: 'uppercase' }}>
                      <span>Tam</span><span style={{ textAlign: 'right' }}>Qtd vendida</span>
                    </div>
                    {(tamanhos ?? []).map(s => (
                      <div key={s.size} style={{ display: 'grid', gridTemplateColumns: '60px 1fr', padding: '12px 14px', alignItems: 'center', borderTop: '1px solid var(--line-1)', fontSize: 13 }}>
                        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--gold-300)' }}>{s.size}</span>
                        <span className="tnum" style={{ textAlign: 'right', fontWeight: 600 }}>{fmtNum(s.qty)}</span>
                      </div>
                    ))}
                  </div>
                </Section>
              )}
            </>
          )}

          {/* ─── Situação dos produtos — sempre visível, independente da seção ── */}
          {classificacao && (
            <div style={{ marginTop: 16, borderTop: '1px solid var(--line-1)', paddingTop: 12 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--text-3)', textTransform: 'uppercase', letterSpacing: 1.2, marginBottom: 8 }}>
                Situação dos produtos
              </div>
              {([
                ['Alta saída, estoque saudável', classificacao.alta_saida_estoque_saudavel.length],
                ['Margem alta', classificacao.margem_alta.length],
                ['Baixa saída, estoque alto', classificacao.baixa_saida_estoque_alto.length],
                ['Estoque crítico', classificacao.estoque_critico.length],
                ['Sem estoque', classificacao.sem_estoque.length],
                ['Produto parado', analise?.stopped?.length ?? 0],
              ] as [string, number][]).map(([rotulo, quantidade]) => (
                <div key={rotulo} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--line-1)' }}>
                  <span style={{ fontSize: 13, color: 'var(--text-2)' }}>{rotulo}</span>
                  <span className="tnum" style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-1)' }}>{quantidade}</span>
                </div>
              ))}
            </div>
          )}
        </ScreenBody>
      )}
      <BottomNav active="intel" />
    </>
  )
}

function Pill({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <span style={{ fontSize: 11.5, color: 'var(--text-3)' }}>
      {label}: <span style={{ color, fontWeight: 700 }} className="tnum">{value}</span>
    </span>
  )
}
