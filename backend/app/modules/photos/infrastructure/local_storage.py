"""Adaptador local para imagens validadas e arquivos autenticados."""

import io
import os
import warnings
from pathlib import Path

from app.shared.application.errors import ApplicationError
from PIL import Image, UnidentifiedImageError

MAX_PHOTO_BYTES = 10 * 1024 * 1024


class LocalPhotoStorage:
    def __init__(self, root=None):
        self.root = root or Path(
            os.environ.get(
                "PHOTO_ROOT",
                str(Path(__file__).resolve().parents[3] / "static" / "uploads" / "products"),
            )
        )

    def validate(self, content):
        if len(content) > MAX_PHOTO_BYTES:
            raise ApplicationError(413, "Foto deve ter no máximo 10 MB")
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(content)) as image:
                    fmt = image.format
                    image.verify()
            if fmt not in ("JPEG", "PNG", "WEBP"):
                raise ValueError()
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ):
            raise ApplicationError(422, "Envie uma foto JPEG, PNG ou WebP válida")
        return fmt

    def path(self, filename):
        return self.root / filename

    def exists(self, filename):
        return self.path(filename).is_file()

    def write(self, filename, content):
        self.root.mkdir(parents=True, exist_ok=True)
        self.path(filename).write_bytes(content)

    def remove(self, filename):
        self.path(filename).unlink(missing_ok=True)


storage = LocalPhotoStorage()
