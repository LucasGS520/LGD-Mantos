import { RecordForm } from "../components/RecordForm";
import { supplierApi } from "./api";
import type { SuppliersRecord } from "./contracts";
export function SuppliersForm(props: {
  editing: SuppliersRecord | null;
  onSaved: () => void;
}) {
  return <RecordForm {...props} save={supplierApi.save} />;
}
