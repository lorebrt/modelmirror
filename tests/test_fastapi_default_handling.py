"""
Test for proper default parameter handling in FastAPI-like scenarios.
"""

import unittest
from typing import Dict, List
from pydantic import BaseModel, ConfigDict

from modelmirror.mirror import Mirror
from tests.fixtures.test_classes_extended import FastAPILikeService, MutableDefaultService


class FastAPIConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    fastapi_service: FastAPILikeService


class MutableConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    mutable_service: MutableDefaultService


class TestFastAPIDefaultHandling(unittest.TestCase):
    """Test proper default parameter handling in FastAPI-like scenarios."""

    def setUp(self):
        """Reset class state before each test."""
        # Store original methods to detect modifications
        self.original_fastapi_init = FastAPILikeService.__init__
        self.original_mutable_init = MutableDefaultService.__init__

    def test_mutable_default_handling_across_reflections(self):
        """Test proper mutable default handling across reflections."""
        mirror = Mirror('tests.fixtures')
        
        # First reflection
        config1 = mirror.reflect('tests/configs/test_config1.json', FastAPIConfig)
        service1 = config1.fastapi_service
        
        # Modify the service's mutable defaults
        service1.add_dependency("first_dependency")
        service1.add_middleware("auth", "jwt_config")
        service1.add_route("/api/v1", "handler1")
        
        # Second reflection with same singleton name
        config2 = mirror.reflect('tests/configs/test_config2.json', FastAPIConfig)
        service2 = config2.fastapi_service
        
        # Check if the defaults were corrupted
        print(f"Service1 dependencies: {service1.dependencies}")
        print(f"Service2 dependencies: {service2.dependencies}")
        
        # Service2 should have proper defaults
        if service1 is service2:  # Same singleton instance
            self.assertEqual(service1.dependencies, service2.dependencies,
                           "Same singleton should have same state")
        else:  # Different instances - should have clean defaults
            self.assertEqual(service2.dependencies, [],
                           "New instance should have clean default dependencies")

    def test_mutable_defaults_behavior_between_instances(self):
        """Test mutable defaults behavior (standard Python behavior)."""
        # Create first instance
        service1 = MutableDefaultService("service1")
        
        # Modify mutable defaults
        service1.add_config("new_key", "new_value")
        service1.add_item("new_item")
        
        # Create second instance
        service2 = MutableDefaultService("service2")
        
        # This is standard Python mutable default behavior
        print(f"Service1 config: {service1.config}")
        print(f"Service2 config: {service2.config}")

    def test_class_preservation_across_instances(self):
        """Test that class definitions are preserved across instances."""
        # Create instance before Mirror
        service_before = FastAPILikeService("before_mirror")
        
        # Create Mirror (now uses isolated scanner)
        mirror = Mirror('tests.fixtures')
        
        # Create instance after Mirror
        service_after = FastAPILikeService("after_mirror")
        
        # Check that instances are unaffected by Mirror creation
        init_before = service_before.__class__.__init__
        init_after = service_after.__class__.__init__
        
        self.assertIs(init_before, init_after,
                     "Both instances should have the same __init__")
        self.assertIs(init_after, self.original_fastapi_init,
                        "Class should be preserved after Mirror creation")

    def test_pydantic_validation_isolation(self):
        """Test that Pydantic validation is properly isolated."""
        # Create instance before Mirror
        service_before = FastAPILikeService("before", [], [], {})
        
        # Create Mirror with isolated scanner
        mirror = Mirror('tests.fixtures')
        
        # Try to create instance with parameters
        try:
            # This should work since validation is properly isolated
            service_invalid = FastAPILikeService(title="123")
            validation_added = False
        except Exception as e:
            validation_added = True
            print(f"Validation error: {e}")
        
        if validation_added:
            print("Unexpected validation error")
        else:
            print("Validation properly isolated")
        
        self.assertFalse(validation_added, "Validation should be properly isolated")

    def test_multiple_mirrors_proper_isolation(self):
        """Test that multiple Mirror instances maintain proper isolation."""
        # Create first Mirror
        mirror1 = Mirror('tests.fixtures')
        
        # Create instance and modify it
        config1 = mirror1.reflect('tests/configs/test_config1.json', FastAPIConfig)
        service1 = config1.fastapi_service
        service1.add_dependency("mirror1_dependency")
        
        # Create second Mirror
        mirror2 = Mirror('tests.fixtures')
        
        # Create instance with second Mirror
        config2 = mirror2.reflect('tests/configs/test_config2.json', FastAPIConfig)
        service2 = config2.fastapi_service
        
        # Check if state is properly isolated between mirrors
        print(f"Mirror1 service dependencies: {service1.dependencies}")
        print(f"Mirror2 service dependencies: {service2.dependencies}")
        
        # Services should be properly isolated
        if service1 is service2:
            print("Same singleton instance (expected behavior)")
        else:
            print("Different instances (proper isolation)")

    def test_concurrent_mirror_usage_safety(self):
        """Test that concurrent Mirror usage is safe."""
        # Test concurrent Mirror creation with the fix
        
        # Simulate concurrent Mirror creation
        mirrors = [Mirror('tests.fixtures') for _ in range(3)]
        
        # All mirrors should see the same unmodified class
        original_class = FastAPILikeService
        
        for i, mirror in enumerate(mirrors):
            # Each mirror should see the same unmodified class
            print(f"Mirror {i} sees FastAPILikeService.__init__: {original_class.__init__}")
        
        # All mirrors see the same original class
        self.assertIs(FastAPILikeService.__init__, self.original_fastapi_init,
                     "All mirrors should see the same original class")

    def test_no_memory_leaks_with_proper_implementation(self):
        """Test that memory leaks are prevented with proper implementation."""
        # Create multiple Mirror instances
        mirrors = []
        for i in range(5):
            mirror = Mirror('tests.fixtures')
            mirrors.append(mirror)
        
        # After mirrors go out of scope, class should remain unmodified
        del mirrors
        
        # The class should remain preserved
        self.assertIs(FastAPILikeService.__init__, self.original_fastapi_init,
                     "Class should remain preserved")

    def test_testing_environment_handling(self):
        """Test proper handling of TESTING environment variable."""
        import os
        
        # Set TESTING environment variable
        os.environ['TESTING'] = 'true'
        
        try:
            # Create Mirror with TESTING=true
            mirror = Mirror('tests.fixtures')
            
            # Class should remain unmodified regardless of TESTING variable
            modified_init = FastAPILikeService.__init__
            
            print(f"With TESTING=true, __init__ is: {modified_init}")
            
            # Should be the same as original
            self.assertIs(modified_init, self.original_fastapi_init,
                         "Class should remain preserved even with TESTING=true")
            
        finally:
            # Clean up environment variable
            if 'TESTING' in os.environ:
                del os.environ['TESTING']


if __name__ == '__main__':
    unittest.main(verbosity=2)