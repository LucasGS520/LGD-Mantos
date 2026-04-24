"""Reexporta os modelos centrais para evitar importações acopladas ao app legado."""

from app.models import *  # noqa: F401,F403
