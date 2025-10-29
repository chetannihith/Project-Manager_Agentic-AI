"""
Enhanced Session Manager with Monitoring and Logging
LAB Assignment-2 - Task Monitoring & Logging Implementation

This module provides comprehensive monitoring, logging, and state management
for the ADK multi-agent workflow.
"""

import asyncio
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types


# ====================================================================================
# LOGGING CONFIGURATION
# ====================================================================================

# Create logs directory (absolute path to ensure it's created correctly)
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure structured logging with unique timestamp
log_filename = LOGS_DIR / f'agent_execution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Create custom logger for this module
logger = logging.getLogger("ADK_Monitor")
logger.setLevel(logging.INFO)

# Only configure if no handlers exist (avoid duplicate handlers)
if not logger.handlers:
    # File handler - writes to log file
    file_handler = logging.FileHandler(log_filename, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler - prints to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log initialization
    logger.info("=" * 80)
    logger.info("🚀 ENHANCED SESSION MANAGER INITIALIZED")
    logger.info(f"📁 Log file: {log_filename}")
    logger.info(f"📂 Logs directory: {LOGS_DIR.absolute()}")
    logger.info("=" * 80)


# ====================================================================================
# EXECUTION MONITOR
# ====================================================================================

class ExecutionMonitor:
    """
    Monitors and logs agent execution with detailed tracking
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.execution_log = []
        self.agent_timings = {}
        self.errors = []
        self.start_time = None
        self.end_time = None
        
    def start_execution(self, user_query: str):
        """Start monitoring an execution"""
        self.start_time = datetime.now()
        log_entry = {
            "timestamp": self.start_time.isoformat(),
            "session_id": self.session_id,
            "event_type": "EXECUTION_START",
            "query": user_query[:200],  # Truncate long queries
        }
        self.execution_log.append(log_entry)
        logger.info(f"🚀 Execution started for session {self.session_id}")
        logger.info(f"Query: {user_query[:100]}...")
        
    def log_agent_start(self, agent_name: str):
        """Log when an agent starts"""
        timestamp = datetime.now()
        self.agent_timings[agent_name] = {"start": timestamp}
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "event_type": "AGENT_START",
            "agent_name": agent_name,
        }
        self.execution_log.append(log_entry)
        logger.info(f"  ▶️  Agent started: {agent_name}")
        
    def log_agent_end(self, agent_name: str, output_preview: str = ""):
        """Log when an agent completes"""
        timestamp = datetime.now()
        
        if agent_name in self.agent_timings:
            start_time = self.agent_timings[agent_name]["start"]
            duration = (timestamp - start_time).total_seconds()
            self.agent_timings[agent_name]["end"] = timestamp
            self.agent_timings[agent_name]["duration_seconds"] = duration
        else:
            duration = 0
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "event_type": "AGENT_COMPLETE",
            "agent_name": agent_name,
            "duration_seconds": duration,
            "output_preview": output_preview[:100],
        }
        self.execution_log.append(log_entry)
        logger.info(f"  ✅ Agent completed: {agent_name} (Duration: {duration:.2f}s)")
        
    def log_tool_use(self, agent_name: str, tool_name: str, tool_input: str):
        """Log when an agent uses a tool"""
        timestamp = datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "event_type": "TOOL_USE",
            "agent_name": agent_name,
            "tool_name": tool_name,
            "tool_input": str(tool_input)[:200],
        }
        self.execution_log.append(log_entry)
        logger.info(f"  🔧 Tool used: {tool_name} by {agent_name}")
        
    def log_error(self, agent_name: str, error: Exception):
        """Log an error"""
        timestamp = datetime.now()
        error_info = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "agent_name": agent_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
        }
        self.errors.append(error_info)
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "session_id": self.session_id,
            "event_type": "ERROR",
            "agent_name": agent_name,
            "error": error_info,
        }
        self.execution_log.append(log_entry)
        logger.error(f"  ❌ Error in {agent_name}: {str(error)}")
        
    def end_execution(self, success: bool = True):
        """End monitoring an execution"""
        self.end_time = datetime.now()
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        log_entry = {
            "timestamp": self.end_time.isoformat(),
            "session_id": self.session_id,
            "event_type": "EXECUTION_END",
            "success": success,
            "total_duration_seconds": total_duration,
            "agents_executed": len(self.agent_timings),
            "errors_count": len(self.errors),
        }
        self.execution_log.append(log_entry)
        
        logger.info(f"🏁 Execution ended for session {self.session_id}")
        logger.info(f"Total duration: {total_duration:.2f}s")
        logger.info(f"Agents executed: {len(self.agent_timings)}")
        logger.info(f"Errors: {len(self.errors)}")
        
    def get_execution_report(self) -> Dict:
        """Generate comprehensive execution report"""
        if not self.start_time or not self.end_time:
            return {"error": "Execution not completed"}
        
        total_duration = (self.end_time - self.start_time).total_seconds()
        
        # Calculate agent statistics
        agent_stats = []
        for agent_name, timing in self.agent_timings.items():
            agent_stats.append({
                "agent_name": agent_name,
                "duration_seconds": timing.get("duration_seconds", 0),
                "start_time": timing["start"].isoformat(),
                "end_time": timing.get("end", datetime.now()).isoformat(),
            })
        
        # Sort by duration
        agent_stats.sort(key=lambda x: x["duration_seconds"], reverse=True)
        
        report = {
            "session_id": self.session_id,
            "execution_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "total_duration_seconds": total_duration,
                "total_agents": len(self.agent_timings),
                "total_errors": len(self.errors),
                "success": len(self.errors) == 0,
            },
            "agent_performance": agent_stats,
            "errors": self.errors,
            "event_count": len(self.execution_log),
            "full_log": self.execution_log,
        }
        
        return report
    
    def save_report(self, filepath: Optional[Path] = None):
        """Save execution report to JSON file"""
        if filepath is None:
            filepath = LOGS_DIR / f'execution_report_{self.session_id}.json'
        
        report = self.get_execution_report()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Execution report saved to: {filepath}")
        return filepath


# ====================================================================================
# ENHANCED SESSION MANAGER
# ====================================================================================

class EnhancedADKSessionManager:
    """
    Enhanced ADK Session Manager with:
    - Memory/State management
    - Comprehensive monitoring
    - Detailed logging
    - Execution tracking
    """
    
    def __init__(self, app_name: str = "software_engineering_mentor"):
        self.app_name = app_name
        self.session_service = None
        self.runner = None
        self._session_initialized = False
        self.monitors = {}  # Session ID -> ExecutionMonitor
        
    async def initialize(self, agent):
        """Initialize session service and runner with agent"""
        if not self._session_initialized:
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                agent=agent,
                session_service=self.session_service
            )
            self._session_initialized = True
            logger.info("✅ Session manager initialized")
    
    async def create_session_with_state(
        self,
        user_id: str = "user",
        session_id: Optional[str] = None,
        initial_state: Optional[Dict] = None
    ):
        """
        Create session with initial state for memory management
        
        State structure:
        {
            "project_name": "",
            "user_requirements": "",
            "complexity_analysis": {},
            "project_roadmap": "",
            "architecture_design": "",
            "validated_tech_stack": {},
            "curated_resources": [],
            "code_examples": [],
            "best_practices": [],
            "prompt_templates": [],
            "visual_diagrams": "",
            "validation_report": {},
            "final_approval": ""
        }
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Default state structure
        default_state = {
            "project_name": "",
            "user_requirements": "",
            "complexity_analysis": {},
            "project_roadmap": "",
            "architecture_design": "",
            "validated_tech_stack": {},
            "curated_resources": [],
            "code_examples": [],
            "best_practices": [],
            "prompt_templates": [],
            "visual_diagrams": "",
            "validation_report": {},
            "final_approval": "",
            "execution_metadata": {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
            }
        }
        
        # Merge with initial state if provided
        if initial_state:
            default_state.update(initial_state)
        
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
            state=default_state
        )
        
        logger.info(f"📝 Session created: {session_id} for user: {user_id}")
        return session
    
    async def send_message_with_monitoring(
        self,
        query: str,
        user_id: str = "user",
        session_id: Optional[str] = None,
        agent = None
    ) -> tuple[str, Dict]:
        """
        Send message with comprehensive monitoring and logging
        
        Returns: (response_text, execution_report)
        """
        if not self._session_initialized and agent:
            await self.initialize(agent)
        
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Create execution monitor
        monitor = ExecutionMonitor(session_id)
        self.monitors[session_id] = monitor
        
        # Start monitoring
        monitor.start_execution(query)
        
        try:
            # Create or get session with state
            try:
                session = await self.session_service.get_session(
                    app_name=self.app_name,
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"📥 Retrieved existing session: {session_id}")
            except:
                # Create new session with initial state
                initial_state = {"user_requirements": query}
                session = await self.create_session_with_state(
                    user_id=user_id,
                    session_id=session_id,
                    initial_state=initial_state
                )
            
            # Create message content
            content = types.Content(
                role="user",
                parts=[types.Part(text=query)]
            )
            
            # Run agent with monitoring
            response_text = ""
            current_agent = None
            
            events = self.runner.run(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            )
            
            for event in events:
                # Log different event types
                if hasattr(event, 'agent_name'):
                    if current_agent != event.agent_name:
                        if current_agent:
                            monitor.log_agent_end(current_agent)
                        current_agent = event.agent_name
                        monitor.log_agent_start(current_agent)
                
                # Check for tool usage
                if hasattr(event, 'tool_name') and event.tool_name:
                    tool_input = getattr(event, 'tool_input', '')
                    monitor.log_tool_use(
                        current_agent or "unknown",
                        event.tool_name,
                        str(tool_input)
                    )
                
                # Capture final response
                if event.is_final_response():
                    if event.content and event.content.parts:
                        response_text = event.content.parts[0].text
                        if current_agent:
                            monitor.log_agent_end(current_agent, response_text[:100])
                        break
            
            # End monitoring successfully
            monitor.end_execution(success=True)
            
            # Save execution report
            report_path = monitor.save_report()
            
            # Get execution report
            execution_report = monitor.get_execution_report()
            
            return response_text, execution_report
            
        except Exception as e:
            # Log error and end monitoring with failure
            monitor.log_error(current_agent or "unknown", e)
            monitor.end_execution(success=False)
            monitor.save_report()
            logger.error(f"❌ Execution failed: {str(e)}")
            raise
    
    async def get_session_state(self, user_id: str, session_id: str) -> Dict:
        """Get current session state"""
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        return dict(session.state)
    
    async def update_session_state(
        self,
        user_id: str,
        session_id: str,
        state_updates: Dict
    ):
        """Update session state"""
        session = await self.session_service.get_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )
        
        # Update state
        current_state = dict(session.state)
        current_state.update(state_updates)
        
        # Save updated session
        await self.session_service.update_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
            state=current_state
        )
        
        logger.info(f"📝 Session state updated: {session_id}")


# Singleton instance
_enhanced_session_manager = None


def get_enhanced_session_manager() -> EnhancedADKSessionManager:
    """Get or create singleton enhanced session manager"""
    global _enhanced_session_manager
    if _enhanced_session_manager is None:
        _enhanced_session_manager = EnhancedADKSessionManager()
    return _enhanced_session_manager


# Synchronous wrapper for Streamlit
def send_message_with_monitoring_sync(
    query: str,
    user_id: str = "user",
    agent = None
) -> tuple[str, Dict]:
    """
    Synchronous wrapper for send_message_with_monitoring
    
    Returns: (response_text, execution_report)
    """
    manager = get_enhanced_session_manager()
    
    # Create new event loop if needed
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Run async function in sync context
    return loop.run_until_complete(
        manager.send_message_with_monitoring(query, user_id, agent=agent)
    )


__all__ = [
    'EnhancedADKSessionManager',
    'ExecutionMonitor',
    'get_enhanced_session_manager',
    'send_message_with_monitoring_sync',
    'logger',
]
