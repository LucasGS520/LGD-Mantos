import { useNav } from './nav'

import Login from './screens/Login'
import ProductList from './screens/op/ProductList'
import ProductDetail from './screens/op/ProductDetail'
import ProductForm from './screens/op/ProductForm'
import SaleModal from './screens/op/SaleModal'
import SalesHistory from './screens/op/SalesHistory'
import PurchaseForm from './screens/op/PurchaseForm'
import PurchaseList from './screens/op/PurchaseList'
import Expenses from './screens/op/Expenses'
import StockMoves from './screens/op/StockMoves'
import StockAlerts from './screens/op/StockAlerts'
import Dashboard from './screens/an/Dashboard'
import TopProducts from './screens/an/TopProducts'
import BySize from './screens/an/BySize'
import ByChannel from './screens/an/ByChannel'
import Suggestions from './screens/an/Suggestions'
import DRE from './screens/an/DRE'
import Marketing from './screens/Marketing'
import More from './screens/mais/More'
import Suppliers from './screens/mais/Suppliers'

export default function App() {
  const { screen } = useNav()

  const screens: Record<string, JSX.Element> = {
    'login':          <Login />,
    'product-list':   <ProductList />,
    'product-detail': <ProductDetail />,
    'product-form':   <ProductForm />,
    'sale-modal':     <SaleModal />,
    'sales-history':  <SalesHistory />,
    'purchase-form':  <PurchaseForm />,
    'purchase-list':  <PurchaseList />,
    'expenses':       <Expenses />,
    'stock-moves':    <StockMoves />,
    'stock-alerts':   <StockAlerts />,
    'dashboard':      <Dashboard />,
    'top-products':   <TopProducts />,
    'by-size':        <BySize />,
    'by-channel':     <ByChannel />,
    'suggestions':    <Suggestions />,
    'dre':            <DRE />,
    'marketing':      <Marketing />,
    'more':           <More />,
    'suppliers':      <Suppliers />,
  }

  return (
    <div style={{
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
      background: 'var(--bg-0)',
      fontFamily: 'var(--font-sans)',
      color: 'var(--text-1)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {screens[screen] ?? <Login />}
    </div>
  )
}
