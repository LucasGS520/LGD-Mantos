"""Limite local e finito para o único acesso do dono; sem armazenar IP/senha."""

from collections import deque
from time import monotonic


class LoginAttempts:
    def __init__(self, limit=10, window=60, clock=monotonic):
        self.limit, self.window, self.clock = limit, window, clock
        self.failures = deque(maxlen=limit)

    def allowed(self):
        now = self.clock()
        while self.failures and self.failures[0] <= now - self.window:
            self.failures.popleft()
        return len(self.failures) < self.limit

    def failed(self):
        self.failures.append(self.clock())
