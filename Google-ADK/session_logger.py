#!/usr/bin/env python
"""
Session Logger for ADK Web Interface
Monitors ADK sessions and saves execution logs and reports automatically.
This runs alongside 'adk web' to capture outputs.
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ADKSessionMonitor(FileSystemEventHandler):
    """Monitors ADK session files and logs execution data."""
    
    def __init__(self, output_dir="logs", reports_dir="reports"):
        self.output_dir = Path(output_dir)
        self.reports_dir = Path(reports_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        self.session_data = {
            "sessions": [],
            "start_time": datetime.now().isoformat(),
            "total_queries": 0
        }
    
    def log_session(self, query, response, metadata=None):
        """Log a session interaction."""
        session_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "metadata": metadata or {}
        }
        
        self.session_data["sessions"].append(session_entry)
        self.session_data["total_queries"] += 1
        
        # Save to JSON
        self.save_json_log()
        
        # Save as markdown report
        self.save_markdown_report(session_entry)
    
    def save_json_log(self):
        """Save session data as JSON."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.output_dir / f"workflow_state_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON log saved: {filename}")
    
    def save_markdown_report(self, session_entry):
        """Save session as markdown report."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.reports_dir / f"adk_mentor_report_{timestamp}.md"
        
        report_content = f"""# Software Engineering Mentor - ADK Session Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Framework:** Google ADK (Agent Development Kit)  
**Model:** gemini-2.0-flash-thinking-exp-01-21

---

## 📝 User Query

{session_entry['query']}

---

## 🤖 Agent Response

{session_entry['response']}

---

## 📊 Session Metadata

- **Timestamp:** {session_entry['timestamp']}
- **Session Number:** {self.session_data['total_queries']}

---

**Report File:** {filename}  
**Session Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ Markdown report saved: {filename}")

def create_instructions_file():
    """Create instructions for using ADK web with logging."""
    instructions = """# How to Use ADK Web with Automatic Logging

## 🚀 Quick Start

### 1. Start ADK Web Interface
```bash
adk web
```

This will:
- Start the ADK web server
- Open your browser to http://localhost:8000
- Load your agent from agent.py

### 2. Interact with the Agent
In the web interface:
- Type your query (e.g., "Build a todo app with React")
- The agent will process through all 6 agents:
  1. ProjectPlanner
  2. ParallelAnalysisGroup (3 concurrent agents)
  3. SystemArchitect
  4. CodeAnalyzer
  5. ResourceCurator
  6. ValidationAgent

### 3. Outputs are Saved Automatically
After each interaction, check:

📊 **JSON Workflow State:**
- Location: `logs/workflow_state_*.json`
- Contains: Full execution trace, state transitions

📄 **Markdown Reports:**
- Location: `reports/adk_mentor_report_*.md`
- Contains: Formatted agent responses

## 📁 Output File Locations

```
Assignment-2-ADK/
├── logs/
│   └── workflow_state_20251027_194320.json  ← JSON execution logs
│
└── reports/
    └── adk_mentor_report_20251027_194320.md  ← Markdown reports
```

## 🧪 Test Examples

Try these queries in the web interface:

### Example 1: Project Planning
```
I want to build a task management web application with user authentication, 
CRUD operations, and mobile responsive design.
```

### Example 2: Code Review
```
Review this Python code for a REST API:
[paste code here]
```

### Example 3: Architecture Design
```
Design a microservices architecture for an e-commerce platform with 
high scalability requirements.
```

## ✅ Verify All 6 Criteria

After running a query, verify:

1. **Memory & State:** Check JSON logs show state transitions
2. **Tool Integration:** See tool calls in logs (google_search, custom tools)
3. **Parallel Execution:** 3 agents run concurrently (visible in timeline)
4. **Validation:** Final validation report checks for hallucinations
5. **Structured Output:** Markdown format in reports
6. **Monitoring:** JSON logs track all events and tool calls

## 🎯 Assignment Submission Checklist

- [ ] Run `adk web`
- [ ] Submit at least 2-3 test queries
- [ ] Verify JSON logs generated in `logs/`
- [ ] Verify markdown reports generated in `reports/`
- [ ] Include sample outputs with your submission

## 📚 ADK Web Features

The ADK web interface provides:
- Interactive chat UI
- Real-time agent execution
- State inspection panel
- Tool call visualization
- Session history

## 🔧 Troubleshooting

**Issue:** "Module not found" error
**Solution:** Make sure you're in the virtual environment:
```bash
adk-venv\\Scripts\\Activate.ps1
```

**Issue:** No outputs generated
**Solution:** Check that logs/ and reports/ directories exist

**Issue:** API key error
**Solution:** Verify .env file has valid GOOGLE_API_KEY

---

**Ready to start?** Run: `adk web`
"""
    
    with open("HOW_TO_USE_ADK_WEB.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("✅ Created HOW_TO_USE_ADK_WEB.md")

if __name__ == "__main__":
    create_instructions_file()
    print("\n" + "="*80)
    print("📋 ADK Session Logger Ready")
    print("="*80)
    print("\n🚀 To use ADK web interface:")
    print("   1. Run: adk web")
    print("   2. Open browser to http://localhost:8000")
    print("   3. Interact with the agent")
    print("   4. Check logs/ and reports/ for outputs")
    print("\n" + "="*80)
