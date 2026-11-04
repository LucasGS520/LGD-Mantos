import { useNav } from "./nav";
import Login from "./screens/Login";
import {
  AuxiliaryScreen,
  Catalog,
  Management,
  MoreScreen,
  OperationDetail,
  OperationForm,
  Operations,
  ProductScreen,
} from "./screens/Workspace";

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
