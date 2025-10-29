"""
Custom Tools for Software Engineering Mentor - CrewAI Implementation
"""

from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import ast


class CodeComplexityInput(BaseModel):
    """Input schema for Code Complexity Analyzer"""
    code: str = Field(..., description="Python code to analyze for complexity")


class CodeComplexityTool(BaseTool):
    name: str = "Code Complexity Analyzer"
    description: str = (
        "Analyzes Python code complexity including cyclomatic complexity, "
        "lines of code, number of functions, and classes. Returns a detailed "
        "complexity report with recommendations."
    )
    args_schema: Type[BaseModel] = CodeComplexityInput
    
    def _run(self, code: str) -> str:
        """
        Analyze Python code and return complexity metrics
        """
        try:
            tree = ast.parse(code)
            
            # Count different elements
            num_functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            num_classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            num_imports = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
            num_if_statements = sum(1 for node in ast.walk(tree) if isinstance(node, ast.If))
            num_loops = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While)))
            num_try_blocks = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Try))
            
            # Calculate metrics
            num_lines = len([line for line in code.split('\n') if line.strip() and not line.strip().startswith('#')])
            cyclomatic_complexity = 1 + num_if_statements + num_loops + num_try_blocks
            
            # Determine complexity level
            if cyclomatic_complexity > 20 or num_lines > 200:
                complexity_level = "Very High"
                recommendation = "Consider refactoring into smaller functions/modules"
            elif cyclomatic_complexity > 10 or num_lines > 100:
                complexity_level = "High"
                recommendation = "Code is complex but manageable. Consider adding more comments and documentation"
            elif cyclomatic_complexity > 5 or num_lines > 50:
                complexity_level = "Medium"
                recommendation = "Code complexity is acceptable. Ensure proper testing coverage"
            else:
                complexity_level = "Low"
                recommendation = "Code is simple and maintainable"
            
            # Function-level analysis
            function_details = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                    function_details.append(f"  - {node.name}(): {func_lines} lines")
            
            function_summary = "\n".join(function_details) if function_details else "  No functions found"
            
            return f"""
## 📊 Code Complexity Analysis

### Metrics:
- **Lines of Code**: {num_lines}
- **Cyclomatic Complexity**: {cyclomatic_complexity}
- **Complexity Level**: {complexity_level}

### Structure:
- **Functions**: {num_functions}
- **Classes**: {num_classes}
- **Imports**: {num_imports}
- **Control Structures**:
  - If statements: {num_if_statements}
  - Loops (for/while): {num_loops}
  - Try/Except blocks: {num_try_blocks}

### Function Breakdown:
{function_summary}

### 💡 Recommendation:
{recommendation}

### Code Quality Score: {max(0, 100 - (cyclomatic_complexity * 3) - (num_lines // 5))}/100
"""
        except SyntaxError as e:
            return f"❌ Syntax Error: Unable to parse code - {str(e)}"
        except Exception as e:
            return f"❌ Analysis Error: {str(e)}"


class ResourceQualityInput(BaseModel):
    """Input schema for Resource Quality Scorer"""
    url: str = Field(..., description="Resource URL to evaluate")
    resource_type: str = Field(..., description="Type of resource: tutorial, documentation, video, course, article")
    source: str = Field(default="unknown", description="Source platform (e.g., MDN, freeCodeCamp, YouTube)")


class ResourceQualityTool(BaseTool):
    name: str = "Resource Quality Scorer"
    description: str = (
        "Scores educational resources based on source reputation, resource type, "
        "and domain authority. Returns quality score and recommendation."
    )
    args_schema: Type[BaseModel] = ResourceQualityInput
    
    def _run(self, url: str, resource_type: str, source: str = "unknown") -> str:
        """
        Score resource quality based on multiple factors
        """
        # Trusted source scoring
        trusted_sources = {
            'developer.mozilla.org': 95,
            'mdn': 95,
            'mozilla': 95,
            'docs.python.org': 95,
            'python.org': 95,
            'reactjs.org': 95,
            'react.dev': 95,
            'nodejs.org': 95,
            'github.com': 85,
            'stackoverflow.com': 80,
            'freecodecamp': 90,
            'codecademy': 85,
            'udemy': 80,
            'coursera': 90,
            'edx': 90,
            'youtube.com': 70,
            'medium.com': 65,
            'dev.to': 70,
            'geeksforgeeks': 70,
            'w3schools': 65,
            'tutorialspoint': 60,
        }
        
        # Calculate source score
        source_score = 50  # default
        url_lower = url.lower()
        source_lower = source.lower()
        
        for trusted, score in trusted_sources.items():
            if trusted in url_lower or trusted in source_lower:
                source_score = score
                break
        
        # Resource type scoring
        type_scores = {
            'documentation': 95,
            'official documentation': 100,
            'course': 90,
            'tutorial': 85,
            'video': 80,
            'article': 75,
            'blog': 65,
        }
        
        type_score = type_scores.get(resource_type.lower(), 70)
        
        # Combined score (weighted average)
        quality_score = int(source_score * 0.6 + type_score * 0.4)
        
        # Determine rating
        if quality_score >= 90:
            rating = "Excellent ⭐⭐⭐⭐⭐"
            recommendation = "Highly recommended - Top quality resource"
        elif quality_score >= 80:
            rating = "Very Good ⭐⭐⭐⭐"
            recommendation = "Recommended - High quality resource"
        elif quality_score >= 70:
            rating = "Good ⭐⭐⭐"
            recommendation = "Recommended - Solid resource"
        elif quality_score >= 60:
            rating = "Fair ⭐⭐"
            recommendation = "Acceptable - Verify with other sources"
        else:
            rating = "Poor ⭐"
            recommendation = "Use with caution - Seek better alternatives"
        
        # Additional insights
        is_official = any(x in url_lower for x in ['docs.', 'official', '.org', 'developer.'])
        is_recent = 'youtube.com' not in url_lower or '2024' in url_lower or '2023' in url_lower
        
        insights = []
        if is_official:
            insights.append("✅ Official/authoritative source")
        if source_score >= 90:
            insights.append("✅ Highly trusted platform")
        if type_score >= 85:
            insights.append("✅ Comprehensive format")
        if quality_score < 70:
            insights.append("⚠️ Consider cross-referencing with other sources")
        
        insights_text = "\n".join([f"  - {insight}" for insight in insights])
        
        return f"""
## 🎯 Resource Quality Report

**URL**: {url}
**Type**: {resource_type}
**Source**: {source}

### Quality Score: {quality_score}/100
### Rating: {rating}

### Score Breakdown:
- Source Reputation: {source_score}/100
- Resource Type Quality: {type_score}/100

### Insights:
{insights_text if insights else "  - Standard quality resource"}

### 📌 Recommendation:
{recommendation}
"""


# Export tools
__all__ = ['CodeComplexityTool', 'ResourceQualityTool']
