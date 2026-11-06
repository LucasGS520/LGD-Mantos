import { RecordPage } from "../components/RecordPage";
import { categoryApi } from "./api";
import { CategoriesForm } from "./Form";
export function CategoriesPage() {
  return <RecordPage Form={CategoriesForm} list={categoryApi.list} />;
}
