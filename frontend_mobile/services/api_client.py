import json
import mimetypes
import os
import uuid
from datetime import datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiError(Exception):
    pass


class ConnectionApiError(ApiError):
    """Raised when the network is unreachable (no HTTP response received)."""
    pass


class ApiClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1", token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.on_unauthorized = None  # callback: () -> None

    def set_token(self, token: str | None) -> None:
        self.token = token

    def _log(self, event: str, result: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[EVENT] {event} | {result} | {ts}")

    def login(self, password: str) -> str:
        try:
            data = self.request("POST", "/auth/login", {"password": password}, auth=False)
            token = data.get("token")
            if not token:
                raise ApiError("Token nao recebido.")
            self.token = token
            self._log("login_success", "ok")
            return token
        except ApiError as exc:
            self._log("login_fail", str(exc))
            raise

    def get(self, path: str, params: dict | None = None):
        if params:
            path = f"{path}?{urlencode(params)}"
        return self.request("GET", path)

    def post(self, path: str, payload: dict):
        return self.request("POST", path, payload)

    def put(self, path: str, payload: dict):
        return self.request("PUT", path, payload)

    def delete(self, path: str):
        return self.request("DELETE", path)

    def upload(self, path: str, file_path: str, field: str = "file"):
        boundary = uuid.uuid4().hex
        filename = os.path.basename(file_path)
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as f:
            file_data = f.read()
        body = (
            f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
            f"Content-Type: {mime_type}\r\n\r\n"
        ).encode("utf-8") + file_data + f"\r\n--{boundary}--\r\n".encode("utf-8")
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        req = Request(f"{self.base_url}{path}", data=body, headers=headers, method="POST")
        try:
            with urlopen(req, timeout=30) as response:
                content = response.read().decode("utf-8")
                self._log("upload_done", f"ok | {filename}")
                return json.loads(content) if content else {}
        except HTTPError as exc:
            self._log("api_error", f"{exc.code} | {path}")
            if exc.code == 401:
                if self.on_unauthorized:
                    self.on_unauthorized()
                raise ApiError("Sessao expirada. Faca login novamente.")
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", str(exc))
            except Exception:
                detail = str(exc)
            raise ApiError(detail)
        except (URLError, TimeoutError):
            self._log("api_error", f"connection | {path}")
            raise ConnectionApiError("Sem conexao com o servidor.")

    def request(self, method: str, path: str, payload: dict | None = None, auth: bool = True):
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        req = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(req, timeout=20) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else {}
        except HTTPError as exc:
            self._log("api_error", f"{exc.code} | {path}")
            if exc.code == 401:
                if self.on_unauthorized:
                    self.on_unauthorized()
                raise ApiError("Sessao expirada. Faca login novamente.")
            try:
                detail = json.loads(exc.read().decode("utf-8")).get("detail", str(exc))
            except Exception:
                detail = str(exc)
            raise ApiError(detail)
        except URLError:
            self._log("api_error", f"connection | {path}")
            raise ConnectionApiError("Sem conexao com o servidor.")
        except TimeoutError:
            self._log("api_error", f"timeout | {path}")
            raise ConnectionApiError("Sem conexao com o servidor.")
