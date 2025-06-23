import re
from typing import Dict, List, Any, Optional, Union, TypeVar, Generic, Callable, Type, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Type variable for generic validators
T = TypeVar('T')
U = TypeVar('U')

class ValidationLevel(Enum):
    """Validation severity levels for different types of validation messages"""
    ERROR = "error"      # Validation fails
    WARNING = "warning"  # Validation continues but warns
    INFO = "info"        # Informational messages

@dataclass
class ValidationError:
    """Individual validation error with context and metadata"""
    field: str                    # Field path where error occurred
    message: str                  # Human-readable error message
    value: Any                    # The value that failed validation
    level: ValidationLevel = ValidationLevel.ERROR  # Error severity level
    code: Optional[str] = None    # Machine-readable error code

@dataclass
class ValidationResult:
    """Result of a validation operation with enhanced error handling"""
    is_valid: bool                # Whether validation passed
    errors: List[ValidationError] = None      # List of validation errors
    warnings: List[ValidationError] = None    # List of validation warnings
    data: Optional[Dict[str, Any]] = None     # Optional validated data
    
    def __post_init__(self):
        """Initialize empty lists if None to avoid mutable default arguments"""
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def add_error(self, field: str, message: str, value: Any, code: Optional[str] = None):
        """Add an error to the validation result and mark as invalid"""
        self.errors.append(ValidationError(field, message, value, ValidationLevel.ERROR, code))
        self.is_valid = False
    
    def add_warning(self, field: str, message: str, value: Any, code: Optional[str] = None):
        """Add a warning to the validation result (doesn't fail validation)"""
        self.warnings.append(ValidationError(field, message, value, ValidationLevel.WARNING, code))

class Validator(ABC, Generic[T]):
    """Base validator class with enhanced type safety and developer support"""
    
    def __init__(self):
        """Initialize base validator with common attributes"""
        self._custom_message: Optional[str] = None    # Custom error message
        self._field_name: Optional[str] = None        # Current field name
        self._required: bool = True                   # Whether field is required
        self._transform: Optional[Callable[[Any], T]] = None  # Data transformation function
    
    @abstractmethod
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a value and return a ValidationResult - must be implemented by subclasses"""
        pass
    
    def with_message(self, message: str) -> 'Validator[T]':
        """Set a custom error message for this validator"""
        self._custom_message = message
        return self  # Return self for method chaining
    
    def required(self, required: bool = True) -> 'Validator[T]':
        """Set whether this field is required (default: True)"""
        self._required = required
        return self
    
    def optional(self) -> 'Validator[T]':
        """Make this field optional (alias for required(False))"""
        return self.required(False)
    
    def transform(self, transform_func: Callable[[Any], T]) -> 'Validator[T]':
        """Add a transformation function to the validator"""
        self._transform = transform_func
        return self
    
    def _handle_optional(self, value: Any, field_name: str) -> Optional[ValidationResult]:
        """Handle optional field validation - returns None if validation should continue"""
        # Check if value is None or empty string
        if value is None or value == "":
            if not self._required:
                # Field is optional and value is None/empty - validation passes
                return ValidationResult(True)
            else:
                # Field is required but value is None/empty - validation fails
                result = ValidationResult(False)
                result.add_error(field_name, self._custom_message or f"Field '{field_name}' is required", value, "REQUIRED")
                return result
        return None  # Continue with normal validation

class StringValidator(Validator[str]):
    """Enhanced string validator with comprehensive validation rules"""
    
    def __init__(self):
        """Initialize string validator with all validation options"""
        super().__init__()
        self._min_length: Optional[int] = None        # Minimum string length
        self._max_length: Optional[int] = None        # Maximum string length
        self._pattern: Optional[str] = None           # Regex pattern to match
        self._allowed_values: Optional[List[str]] = None  # List of allowed values
        self._trim: bool = False                      # Whether to trim whitespace
        self._case_sensitive: bool = True             # Case sensitivity for allowed values
    
    def min_length(self, length: int) -> 'StringValidator':
        """Set minimum length requirement for the string"""
        self._min_length = length
        return self
    
    def max_length(self, length: int) -> 'StringValidator':
        """Set maximum length requirement for the string"""
        self._max_length = length
        return self
    
    def pattern(self, regex: str) -> 'StringValidator':
        """Set regex pattern requirement for the string"""
        self._pattern = regex
        return self
    
    def allowed_values(self, values: List[str]) -> 'StringValidator':
        """Set list of allowed values for the string"""
        self._allowed_values = values
        return self
    
    def trim(self, trim: bool = True) -> 'StringValidator':
        """Enable/disable string trimming (removes leading/trailing whitespace)"""
        self._trim = trim
        return self
    
    def case_sensitive(self, case_sensitive: bool = True) -> 'StringValidator':
        """Set case sensitivity for allowed values validation"""
        self._case_sensitive = case_sensitive
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a string value against all configured rules"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking - ensure value is a string
        if not isinstance(value, str):
            result.add_error(field_name, self._custom_message or "Value must be a string", value, "TYPE_ERROR")
            return result
        
        # Apply data transformation if configured
        if self._transform:
            try:
                value = self._transform(value)
            except Exception as e:
                result.add_error(field_name, f"Transformation failed: {str(e)}", value, "TRANSFORM_ERROR")
                return result
        
        # Trim whitespace if enabled
        if self._trim:
            value = value.strip()
        
        # Length validation - check minimum length
        if self._min_length is not None and len(value) < self._min_length:
            result.add_error(field_name, f"String must be at least {self._min_length} characters long", value, "MIN_LENGTH")
        
        # Length validation - check maximum length
        if self._max_length is not None and len(value) > self._max_length:
            result.add_error(field_name, f"String must be at most {self._max_length} characters long", value, "MAX_LENGTH")
        
        # Pattern validation - check regex match
        if self._pattern is not None and not re.match(self._pattern, value):
            result.add_error(field_name, f"String must match pattern: {self._pattern}", value, "PATTERN_MISMATCH")
        
        # Allowed values validation - check if value is in allowed list
        if self._allowed_values is not None:
            # Handle case sensitivity for comparison
            check_value = value if self._case_sensitive else value.lower()
            check_values = self._allowed_values if self._case_sensitive else [v.lower() for v in self._allowed_values]
            if check_value not in check_values:
                result.add_error(field_name, f"Value must be one of: {', '.join(self._allowed_values)}", value, "INVALID_VALUE")
        
        return result

class NumberValidator(Validator[Union[int, float]]):
    """Enhanced number validator with comprehensive validation rules"""
    
    def __init__(self):
        """Initialize number validator with all validation options"""
        super().__init__()
        self._min_value: Optional[Union[int, float]] = None  # Minimum numeric value
        self._max_value: Optional[Union[int, float]] = None  # Maximum numeric value
        self._integer_only: bool = False                     # Whether only integers are allowed
        self._allowed_values: Optional[List[Union[int, float]]] = None  # List of allowed values
    
    def min_value(self, value: Union[int, float]) -> 'NumberValidator':
        """Set minimum value requirement for the number"""
        self._min_value = value
        return self
    
    def max_value(self, value: Union[int, float]) -> 'NumberValidator':
        """Set maximum value requirement for the number"""
        self._max_value = value
        return self
    
    def integer_only(self, integer_only: bool = True) -> 'NumberValidator':
        """Set whether only integers are allowed (no floats)"""
        self._integer_only = integer_only
        return self
    
    def allowed_values(self, values: List[Union[int, float]]) -> 'NumberValidator':
        """Set list of allowed values for the number"""
        self._allowed_values = values
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a numeric value against all configured rules"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking - ensure value is a number (int or float) but not boolean
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            result.add_error(field_name, self._custom_message or "Value must be a number", value, "TYPE_ERROR")
            return result
        
        # Apply data transformation if configured
        if self._transform:
            try:
                value = self._transform(value)
            except Exception as e:
                result.add_error(field_name, f"Transformation failed: {str(e)}", value, "TRANSFORM_ERROR")
                return result
        
        # Integer-only validation - check if float is provided when only integers allowed
        if self._integer_only and not isinstance(value, int):
            result.add_error(field_name, "Value must be an integer", value, "INTEGER_REQUIRED")
        
        # Range validation - check minimum value
        if self._min_value is not None and value < self._min_value:
            result.add_error(field_name, f"Number must be at least {self._min_value}", value, "MIN_VALUE")
        
        # Range validation - check maximum value
        if self._max_value is not None and value > self._max_value:
            result.add_error(field_name, f"Number must be at most {self._max_value}", value, "MAX_VALUE")
        
        # Allowed values validation - check if value is in allowed list
        if self._allowed_values is not None and value not in self._allowed_values:
            result.add_error(field_name, f"Value must be one of: {', '.join(map(str, self._allowed_values))}", value, "INVALID_VALUE")
        
        return result

class BooleanValidator(Validator[bool]):
    """Enhanced boolean validator with transformation support"""
    
    def __init__(self):
        """Initialize boolean validator with truthy/falsy value lists"""
        super().__init__()
        # Default truthy values that can be converted to True
        self._truthy_values: List[Any] = [True, "true", "1", 1, "yes", "on"]
        # Default falsy values that can be converted to False
        self._falsy_values: List[Any] = [False, "false", "0", 0, "no", "off", ""]
    
    def truthy_values(self, values: List[Any]) -> 'BooleanValidator':
        """Set custom truthy values that should be treated as True"""
        self._truthy_values = values
        return self
    
    def falsy_values(self, values: List[Any]) -> 'BooleanValidator':
        """Set custom falsy values that should be treated as False"""
        self._falsy_values = values
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a boolean value or convertible value"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Check if value is already a boolean
        if isinstance(value, bool):
            return result
        
        # Try to convert string/number to boolean using truthy/falsy lists
        if value in self._truthy_values:
            return result
        elif value in self._falsy_values:
            return result
        else:
            # Value cannot be converted to boolean
            result.add_error(field_name, self._custom_message or "Value must be a boolean or convertible to boolean", value, "TYPE_ERROR")
            return result

class DateValidator(Validator[datetime]):
    """Enhanced date validator with format support"""
    
    def __init__(self):
        """Initialize date validator with format and range options"""
        super().__init__()
        self._format: Optional[str] = None            # Expected date format string
        self._min_date: Optional[datetime] = None     # Minimum allowed date
        self._max_date: Optional[datetime] = None     # Maximum allowed date
    
    def format(self, date_format: str) -> 'DateValidator':
        """Set expected date format for string parsing"""
        self._format = date_format
        return self
    
    def min_date(self, date: datetime) -> 'DateValidator':
        """Set minimum allowed date"""
        self._min_date = date
        return self
    
    def max_date(self, date: datetime) -> 'DateValidator':
        """Set maximum allowed date"""
        self._max_date = date
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a date value (datetime object or date string)"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # If already a datetime object, use it directly
        if isinstance(value, datetime):
            parsed_date = value
        elif isinstance(value, str):
            # Try to parse string as date
            try:
                if self._format:
                    # Use specified format
                    parsed_date = datetime.strptime(value, self._format)
                else:
                    # Try common date formats automatically
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%m/%d/%Y']:
                        try:
                            parsed_date = datetime.strptime(value, fmt)
                            break
                        except ValueError:
                            continue
                    else:
                        # No format matched
                        result.add_error(field_name, "Invalid date format", value, "DATE_FORMAT_ERROR")
                        return result
            except ValueError:
                # Date parsing failed
                result.add_error(field_name, "Invalid date format", value, "DATE_FORMAT_ERROR")
                return result
        else:
            # Invalid type
            result.add_error(field_name, self._custom_message or "Value must be a date string or datetime object", value, "TYPE_ERROR")
            return result
        
        # Date range validation - check minimum date
        if self._min_date is not None and parsed_date < self._min_date:
            result.add_error(field_name, f"Date must be after {self._min_date.strftime('%Y-%m-%d')}", value, "MIN_DATE")
        
        # Date range validation - check maximum date
        if self._max_date is not None and parsed_date > self._max_date:
            result.add_error(field_name, f"Date must be before {self._max_date.strftime('%Y-%m-%d')}", value, "MAX_DATE")
        
        return result

class ObjectValidator(Validator[Dict[str, Any]]):
    """Enhanced object validator with strict mode and unknown field handling"""
    
    def __init__(self, schema: Dict[str, Validator]):
        """Initialize object validator with field schema"""
        super().__init__()
        self._schema = schema                         # Schema defining field validators
        self._strict: bool = False                    # Whether to allow unknown fields
        self._allow_unknown: bool = True              # Whether unknown fields are allowed
    
    def strict(self, strict: bool = True) -> 'ObjectValidator':
        """Set strict mode (no unknown fields allowed)"""
        self._strict = strict
        return self
    
    def allow_unknown(self, allow: bool = True) -> 'ObjectValidator':
        """Set whether unknown fields are allowed"""
        self._allow_unknown = allow
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate an object against the defined schema"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking - ensure value is a dictionary but not a list
        if not isinstance(value, dict):
            result.add_error(field_name, self._custom_message or "Value must be an object", value, "TYPE_ERROR")
            return result
        
        # Check for unknown fields in strict mode
        if self._strict:
            unknown_fields = set(value.keys()) - set(self._schema.keys())
            if unknown_fields:
                result.add_error(field_name, f"Unknown fields not allowed: {', '.join(unknown_fields)}", value, "UNKNOWN_FIELDS")
        
        # Validate each field in the schema
        for schema_field_name, validator in self._schema.items():
            # Build field path for nested validation
            current_field_name = f"{field_name}.{schema_field_name}" if field_name else schema_field_name
            
            if schema_field_name in value:
                # Field exists - validate it
                field_result = validator.validate(value[schema_field_name], current_field_name)
                if not field_result.is_valid:
                    # Add all errors from field validation
                    result.errors.extend(field_result.errors)
                    result.is_valid = False
                # Add all warnings from field validation
                result.warnings.extend(field_result.warnings)
            elif hasattr(validator, '_required') and validator._required:
                # Field is required but missing
                result.add_error(current_field_name, f"Missing required field: {schema_field_name}", None, "MISSING_FIELD")
        
        return result

class ArrayValidator(Validator[List[T]]):
    """Enhanced array validator with length constraints and unique items"""
    
    def __init__(self, item_validator: Validator[T]):
        """Initialize array validator with item validator"""
        super().__init__()
        self._item_validator = item_validator         # Validator for array items
        self._min_length: Optional[int] = None        # Minimum array length
        self._max_length: Optional[int] = None        # Maximum array length
        self._unique: bool = False                    # Whether items must be unique
    
    def min_length(self, length: int) -> 'ArrayValidator[T]':
        """Set minimum array length requirement"""
        self._min_length = length
        return self
    
    def max_length(self, length: int) -> 'ArrayValidator[T]':
        """Set maximum array length requirement"""
        self._max_length = length
        return self
    
    def unique(self, unique: bool = True) -> 'ArrayValidator[T]':
        """Set whether array items must be unique"""
        self._unique = unique
        return self
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate an array against all configured rules"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking - ensure value is a list
        if not isinstance(value, list):
            result.add_error(field_name, self._custom_message or "Value must be an array", value, "TYPE_ERROR")
            return result
        
        # Length validation - check minimum length
        if self._min_length is not None and len(value) < self._min_length:
            result.add_error(field_name, f"Array must have at least {self._min_length} items", value, "MIN_LENGTH")
        
        # Length validation - check maximum length
        if self._max_length is not None and len(value) > self._max_length:
            result.add_error(field_name, f"Array must have at most {self._max_length} items", value, "MAX_LENGTH")
        
        # Unique items validation - check for duplicates
        if self._unique:
            seen = set()
            for i, item in enumerate(value):
                if item in seen:
                    result.add_error(field_name, f"Duplicate item at index {i}", item, "DUPLICATE_ITEM")
                seen.add(item)
        
        # Validate each item in the array
        for i, item in enumerate(value):
            # Build field path for item validation
            item_field_name = f"{field_name}[{i}]" if field_name else f"[{i}]"
            item_result = self._item_validator.validate(item, item_field_name)
            if not item_result.is_valid:
                # Add all errors from item validation
                result.errors.extend(item_result.errors)
                result.is_valid = False
            # Add all warnings from item validation
            result.warnings.extend(item_result.warnings)
        
        return result

class IPAddressValidator(Validator[str]):
    """Validator for IP addresses (IPv4 and IPv6)"""
    
    def __init__(self, allow_ipv4: bool = True, allow_ipv6: bool = True):
        """Initialize IP address validator"""
        super().__init__()
        self._allow_ipv4 = allow_ipv4
        self._allow_ipv6 = allow_ipv6
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate an IP address"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking
        if not isinstance(value, str):
            result.add_error(field_name, "Value must be a string", value, "TYPE_ERROR")
            return result
        
        # IPv4 validation
        if self._allow_ipv4:
            ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
            if re.match(ipv4_pattern, value):
                return result
        
        # IPv6 validation
        if self._allow_ipv6:
            # Simpler approach: check basic IPv6 structure and validate with ipaddress module
            try:
                import ipaddress
                ipaddress.IPv6Address(value)
                return result
            except (ImportError, ValueError):
                # Fallback to basic pattern if ipaddress module not available
                ipv6_pattern = r'^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$|^(?:[0-9a-fA-F]{1,4}:){1,7}:$|^:(?::[0-9a-fA-F]{1,4}){1,7}$|^::$'
                if re.match(ipv6_pattern, value):
                    return result
        
        # If we get here, it's not a valid IP address
        allowed_types = []
        if self._allow_ipv4:
            allowed_types.append("IPv4")
        if self._allow_ipv6:
            allowed_types.append("IPv6")
        
        result.add_error(field_name, f"Value must be a valid {' or '.join(allowed_types)} address", value, "INVALID_IP")
        return result

class PhoneNumberValidator(Validator[str]):
    """Validator for phone numbers with international format support"""
    
    def __init__(self, country_code: Optional[str] = None):
        """Initialize phone number validator"""
        super().__init__()
        self._country_code = country_code
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate a phone number"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        # Type checking
        if not isinstance(value, str):
            result.add_error(field_name, "Value must be a string", value, "TYPE_ERROR")
            return result
        
        # Remove common separators and spaces
        cleaned = re.sub(r'[\s\-\(\)\.]', '', value)
        
        # Basic phone number pattern (7-15 digits, optionally starting with +)
        phone_pattern = r'^\+?[1-9]\d{6,14}$'
        if not re.match(phone_pattern, cleaned):
            result.add_error(field_name, "Invalid phone number format", value, "INVALID_PHONE")
        
        return result

class CustomValidator(Validator[Any]):
    """Validator that uses a custom validation function"""
    
    def __init__(self, validation_func: Callable[[Any], Union[bool, str, Tuple[bool, str]]]):
        """Initialize custom validator with validation function
        
        Args:
            validation_func: Function that takes a value and returns:
                - bool: True if valid, False if invalid
                - str: Error message if invalid, empty string if valid
                - Tuple[bool, str]: (is_valid, error_message)
        """
        super().__init__()
        self._validation_func = validation_func
    
    def validate(self, value: Any, field_name: str = "") -> ValidationResult:
        """Validate using custom function"""
        # Handle optional fields first
        optional_result = self._handle_optional(value, field_name)
        if optional_result is not None:
            return optional_result
        
        result = ValidationResult(True)
        
        try:
            validation_result = self._validation_func(value)
            
            if isinstance(validation_result, bool):
                if not validation_result:
                    result.add_error(field_name, self._custom_message or "Custom validation failed", value, "CUSTOM_VALIDATION")
            elif isinstance(validation_result, str):
                if validation_result:  # Non-empty string means error
                    result.add_error(field_name, validation_result, value, "CUSTOM_VALIDATION")
            elif isinstance(validation_result, tuple) and len(validation_result) == 2:
                is_valid, error_message = validation_result
                if not is_valid:
                    result.add_error(field_name, error_message or "Custom validation failed", value, "CUSTOM_VALIDATION")
            else:
                result.add_error(field_name, "Invalid validation function return type", value, "VALIDATION_ERROR")
                
        except Exception as e:
            result.add_error(field_name, f"Validation function error: {str(e)}", value, "VALIDATION_ERROR")
        
        return result

class Schema:
    """Enhanced Schema Builder with additional validator types"""
    
    @staticmethod
    def string() -> StringValidator:
        """Create a string validator"""
        return StringValidator()
    
    @staticmethod
    def number() -> NumberValidator:
        """Create a number validator"""
        return NumberValidator()
    
    @staticmethod
    def boolean() -> BooleanValidator:
        """Create a boolean validator"""
        return BooleanValidator()
    
    @staticmethod
    def date() -> DateValidator:
        """Create a date validator"""
        return DateValidator()
    
    @staticmethod
    def object(schema: Dict[str, Validator]) -> ObjectValidator:
        """Create an object validator with field schema"""
        return ObjectValidator(schema)
    
    @staticmethod
    def array(item_validator: Validator[T]) -> ArrayValidator[T]:
        """Create an array validator with item validator"""
        return ArrayValidator(item_validator)
    
    @staticmethod
    def email() -> StringValidator:
        """Create an email validator with built-in email pattern"""
        return StringValidator().pattern(r'^[^\s@]+@[^\s@]+\.[^\s@]+$').with_message("Invalid email format")
    
    @staticmethod
    def url() -> StringValidator:
        """Create a URL validator with built-in URL pattern"""
        return StringValidator().pattern(r'^https?://.+').with_message("Invalid URL format")
    
    @staticmethod
    def uuid() -> StringValidator:
        """Create a UUID validator with built-in UUID pattern"""
        return StringValidator().pattern(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$').with_message("Invalid UUID format")
    
    @staticmethod
    def ip_address(allow_ipv4: bool = True, allow_ipv6: bool = True) -> IPAddressValidator:
        """Create an IP address validator"""
        return IPAddressValidator(allow_ipv4, allow_ipv6)
    
    @staticmethod
    def phone_number(country_code: Optional[str] = None) -> PhoneNumberValidator:
        """Create a phone number validator"""
        return PhoneNumberValidator(country_code)
    
    @staticmethod
    def custom(validation_func: Callable[[Any], Union[bool, str, Tuple[bool, str]]]) -> CustomValidator:
        """Create a custom validator with a validation function"""
        return CustomValidator(validation_func)


# Enhanced schema examples demonstrating complex validation scenarios
address_schema = Schema.object({
    'street': Schema.string().min_length(1).max_length(100),  # Street address with length constraints
    'city': Schema.string().min_length(1).max_length(50),     # City name with length constraints
    'postalCode': Schema.string().pattern(r'^\d{5}$').with_message('Postal code must be 5 digits'),  # 5-digit postal code
    'country': Schema.string().allowed_values(['USA', 'Canada', 'UK', 'Germany', 'France']),  # Allowed countries
    'coordinates': Schema.object({  # Optional nested coordinates object
        'lat': Schema.number().min_value(-90).max_value(90),   # Latitude range
        'lng': Schema.number().min_value(-180).max_value(180)  # Longitude range
    }).optional()
})

user_schema = Schema.object({
    'id': Schema.string().with_message('ID must be a string'),  # User ID
    'name': Schema.string().min_length(2).max_length(50).trim(),  # Name with trimming
    'email': Schema.email(),  # Email validation
    'age': Schema.number().min_value(0).max_value(150).integer_only().optional(),  # Optional age
    'isActive': Schema.boolean(),  # Active status
    'tags': Schema.array(Schema.string()).min_length(1).max_length(10).unique(),  # Unique tags
    'address': address_schema.optional(),  # Optional address
    'metadata': Schema.object({}).optional(),  # Optional metadata object
    'createdAt': Schema.date().format('%Y-%m-%d %H:%M:%S').optional()  # Optional creation date
})

if __name__ == "__main__":
    # Test with valid data demonstrating all validation features
    user_data = {
        'id': "12345",
        'name': "  John Doe  ",  # Will be trimmed
        'email': "john@example.com",
        'age': 30,
        'isActive': True,
        'tags': ["developer", "designer"],
        'address': {
            'street': "123 Main St",
            'city': "Anytown",
            'postalCode': "12345",
            'country': "USA",
            'coordinates': {
                'lat': 40.7128,
                'lng': -74.0060
            }
        },
        'createdAt': "2024-01-15 10:30:00"
    }
    
    print("--- Testing enhanced valid data ---")
    result = user_schema.validate(user_data)
    
    if result.is_valid:
        print("✅ Validation successful!")
        if result.warnings:
            print("⚠️  Warnings:")
            for warning in result.warnings:
                print(f"  - {warning.field}: {warning.message}")
    else:
        print("❌ Validation failed:")
        for error in result.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    # Test with invalid data demonstrating error handling
    invalid_data = {
        'id': 123,  # Should be string
        'name': "A",  # Too short
        'email': "invalid-email",  # Invalid email
        'age': -5,  # Negative age
        'isActive': "maybe",  # This would generate a boolean error
        'tags': ["developer", 123],  # Mixed types in array (string and number)
        'address': {
            'street': "123 Main St",
            'city': "Anytown",
            'postalCode': "123",  # Invalid postal code
            'country': "InvalidCountry",  # Not in allowed values
            'coordinates': {
                'lat': 200,  # Invalid latitude
                'lng': -200  # Invalid longitude
            }
        }
    }
    
    print("\n--- Testing enhanced invalid data ---")
    invalid_result = user_schema.validate(invalid_data)
    
    if invalid_result.is_valid:
        print("✅ Validation successful!")
    else:
        print("❌ Validation failed:")
        for error in invalid_result.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    # Test field-level validators
    print("\n--- Testing field-level validators ---")
    
    # IP Address validation
    ip_validator = Schema.ip_address()
    ip_result1 = ip_validator.validate('192.168.1.1')
    ip_result2 = ip_validator.validate('256.1.2.3')
    ip_result3 = ip_validator.validate('2001:db8::1')
    
    print(f"IP '192.168.1.1': {'✅' if ip_result1.is_valid else '❌'}")
    if not ip_result1.is_valid:
        for error in ip_result1.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    print(f"IP '256.1.2.3': {'✅' if ip_result2.is_valid else '❌'}")
    if not ip_result2.is_valid:
        for error in ip_result2.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    print(f"IPv6 '2001:db8::1': {'✅' if ip_result3.is_valid else '❌'}")
    if not ip_result3.is_valid:
        for error in ip_result3.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    # Phone number validation
    phone_validator = Schema.phone_number()
    phone_result1 = phone_validator.validate('+1-234-567-8900')
    phone_result2 = phone_validator.validate('123')
    
    print(f"Phone '+1-234-567-8900': {'✅' if phone_result1.is_valid else '❌'}")
    if not phone_result1.is_valid:
        for error in phone_result1.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    print(f"Phone '123': {'✅' if phone_result2.is_valid else '❌'}")
    if not phone_result2.is_valid:
        for error in phone_result2.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    # Custom validator
    def is_even(value):
        return isinstance(value, int) and value % 2 == 0
    
    even_validator = Schema.custom(is_even)
    even_result1 = even_validator.validate(4)
    even_result2 = even_validator.validate(3)
    
    print(f"Even number 4: {'✅' if even_result1.is_valid else '❌'}")
    if not even_result1.is_valid:
        for error in even_result1.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    print(f"Even number 3: {'✅' if even_result2.is_valid else '❌'}")
    if not even_result2.is_valid:
        for error in even_result2.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})")
    
    # Complex schema with field-level validators
    network_device_schema = Schema.object({
        'name': Schema.string().min_length(1).max_length(50),
        'ip_address': Schema.ip_address(allow_ipv4=True, allow_ipv6=True),
        'phone': Schema.phone_number().optional(),
        'port_count': Schema.custom(lambda x: isinstance(x, int) and 1 <= x <= 48).with_message("Port count must be between 1 and 48")
    })
    
    device_data = {
        'name': 'Router-01',
        'ip_address': '192.168.1.1',
        'phone': '+1-555-0123',
        'port_count': 24
    }
    
    print("\n--- Testing network device schema ---")
    device_result = network_device_schema.validate(device_data)
    
    if device_result.is_valid:
        print("✅ Network device validation successful!")
    else:
        print("❌ Network device validation failed:")
        for error in device_result.errors:
            print(f"  - {error.field}: {error.message} (code: {error.code})") 