"""
Test suite for class isolation and proper scanning behavior.
"""

import unittest
import inspect
from modelmirror.mirror import Mirror
from modelmirror.class_provider.class_scanner import ClassScanner
from tests.fixtures.test_classes import SimpleService


class TestClassIsolation(unittest.TestCase):
    """Test verifying proper class isolation and scanning behavior."""

    def setUp(self):
        """Store original class state."""
        self.original_init = SimpleService.__init__
        self.original_signature = str(inspect.signature(self.original_init))

    def test_class_scanner_preserves_original_classes(self):
        """Test that ClassScanner preserves original class definitions."""
        print(f"\nOriginal SimpleService.__init__: {self.original_init}")
        print(f"Original signature: {self.original_signature}")
        print(f"Has __wrapped__: {hasattr(self.original_init, '__wrapped__')}")
        
        # Create ClassScanner and scan
        scanner = ClassScanner('tests.fixtures')
        registered_classes = scanner.scan()
        
        # Check if class was modified
        modified_init = SimpleService.__init__
        modified_signature = str(inspect.signature(modified_init))
        
        print(f"\nAfter scanning SimpleService.__init__: {modified_init}")
        print(f"After scanning signature: {modified_signature}")
        print(f"Has __wrapped__: {hasattr(modified_init, '__wrapped__')}")
        
        # Classes should NOT be modified globally
        is_modified = (self.original_init is not modified_init) or hasattr(modified_init, '__wrapped__')
        
        if is_modified:
            print("✗ Class was modified unexpectedly")
        else:
            print("✓ Class was preserved correctly")
        
        self.assertFalse(is_modified, "ClassScanner should preserve original classes")

    def test_multiple_scanners_see_same_original_class(self):
        """Test that multiple scanners see the same original class."""
        # First scanner
        scanner1 = ClassScanner('tests.fixtures')
        scanner1.scan()
        init_after_scanner1 = SimpleService.__init__
        
        # Second scanner
        scanner2 = ClassScanner('tests.fixtures')
        scanner2.scan()
        init_after_scanner2 = SimpleService.__init__
        
        print(f"\nAfter scanner1: {init_after_scanner1}")
        print(f"After scanner2: {init_after_scanner2}")
        print(f"Same object: {init_after_scanner1 is init_after_scanner2}")
        
        # Scanners should see the same unmodified class
        self.assertIs(init_after_scanner1, init_after_scanner2,
                     "Multiple scanners should see the same original class")

    def test_mirror_instances_share_original_classes(self):
        """Test that multiple Mirror instances share original classes."""
        # Create first Mirror
        mirror1 = Mirror('tests.fixtures')
        init_after_mirror1 = SimpleService.__init__
        
        # Create second Mirror
        mirror2 = Mirror('tests.fixtures')
        init_after_mirror2 = SimpleService.__init__
        
        print(f"\nAfter mirror1: {init_after_mirror1}")
        print(f"After mirror2: {init_after_mirror2}")
        print(f"Same object: {init_after_mirror1 is init_after_mirror2}")
        
        # Mirrors should see the same unmodified class
        self.assertIs(init_after_mirror1, init_after_mirror2,
                     "Multiple Mirror instances should see the same original class")

    def test_pydantic_validation_isolation(self):
        """Test that Pydantic validation is properly isolated."""
        # Create Mirror with isolated scanner
        mirror = Mirror('tests.fixtures')
        
        # Try to create instance with parameters
        validation_error_occurred = False
        try:
            # This should work since validation is properly isolated
            service = SimpleService(name="123")
        except Exception as e:
            validation_error_occurred = True
            print(f"\nValidation error occurred: {e}")
        
        if validation_error_occurred:
            print("✗ Unexpected validation error")
        else:
            print("✓ Validation properly isolated")
        
        # Validation should be properly isolated
        self.assertFalse(validation_error_occurred, "Validation should be properly isolated")

    def test_class_preservation_across_instances(self):
        """Test that class definitions are preserved across instance creation."""
        # Create instance before Mirror
        service_before = SimpleService("before_mirror")
        
        # Create Mirror with isolated scanner
        mirror = Mirror('tests.fixtures')
        
        # Create instance after Mirror
        service_after = SimpleService("after_mirror")
        
        # Both instances should have the same class
        self.assertIs(service_before.__class__, service_after.__class__,
                     "Both instances should have the same class")
        
        # The class should be preserved
        current_init = SimpleService.__init__
        is_modified = (self.original_init is not current_init) or hasattr(current_init, '__wrapped__')
        
        print(f"\nOriginal init: {self.original_init}")
        print(f"Current init: {current_init}")
        print(f"Class was modified: {is_modified}")
        
        if not is_modified:
            print("✓ Class properly preserved")
        else:
            print("✗ Class was unexpectedly modified")
        
        self.assertFalse(is_modified, "Class should be preserved")

    def test_cleanup_mechanism_available(self):
        """Test that automatic cleanup mechanism works correctly."""
        # Store original state
        original_init = SimpleService.__init__
        
        # Create Mirror with isolated scanner
        mirror = Mirror('tests.fixtures')
        
        # Class should be preserved
        modified_init = SimpleService.__init__
        is_modified = original_init is not modified_init
        
        # Check for private reset method (automatic cleanup)
        has_private_reset = hasattr(mirror, '_Mirror__reset_state')
        
        print(f"\nClass was modified: {is_modified}")
        print(f"Private reset method available: {has_private_reset}")
        
        if not is_modified and has_private_reset:
            print("✓ Proper isolation and automatic cleanup available")
        else:
            print("✗ Issues with isolation or cleanup")
        
        self.assertFalse(is_modified, "Class should be preserved")
        self.assertTrue(has_private_reset, "Automatic cleanup mechanism should be available")


if __name__ == '__main__':
    unittest.main(verbosity=2)