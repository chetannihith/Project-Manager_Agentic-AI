# 🧠 Project-Manager_Agentic-AI

This software leverages **AI Agent frameworks** to intelligently simulate the role of a **project mentor**, guiding users through the complete process of developing any software project.  
It includes two major components:
- **CrewAI-based mentor** for AI-powered project guidance.
- **Google ADK-based agent** for web-based project interaction and control.

---
````markdown

## ⚙️ Steps to Run the Project Locally

Follow the instructions below to set up and run both components of the project.

---
# ⚡ Quick Start

## Clone the Repository
```bash
- git clone https://github.com/<your-username>/Project-Manager_Agentic-AI.git
- cd Project-Manager_Agentic-AI

### 🚀 1. Run the CrewAI Component

**Path:** `Project-Manager_Agentic-AI\Crew`

#### 🔧 Setup Instructions

```bash
# Navigate to the CrewAI project folder
- cd Project-Manager_Agentic-AI\Crew

# Create and activate a virtual environment
- python -m venv crew-venv
- crew-venv\Scripts\activate

# Install the required dependencies
- pip install -r requirements.txt

# Navigate to the main module directory
- cd software_engineering_mentor

# (Optional) Create another venv inside if needed
- python -m venv .venv
- .venv\Scripts\activate

# Go back to the parent directory
- cd ..

# Install remaining dependencies using uv
- uv pip install -r requirements.txt

# Navigate back to the mentor module
- cd software_engineering_mentor

# Initialize CrewAI (only once)
- crewai install

# Run the CrewAI agent
- crewai run
````

💡 *This will launch the CrewAI project mentor agent, capable of guiding users through software development steps interactively.*

---

### 🌐 2. Run the Google ADK Component

**Path:** `Project-Manager_Agentic-AI\Google-ADK`

#### 🔧 Setup Instructions

```bash
# Navigate to the ADK project folder
- cd Project-Manager_Agentic-AI\Google-ADK

# Create and activate a virtual environment
- python -m venv adk-venv
- adk-venv\Scripts\activate

# Install dependencies
- pip install -r requirements.txt

# Move one level up (optional)
- cd ..

# Launch the ADK Web UI
- adk web .
```

💡 *This will open the Google ADK web interface, where you can select and interact with your AI agent projects directly from the browser.*

---

### 🧩 Notes

* Ensure **Python 3.10+** is installed.
* Always activate the correct virtual environment before running commands.
* If you face any dependency issues, try upgrading pip:

  ```bash
  - python -m pip install --upgrade pip
  ```
* For Windows PowerShell users, ensure script execution is enabled:

  ```bash
  - Set-ExecutionPolicy Unrestricted -Scope Process
  ```

---

### 📦 Recommended Folder Structure

```
Project-Manager_Agentic-AI/
│
├── Crew/
│   ├── requirements.txt
│   ├── crew-venv/
│   └── software_engineering_mentor/
│
└── Google-ADK/
    ├── requirements.txt
    ├── adk-venv/
    └── other project files...
```

---

### 🧠 Summary

| Component  | Framework     | Command to Run | Description                     |
| ---------- | ------------- | -------------- | ------------------------------- |
| CrewAI     | CrewAI        | `crewai run`   | AI-powered project mentor agent |
| Google ADK | ADK Framework | `adk web .`    | Web-based agent workspace       |

---

### 👨‍💻 Author

**Chetan Vemula**
*Developed as part of Academic Cource*
🚀 *Empowering developers through intelligent agentic project guidance.*
