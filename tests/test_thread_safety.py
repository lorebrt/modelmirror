"""
Test suite to demonstrate thread safety issues in ModelMirror.

This test shows how concurrent usage of ModelMirror can lead to:
1. Race conditions in class modification
2. Shared state corruption
3. Inconsistent behavior across threads
"""

import unittest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from pydantic import BaseModel, ConfigDict

from modelmirror.mirror import Mirror
from tests.fixtures.test_classes_extended import StatefulService, ValidationSensitiveService


class ThreadTestConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    stateful_service: StatefulService


class TestThreadSafetyBug(unittest.TestCase):
    """Test suite demonstrating thread safety issues in ModelMirror."""

    def setUp(self):
        """Reset state before each test."""
        StatefulService.reset_class_state()

    def test_concurrent_mirror_creation_race_condition(self):
        """Test race conditions when creating Mirror instances concurrently."""
        results = []
        errors = []
        
        def create_mirror_and_reflect(thread_id: int):
            try:
                mirror = Mirror('tests.fixtures')
                # Simulate some work
                time.sleep(0.01)  # Small delay to increase chance of race conditions
                
                # Check the state of the class after Mirror creation
                init_method = StatefulService.__init__
                results.append({
                    'thread_id': thread_id,
                    'init_method': init_method,
                    'instance_count': StatefulService.get_instance_count()
                })
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
        
        # Create multiple threads that create Mirror instances concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_mirror_and_reflect, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Analyze results
        print(f"Errors: {errors}")
        print(f"Results count: {len(results)}")
        
        if errors:
            print(f"Race condition errors occurred: {errors}")
        
        # Check if all threads see the same modified class
        if results:
            first_init = results[0]['init_method']
            for result in results[1:]:
                self.assertIs(result['init_method'], first_init,
                             "All threads should see the same globally modified class")

    def test_concurrent_reflection_with_shared_singletons(self):
        """Test concurrent reflections that use shared singletons."""
        results = []
        errors = []
        
        def reflect_config(thread_id: int):
            try:
                mirror = Mirror('tests.fixtures')
                
                # Create a simple config that uses singletons
                config_data = {
                    "service": {
                        "$mirror": "stateful_service:shared_singleton",
                        "name": f"thread_{thread_id}"
                    }
                }
                
                # Write temporary config file
                import json
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(config_data, f)
                    temp_file = f.name
                
                try:
                    instances = mirror.reflect_raw(temp_file)
                    service = instances.get(StatefulService, '$shared_singleton')
                    
                    results.append({
                        'thread_id': thread_id,
                        'service_name': service.name,
                        'service_id': service.instance_id,
                        'service_object_id': id(service)
                    })
                finally:
                    os.unlink(temp_file)
                    
            except Exception as e:
                errors.append({'thread_id': thread_id, 'error': str(e)})
        
        # Run concurrent reflections
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(reflect_config, i) for i in range(10)]
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append({'error': str(e)})
        
        print(f"Concurrent reflection results: {results}")
        print(f"Concurrent reflection errors: {errors}")
        
        if errors:
            print(f"Concurrent reflection errors: {errors}")
        
        # Analyze singleton behavior
        if results:
            # Check if singleton names are consistent
            singleton_objects = set(r['service_object_id'] for r in results)
            print(f"Number of unique singleton objects: {len(singleton_objects)}")
            
            # In a properly isolated system, each thread should get its own singleton
            # But due to global state, they might share the same singleton
            if len(singleton_objects) == 1:
                print("PROBLEM: All threads share the same singleton instance!")
            else:
                print("Threads have separate singleton instances (better isolation)")

    def test_class_modification_thread_safety(self):
        """Test thread safety of class modifications."""
        modification_results = []
        
        def check_class_modification(thread_id: int):
            # Check initial state
            initial_init = ValidationSensitiveService.__init__
            
            # Create Mirror (which modifies classes)
            mirror = Mirror('tests.fixtures')
            
            # Check final state
            final_init = ValidationSensitiveService.__init__
            
            modification_results.append({
                'thread_id': thread_id,
                'initial_init': initial_init,
                'final_init': final_init,
                'was_modified': initial_init is not final_init
            })
        
        # Run concurrent class modifications
        threads = []
        for i in range(5):
            thread = threading.Thread(target=check_class_modification, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print(f"Class modification results: {modification_results}")
        
        # Check consistency
        if modification_results:
            final_inits = [r['final_init'] for r in modification_results]
            unique_final_inits = set(id(init) for init in final_inits)
            
            self.assertEqual(len(unique_final_inits), 1,
                           "All threads should see the same final modified class")

    def test_registry_state_corruption_under_concurrency(self):
        """Test registry state corruption under concurrent access."""
        registry_states = []
        
        def capture_registry_state(thread_id: int):
            mirror = Mirror('tests.fixtures')
            
            # Access internal registry state (if possible)
            # This is implementation-specific
            try:
                registered_classes = mirror._Mirror__registered_classes # type: ignore
                class_count = len(registered_classes)
                
                registry_states.append({
                    'thread_id': thread_id,
                    'class_count': class_count,
                    'registry_id': id(registered_classes)
                })
            except AttributeError:
                # Registry structure might be different
                registry_states.append({
                    'thread_id': thread_id,
                    'error': 'Could not access registry state'
                })
        
        # Concurrent registry access
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(capture_registry_state, i) for i in range(6)]
            
            for future in as_completed(futures):
                future.result()
        
        print(f"Registry states: {registry_states}")
        
        # Check for consistency
        valid_states = [s for s in registry_states if 'class_count' in s]
        if valid_states:
            class_counts = [s['class_count'] for s in valid_states]
            unique_counts = set(class_counts)
            
            if len(unique_counts) > 1:
                print(f"PROBLEM: Inconsistent registry states: {unique_counts}")
            else:
                print(f"Registry states are consistent: {unique_counts}")

    def test_singleton_lifecycle_thread_safety(self):
        """Test singleton lifecycle thread safety."""
        singleton_lifecycles = []
        
        def test_singleton_lifecycle(thread_id: int):
            try:
                mirror = Mirror('tests.fixtures')
                
                # Create config with singleton
                config_data = {
                    "service": {
                        "$mirror": "stateful_service:lifecycle_test",
                        "name": f"lifecycle_{thread_id}"
                    }
                }
                
                import json
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(config_data, f)
                    temp_file = f.name
                
                try:
                    # First reflection
                    instances1 = mirror.reflect_raw(temp_file)
                    service1 = instances1.get(StatefulService, '$lifecycle_test')
                    
                    # Second reflection (should reset and create new singleton)
                    instances2 = mirror.reflect_raw(temp_file)
                    service2 = instances2.get(StatefulService, '$lifecycle_test')
                    
                    singleton_lifecycles.append({
                        'thread_id': thread_id,
                        'first_service_id': id(service1),
                        'second_service_id': id(service2),
                        'same_instance': service1 is service2
                    })
                    
                finally:
                    os.unlink(temp_file)
                    
            except Exception as e:
                singleton_lifecycles.append({
                    'thread_id': thread_id,
                    'error': str(e)
                })
        
        # Test concurrent singleton lifecycles
        threads = []
        for i in range(4):
            thread = threading.Thread(target=test_singleton_lifecycle, args=(i,))
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print(f"Singleton lifecycles: {singleton_lifecycles}")
        
        # Analyze results
        valid_results = [r for r in singleton_lifecycles if 'same_instance' in r]
        if valid_results:
            same_instance_counts = sum(1 for r in valid_results if r['same_instance'])
            print(f"Threads with same singleton instance: {same_instance_counts}/{len(valid_results)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)