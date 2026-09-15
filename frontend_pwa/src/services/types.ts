// Auth
export interface LoginResponse {
  token: string
}

// Catalog
export interface Variant {
  id: string
  product_id: string
  size: string
  color: string
  stock_quantity: number
  price_override: number | null
}

export interface Product {
  id: string
  sku: string
  name: string
  description: string | null
  category_id: string | null
  supplier_id: string | null
  cost_price: number
  sale_price: number
  brand: string | null
  product_type: string | null
  notes: string | null
  photos: string[] | null
  is_active: boolean
  created_at: string
  variants: Variant[]
}

// Sale Channels
export interface SaleChannel {
  id: string
  name: string
  description: string | null
  color: string
  fee_pct: number
  monthly_goal: number | null
  is_active: boolean
  created_at: string
}

// Categories
export interface Category {
  id: string
  name: string
  description: string | null
  created_at: string
}

// Suppliers
export interface Supplier {
  id: string
  name: string
  contact: string | null
  phone: string | null
  email: string | null
  notes: string | null
  is_active: boolean
  created_at: string
}

// Sales
export interface SaleItem {
  id: string
  variant_id: string
  quantity: number
  unit_price: number
  unit_cost: number
}

export interface Sale {
  id: string
  sold_at: string
  sale_channel_id: string | null
  notes: string | null
  total: number
  items: SaleItem[]
}

// Merchandise Entries
export interface EntryItem {
  id: string
  variant_id: string
  quantity: number
  unit_cost: number
}

export interface MerchandiseEntry {
  id: string
  supplier_id: string | null
  entry_date: string
  notes: string | null
  total_cost: number
  products_created: number
  variants_added: number
  created_at: string
  items: EntryItem[]
}

// Expenses
export interface Expense {
  id: string
  date: string
  category: string
  amount: number
  description: string | null
  created_at: string
}

// Stock
export interface StockMovement {
  id: string
  variant_id: string
  movement_type: 'entrada' | 'saida'
  quantity: number
  unit_cost: number
  notes: string | null
  created_at: string
}

// Analytics
export interface DailyRevenue {
  date: string
  value: number
}

/** Um indicador com seu valor no período anterior e a variação entre eles.
 *  `variacao_pct` é null quando não há base de comparação (anterior ausente ou zero). */
export interface Comparado {
  atual: number
  anterior: number | null
  variacao_pct: number | null
}

export interface Dashboard {
  today_revenue: number
  today_count: number
  month_revenue: number
  month_cogs: number
  month_expenses: number
  gross_profit: number
  net_profit: number
  margin_pct: number
  avg_ticket: number
  total_units_sold: number
  stock_cost_value: number
  stock_sale_value: number
  stock_units: number
  daily_revenue: DailyRevenue[]
  // Só vem com `?compare=true` — variação de cada indicador vs. mesmos dias do mês anterior.
  comparacao?: {
    month_revenue: Comparado
    gross_profit: Comparado
    net_profit: Comparado
    margin_pct: Comparado
    avg_ticket: Comparado
    total_units_sold: Comparado
  }
}

export interface TopProduct {
  name: string
  sku: string
  qty: number
  revenue: number
  profit: number
}

export interface BySizeItem {
  size: string
  qty: number
}

export interface ByChannelItem {
  channel: string
  count: number
  total: number
  // Só vem com `?compare=true` — variação de receita e nº de vendas daquele canal.
  comparacao?: {
    total: Comparado
    count: Comparado
  }
}

export interface DRE {
  period: string
  revenue: number
  cogs: number
  gross_profit: number
  gross_margin_pct: number
  expenses: number
  expenses_by_category: { category: string; total: number }[]
  net_profit: number
  margin_pct: number
  break_even: number | null
  evolution: { period: string; revenue: number; net_profit: number }[]
  // Só vem com `?compare=true` — variação vs. mês fechado anterior (virada de ano tratada no backend).
  comparacao?: {
    revenue: Comparado
    cogs: Comparado
    gross_profit: Comparado
    gross_margin_pct: Comparado
    expenses: Comparado
    net_profit: Comparado
    margin_pct: Comparado
  }
}

// Analytics — Product Analysis
export interface TopProductDetail {
  name: string
  sku: string
  qty: number
  revenue: number
  profit: number
  margin_pct?: number
}

export interface RuptureRiskItem {
  product_name: string
  sku: string
  size: string | null
  color: string | null
  stock: number
  sold_30d: number
  days_remaining: number
}

export interface StoppedProduct {
  name: string
  sku: string
  total_stock: number
}

export interface ProductAnalysis {
  period_days: number
  top_by_profit: TopProductDetail[]
  top_by_margin: TopProductDetail[]
  stopped: StoppedProduct[]
  rupture_risk: RuptureRiskItem[]
  top_categories: { category: string; qty: number; revenue: number }[]
}

// Analytics — Data Quality
export interface DataQuality {
  score: number
  total_issues: number
  issues: {
    no_cost_price: { name: string; sku: string }[]
    no_sale_price: { name: string; sku: string }[]
    no_supplier: { name: string; sku: string }[]
    no_category: { name: string; sku: string }[]
    active_no_photo: { name: string; sku: string }[]
    variants_without_info: { name: string; sku: string; size: string; color: string }[]
    sales_without_channel: { id: string; sold_at: string; total: number }[]
    expenses_without_category: { id: string; date: string; amount: number; description: string | null }[]
  }
}

// Analytics — Category
export interface CategoryPerformance {
  category_id: string
  category_name: string
  units: number
  revenue: number
  cogs: number
  profit: number
  margin_pct: number
  daily_velocity: number
}

export interface SizeShare {
  size: string
  qty: number
  pct: number
}

export interface CategorySizeDistribution {
  category_name: string
  total_units: number
  sizes: SizeShare[]
}

export interface CategoryCoverage {
  category_id: string
  category_name: string
  stock_units: number
  stock_value: number
  daily_velocity: number
  coverage_days: number | null
}

export interface BuyingPattern {
  category_name: string
  monthly_sales_avg: number
  coverage_days: number | null
  suggested_batch: number
  top_sizes: { size: string; pct: number }[]
  avg_margin_pct: number
  active_product_count: number
}

export interface CategorySizeStock {
  category_name: string
  sizes: { size: string; stock: number }[]
}

// Analytics — Classificação de produtos (substitui a antiga Marketing Intelligence)
export interface ClassifiedVariant {
  product_name: string
  sku: string
  size: string | null
  color: string | null
  stock: number
  margin_pct: number
  sold_30d: number
  reason: string
}

/** Cinco situações de estoque devolvidas por GET /analytics/product-classification.
 *  A sexta situação — produto parado — vem de ProductAnalysis.stopped. */
export interface ProductClassification {
  alta_saida_estoque_saudavel: ClassifiedVariant[]
  margem_alta: ClassifiedVariant[]
  baixa_saida_estoque_alto: ClassifiedVariant[]
  estoque_critico: ClassifiedVariant[]
  sem_estoque: ClassifiedVariant[]
}

// ─── Configurações e Status do sistema ─────────────────────────────────────

// Limiares de alerta configuráveis (tela Configurações). O payload de escrita
// exige os três campos — não há atualização parcial (ver PreferencesUpdate no backend).
export interface AppPreferences {
  rupture_days: number
  stopped_days: number
  critical_stock: number
  updated_at: string
}

export type AppPreferencesInput = Pick<AppPreferences, 'rupture_days' | 'stopped_days' | 'critical_stock'>

// Resposta de GET /health — rota pública, usada pela tela Status do sistema.
export interface HealthStatus {
  status: string
  version: string
  database: 'ok' | 'error'
  server_time: string
}
