from .errors import ApplicationError


def check_version(row, data):
    if data.version != row.version:
        raise ApplicationError(409, "Registro alterado. Recarregue antes de corrigir")
    if not data.reason:
        raise ApplicationError(422, "Informe o motivo da correção")
