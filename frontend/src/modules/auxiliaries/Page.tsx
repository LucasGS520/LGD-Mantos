import { useState } from "react";
import { AppBar } from "../../components/Chrome";
import { Select } from "../../shared/ui/Select";
import { CategoriesPage } from "./categories/Page";
import { auxLabels } from "./labels";
import { PaymentMethodsPage } from "./payment-methods/Page";
import { PurchaseChannelsPage } from "./purchase-channels/Page";
import { SaleChannelsPage } from "./sale-channels/Page";
import { SuppliersPage } from "./suppliers/Page";
const pages: Record<string, () => JSX.Element> = {
  supplier: SuppliersPage,
  category: CategoriesPage,
  purchase_channel: PurchaseChannelsPage,
  sale_channel: SaleChannelsPage,
  payment_method: PaymentMethodsPage,
};
export function AuxiliaryScreen() {
  const [kind, setKind] = useState("supplier");
  const Page = pages[kind];
  return (
    <>
      <AppBar title="Cadastros auxiliares" back />
      <Select
        label="Cadastro"
        allowEmpty={false}
        value={kind}
        onChange={setKind}
        options={Object.entries(auxLabels).map(([id, name]) => ({ id, name }))}
      />
      <Page key={kind} />
    </>
  );
}
