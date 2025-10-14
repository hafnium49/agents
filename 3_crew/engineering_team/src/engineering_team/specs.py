"""
Pydantic models for structured outputs in the engineering team crew.
These models enforce type safety and enable dynamic task generation.
"""

from pydantic import BaseModel, Field
from typing import List


class ClassSpec(BaseModel):
    """Specification for a single class in a module."""
    name: str = Field(..., description="Name of the class")
    public_methods: List[str] = Field(
        default_factory=list,
        description="List of public method signatures"
    )
    description: str = Field(
        default="",
        description="Brief description of the class purpose"
    )


class ModuleSpec(BaseModel):
    """Specification for a Python module."""
    name: str = Field(..., description="Module filename (e.g., 'accounts.py')")
    classes: List[ClassSpec] = Field(
        default_factory=list,
        description="Classes defined in this module"
    )
    functions: List[str] = Field(
        default_factory=list,
        description="Standalone functions in the module"
    )
    needs_ui_demo: bool = Field(
        default=False,
        description="Whether this module needs a Gradio UI demo"
    )
    needs_tests: bool = Field(
        default=True,
        description="Whether this module needs unit tests"
    )
    dependencies: List[str] = Field(
        default_factory=list,
        description="External dependencies required by this module"
    )


class SystemPlan(BaseModel):
    """Complete system design plan with all modules and metadata."""
    modules: List[ModuleSpec] = Field(
        ...,
        description="All modules to be implemented in this system"
    )
    notes: str = Field(
        default="",
        description="Additional design notes, architecture decisions, or considerations"
    )
    system_name: str = Field(
        default="system",
        description="Overall system/project name"
    )
    requirements_summary: str = Field(
        default="",
        description="Brief summary of what this system does"
    )
