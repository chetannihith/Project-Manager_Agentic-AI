#!/usr/bin/env python
import sys
import warnings
import os
from pathlib import Path

from datetime import datetime

from software_engineering_mentor.crew import SoftwareEngineeringMentor

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew with custom user input.
    """
    print("\n" + "="*70)
    print("🤖 AI-Powered Software Engineering Mentor")
    print("="*70 + "\n")
    
    # Get custom input from user
    print("Please provide the following information:\n")
    
    project_idea = input("📋 Enter your software project idea:\n> ").strip()
    if not project_idea:
        project_idea = "Build a cross-platform note-taking app with offline sync and real-time collaboration features"
        print(f"   (Using default: {project_idea})")
    
    print("\n💻 Enter code snippet to analyze (press Enter twice when done, or skip):")
    code_lines = []
    while True:
        line = input()
        if line == "" and code_lines and code_lines[-1] == "":
            code_lines.pop()  # Remove the last empty line
            break
        elif line == "" and not code_lines:
            break
        code_lines.append(line)
    
    code_snippet = "\n".join(code_lines) if code_lines else "No code snippet provided"
    
    print("\n🎯 Enter your coding goal (or press Enter to skip):")
    coding_goal = input("> ").strip()
    if not coding_goal:
        coding_goal = "No specific coding goal provided"
    
    inputs = {
        'project_idea': project_idea,
        'code_snippet': code_snippet,
        'coding_goal': coding_goal
    }
    
    print("\n" + "="*70)
    print("🚀 Starting crew analysis...")
    print("="*70 + "\n")

    try:
        result = SoftwareEngineeringMentor().crew().kickoff(inputs=inputs)
        print("\n" + "="*70)
        print("✅ Crew execution completed successfully!")
        print("="*70 + "\n")
        
        # Save result as MD file
        save_result_as_md(result, inputs)
        
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def save_result_as_md(result, inputs):
    """
    Save the crew execution result as a Markdown file.
    """
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = reports_dir / f"crew_analysis_report_{timestamp}.md"
    
    # Extract result text
    result_text = result.raw if hasattr(result, 'raw') else str(result)
    
    # Add header with metadata and inputs
    md_content = f"""# Software Engineering Mentor - Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Input Parameters

### Project Idea
{inputs['project_idea']}

### Code Snippet
```
{inputs['code_snippet']}
```

### Coding Goal
{inputs['coding_goal']}

---

## Analysis Results

{result_text}
"""
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✅ Report saved as: {filename.absolute()}")
    print(f"📄 You can find your report at: {filename.absolute()}\n")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "project_idea": "Build a cross-platform note-taking app with offline sync and real-time collaboration features",
        "code_snippet": '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
        ''',
        "coding_goal": "Implement user authentication with JWT tokens"
    }
    try:
        SoftwareEngineeringMentor().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        SoftwareEngineeringMentor().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "project_idea": "Build a cross-platform note-taking app with offline sync and real-time collaboration features",
        "code_snippet": '''
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price
    return total
        ''',
        "coding_goal": "Implement user authentication with JWT tokens"
    }

    try:
        SoftwareEngineeringMentor().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "project_idea": "",
        "code_snippet": "",
        "coding_goal": ""
    }

    try:
        result = SoftwareEngineeringMentor().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
