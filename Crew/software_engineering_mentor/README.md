# AI-Powered Software Engineering Mentor

Welcome to the Software Engineering Mentor project, powered by [CrewAI](https://crewai.com). This multi-agent AI system provides comprehensive guidance for software development projects through specialized AI agents that collaborate to deliver project planning, architecture design, code analysis, and learning resources.

## 🤖 Features

This platform includes **6 specialized AI agents**:

- **📋 Planner Agent**: Generates comprehensive project roadmaps with milestones and deliverables
- **🏗️ Architect Agent**: Designs system architecture with Mermaid diagrams
- **📚 Resource Curator Agent**: Curates high-quality learning resources for each milestone
- **🔍 Code Explainer Agent**: Analyzes code snippets and provides improvement suggestions
- **💡 Prompt Coach Agent**: Teaches effective AI tool prompt engineering
- **📊 Visualizer Agent**: Creates visual diagrams and workflow representations

## 🚀 Quick Start

### Prerequisites

- Python >=3.10 <3.14
- API key from at least one provider (OpenAI, Anthropic, or Google)

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd Assignment-1-CrewAI/software_engineering_mentor
   ```

2. **Activate the virtual environment:**
   ```bash
   # Windows
   ..\crew-venv\Scripts\activate
   
   # macOS/Linux
   source ../crew-venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys
   # You need at least one provider key:
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   ANTHROPIC_API_KEY=your_anthropic_api_key_here  
   # OR
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## 🎯 Running the Application

### Option 1: Streamlit Web Interface (Recommended)

Launch the interactive web interface:

```bash
streamlit run streamlit_app.py
```

This opens a web interface where you can:
- Enter project ideas and get complete analysis
- Run individual workflows (planning, architecture, etc.)
- Analyze code snippets
- Get prompt coaching for AI tools
- Curate learning resources

### Option 2: Command Line Interface

Run the crew directly:

```bash
crewai run
```

This executes the default workflow with sample inputs.

### Option 3: Python Script

Run the main Python script:

```bash
python src/software_engineering_mentor/main.py
```

## 📁 Project Structure

```
software_engineering_mentor/
├── src/software_engineering_mentor/
│   ├── config/
│   │   ├── agents.yaml          # Agent definitions
│   │   └── tasks.yaml           # Task definitions
│   ├── crew.py                  # Crew orchestration
│   ├── main.py                  # Entry point
│   └── tools/                   # Custom tools
├── streamlit_app.py             # Web interface
├── .env                         # Environment variables (create from .env.example)
├── README.md                   # This file
└── tests/                      # Test files
```

## 🔧 Customization

### Adding New Agents

1. **Define the agent** in `src/software_engineering_mentor/config/agents.yaml`:
   ```yaml
   my_new_agent:
     role: >
       My New Agent Role
     goal: >
       What this agent should achieve
     backstory: >
       Background and expertise of the agent
   ```

2. **Add the agent method** in `src/software_engineering_mentor/crew.py`:
   ```python
   @agent
   def my_new_agent(self) -> Agent:
       return Agent(
           config=self.agents_config['my_new_agent'],
           verbose=True
       )
   ```

### Adding New Tasks

1. **Define the task** in `src/software_engineering_mentor/config/tasks.yaml`:
   ```yaml
   my_new_task:
     description: >
       What this task should do
     expected_output: >
       Expected output format
     agent: my_new_agent
   ```

2. **Add the task method** in `src/software_engineering_mentor/crew.py`:
   ```python
   @task
   def my_new_task(self) -> Task:
       return Task(
           config=self.tasks_config['my_new_task']
       )
   ```

## 🎨 Workflow Examples

### Complete Project Analysis
Input: "Build a cross-platform note-taking app with offline sync"
Output: Complete roadmap, architecture, resources, and visualizations

### Code Explanation
Input: Code snippet
Output: Detailed explanation, issues identified, improvement suggestions

### Prompt Coaching
Input: "Implement user authentication with JWT tokens"
Output: Refined prompts for AI coding tools with examples

## 🔍 Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure your `.env` file has valid API keys
2. **Import Errors**: Make sure you're in the correct directory and virtual environment is activated
3. **Dependency Issues**: Run `pip install -r ../requirements.txt` to ensure all packages are installed

### Getting Help

- Check the [CrewAI Documentation](https://docs.crewai.com)
- Visit the [CrewAI GitHub Repository](https://github.com/joaomdmoura/crewai)
- Join the [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)

## 📝 License

This project is part of the Generative AI Agents course assignment. Please refer to your course guidelines for usage and distribution policies.

---

**Happy coding with AI assistance! 🤖✨**
