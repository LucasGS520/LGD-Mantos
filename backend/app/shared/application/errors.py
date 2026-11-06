"""Erros traduzidos para HTTP na borda."""


class ApplicationError(Exception):
    def __init__(self, status_code: int, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(str(detail))
