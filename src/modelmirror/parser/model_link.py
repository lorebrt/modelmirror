from dataclasses import dataclass


@dataclass
class ModelLink:
    id: str
    instance: str | None = None
