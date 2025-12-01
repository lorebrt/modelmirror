from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final


@dataclass
class ParsedReference:
    id: str
    instance: str | None = None


@dataclass
class FormatValidation:
    is_valid: bool
    reason: str = ""


class ReferenceParser(ABC):
    __name__: str

    def __init__(self, placeholder: str):
        self.placeholder = placeholder
        self.__name__ = f"{self.__class__.__name__}:{placeholder}"

    @abstractmethod
    def _parse(self, reference: str) -> ParsedReference:
        raise NotImplementedError

    @abstractmethod
    def _validate(self, reference: str) -> FormatValidation:
        raise NotImplementedError

    @final
    def parse(self, reference: str) -> ParsedReference:
        if not isinstance(reference, str):
            raise ValueError(f"Reference must be a string. Error in reference: '{reference!r}")
        format_validation = self._validate(reference)
        if format_validation.is_valid:
            return self._parse(reference)
        raise ValueError(format_validation.reason)
