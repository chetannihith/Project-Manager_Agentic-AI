"""
Custom Tools for Software Engineering Mentor
Implements custom ADK tools for project analysis
"""

from google.genai.types import Tool, FunctionDeclaration
from typing import List, Dict
import json


# ==================== CUSTOM TOOL 1: Project Complexity Calculator ====================

def calculate_project_complexity(features: list[str], team_size: int, timeline_months: int, tech_stack_count: int) -> dict:
    """
    Calculates project complexity score based on multiple factors.
    
    Args:
        features: List of project features/requirements
        team_size: Number of team members (1-50)
        timeline_months: Project timeline in months (1-36)
        tech_stack_count: Number of technologies in stack (1-20)
    
    Returns:
        A complexity analysis with score, difficulty level, and recommendations
    """
    # Calculate complexity score
    feature_score = len(features) * 10
    timeline_pressure = (12 / timeline_months) * 20
    team_factor = max(0, (5 - team_size) * 5)  # Smaller teams = higher complexity
    tech_complexity = tech_stack_count * 3
    
    total_score = feature_score + timeline_pressure + team_factor + tech_complexity
    
    # Determine difficulty level
    if total_score > 80:
        difficulty = "Very High"
        recommendation = "Consider breaking into smaller phases, expanding team, or extending timeline"
    elif total_score > 60:
        difficulty = "High"
        recommendation = "Requires experienced team and careful planning"
    elif total_score > 40:
        difficulty = "Medium"
        recommendation = "Manageable with proper planning and regular milestones"
    else:
        difficulty = "Low"
        recommendation = "Good project scope for the given constraints"
    
    # Calculate recommended timeline
    recommended_months = max(
        timeline_months,
        int((len(features) * 0.5) + (tech_stack_count * 0.3))
    )
    
    risk_factors = []
    if len(features) > 10:
        risk_factors.append("High feature count")
    if timeline_pressure > 15:
        risk_factors.append("Tight timeline")
    if team_size < 3:
        risk_factors.append("Small team")
    if tech_stack_count > 8:
        risk_factors.append("Complex tech stack")
    
    return {
        "complexity_score": round(total_score, 2),
        "difficulty_level": difficulty,
        "recommendation": recommendation,
        "analysis": {
            "feature_complexity": feature_score,
            "timeline_pressure": round(timeline_pressure, 2),
            "team_adequacy": team_factor,
            "technology_complexity": tech_complexity
        },
        "suggested_timeline_months": recommended_months,
        "risk_factors": risk_factors if risk_factors else ["None identified"]
    }


# Create the tool using GenAI FunctionDeclaration
project_complexity_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="calculate_project_complexity",
            description="Calculates project complexity score based on features, team size, timeline, and technology stack. Returns detailed complexity analysis with recommendations.",
            parameters={
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of project features/requirements"
                    },
                    "team_size": {
                        "type": "integer",
                        "description": "Number of team members (1-50)"
                    },
                    "timeline_months": {
                        "type": "integer",
                        "description": "Project timeline in months (1-36)"
                    },
                    "tech_stack_count": {
                        "type": "integer",
                        "description": "Number of technologies in stack (1-20)"
                    }
                },
                "required": ["features", "team_size", "timeline_months", "tech_stack_count"]
            }
        )
    ]
)


# ==================== CUSTOM TOOL 2: Technology Stack Validator ====================

class TechStackInput(BaseModel):
    """Input schema for technology stack validation"""
    frontend: str = Field(description="Frontend framework/library (e.g., React, Vue, Angular)")
    backend: str = Field(description="Backend framework (e.g., Node.js, Django, Flask)")
    database: str = Field(description="Database system (e.g., MongoDB, PostgreSQL, MySQL)")
    additional_tools: List[str] = Field(default=[], description="Additional tools/services")


def validate_tech_stack(input: TechStackInput) -> Dict:
    """
    Validates technology stack compatibility and provides recommendations
    
    Returns compatibility analysis and alternative suggestions
    """
    # Define compatible stack combinations
    popular_stacks = {
        "MERN": ("React", "Node.js", "MongoDB"),
        "MEAN": ("Angular", "Node.js", "MongoDB"),
        "MEVN": ("Vue", "Node.js", "MongoDB"),
        "Django Stack": ("React", "Django", "PostgreSQL"),
        "Flask Stack": ("React", "Flask", "PostgreSQL"),
        "Ruby Stack": ("React", "Ruby on Rails", "PostgreSQL"),
        "Laravel Stack": ("Vue", "Laravel", "MySQL"),
        "ASP.NET Stack": ("React", "ASP.NET Core", "SQL Server"),
    }
    
    # Normalize inputs
    frontend_norm = input.frontend.lower()
    backend_norm = input.backend.lower()
    database_norm = input.database.lower()
    
    # Check for known compatible stacks
    matched_stack = None
    for stack_name, (fe, be, db) in popular_stacks.items():
        if (fe.lower() in frontend_norm and 
            be.lower() in backend_norm and 
            db.lower() in database_norm):
            matched_stack = stack_name
            break
    
    # Compatibility scoring
    compatibility_score = 0
    compatibility_issues = []
    
    # Frontend-Backend compatibility
    if any(x in frontend_norm for x in ["react", "vue", "angular"]):
        if any(x in backend_norm for x in ["node", "express", "nest"]):
            compatibility_score += 30
        elif any(x in backend_norm for x in ["django", "flask", "fastapi"]):
            compatibility_score += 25
        else:
            compatibility_score += 15
            compatibility_issues.append("Frontend-Backend pairing is unconventional")
    
    # Backend-Database compatibility
    if "node" in backend_norm and "mongo" in database_norm:
        compatibility_score += 35
    elif "django" in backend_norm and "postgres" in database_norm:
        compatibility_score += 35
    elif "flask" in backend_norm and "postgres" in database_norm:
        compatibility_score += 35
    else:
        compatibility_score += 20
        compatibility_issues.append("Backend-Database pairing may need additional configuration")
    
    # Additional tools bonus
    compatibility_score += min(len(input.additional_tools) * 5, 35)
    
    # Determine compatibility level
    if compatibility_score >= 80:
        compatibility = "Excellent"
    elif compatibility_score >= 60:
        compatibility = "Good"
    elif compatibility_score >= 40:
        compatibility = "Fair"
    else:
        compatibility = "Poor"
    
    # Generate recommendations
    recommendations = []
    if matched_stack:
        recommendations.append(f"This is a well-known '{matched_stack}' stack - excellent choice!")
    
    if compatibility_score < 60:
        recommendations.append("Consider using a more standard stack combination for easier development")
    
    if "mongo" in database_norm and "sql" in backend_norm:
        recommendations.append("Note: Using SQL-focused backend with NoSQL database - ensure proper ODM/ORM setup")
    
    return {
        "is_compatible": compatibility_score >= 40,
        "compatibility_level": compatibility,
        "compatibility_score": compatibility_score,
        "matched_stack": matched_stack or "Custom Stack",
        "issues": compatibility_issues if compatibility_issues else ["No major issues detected"],
        "recommendations": recommendations if recommendations else ["Stack looks good!"],
        "suggested_alternatives": [
            "MERN Stack (MongoDB, Express, React, Node.js)",
            "Django + React + PostgreSQL",
            "Vue + Node.js + MongoDB"
        ] if compatibility_score < 60 else []
    }


# Create the tool
tech_stack_validator_tool = FunctionTool(
    name="validate_tech_stack",
    description="Validates technology stack compatibility and provides recommendations for frontend, backend, and database combinations.",
    input_schema=TechStackInput,
    function=validate_tech_stack
)


# ==================== CUSTOM TOOL 3: Resource Quality Scorer ====================

class ResourceInput(BaseModel):
    """Input schema for resource quality scoring"""
    url: str = Field(description="Resource URL")
    resource_type: str = Field(description="Type: tutorial, documentation, course, article, video")
    source: str = Field(description="Source platform (e.g., MDN, freeCodeCamp, Udemy)")
    last_updated_year: int = Field(description="Year of last update", ge=2015, le=2025)


def score_resource_quality(input: ResourceInput) -> Dict:
    """
    Scores learning resource quality based on multiple factors
    
    Returns quality score and rating
    """
    score = 0
    factors = {}
    
    # Source reputation scoring
    trusted_sources = {
        "mdn": 95, "mozilla": 95,
        "freecodecamp": 90, "codecademy": 85,
        "udemy": 80, "coursera": 90,
        "youtube": 70, "medium": 65,
        "dev.to": 70, "stackoverflow": 85,
        "github": 88, "official docs": 95
    }
    
    source_lower = input.source.lower()
    source_score = 50  # default
    for source, score_val in trusted_sources.items():
        if source in source_lower:
            source_score = score_val
            break
    
    factors["source_reputation"] = source_score
    score += source_score * 0.4  # 40% weight
    
    # Recency scoring
    current_year = 2025
    years_old = current_year - input.last_updated_year
    if years_old == 0:
        recency_score = 100
    elif years_old == 1:
        recency_score = 90
    elif years_old == 2:
        recency_score = 75
    elif years_old <= 3:
        recency_score = 60
    else:
        recency_score = 40
    
    factors["recency"] = recency_score
    score += recency_score * 0.3  # 30% weight
    
    # Resource type scoring
    type_scores = {
        "documentation": 95,
        "course": 90,
        "tutorial": 85,
        "article": 75,
        "video": 80
    }
    type_score = type_scores.get(input.resource_type.lower(), 70)
    factors["resource_type_quality"] = type_score
    score += type_score * 0.3  # 30% weight
    
    # Overall rating
    if score >= 85:
        rating = "Excellent"
    elif score >= 70:
        rating = "Good"
    elif score >= 55:
        rating = "Fair"
    else:
        rating = "Poor"
    
    return {
        "quality_score": round(score, 2),
        "rating": rating,
        "factors": factors,
        "recommendation": "Highly recommended" if score >= 80 else "Recommended" if score >= 65 else "Use with caution"
    }


# Create the tool
resource_scorer_tool = FunctionTool(
    name="score_resource_quality",
    description="Scores the quality of learning resources based on source reputation, recency, and type.",
    input_schema=ResourceInput,
    function=score_resource_quality
)


# Export all tools
__all__ = [
    'project_complexity_tool',
    'tech_stack_validator_tool',
    'resource_scorer_tool',
    'calculate_project_complexity',
    'validate_tech_stack',
    'score_resource_quality'
]
