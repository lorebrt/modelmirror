"""
Edge cases and error condition tests for ModelMirror JSON configurations.

This test suite focuses on boundary conditions, error handling, and edge cases
that the ModelMirror library should handle gracefully.
"""

import unittest
import json
from typing import List, Dict
from pydantic import BaseModel, ConfigDict

from modelmirror.mirror import Mirror
from tests.fixtures.test_classes import SimpleService, DatabaseService


class EdgeCaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    service: SimpleService


class TestJSONEdgeCases(unittest.TestCase):
    """Test suite for JSON configuration edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.mirror = Mirror('tests.fixtures')

    def test_empty_json_object(self):
        """Test handling of completely empty JSON object."""
        config = self.mirror.reflect_typed('tests/configs/empty.json', BaseModel)
        self.assertIsInstance(config, BaseModel)

    def test_json_with_only_primitives(self):
        """Test JSON containing only primitive values (no $reference objects)."""
        with open('tests/configs/primitives_only.json', 'w') as f:
            json.dump({
                "string_value": "test",
                "number_value": 42,
                "boolean_value": True,
                "null_value": None,
                "array_value": [1, 2, 3],
                "object_value": {"nested": "value"}
            }, f)
        
        instances = self.mirror.reflect_raw('tests/configs/primitives_only.json')
        # Should return empty instances since no $reference objects
        self.assertEqual(len(instances._instances), 0)

    def test_deeply_nested_json_structure(self):
        """Test very deeply nested JSON structures."""
        deep_config = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "service": {
                                    "$reference": {
                                        "registry": {
                                            "schema": "simple_service",
                                            "version": "1.0.0"
                                        }
                                    },
                                    "name": "deep_service"
                                }
                            }
                        }
                    }
                }
            }
        }
        
        with open('tests/configs/deep_structure.json', 'w') as f:
            json.dump(deep_config, f)
        
        instances = self.mirror.reflect_raw('tests/configs/deep_structure.json')
        services = instances.get(list[SimpleService])
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0].name, "deep_service")

    def test_large_array_of_instances(self):
        """Test handling of large arrays with many instances."""
        large_config = {
            "services": []
        }
        
        # Create 100 service instances
        for i in range(100):
            service_config = {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": f"service_{i}"
            }
            large_config["services"].append(service_config)
        
        with open('tests/configs/large_array.json', 'w') as f:
            json.dump(large_config, f)
        
        instances = self.mirror.reflect_raw('tests/configs/large_array.json')
        services = instances.get(list[SimpleService])
        self.assertEqual(len(services), 100)

    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters in JSON."""
        unicode_config = {
            "service": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": "测试服务_🚀_special-chars.test@domain.com"
            }
        }
        
        with open('tests/configs/unicode_test.json', 'w', encoding='utf-8') as f:
            json.dump(unicode_config, f, ensure_ascii=False)
        
        config = self.mirror.reflect_typed('tests/configs/unicode_test.json', EdgeCaseConfig)
        self.assertEqual(config.service.name, "测试服务_🚀_special-chars.test@domain.com")

    def test_json_with_comments_should_fail(self):
        """Test that JSON with comments fails gracefully."""
        json_with_comments = '''
        {
            // This is a comment
            "service": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": "test" /* inline comment */
            }
        }
        '''
        
        with open('tests/configs/with_comments.json', 'w') as f:
            f.write(json_with_comments)
        
        with self.assertRaises(json.JSONDecodeError):
            self.mirror.reflect_raw('tests/configs/with_comments.json')

    def test_malformed_json_syntax(self):
        """Test handling of malformed JSON syntax."""
        malformed_json = '{"service": {"name": "test",}}'  # Trailing comma
        
        with open('tests/configs/malformed.json', 'w') as f:
            f.write(malformed_json)
        
        with self.assertRaises(json.JSONDecodeError):
            self.mirror.reflect_raw('tests/configs/malformed.json')

    def test_reference_object_missing_registry(self):
        """Test $reference object missing required registry field."""
        config = {
            "service": {
                "$reference": {
                    "instance": "test_instance"
                    # Missing registry field
                },
                "name": "test"
            }
        }
        
        with open('tests/configs/missing_registry.json', 'w') as f:
            json.dump(config, f)
        
        with self.assertRaises(Exception):
            self.mirror.reflect_raw('tests/configs/missing_registry.json')

    def test_reference_object_with_extra_fields(self):
        """Test $reference object with unexpected extra fields."""
        config = {
            "service": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    },
                    "unexpected_field": "should_be_ignored"
                },
                "name": "test"
            }
        }
        
        with open('tests/configs/extra_fields.json', 'w') as f:
            json.dump(config, f)
        
        # Should handle gracefully by ignoring extra fields
        instances = self.mirror.reflect_raw('tests/configs/extra_fields.json')
        services = instances.get(list[SimpleService])
        self.assertEqual(len(services), 1)

    def test_singleton_reference_case_sensitivity(self):
        """Test that singleton references are case sensitive."""
        config = {
            "service1": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    },
                    "instance": "TestService"
                },
                "name": "original"
            },
            "service2": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": "$testservice"  # Different case
            }
        }
        
        with open('tests/configs/case_sensitive.json', 'w') as f:
            json.dump(config, f)
        
        with self.assertRaises(Exception):
            self.mirror.reflect_raw('tests/configs/case_sensitive.json')

    def test_numeric_and_boolean_singleton_names(self):
        """Test singleton names that are numeric or boolean-like."""
        config = {
            "service1": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    },
                    "instance": "123"
                },
                "name": "numeric_singleton"
            },
            "service2": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": "$123"
            }
        }
        
        with open('tests/configs/numeric_singleton.json', 'w') as f:
            json.dump(config, f)
        
        instances = self.mirror.reflect_raw('tests/configs/numeric_singleton.json')
        services = instances.get(list[SimpleService])
        self.assertEqual(len(services), 2)
        # Both should reference the same instance
        self.assertIs(services[0], services[1])

    def test_empty_string_values(self):
        """Test handling of empty string values in configuration."""
        config = {
            "service": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": ""  # Empty string
            }
        }
        
        with open('tests/configs/empty_strings.json', 'w') as f:
            json.dump(config, f)
        
        config_obj = self.mirror.reflect_typed('tests/configs/empty_strings.json', EdgeCaseConfig)
        self.assertEqual(config_obj.service.name, "")

    def test_very_long_string_values(self):
        """Test handling of very long string values."""
        long_string = "x" * 10000  # 10KB string
        
        config = {
            "service": {
                "$reference": {
                    "registry": {
                        "schema": "simple_service",
                        "version": "1.0.0"
                    }
                },
                "name": long_string
            }
        }
        
        with open('tests/configs/long_strings.json', 'w') as f:
            json.dump(config, f)
        
        config_obj = self.mirror.reflect_typed('tests/configs/long_strings.json', EdgeCaseConfig)
        self.assertEqual(len(config_obj.service.name), 10000)

    def test_nested_arrays_and_objects(self):
        """Test complex nested structures with arrays and objects."""
        config = {
            "complex_structure": {
                "arrays": [
                    [1, 2, 3],
                    ["a", "b", "c"],
                    [
                        {
                            "$reference": {
                                "registry": {
                                    "schema": "simple_service",
                                    "version": "1.0.0"
                                }
                            },
                            "name": "nested_in_array"
                        }
                    ]
                ],
                "objects": {
                    "level1": {
                        "level2": {
                            "services": [
                                {
                                    "$reference": {
                                        "registry": {
                                            "schema": "simple_service",
                                            "version": "1.0.0"
                                        }
                                    },
                                    "name": "deeply_nested"
                                }
                            ]
                        }
                    }
                }
            }
        }
        
        with open('tests/configs/complex_nested.json', 'w') as f:
            json.dump(config, f)
        
        instances = self.mirror.reflect_raw('tests/configs/complex_nested.json')
        services = instances.get(list[SimpleService])
        self.assertEqual(len(services), 2)


if __name__ == '__main__':
    unittest.main()