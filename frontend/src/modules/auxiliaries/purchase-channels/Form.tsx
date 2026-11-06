import { RecordForm } from "../components/RecordForm";
import { purchaseChannelApi } from "./api";
import type { PurchaseChannelsRecord } from "./contracts";
export function PurchaseChannelsForm(props: {
  editing: PurchaseChannelsRecord | null;
  onSaved: () => void;
}) {
  return <RecordForm {...props} save={purchaseChannelApi.save} />;
}
