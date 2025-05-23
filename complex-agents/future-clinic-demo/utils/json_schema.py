import json
import dataclasses
from typing import Any, Dict, Type, get_origin, get_args, get_type_hints
from pydantic import BaseModel
from pydantic.fields import FieldInfo


def pydantic_to_commented_json_schema(model: Type[BaseModel], indent: int = 2) -> str:
    """
    Convert a Pydantic model to a JSON schema with type comments and descriptions.

    Args:
        model: The Pydantic model class to convert
        indent: Number of spaces for indentation (default: 2)

    Returns:
        A string containing the JSON schema with comments in the format:
        {
          "field_name": "", // type - description
          "array_field": [ // type[] - description
            {
              "nested_field": "" // type - description
            }
          ]
        }
    """
    schema = model.model_json_schema()
    return _convert_schema_to_commented_json(schema, indent)


def _convert_schema_to_commented_json(
    schema: Dict[str, Any], indent: int = 2, level: int = 0
) -> str:
    """
    Recursively convert a JSON schema to commented JSON format.
    """
    if "properties" not in schema:
        return "{}"

    lines = ["{"]
    properties = schema["properties"]
    required_fields = set(schema.get("required", []))

    property_items = list(properties.items())
    for i, (field_name, field_schema) in enumerate(property_items):
        is_last = i == len(property_items) - 1
        line = _format_field(
            field_name, field_schema, required_fields, indent, level + 1
        )
        if not is_last:
            line += ","
        lines.append(line)

    lines.append(" " * (level * indent) + "}")
    return "\n".join(lines)


def _format_field(
    field_name: str,
    field_schema: Dict[str, Any],
    required_fields: set,
    indent: int,
    level: int,
) -> str:
    """
    Format a single field with appropriate type comments and default values.
    """
    base_indent = " " * (level * indent)

    # Determine the type and default value
    field_type = _get_field_type(field_schema)
    default_value = _get_default_value(field_schema, field_name in required_fields)

    # Only use description if it exists in the field schema (from Field description)
    description = field_schema.get("description", "")
    description_part = f" - {description}" if description else ""

    # Handle arrays
    if field_schema.get("type") == "array":
        array_items = field_schema.get("items", {})
        if array_items.get("type") == "object":
            # Array of objects
            nested_schema = _convert_schema_to_commented_json(
                array_items, indent, level + 1
            )
            nested_lines = nested_schema.split("\n")
            nested_content = "\n".join(
                [
                    " " * (indent if i == 0 else 0) + line
                    for i, line in enumerate(nested_lines)
                ]
            )
            return f'{base_indent}"{field_name}": [ // {field_type}{description_part}\n{base_indent}{nested_content}\n{base_indent}]'
        else:
            # Array of primitives
            return f'{base_indent}"{field_name}": {default_value} // {field_type}{description_part}'

    # Handle objects
    elif field_schema.get("type") == "object" or "properties" in field_schema:
        nested_schema = _convert_schema_to_commented_json(field_schema, indent, level)
        return (
            f'{base_indent}"{field_name}": {nested_schema} // object{description_part}'
        )

    # Handle primitives
    else:
        return f'{base_indent}"{field_name}": {default_value} // {field_type}{description_part}'


def _get_field_type(field_schema: Dict[str, Any]) -> str:
    """
    Extract the field type for the comment.
    """
    if field_schema.get("type") == "array":
        items = field_schema.get("items", {})
        if items.get("type") == "object":
            return "object[]"
        elif items.get("type"):
            return f"{items['type']}[]"
        else:
            return "array"
    elif field_schema.get("type") == "object" or "properties" in field_schema:
        return "object"
    elif field_schema.get("type"):
        return field_schema["type"]
    elif "anyOf" in field_schema:
        types = []
        for option in field_schema["anyOf"]:
            if option.get("type"):
                types.append(option["type"])
        return " | ".join(types) if types else "any"
    else:
        return "any"


def _get_default_value(field_schema: Dict[str, Any], is_required: bool) -> str:
    """
    Get the appropriate default value representation for the field.
    """
    # Check if there's a default value in the schema
    if "default" in field_schema:
        default = field_schema["default"]
        if isinstance(default, str):
            return f'"{default}"'
        elif isinstance(default, bool):
            return "true" if default else "false"
        elif default is None:
            return "null"
        elif isinstance(default, (int, float)):
            return str(default)
        elif isinstance(default, list):
            return "[]"
        elif isinstance(default, dict):
            return "{}"
        else:
            return json.dumps(default)

    # Provide type-appropriate defaults based on schema type
    field_type = field_schema.get("type")
    if field_type == "string":
        return '""'
    elif field_type == "number" or field_type == "integer":
        return "0"
    elif field_type == "boolean":
        return "false"
    elif field_type == "array":
        return "[]"
    elif field_type == "object" or "properties" in field_schema:
        return "{}"
    else:
        return '""'


def dataclass_to_commented_json_schema(dataclass_type: Type, indent: int = 2) -> str:
    """
    Convert a dataclass to a JSON schema with type comments and descriptions.
    This is a helper function for dataclasses that follows the same format as Pydantic models.

    Args:
        dataclass_type: The dataclass to convert
        indent: Number of spaces for indentation (default: 2)

    Returns:
        A string containing the JSON schema with comments
    """

    if not dataclasses.is_dataclass(dataclass_type):
        raise ValueError("Input must be a dataclass")

    return _convert_dataclass_to_json(dataclass_type, indent, 0)


def _convert_dataclass_to_json(dataclass_type: Type, indent: int, level: int) -> str:
    """
    Recursively convert a dataclass to commented JSON format.
    """
    fields = dataclasses.fields(dataclass_type)
    type_hints = get_type_hints(dataclass_type)

    lines = ["{"]

    for i, field in enumerate(fields):
        is_last = i == len(fields) - 1
        field_type = type_hints.get(field.name, field.type)

        # Only use description if it exists in field metadata
        description = field.metadata.get("description", "")

        # Format the field
        line = _format_dataclass_field(
            field, field_type, description, indent, level + 1
        )

        if not is_last:
            line += ","
        lines.append(line)

    lines.append(" " * (level * indent) + "}")
    return "\n".join(lines)


def _format_dataclass_field(
    field, field_type: Type, description: str, indent: int, level: int
) -> str:
    """
    Format a dataclass field with appropriate type comments and nested structures.
    """
    base_indent = " " * (level * indent)
    origin = get_origin(field_type)
    args = get_args(field_type)

    # Add description part only if description exists
    description_part = f" - {description}" if description else ""

    # Handle List types
    if origin is list and args:
        element_type = args[0]

        # Check if the list element is a dataclass
        if dataclasses.is_dataclass(element_type):
            # Create nested structure for dataclass arrays
            nested_json = _convert_dataclass_to_json(element_type, indent, level + 1)
            nested_lines = nested_json.split("\n")
            nested_content = "\n".join(
                [
                    " " * (indent if i == 0 else 0) + line
                    for i, line in enumerate(nested_lines)
                ]
            )
            element_name = (
                element_type.__name__.replace("Input", "").replace("Form", "").lower()
            )
            return f'{base_indent}"{field.name}": [ // {element_name}[]{description_part}\n{base_indent}{nested_content}\n{base_indent}]'
        else:
            # Simple array
            element_type_str = _get_type_string(element_type)
            default_val = _get_dataclass_default_value(field, field_type)
            return f'{base_indent}"{field.name}": {default_val} // {element_type_str}[]{description_part}'

    # Handle nested dataclass objects
    elif dataclasses.is_dataclass(field_type):
        nested_json = _convert_dataclass_to_json(field_type, indent, level)
        return f'{base_indent}"{field.name}": {nested_json} // object{description_part}'

    # Handle simple types
    else:
        type_str = _get_type_string(field_type)
        default_val = _get_dataclass_default_value(field, field_type)
        return f'{base_indent}"{field.name}": {default_val} // {type_str}{description_part}'


def _get_type_string(field_type: Type) -> str:
    """
    Convert a Python type to a JSON schema type string.
    """
    origin = get_origin(field_type)
    args = get_args(field_type)

    if origin is list:
        if args:
            element_type = _get_type_string(args[0])
            return f"{element_type}[]"
        return "array"
    elif origin is dict:
        return "object"
    elif field_type is str:
        return "string"
    elif field_type is int:
        return "integer"
    elif field_type is float:
        return "number"
    elif field_type is bool:
        return "boolean"
    else:
        return "string"


def _get_dataclass_default_value(field, field_type: Type) -> str:
    """
    Get the default value for a dataclass field.
    """
    if field.default != dataclasses.MISSING:
        if isinstance(field.default, str):
            return f'"{field.default}"'
        elif isinstance(field.default, bool):
            return "true" if field.default else "false"
        elif field.default is None:
            return "null"
        elif isinstance(field.default, (int, float)):
            return str(field.default)
        else:
            return json.dumps(field.default)
    elif field.default_factory != dataclasses.MISSING:
        # Handle default_factory
        try:
            default_val = field.default_factory()
            if isinstance(default_val, list):
                return "[]"
            elif isinstance(default_val, dict):
                return "{}"
            else:
                return json.dumps(default_val)
        except:
            return '""'

    # Type-based defaults
    origin = get_origin(field_type)
    if origin is list:
        return "[]"
    elif origin is dict:
        return "{}"
    elif field_type is str:
        return '""'
    elif field_type in (int, float):
        return "0"
    elif field_type is bool:
        return "false"
    else:
        return '""'
