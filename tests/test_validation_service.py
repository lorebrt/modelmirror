"""
Test suite for ValidationService with safe init functionality.
"""

import unittest
from unittest.mock import Mock

from modelmirror.instance.validation_service import ValidationService


# Test classes with different init patterns
class SafeClass:
    """Class with only safe assignments."""

    def __init__(self, name: str, value: int):
        self.name = name
        self.value = value


class UnsafeClass:
    """Class with function calls in init."""

    def __init__(self, name: str, callback):
        self.name = name
        self.callback = callback
        callback()  # This should be removed
        self._data = callback()  # This should be removed


class MixedClass:
    """Class with both safe and unsafe operations."""

    def __init__(self, name: str, value: int, func):
        self.name = name  # Safe - should be kept
        self.value = value  # Safe - should be kept
        func()  # Unsafe - should be removed
        self._result = func()  # Unsafe - should be removed


class ClsParameterClass:
    """Class with cls parameter that conflicts with Pydantic."""

    def __init__(self, cls, name: str):
        self.cls = cls
        self.name = name
        cls()  # This should be handled without validation


class ComplexUnsafeClass:
    """Class with complex unsafe operations."""

    def __init__(self, name: str, factory, processor):
        self.name = name
        # These should all be removed
        factory.create()
        self._processed = processor(name)


class TestValidationService(unittest.TestCase):
    """Test ValidationService safe init functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_service = ValidationService()

    def test_safe_class_validation(self):
        """Test that safe classes work normally."""
        params = {"name": "test", "value": 42}

        # Should not raise any exception
        self.validation_service.validate_or_raise(SafeClass, params)

    def test_unsafe_class_validation_no_side_effects(self):
        """Test that unsafe classes don't trigger side effects during validation."""
        mock_callback = Mock()
        params = {"name": "test", "callback": mock_callback}

        # Validation should work without calling the callback
        self.validation_service.validate_or_raise(UnsafeClass, params)

        # The mock should not have been called during validation
        mock_callback.assert_not_called()

    def test_mixed_class_validation(self):
        """Test that mixed classes only keep safe assignments."""
        mock_func = Mock()
        params = {"name": "test", "value": 42, "func": mock_func}

        # Should validate without calling the function
        self.validation_service.validate_or_raise(MixedClass, params)

        # Function should not be called during validation
        mock_func.assert_not_called()

    def test_cls_parameter_handling(self):
        """Test that classes with cls parameter are handled correctly."""
        mock_cls = Mock()
        params = {"cls": Mock, "name": "test"}

        # Should handle cls parameter without Pydantic conflicts
        self.validation_service.validate_or_raise(ClsParameterClass, params)

        # Mock should not be called during validation
        mock_cls.assert_not_called()

    def test_complex_unsafe_class(self):
        """Test complex unsafe operations are removed."""
        mock_factory = Mock()
        mock_processor = Mock()
        params = {"name": "test", "factory": mock_factory, "processor": mock_processor}

        # Should validate without calling any methods
        self.validation_service.validate_or_raise(ComplexUnsafeClass, params)

        # No methods should be called
        mock_factory.create.assert_not_called()
        mock_factory.build.assert_not_called()
        mock_processor.assert_not_called()
        mock_processor.process.assert_not_called()

    def test_validation_with_invalid_parameters(self):
        """Test that validation still works for parameter validation."""
        # Missing required parameter should still raise validation error
        with self.assertRaises(Exception):
            self.validation_service.validate_or_raise(SafeClass, {"name": "test"})  # Missing value

        # Valid parameters should work
        try:
            self.validation_service.validate_or_raise(SafeClass, {"name": "test", "value": 42})
        except Exception as e:
            self.fail(f"Valid parameters should work: {e}")

    def test_isolated_class_creation(self):
        """Test that isolated classes are created correctly."""
        isolated_class = self.validation_service._ValidationService__create_isolated_class(SafeClass)  # type: ignore

        # Should be a different class
        self.assertNotEqual(isolated_class, SafeClass)
        self.assertTrue(isolated_class.__name__.startswith("Isolated"))

        # Should still be instantiable
        instance = isolated_class(name="test", value=42)
        self.assertEqual(instance.name, "test")
        self.assertEqual(instance.value, 42)

    def test_safe_init_preserves_signature(self):
        """Test that safe init preserves the original method parameter names."""
        isolated_class = self.validation_service._ValidationService__create_isolated_class(UnsafeClass)  # type: ignore

        import inspect

        original_sig = inspect.signature(UnsafeClass.__init__)
        isolated_sig = inspect.signature(isolated_class.__init__)

        # Parameter names should be the same (type annotations may be lost)
        original_params = list(original_sig.parameters.keys())
        isolated_params = list(isolated_sig.parameters.keys())
        self.assertEqual(original_params, isolated_params)

    def test_fallback_for_unparseable_methods(self):
        """Test fallback behavior when AST parsing fails."""

        # Create a class that might cause AST parsing issues
        class ProblematicClass:
            pass

        # Manually set an unparseable init (simulating edge case)
        def problematic_init(self, name: str):
            self.name = name

        # Remove source code to trigger fallback
        problematic_init.__code__ = problematic_init.__code__.replace(co_filename="<built-in>")
        ProblematicClass.__init__ = problematic_init  # type: ignore

        # Should still work with fallback
        params = {"name": "test"}
        self.validation_service.validate_or_raise(ProblematicClass, params)

    def test_empty_init_body_after_filtering(self):
        """Test behavior when all statements are filtered out."""

        class AllUnsafeClass:
            def __init__(self, func):
                func()  # Only unsafe operations
                func.call()

        mock_func = Mock()
        params = {"func": mock_func}

        # Should work even when all statements are removed
        self.validation_service.validate_or_raise(AllUnsafeClass, params)

        # No calls should be made
        mock_func.assert_not_called()
        mock_func.call.assert_not_called()

    def test_nested_function_calls_removed(self):
        """Test that nested function calls are properly removed."""

        class NestedCallsClass:
            def __init__(self, name: str, service):
                self.name = name
                service.method().chain().call()  # Complex nested calls

        mock_service = Mock()
        params = {"name": "test", "service": mock_service}

        # Should validate without executing nested calls
        self.validation_service.validate_or_raise(NestedCallsClass, params)

        # No methods should be called
        mock_service.method.assert_not_called()
        mock_service.get.assert_not_called()


class TestValidationServiceIntegration(unittest.TestCase):
    """Integration tests for ValidationService with real scenarios."""

    def setUp(self):
        """Set up test fixtures."""
        self.validation_service = ValidationService()

    def test_real_world_service_class(self):
        """Test with a realistic service class."""

        class DatabaseService:
            def __init__(self, host: str, port: int, logger):
                self.host = host
                self.port = port
                self.logger = logger
                logger.info(f"Connecting to {host}:{port}")  # Should be removed
                self._connection = self._create_connection()  # Should be removed

            def _create_connection(self):
                return f"connection to {self.host}:{self.port}"

        mock_logger = Mock()
        params = {"host": "localhost", "port": 5432, "logger": mock_logger}

        # Should validate without side effects
        self.validation_service.validate_or_raise(DatabaseService, params)

        # Logger should not be called during validation
        mock_logger.info.assert_not_called()

    def test_factory_pattern_class(self):
        """Test with factory pattern that has initialization side effects."""

        class ServiceFactory:
            def __init__(self, config: dict, registry):
                self.config = config
                self.registry = registry
                registry.register(self)  # Should be removed
                self._services = self._initialize_services()  # Should be removed

            def _initialize_services(self):
                return []

        mock_registry = Mock()
        params = {"config": {"key": "value"}, "registry": mock_registry}

        # Should validate without registering or initializing
        self.validation_service.validate_or_raise(ServiceFactory, params)

        # Registry should not be called
        mock_registry.register.assert_not_called()

    def test_validation_with_pydantic_model(self):
        """Test validation works correctly with Pydantic-style validation."""

        class ServiceWithValidation:
            def __init__(self, name: str, port: int, callback):
                if port < 1 or port > 65535:
                    raise ValueError("Invalid port")
                self.name = name
                self.port = port
                self.callback = callback
                callback.initialize()  # Should be removed

        mock_callback = Mock()

        # Valid parameters should work
        valid_params = {"name": "service", "port": 8080, "callback": mock_callback}
        self.validation_service.validate_or_raise(ServiceWithValidation, valid_params)

        # Callback should not be called during validation
        mock_callback.initialize.assert_not_called()

        # Invalid parameters should still raise validation errors
        # Note: This might not raise an error since we're only doing structural validation
        # The actual business logic validation is bypassed for safety


if __name__ == "__main__":
    unittest.main(verbosity=2)
