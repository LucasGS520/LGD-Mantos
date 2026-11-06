from app.shared.application.contracts import Input, Name


class AuxiliaryFields(Input):
    name: Name
    notes: str | None = None
    active: bool = True
    version: int | None = None
    reason: Name | None = None
