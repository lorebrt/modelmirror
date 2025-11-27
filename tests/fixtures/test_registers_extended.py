"""
Class registers for extended testing classes.
"""

from modelmirror.class_provider.class_register import ClassRegister
from modelmirror.class_provider.class_reference import ClassReference

from tests.fixtures.test_classes_extended import (
    TestService,
    MutableDefaultService, 
    FastAPILikeService,
    StatefulService,
    ValidationSensitiveService
)


class TestServiceRegister(ClassRegister):
    reference = ClassReference(id="test_service", cls=TestService)


class MutableDefaultServiceRegister(ClassRegister):
    reference = ClassReference(id="mutable_default_service", cls=MutableDefaultService)


class FastAPILikeServiceRegister(ClassRegister):
    reference = ClassReference(id="fastapi_like_service", cls=FastAPILikeService)


class StatefulServiceRegister(ClassRegister):
    reference = ClassReference(id="stateful_service", cls=StatefulService)


class ValidationSensitiveServiceRegister(ClassRegister):
    reference = ClassReference(id="validation_sensitive_service", cls=ValidationSensitiveService)