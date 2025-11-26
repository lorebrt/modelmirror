# ModelMirror Test Suite

This directory contains a comprehensive test suite for ModelMirror JSON configuration handling.

## Test Structure

### Core Test Files

- **`test_json_configurations.py`** - Main test suite covering all JSON configuration patterns
- **`test_json_edge_cases.py`** - Edge cases and error condition tests  
- **`test_json_validation.py`** - Pydantic validation and type safety tests
- **`test_runner.py`** - Comprehensive test runner

### Test Fixtures

- **`fixtures/`** - Test classes and class registers
  - `test_classes.py` - Service classes for testing
  - `class_registers.py` - Class registrations for the test classes

### Test Configurations

- **`configs/`** - JSON configuration files for testing
  - Basic configurations (simple.json, database.json)
  - Singleton patterns (singleton_basic.json, dependency_injection.json)
  - Collection patterns (list_*.json, dict_*.json)
  - Nested structures (nested_objects.json, deep_nesting.json)
  - Error conditions (circular_references.json, missing_singleton.json)
  - Validation tests (strict_*.json, optional_*.json)

## Test Categories

### 1. Basic JSON Configuration Tests (`test_json_configurations.py`)

Tests fundamental JSON configuration patterns:

- **Simple Instance Creation** - Basic object instantiation from JSON
- **Multiple Parameters** - Services with multiple constructor parameters
- **Singleton References** - Basic singleton functionality with `$mirror`
- **Dependency Injection** - Services depending on other services
- **Collections** - Lists and dictionaries of instances
- **Nested Objects** - Complex nested object structures
- **Mixed Configurations** - Complex scenarios combining all features

### 2. Edge Cases and Error Handling (`test_json_edge_cases.py`)

Tests boundary conditions and error scenarios:

- **Empty Configurations** - Handling of empty JSON objects
- **Large Structures** - Performance with large arrays and deep nesting
- **Unicode Support** - Special characters and internationalization
- **Malformed JSON** - Graceful handling of syntax errors
- **Invalid References** - Missing or malformed `$mirror` objects
- **Circular Dependencies** - Detection and handling of circular references

### 3. Validation and Type Safety (`test_json_validation.py`)

Tests Pydantic integration and type validation:

- **Strict Validation** - Field constraints and extra field handling
- **Optional Fields** - Handling of optional and nullable fields
- **Union Types** - Support for Union type annotations
- **Custom Validators** - Integration with Pydantic validators
- **Type Coercion** - Automatic type conversion
- **Error Messages** - Informative validation error reporting

## JSON Configuration Patterns Tested

### Basic Patterns

```json
{
    "service": {
        "$mirror": {
            "registry": {"schema": "service_type", "version": "1.0.0"}
        },
        "param1": "value1",
        "param2": "value2"
    }
}
```

### Singleton Pattern

```json
{
    "shared_service": {
        "$mirror": {
            "registry": {"schema": "service_type", "version": "1.0.0"},
            "instance": "shared"
        },
        "config": "shared_config"
    },
    "dependent_service": {
        "$mirror": {
            "registry": {"schema": "other_service", "version": "1.0.0"}
        },
        "dependency": "$shared"
    }
}
```

### Collection Patterns

```json
{
    "service_list": [
        {"$mirror": {...}, "param": "value1"},
        {"$mirror": {...}, "param": "value2"},
        "$singleton_reference"
    ],
    "service_map": {
        "key1": {"$mirror": {...}, "param": "value"},
        "key2": "$singleton_reference"
    }
}
```

### Nested Patterns

```json
{
    "complex_service": {
        "$mirror": {
            "registry": {"schema": "complex", "version": "1.0.0"}
        },
        "nested_dependency": {
            "$mirror": {
                "registry": {"schema": "nested", "version": "1.0.0"}
            },
            "param": "nested_value"
        }
    }
}
```

## Running Tests

### Run All Tests
```bash
python -m tests.test_runner
```

### Run Specific Test Suite
```bash
python -m tests.test_runner configurations
python -m tests.test_runner edge_cases  
python -m tests.test_runner validation
```

### Run Individual Test Files
```bash
python -m pytest tests/test_json_configurations.py
python -m pytest tests/test_json_edge_cases.py
python -m pytest tests/test_json_validation.py
```

### Run Specific Test Methods
```bash
python -m pytest tests/test_json_configurations.py::TestJSONConfigurations::test_singleton_reference_basic
```

## Test Coverage

The test suite provides comprehensive coverage of:

- ✅ All JSON configuration patterns supported by ModelMirror
- ✅ Error conditions and edge cases
- ✅ Pydantic validation integration
- ✅ Type safety and schema enforcement
- ✅ Performance with large configurations
- ✅ Unicode and special character support
- ✅ Circular dependency detection
- ✅ Singleton reference management
- ✅ Nested object creation
- ✅ Collection handling (lists, dictionaries)
- ✅ Raw vs typed reflection modes

## Adding New Tests

When adding new tests:

1. **Create test classes** in `fixtures/test_classes.py`
2. **Register classes** in `fixtures/class_registers.py`  
3. **Add JSON configs** in `configs/` directory
4. **Write test methods** in appropriate test file
5. **Update this README** with new patterns tested

## Test Philosophy

These tests follow unit testing best practices:

- **Focused** - Each test validates a specific JSON configuration pattern
- **Independent** - Tests don't depend on each other
- **Comprehensive** - Cover all supported JSON structures
- **Clear** - Test names and documentation explain what's being tested
- **Fast** - Efficient execution for rapid development feedback