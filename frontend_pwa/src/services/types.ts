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
  min_stock_alert: number
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
  notes: string | null
  photos: string[] | null
  is_active: boolean
  created_at: string
  variants: Variant[]
}

// Categories
export interface Category {
  id: string
  name: string
}

// Suppliers
export interface Supplier {
  id: string
  name: string
  contact: string | null
  phone: string | null
  email: string | null
  is_active: boolean
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
  channel: string
  notes: string | null
  total: number
  items: SaleItem[]
}

// Purchases
export interface POItem {
  id: string
  variant_id: string
  quantity: number
  unit_cost: number
}

export interface Purchase {
  id: string
  supplier_id: string
  order_date: string
  status: string
  notes: string | null
  created_at: string
  items: POItem[]
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
export interface StockAlert {
  variant_id: string
  product_name: string
  sku: string
  size: string
  color: string
  stock: number
  min: number
}

export interface StockMovement {
  id: string
  variant_id: string
  movement_type: 'entrada' | 'saida' | 'ajuste' | 'devolucao'
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

export interface Dashboard {
  today_revenue: number
  today_count: number
  month_revenue: number
  month_cogs: number
  month_expenses: number
  gross_profit: number
  net_profit: number
  margin_pct: number
  stock_alerts: number
  stock_cost_value: number
  stock_sale_value: number
  stock_units: number
  daily_revenue: DailyRevenue[]
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
}

export interface Suggestion {
  variant_id: string
  product_name: string
  sku: string
  size: string
  color: string
  stock: number
  sold_30d: number
  days_remaining: number | null
  urgency: 'alta' | 'media'
  suggested_qty: number
}

export interface DRE {
  period: string
  revenue: number
  cogs: number
  gross_profit: number
  expenses: number
  net_profit: number
  margin_pct: number
}

// Marketing
export interface MarketingRequest {
  message: string
  product_ids?: string[]
}

export interface MarketingResponse {
  content: string
}
