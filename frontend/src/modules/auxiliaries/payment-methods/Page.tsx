import { RecordPage } from "../components/RecordPage";
import { paymentMethodApi } from "./api";
import { PaymentMethodsForm } from "./Form";
export function PaymentMethodsPage() {
  return <RecordPage Form={PaymentMethodsForm} list={paymentMethodApi.list} />;
}
