id: 696e7588af3b3d8cb59d82de_documentation
summary: Lab 9: MCP Server Implementation Documentation
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# QuLab: Lab 9: PE Org-AI-R MCP Server Implementation

## 1. Introduction: Laying the Groundwork for AI Interoperability
Duration: 05:00

Welcome to the **PE Org-AI-R Model Context Protocol (MCP) Server Implementation Lab**! This codelab will guide you through understanding a Streamlit application designed to showcase the implementation of an MCP server. This server is crucial for enabling AI agents, such as Claude Desktop, to seamlessly access and interact with core Organizational AI-Readiness (Org-AI-R) capabilities.

<aside class="positive">
<b>Important Context:</b> The original `source.py` file, which would normally contain the backend MCP server logic, had a syntax error (<code>await</code> used outside <code>async</code>). To make this Streamlit application functional and demonstrate the MCP concepts, <b>mock implementations</b> of the MCP functions (<code>list_tools</code>, <code>call_tool</code>, <code>list_resources_mcp</code>, <code>read_resource_mcp</code>, <code>list_prompts</code>, <code>get_prompt</code>) have been integrated directly into <code>app.py</code>. This allows us to simulate the MCP server's behavior for demonstration purposes.
</aside>

### The Importance of AI Interoperability
Currently, AI-readiness assessments often exist in silos, requiring manual data exports or custom API integrations for each new AI tool or client. This is inefficient and prone to inconsistencies. By implementing an MCP server, we standardize how AI agents discover, invoke, and interpret our services, reducing integration friction and enabling autonomous AI-driven insights across the organization. This project is pivotal for the organization, as it paves the way for a truly AI-ready ecosystem where intelligent agents can autonomously contribute to strategic decision-making, from assessing potential investments to identifying areas for AI-driven transformation within portfolio companies.

### The Core Challenge: Transforming Services into MCP Primitives
The central idea behind the Model Context Protocol (MCP) is to expose an application's functionalities, data, and workflows in a structured, discoverable way that AI agents can understand and interact with. This involves transforming existing services into three fundamental MCP primitives:

*   **Tools:** Executable functions that AI agents can call to perform specific actions (e.g., calculating a score, retrieving data programmatically).
*   **Resources:** Structured access to static or dynamic data, exposed via Uniform Resource Identifiers (URIs).
*   **Prompts:** Templated instructions that guide an AI agent through a complex, multi-step task, often involving multiple tool calls and resource reads.

This lab will demonstrate the setup of these MCP primitives and their practical application in a simulated workflow, providing a comprehensive guide for developers to understand the application's structure and functionalities.

### Lab Objectives for Developers
*   **Remember**: How to list MCP primitives (Tools, Resources, Prompts) within the application context.
*   **Understand**: Why protocol standardization is essential for enabling AI interoperability.
*   **Apply**: How the MCP server exposes PE Org-AI-R capabilities through mock implementations.
*   **Analyze**: The advantages of MCP over custom API integrations for AI agent interaction.
*   **Create**: How resource hierarchies are designed for portfolio data within the MCP framework.

### Key Concepts
*   **Model Context Protocol (MCP)** specification: A framework for AI agents to understand and interact with external systems.
*   **Tools vs. Resources vs. Prompts**: The three core primitives of MCP for executable actions, data access, and guided workflows.
*   **JSON-RPC**: The underlying communication protocol often used by MCP for invoking tools and other server methods.
*   **Claude Desktop integration**: How an MCP server can provide capabilities to an AI client like Claude Desktop.

### Conceptual Architecture Diagram
Let's visualize how the MCP Server, with its Tools, Resources, and Prompts, enables interaction between AI agents and the underlying PE Org-AI-R capabilities.

```mermaid
graph TD
    A[AI Agent / Claude Desktop] -->|Discovers & Invokes| B(MCP Server)
    B -->|Calls| C(MCP Tools)
    B -->|Reads| D(MCP Resources)
    B -->|Generates Content for| E(MCP Prompts)

    C -->|Performs Actions / Computations| F[PE Org-AI-R Core Logic / Mock Functions]
    D -->|Provides Data| F
    E -->|Orchestrates Tools & Resources| F
    
    F -->|Returns Results / Data| C
    F -->|Returns Content| D
    F -->|Returns Structured Instructions| E

    C -- "calculate_org_air_score" --> F
    C -- "project_ebitda_impact" --> F
    D -- "orgair://companies" --> F
    D -- "orgair://company/{{id}}/score" --> F
    E -- "due_diligence_assessment" --> F
    E -- "value_creation_plan" --> F

    subgraph User Interaction (Streamlit App)
        SA[Streamlit User Interface] -->|Displays & Interacts with| B
    end
```
<aside class="positive">
This diagram illustrates the role of the MCP Server as an intermediary, translating AI agent requests into calls to our PE Org-AI-R functionalities (represented by 'Core Logic / Mock Functions' in our case). The Streamlit app provides a user-friendly interface to test these interactions directly.
</aside>

## 2. Building Core AI Assessment Tools
Duration: 10:00

My first task as a Software Developer at PE Org-AI-R is to expose core functionalities as **MCP Tools**. These are executable functions that an AI agent can invoke with specific parameters and receive structured results. This is the cornerstone of our platform, enabling AI agents to programmatically access our analytical capabilities.

### Understanding the Org-AI-R Score
The `calculate_org_air_score` functionality is paramount. It provides a holistic view of a company's AI readiness, a composite metric derived from several dimensions and adjusted by factors like talent concentration and sector-specific benchmarks. Conceptually, it combines:
*   **Idiosyncratic Readiness ($V^R$):** Reflects internal capabilities, often a weighted average of dimension scores adjusted for specific company factors.
*   **Systematic Opportunity ($H^R$):** Represents external market opportunities and sector-specific AI adoption baselines.
*   **Synergy Score:** Captures the interaction between internal readiness and external opportunity.

The final Org-AI-R score ($S$) can be conceptually represented as:
$$ S = f(V^R, H^R, \text{Synergy}) $$
where $V^R$ is Idiosyncratic Readiness, $H^R$ is Systematic Opportunity, and $\text{Synergy}$ is the interaction score.

The tool returns not just the final score, but also its components and a confidence interval, giving AI agents a richer understanding of the assessment.

### Other Crucial Tools
We also expose other important tools for a comprehensive assessment:
*   `get_company_evidence`: Retrieves supporting evidence for a specific AI readiness dimension.
*   `project_ebitda_impact`: Projects potential EBITDA impact based on AI-readiness score improvement.
*   `analyze_whatif_scenario`: Analyzes the impact of a hypothetical investment or strategic change on Org-AI-R score and financial metrics.
*   `get_fund_portfolio`: Retrieves a list of companies within a specific fund's portfolio.

Each tool is defined with a clear `inputSchema` (a JSON Schema) to guide AI agents on how to invoke them correctly, ensuring type safety and argument validation.

### Exploring the Tool Implementation (Mock)
In our `app.py`, the `list_tools` and `call_tool` functions provide mock implementations of these MCP capabilities.

The `list_tools` function returns a list of `MockTool` objects:
```python
async def list_tools():
    """Mocks the listing of available MCP Tools."""
    return [
        MockTool(
            "calculate_org_air_score",
            "Calculates the Org-AI-R score for a company.",
            {"type": "object", "properties": {
                "company_id": {"type": "string", "description": "The ID of the company."},
                "sector_id": {"type": "string", "description": "The sector of the company.", "enum": ["technology", "finance", "healthcare"], "default": "technology"},
                "dimension_scores": {"type": "array", "items": {"type": "number"}, "description": "List of scores for each AI dimension (e.g., data, talent)."},
                "talent_concentration": {"type": "number", "description": "Concentration of AI talent (0.0-1.0).", "minimum": 0, "maximum": 1},
            }, "required": ["company_id", "sector_id", "dimension_scores", "talent_concentration"]}
        ),
        # ... other MockTool definitions ...
    ]
```
Each `MockTool` has a `name`, `description`, and `inputSchema`. The `inputSchema` is a JSON schema detailing the expected arguments, their types, descriptions, and whether they are required.

The `call_tool` function simulates the execution of these tools based on the `tool_name` and provided `args`:
```python
async def call_tool(tool_name: str, args: dict):
    """Mocks the execution of an MCP Tool."""
    if tool_name == "calculate_org_air_score":
        company_id = args.get("company_id", "UNKNOWN")
        #  Mock calculation logic 
        score = 75.0 + (sum(args.get("dimension_scores", [])) / len(args.get("dimension_scores", [1])) - 70) * 0.5 if args.get("dimension_scores") else 75.0
        output_data = {
            "company_id": company_id,
            "final_score": round(score, 2),
            "components": {"v_r_score": round(score - 5, 2), "h_r_score": 75, "synergy_score": round(score - 2, 2)},
            "confidence_interval": [round(score - 3, 2), round(score + 3, 2)]
        }
    # ... elif blocks for other tools ...
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
    return [MockTextContent(json.dumps(output_data))]
```
The `call_tool` function processes the arguments for the specified tool and returns a `MockTextContent` object containing a JSON string of the result. This JSON output is easily parsable by AI agents.

### Interaction in the Streamlit App
Below, you can interact with the defined MCP Tools. Select a tool, provide its required arguments, and execute it to see the structured output an AI agent would receive. The application dynamically generates input fields based on the `inputSchema` of the selected tool.

**(Interact with the "Define MCP Tools" section of the Streamlit application)**

<aside class="positive">
By experimenting with different inputs and tools, you can observe how the structured JSON outputs from each tool provide precise, machine-readable information. This precision is critical for AI agents to make informed decisions and progress through their tasks autonomously.
</aside>

## 3. Standardizing Data Access with MCP Resources
Duration: 08:00

Beyond executable tools, AI agents often need access to structured data. **MCP Resources** provide a standardized way to expose this data through Uniform Resource Identifiers (URIs). This mechanism allows AI agents to retrieve static reference data (like sector definitions) and dynamic, contextual information (like a specific company's details or their current score).

### Types of Resources
1.  **Static Resources**: These are resources with fixed URIs, providing stable access to global configuration and reference data. Examples include a list of all registered companies or definitions of industry sectors.
    *   `orgair://companies`: List of all registered companies with basic details.
    *   `orgair://sectors`: Definitions and baseline metrics for various industry sectors.
    *   `orgair://parameters/v2.0`: Global parameters and configuration for Org-AI-R model version 2.0.

2.  **Dynamic Resource Templates**: These resources use URI templates (e.g., `{{company_id}}`) to allow AI agents to construct URIs dynamically to fetch specific, up-to-date information for individual entities. This is powerful for targeted inquiries.
    *   `orgair://company/{{company_id}}/score`: AI-readiness score and detailed profile for a specific company.
    *   `orgair://fund/{{fund_id}}/companies`: List of companies associated with a particular investment fund.
    *   `orgair://metric/{{metric_name}}/history`: Historical data series for a given financial or operational metric.

This structured, URI-addressable data access is crucial for building robust AI applications that can autonomously gather necessary context. For example, an AI agent performing a sector-specific analysis might need to retrieve the `H^R` baselines for various sectors.

### Exploring the Resource Implementation (Mock)
Our `app.py` provides mock implementations for listing and reading these MCP Resources.

The `list_resources_mcp` function returns a list of static resources:
```python
async def list_resources_mcp():
    """Mocks the listing of static MCP Resources."""
    return [
        MockResource("orgair://companies", "List of all registered companies with basic details."),
        MockResource("orgair://sectors", "Definitions and baseline metrics for various industry sectors."),
        # ... more resources ...
    ]
```

The `list_resource_templates_mcp` function provides the dynamic URI templates:
```python
async def list_resource_templates_mcp():
    """Mocks the listing of dynamic MCP Resource templates."""
    return [
        MockResourceTemplate("orgair://company/{{company_id}}/score", "AI-readiness score and detailed profile for a specific company."),
        MockResourceTemplate("orgair://fund/{{fund_id}}/companies", "List of companies associated with a particular investment fund."),
        # ... more templates ...
    ]
```

The `read_resource_mcp` function simulates fetching data for a given URI:
```python
async def read_resource_mcp(uri: str):
    """Mocks the reading of content from an MCP Resource URI."""
    if uri == "orgair://companies":
        return json.dumps({"companies": [{"id": "ACME-001", "name": "ACME Corp"}, {"id": "GLOBEX-002", "name": "Globex Inc."}]})
    elif uri == "orgair://sectors":
        return json.dumps({"sectors": [{"id": "technology", "h_r_baseline": 75, "avg_air_score": 72.5}, {"id": "finance", "h_r_baseline": 68, "avg_air_score": 65.1}]})
    elif uri.startswith("orgair://company/") and "/score" in uri:
        company_id = uri.split("/")[3]
        return json.dumps({"company_id": company_id, "org_air_score": 78.5, "last_updated": "2023-10-27", "details": "Mock score data."})
    # ... logic for other URIs ...
    raise ValueError(f"Resource not found or URI not supported by mock: {uri}")
```
This function parses the URI and returns a JSON string representing the resource's content.

### Flowchart: Reading an MCP Resource

```mermaid
graph TD
    A[AI Agent / User Enters URI] --> B{Is URI known?}
    B -- No --> F[Error: Resource Not Found]
    B -- Yes --> C{Is URI a static resource (e.g., orgair://sectors)?}
    C -- Yes --> G[Retrieve static data from mock storage]
    C -- No --> D{Is URI a dynamic template instance (e.g., orgair://company/ACME-001/score)?}
    D -- Yes --> E[Extract parameters (e.g., company_id)]
    E --> H[Generate dynamic data based on parameters from mock storage]
    G --> I[Return Resource Content (JSON)]
    H --> I
    I --> J[Display Content to AI Agent / User]
```

### Interaction in the Streamlit App
Below, you can explore the defined MCP Resources. You can list static resources, view dynamic resource templates, and then read a specific resource by providing its URI. Use the select boxes to pre-fill the URI input for easier testing.

**(Interact with the "Standardize MCP Resources" section of the Streamlit application)**

<aside class="positive">
The URI-based access model for resources is analogous to how a web browser accesses information using URLs. This familiar pattern makes it intuitive for AI agents to discover and consume data, providing a robust foundation for context-aware AI applications.
</aside>

## 4. Empowering AI with Intelligent Prompts
Duration: 07:00

To truly enhance the capabilities of AI agents, we move beyond simple tool calls and data access. **MCP Prompts** allow us to define reusable, structured templates that guide an AI agent through a complex, multi-step workflow. These prompts act as high-level instructions, orchestrating the use of various tools and resources to achieve a specific analytical goal.

### Example Prompts
Consider the `due_diligence_assessment` prompt:
Instead of an AI agent needing to figure out the steps for due diligence, this prompt provides a clear roadmap:
1.  Retrieve the Org-AI-R score using `calculate_org_air_score`.
2.  Gather evidence for key dimensions using `get_company_evidence`.
3.  Analyze strengths, weaknesses, opportunities, and threats (SWOT).
4.  Compare to sector benchmarks using `orgair://sectors`.
5.  Formulate an investment recommendation.

Other powerful prompts include:
*   `value_creation_plan`: Guides an AI agent to create a strategic value creation plan focused on improving AI readiness and financial impact, potentially using `analyze_whatif_scenario` and `project_ebitda_impact`.
*   `competitive_analysis`: Directs an AI agent to perform a comparative analysis of AI readiness across a set of companies.

Defining these as prompt templates ensures that every AI agent performs tasks consistently and comprehensively, delivering high-quality, structured output, and reducing variability.

### Exploring the Prompt Implementation (Mock)
Our `app.py` uses `list_prompts` and `get_prompt` functions to provide mock implementations.

The `list_prompts` function returns a list of available prompts:
```python
async def list_prompts():
    """Mocks the listing of available MCP Prompts."""
    return [
        MockPrompt("due_diligence_assessment", "Guides an AI agent through a comprehensive due diligence assessment of a company's AI readiness.", [
            {"name": "company_id", "required": True, "description": "The ID of the company to assess."}
        ]),
        MockPrompt("value_creation_plan", "Creates a strategic value creation plan focused on improving a company's AI readiness and financial impact.", [
            {"name": "company_id", "required": True, "description": "The ID of the company for the plan."},
            {"name": "target_score", "required": True, "description": "The target Org-AI-R score."},
            {"name": "timeline_months", "required": True, "description": "The target timeline in months."}
        ]),
        # ... other MockPrompt definitions ...
    ]
```
Each `MockPrompt` specifies its `name`, `description`, and the `arguments` it expects, similar to tool schemas.

The `get_prompt` function generates the actual structured message for the AI agent:
```python
async def get_prompt(prompt_name: str, args: dict):
    """Mocks the generation of a structured prompt message for an AI agent."""
    if prompt_name == "due_diligence_assessment":
        company_id = args.get("company_id", "UNKNOWN")
        text = f"""
As an expert AI due diligence analyst, perform a comprehensive assessment of {company_id}'s AI readiness.
1. Use `calculate_org_air_score` to get the current score.
2. Use `get_company_evidence` for key dimensions like 'data_infrastructure' and 'talent'.
3. Analyze strengths, weaknesses, opportunities, and threats (SWOT) related to AI.
4. Compare {company_id}'s score against sector benchmarks from `orgair://sectors`.
5. Formulate a recommendation on {company_id}'s investment potential regarding AI readiness.
Provide the output as a structured report in markdown format, including a summary, detailed findings, and recommendations.
"""
    # ... elif blocks for other prompts ...
    else:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    return [MockPromptMessage(MockContent(text))]
```
This function dynamically constructs a detailed markdown message, often including instructions for the AI agent to use specific tools and resources.

### Conceptual Flow of a Prompt

```mermaid
graph TD
    A[AI Agent Receives Task (e.g., "Assess Company AI Readiness")] --> B{AI Agent Requests "due_diligence_assessment" Prompt}
    B --> C(MCP Server: Calls get_prompt("due_diligence_assessment", args))
    C --> D[MCP Server Returns Structured Markdown Prompt]
    D --> E[AI Agent Parses Prompt]
    E --> F[AI Agent Invokes Tool: calculate_org_air_score]
    F --> G[AI Agent Reads Resource: orgair://sectors]
    G --> H[AI Agent Invokes Tool: get_company_evidence]
    H --> I[AI Agent Synthesizes Information & Formulates Report]
    I --> J[AI Agent Presents Report to User]
```

### Interaction in the Streamlit App
Below, you can explore the defined MCP Prompts. Select a prompt, provide its arguments, and generate the structured message that an AI agent would receive.

**(Interact with the "Empower MCP Prompts" section of the Streamlit application)**

<aside class="negative">
Without standardized prompts, AI agents might produce inconsistent or incomplete analyses, especially for complex tasks. Prompts enforce best practices and ensure critical steps are not missed.
</aside>

## 5. End-to-End Workflow Simulation
Duration: 10:00

Now that all MCP primitives (Tools, Resources, and Prompts) are defined and registered (via our mock implementations), it's time to demonstrate how an AI agent would orchestrate these capabilities to perform a complex real-world task. This section simulates an AI agent performing a complete company assessment, from scoring to impact analysis, and then preparing a value creation plan. This confirms that our MCP server provides the necessary interoperability layer for AI agents to autonomously drive strategic insights.

### The Simulated Workflow: AI Value Creation Plan
The workflow will involve a sequence of interactions, mimicking how an intelligent agent would fulfill a user request:

1.  **Initiation:** An AI agent receives a request to create a value creation plan for a specific company (e.g., "ACME-001"). It first uses the `value_creation_plan` prompt template to understand the required steps and objectives.
2.  **Current State Assessment:** The agent retrieves the current Org-AI-R score for "ACME-001" using the `calculate_org_air_score` tool. It also identifies the current `H^R` (Systematic Opportunity) score from this tool's output, which is needed for later projections.
3.  **Gap Analysis & Evidence Gathering:** Based on the current score and target, the agent infers areas for improvement (e.g., 'data_infrastructure'). It then gathers supporting evidence for these dimensions using the `get_company_evidence` tool.
4.  **Scenario Modeling:** The agent uses the `analyze_whatif_scenario` tool to model the impact of hypothetical interventions (e.g., a $2M investment leading to specific dimension score changes). This provides a projected change in Org-AI-R score and estimated financial impact.
5.  **Financial Impact Projection:** Using the current Org-AI-R score, a target score, and the `H^R` score, the agent projects the potential EBITDA impact over a specified holding period (e.g., 3 years) using the `project_ebitda_impact` tool.
6.  **Plan Generation:** Finally, the agent synthesizes all the information gathered from tool calls into a structured value creation plan summary, guided by the initial prompt.

This end-to-end simulation validates the true power of the MCP: enabling autonomous, intelligent, and standardized workflows for AI agents.

### Interaction in the Streamlit App
Click the button below to start the simulation. The application will log each step the AI agent takes, including the tool/prompt name, arguments used, and the structured output received.

**(Interact with the "End-to-End Workflow Simulation" section of the Streamlit application)**

### Simulation Insights
As you review the simulation steps, notice how each tool call builds upon the previous one. The AI agent:
*   Uses `get_prompt` to get initial instructions.
*   Calls `calculate_org_air_score` to establish a baseline.
*   Calls `get_company_evidence` for deeper insights into specific areas.
*   Calls `analyze_whatif_scenario` to explore potential future states.
*   Calls `project_ebitda_impact` to quantify financial returns.
*   Finally, combines all these data points to create a coherent "Value Creation Plan Summary".

<aside class="positive">
This simulated workflow highlights the orchestration capabilities that an MCP server provides. It transforms a collection of individual services into a cohesive, intelligent system capable of performing complex analytical tasks autonomously. For developers, this demonstrates the successful integration and interoperability of all defined MCP components: Tools, Resources, and Prompts working in harmony.
</aside>
