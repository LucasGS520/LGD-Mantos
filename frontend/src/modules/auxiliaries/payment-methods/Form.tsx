import { RecordForm } from "../components/RecordForm";
import { paymentMethodApi } from "./api";
import type { PaymentMethodsRecord } from "./contracts";
export function PaymentMethodsForm(props: {
  editing: PaymentMethodsRecord | null;
  onSaved: () => void;
}) {
  return <RecordForm {...props} save={paymentMethodApi.save} />;
}
