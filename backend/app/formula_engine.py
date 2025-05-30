import re
import math # For potentially safe math functions if allowed later

# For a safer eval, one might use a library like 'asteval' or 'numexpr'.
# Since direct eval is risky, we'll try to create a very restricted environment.
# This is still a simplified and potentially unsafe example.
# Production systems should use robust, secure parsing/evaluation libraries.

ALLOWED_OPERATORS = {
    '+': lambda a, b: a + b,
    '-': lambda a, b: a - b,
    '*': lambda a, b: a * b,
    '/': lambda a, b: a / b if b != 0 else float('inf'), # Handle division by zero
}
# Future: Add more functions, e.g., from math module, if deemed safe.
ALLOWED_FUNCTIONS = {
    # "sqrt": math.sqrt, # Example
}
ALLOWED_NAMES = {**{name: func for name, func in ALLOWED_FUNCTIONS.items()},
                 **{konst: getattr(math, konst) for konst in ["pi", "e"] if hasattr(math, konst)}}


def get_field_value_from_map(field_id_str: str, record_values_map: dict, field_defs_map: dict):
    """
    Extracts and converts field value from the record_values_map.
    Assumes field_id_str is like "field_123".
    """
    actual_id = int(field_id_str.split('_')[1])

    value_obj = record_values_map.get(actual_id)
    field_def = field_defs_map.get(actual_id)

    if value_obj is None or field_def is None:
        # Referenced field has no value or definition, treat as None or raise error
        # For now, let's treat as None, which might become 0 for numeric ops or cause type errors
        return None

    # Based on field type, extract the correct value
    # This logic should mirror how values are stored/retrieved
    if field_def.type == 'number' or field_def.type == 'count':
        return value_obj.value_number
    elif field_def.type == 'boolean':
        return float(value_obj.value_boolean) if value_obj.value_boolean is not None else None # Convert boolean to 0/1 for math
    # Add other type conversions if necessary (e.g., date differences)
    # For now, mainly supporting numeric operations.
    # If a text field is referenced, it will likely cause an error in eval if used with arithmetic ops.
    return value_obj.value_text # Fallback, or could be None if not text-based


def evaluate_formula(formula_string: str, record_values_map: dict, field_defs_map: dict) -> any:
    """
    Evaluates a formula string.
    record_values_map: {field_id_int: RecordValue object, ...}
    field_defs_map: {field_id_int: Field object (for type info), ...}
    """
    if not formula_string:
        return None

    # 1. Replace placeholders like {field_123} with their actual values
    def replace_placeholder(match):
        placeholder = match.group(0) # e.g., {field_123}
        field_id_str_token = placeholder.strip('{}') # e.g., field_123

        value = get_field_value_from_map(field_id_str_token, record_values_map, field_defs_map)

        if value is None:
            # If a referenced field has no value, it's problematic for most ops.
            # Could default to 0 for numeric, or raise specific error.
            # For now, returning "None" as string which will likely fail eval safely or be handled by it.
            return "None"

        # Ensure the value is a string representation of a number for safe eval,
        # or if strings are allowed in formulas, ensure proper quoting (not handled here yet).
        # For now, assuming numeric context.
        if isinstance(value, (int, float)):
            return str(value)
        else:
            # Attempt to convert to float if possible (e.g. from string number)
            try:
                return str(float(value))
            except (ValueError, TypeError):
                 # If it's not a number, this basic engine won't handle it well with arithmetic.
                 # Returning it as "None" or raising an error might be options.
                 # This part needs to be more robust if non-numeric fields are used in formulas.
                return "None" # Or raise FormulaError(f"Field {field_id_str_token} has non-numeric value '{value}'")


    # Regex to find placeholders like {field_XXX}
    # Using a simpler {field_id} format as per problem description
    # Formula string will use placeholders like "{field_id_1} + {field_id_2}"
    # The problem states "{field_id_X}", let's use that.
    # For the actual replacement, we need to map "field_id_X" to the actual integer field_id.
    # This example assumes formula_string uses actual IDs like "{123} + {456}"
    # Let's adjust to the prompt's "{field_id_X}" - this means the formula string itself
    # must be created with these symbolic names, or we use a regex that captures the ID.
    # For simplicity, let's assume formula string uses actual IDs: e.g., "{1} + {2}"

    # Simpler placeholder: {ID}, e.g., "{123} + {456}"
    # Modified placeholder replacement to handle missing values by raising an error
    # instead of defaulting to 0, to make missing fields explicit errors.
    def replace_placeholder_value(match):
        field_id_str = match.group(1) # The numeric ID from placeholder {ID}
        value = get_field_value_from_map(f"field_{field_id_str}", record_values_map, field_defs_map)
        if value is None:
            # Raise a specific error that can be caught by the main try-except block
            raise FormulaError(f"Field ID {{{field_id_str}}} not found, has no value, or is not suitable for formula.")
        return str(value) # Ensure it's a string for re.sub

    try:
        processed_formula = re.sub(r"\{(\d+)\}", replace_placeholder_value, formula_string)
    except FormulaError as e: # Catch error from placeholder replacement
        return str(e) # Return the custom error message directly

    # Security: Validate the processed_formula to ensure it only contains allowed characters/operations
    # This is a very basic check, a proper tokenizer/parser is better.
    allowed_chars_pattern = r"^[0-9\.\s\(\)\+\-\*\/]*$" # Allows numbers, dots, spaces, parens, and basic operators
    if not re.match(allowed_chars_pattern, processed_formula):
        # Additionally, check for functions if we allow them
        # For now, strictly arithmetic.
        return "Error: Invalid characters in formula"

    # 2. Evaluate the processed formula string in a restricted environment
    try:
        # WARNING: eval() is dangerous. This is a simplified example.
        # A real implementation should use a safer evaluation library (e.g., asteval)
        # or a custom parser for the specific allowed operations.
        # For this basic step, we are using it with heavy caveats.

        # Create a limited scope for eval
        # No builtins are passed, only allowed names (math constants/functions if any)
        # This still doesn't make eval fully safe from all exploits (e.g., resource exhaustion).
        scope = {"__builtins__": {}}
        # Add any allowed functions/constants to scope here if using them
        # scope.update(ALLOWED_NAMES)

        result = eval(processed_formula, scope, {}) # No locals passed either

        if isinstance(result, (int, float)):
            return result
        else:
            # This case might be hit if eval results in something non-numeric
            # that wasn't caught as a TypeError during evaluation.
            return "Error: Formula result is not a number"

    except ZeroDivisionError:
        return "Error: Division by zero"
    except SyntaxError: # Includes cases where "None" string might cause issues if not handled before
        return "Error: Syntax error in formula"
    except TypeError: # Catch type errors from operations like "10 + 'text'" if not caught by regex
        return "Error: Type error in formula (e.g., mixing text and numbers)"
    except FormulaError as fe: # Catch our custom error from placeholder replacement
        return str(fe)
    except Exception as e:
        # Log the full error for debugging, but return a generic error to user
        print(f"Formula evaluation error: {e} for formula '{processed_formula}'")
        return "Error: Formula evaluation failed"

class FormulaError(Exception): # Custom exception for formula-specific issues
    pass
