import { RecordForm } from "../components/RecordForm";
import { saleChannelApi } from "./api";
import type { SaleChannelsRecord } from "./contracts";
export function SaleChannelsForm(props: {
  editing: SaleChannelsRecord | null;
  onSaved: () => void;
}) {
  return <RecordForm {...props} save={saleChannelApi.save} />;
}
