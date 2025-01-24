from typing import Dict, List, Annotated
from mcp import GetPromptResult
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, PromptMessage
from pydantic import BaseModel, Field, EmailStr

# Create server
mcp = FastMCP("ComplexDataServer")

# Model Definitions
class UserProfile(BaseModel):
    """User profile with contact and role information."""
    username: str = Field(..., min_length=1, description="User's unique identifier (str)")
    email: EmailStr = Field(..., description="User's email address (EmailStr)")
    roles: List[str] = Field(..., description="List of assigned roles (List[str])")
    preferences: Dict[str, List[str]] = Field(..., description="User preferences with multiple options (Dict[str, List[str]])")

class MetricsData(BaseModel):
    """Represents performance metrics as matrix data."""
    metric_names: List[str] = Field(..., description="Names of the metrics being tracked (List[str])")
    daily_values: List[List[float]] = Field(..., description="Matrix of daily metric values (List[List[float]])")
    targets: Dict[str, float] = Field(..., description="Target value for each metric (Dict[str, float])")

class TeamStructure(BaseModel):
    """Represents team hierarchy and responsibilities."""
    leads: Dict[str, List[str]] = Field(..., description="Team leads and their direct reports (Dict[str, List[str]])")
    specialties: Dict[str, Dict[str, List[str]]] = Field(..., description="Team specialties and capabilities (Dict[str, Dict[str, List[str]]])")
    locations: List[Dict[str, str]] = Field(..., description="Office locations and details (List[Dict[str, str]])")

class ComplexProjectData(BaseModel):
    """Complex project data combining various nested structures."""
    project_name: str = Field(..., min_length=1, description="Name of the project (str)")
    owner: UserProfile = Field(..., description="Project owner details (UserProfile)")
    metrics: MetricsData = Field(..., description="Project performance metrics (MetricsData)")
    team: TeamStructure = Field(..., description="Team organization details (TeamStructure)")

@mcp.prompt("nested_collections")
def nested_collections_prompt(
    project_name: Annotated[str, Field(description=ComplexProjectData.model_fields["project_name"].description)],
    # Owner fields (UserProfile)
    owner_username: Annotated[str, Field(description=UserProfile.model_fields["username"].description)],
    owner_email: Annotated[EmailStr, Field(description=UserProfile.model_fields["email"].description)],
    owner_roles: Annotated[List[str], Field(description=UserProfile.model_fields["roles"].description)],
    owner_preferences: Annotated[Dict[str, List[str]], Field(description=UserProfile.model_fields["preferences"].description)],
    # Metrics fields (MetricsData)
    metric_names: Annotated[List[str], Field(description=MetricsData.model_fields["metric_names"].description)],
    daily_values: Annotated[List[List[float]], Field(description=MetricsData.model_fields["daily_values"].description)],
    metric_targets: Annotated[Dict[str, float], Field(description=MetricsData.model_fields["targets"].description)],
    # Team fields (TeamStructure)
    team_leads: Annotated[Dict[str, List[str]], Field(description=TeamStructure.model_fields["leads"].description)],
    team_specialties: Annotated[Dict[str, Dict[str, List[str]]], Field(description=TeamStructure.model_fields["specialties"].description)],
    team_locations: Annotated[List[Dict[str, str]], Field(description=TeamStructure.model_fields["locations"].description)]
) -> GetPromptResult:
    """
    Generate a comprehensive project report with nested data structures.
    
    Args:
        project_name (str): Name of the project
        owner_username (str): User's unique identifier
        owner_email (EmailStr): User's email address
        owner_roles (List[str]): List of assigned roles
        owner_preferences (Dict[str, List[str]]): User preferences with multiple options
        metric_names (List[str]): Names of the metrics being tracked
        daily_values (List[List[float]]): Matrix of daily metric values
        metric_targets (Dict[str, float]): Target value for each metric
        team_leads (Dict[str, List[str]]): Team leads and their direct reports
        team_specialties (Dict[str, Dict[str, List[str]]]): Team specialties and capabilities
        team_locations (List[Dict[str, str]]): Office locations and details
    
    Returns:
        GetPromptResult: A result containing the formatted project report.
    """
    # Construct nested objects
    owner = UserProfile(
        username=owner_username,
        email=owner_email,
        roles=owner_roles,
        preferences=owner_preferences
    )
    
    metrics = MetricsData(
        metric_names=metric_names,
        daily_values=daily_values,
        targets=metric_targets
    )
    
    team = TeamStructure(
        leads=team_leads,
        specialties=team_specialties,
        locations=team_locations
    )
    
    input_data = ComplexProjectData(
        project_name=project_name,
        owner=owner,
        metrics=metrics,
        team=team
    )

    # Format the report (simplified for brevity)
    report = f"""
    Project: {input_data.project_name}
    Owner: {input_data.owner.username} ({input_data.owner.email})
    Roles: {', '.join(input_data.owner.roles)}
    Metrics Tracked: {', '.join(input_data.metrics.metric_names)}
    Teams: {', '.join(input_data.team.leads.keys())}
    """
    
    return GetPromptResult(
        description="Complex nested data project report",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=report),
            ),
        ],
    )