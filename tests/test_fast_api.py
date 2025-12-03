"""
Test suite for nested inline instance creation.
"""

import os
import sys
import unittest

# Add workspace to path when running directly
if __name__ == "__main__":
    workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if workspace_path not in sys.path:
        sys.path.insert(0, workspace_path)

from modelmirror.mirror import Mirror
from tests.fixtures.fast_api_classes import AppModel


class TestFastApi(unittest.TestCase):
    """Test FastAPI-related functionality including nested inline instances and default handling."""

    def setUp(self):
        """Set up test fixtures."""
        self.mirror = Mirror("tests.fixtures")

    def test_nested_inline_instance_creation(self):
        """Test that nested inline instances are created correctly."""
        config = self.mirror.reflect("tests/configs/fast-api.json", AppModel)

        # Verify structure is created correctly
        self.assertIsNotNone(config.international)
        self.assertIsNotNone(config.international.language)
        self.assertEqual(len(config.dataSourcesParams), 1)

    def test_mutable_default_handling_across_reflections(self):
        """Test proper mutable default handling across reflections."""
        from pydantic import BaseModel, ConfigDict

        from tests.fixtures.test_classes_extended import FastAPILikeService

        class FastAPIConfig(BaseModel):
            model_config = ConfigDict(arbitrary_types_allowed=True)
            fastapi_service: FastAPILikeService

        # First reflection
        config1 = self.mirror.reflect("tests/configs/test_config1.json", FastAPIConfig)
        service1 = config1.fastapi_service

        # Modify the service's mutable defaults
        service1.add_dependency("first_dependency")
        service1.add_middleware("auth", "jwt_config")
        service1.add_route("/api/v1", "handler1")

        # Second reflection with same singleton name
        config2 = self.mirror.reflect("tests/configs/test_config2.json", FastAPIConfig)
        service2 = config2.fastapi_service

        # Check if the defaults were corrupted
        if service1 is service2:  # Same singleton instance
            self.assertEqual(service1.dependencies, service2.dependencies, "Same singleton should have same state")
        else:  # Different instances - should have clean defaults
            self.assertEqual(service2.dependencies, [], "New instance should have clean default dependencies")


if __name__ == "__main__":
    unittest.main(verbosity=2)
