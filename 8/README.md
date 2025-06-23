# Python Schema Validation Library

A robust, type-safe validation library built from scratch in Python. This library provides comprehensive validation for primitive types, complex data structures, and nested objects with excellent error handling and developer experience.

## Features

- **Type-Safe Validation**: Full type hints and runtime type checking
- **Primitive Type Validators**: String, Number, Boolean, Date with comprehensive rules
- **Complex Type Support**: Arrays, Objects, Nested structures
- **Enhanced Error Handling**: Structured errors with field paths and error codes
- **Fluent API**: Method chaining for intuitive validation rules
- **Optional Fields**: Support for nullable/optional data
- **Custom Validators**: Email, URL, UUID with built-in patterns
- **Transformation Support**: Built-in data transformation capabilities
- **Comprehensive Documentation**: Extensive inline comments and self-documenting code

## Installation

No external dependencies required! This library uses only Python standard library modules.

```bash
# Clone or download the schema.py file
# The library is self-contained and ready to use
```

## Quick Start

### Basic Usage

```python
from schema import Schema

# Create a simple user validation schema
user_schema = Schema.object({
    'name': Schema.string().min_length(2).max_length(50),
    'email': Schema.email(),
    'age': Schema.number().min_value(0).max_value(150).optional(),
    'isActive': Schema.boolean()
})

# Validate data
user_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30,
    'isActive': True
}

result = user_schema.validate(user_data)

if result.is_valid:
    print("✅ Validation successful!")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error.field}: {error.message}")
```

## Running the Application

### Method 1: Direct Execution

```bash
python schema.py
```

This will run the built-in test cases demonstrating both valid and invalid data validation with comprehensive error reporting.

### Method 2: Import and Use

```python
from schema import Schema, ValidationResult

# Your validation code here
```

## Code Quality and Documentation

The library features extensive inline documentation:

- **Comprehensive Comments**: Every class, method, and complex logic section is documented
- **Self-Documenting Code**: Clear variable names and function signatures
- **Type Annotations**: Full type hints for better IDE support and code understanding
- **Error Context**: Detailed error messages with field paths and error codes
- **Best Practices**: Follows Python conventions and modern coding standards

## Validator Types and Usage

### String Validator

```python
# Basic string validation
name_validator = Schema.string().min_length(2).max_length(50)

# String with pattern matching
email_validator = Schema.string().pattern(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')

# String with allowed values
country_validator = Schema.string().allowed_values(['USA', 'Canada', 'UK'])

# String with trimming
name_validator = Schema.string().trim().min_length(2)

# Case-insensitive validation
status_validator = Schema.string().allowed_values(['active', 'inactive']).case_sensitive(False)
```

### Number Validator

```python
# Basic number validation
age_validator = Schema.number().min_value(0).max_value(150)

# Integer-only validation
count_validator = Schema.number().integer_only().min_value(0)

# Number with allowed values
rating_validator = Schema.number().allowed_values([1, 2, 3, 4, 5])

# Optional number
score_validator = Schema.number().min_value(0).max_value(100).optional()
```

### Boolean Validator

```python
# Basic boolean validation
active_validator = Schema.boolean()

# Boolean with custom truthy/falsy values
custom_bool = Schema.boolean().truthy_values(['yes', 'on', '1']).falsy_values(['no', 'off', '0'])
```

### Date Validator

```python
# Date with specific format
date_validator = Schema.date().format('%Y-%m-%d')

# Date with range validation
from datetime import datetime
birth_date = Schema.date().max_date(datetime.now())

# Date with multiple format support
flexible_date = Schema.date()  # Tries common formats automatically
```

### Array Validator

```python
# Array of strings
tags_validator = Schema.array(Schema.string()).min_length(1).max_length(10)

# Array with unique items
unique_tags = Schema.array(Schema.string()).unique()

# Array of numbers
scores_validator = Schema.array(Schema.number().min_value(0).max_value(100))
```

### Object Validator

```python
# Simple object validation
user_validator = Schema.object({
    'id': Schema.string(),
    'name': Schema.string().min_length(2),
    'email': Schema.email()
})

# Object with optional fields
profile_validator = Schema.object({
    'name': Schema.string().required(),
    'bio': Schema.string().optional(),
    'avatar': Schema.string().optional()
})

# Strict object (no unknown fields allowed)
strict_user = Schema.object({
    'name': Schema.string(),
    'email': Schema.email()
}).strict()
```

### Built-in Specialized Validators

```python
# Email validation
email_validator = Schema.email()

# URL validation
url_validator = Schema.url()

# UUID validation
uuid_validator = Schema.uuid()

# IP address validation (IPv4 and/or IPv6)
ip_validator = Schema.ip_address()

# Phone number validation (international format)
phone_validator = Schema.phone_number()

# Custom validator (with a function)
custom_validator = Schema.custom(lambda x: isinstance(x, int) and x > 0)
```

## Complex Schema Examples

### Nested Object Validation

```python
# Address schema
address_schema = Schema.object({
    'street': Schema.string().min_length(1).max_length(100),
    'city': Schema.string().min_length(1).max_length(50),
    'postalCode': Schema.string().pattern(r'^\d{5}$'),
    'country': Schema.string().allowed_values(['USA', 'Canada', 'UK']),
    'coordinates': Schema.object({
        'lat': Schema.number().min_value(-90).max_value(90),
        'lng': Schema.number().min_value(-180).max_value(180)
    }).optional()
})

# User schema with nested address
user_schema = Schema.object({
    'id': Schema.string(),
    'name': Schema.string().min_length(2).max_length(50).trim(),
    'email': Schema.email(),
    'age': Schema.number().min_value(0).max_value(150).integer_only().optional(),
    'isActive': Schema.boolean(),
    'tags': Schema.array(Schema.string()).min_length(1).max_length(10).unique(),
    'address': address_schema.optional(),
    'createdAt': Schema.date().format('%Y-%m-%d %H:%M:%S').optional()
})
```

### Array of Objects

```python
# Product schema
product_schema = Schema.object({
    'id': Schema.string(),
    'name': Schema.string().min_length(1),
    'price': Schema.number().min_value(0),
    'category': Schema.string().allowed_values(['electronics', 'clothing', 'books'])
})

# Order schema with array of products
order_schema = Schema.object({
    'orderId': Schema.string(),
    'customer': Schema.object({
        'name': Schema.string(),
        'email': Schema.email()
    }),
    'products': Schema.array(product_schema).min_length(1),
    'total': Schema.number().min_value(0),
    'status': Schema.string().allowed_values(['pending', 'confirmed', 'shipped', 'delivered'])
})
```

## Error Handling

The library provides structured error handling with detailed information:

```python
result = user_schema.validate(invalid_data)

if not result.is_valid:
    for error in result.errors:
        print(f"Field: {error.field}")
        print(f"Message: {error.message}")
        print(f"Value: {error.value}")
        print(f"Code: {error.code}")
        print(f"Level: {error.level}")
        print("---")
```

### Error Codes

- `TYPE_ERROR`: Invalid data type
- `MIN_LENGTH`: Value too short
- `MAX_LENGTH`: Value too long
- `MIN_VALUE`: Value below minimum
- `MAX_VALUE`: Value above maximum
- `PATTERN_MISMATCH`: Pattern validation failed
- `INVALID_VALUE`: Value not in allowed list
- `REQUIRED`: Required field missing
- `DUPLICATE_ITEM`: Duplicate item in array
- `UNKNOWN_FIELDS`: Unknown fields in strict mode
- `DATE_FORMAT_ERROR`: Invalid date format
- `TRANSFORM_ERROR`: Data transformation failed

## Advanced Features

### Custom Error Messages

```python
validator = Schema.string().min_length(5).with_message("Name must be at least 5 characters")
```

### Data Transformation

```python
# Transform string to uppercase
upper_validator = Schema.string().transform(str.upper)

# Transform number to integer
int_validator = Schema.number().transform(int)
```

### Validation Levels

The library supports different validation levels:

```python
# Errors (default) - validation fails
# Warnings - validation continues but warns
# Info - informational messages
```

## Performance Considerations

- **Type Checking**: Uses `isinstance()` for efficient runtime type checking
- **Lazy Evaluation**: Validators are configured once and reused
- **Early Exit**: Validation stops on first error (configurable)
- **Memory Efficient**: Minimal object creation during validation

## Best Practices

1. **Define Schemas Once**: Create validator instances once and reuse them
2. **Use Type Hints**: Leverage the library's type hints for better code quality
3. **Handle Errors Gracefully**: Always check `result.is_valid` before proceeding
4. **Use Field Paths**: Error messages include field paths for easy debugging
5. **Validate Early**: Validate data as close to the source as possible
6. **Read the Comments**: The code is extensively documented with inline comments

## Testing and Coverage

The library includes comprehensive unit tests with **81% test coverage**:

```bash
# Run tests
pytest test_schema.py -v

# Run with coverage
pytest --cov=schema --cov-report=term test_schema.py
```

Test coverage includes:
- All validator types (String, Number, Boolean, Date, Array, Object)
- Valid and invalid data scenarios
- Edge cases and boundary conditions
- Complex nested schemas
- Error handling and custom messages
- Data transformations

## Example Application

```python
from schema import Schema

def validate_user_registration(data):
    """Validate user registration data"""
    
    registration_schema = Schema.object({
        'username': Schema.string().min_length(3).max_length(20).pattern(r'^[a-zA-Z0-9_]+$'),
        'email': Schema.email(),
        'password': Schema.string().min_length(8).pattern(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]'),
        'confirmPassword': Schema.string(),
        'age': Schema.number().min_value(13).max_value(120).integer_only().optional(),
        'termsAccepted': Schema.boolean()
    })
    
    result = registration_schema.validate(data)
    
    # Custom validation: password confirmation
    if result.is_valid and data.get('password') != data.get('confirmPassword'):
        result.add_error('confirmPassword', 'Passwords do not match', data.get('confirmPassword'), 'PASSWORD_MISMATCH')
    
    return result

# Usage
user_data = {
    'username': 'john_doe',
    'email': 'john@example.com',
    'password': 'SecurePass123',
    'confirmPassword': 'SecurePass123',
    'age': 25,
    'termsAccepted': True
}

validation_result = validate_user_registration(user_data)

if validation_result.is_valid:
    print("✅ Registration data is valid!")
else:
    print("❌ Registration validation failed:")
    for error in validation_result.errors:
        print(f"  - {error.field}: {error.message}")
```

## Contributing

This library is designed to be extensible. You can easily add new validator types by extending the base `Validator` class:

```python
class CustomValidator(Validator[YourType]):
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        # Your validation logic here
        pass
```

The codebase is well-documented with inline comments, making it easy to understand and extend.

## License

This library is provided as-is for educational and development purposes.

## Field-level Validators

Field-level validators can be used to validate individual values outside of object schemas, e.g.:

```python
result = Schema.ip_address().validate('192.168.1.1')
if result.is_valid:
    print('Valid IP!')
else:
    print('Invalid IP:', result.errors)
``` 