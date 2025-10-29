"""
Software Engineering Mentor - Google ADK Agent Implementation
LAB Assignment-2 Requirements:
1. ✅ Memory: State management across agents via output_key
2. ✅ Tool Integration: google_search (external) + 2 custom tools (analyze_code_complexity, store_user_context)
3. ✅ Parallel Execution: ParallelAgent for concurrent analysis tasks
4. ✅ Hallucination Mitigation: Validator agent reviews all outputs
5. ✅ Structured Output: Markdown format (simpler than JSON/Pydantic)
6. ✅ Task Monitoring & Logging: Callbacks for execution tracking
"""

import os
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.tools import ToolContext, google_search
from google.adk.tools.base_tool import BaseTool

# Load environment variables
load_dotenv()

GEMINI_MODEL = "gemini-2.0-flash-thinking-exp-01-21"

# ============================================================================
# CRITERION 2: TOOL INTEGRATION
# - External Tool: google_search (used in tech_researcher_agent, resource_curator_agent)
# - Custom Tool 1: analyze_code_complexity (static code analysis)
# - Custom Tool 2: store_user_context (state management tool)
# ============================================================================

def analyze_code_complexity(code: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Custom tool: Analyzes code complexity using static analysis metrics
    Stores results in state for downstream agents
    """
    # Store user code in state for memory
    if 'user_context' not in tool_context.state:
        tool_context.state.user_context = {}
    tool_context.state.user_context['analyzed_code'] = code
    
    # Simple complexity heuristics
    lines = code.split('\n')
    num_lines = len([l for l in lines if l.strip()])
    num_functions = len(re.findall(r'\bdef\s+\w+', code))
    num_classes = len(re.findall(r'\bclass\s+\w+', code))
    nesting_level = max([len(l) - len(l.lstrip()) for l in lines] + [0]) // 4
    
    # Calculate complexity score
    complexity_score = min(10, num_lines / 10 + num_functions * 0.5 + nesting_level)
    
    if complexity_score < 3:
        complexity = "LOW"
    elif complexity_score < 6:
        complexity = "MEDIUM"
    elif complexity_score < 8:
        complexity = "HIGH"
    else:
        complexity = "VERY_HIGH"
    
    result = {
        "complexity_level": complexity,
        "metrics": {
            "lines_of_code": num_lines,
            "functions": num_functions,
            "classes": num_classes,
            "max_nesting_level": nesting_level,
            "complexity_score": round(complexity_score, 2)
        }
    }
    
    print(f"[TOOL] Code Complexity Analysis Complete: {complexity} (Score: {complexity_score:.2f})")
    return result

def store_user_context(context_key: str, context_value: str, tool_context: ToolContext) -> Dict[str, Any]:
    """
    Custom tool: Stores user context in state for cross-agent memory
    """
    if 'user_context' not in tool_context.state:
        tool_context.state.user_context = {}
    
    tool_context.state.user_context[context_key] = context_value
    print(f"[TOOL] Stored user context: {context_key} = {context_value[:50]}...")
    
    return {"status": "success", "stored_key": context_key}

# ============================================================================
# CRITERION 6: MONITORING & LOGGING - Tool Callbacks
# ============================================================================

def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> None:
    """Callback executed before tool invocation"""
    print(f"\n[MONITOR] 🔧 Executing tool: {tool.__name__ if hasattr(tool, '__name__') else 'Unknown'}")
    print(f"[MONITOR] 📥 Tool arguments: {list(args.keys())}")

def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    """Callback executed after tool invocation"""
    print(f"[MONITOR] ✅ Tool completed: {tool.__name__ if hasattr(tool, '__name__') else 'Unknown'}")
    print(f"[MONITOR] 📤 Tool response keys: {list(tool_response.keys()) if isinstance(tool_response, dict) else 'Non-dict response'}")
    
    # Log state changes
    if hasattr(tool_context.state, 'user_context'):
        print(f"[MONITOR] 💾 State updated: user_context keys = {list(tool_context.state.user_context.keys())}")
    
    return None  # Don't modify response

# ============================================================================
# CRITERION 3: PARALLEL EXECUTION - Parallel Analysis Agents
# ============================================================================

# Parallel Agent 1: Quick Code Analyzer
quick_analyzer_agent = LlmAgent(
    name="QuickCodeAnalyzer",
    model=GEMINI_MODEL,
    instruction="""You are a Quick Code Analyzer. Analyze the provided code snippet for:
1. Syntax correctness
2. Basic code structure
3. Naming conventions
4. Import statements

Provide a concise 2-3 sentence summary focusing on immediate observations.
Use the code_complexity tool if code is provided in user context.
Output ONLY the analysis summary.""",
    description="Performs quick code analysis",
    tools=[analyze_code_complexity],
    output_key="quick_analysis",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# Parallel Agent 2: Technology Researcher
tech_researcher_agent = LlmAgent(
    name="TechnologyResearcher",
    model=GEMINI_MODEL,
    instruction="""You are a Technology Research Specialist. 
Based on the user's project idea, identify the key technologies mentioned and research:
1. Latest versions and updates
2. Community support and popularity
3. Alternative options

Use Google Search to find current information.
Provide a concise 2-3 sentence summary of your findings.
Output ONLY the research summary.""",
    description="Researches relevant technologies",
    tools=[google_search],
    output_key="tech_research",
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# Parallel Agent 3: Best Practices Advisor
best_practices_agent = LlmAgent(
    name="BestPracticesAdvisor",
    model=GEMINI_MODEL,
    instruction="""You are a Software Best Practices Advisor.
Based on the project type and technologies, identify:
1. Industry best practices
2. Common pitfalls to avoid
3. Design patterns to consider

Provide a concise 2-3 sentence summary of key recommendations.
Output ONLY the best practices summary.""",
    description="Advises on best practices",
    output_key="best_practices",
)

# Create Parallel Agent Group
parallel_analysis_group = ParallelAgent(
    name="ParallelAnalysisGroup",
    sub_agents=[quick_analyzer_agent, tech_researcher_agent, best_practices_agent],
    description="Runs multiple analysis agents concurrently for comprehensive insights"
)

# ============================================================================
# SEQUENTIAL PIPELINE AGENTS
# ============================================================================

# Agent 1: Project Planner - Markdown Output
planner_agent = LlmAgent(
    name="ProjectPlanner",
    model=GEMINI_MODEL,
    instruction="""You are a Software Project Planner. Analyze the user's project idea and create a comprehensive project roadmap.

Create a detailed markdown document with the following sections:

# Project Roadmap: [Project Name]

## Overview
[Brief 2-3 sentence overview of the project]

## Milestones

### Milestone 1: Planning Phase
- **Duration**: [Estimate]
- **Key Deliverables**:
  - [Deliverable 1]
  - [Deliverable 2]
- **Technologies**: [List technologies]

[Continue with 4-6 milestones covering: Planning, Design, Implementation, Testing, Deployment]

## Potential Risks
- [Risk 1]
- [Risk 2]
- [Risk 3]

## Success Criteria
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

Output your response in clean, well-formatted markdown. Be specific and actionable.""",
    description="Creates structured project roadmaps in markdown",
    output_key="project_roadmap",
    tools=[store_user_context],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# Agent 2: System Architect - Markdown Output
architect_agent = LlmAgent(
    name="SystemArchitect",
    model=GEMINI_MODEL,
    instruction="""You are a System Architecture Designer.

Based on the project roadmap provided earlier, design a comprehensive system architecture.

Create a markdown document with these sections:

# System Architecture Design

## Architecture Pattern
[Choose: MVC, Microservices, Monolithic, Serverless, Event-Driven, or Layered]

## System Components
1. [Component 1]: [Description]
2. [Component 2]: [Description]
3. [Component 3]: [Description]

## Data Flow
[Describe how data flows through the system]

## Scalability Considerations
- [Scalability point 1]
- [Scalability point 2]

## Security Measures
- [Security measure 1]
- [Security measure 2]
- [Security measure 3]

## Architecture Diagram (Mermaid)
```mermaid
graph TD
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

Output clean, well-formatted markdown with a valid Mermaid diagram.""",
    description="Designs system architectures with diagrams",
    output_key="architecture_design"
)

# Agent 3: Code Analyzer - Markdown Output (uses parallel analysis results)
code_analyzer_agent = LlmAgent(
    name="CodeAnalyzer",
    model=GEMINI_MODEL,
    instruction="""You are a Code Quality Analyst.

Review the parallel analysis results and provide comprehensive code analysis.

Create a markdown document with:

# Code Analysis Report

## Quick Analysis Summary
{quick_analysis}

## Technology Research Findings
{tech_research}

## Best Practices Assessment
{best_practices}

## Code Complexity
- **Level**: [Low/Medium/High/Very High]
- **Quality Score**: [0-10]

## Strengths
- [Strength 1]
- [Strength 2]

## Issues Found
- [Issue 1]
- [Issue 2]

## Improvement Suggestions
1. [Suggestion 1]
2. [Suggestion 2]

## Refactored Code (if applicable)
```python
# Improved version
```

Output clean, well-formatted markdown.""",
    description="Performs comprehensive code analysis",
    output_key="code_analysis",
    tools=[analyze_code_complexity],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# Agent 4: Resource Curator - Markdown Output
resource_curator_agent = LlmAgent(
    name="ResourceCurator",
    model=GEMINI_MODEL,
    instruction="""You are a Learning Resource Curator.

Based on the project roadmap and architecture design, curate high-quality learning resources.

Create a markdown document with:

# Learning Resources

## Topic: [Main Topic]

## Recommended Resources

### 1. [Resource Title]
- **Type**: [Documentation/Tutorial/Course/Article]
- **Difficulty**: [Beginner/Intermediate/Advanced]
- **URL**: [URL]
- **Description**: [Brief description]

[Continue with 3-5 resources]

## Learning Path Recommendation
[Provide a suggested learning sequence and rationale]

Use Google Search to find current, relevant resources. Output clean markdown.""",
    description="Curates learning resources",
    output_key="learning_resources",
    tools=[google_search],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback
)

# ============================================================================
# CRITERION 4: HALLUCINATION MITIGATION - Validator Agent
# ============================================================================

validator_agent = LlmAgent(
    name="ValidationAgent",
    model=GEMINI_MODEL,
    instruction="""You are a Validation and Quality Assurance Agent responsible for detecting hallucinations and ensuring accuracy.

Review ALL previous agent outputs and validate their quality.

Create a markdown validation report:

# Validation Report

## Validation Status
✅ **PASSED** / ⚠️ **WARNINGS** / ❌ **FAILED**

## Confidence Score
[0.0 - 1.0]: [Your assessment]

## Validation Checklist

### Factual Accuracy
- [ ] Claims are verifiable and realistic
- [ ] Technologies mentioned are real and current
- [ ] URLs (if any) are valid

### Consistency
- [ ] Outputs align with each other
- [ ] No contradictions between agents
- [ ] Terminology is consistent

### Completeness
- [ ] All required sections present
- [ ] Adequate detail provided
- [ ] No placeholder text remaining

### Hallucination Detection
❌ **Hallucinations Detected**: Yes / No

**Details**: [List any fabricated information, fake URLs, or unrealistic claims]

## Recommended Corrections
1. [Correction 1]
2. [Correction 2]

## Overall Assessment
[2-3 sentence summary of validation]

Be strict but fair in your assessment. Output clean markdown.""",
    description="Validates outputs and detects hallucinations",
    output_key="validation_result"
)

# ============================================================================
# CRITERION 1: MEMORY - Sequential Agent with State Management
# ============================================================================

# Main Sequential Pipeline
main_pipeline = SequentialAgent(
    name="MainPipeline",
    sub_agents=[
        planner_agent,           # 1. Creates roadmap → stores in state
        parallel_analysis_group, # 2. Parallel analysis → stores results in state
        architect_agent,         # 3. Uses roadmap from state
        code_analyzer_agent,     # 4. Uses parallel results from state
        resource_curator_agent,  # 5. Uses roadmap + architecture from state
        validator_agent          # 6. Validates all outputs from state
    ],
    description="Sequential pipeline with state management and parallel execution"
)

# Root Agent - Entry point for 'adk web' command
root_agent = main_pipeline

# Export
__all__ = ['root_agent']
