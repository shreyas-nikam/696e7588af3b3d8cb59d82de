id: 696e7588af3b3d8cb59d82de_user_guide
summary: Lab 9: MCP Server Implementation User Guide
feedback link: https://docs.google.com/forms/d/e/1FAIpQLSfWkOK-in_bMMoHSZfcIvAeO58PAH9wrDqcxnJABHaxiDqhSA/viewform?usp=sf_link
environments: Web
status: Published
# Building an AI-Ready Ecosystem with Model Context Protocol (MCP) Server

## Introduction to MCP and the Org-AI-R Application
Duration: 0:05

Welcome to the **PE Org-AI-R Model Context Protocol (MCP) Server Implementation Lab**! This lab is designed to guide you through understanding and interacting with an MCP server implementation that exposes the core capabilities of the PE Org-AI-R platform.

<aside class="positive">
<b>What is MCP and why is it important?</b> The Model Context Protocol (MCP) is a standardized way for AI agents (like Claude Desktop) to discover, understand, and interact with the functionalities and data of other services. Imagine you have many specialized AI tools and data sources. MCP acts as a universal translator, allowing an AI agent to seamlessly integrate with all of them without needing custom integrations for each one. This standardization is crucial for building truly autonomous and interoperable AI systems.
</aside>

Our goal in this lab is to transform traditional, siloed AI readiness assessments into a standardized, AI-interoperable ecosystem. This involves exposing our assessment logic, data, and strategic workflows in a structured format that AI agents can easily consume.

This project is pivotal for the organization, as it paves the way for a truly AI-ready ecosystem where intelligent agents can autonomously contribute to strategic decision-making, from assessing potential investments to identifying areas for AI-driven transformation within portfolio companies.

**Key Objectives of this Lab:**
*   **Remember**: How to list MCP primitives (Tools, Resources, Prompts).
*   **Understand**: Why protocol standardization enables interoperability.
*   **Apply**: Interact with an MCP server exposing PE Org-AI-R capabilities.
*   **Analyze**: Understand the benefits of MCP compared to custom API integrations.
*   **Create**: Conceptualize resource hierarchies for portfolio data.

**Key Concepts you will encounter:**
*   **Model Context Protocol (MCP)** specification.
*   **Tools**: Executable functions that perform specific actions.
*   **Resources**: URI-addressable data that AI agents can read.
*   **Prompts**: Templated instructions that guide AI agents through complex tasks.
*   **AI Agent Interaction**: How an AI agent uses these components to achieve goals.

**Prerequisites:** Familiarity with the general concepts of AI agents and data interaction. No coding knowledge is required for this codelab.

To begin, navigate through the Streamlit application using the sidebar on the left. The "Introduction" page you are currently viewing mirrors the content discussed above.

## Defining Core AI Assessment "Tools"
Duration: 0:10

My first task is to expose the core `calculate_org_air_score` functionality. This is the cornerstone of our platform, providing a holistic view of a company's AI readiness. Financial analysts, for example, will use AI agents to quickly assess the AI readiness of potential investment targets.

In the context of MCP, **Tools** are executable functions that an AI agent can invoke to perform specific actions or calculations. They have clearly defined input parameters (an `inputSchema`) and produce structured outputs.

The Org-AI-R score is a composite metric derived from several dimensions and adjusted by factors like talent concentration and sector-specific benchmarks. Conceptually, it combines:
*   **Idiosyncratic Readiness ($V^R$):** Reflects internal capabilities, often a weighted average of dimension scores adjusted for specific company factors.
*   **Systematic Opportunity ($H^R$):** Represents external market opportunities and sector-specific AI adoption baselines.
*   **Synergy Score:** Captures the interaction between internal readiness and external opportunity.

The final Org-AI-R score $S$ can be thought of as a function:
$$ S = f(V^R, H^R, \text{Synergy}) $$
The tool will return not just the final score, but also its components and a confidence interval, giving AI agents a richer understanding of the assessment.

Other crucial tools include:
*   `get_company_evidence`: Retrieves supporting evidence for a specific AI readiness dimension.
*   `project_ebitda_impact`: Projects potential EBITDA impact based on AI-readiness score improvement.
*   `analyze_whatif_scenario`: Analyzes the impact of a hypothetical investment or strategic change on Org-AI-R score and financial metrics.
*   `get_fund_portfolio`: Retrieves a list of companies within a specific fund's portfolio.

### Interacting with MCP Tools

1.  Navigate to the **"Define MCP Tools"** section using the sidebar navigation in the Streamlit app.
2.  You will see a dropdown labeled "Select an MCP Tool to test:". Choose `calculate_org_air_score`.
3.  Observe the "Input for `calculate_org_air_score`:" section. Here, you need to provide values for the tool's arguments. For `calculate_org_air_score`, you might fill in:
    *   `company_id`: `ACME-001`
    *   `sector_id`: `technology`
    *   `dimension_scores`: `70, 65, 75, 68, 72, 60, 70` (enter as comma-separated numbers)
    *   `talent_concentration`: `0.2`
4.  Click the "Execute `calculate_org_air_score`" button.
5.  The "Tool Output:" section will display the structured result, typically in JSON format, which an AI agent would parse.

<aside class="positive">
<b>Example Output Structure:</b> An AI agent receives structured data like this, allowing it to easily extract specific values (e.g., `final_score` or `v_r_score`) for further analysis or decision-making.
</aside>

```json
{
  "company_id": "ACME-001",
  "final_score": 75.36,
  "components": {
    "v_r_score": 70.36,
    "h_r_score": 75,
    "synergy_score": 73.36
  },
  "confidence_interval": [
    72.36,
    78.36
  ]
}
```

Feel free to try other tools like `project_ebitda_impact` or `analyze_whatif_scenario` by providing suitable inputs. Notice how each tool has its own set of required and optional arguments based on its specific function.

## Standardizing Data Access with "Resources"
Duration: 0:08

Beyond executable tools, AI agents often need access to static reference data (like sector definitions or model parameters) and dynamic, contextual information (like a specific company's details or their current score). In MCP, **Resources** provide a standardized way to expose this data through URI-based access.

Imagine an AI agent performing a sector-specific analysis; it might need to retrieve the `H^R` baselines for various sectors. Similarly, when a user asks about a specific company's AI-readiness profile, the AI agent should be able to fetch that information using a dynamic URI like `orgair://company/{{company_id}}/score`. This structured, URI-addressable data access is crucial for building robust AI applications that can autonomously gather necessary context.

### Exploring MCP Resources

1.  Navigate to the **"Standardize MCP Resources"** section in the Streamlit app's sidebar.
2.  First, observe the "Available Static Resources" section. These are resources with fixed URIs that provide general, unchanging data. Select `orgair://sectors` from the dropdown. This resource provides definitions and baseline metrics for various industry sectors.
3.  Next, look at "Dynamic Resource Templates". These are patterns with placeholders (like `{{company_id}}`) that an AI agent uses to construct specific URIs for dynamic data. Select `orgair://company/{{company_id}}/score`.
4.  Below the template, enter `ACME-001` in the "Enter Company ID to preview URI:" field. You'll see the full URI `orgair://company/ACME-001/score` generated. Click "Use this URI".
5.  Now, in the "Read a Resource by URI" section, the URI input field should be pre-filled with the URI you selected/generated.
6.  Click "Read Resource".
7.  The "Resource Content:" section will display the data retrieved from that URI.

<aside class="positive">
<b>Resource Output Example:</b> When you read `orgair://company/ACME-001/score`, an AI agent would receive data formatted like this:
</aside>

```json
{
  "company_id": "ACME-001",
  "org_air_score": 78.5,
  "last_updated": "2023-10-27",
  "details": "Mock score data."
}
```

This modular approach ensures that data access is standardized, discoverable, and easily extendable, fulfilling a critical requirement for flexible AI interoperability.

## Empowering AI with Intelligent "Prompts"
Duration: 0:07

To further enhance the capabilities of AI agents, we need to provide them with structured guidance for complex analytical tasks. Instead of just exposing raw tools and data, MCP **Prompts** allow us to define reusable templates that guide an AI agent through a multi-step workflow.

For example, an AI agent performing a `due_diligence_assessment` for a new investment target needs to:
1.  Retrieve the Org-AI-R score.
2.  Gather evidence for each dimension.
3.  Analyze strengths and gaps.
4.  Compare to benchmarks.
5.  Identify risks and opportunities.
6.  Formulate a recommendation.

Defining this as a prompt template ensures that every AI agent performs due diligence consistently and comprehensively, delivering high-quality, structured output. Similarly, `value_creation_plan` and `competitive_analysis` prompts guide agents through other strategic tasks, reducing variability and improving efficiency.

### Generating MCP Prompts

1.  Navigate to the **"Empower MCP Prompts"** section in the Streamlit app's sidebar.
2.  You will see a dropdown labeled "Select an MCP Prompt to generate:". Choose `due_diligence_assessment`.
3.  Observe the "Arguments for `due_diligence_assessment`:" section. For this prompt, you only need to provide a `company_id`. Enter `GLOBEX-002`.
4.  Click the "Generate `due_diligence_assessment` Prompt" button.
5.  The "Generated Prompt Message (for AI Agent):" section will display the comprehensive instructions that an AI agent would receive.

<aside class="positive">
<b>Example Generated Prompt:</b> Notice how the prompt clearly outlines the steps and the specific MCP Tools and Resources an AI agent should utilize.
</aside>

```markdown
As an expert AI due diligence analyst, perform a comprehensive assessment of GLOBEX-002's AI readiness.
1. Use `calculate_org_air_score` to get the current score.
2. Use `get_company_evidence` for key dimensions like 'data_infrastructure' and 'talent'.
3. Analyze strengths, weaknesses, opportunities, and threats (SWOT) related to AI.
4. Compare GLOBEX-002's score against sector benchmarks from `orgair://sectors`.
5. Formulate a recommendation on GLOBEX-002's investment potential regarding AI readiness.
Provide the output as a structured report in markdown format, including a summary, detailed findings, and recommendations.
```

By defining these prompts, we transform simple tool calls into complex, goal-oriented workflows that AI agents can execute autonomously. This greatly enhances the utility of our MCP server, allowing us to standardize high-level analytical tasks and ensure consistent, high-quality output from various AI clients.

## Verifying Interoperability: Simulating an End-to-End Workflow
Duration: 0:15

Now that all MCP primitives (Tools, Resources, and Prompts) are defined and registered, it's time to demonstrate how an AI agent would orchestrate these capabilities to perform a complex real-world task. This simulation confirms that our MCP server provides the necessary interoperability layer for AI agents to autonomously drive strategic insights.

The workflow will involve an AI agent creating a "Value Creation Plan" for a company, which includes:
1.  **Initiation:** The AI agent receives a request and uses the `value_creation_plan` prompt template to understand the required steps.
2.  **Current State Assessment:** It retrieves the current Org-AI-R score using the `calculate_org_air_score` tool.
3.  **Gap Analysis & Evidence Gathering:** It gathers evidence for key dimensions using `get_company_evidence`.
4.  **Scenario Modeling:** It uses `analyze_whatif_scenario` to model hypothetical investments and their impact.
5.  **Financial Impact Projection:** It projects the EBITDA impact of the improvements using the `project_ebitda_impact` tool.
6.  **Plan Generation:** Finally, it synthesizes all this information into a structured value creation plan.

This end-to-end simulation validates the true power of the MCP: enabling autonomous, intelligent, and standardized workflows for AI agents.

### Running the End-to-End Workflow

1.  Navigate to the **"End-to-End Workflow Simulation"** section in the Streamlit app's sidebar.
2.  Click the "Start AI Value Creation Workflow Simulation" button.
3.  The application will simulate the AI agent's actions step-by-step, displaying the calls made to MCP Tools and the data retrieved. This process will take a few moments to complete.
4.  Review the "Simulation Steps & Results:" output. It shows a narrative of the AI agent's thought process and the results of each MCP call.

<aside class="positive">
<b>Understanding the Simulation Output:</b> Pay close attention to how the AI agent first generates a prompt, then calls various tools (`calculate_org_air_score`, `get_company_evidence`, `analyze_whatif_scenario`, `project_ebitda_impact`), and finally synthesizes all the collected information into a comprehensive summary. This demonstrates the seamless flow and decision-making capabilities enabled by MCP.
</aside>

This simulated end-to-end workflow demonstrates how an AI agent, powered by our MCP server, can execute a complex task like generating an "AI Value Creation Plan":
1.  The agent starts by requesting a `value_creation_plan` prompt, which provides a structured set of instructions, essentially acting as a project brief.
2.  It then autonomously invokes the `calculate_org_air_score` tool to fetch the current state of AI readiness.
3.  It uses the `get_company_evidence` tool to gather supporting context for specific dimensions.
4.  Next, it calls `analyze_whatif_scenario` to model the impact of proposed initiatives.
5.  Finally, it leverages `project_ebitda_impact` to quantify the potential financial returns, specifically the `base_impact` percentage for EBITDA.
6.  All these pieces of information, retrieved and analyzed through MCP primitives, are then synthesized by the AI agent into a coherent and actionable value creation plan summary.

This demonstrates the core value proposition of our MCP server: enabling AI agents to interact intelligently and autonomously with our organization's capabilities, transforming raw data and models into strategic insights and actionable plans. This validates the successful integration and interoperability of all defined MCP components.
