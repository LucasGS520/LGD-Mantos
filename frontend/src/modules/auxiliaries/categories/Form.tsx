import { RecordForm } from "../components/RecordForm";
import { categoryApi } from "./api";
import type { CategoriesRecord } from "./contracts";
export function CategoriesForm(props: {
  editing: CategoriesRecord | null;
  onSaved: () => void;
}) {
  return <RecordForm {...props} save={categoryApi.save} />;
}
