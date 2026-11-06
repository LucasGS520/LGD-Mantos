import { MoreScreen } from "./app/MoreScreen";
import { useNav } from "./app/nav";
import Login from "./modules/auth/Login";
import { AuxiliaryScreen } from "./modules/auxiliaries/Page";
import { Catalog } from "./modules/catalog/pages/Catalog";
import { ProductScreen } from "./modules/catalog/pages/ProductScreen";
import { Management } from "./modules/management/pages/Management";
import { OperationDetail } from "./modules/operations/pages/OperationDetail";
import { OperationForm } from "./modules/operations/pages/OperationForm";
import { Operations } from "./modules/operations/pages/Operations";

export default function App() {
  const { screen, params } = useNav();
  const screens: Record<string, JSX.Element> = {
    login: <Login />,
    catalog: <Catalog />,
    product: <ProductScreen />,
    operations: <Operations />,
    "operation-form": <OperationForm />,
    "operation-detail": <OperationDetail />,
    management: <Management />,
    more: <MoreScreen />,
    auxiliaries: <AuxiliaryScreen />,
  };
  return (
    <div
      key={screen + JSON.stringify(params)}
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        background: "var(--bg-0)",
      }}
    >
      {screens[screen] || <Catalog />}
    </div>
  );
}
