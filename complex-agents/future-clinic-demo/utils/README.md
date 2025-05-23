# JSON Schema Utilities

This module provides functions to convert Pydantic models and dataclasses into commented JSON schema descriptions.

## Functions

### `pydantic_to_commented_json_schema(model, indent=2)`

Converts a Pydantic model to a JSON schema with type comments and descriptions.

**Important**: Only uses descriptions explicitly defined in Pydantic `Field()` definitions. Fields without Field descriptions will show only the type comment.

**Parameters:**

- `model`: The Pydantic model class to convert
- `indent`: Number of spaces for indentation (default: 2)

**Example:**

```python
from pydantic import BaseModel, Field
from utils.json_schema import pydantic_to_commented_json_schema

class User(BaseModel):
    name: str = Field(description="User's full name")
    age: int = Field(default=0)
    email: str = ""

schema = pydantic_to_commented_json_schema(User)
print(schema)
```

**Output:**

```json
{
  "name": "" // string - User's full name,
  "age": 0 // integer,
  "email": "" // string
}
```

### `dataclass_to_commented_json_schema(dataclass_type, indent=2)`

Converts a dataclass to a JSON schema with type comments and descriptions.

**Important**: Only uses descriptions explicitly defined in field metadata. Fields without metadata descriptions will show only the type comment.

**Parameters:**

- `dataclass_type`: The dataclass to convert
- `indent`: Number of spaces for indentation (default: 2)

**Example:**

```python
from dataclasses import dataclass, field
from typing import List
from utils.json_schema import dataclass_to_commented_json_schema

@dataclass
class Address:
    street: str = field(default="", metadata={"description": "Street address"})
    city: str = ""  # No description

@dataclass
class User:
    name: str = field(default="", metadata={"description": "User's full name"})
    age: int = 0  # No description
    addresses: List[Address] = field(default_factory=list, metadata={"description": "User addresses"})

schema = dataclass_to_commented_json_schema(User)
print(schema)
```

**Output:**

```json
{
  "name": "" // string - User's full name,
  "age": 0 // integer,
  "addresses": [ // address[] - User addresses
    {
      "street": "" // string - Street address,
      "city": "" // string
    }
  ]
}
```

## Features

- **Consistent behavior**: Both Pydantic and dataclass functions only use explicit descriptions
- **Nested object support**: Automatically handles nested dataclasses and Pydantic models
- **Array handling**: Shows array element types (e.g., `string[]`, `object[]`)
- **Type inference**: Automatically determines appropriate JSON types
- **No auto-generation**: Field names are not converted to descriptions automatically
- **Customizable formatting**: Configurable indentation

## Usage in Medical Forms

This utility is particularly useful for generating schema descriptions for medical forms. To add descriptions to dataclass fields, use the metadata parameter:

```python
from dataclasses import dataclass, field

@dataclass
class SymptomForm:
    chief_complaint: str = field(
        default="",
        metadata={"description": "Primary reason for medical visit"}
    )
    symptoms: List[str] = field(
        default_factory=list,
        metadata={"description": "List of patient's detailed symptoms"}
    )
```

This will generate schemas with proper descriptions that match the format expected by LLM agents for structured data collection.
