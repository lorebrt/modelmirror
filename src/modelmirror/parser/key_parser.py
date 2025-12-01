from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


@dataclass
class ParsedKey:
    id: str
    instance: str | None = None


@dataclass
class FormatValidation:
    is_valid: bool
    reason: str = ""


class KeyParser(ABC):
    __name__: str

    def __init__(self, placeholder: str):
        self.placeholder = placeholder
        self.__name__ = f"{self.__class__.__name__}:{placeholder}"

    @abstractmethod
    def _parse(self, key: str) -> ParsedKey:
        raise NotImplementedError

    @abstractmethod
    def _validate(self, key: str) -> FormatValidation:
        raise NotImplementedError

    @final
    def parse(self, key: str) -> ParsedKey:
        if not isinstance(key, str):
            raise ValueError(f"Reference must be a string. Error in reference: '{key!r}")
        format_validation = self._validate(key)
        if format_validation.is_valid:
            return self._parse(key)
        raise ValueError(format_validation.reason)
