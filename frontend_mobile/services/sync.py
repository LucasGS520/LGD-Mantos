from datetime import datetime

from services.api_client import ApiError, ConnectionApiError

_COMMAND_ENDPOINTS = {
    "create_product": "/products",
    "create_sale": "/sales",
}
_MAX_ATTEMPTS = 3


class SyncService:
    def __init__(self, api, queue):
        self.api = api
        self.queue = queue

    def sync(self) -> dict:
        pending = self.queue.get_pending()
        if not pending:
            return {"processed": 0, "done": 0, "rejected": 0, "skipped": 0}

        done_count = rejected_count = skipped_count = 0

        for item in pending:
            if item["attempts"] >= _MAX_ATTEMPTS:
                skipped_count += 1
                continue

            endpoint = _COMMAND_ENDPOINTS.get(item["command_type"])
            if not endpoint:
                self.queue.mark_rejected(item["local_id"], "Tipo de comando desconhecido.")
                rejected_count += 1
                continue

            try:
                self.api.post(endpoint, item["payload"])
                self.queue.mark_done(item["local_id"])
                done_count += 1
            except ConnectionApiError:
                self.queue.increment_attempts(item["local_id"])
                skipped_count += 1
            except ApiError as exc:
                self.queue.mark_rejected(item["local_id"], str(exc))
                rejected_count += 1

        total = len(pending)
        ts = datetime.now().strftime("%H:%M:%S")
        print(
            f"[EVENT] sync_done | {total} processados, {done_count} ok, "
            f"{rejected_count} rejeitados, {skipped_count} pulados | {ts}"
        )
        return {"processed": total, "done": done_count, "rejected": rejected_count, "skipped": skipped_count}
