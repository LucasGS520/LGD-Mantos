import { RecordPage } from "../components/RecordPage";
import { purchaseChannelApi } from "./api";
import { PurchaseChannelsForm } from "./Form";
export function PurchaseChannelsPage() {
  return (
    <RecordPage Form={PurchaseChannelsForm} list={purchaseChannelApi.list} />
  );
}
