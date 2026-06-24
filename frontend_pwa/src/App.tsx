import { useNav } from './nav'

import Login from './screens/Login'
import ProductList from './screens/op/ProductList'
import ProductDetail from './screens/op/ProductDetail'
import ProductForm from './screens/op/ProductForm'
import SaleModal from './screens/op/SaleModal'
import SalesHistory from './screens/op/SalesHistory'
import SaleDetail from './screens/op/SaleDetail'
import EntryForm from './screens/op/EntryForm'
import PurchaseList from './screens/op/PurchaseList'
import EntryDetail from './screens/op/EntryDetail'
import Expenses from './screens/op/Expenses'
import StockMoves from './screens/op/StockMoves'
import Dashboard from './screens/an/Dashboard'
import TopProducts from './screens/an/TopProducts'
import BySize from './screens/an/BySize'
import ByChannel from './screens/an/ByChannel'
import Suggestions from './screens/an/Suggestions'
import DRE from './screens/an/DRE'
import Categorias from './screens/an/Categorias'
import CategoryDetail from './screens/an/CategoryDetail'
import Alertas from './screens/an/Alertas'
import MarketingIntel from './screens/an/MarketingIntel'
import ComprasReposicao from './screens/an/ComprasReposicao'
import Marketing from './screens/Marketing'
import More from './screens/mais/More'
import Suppliers from './screens/mais/Suppliers'
import SupplierForm from './screens/mais/SupplierForm'
import Categories from './screens/mais/Categories'
import CategoryForm from './screens/mais/CategoryForm'
import SaleChannels from './screens/mais/SaleChannels'
import SaleChannelForm from './screens/mais/SaleChannelForm'
import Settings from './screens/mais/Settings'
import About from './screens/mais/About'

export default function App() {
  const { screen } = useNav()

  const screens: Record<string, JSX.Element> = {
    'login':          <Login />,
    'product-list':   <ProductList />,
    'product-detail': <ProductDetail />,
    'product-form':   <ProductForm />,
    'sale-modal':     <SaleModal />,
    'sales-history':  <SalesHistory />,
    'sale-detail':    <SaleDetail />,
    'purchase-form':  <EntryForm />,
    'purchase-list':  <PurchaseList />,
    'entry-detail':   <EntryDetail />,
    'expenses':       <Expenses />,
    'stock-moves':    <StockMoves />,
    'dashboard':          <Dashboard />,
    'top-products':       <TopProducts />,
    'by-size':            <BySize />,
    'by-channel':         <ByChannel />,
    'suggestions':        <Suggestions />,
    'dre':                <DRE />,
    'an-categorias':      <Categorias />,
    'an-category-detail': <CategoryDetail />,
    'an-alertas':         <Alertas />,
    'an-marketing-intel': <MarketingIntel />,
    'an-compras':         <ComprasReposicao />,
    'marketing':      <Marketing />,
    'more':           <More />,
    'suppliers':      <Suppliers />,
    'supplier-form':  <SupplierForm />,
    'categories':     <Categories />,
    'category-form':  <CategoryForm />,
    'sale-channels':  <SaleChannels />,
    'channel-form':   <SaleChannelForm />,
    'settings':       <Settings />,
    'about':          <About />,
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
