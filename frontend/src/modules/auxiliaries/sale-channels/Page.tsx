import { RecordPage } from "../components/RecordPage";
import { saleChannelApi } from "./api";
import { SaleChannelsForm } from "./Form";
export function SaleChannelsPage() {
  return <RecordPage Form={SaleChannelsForm} list={saleChannelApi.list} />;
}
