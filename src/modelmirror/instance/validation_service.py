import inspect
from typing import Any

from pydantic import validate_call


class ValidationService:
    def validate_or_raise(self, cls: type, params: dict[str, Any]) -> None:
        isolated_class = self.__create_isolated_class(cls)
        isolated_class(**params)

    def __create_isolated_class(self, cls: type):
        class_name = f"Isolated{cls.__name__}"

        class Isolated:
            pass

        Isolated.__name__ = class_name
        Isolated.__qualname__ = class_name

        self.__set_attributes(cls, Isolated)
        cls_sig = inspect.signature(cls)
        init_sig = self.__build_init_signature(cls_sig)
        raw_init = self.__build_side_effect_free_init(init_sig)
        annotations = self._build_annotations(cls_sig)
        raw_init.__annotations__ = annotations

        init_sig = inspect.signature(raw_init)

        try:
            validated_init = validate_call(config={"arbitrary_types_allowed": True, "extra": "forbid"})(raw_init)
            setattr(Isolated, "__init__", validated_init)
        except Exception:
            setattr(Isolated, "__init__", raw_init)

        return Isolated

    def __set_attributes(self, cls: type, isolated_cls: type) -> None:
        """Copy only public, non-callable class attributes from cls to isolated_cls."""
        for name, value in cls.__dict__.items():
            # Skip dunder attributes
            if name.startswith("__") and name.endswith("__"):
                continue

            # Skip anything "non-public" (starts with underscore)
            if name.startswith("_"):
                continue

            # Skip methods / callables
            if callable(value):
                continue

            setattr(isolated_cls, name, value)

    def __build_init_signature(self, cls_sig: inspect.Signature) -> inspect.Signature:
        """Build an __init__(self, *cls_params...) signature from the class signature."""
        params = [inspect.Parameter("self", inspect.Parameter.POSITIONAL_OR_KEYWORD)]
        params.extend(cls_sig.parameters.values())
        return inspect.Signature(params)

    def __build_side_effect_free_init(self, init_sig: inspect.Signature):
        """Create the raw __init__ function that just assigns attributes."""

        def raw_init(*args, **kwargs):
            bound = init_sig.bind(*args, **kwargs)
            bound.apply_defaults()

            self = bound.arguments.pop("self")

            for name, value in bound.arguments.items():
                setattr(self, name, value)

        raw_init.__name__ = "__init__"
        raw_init.__qualname__ = "__init__"
        setattr(raw_init, "__signature__", init_sig)

        return raw_init

    def _build_annotations(self, cls_sig: inspect.Signature) -> dict[str, Any]:
        """Build annotations dict for raw_init from the original class signature."""
        annotations: dict[str, Any] = {}
        annotations["self"] = Any

        for name, param in cls_sig.parameters.items():
            if param.annotation is inspect._empty:
                annotations[name] = Any
            else:
                annotations[name] = param.annotation

        annotations["return"] = None
        return annotations
