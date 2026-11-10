from app.shared.application.contracts import EntityId, Input
from pydantic import Field


class PhotoIn(Input):
    position: int = Field(ge=0)
    primary: bool = False
    variant_id: EntityId | None = None
    color: str | None = None
