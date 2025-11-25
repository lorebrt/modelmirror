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
    reference=ClassReference(schema="simple_service", version="1.0.0", cls=SimpleService)):
    pass


class DatabaseServiceRegister(ClassRegister,
    reference=ClassReference(schema="database_service", version="1.0.0", cls=DatabaseService)):
    pass


class UserServiceRegister(ClassRegister,
    reference=ClassReference(schema="user_service", version="1.0.0", cls=UserService)):
    pass


class ConfigurableServiceRegister(ClassRegister,
    reference=ClassReference(schema="configurable_service", version="1.0.0", cls=ConfigurableService)):
    pass


class ComplexServiceRegister(ClassRegister,
    reference=ClassReference(schema="complex_service", version="1.0.0", cls=ComplexService)):
    pass


class ServiceWithDefaultsRegister(ClassRegister,
    reference=ClassReference(schema="service_with_defaults", version="1.0.0", cls=ServiceWithDefaults)):
    pass


class ServiceWithOptionalsRegister(ClassRegister,
    reference=ClassReference(schema="service_with_optionals", version="1.0.0", cls=ServiceWithOptionals)):
    pass


class ListServiceRegister(ClassRegister,
    reference=ClassReference(schema="list_service", version="1.0.0", cls=ListService)):
    pass


class DictServiceRegister(ClassRegister,
    reference=ClassReference(schema="dict_service", version="1.0.0", cls=DictService)):
    pass


class NestedServiceRegister(ClassRegister,
    reference=ClassReference(schema="nested_service", version="1.0.0", cls=NestedService)):
    pass


class ValidationServiceRegister(ClassRegister,
    reference=ClassReference(schema="validation_service", version="1.0.0", cls=ValidationService)):
    pass