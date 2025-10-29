import streamlit as st
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from software_engineering_mentor.crew import SoftwareEngineeringMentor

# Page configuration
st.set_page_config(
    page_title="AI-Powered Software Engineering Mentor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    .output-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI-Powered Software Engineering Mentor</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Welcome to the Software Engineering Mentor! This AI-powered platform helps you plan, architect, and develop software projects with guidance from specialized AI agents.
    """)
    
    # Sidebar for different modes
    st.sidebar.title("🎯 Workflow Options")
    
    workflow_mode = st.sidebar.selectbox(
        "Choose your workflow:",
        [
            "Complete Project Analysis",
            "Project Planning Only", 
            "Architecture Design Only",
            "Code Explanation",
            "Prompt Coaching",
            "Resource Curation"
        ]
    )
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = {}
    
    # Main content area
    if workflow_mode == "Complete Project Analysis":
        complete_analysis_workflow()
    elif workflow_mode == "Project Planning Only":
        planning_workflow()
    elif workflow_mode == "Architecture Design Only":
        architecture_workflow()
    elif workflow_mode == "Code Explanation":
        code_explanation_workflow()
    elif workflow_mode == "Prompt Coaching":
        prompt_coaching_workflow()
    elif workflow_mode == "Resource Curation":
        resource_curation_workflow()

def complete_analysis_workflow():
    st.markdown('<h2 class="section-header">📋 Complete Project Analysis</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        project_idea = st.text_area(
            "Describe your software project idea:",
            placeholder="e.g., Build a cross-platform note-taking app with offline sync and real-time collaboration features",
            height=100
        )
    
    with col2:
        st.markdown("**Additional Inputs:**")
        code_snippet = st.text_area(
            "Code snippet to analyze (optional):",
            placeholder="def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item.price\n    return total",
            height=80
        )
        
        coding_goal = st.text_input(
            "Coding goal for prompt coaching (optional):",
            placeholder="e.g., Implement user authentication with JWT tokens"
        )
    
    if st.button("🚀 Generate Complete Analysis", type="primary"):
        if project_idea:
            with st.spinner("🤖 AI agents are working on your project analysis..."):
                try:
                    inputs = {
                        'project_idea': project_idea,
                        'code_snippet': code_snippet if code_snippet else "No code snippet provided",
                        'coding_goal': coding_goal if coding_goal else "No specific coding goal provided"
                    }
                    
                    crew = SoftwareEngineeringMentor().crew()
                    result = crew.kickoff(inputs=inputs)
                    
                    st.session_state.results['complete_analysis'] = result
                    
                    st.markdown('<div class="success-box">✅ Complete analysis generated successfully!</div>', unsafe_allow_html=True)
                      # Display results
                    display_complete_results(result)
                    
                    # MD Export Button for Complete Analysis
                    result_text = result.raw if hasattr(result, 'raw') else str(result)
                    st.download_button(
                        label="📥 Download Complete Analysis as Markdown",
                        data=result_text,
                        file_name=f"complete_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a project idea to get started!")

def planning_workflow():
    st.markdown('<h2 class="section-header">📅 Project Planning</h2>', unsafe_allow_html=True)
    
    project_idea = st.text_area(
        "Describe your software project idea:",
        placeholder="e.g., Build a cross-platform note-taking app with offline sync and real-time collaboration features",
        height=100
    )
    
    if st.button("📋 Generate Project Roadmap", type="primary"):
        if project_idea:
            with st.spinner("🤖 Planning agent is creating your roadmap..."):
                try:
                    inputs = {'project_idea': project_idea}
                    crew = SoftwareEngineeringMentor().crew()
                      # Run only the planning task
                    plan_task = crew.tasks[0]  # plan_task is first
                    result = plan_task.execute()
                    
                    st.session_state.results['planning'] = result
                    st.markdown('<div class="success-box">✅ Project roadmap generated!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(result.raw if hasattr(result, 'raw') else str(result))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # MD Export Button
                    result_text = result.raw if hasattr(result, 'raw') else str(result)
                    st.download_button(
                        label="📥 Download as Markdown",
                        data=result_text,
                        file_name=f"project_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a project idea!")

def architecture_workflow():
    st.markdown('<h2 class="section-header">🏗️ Architecture Design</h2>', unsafe_allow_html=True)
    
    project_idea = st.text_area(
        "Describe your software project idea:",
        placeholder="e.g., Build a cross-platform note-taking app with offline sync and real-time collaboration features",
        height=100
    )
    
    if st.button("🏗️ Generate Architecture", type="primary"):
        if project_idea:
            with st.spinner("🤖 Architecture agent is designing your system..."):
                try:
                    inputs = {'project_idea': project_idea}
                    crew = SoftwareEngineeringMentor().crew()
                      # Run planning first, then architecture
                    plan_result = crew.tasks[0].execute()
                    arch_result = crew.tasks[1].execute()
                    
                    st.session_state.results['architecture'] = arch_result
                    st.markdown('<div class="success-box">✅ Architecture design generated!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(arch_result.raw if hasattr(arch_result, 'raw') else str(arch_result))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # MD Export Button
                    arch_text = arch_result.raw if hasattr(arch_result, 'raw') else str(arch_result)
                    st.download_button(
                        label="📥 Download Architecture as Markdown",
                        data=arch_text,
                        file_name=f"system_architecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a project idea!")

def code_explanation_workflow():
    st.markdown('<h2 class="section-header">🔍 Code Explanation</h2>', unsafe_allow_html=True)
    
    code_snippet = st.text_area(
        "Enter your code snippet:",
        placeholder="def calculate_total(items):\n    total = 0\n    for item in items:\n        total += item.price\n    return total",
        height=150
    )
    
    if st.button("🔍 Explain Code", type="primary"):
        if code_snippet:
            with st.spinner("🤖 Code explainer agent is analyzing your code..."):
                try:
                    inputs = {'code_snippet': code_snippet}
                    crew = SoftwareEngineeringMentor().crew()
                      # Run only the code explanation task
                    explain_task = crew.tasks[3]  # explain_task is 4th
                    result = explain_task.execute()
                    
                    st.session_state.results['code_explanation'] = result
                    st.markdown('<div="success-box">✅ Code explanation generated!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(result.raw if hasattr(result, 'raw') else str(result))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # MD Export Button
                    result_text = result.raw if hasattr(result, 'raw') else str(result)
                    st.download_button(
                        label="📥 Download Code Analysis as Markdown",
                        data=result_text,
                        file_name=f"code_explanation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a code snippet!")

def prompt_coaching_workflow():
    st.markdown('<h2 class="section-header">💡 Prompt Coaching</h2>', unsafe_allow_html=True)
    
    coding_goal = st.text_input(
        "What do you want to achieve with AI coding tools?",
        placeholder="e.g., Implement user authentication with JWT tokens"
    )
    
    if st.button("💡 Get Prompt Coaching", type="primary"):
        if coding_goal:
            with st.spinner("🤖 Prompt coach agent is preparing guidance..."):
                try:
                    inputs = {'coding_goal': coding_goal}
                    crew = SoftwareEngineeringMentor().crew()
                    
                    # Run only the prompt coaching task
                    prompt_task = crew.tasks[4]  # prompt_task is 5th
                    result = prompt_task.execute()
                    
                    st.session_state.results['prompt_coaching'] = result
                    st.markdown('<div class="success-box">✅ Prompt coaching generated!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(result.raw if hasattr(result, 'raw') else str(result))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a coding goal!")

def resource_curation_workflow():
    st.markdown('<h2 class="section-header">📚 Resource Curation</h2>', unsafe_allow_html=True)
    
    project_idea = st.text_area(
        "Describe your software project idea:",
        placeholder="e.g., Build a cross-platform note-taking app with offline sync and real-time collaboration features",
        height=100
    )
    
    if st.button("📚 Curate Learning Resources", type="primary"):
        if project_idea:
            with st.spinner("🤖 Resource curator agent is finding learning materials..."):
                try:
                    inputs = {'project_idea': project_idea}
                    crew = SoftwareEngineeringMentor().crew()
                      # Run planning first, then resource curation
                    plan_result = crew.tasks[0].execute()
                    resource_result = crew.tasks[2].execute()
                    
                    st.session_state.results['resources'] = resource_result
                    st.markdown('<div class="success-box">✅ Learning resources curated!</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="output-box">', unsafe_allow_html=True)
                    st.markdown(resource_result.raw if hasattr(resource_result, 'raw') else str(resource_result))
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # MD Export Button
                    resource_text = resource_result.raw if hasattr(resource_result, 'raw') else str(resource_result)
                    st.download_button(
                        label="📥 Download Resources as Markdown",
                        data=resource_text,
                        file_name=f"learning_resources_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.markdown(f'<div class="error-box">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.warning("Please enter a project idea!")

def display_complete_results(result):
    """Display the complete analysis results in organized sections"""
    
    # Try to extract individual task results if available
    if hasattr(result, 'tasks_output'):
        tasks_output = result.tasks_output
    else:
        # Fallback to raw output
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(result.raw if hasattr(result, 'raw') else str(result))
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # Display each task result in its own section
    task_names = [
        "Project Roadmap",
        "System Architecture", 
        "Learning Resources",
        "Code Explanation",
        "Prompt Coaching",
        "Visual Diagrams"
    ]
    
    for i, (task_name, task_output) in enumerate(zip(task_names, tasks_output)):
        st.markdown(f'<h3 class="section-header">{task_name}</h3>', unsafe_allow_html=True)
        st.markdown('<div class="output-box">', unsafe_allow_html=True)
        st.markdown(task_output.raw if hasattr(task_output, 'raw') else str(task_output))
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
