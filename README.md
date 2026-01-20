# QuLab: Lab 9 - PE Org-AI-R Model Context Protocol (MCP) Server Implementation

## Table of Contents
1.  [Project Title and Description](#project-title-and-description)
2.  [Features](#features)
3.  [Getting Started](#getting-started)
    *   [Prerequisites](#prerequisites)
    *   [Installation](#installation)
4.  [Usage](#usage)
5.  [Project Structure](#project-structure)
6.  [Technology Stack](#technology-stack)
7.  [Contributing](#contributing)
8.  [License](#license)
9.  [Contact](#contact)

---

## 1. Project Title and Description

**Project Title:** PE Org-AI-R Model Context Protocol (MCP) Server Implementation Lab

This Streamlit application serves as a hands-on lab project focusing on implementing a foundational AI interoperability layer for the PE Org-AI-R platform. The core objective is to demonstrate how to expose existing AI assessment capabilities, data resources, and strategic prompt templates via a standardized Model Context Protocol (MCP) server. This enables AI agents, such as Claude Desktop, to autonomously discover, invoke, and interpret Org-AI-R services, moving away from siloed assessments and custom API integrations.

The lab addresses the challenge of transforming complex services into discoverable and executable MCP primitives:
*   **Tools:** For executing core functionalities like calculating Org-AI-R scores or projecting EBITDA impact.
*   **Resources:** For standardized access to static reference data (e.g., sector baselines) and dynamic contextual information (e.g., company-specific scores).
*   **Prompts:** For providing structured, reusable guidance to AI agents for complex, multi-step workflows like due diligence assessments or value creation plans.

This project is a critical step towards an AI-ready ecosystem, empowering intelligent agents to contribute to strategic decision-making and AI-driven transformation within portfolio companies.

**Note on Implementation:** Due to an assumed `SyntaxError` in the original `source.py` file (which would typically house the actual backend logic), this `app.py` file contains **mock implementations** for all MCP server functions (`list_tools`, `call_tool`, `list_resources_mcp`, `read_resource_mcp`, `list_prompts`, `get_prompt`). These mocks accurately simulate the expected behavior and return types, allowing the Streamlit UI to fully demonstrate the MCP concepts and user interactions as intended by the lab.

## 2. Features

This application provides an interactive interface to explore and test the various components of an MCP server implementation:

*   **Introduction Page:** Provides a detailed overview of the lab's objectives, key concepts, tools, and prerequisites.
*   **MCP Tool Definition & Execution:**
    *   Lists all defined MCP Tools (e.g., `calculate_org_air_score`, `get_company_evidence`, `project_ebitda_impact`, `analyze_whatif_scenario`, `get_fund_portfolio`).
    *   Allows users to select a tool, input its arguments based on a dynamically rendered schema, and execute it to view its structured JSON output.
*   **MCP Resource Standardization & Access:**
    *   Displays available static MCP Resources (e.g., `orgair://companies`, `orgair://sectors`).
    *   Lists dynamic MCP Resource Templates (e.g., `orgair://company/{{company_id}}/score`).
    *   Enables users to input a full URI (static or dynamically generated from a template) and read the resource's content, presented as structured JSON.
*   **MCP Prompt Empowerment & Generation:**
    *   Presents defined MCP Prompts (e.g., `due_diligence_assessment`, `value_creation_plan`, `competitive_analysis`).
    *   Facilitates input of prompt arguments and generates the complete, structured message an AI agent would receive for initiating a complex workflow.
*   **End-to-End Workflow Simulation:**
    *   Demonstrates a simulated AI agent orchestrating multiple MCP Tools and Resources to perform a comprehensive task, such as generating an "AI Value Creation Plan."
    *   Outputs a step-by-step log of the AI agent's interactions and the resulting data/plan.

## 3. Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

*   **Python 3.8+**: Ensure Python is installed on your system.
*   **`pip`**: Python's package installer.
*   **`asyncio` and `json`**: These are standard Python libraries and typically come with Python installations.

### Installation

1.  **Clone the repository (or copy the code):**
    ```bash
    git clone <repository_url_here> # Replace with actual repo URL if available
    cd <project_directory_name>
    ```
    If no repository URL is provided, simply save the provided `app.py` code into a file named `app.py` in your desired project directory.

2.  **Install Streamlit:**
    ```bash
    pip install streamlit
    ```

## 4. Usage

To run the application:

1.  Navigate to the directory containing `app.py` in your terminal.
2.  Execute the Streamlit command:
    ```bash
    streamlit run app.py
    ```
3.  Your web browser will automatically open to the Streamlit application (usually `http://localhost:8501`).
4.  Use the sidebar navigation to explore the different sections of the MCP server implementation:
    *   **Introduction:** Get an overview of the lab.
    *   **Define MCP Tools:** Interact with and test various Org-AI-R tools.
    *   **Standardize MCP Resources:** Explore and read static and dynamic data resources.
    *   **Empower MCP Prompts:** Generate structured prompts for AI agent workflows.
    *   **End-to-End Workflow Simulation:** Observe a full multi-step AI workflow in action.

## 5. Project Structure

The project currently consists of a single file:

```
.
└── app.py
```

*   **`app.py`**: This is the main Streamlit application file. It contains the entire UI definition, the mock implementations of the MCP server functions (`list_tools`, `call_tool`, `list_resources_mcp`, `read_resource_mcp`, `list_prompts`, `get_prompt`), and the logic for interacting with these functions within the Streamlit interface. In a production environment, the MCP function implementations would typically reside in a separate backend service (e.g., `source.py` or a dedicated FastMCP server). The mock implementations are used here to resolve a `SyntaxError` that would prevent `app.py` from importing from the hypothetical `source.py`.

## 6. Technology Stack

*   **Frontend / UI Framework:** [Streamlit](https://streamlit.io/)
*   **Programming Language:** Python 3
*   **Asynchronous Operations:** `asyncio` (for simulating non-blocking MCP calls)
*   **Data Handling:** `json` (for structured data exchange)
*   **Conceptual Protocols:** Model Context Protocol (MCP)
*   **Conceptual Tools (introduced in lab):** `mcp-sdk`, `FastMCP`, Claude Desktop (as an MCP client)

## 7. Contributing

This project is part of a university lab curriculum and primarily serves educational purposes. Therefore, direct contributions via pull requests are generally not expected. However, feedback, bug reports, or suggestions for improvements are always welcome by opening an issue in the (hypothetical) repository.

## 8. License

This project is open-sourced under the MIT License. See the `LICENSE` file for more details.
*(If a `LICENSE` file doesn't exist, you might want to create one or remove this line.)*

## 9. Contact

For questions or inquiries, please contact:

*   **QuantUniversity:** [https://www.quantuniversity.com/](https://www.quantuniversity.com/)
*   **GitHub (Hypothetical):** [Your GitHub Profile Link]
*   **Email (Hypothetical):** [your.email@example.com]
