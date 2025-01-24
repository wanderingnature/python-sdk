"""FastMCP Echo Server."""
from enum import Enum
from pathlib import Path
from typing import Dict, List, Literal, Optional, Annotated

from mcp import GetPromptResult
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ValidationError
from mcp.server.fastmcp.prompts.prompt_manager import Prompt
from mcp.server.fastmcp.prompts.base import PromptArgument
from mcp.types import TextContent, PromptMessage
from pydantic import BaseModel, Field, EmailStr



# Create server
mcp = FastMCP("EchoPromptServer")


# PROMPTS SETUP

class MessageTaskInput(BaseModel):
    """
    Input validation for echo task prompt.

    Attributes:
        name (str): Name of the user
        email (EmailStr): Email address of the user
        subscribe (bool): Whether the user wants to subscribe
    """
    name: str = Field(..., min_length=1, max_length=100, description="Name of the user (str)")
    number: int = Field(...,description="your lucky number (int)")
    email: EmailStr = Field(..., description="Email address of the user (EmailStr)")
    subscribe: bool = Field(..., description="Whether the user wants to subscribe (bool)")


EMAIL_TEMPLATE_SUBSCRIBE = """
    Hello {name}, thanks for subscribing today. We'll send updates to {email}.
    {number} is your lucky number
"""

EMAIL_TEMPLATE_UNSUBSCRIBE = """
    Hello {name}, you unsubscribed today. We will no longer send updates to {email}.
    {number} is your lucky number
"""



@mcp.prompt("basic")
def basic_prompt(
    name: Annotated[str, Field(description="Name of the user (str)")],
    number: Annotated[int, Field(description="Lucky number (int)")],
    email: Annotated[EmailStr, Field(description="Contact email address (EmailStr|str)")],
    subscribe: Annotated[bool, Field(description="Whether to subscribe to updates (bool)")]
) -> GetPromptResult:
    """
    Generate a text response using the provided input.

    Args:
        name (str): Name of the user.
        number (int): Lucky number.
        email (EmailStr): Email address of the user.
        subscribe (bool): Whether the user wants to subscribe.

    Returns:
        str: a message for the user.
    """

    # Validate input using MessageTaskInput

    try:
        input_data = MessageTaskInput(name=name, number=number, email=email, subscribe=subscribe)
        if input_data.subscribe:
            prompt = EMAIL_TEMPLATE_SUBSCRIBE.format(
                name=input_data.name, email=input_data.email, number=input_data.number
            )
        else:
            prompt = EMAIL_TEMPLATE_UNSUBSCRIBE.format(
                name=input_data.name, email=input_data.email, number=input_data.number
            )
        prompt = prompt.strip()
        return GetPromptResult(
            description="py-code task execution template",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt),
                ),
            ],
        )

    except ValidationError as e:
        return f"Validation error {e}"


@mcp.prompt("basic_plus")
def basic_plus_prompt(
        name: Annotated[
            str,
            Field(
                description=MessageTaskInput.model_fields["name"].description,
            ),
        ],
        number: Annotated[
            int,
            Field(
                description=MessageTaskInput.model_fields["number"].description,
            ),
        ],
        email: Annotated[
            EmailStr,
            Field(
                description=MessageTaskInput.model_fields["email"].description,
            ),
        ],
        subscribe: Annotated[
            bool,
            Field(
                description=MessageTaskInput.model_fields["subscribe"].description,
            ),
        ],
) -> GetPromptResult:
    """
    A function that uses individual arguments, directly referencing the model
    for validation metadata.
    """

    # Validate input using MessageTaskInput

    try:
        input_data = MessageTaskInput(name=name, number=number, email=email, subscribe=subscribe)
        if input_data.subscribe:
            prompt = EMAIL_TEMPLATE_SUBSCRIBE.format(
                name=input_data.name, email=input_data.email, number=input_data.number
            )
        else:
            prompt = EMAIL_TEMPLATE_UNSUBSCRIBE.format(
                name=input_data.name, email=input_data.email, number=input_data.number
            )
        prompt = prompt.strip()
        return GetPromptResult(
            description="py-code task execution template",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt),
                ),
            ],
        )

    except ValidationError as e:
        return f"Validation error {e}"



@mcp.prompt("typed")
def types_prompt(
        input_data: Annotated[
            MessageTaskInput,
            Field(description="Input containing: name (str), number (int), email (EmailStr), and subscribe (bool)")
        ]
) -> GetPromptResult:
    """
    A function that uses the model class directly. Does not expose the types to the client.

    Args:
        input_data (MessageTaskInput): Input data containing:
            - name (str): Name of the user
            - number (int): Lucky number
            - email (EmailStr): Email address of the user
            - subscribe (bool): Whether to subscribe

    Returns:
        GetPromptResult: A result containing the formatted message for the user.
    """
    if input_data.subscribe:
        prompt = EMAIL_TEMPLATE_SUBSCRIBE.format(
            name=input_data.name, email=input_data.email, number=input_data.number
        )
    else:
        prompt = EMAIL_TEMPLATE_UNSUBSCRIBE.format(
            name=input_data.name, email=input_data.email, number=input_data.number
        )
    prompt = prompt.strip()

    return GetPromptResult(
        description="py-code task execution template",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            ),
        ],
    )

class ProjectStatus(BaseModel):
    """Represents the current status and priority of a project, along with assigned users.

    Attributes:
        task (str): The name of the task.
        status (str): The current status of the project (e.g., "In Progress", "Completed").
        priority (int): A numeric priority level (e.g., 1 for high priority).
        assignees (List[str]): A list of usernames assigned to this project status.
    """

    task: str
    status: str
    priority: int
    assignees: List[str]



@mcp.prompt("mixed")
def mixed(
        input_data: Annotated[
            ProjectStatus,
            Field(description="Project status containing: task (str), status (str), priority (int), assignees (List[str])")
        ]
) -> GetPromptResult:
    """
    A function that uses the model class directly. Does not expose the types to the client.

    Args:
        input_data (ProjectStatus): Project status containing:
            - task (str): Name of the task
            - status (str): Current project status
            - priority (int): Priority level
            - assignees (List[str]): List of assigned usernames

    Returns:
        GetPromptResult: A result containing the formatted status report.
    """
    # Format the status report
    assignee_list = ", ".join(input_data.assignees)
    report = f"""
    Project Status Report
    --------------------
    Task Name: {input_data.task}
    Status: {input_data.status}
    Priority Level: {input_data.priority}
    Assigned Team Members: {assignee_list}
    """
    report = report.strip()

    return GetPromptResult(
        description="Project status report",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=report),
            ),
        ],
    )