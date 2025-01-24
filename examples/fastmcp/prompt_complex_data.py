"""Enhanced Smart client for MCP Servers with example model discovery."""
import asyncio
import json
import sys
from pydantic import BaseModel, Field, create_model
from typing import Any, Dict, Type, get_type_hints, List, Optional
import traceback

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def generate_example_input(model: Type[BaseModel]) -> str:
    """Generate example input data based on a Pydantic model's structure."""
    def generate_field_example(field_type: Any, field_name: str) -> Any:
        if field_type == str:
            return f"<string: {field_name}>"
        elif field_type == int:
            return f"<integer: {field_name}>"
        elif field_type == float:
            return f"<float: {field_name}>"
        elif field_type == bool:
            return f"<boolean: {field_name}>"
        elif hasattr(field_type, "__origin__"):
            origin = field_type.__origin__
            if origin == list:
                inner_type = field_type.__args__[0]
                return [generate_field_example(inner_type, f"{field_name} item")]
            elif origin == dict:
                key_type, value_type = field_type.__args__
                return {
                    generate_field_example(key_type, f"{field_name} key"):
                        generate_field_example(value_type, f"{field_name} value")
                }
        return f"<any: {field_name}>"

    example_data = {}
    for field_name, field_info in model.model_fields.items():
        field_type = get_type_hints(model).get(field_name, field_info.annotation)
        example_data[field_name] = generate_field_example(field_type, field_name)

    return json.dumps(example_data, indent=4)

def print_pydantic_model(model: Type[BaseModel]) -> None:
    """Prints a Pydantic model representation."""
    model_name = model.__name__
    print(f"class {model_name}(BaseModel):")
    for field_name, field_info in model.model_fields.items():
        field_type = get_type_hints(model).get(field_name, field_info.annotation)
        field_description = field_info.description or "No description provided"
        print(f"    {field_name}: {field_type} = Field(..., description={field_description!r})")

def extract_type_from_description(description: str) -> Optional[Any]:
    """Extract type information from field description."""
    import re
    match = re.search(r'\((.*?)\)$', description)
    if not match:
        return None

    type_str = match.group(1)
    basic_types = {
        'str': str, 'int': int, 'float': float, 'bool': bool,
        'EmailStr': str
    }

    if type_str in basic_types:
        return basic_types[type_str]

    def parse_nested_type(type_str: str) -> Any:
        list_match = re.match(r'List\[(.*)\]', type_str)
        if list_match:
            inner = list_match.group(1)
            return List[basic_types.get(inner, Any)]

        dict_match = re.match(r'Dict\[(.*),\s*(.*)\]', type_str)
        if dict_match:
            key_type = dict_match.group(1).strip()
            value_type = dict_match.group(2).strip()
            key = basic_types.get(key_type, str)
            return Dict[key, basic_types.get(value_type, Any)]

        return Any

    return parse_nested_type(type_str)

def create_pydantic_model_from_schema(schema: Dict[str, Any], model_name: str = "PromptInputModel") -> Type[BaseModel]:
    """Generate a Pydantic model from a JSON schema."""
    fields = {}
    for argument in schema.get("arguments", []):
        field_name = argument["name"]
        description = argument.get("description", "")
        field_type = extract_type_from_description(description)

        if field_type is None:
            field_type = {
                "string": str, "integer": int, "boolean": bool,
                "number": float, "null": type(None),
                "array": List[Any], "object": Dict[str, Any],
            }.get(argument["type"], Any)

        required = argument.get("required", False)
        fields[field_name] = (field_type, Field(..., description=description) if required
                            else Field(None, description=description))

    return create_model(model_name, **fields)

async def discover_capabilities(session: ClientSession):
    """Discover and print server capabilities."""
    try:
        prompts_response = await session.list_prompts()
        print("Server Prompts:", [p.name for p in prompts_response.prompts])

        for p in prompts_response.prompts:
            print(f"#" * 80)
            print(f"\nPrompt: {p.name}")
            print(f"Description: {p.description}")

            json_schema = p.model_dump_json()
            DynamicModel = create_pydantic_model_from_schema(json.loads(json_schema))

            print("\nModel Class:")
            print_pydantic_model(DynamicModel)

            print("\nExample Input Structure:")
            print(generate_example_input(DynamicModel))

    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc())

async def run_with_server(script_path: str):
    """Run operations within server connection context."""
    params = StdioServerParameters(command="/Users/deepnpisgah/.local/bin/uv",
                                 args=["run", "--with", "mcp", "mcp", "run", script_path])
    async with stdio_client(params) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            await discover_capabilities(session)

async def main():
    if len(sys.argv) < 2:
        print("Usage: python prompt_client.py <server.py>")
        sys.exit(1)
    await run_with_server(sys.argv[1])

if __name__ == "__main__":
    asyncio.run(main())