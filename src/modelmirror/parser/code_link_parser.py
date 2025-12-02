from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass
class ParsedKey:
    id: str
    params: dict[str, Any]
    instance: str | None = None


class CodeLinkParser(ABC):
    __name__: str

    def __init__(self, placeholder: str):
        self.placeholder = placeholder
        self.__name__ = f"{self.__class__.__name__}:{placeholder}"

    def has_code_link(self, node: dict[str, Any]) -> bool:
        if self.placeholder in node:
            if isinstance(node[self.placeholder], str):
                return True
            raise ValueError(f"Value of '{self.placeholder}' must be a string")
        return False

    def parse(self, node: dict[str, Any]) -> ParsedKey:
        raw_reference: str = node.pop(self.placeholder)
        params: dict[str, Any] = {name: prop for name, prop in node.items()}
        if ":" in raw_reference:
            id, instance = raw_reference.split(":", 1)
            return ParsedKey(id=id, instance=f"${instance}", params=params)
        return ParsedKey(id=raw_reference, instance=None, params=params)
