from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.llm import LLM
from typing import List
import os
from dotenv import load_dotenv

# Import tools
from software_engineering_mentor.tools.complexity_analyzer import CodeComplexityTool, ResourceQualityTool
try:
    from crewai_tools import SerperDevTool, FileReadTool
    CREWAI_TOOLS_AVAILABLE = True
except ImportError:
    CREWAI_TOOLS_AVAILABLE = False
    print("⚠️ Warning: crewai-tools not installed. Some tools will not be available.")
    print("   Install with: pip install 'crewai[tools]'")

# Load environment variables
load_dotenv()

# Workaround for Ollama provider config mismatch causing 'supports_stop_words' error
try:
    from crewai.cli.constants import ENV_VARS
    for entry in ENV_VARS.get("ollama", []):
        if isinstance(entry, dict) and "API_BASE" in entry:
            entry["BASE_URL"] = entry.pop("API_BASE")
    
    # Add Groq provider configuration
    if "groq" not in ENV_VARS:
        ENV_VARS["groq"] = [
            {"GROQ_API_KEY": "GROQ_API_KEY"},
            {"GROQ_MODEL": "GROQ_MODEL"}
        ]
except Exception:
    # Silently ignore if structure changes or import not present
    pass
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class SoftwareEngineeringMentor():
    """SoftwareEngineeringMentor crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def _default_llm(self):
        """Resolve a default LLM provider/model from environment variables."""
        # Check for Gemini API key (using the exact variable name from .env file)
        gemini_key = os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("MODEL")
        
        # Also check for other providers as fallback
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        ollama_base = os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_API_BASE") or os.getenv("OLLAMA_HOST")

        if gemini_key and model_name:
            # Use the exact MODEL and GEMINI_API_KEY from .env file
            # Check if model_name already has the provider prefix
            if not model_name.startswith("gemini/"):
                model_name = f"gemini/{model_name}"
            return LLM(
                model=model_name,
                api_key=gemini_key
            )
        if groq_key:
            return LLM(
                model="groq/" + os.getenv('GROQ_MODEL', 'gemma2-9b-it'),
                api_key=groq_key
            )
        if openai_key:
            return LLM(
                model=os.getenv('OPENAI_MODEL_NAME', 'gpt-4o-mini'),
                api_key=openai_key
            )
        if google_key:
            return LLM(
                model=os.getenv('GOOGLE_MODEL_NAME', 'gemini-1.5-flash'),
                api_key=google_key
            )
        if anthropic_key:
            return LLM(
                model=os.getenv('ANTHROPIC_MODEL_NAME', 'claude-3-sonnet-20240229'),
                api_key=anthropic_key
            )
        if ollama_base:
            return LLM(
                model=os.getenv('OLLAMA_MODEL', 'llama3.1'),
                base_url=ollama_base
            )
        # Fallback raises to surface misconfiguration clearly
        raise RuntimeError("No LLM provider configured. Set GEMINI_API_KEY and MODEL in .env file, or set GROQ_API_KEY, OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, or OLLAMA_BASE_URL")

    def _with_default_llm(self, agent_key: str) -> dict:
        cfg = dict(self.agents_config[agent_key])  # type: ignore[index]
        if "llm" not in cfg or not cfg.get("llm"):
            cfg["llm"] = self._default_llm()
        return cfg

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def planner_agent(self) -> Agent:
        return Agent(config=self._with_default_llm('planner_agent'), verbose=True)

    @agent
    def architect_agent(self) -> Agent:
        return Agent(config=self._with_default_llm('architect_agent'), verbose=True)

    @agent
    def resource_curator_agent(self) -> Agent:
        tools = []
        if CREWAI_TOOLS_AVAILABLE:
            tools.append(SerperDevTool())
        tools.append(ResourceQualityTool())
        return Agent(
            config=self._with_default_llm('resource_curator_agent'), 
            verbose=True,
            tools=tools
        )

    @agent
    def code_explainer_agent(self) -> Agent:
        tools = []
        if CREWAI_TOOLS_AVAILABLE:
            tools.append(FileReadTool())
        tools.append(CodeComplexityTool())
        return Agent(
            config=self._with_default_llm('code_explainer_agent'), 
            verbose=True,
            tools=tools
        )

    @agent
    def prompt_coach_agent(self) -> Agent:
        return Agent(config=self._with_default_llm('prompt_coach_agent'), verbose=True)

    @agent
    def visualizer_agent(self) -> Agent:
        return Agent(config=self._with_default_llm('visualizer_agent'), verbose=True)

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def plan_task(self) -> Task:
        return Task(
            config=self.tasks_config['plan_task'], # type: ignore[index]
        )

    @task
    def architect_task(self) -> Task:
        return Task(
            config=self.tasks_config['architect_task'], # type: ignore[index]
        )

    @task
    def resource_task(self) -> Task:
        return Task(
            config=self.tasks_config['resource_task'], # type: ignore[index]
            async_execution=True
        )

    @task
    def explain_task(self) -> Task:
        return Task(
            config=self.tasks_config['explain_task'], # type: ignore[index]
            async_execution=True
        )

    @task
    def prompt_task(self) -> Task:
        return Task(
            config=self.tasks_config['prompt_task'], # type: ignore[index]
            async_execution=True
        )

    @task
    def visualize_task(self) -> Task:
        return Task(
            config=self.tasks_config['visualize_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the SoftwareEngineeringMentor crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
