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
def typed_prompt(
        name: Annotated[str, Field(description=MessageTaskInput.model_fields["name"].description)],
        number: Annotated[int, Field(description=MessageTaskInput.model_fields["number"].description)],
        email: Annotated[EmailStr, Field(description=MessageTaskInput.model_fields["email"].description)],
        subscribe: Annotated[bool, Field(description=MessageTaskInput.model_fields["subscribe"].description)]
) -> GetPromptResult:
    """
    Generate a text response using the provided input.

    Args:
        name (str): Name of the user
        number (int): Lucky number
        email (EmailStr): Email address of the user
        subscribe (bool): Whether to subscribe

    Returns:
        GetPromptResult: A result containing the formatted message for the user.
    """
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


class ProjectStatus(BaseModel):
    """Represents the current status and priority of a project, along with assigned users.

    Attributes:
        task (str): The name of the task.
        status (str): The current status of the project (e.g., "In Progress", "Completed").
        priority (int): A numeric priority level (e.g., 1 for high priority).
        assignees (List[str]): A list of usernames assigned to this project status.
    """

    task: str = Field(..., min_length=1, max_length=100, description="Name of the task (str)")
    status: str = Field(..., min_length=1, max_length=100, description="Status of the task (str)")
    priority: int = Field(..., description="Priority of the task (int)")
    assignees: List[str] = Field(...,  description="list of assignees (List[str])")


@mcp.prompt("mixed")
def mixed_prompt(
        task: Annotated[str, Field(description=ProjectStatus.model_fields["task"].description)],
        status: Annotated[str, Field(description=ProjectStatus.model_fields["status"].description)],
        priority: Annotated[int, Field(description=ProjectStatus.model_fields["priority"].description)],
        assignees: Annotated[List[str], Field(description=ProjectStatus.model_fields["assignees"].description)]
) -> GetPromptResult:
    """
    Generate a status report for a project.

    Args:
        task (str): Name of the task
        status (str): Current project status
        priority (int): Priority level
        assignees (List[str]): List of assigned usernames

    Returns:
        GetPromptResult: A result containing the formatted status report.
    """
    input_data = ProjectStatus(
        task=task,
        status=status,
        priority=priority,
        assignees=assignees
    )

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


class UserProfile(BaseModel):
    """Represents a user profile with essential identity details.

    Attributes:
        username (str): The unique identifier for the user.
        email (str): The email address associated with the user.
        is_active (bool): Indicates whether the user's account is currently active.
    """
    username: str = Field(..., min_length=1, max_length=50, description="The unique identifier for the user (str)")
    email: str = Field(..., min_length=5, max_length=100, description="The email address associated with the user (str)")
    is_active: bool = Field(..., description="Indicates whether the user's account is currently active (bool)")


class ComplexInput(BaseModel):
    """Defines a complex input structure containing project details, ownership, status updates, and settings.

    Attributes:
        project_name (str): The name of the project.
        owner (UserProfile): The user profile of the project owner.
        statuses (List[ProjectStatus]): A list of status updates, including priority and assignees.
        settings (Dict[str, List[str]]): A dictionary of configuration settings,
            where keys represent setting categories and values are lists of associated options.
    """
    project_name: str = Field(..., min_length=1, max_length=100, description="The name of the project (str)")
    owner: UserProfile = Field(..., description="The user profile of the project owner (UserProfile)")
    statuses: List[ProjectStatus] = Field(..., description="List of status updates, including priority and assignees (List[ProjectStatus])")
    settings: Dict[str, List[str]] = Field(..., description="Dictionary of configuration settings with categories and options (Dict[str, List[str]])")


@mcp.prompt("complex")
def complex_prompt(
        project_name: Annotated[str, Field(description=ComplexInput.model_fields["project_name"].description)],
        owner_username: Annotated[str, Field(description=UserProfile.model_fields["username"].description)],
        owner_email: Annotated[str, Field(description=UserProfile.model_fields["email"].description)],
        owner_is_active: Annotated[bool, Field(description=UserProfile.model_fields["is_active"].description)],
        statuses_task: Annotated[str, Field(description=ProjectStatus.model_fields["task"].description)],
        statuses_status: Annotated[str, Field(description=ProjectStatus.model_fields["status"].description)],
        statuses_priority: Annotated[int, Field(description=ProjectStatus.model_fields["priority"].description)],
        statuses_assignees: Annotated[
            List[str], Field(description=ProjectStatus.model_fields["assignees"].description)],
        settings: Annotated[Dict[str, List[str]], Field(description=ComplexInput.model_fields["settings"].description)]
) -> GetPromptResult:
    """
    Generate a comprehensive project report.

    Args:
        project_name (str): The name of the project
        owner_username (str): The unique identifier for the project owner
        owner_email (str): The email address of the project owner
        owner_is_active (bool): Whether the project owner's account is active
        statuses_task (str): Name of the task
        statuses_status (str): Current project status
        statuses_priority (int): Priority level
        statuses_assignees (List[str]): List of assigned usernames
        settings (Dict[str, List[str]]): Project configuration settings

    Returns:
        GetPromptResult: A result containing the formatted project report.
    """
    # Construct nested objects
    owner = UserProfile(
        username=owner_username,
        email=owner_email,
        is_active=owner_is_active
    )

    status = ProjectStatus(
        task=statuses_task,
        status=statuses_status,
        priority=statuses_priority,
        assignees=statuses_assignees
    )

    input_data = ComplexInput(
        project_name=project_name,
        owner=owner,
        statuses=[status],  # Note: Using single status for now
        settings=settings
    )

    # Format the comprehensive report
    assignee_list = ", ".join(status.assignees)
    settings_str = "\n".join(f"    {category}: {', '.join(values)}"
                             for category, values in input_data.settings.items())

    report = f"""
    Comprehensive Project Report
    --------------------------
    Project Name: {input_data.project_name}

    Owner Information:
    - Username: {input_data.owner.username}
    - Email: {input_data.owner.email}
    - Account Status: {"Active" if input_data.owner.is_active else "Inactive"}

    Current Status:
    - Task: {status.task}
    - Status: {status.status}
    - Priority Level: {status.priority}
    - Assigned Team Members: {assignee_list}

    Project Settings:
{settings_str}
    """
    report = report.strip()

    return GetPromptResult(
        description="Comprehensive project report",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=report),
            ),
        ],
    )