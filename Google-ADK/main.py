#!/usr/bin/env python
"""
Software Engineering Mentor - Google ADK Implementation
Command-line interface with Markdown report generation and JSON logging

LAB Assignment-2 Requirements:
- Runs agent pipeline with user input
- Generates markdown reports in reports/
- Creates execution logs as JSON in logs/
- Demonstrates all 6 criteria in action

Run: python main.py
Run Test: python main.py --test
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Import the root agent
from agent import root_agent

# Load environment variables
load_dotenv()

# ============================================================================
# WORKFLOW MEMORY - CRITERION 6: Task Monitoring & Logging (JSON)
# ============================================================================

class WorkflowMemory:
    """Shared memory and execution tracker for agent workflow."""
    
    def __init__(self):
        self.data: Dict[str, Any] = {
            "query": None,
            "project_roadmap": None,
            "quick_analysis": None,
            "tech_research": None,
            "best_practices": None,
            "architecture_design": None,
            "code_analysis": None,
            "learning_resources": None,
            "validation_result": None,
            "final_report": None,
            "execution_logs": [],
            "tool_calls": [],
        }
    
    def store(self, key: str, value: Any):
        """Store data in workflow memory."""
        self.data[key] = value
        self.log_event(f"Stored '{key}'", "INFO")
    
    def retrieve(self, key: str) -> Any:
        """Retrieve data from workflow memory."""
        return self.data.get(key)
    
    def log_event(self, message: str, level: str = "INFO"):
        """Log an event with timestamp and level."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
        }
        self.data["execution_logs"].append(log_entry)
        print(f"[{level}] {message}")
    
    def log_tool_call(self, tool_name: str, args: Dict[str, Any], result: Any = None):
        """Log a tool execution."""
        tool_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": args,
            "result": str(result)[:200] if result else None,  # Truncate long results
        }
        self.data["tool_calls"].append(tool_entry)
        self.log_event(f"Tool executed: {tool_name}", "INFO")
    
    def export_report(self, filename: str = None):
        """Export workflow state as JSON."""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"logs/workflow_state_{timestamp}.json"
        
        # Ensure logs directory exists
        Path("logs").mkdir(exist_ok=True)
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        
        self.log_event(f"Workflow state exported to {filename}", "INFO")
        return filename

# ============================================================================
# REPORT GENERATION
# ============================================================================

def save_report_as_md(markdown_output: str, inputs: dict, workflow_memory: WorkflowMemory):
    """
    Save the agent's markdown output as a report file.
    
    Args:
        markdown_output: The combined markdown from all agents
        inputs: User input dictionary
        workflow_memory: Workflow memory instance
    """
    # Create reports directory
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = reports_dir / f"adk_mentor_report_{timestamp}.md"
    
    # Create formatted markdown report
    report_content = f"""# Software Engineering Mentor - Analysis Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Framework:** Google ADK (Agent Development Kit)  
**Model:** gemini-2.0-flash-thinking-exp-01-21

---

## 📝 User Input

**Query:**
{inputs['query']}

---

## 🤖 AI Agent Analysis

{markdown_output}

---

## 📊 Execution Summary

- **Total Agents Executed:** 6 agents (1 sequential pipeline + 3 parallel + 2 sequential)
  1. ProjectPlanner (sequential)
  2. ParallelAnalysisGroup (3 concurrent agents)
     - QuickCodeAnalyzer
     - TechnologyResearcher
     - BestPracticesAdvisor
  3. SystemArchitect (sequential)
  4. CodeAnalyzer (sequential)
  5. ResourceCurator (sequential)
  6. ValidationAgent (sequential - hallucination detection)

- **Tools Used:**
  - google_search (external tool)
  - analyze_code_complexity (custom tool)
  - store_user_context (custom tool)

- **State Management:** All agents share state via output_key mechanism
- **Validation:** Final ValidationAgent checks for hallucinations

- **Total Events Logged:** {len(workflow_memory.data['execution_logs'])}
- **Total Tool Calls:** {len(workflow_memory.data['tool_calls'])}

---

**Report File:** {filename}  
**Session Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    # Write to file
    try:
        filename.write_text(report_content, encoding='utf-8')
        workflow_memory.log_event(f"Report saved to {filename}", "INFO")
        
        print(f"\n{'='*80}")
        print(f"📄 Report saved: {filename}")
        print(f"{'='*80}\n")
        
        return filename
    except Exception as e:
        workflow_memory.log_event(f"Failed to save report: {e}", "ERROR")
        print(f"❌ WARNING: Could not save report to .md file: {e}")
        return None

# ============================================================================
# USER INPUT HANDLING
# ============================================================================

def get_user_input(workflow_memory: WorkflowMemory) -> dict:
    """
    Get user input via interactive prompts.
    
    Returns:
        dict: User inputs
    """
    workflow_memory.log_event("USER INPUT COLLECTION", "INFO")
    
    print("\n" + "="*80)
    print("🎯 SOFTWARE ENGINEERING MENTOR - ADK Agent")
    print("="*80)
    print("\nThis agent will help you with:")
    print("  • Project planning and roadmaps")
    print("  • System architecture design")
    print("  • Code analysis and review")
    print("  • Technology recommendations")
    print("  • Learning resources curation")
    print("  • Validation and quality assurance")
    print("\n" + "="*80 + "\n")
    
    # Get project idea/query
    print("📋 What would you like help with?")
    print("   (e.g., 'Build a todo app', 'Review my Python code', 'Design an e-commerce system')")
    print()
    query = input("Your query: ").strip()
    
    if not query:
        query = "I want to build a simple todo list web application using React and Firebase"
        print(f"  → Using default: {query}")
    
    workflow_memory.log_event(f"User query received: {query[:50]}...", "INFO")
    
    inputs = {
        'query': query,
        'timestamp': datetime.now().isoformat()
    }
    
    # Store in workflow memory
    workflow_memory.store("query", query)
    
    return inputs

def get_test_input(workflow_memory: WorkflowMemory) -> dict:
    """
    Get predefined test input for quick testing.
    
    Returns:
        dict: Test inputs
    """
    workflow_memory.log_event("TEST MODE - Using predefined input", "INFO")
    
    query = """I want to build a task management web application with the following features:
- User authentication
- Create, read, update, delete tasks
- Task categories and tags
- Due dates and reminders
- Mobile responsive design

Please provide a comprehensive project plan, architecture, and technology recommendations."""
    
    print(f"\n🧪 TEST MODE - Using predefined query:\n{query}\n")
    
    inputs = {
        'query': query,
        'timestamp': datetime.now().isoformat()
    }
    
    # Store in workflow memory
    workflow_memory.store("query", query)
    
    return inputs

# ============================================================================
# AGENT EXECUTION
# ============================================================================

def run_agent(inputs: dict, workflow_memory: WorkflowMemory) -> str:
    """
    Execute the ADK agent with user input.
    
    Args:
        inputs: User input dictionary
        workflow_memory: Workflow memory instance
    
    Returns:
        str: Markdown output from agents
    """    
    workflow_memory.log_event("="*80, "INFO")
    workflow_memory.log_event("AGENT EXECUTION STARTED", "INFO")
    workflow_memory.log_event("="*80, "INFO")
    
    print("\n🚀 Starting agent pipeline...")
    print("   This will execute 6 agents in sequence with parallel analysis...\n")
    
    try:
        # Run the root agent with the query
        # Note: SequentialAgent uses .execute() method, not .run()
        workflow_memory.log_event(f"Executing root_agent.execute() with query", "INFO")
        response = root_agent.execute(inputs['query'])
        
        workflow_memory.log_event("Agent execution completed successfully", "INFO")
        
        # Extract markdown output
        # The response should contain all the markdown from the agents
        if hasattr(response, 'text'):
            markdown_output = response.text
        elif hasattr(response, 'content'):
            markdown_output = response.content
        elif isinstance(response, str):
            markdown_output = response
        else:
            # Fallback: try to get state outputs
            markdown_output = extract_markdown_from_state(response, workflow_memory)
        
        workflow_memory.log_event(f"Output length: {len(markdown_output)} characters", "INFO")
        
        # Store final output
        workflow_memory.store("final_report", markdown_output)
        
        return markdown_output
        
    except Exception as e:
        error_msg = f"❌ Error during agent execution: {str(e)}"
        workflow_memory.log_event(error_msg, "ERROR")
        print(f"\n{error_msg}\n")
        raise

def extract_markdown_from_state(response, workflow_memory: WorkflowMemory) -> str:
    """
    Extract markdown outputs from agent state if direct text not available.
    
    Args:
        response: Agent response object
        workflow_memory: Workflow memory instance
    
    Returns:
        str: Combined markdown from all agents
    """
    workflow_memory.log_event("Extracting markdown from agent state...", "INFO")
    
    markdown_parts = ["# Software Engineering Mentor - Comprehensive Analysis\n\n"]
    
    try:
        if hasattr(response, 'state'):
            state = response.state
            
            # Extract outputs from each agent
            state_keys = [
                'project_roadmap',
                'quick_analysis', 
                'tech_research',
                'best_practices',
                'architecture_design',
                'code_analysis',
                'learning_resources',
                'validation_result'
            ]
            
            for key in state_keys:
                if hasattr(state, key):
                    value = getattr(state, key)
                    markdown_parts.append(f"\n---\n\n")
                    markdown_parts.append(str(value))
                    workflow_memory.log_event(f"Extracted {key}: {len(str(value))} chars", "INFO")
                    
                    # Store in workflow memory
                    workflow_memory.store(key, str(value))
            
            return "".join(markdown_parts)
        
    except Exception as e:
        workflow_memory.log_event(f"Could not extract from state: {e}", "WARNING")
    
    # Fallback
    return str(response)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function with WorkflowMemory for JSON logging.
    """
    # Initialize workflow memory
    workflow_memory = WorkflowMemory()
    workflow_memory.log_event("="*80, "INFO")
    workflow_memory.log_event("SOFTWARE ENGINEERING MENTOR - ADK Agent Started", "INFO")
    workflow_memory.log_event("="*80, "INFO")
    
    try:
        # Check if test mode
        test_mode = '--test' in sys.argv
        
        # Get user input
        if test_mode:
            inputs = get_test_input(workflow_memory)
        else:
            inputs = get_user_input(workflow_memory)
        
        # Run the agent
        markdown_output = run_agent(inputs, workflow_memory)
        
        # Save markdown report
        report_file = save_report_as_md(markdown_output, inputs, workflow_memory)
        
        # Export workflow state as JSON
        workflow_state_file = workflow_memory.export_report()
        
        # Success summary
        workflow_memory.log_event("="*80, "INFO")
        workflow_memory.log_event("EXECUTION COMPLETED SUCCESSFULLY", "INFO")
        workflow_memory.log_event("="*80, "INFO")
        workflow_memory.log_event(f"Markdown Report: {report_file}", "INFO")
        workflow_memory.log_event(f"JSON Workflow State: {workflow_state_file}", "INFO")
        
        print("\n" + "="*80)
        print("✅ SUCCESS! Agent execution completed.")
        print("="*80)
        print(f"📄 Markdown Report: {report_file}")
        print(f"📊 JSON Workflow State: {workflow_state_file}")
        print(f"📁 Check reports/ and logs/ directories")
        print("="*80 + "\n")
        
        return 0
        
    except KeyboardInterrupt:
        workflow_memory.log_event("\n⚠️  Execution interrupted by user", "WARNING")
        print("\n⚠️  Execution interrupted by user\n")
        return 130
        
    except Exception as e:
        workflow_memory.log_event(f"\n❌ Fatal error: {str(e)}", "ERROR")
        print(f"\n❌ Fatal error: {str(e)}")
        print("   Check logs/ directory for details\n")
        
        # Still export workflow state even on error
        try:
            workflow_memory.export_report()
        except:
            pass
        
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
