"""
Import all tools for Software Engineering Mentor
"""

from .complexity_analyzer import CodeComplexityTool, ResourceQualityTool

# Import CrewAI built-in tools
try:
    from crewai_tools import SerperDevTool, FileReadTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False
    SerperDevTool = None
    FileReadTool = None

__all__ = [
    'CodeComplexityTool',
    'ResourceQualityTool',
    'SerperDevTool',
    'FileReadTool',
    'CREWAI_TOOLS_AVAILABLE'
]
