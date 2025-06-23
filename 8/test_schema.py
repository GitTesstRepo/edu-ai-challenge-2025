import unittest
from datetime import datetime, timedelta
from schema import (
    Schema, ValidationResult, ValidationError, ValidationLevel,
    StringValidator, NumberValidator, BooleanValidator, DateValidator,
    ObjectValidator, ArrayValidator
)


class TestStringValidator(unittest.TestCase):
    """Test cases for StringValidator"""

    def test_valid_string(self):
        """Test basic string validation"""
        validator = Schema.string()
        result = validator.validate("hello")
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_invalid_type(self):
        """Test string validator with non-string input"""
        validator = Schema.string()
        result = validator.validate(123)
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_min_length(self):
        """Test minimum length validation"""
        validator = Schema.string().min_length(5)
        
        # Valid case
        result = validator.validate("hello world")
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("hi")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MIN_LENGTH")

    def test_max_length(self):
        """Test maximum length validation"""
        validator = Schema.string().max_length(5)
        
        # Valid case
        result = validator.validate("hello")
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("hello world")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MAX_LENGTH")

    def test_pattern_matching(self):
        """Test regex pattern validation"""
        validator = Schema.string().pattern(r'^\d{3}-\d{2}-\d{4}$')
        
        # Valid case
        result = validator.validate("123-45-6789")
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("123456789")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "PATTERN_MISMATCH")

    def test_allowed_values(self):
        """Test allowed values validation"""
        validator = Schema.string().allowed_values(['red', 'green', 'blue'])
        
        # Valid cases
        for color in ['red', 'green', 'blue']:
            result = validator.validate(color)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("yellow")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "INVALID_VALUE")

    def test_case_insensitive_allowed_values(self):
        """Test case-insensitive allowed values"""
        validator = Schema.string().allowed_values(['Red', 'Green']).case_sensitive(False)
        
        # Valid cases (case-insensitive)
        for color in ['red', 'RED', 'Red', 'green', 'GREEN']:
            result = validator.validate(color)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("blue")
        self.assertFalse(result.is_valid)

    def test_trim_functionality(self):
        """Test string trimming functionality"""
        validator = Schema.string().trim().min_length(5)
        
        # Valid case (trimmed)
        result = validator.validate("  hello world  ")
        self.assertTrue(result.is_valid)
        
        # Invalid case (too short after trimming)
        result = validator.validate("  hi  ")
        self.assertFalse(result.is_valid)

    def test_optional_string(self):
        """Test optional string validation"""
        validator = Schema.string().optional()
        
        # Valid cases
        for value in [None, "", "hello"]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid)

    def test_custom_error_message(self):
        """Test custom error message"""
        validator = Schema.string().with_message("Custom error message")
        result = validator.validate(123)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].message, "Custom error message")


class TestNumberValidator(unittest.TestCase):
    """Test cases for NumberValidator"""

    def test_valid_number(self):
        """Test basic number validation"""
        validator = Schema.number()
        
        # Valid cases
        for num in [0, 1, -1, 3.14, 100]:
            result = validator.validate(num)
            self.assertTrue(result.is_valid)

    def test_invalid_type(self):
        """Test number validator with non-number input"""
        validator = Schema.number()
        
        # Invalid cases
        for value in ["123", True, False, [], {}]:
            result = validator.validate(value)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_min_value(self):
        """Test minimum value validation"""
        validator = Schema.number().min_value(0)
        
        # Valid cases
        for num in [0, 1, 100]:
            result = validator.validate(num)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate(-1)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MIN_VALUE")

    def test_max_value(self):
        """Test maximum value validation"""
        validator = Schema.number().max_value(100)
        
        # Valid cases
        for num in [0, 50, 100]:
            result = validator.validate(num)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate(101)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MAX_VALUE")

    def test_integer_only(self):
        """Test integer-only validation"""
        validator = Schema.number().integer_only()
        
        # Valid cases
        for num in [0, 1, -1, 100]:
            result = validator.validate(num)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate(3.14)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "INTEGER_REQUIRED")

    def test_allowed_values(self):
        """Test allowed values validation"""
        validator = Schema.number().allowed_values([1, 2, 3, 5, 8])
        
        # Valid cases
        for num in [1, 2, 3, 5, 8]:
            result = validator.validate(num)
            self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate(4)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "INVALID_VALUE")

    def test_optional_number(self):
        """Test optional number validation"""
        validator = Schema.number().optional()
        
        # Valid cases
        for value in [None, 0, 1, 3.14]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid)


class TestBooleanValidator(unittest.TestCase):
    """Test cases for BooleanValidator"""

    def test_valid_boolean(self):
        """Test basic boolean validation"""
        validator = Schema.boolean()
        
        # Valid cases
        for value in [True, False]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid)

    def test_truthy_values(self):
        """Test truthy value conversion"""
        validator = Schema.boolean()
        
        # Valid truthy values
        for value in ["true", "1", 1, "yes", "on"]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid, f"Failed for truthy value: {value}")
        
        # Valid falsy values (excluding empty string for required fields)
        for value in ["false", "0", 0, "no", "off"]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid, f"Failed for falsy value: {value}")

    def test_custom_truthy_falsy_values(self):
        """Test custom truthy/falsy values"""
        validator = Schema.boolean().truthy_values(['yes', 'y']).falsy_values(['no', 'n'])
        
        # Valid cases
        for value in ['yes', 'y', 'no', 'n']:
            result = validator.validate(value)
            self.assertTrue(result.is_valid, f"Failed for custom value: {value}")
        
        # Invalid case
        result = validator.validate("maybe")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_invalid_type(self):
        """Test boolean validator with invalid input"""
        validator = Schema.boolean()
        
        # Invalid cases
        for value in [123, "invalid", [], {}]:
            result = validator.validate(value)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_optional_boolean(self):
        """Test optional boolean validation"""
        validator = Schema.boolean().optional()
        
        # Valid cases
        for value in [None, True, False, "true", "false"]:
            result = validator.validate(value)
            self.assertTrue(result.is_valid, f"Failed for optional value: {value}")


class TestDateValidator(unittest.TestCase):
    """Test cases for DateValidator"""

    def test_valid_datetime_object(self):
        """Test validation with datetime object"""
        validator = Schema.date()
        now = datetime.now()
        result = validator.validate(now)
        self.assertTrue(result.is_valid)

    def test_valid_date_string(self):
        """Test validation with date string"""
        validator = Schema.date()
        
        # Valid date strings
        for date_str in ["2024-01-15", "2024-01-15 10:30:00", "15/01/2024"]:
            result = validator.validate(date_str)
            self.assertTrue(result.is_valid)

    def test_invalid_date_format(self):
        """Test invalid date format"""
        validator = Schema.date()
        
        # Invalid date strings
        for date_str in ["invalid-date", "2024/13/45", "not-a-date"]:
            result = validator.validate(date_str)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "DATE_FORMAT_ERROR")

    def test_specific_date_format(self):
        """Test specific date format validation"""
        validator = Schema.date().format('%Y-%m-%d')
        
        # Valid case
        result = validator.validate("2024-01-15")
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate("15/01/2024")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "DATE_FORMAT_ERROR")

    def test_date_range_validation(self):
        """Test date range validation"""
        now = datetime.now()
        past_date = now - timedelta(days=365)
        future_date = now + timedelta(days=365)
        
        validator = Schema.date().min_date(past_date).max_date(future_date)
        
        # Valid case
        result = validator.validate(now)
        self.assertTrue(result.is_valid)
        
        # Invalid case (too old)
        old_date = now - timedelta(days=400)
        result = validator.validate(old_date)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MIN_DATE")

    def test_invalid_type(self):
        """Test date validator with invalid type"""
        validator = Schema.date()
        
        # Invalid cases
        for value in [123, True, [], {}]:
            result = validator.validate(value)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "TYPE_ERROR")


class TestArrayValidator(unittest.TestCase):
    """Test cases for ArrayValidator"""

    def test_valid_array(self):
        """Test basic array validation"""
        validator = Schema.array(Schema.string())
        
        # Valid cases
        for arr in [["a", "b"], [], ["single"]]:
            result = validator.validate(arr)
            self.assertTrue(result.is_valid)

    def test_invalid_type(self):
        """Test array validator with non-array input"""
        validator = Schema.array(Schema.string())
        
        # Invalid cases
        for value in ["not-array", 123, True, {}]:
            result = validator.validate(value)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_array_length_validation(self):
        """Test array length validation"""
        validator = Schema.array(Schema.string()).min_length(2).max_length(4)
        
        # Valid cases
        for arr in [["a", "b"], ["a", "b", "c"], ["a", "b", "c", "d"]]:
            result = validator.validate(arr)
            self.assertTrue(result.is_valid)
        
        # Invalid cases
        result = validator.validate(["a"])  # Too short
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MIN_LENGTH")
        
        result = validator.validate(["a", "b", "c", "d", "e"])  # Too long
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MAX_LENGTH")

    def test_unique_items(self):
        """Test unique items validation"""
        validator = Schema.array(Schema.string()).unique()
        
        # Valid case
        result = validator.validate(["a", "b", "c"])
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate(["a", "b", "a"])
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "DUPLICATE_ITEM")

    def test_array_item_validation(self):
        """Test validation of array items"""
        validator = Schema.array(Schema.number().min_value(0))
        
        # Valid case
        result = validator.validate([1, 2, 3])
        self.assertTrue(result.is_valid)
        
        # Invalid case (negative number)
        result = validator.validate([1, -2, 3])
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].field, "[1]")
        self.assertEqual(result.errors[0].code, "MIN_VALUE")

    def test_nested_array_validation(self):
        """Test nested array validation"""
        validator = Schema.array(Schema.array(Schema.number()))
        
        # Valid case
        result = validator.validate([[1, 2], [3, 4]])
        self.assertTrue(result.is_valid)
        
        # Invalid case
        result = validator.validate([[1, 2], ["invalid", 4]])
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].field, "[1][0]")
        self.assertEqual(result.errors[0].code, "TYPE_ERROR")


class TestObjectValidator(unittest.TestCase):
    """Test cases for ObjectValidator"""

    def test_valid_object(self):
        """Test basic object validation"""
        schema = {
            'name': Schema.string(),
            'age': Schema.number()
        }
        validator = Schema.object(schema)
        
        # Valid case
        data = {'name': 'John', 'age': 30}
        result = validator.validate(data)
        self.assertTrue(result.is_valid)

    def test_invalid_type(self):
        """Test object validator with non-object input"""
        schema = {'name': Schema.string()}
        validator = Schema.object(schema)
        
        # Invalid cases
        for value in ["not-object", 123, True, []]:
            result = validator.validate(value)
            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_missing_required_fields(self):
        """Test missing required fields"""
        schema = {
            'name': Schema.string(),
            'age': Schema.number()
        }
        validator = Schema.object(schema)
        
        # Missing field
        data = {'name': 'John'}
        result = validator.validate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MISSING_FIELD")
        self.assertEqual(result.errors[0].field, "age")

    def test_optional_fields(self):
        """Test optional fields"""
        schema = {
            'name': Schema.string(),
            'age': Schema.number().optional()
        }
        validator = Schema.object(schema)
        
        # Valid cases
        for data in [
            {'name': 'John', 'age': 30},
            {'name': 'John'}  # age is optional
        ]:
            result = validator.validate(data)
            self.assertTrue(result.is_valid)

    def test_nested_object_validation(self):
        """Test nested object validation"""
        address_schema = {
            'street': Schema.string(),
            'city': Schema.string()
        }
        user_schema = {
            'name': Schema.string(),
            'address': Schema.object(address_schema)
        }
        validator = Schema.object(user_schema)
        
        # Valid case
        data = {
            'name': 'John',
            'address': {'street': '123 Main St', 'city': 'Anytown'}
        }
        result = validator.validate(data)
        self.assertTrue(result.is_valid)
        
        # Invalid nested field
        data = {
            'name': 'John',
            'address': {'street': 123, 'city': 'Anytown'}  # street should be string
        }
        result = validator.validate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].field, "address.street")
        self.assertEqual(result.errors[0].code, "TYPE_ERROR")

    def test_strict_mode(self):
        """Test strict mode (no unknown fields)"""
        schema = {'name': Schema.string()}
        validator = Schema.object(schema).strict()
        
        # Valid case
        data = {'name': 'John'}
        result = validator.validate(data)
        self.assertTrue(result.is_valid)
        
        # Invalid case (unknown field)
        data = {'name': 'John', 'unknown': 'field'}
        result = validator.validate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "UNKNOWN_FIELDS")

    def test_field_path_tracking(self):
        """Test field path tracking in nested objects"""
        deep_schema = {
            'level1': Schema.object({
                'level2': Schema.object({
                    'level3': Schema.string()
                })
            })
        }
        validator = Schema.object(deep_schema)
        
        # Invalid deep field
        data = {
            'level1': {
                'level2': {
                    'level3': 123  # Should be string
                }
            }
        }
        result = validator.validate(data)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].field, "level1.level2.level3")
        self.assertEqual(result.errors[0].code, "TYPE_ERROR")


class TestSchemaFactory(unittest.TestCase):
    """Test cases for Schema factory methods"""

    def test_email_validator(self):
        """Test email validator factory"""
        validator = Schema.email()
        
        # Valid emails
        for email in ["test@example.com", "user.name@domain.co.uk", "a@b.c"]:
            result = validator.validate(email)
            self.assertTrue(result.is_valid)
        
        # Invalid emails
        for email in ["invalid-email", "@domain.com", "user@", "user.domain.com"]:
            result = validator.validate(email)
            self.assertFalse(result.is_valid)

    def test_url_validator(self):
        """Test URL validator factory"""
        validator = Schema.url()
        
        # Valid URLs
        for url in ["http://example.com", "https://www.example.com/path", "http://localhost:3000"]:
            result = validator.validate(url)
            self.assertTrue(result.is_valid)
        
        # Invalid URLs
        for url in ["not-a-url", "ftp://example.com", "example.com"]:
            result = validator.validate(url)
            self.assertFalse(result.is_valid)

    def test_uuid_validator(self):
        """Test UUID validator factory"""
        validator = Schema.uuid()
        
        # Valid UUIDs
        for uuid_str in [
            "123e4567-e89b-12d3-a456-426614174000",
            "550e8400-e29b-41d4-a716-446655440000"
        ]:
            result = validator.validate(uuid_str)
            self.assertTrue(result.is_valid)
        
        # Invalid UUIDs
        for uuid_str in ["not-a-uuid", "123e4567-e89b-12d3-a456", "invalid-uuid-format"]:
            result = validator.validate(uuid_str)
            self.assertFalse(result.is_valid)


class TestComplexSchemas(unittest.TestCase):
    """Test cases for complex schema combinations"""

    def test_user_registration_schema(self):
        """Test complex user registration schema"""
        schema = Schema.object({
            'username': Schema.string().min_length(3).max_length(20).pattern(r'^[a-zA-Z0-9_]+$'),
            'email': Schema.email(),
            'password': Schema.string().min_length(8),
            'age': Schema.number().min_value(13).max_value(120).integer_only().optional(),
            'preferences': Schema.object({
                'theme': Schema.string().allowed_values(['light', 'dark']).optional(),
                'notifications': Schema.boolean().optional()
            }).optional(),
            'tags': Schema.array(Schema.string()).max_length(5).unique().optional()
        })
        
        # Valid data
        valid_data = {
            'username': 'john_doe',
            'email': 'john@example.com',
            'password': 'securepass123',
            'age': 25,
            'preferences': {
                'theme': 'dark',
                'notifications': True
            },
            'tags': ['developer', 'python']
        }
        result = schema.validate(valid_data)
        self.assertTrue(result.is_valid)
        
        # Invalid data (multiple errors)
        invalid_data = {
            'username': 'jo',  # Too short
            'email': 'invalid-email',  # Invalid email
            'password': '123',  # Too short
            'age': 5,  # Too young
            'preferences': {
                'theme': 'invalid-theme'  # Not allowed
            },
            'tags': ['dev', 'dev']  # Duplicate
        }
        result = schema.validate(invalid_data)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 1)

    def test_ecommerce_order_schema(self):
        """Test e-commerce order schema"""
        product_schema = Schema.object({
            'id': Schema.string(),
            'name': Schema.string().min_length(1),
            'price': Schema.number().min_value(0),
            'quantity': Schema.number().integer_only().min_value(1)
        })
        
        order_schema = Schema.object({
            'orderId': Schema.string(),
            'customer': Schema.object({
                'name': Schema.string().min_length(2),
                'email': Schema.email(),
                'phone': Schema.string().pattern(r'^\+?[\d\s\-\(\)]+$').optional()
            }),
            'products': Schema.array(product_schema).min_length(1),
            'total': Schema.number().min_value(0),
            'status': Schema.string().allowed_values(['pending', 'confirmed', 'shipped', 'delivered']),
            'createdAt': Schema.date().format('%Y-%m-%d %H:%M:%S')
        })
        
        # Valid order
        valid_order = {
            'orderId': 'ORD-12345',
            'customer': {
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1-555-123-4567'
            },
            'products': [
                {'id': 'PROD-1', 'name': 'Laptop', 'price': 999.99, 'quantity': 1},
                {'id': 'PROD-2', 'name': 'Mouse', 'price': 29.99, 'quantity': 2}
            ],
            'total': 1059.97,
            'status': 'pending',
            'createdAt': '2024-01-15 10:30:00'
        }
        result = order_schema.validate(valid_order)
        self.assertTrue(result.is_valid)

    def test_data_transformation(self):
        """Test data transformation functionality"""
        # String transformation
        upper_validator = Schema.string().transform(str.upper)
        result = upper_validator.validate("hello")
        self.assertTrue(result.is_valid)
        
        # Number transformation
        int_validator = Schema.number().transform(int)
        result = int_validator.validate(3.14)
        self.assertTrue(result.is_valid)
        
        # Custom transformation
        def custom_transform(value):
            return value.strip().lower()
        
        custom_validator = Schema.string().transform(custom_transform)
        result = custom_validator.validate("  HELLO WORLD  ")
        self.assertTrue(result.is_valid)

    def test_validation_levels(self):
        """Test validation levels (errors, warnings, info)"""
        result = ValidationResult(True)
        
        # Add different types of messages
        result.add_error('field1', 'This is an error', 'value1', 'ERROR_CODE')
        result.add_warning('field2', 'This is a warning', 'value2', 'WARNING_CODE')
        
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(len(result.warnings), 1)
        self.assertEqual(result.errors[0].level, ValidationLevel.ERROR)
        self.assertEqual(result.warnings[0].level, ValidationLevel.WARNING)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def test_empty_values(self):
        """Test validation with empty values"""
        # Empty string (valid only if optional)
        result = Schema.string().optional().validate("")
        self.assertTrue(result.is_valid)
        
        # Empty array (valid by default)
        result = Schema.array(Schema.string()).validate([])
        self.assertTrue(result.is_valid)
        
        # Empty object (valid by default)
        result = Schema.object({}).validate({})
        self.assertTrue(result.is_valid)
        
        # Empty array with min_length constraint
        result = Schema.array(Schema.string()).min_length(1).validate([])
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "MIN_LENGTH")

    def test_none_values(self):
        """Test validation with None values"""
        # Required field with None
        result = Schema.string().validate(None)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "REQUIRED")
        
        # Optional field with None
        result = Schema.string().optional().validate(None)
        self.assertTrue(result.is_valid)

    def test_extreme_values(self):
        """Test validation with extreme values"""
        # Very long string
        long_string = "a" * 1000
        result = Schema.string().max_length(100).validate(long_string)
        self.assertFalse(result.is_valid)
        
        # Very large number
        large_number = 999999999999999
        result = Schema.number().max_value(100).validate(large_number)
        self.assertFalse(result.is_valid)

    def test_nested_optional_fields(self):
        """Test deeply nested optional fields"""
        schema = Schema.object({
            'level1': Schema.object({
                'level2': Schema.object({
                    'level3': Schema.string().optional()
                }).optional()
            }).optional()
        })
        
        # All levels present
        data = {'level1': {'level2': {'level3': 'value'}}}
        result = schema.validate(data)
        self.assertTrue(result.is_valid)
        
        # Missing optional levels
        data = {}
        result = schema.validate(data)
        self.assertTrue(result.is_valid)

    def test_circular_references(self):
        """Test handling of potential circular references"""
        # This should not cause infinite recursion
        schema = Schema.object({
            'name': Schema.string(),
            'children': Schema.array(Schema.object({
                'name': Schema.string(),
                'parent': Schema.string().optional()
            })).optional()
        })
        
        data = {
            'name': 'Parent',
            'children': [
                {'name': 'Child1'},
                {'name': 'Child2'}
            ]
        }
        result = schema.validate(data)
        self.assertTrue(result.is_valid)


class TestFieldLevelValidators:
    """Test the field-level specialized validators"""
    
    def test_ip_address_validator_ipv4(self):
        """Test IPv4 address validation"""
        validator = Schema.ip_address(allow_ipv4=True, allow_ipv6=False)
        
        # Valid IPv4 addresses
        assert validator.validate("192.168.1.1").is_valid
        assert validator.validate("10.0.0.1").is_valid
        assert validator.validate("172.16.0.1").is_valid
        assert validator.validate("127.0.0.1").is_valid
        assert validator.validate("255.255.255.255").is_valid
        
        # Invalid IPv4 addresses
        assert not validator.validate("256.1.2.3").is_valid
        assert not validator.validate("1.2.3.256").is_valid
        assert not validator.validate("192.168.1").is_valid
        assert not validator.validate("192.168.1.1.1").is_valid
        assert validator.validate("192.168.001.1").is_valid  # Leading zeros are allowed
        assert not validator.validate("192.168.1.").is_valid  # Trailing dot
    
    def test_ip_address_validator_ipv6(self):
        """Test IPv6 address validation"""
        validator = Schema.ip_address(allow_ipv4=False, allow_ipv6=True)
        
        # Valid IPv6 addresses
        assert validator.validate("2001:0db8:85a3:0000:0000:8a2e:0370:7334").is_valid
        assert validator.validate("2001:db8:85a3::8a2e:370:7334").is_valid
        assert validator.validate("::1").is_valid  # Localhost
        assert validator.validate("fe80::1").is_valid  # Link-local
        assert validator.validate("2001:db8::1").is_valid  # Compressed
        
        # Invalid IPv6 addresses
        assert not validator.validate("2001:0db8:85a3:0000:0000:8a2e:0370").is_valid
        assert not validator.validate("2001:0db8:85a3:0000:0000:8a2e:0370:7334:extra").is_valid
        assert not validator.validate("2001:db8::1::2").is_valid  # Multiple ::
        assert not validator.validate("2001:db8:1").is_valid  # Too short
    
    def test_ip_address_validator_both(self):
        """Test IP address validator allowing both IPv4 and IPv6"""
        validator = Schema.ip_address(allow_ipv4=True, allow_ipv6=True)
        
        # Valid IPv4
        assert validator.validate("192.168.1.1").is_valid
        # Valid IPv6
        assert validator.validate("2001:0db8:85a3:0000:0000:8a2e:0370:7334").is_valid
        # Invalid
        assert not validator.validate("invalid").is_valid
        assert not validator.validate("192.168.1.1:8080").is_valid  # Port number
    
    def test_ip_address_validator_ipv4_only(self):
        """Test IP address validator with IPv4 only"""
        validator = Schema.ip_address(allow_ipv4=True, allow_ipv6=False)
        
        # IPv4 should work
        assert validator.validate("192.168.1.1").is_valid
        # IPv6 should fail
        assert not validator.validate("2001:db8::1").is_valid
    
    def test_phone_number_validator(self):
        """Test phone number validation"""
        validator = Schema.phone_number()
        
        # Valid phone numbers
        assert validator.validate("+1234567890").is_valid
        assert validator.validate("1234567890").is_valid
        assert validator.validate("+1-234-567-8900").is_valid
        assert validator.validate("(123) 456-7890").is_valid
        assert validator.validate("123.456.7890").is_valid
        assert validator.validate("+44 20 7946 0958").is_valid  # UK format
        assert validator.validate("+33 1 42 86 20 00").is_valid  # French format
        
        # Invalid phone numbers
        assert not validator.validate("123").is_valid  # Too short
        assert not validator.validate("1234567890123456").is_valid  # Too long
        assert not validator.validate("abc").is_valid  # Not numeric
        assert not validator.validate("0123456789").is_valid  # Starts with 0
        assert not validator.validate("123-456").is_valid  # Too short after cleaning
    
    def test_phone_number_validator_with_country_code(self):
        """Test phone number validator with specific country code"""
        validator = Schema.phone_number(country_code="+1")
        
        # Should still work the same way
        assert validator.validate("+1234567890").is_valid
        assert validator.validate("1234567890").is_valid
        assert not validator.validate("123").is_valid
    
    def test_custom_validator_bool_return(self):
        """Test custom validator with boolean return"""
        def is_even(value):
            return isinstance(value, int) and value % 2 == 0
        
        validator = Schema.custom(is_even)
        
        assert validator.validate(2).is_valid
        assert validator.validate(4).is_valid
        assert validator.validate(0).is_valid
        assert not validator.validate(3).is_valid
        assert not validator.validate("2").is_valid
        assert not validator.validate(2.5).is_valid
    
    def test_custom_validator_string_return(self):
        """Test custom validator with string return (error message)"""
        def validate_age(value):
            if not isinstance(value, int):
                return "Age must be a number"
            if value < 0:
                return "Age cannot be negative"
            if value > 150:
                return "Age cannot exceed 150"
            return ""  # Empty string means valid
        
        validator = Schema.custom(validate_age)
        
        assert validator.validate(25).is_valid
        assert validator.validate(0).is_valid
        assert validator.validate(150).is_valid
        assert not validator.validate(-5).is_valid
        assert not validator.validate(200).is_valid
        assert not validator.validate("25").is_valid
        assert not validator.validate(25.5).is_valid
    
    def test_custom_validator_tuple_return(self):
        """Test custom validator with tuple return"""
        def validate_password(value):
            if not isinstance(value, str):
                return False, "Password must be a string"
            if len(value) < 8:
                return False, "Password must be at least 8 characters"
            if not any(c.isupper() for c in value):
                return False, "Password must contain uppercase letter"
            if not any(c.isdigit() for c in value):
                return False, "Password must contain a digit"
            return True, ""
        
        validator = Schema.custom(validate_password)
        
        assert validator.validate("StrongPass123").is_valid
        assert not validator.validate("weak").is_valid
        assert not validator.validate("WeakPass").is_valid  # No digit
        assert not validator.validate("strongpass123").is_valid  # No uppercase
        assert not validator.validate(123).is_valid
    
    def test_custom_validator_exception_handling(self):
        """Test custom validator handles exceptions gracefully"""
        def buggy_validator(value):
            raise ValueError("Test exception")
        
        validator = Schema.custom(buggy_validator)
        result = validator.validate("test")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Validation function error" in result.errors[0].message
        assert result.errors[0].code == "VALIDATION_ERROR"
    
    def test_custom_validator_with_custom_message(self):
        """Test custom validator with custom error message"""
        def always_fail(value):
            return False
        
        validator = Schema.custom(always_fail).with_message("Custom failure message")
        result = validator.validate("anything")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].message == "Custom failure message"
    
    def test_custom_validator_optional_field(self):
        """Test custom validator with optional field"""
        def validate_positive(value):
            return isinstance(value, (int, float)) and value > 0
        
        validator = Schema.custom(validate_positive).optional()
        
        # Valid values
        assert validator.validate(5).is_valid
        assert validator.validate(3.14).is_valid
        
        # Invalid values
        assert not validator.validate(-5).is_valid
        assert not validator.validate(0).is_valid
        assert not validator.validate("5").is_valid
        
        # Optional field with None/empty
        assert validator.validate(None).is_valid
        assert validator.validate("").is_valid
    
    def test_field_level_validators_in_complex_schema(self):
        """Test field-level validators within a complex object schema"""
        schema = Schema.object({
            'server': Schema.object({
                'name': Schema.string().min_length(1),
                'ip_address': Schema.ip_address(),
                'port': Schema.number().min_value(1).max_value(65535),
                'contact_phone': Schema.phone_number().optional(),
                'is_active': Schema.boolean(),
                'tags': Schema.array(Schema.string()).min_length(1),
                'custom_field': Schema.custom(lambda x: isinstance(x, str) and len(x) > 3)
            })
        })
        
        # Valid data
        valid_data = {
            'server': {
                'name': 'WebServer01',
                'ip_address': '192.168.1.100',
                'port': 8080,
                'contact_phone': '+1-555-0123',
                'is_active': True,
                'tags': ['web', 'production'],
                'custom_field': 'valid_custom_value'
            }
        }
        
        result = schema.validate(valid_data)
        assert result.is_valid
        
        # Invalid data
        invalid_data = {
            'server': {
                'name': 'WebServer01',
                'ip_address': '256.1.2.3',  # Invalid IP
                'port': 70000,  # Invalid port
                'contact_phone': '123',  # Invalid phone
                'is_active': 'maybe',  # Invalid boolean
                'tags': ['web', 'production'],
                'custom_field': 'abc'  # Too short for custom validator
            }
        }
        
        result = schema.validate(invalid_data)
        assert not result.is_valid
        assert len(result.errors) >= 4  # At least 4 validation errors


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 