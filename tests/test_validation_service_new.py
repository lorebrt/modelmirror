"""
Test suite for ValidationService with safe class creation.
"""

import unittest
from dataclasses import dataclass, field
from typing import List
from unittest.mock import Mock

from pydantic import BaseModel, ConfigDict

from modelmirror.instance.validation_service import ValidationService


# Test classes with different patterns
class RegularClass:
    """Regular class with side effects in init."""

    class_var: int = 42

    def __init__(self, name: str, callback):
        self.name = name
        self.callback = callback
        callback()  # Side effect - should be removed
        self._data = callback.get_data()  # Side effect - should be removed


class ClassWithClassVars:
    """Class with class variables."""

    default_timeout: int = 30
    max_retries: int = 3

    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port


@dataclass
class DataclassWithPostInit:
    """Dataclass with __post_init__ side effects."""

    name: str
    values: List[str] = field(default_factory=list)

    def __post_init__(self):
        # This should not be called during validation
        self.values.append("processed")
        self._computed = len(self.values)


class PydanticModel(BaseModel):
    """Pydantic model with validation."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    port: int

    def model_post_init(self, __context):
        # This should not be called during validation
        self.computed_value = f"{self.name}:{self.port}"


class ClassWithClsParameter:
    """Class with cls parameter."""

    def __init__(self, cls, name: str):
        self.cls = cls
        self.name = name
        cls.static_method()  # Side effect - should be removed


class ComplexClass:
    """Class with complex initialization logic."""

    version: str = "1.0"

    def __init__(self, config: dict, factory, logger):
        self.config = config
        self.factory = factory
        self.logger = logger

        # All these should be removed
        logger.info("Initializing service")
        self._service = factory.create_service()
        self._connection = self._establish_connection()
        factory.register(self)

    def _establish_connection(self):
        return "connection"


class TestValidationService(unittest.TestCase):
    """Test ValidationService safe class creation."""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_service = ValidationService()

    def test_regular_class_no_side_effects(self):
        """Test that regular classes don't trigger side effects during validation."""
        mock_callback = Mock()
        params = {"name": "test", "callback": mock_callback}

        # Should validate without calling callback methods
        self.validation_service.validate_or_raise(RegularClass, params)

        # No methods should be called
        mock_callback.assert_not_called()
        mock_callback.process.assert_not_called()
        mock_callback.get_data.assert_not_called()

    def test_class_variables_preserved(self):
        """Test that class variables are preserved in isolated class."""
        params = {"name": "test", "port": 8080}

        # Should work and preserve class variables
        self.validation_service.validate_or_raise(ClassWithClassVars, params)

        # Create isolated class to check class variables
        isolated_class = self.validation_service._ValidationService__create_isolated_class(ClassWithClassVars)  # type: ignore

        # Class variables should be preserved
        self.assertEqual(isolated_class.default_timeout, 30)
        self.assertEqual(isolated_class.max_retries, 3)

    def test_dataclass_no_post_init(self):
        """Test that dataclass __post_init__ is not called during validation."""
        params = {"name": "test", "values": ["initial"]}

        # Should validate without calling __post_init__
        self.validation_service.validate_or_raise(DataclassWithPostInit, params)

        # Create instance to verify __post_init__ wasn't called
        isolated_class = self.validation_service._ValidationService__create_isolated_class(DataclassWithPostInit)  # type: ignore
        instance = isolated_class(name="test", values=["initial"])

        # Should only have assigned parameters, no post-init processing
        self.assertEqual(instance.name, "test")
        self.assertEqual(instance.values, ["initial"])
        # Should not have computed attributes from __post_init__
        self.assertFalse(hasattr(instance, "_computed"))

    def test_pydantic_model_no_post_init(self):
        """Test that Pydantic model_post_init is not called during validation."""
        params = {"name": "service", "port": 8080}

        # Should validate without calling model_post_init
        self.validation_service.validate_or_raise(PydanticModel, params)

        # Create instance to verify model_post_init wasn't called
        isolated_class = self.validation_service._ValidationService__create_isolated_class(PydanticModel)  # type: ignore
        instance = isolated_class(name="service", port=8080)

        # Should only have assigned parameters
        self.assertEqual(instance.name, "service")
        self.assertEqual(instance.port, 8080)
        # Should not have computed attributes from model_post_init
        self.assertFalse(hasattr(instance, "computed_value"))

    def test_cls_parameter_handling(self):
        """Test that classes with cls parameter are handled without Pydantic validation."""
        mock_cls = Mock()
        params = {"cls": mock_cls, "name": "test"}

        # Should handle without Pydantic conflicts
        self.validation_service.validate_or_raise(ClassWithClsParameter, params)

        # Static method should not be called
        mock_cls.static_method.assert_not_called()

    def test_complex_class_side_effects_removed(self):
        """Test that complex initialization side effects are removed."""
        mock_factory = Mock()
        mock_logger = Mock()
        params = {"config": {"key": "value"}, "factory": mock_factory, "logger": mock_logger}

        # Should validate without side effects
        self.validation_service.validate_or_raise(ComplexClass, params)

        # No side effect methods should be called
        mock_logger.info.assert_not_called()
        mock_factory.create_service.assert_not_called()
        mock_factory.register.assert_not_called()

    def test_isolated_class_is_completely_new(self):
        """Test that isolated class is completely new, not inheriting from original."""
        isolated_class = self.validation_service._ValidationService__create_isolated_class(RegularClass)  # type: ignore

        # Should be a different class
        self.assertNotEqual(isolated_class, RegularClass)
        self.assertTrue(isolated_class.__name__.startswith("Isolated"))

        # Should not inherit from original class
        self.assertFalse(issubclass(isolated_class, RegularClass))

        # Should have class variables but no methods
        self.assertEqual(isolated_class.class_var, 42)
        self.assertFalse(hasattr(isolated_class, "_establish_connection"))

    def test_no_methods_copied(self):
        """Test that no methods are copied to isolated class."""
        isolated_class = self.validation_service._ValidationService__create_isolated_class(ComplexClass)  # type: ignore

        # Should have class variables
        self.assertEqual(isolated_class.version, "1.0")

        # Should not have any methods except __init__
        methods = [
            name for name, value in isolated_class.__dict__.items() if callable(value) and not name.startswith("__")
        ]
        self.assertEqual(len(methods), 0)

    def test_init_signature_preserved(self):
        """Test that __init__ signature is preserved."""
        isolated_class = self.validation_service._ValidationService__create_isolated_class(ComplexClass)  # type: ignore

        import inspect

        original_sig = inspect.signature(ComplexClass.__init__)
        isolated_sig = inspect.signature(isolated_class.__init__)

        # Parameter names should be the same
        original_params = list(original_sig.parameters.keys())
        isolated_params = list(isolated_sig.parameters.keys())
        self.assertEqual(original_params, isolated_params)

    def test_validation_still_works(self):
        """Test that parameter validation still works."""
        # Missing required parameter should fail
        with self.assertRaises(Exception):
            self.validation_service.validate_or_raise(RegularClass, {"name": "test"})  # Missing callback

        # Valid parameters should work
        mock_callback = Mock()
        params = {"name": "test", "callback": mock_callback}
        self.validation_service.validate_or_raise(RegularClass, params)

    def test_empty_init_class(self):
        """Test class with no __init__ method."""

        class NoInitClass:
            class_var = "test"

        params = {}
        # Should work even without __init__
        self.validation_service.validate_or_raise(NoInitClass, params)

        isolated_class = self.validation_service._ValidationService__create_isolated_class(NoInitClass)  # type: ignore
        self.assertEqual(isolated_class.class_var, "test")

    def test_class_with_only_private_vars(self):
        """Test class with only private variables."""

        class PrivateVarsClass:
            _private_var = "private"
            __very_private = "very_private"
            public_var = "public"

            def __init__(self, name: str):
                self.name = name

        params = {"name": "test"}
        self.validation_service.validate_or_raise(PrivateVarsClass, params)

        isolated_class = self.validation_service._ValidationService__create_isolated_class(PrivateVarsClass)  # type: ignore
        # Should only have public class variables
        self.assertEqual(isolated_class.public_var, "public")
        self.assertFalse(hasattr(isolated_class, "_private_var"))
        self.assertFalse(hasattr(isolated_class, "__very_private"))


class TestValidationServiceIntegration(unittest.TestCase):
    """Integration tests for ValidationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_service = ValidationService()

    def test_real_world_service_pattern(self):
        """Test with realistic service class pattern."""

        class DatabaseService:
            connection_timeout: int = 30

            def __init__(self, host: str, port: int, logger):
                self.host = host
                self.port = port
                self.logger = logger
                logger.info(f"Connecting to {host}:{port}")  # Should be removed
                self._pool = self._create_connection_pool()  # Should be removed

            def _create_connection_pool(self):
                return "pool"

        mock_logger = Mock()
        params = {"host": "localhost", "port": 5432, "logger": mock_logger}

        # Should validate without side effects
        self.validation_service.validate_or_raise(DatabaseService, params)

        # Logger should not be called
        mock_logger.info.assert_not_called()

    def test_factory_pattern_with_registration(self):
        """Test factory pattern that registers itself."""

        class ServiceFactory:
            registry_enabled: bool = True

            def __init__(self, config: dict, registry):
                self.config = config
                self.registry = registry
                registry.register(self)  # Should be removed
                self._initialize()  # Should be removed

            def _initialize(self):
                pass

        mock_registry = Mock()
        params = {"config": {"type": "factory"}, "registry": mock_registry}

        # Should validate without registration
        self.validation_service.validate_or_raise(ServiceFactory, params)

        # Registry should not be called
        mock_registry.register.assert_not_called()

    def test_mixed_dataclass_and_regular_class(self):
        """Test validation works with mixed class types."""

        @dataclass
        class DataConfig:
            name: str
            enabled: bool = True

            def __post_init__(self):
                self.computed = f"{self.name}_computed"

        class RegularService:
            def __init__(self, config: DataConfig, processor):
                self.config = config
                self.processor = processor
                processor.initialize(config)  # Should be removed

        mock_processor = Mock()
        data_config = DataConfig(name="test", enabled=True)
        params = {"config": data_config, "processor": mock_processor}

        # Should validate without calling processor
        self.validation_service.validate_or_raise(RegularService, params)

        # Processor should not be called
        mock_processor.initialize.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
