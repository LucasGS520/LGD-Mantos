"""O limite expira sem acumular dados de clientes ou crescer sem limite."""

from app.modules.auth.attempts import LoginAttempts


def test_failed_attempts_block_until_window_expires():
    now = [0]
    attempts = LoginAttempts(limit=2, window=60, clock=lambda: now[0])
    assert attempts.allowed()
    attempts.failed()
    attempts.failed()
    assert not attempts.allowed()
    now[0] = 60
    assert attempts.allowed()
    assert len(attempts.failures) == 0
