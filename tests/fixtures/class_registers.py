"""
Class registers for test fixtures.
These registers link the test classes to their schema identifiers.
"""

from modelmirror.class_provider.class_register import ClassRegister
from modelmirror.class_provider.class_reference import ClassReference

from tests.fixtures.test_classes import (
    SimpleService, DatabaseService, UserService, ConfigurableService,
    ComplexService, ServiceWithDefaults, ServiceWithOptionals,
    ListService, DictService, NestedService, ValidationService
)


class SimpleServiceRegister(ClassRegister, 
    reference=ClassReference(id="simple_service", cls=SimpleService)):
    pass


class DatabaseServiceRegister(ClassRegister,
    reference=ClassReference(id="database_service", cls=DatabaseService)):
    pass


class UserServiceRegister(ClassRegister,
    reference=ClassReference(id="user_service", cls=UserService)):
    pass


class ConfigurableServiceRegister(ClassRegister,
    reference=ClassReference(id="configurable_service", cls=ConfigurableService)):
    pass


class ComplexServiceRegister(ClassRegister,
    reference=ClassReference(id="complex_service", cls=ComplexService)):
    pass


class ServiceWithDefaultsRegister(ClassRegister,
    reference=ClassReference(id="service_with_defaults", cls=ServiceWithDefaults)):
    pass


class ServiceWithOptionalsRegister(ClassRegister,
    reference=ClassReference(id="service_with_optionals", cls=ServiceWithOptionals)):
    pass


class ListServiceRegister(ClassRegister,
    reference=ClassReference(id="list_service", cls=ListService)):
    pass


class DictServiceRegister(ClassRegister,
    reference=ClassReference(id="dict_service", cls=DictService)):
    pass


class NestedServiceRegister(ClassRegister,
    reference=ClassReference(id="nested_service", cls=NestedService)):
    pass


class ValidationServiceRegister(ClassRegister,
    reference=ClassReference(id="validation_service", cls=ValidationService)):
    pass