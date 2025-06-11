import unittest
from app.matching.field_similarity import FieldSimilarityCalculator

class TestFieldSimilarityCalculator(unittest.TestCase):
    
    def test_init_field_handlers_keys(self):
        """Test that __init__ creates _field_handlers with correct keys."""
        calculator = FieldSimilarityCalculator()
        expected_keys = {"PhoneNumber", "Address"}
        self.assertEqual(set(calculator._field_handlers.keys()), expected_keys)
    
    def test_init_field_handlers_values_are_callable(self):
        """Test that __init__ creates _field_handlers with callable values."""
        calculator = FieldSimilarityCalculator()
        for key, handler in calculator._field_handlers.items():
            with self.subTest(key=key):
                self.assertTrue(callable(handler))
    
    def test_init_field_handlers_correct_methods(self):
        """Test that __init__ maps field handlers to correct methods."""
        calculator = FieldSimilarityCalculator()
        self.assertEqual(calculator._field_handlers["PhoneNumber"], calculator._phone_similarity)
        self.assertEqual(calculator._field_handlers["Address"], calculator._address_similarity)
    
    def test_init_type_handlers_keys(self):
        """Test that __init__ creates _type_handlers with correct keys."""
        calculator = FieldSimilarityCalculator()
        expected_keys = {"exact", "name", "general"}
        self.assertEqual(set(calculator._type_handlers.keys()), expected_keys)
    
    def test_init_type_handlers_values_are_callable(self):
        """Test that __init__ creates _type_handlers with callable values."""
        calculator = FieldSimilarityCalculator()
        for key, handler in calculator._type_handlers.items():
            with self.subTest(key=key):
                self.assertTrue(callable(handler))
    
    def test_init_type_handlers_correct_methods(self):
        """Test that __init__ maps type handlers to correct methods."""
        calculator = FieldSimilarityCalculator()
        self.assertEqual(calculator._type_handlers["name"], calculator._name_similarity)
        self.assertEqual(calculator._type_handlers["general"], calculator._general_similarity)
    
    def test_init_exact_handler_lambda_function(self):
        """Test that __init__ creates correct lambda function for exact handler."""
        calculator = FieldSimilarityCalculator()
        exact_handler = calculator._type_handlers["exact"]
        
        # Test exact match returns 1.0
        self.assertEqual(exact_handler("test", "test"), 1.0)
        
        # Test non-match returns 0.0
        self.assertEqual(exact_handler("test", "different"), 0.0)
        self.assertEqual(exact_handler("", "test"), 0.0)
        self.assertEqual(exact_handler("test", ""), 0.0)
    
    def test_init_field_handlers_count(self):
        """Test that __init__ creates correct number of field handlers."""
        calculator = FieldSimilarityCalculator()
        self.assertEqual(len(calculator._field_handlers), 2)
    
    def test_init_type_handlers_count(self):
        """Test that __init__ creates correct number of type handlers."""
        calculator = FieldSimilarityCalculator()
        self.assertEqual(len(calculator._type_handlers), 3)
    
    def test_init_creates_separate_instances(self):
        """Test that __init__ creates separate handler dictionaries for different instances."""
        calculator1 = FieldSimilarityCalculator()
        calculator2 = FieldSimilarityCalculator()
        
        # Dictionaries should be separate objects
        self.assertIsNot(calculator1._field_handlers, calculator2._field_handlers)
        self.assertIsNot(calculator1._type_handlers, calculator2._type_handlers)
        
        # But should have same content
        self.assertEqual(calculator1._field_handlers.keys(), calculator2._field_handlers.keys())
        self.assertEqual(calculator1._type_handlers.keys(), calculator2._type_handlers.keys())


if __name__ == "__main__":
    unittest.main()