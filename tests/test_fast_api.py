"""
Test suite for class isolation and proper scanning behavior.
"""

import unittest

from modelmirror.mirror import Mirror
from tests.fixtures.fast_api_classes import AppModel

# # Add workspace to path when running directly
# if __name__ == "__main__":
#     workspace_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     if workspace_path not in sys.path:
#         sys.path.insert(0, workspace_path)


class TestFastApi(unittest.TestCase):
    """Test verifying proper class isolation and scanning behavior."""

    def setUp(self):
        """Set up test fixtures."""
        self.mirror = Mirror("tests.fixtures")

    def test_simple_instance_creation(self):
        config = self.mirror.reflect("tests/configs/fast-api.json", AppModel)
        print(config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
