from app.shared.application.contracts import Input
from pydantic import Field


class PhotoIn(Input):
    position: int = Field(ge=0)
    primary: bool = False
    variant_id: str | None = None
    color: str | None = None
