import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class ApiError(Exception):
    pass


class ApiClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1", token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def set_token(self, token: str | None) -> None:
        self.token = token

    def login(self, password: str) -> str:
        data = self.request("POST", "/auth/login", {"password": password}, auth=False)
        token = data.get("token")
        if not token:
            raise ApiError("Token nao recebido.")
        self.token = token
        return token

    def get(self, path: str, params: dict | None = None):
        if params:
            path = f"{path}?{urlencode(params)}"
        return self.request("GET", path)

    def post(self, path: str, payload: dict):
        return self.request("POST", path, payload)

    def request(self, method: str, path: str, payload: dict | None = None, auth: bool = True):
        body = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        request = Request(f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=20) as response:
                content = response.read().decode("utf-8")
                return json.loads(content) if content else {}
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                detail = payload.get("detail", str(exc))
            except Exception:
                detail = str(exc)
            raise ApiError(detail)
        except URLError:
            raise ApiError("Nao foi possivel conectar ao backend.")
        except TimeoutError:
            raise ApiError("Tempo limite ao conectar com o backend.")
