import unittest

from modelmirror.class_provider.class_reference import ClassReference
from modelmirror.class_provider.class_register import ClassRegister

# # Add src to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


class SimpleService:
    def __init__(self, name: str):
        self.name = name


class SimpleServiceRegister(ClassRegister):
    reference = ClassReference(id="simple", cls=SimpleService)


class TestSimple(unittest.TestCase):
    def test_works(self):
        self.assertTrue(True)


if __name__ == "__main__":
    unittest.main()
