import { RecordPage } from "../components/RecordPage";
import { supplierApi } from "./api";
import { SuppliersForm } from "./Form";
export function SuppliersPage() {
  return <RecordPage Form={SuppliersForm} list={supplierApi.list} />;
}
