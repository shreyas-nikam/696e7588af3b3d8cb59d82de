
import streamlit as st
import asyncio
import json

# The original error indicates a SyntaxError in source.py at line 453:
# "score_result = await call_tool("calculate_org_air_score", calculate_score_args)"
# This means `await` is used outside of an `async` function definition within `source.py`,
# making `source.py` unimportable.
#
# Since we are asked to fix `app.py` and cannot modify `source.py`,
# the only way to make `app.py` runnable is to provide mock implementations
# for the functions it expects to import from `source.py`.
# This allows `app.py` to execute without a SyntaxError and demonstrate its structure,
# even if the underlying MCP server functionality is simulated.

# --- Mock Implementations for source.py functions ---
# These mocks mimic the expected behavior and return types of the functions
# that would normally be imported from 'source.py'.

class MockTextContent:
    """Mock class to simulate the TextContent object returned by call_tool."""
    def __init__(self, text):
        self.text = text

class MockPromptMessage:
    """Mock class to simulate the PromptMessage object returned by get_prompt."""
    def __init__(self, content):
        self.content = content

class MockContent:
    """Mock class to simulate the Content object within PromptMessage."""
    def __init__(self, text):
        self.text = text

class MockTool:
    """Mock class to simulate the Tool object returned by list_tools."""
    def __init__(self, name, description, input_schema):
        self.name = name
        self.description = description
        self.inputSchema = input_schema

class MockResource:
    """Mock class to simulate the Resource object returned by list_resources_mcp."""
    def __init__(self, uri, description):
        self.uri = uri
        self.description = description

class MockResourceTemplate:
    """Mock class to simulate the ResourceTemplate object returned by list_resource_templates_mcp."""
    def __init__(self, uri_template, description):
        self.uriTemplate = uri_template
        self.description = description

class MockPrompt:
    """Mock class to simulate the Prompt object returned by list_prompts."""
    def __init__(self, name, description, arguments):
        self.name = name
        self.description = description
        self.arguments = arguments

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
        MockTool(
            "get_company_evidence",
            "Retrieves supporting evidence for a specific AI readiness dimension.",
            {"type": "object", "properties": {
                "company_id": {"type": "string", "description": "The ID of the company."},
                "dimension": {"type": "string", "description": "The AI readiness dimension (e.g., 'data_infrastructure')."},
                "limit": {"type": "integer", "description": "Maximum number of evidence items to return.", "default": 1}
            }, "required": ["company_id", "dimension"]}
        ),
        MockTool(
            "project_ebitda_impact",
            "Projects potential EBITDA impact based on AI-readiness score improvement.",
            {"type": "object", "properties": {
                "company_id": {"type": "string", "description": "The ID of the company."},
                "entry_score": {"type": "number", "description": "Current Org-AI-R score."},
                "target_score": {"type": "number", "description": "Target Org-AI-R score."},
                "h_r_score": {"type": "number", "description": "Systematic Opportunity score (H^R)."},
                "holding_period_years": {"type": "integer", "description": "Investment holding period in years.", "default": 3},
            }, "required": ["company_id", "entry_score", "target_score", "h_r_score"]}
        ),
        MockTool(
            "analyze_whatif_scenario",
            "Analyzes the impact of a hypothetical investment or strategic change on Org-AI-R score and financial metrics.",
            {"type": "object", "properties": {
                "company_id": {"type": "string", "description": "The ID of the company."},
                "scenario_name": {"type": "string", "description": "Name of the what-if scenario."},
                "dimension_changes": {"type": "object", "additionalProperties": {"type": "number"}, "description": "Map of dimension to expected score change (e.g., {'data_infrastructure': 10})."},
                "investment_usd": {"type": "number", "description": "Hypothetical investment amount in USD.", "default": 0},
            }, "required": ["company_id", "scenario_name", "dimension_changes"]}
        ),
        MockTool(
            "get_fund_portfolio",
            "Retrieves a list of companies within a specific fund's portfolio.",
            {"type": "object", "properties": {
                "fund_id": {"type": "string", "description": "The ID of the investment fund."}
            }, "required": ["fund_id"]}
        ),
    ]

async def call_tool(tool_name: str, args: dict):
    """Mocks the execution of an MCP Tool."""
    if tool_name == "calculate_org_air_score":
        company_id = args.get("company_id", "UNKNOWN")
        score = 75.0 + (sum(args.get("dimension_scores", [])) / len(args.get("dimension_scores", [1])) - 70) * 0.5 if args.get("dimension_scores") else 75.0
        output_data = {
            "company_id": company_id,
            "final_score": round(score, 2),
            "components": {"v_r_score": round(score - 5, 2), "h_r_score": 75, "synergy_score": round(score - 2, 2)},
            "confidence_interval": [round(score - 3, 2), round(score + 3, 2)]
        }
    elif tool_name == "get_company_evidence":
        company_id = args.get("company_id", "UNKNOWN")
        dimension = args.get("dimension", "UNKNOWN")
        output_data = {
            "company_id": company_id,
            "dimension": dimension,
            "evidence_items": [{"id": "ev1", "content": f"Sample evidence for {dimension} in {company_id}: Robust data pipeline for customer analytics."}]
        }
    elif tool_name == "project_ebitda_impact":
        company_id = args.get("company_id", "UNKNOWN")
        entry_score = args.get("entry_score", 0)
        target_score = args.get("target_score", 0)
        h_r_score = args.get("h_r_score", 0)
        impact_multiplier = 0.005 # A mock impact factor
        ebitda_impact_pct = (target_score - entry_score) * impact_multiplier
        output_data = {
            "company_id": company_id,
            "scenarios": {"base": {"ebitda_impact_pct": round(ebitda_impact_pct, 4), "confidence": "high"}}
        }
    elif tool_name == "analyze_whatif_scenario":
        company_id = args.get("company_id", "UNKNOWN")
        scenario_name = args.get("scenario_name", "UNKNOWN")
        dimension_changes = args.get("dimension_changes", {})
        investment_usd = args.get("investment_usd", 0)
        org_air_change = sum(dimension_changes.values()) * 0.6 / len(dimension_changes) if dimension_changes else 0
        projected_impact_usd = investment_usd * 0.18 # Mock 18% ROI
        output_data = {
            "company_id": company_id,
            "scenario": scenario_name,
            "org_air_change": round(org_air_change, 2),
            "projected_impact_usd": round(projected_impact_usd, 2),
            "confidence": "medium"
        }
    elif tool_name == "get_fund_portfolio":
        fund_id = args.get("fund_id", "UNKNOWN")
        output_data = {
            "fund_id": fund_id,
            "companies": [f"CompanyA-from-{fund_id}", f"CompanyB-from-{fund_id}", f"CompanyC-from-{fund_id}"]
        }
    else:
        raise ValueError(f"Unknown tool: {tool_name}")
    return [MockTextContent(json.dumps(output_data))]

async def list_resources_mcp():
    """Mocks the listing of static MCP Resources."""
    return [
        MockResource("orgair://companies", "List of all registered companies with basic details."),
        MockResource("orgair://sectors", "Definitions and baseline metrics for various industry sectors."),
        MockResource("orgair://parameters/v2.0", "Global parameters and configuration for Org-AI-R model version 2.0."),
    ]

async def list_resource_templates_mcp():
    """Mocks the listing of dynamic MCP Resource templates."""
    return [
        MockResourceTemplate("orgair://company/{{company_id}}/score", "AI-readiness score and detailed profile for a specific company."),
        MockResourceTemplate("orgair://fund/{{fund_id}}/companies", "List of companies associated with a particular investment fund."),
        MockResourceTemplate("orgair://metric/{{metric_name}}/history", "Historical data series for a given financial or operational metric."),
    ]

async def read_resource_mcp(uri: str):
    """Mocks the reading of content from an MCP Resource URI."""
    if uri == "orgair://companies":
        return json.dumps({"companies": [{"id": "ACME-001", "name": "ACME Corp"}, {"id": "GLOBEX-002", "name": "Globex Inc."}]})
    elif uri == "orgair://sectors":
        return json.dumps({"sectors": [{"id": "technology", "h_r_baseline": 75, "avg_air_score": 72.5}, {"id": "finance", "h_r_baseline": 68, "avg_air_score": 65.1}]})
    elif uri.startswith("orgair://company/") and "/score" in uri:
        company_id = uri.split("/")[3]
        return json.dumps({"company_id": company_id, "org_air_score": 78.5, "last_updated": "2023-10-27", "details": "Mock score data."})
    elif uri.startswith("orgair://fund/") and "/companies" in uri:
        fund_id = uri.split("/")[3]
        return json.dumps({"fund_id": fund_id, "companies": [f"CompanyA-{fund_id}", f"CompanyB-{fund_id}"]})
    elif uri.startswith("orgair://metric/") and "/history" in uri:
        metric_name = uri.split("/")[3]
        return json.dumps({"metric": metric_name, "history": [{"date": "2023-01-01", "value": 100}, {"date": "2023-04-01", "value": 105}]})
    raise ValueError(f"Resource not found or URI not supported by mock: {uri}")

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
        MockPrompt("competitive_analysis", "Performs a competitive analysis of AI readiness across a set of companies.", [
            {"name": "company_ids", "required": True, "description": "A comma-separated list of company IDs for analysis."}
        ])
    ]

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
    elif prompt_name == "value_creation_plan":
        company_id = args.get("company_id", "UNKNOWN")
        target_score = args.get("target_score", "N/A")
        timeline_months = args.get("timeline_months", "N/A")
        text = f"""
As an AI strategy consultant, develop a detailed AI Value Creation Plan for {company_id}.
The goal is to increase {company_id}'s Org-AI-R score to {target_score} within {timeline_months} months.
1. Begin by calling `calculate_org_air_score` to understand the current state.
2. Identify 2-3 key dimensions for improvement.
3. Use `analyze_whatif_scenario` to model the impact of targeted investments (e.g., $2M USD).
4. Project the potential EBITDA impact using `project_ebitda_impact` based on the target score.
5. Outline a phased roadmap (e.g., 3 phases) with actionable initiatives for each phase.
6. Estimate required investment and projected ROI.
Present the plan in a clear, actionable markdown format.
"""
    elif prompt_name == "competitive_analysis":
        company_ids_str = args.get("company_ids", "")
        company_ids = [c.strip() for c in company_ids_str.split(',') if c.strip()]
        text = f"""
Perform a competitive analysis of AI readiness for the following companies: {', '.join(company_ids)}.
For each company:
1. Call `calculate_org_air_score`.
2. Access relevant sector baselines from `orgair://sectors`.
3. Identify their relative strengths and weaknesses in AI.
4. Summarize the competitive landscape in terms of AI maturity and potential.
Provide the output as a comparative table and a narrative summary.
"""
    else:
        raise ValueError(f"Unknown prompt: {prompt_name}")
    return [MockPromptMessage(MockContent(text))]


# --- App Initialization ---
st.set_page_config(page_title="QuLab: Lab 9: MCP Server Implementation", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Lab 9: MCP Server Implementation")
st.divider()

# Initialize session state for page navigation if not already present
if "current_page" not in st.session_state:
    st.session_state.current_page = "Introduction"

# Global initialization for tool inputs and prompt inputs to ensure persistence across reruns and pages
if "all_tool_inputs" not in st.session_state:
    st.session_state.all_tool_inputs = {}
if "tool_output" not in st.session_state:
    st.session_state.tool_output = None # Holds output for the currently selected tool
if "prompt_all_inputs" not in st.session_state:
    st.session_state.prompt_all_inputs = {} # Holds inputs for all prompts, keyed by prompt name
if "prompt_output" not in st.session_state:
    st.session_state.prompt_output = None # Holds output for the currently selected prompt
if "resource_selected_uri" not in st.session_state:
    st.session_state.resource_selected_uri = ""
if "resource_output" not in st.session_state:
    st.session_state.resource_output = None
if "e2e_workflow_results" not in st.session_state:
    st.session_state.e2e_workflow_results = []


# --- Sidebar Navigation ---
st.sidebar.title("MCP Server Lab Navigation")
page_options = [
    "Introduction",
    "Define MCP Tools",
    "Standardize MCP Resources",
    "Empower MCP Prompts",
    "End-to-End Workflow Simulation",
]

# Use index to set default value compliant with Streamlit standards
try:
    current_index = page_options.index(st.session_state.current_page)
except ValueError:
    current_index = 0

st.session_state.current_page = st.sidebar.selectbox(
    "Go to section:",
    page_options,
    index=current_index
)

# --- Main Content Area (Conditional Rendering) ---

if st.session_state.current_page == "Introduction":
    # ----------------------------------------------------
    # 1. Introduction Page
    # ----------------------------------------------------
    st.subheader("1. Introduction: Laying the Groundwork for AI Interoperability")

    st.markdown(f"""
    Welcome to the **PE Org-AI-R Model Context Protocol (MCP) Server Implementation Lab**!

    As a Software Developer at PE Org-AI-R, a leading platform for Organizational AI-Readiness assessments, I'm tasked with a crucial project: establishing the foundational AI interoperability layer. Our goal is to enable AI agents, like Claude Desktop, to seamlessly access and interact with our core Org-AI-R capabilities. This means exposing our assessment tools, data resources, and strategic prompt templates through a standardized Model Context Protocol (MCP) server.

    Currently, our AI-readiness assessments are often siloed, requiring manual data exports or custom API integrations for each new AI tool or client. This is inefficient and prone to inconsistencies. By implementing an MCP server, we aim to standardize how AI agents discover, invoke, and interpret our services, reducing integration friction and enabling autonomous AI-driven insights across the organization. This lab will demonstrate the setup of the MCP server, the definition of its capabilities (Tools, Resources, Prompts), and their practical application in a simulated workflow.

    The core challenge is to transform our existing services into discoverable and executable MCP primitives. This involves:
    *   **Tools:** Exposing executable functions, such as calculating the Org-AI-R score or projecting EBITDA impact.
    *   **Resources:** Providing structured access to static data (e.g., sector baselines) and dynamic data (e.g., specific company scores).
    *   **Prompts:** Offering templated instructions for AI agents to perform complex, multi-step tasks like due diligence assessments or value creation plans.

    This project is pivotal for the organization, as it paves the way for a truly AI-ready ecosystem where intelligent agents can autonomously contribute to strategic decision-making, from assessing potential investments to identifying areas for AI-driven transformation within portfolio companies.
    """)

    st.subheader("Lab Preamble")
    st.markdown(f"**Key Objectives:**")
    st.markdown(f"- **Remember**: List MCP primitives (Tools, Resources, Prompts)")
    st.markdown(f"- **Understand**: Explain why protocol standardization enables interoperability")
    st.markdown(f"- **Apply**: Implement MCP server exposing PE Org-AI-R capabilities")
    st.markdown(f"- **Analyze**: Compare MCP vs custom API integrations")
    st.markdown(f"- **Create**: Design resource hierarchies for portfolio data")

    st.markdown(f"**Tools Introduced:**")
    st.markdown(f"| Tool           | Purpose               | Why This Tool              |")
    st.markdown(f"| :------------- | :-------------------- | :------------------------- |")
    st.markdown(f"| `mcp-sdk`      | MCP implementation    | Official Anthropic SDK     |")
    st.markdown(f"| `FastMCP`      | MCP server framework  | High-level abstractions    |")
    st.markdown(f"| Claude Desktop | MCP client            | Test integration           |")

    st.markdown(f"**Key Concepts:**")
    st.markdown(f"- Model Context Protocol (MCP) specification")
    st.markdown(f"- Tools vs Resources vs Prompts")
    st.markdown(f"- Transport layers (stdio, SSE)")
    st.markdown(f"- Claude Desktop integration")
    st.markdown(f"- Resource subscriptions")

    st.markdown(f"**Prerequisites:**")
    st.markdown(f"- Weeks 1-8 completed")
    st.markdown(f"- Understanding of JSON-RPC")
    st.markdown(f"- Familiarity with Claude Desktop")

    st.info("The MCP server and mock services have been initialized in `app.py` (due to `source.py` error).")


elif st.session_state.current_page == "Define MCP Tools":
    # ----------------------------------------------------
    # 2. Define MCP Tools Page
    # ----------------------------------------------------
    st.subheader("2. Building Core AI Assessment Tools")

    st.markdown(f"""
    My first task is to expose the core `calculate_org_air_score` functionality. This is the cornerstone of our platform, providing a holistic view of a company's AI readiness. Financial analysts, for example, will use AI agents to quickly assess the AI readiness of potential investment targets.

    The Org-AI-R score is a composite metric derived from several dimensions and adjusted by factors like talent concentration and sector-specific benchmarks. Conceptually, it combines:
    *   **Idiosyncratic Readiness ($V^R$):** Reflects internal capabilities, often a weighted average of dimension scores adjusted for specific company factors.
    *   **Systematic Opportunity ($H^R$):** Represents external market opportunities and sector-specific AI adoption baselines.
    *   **Synergy Score:** Captures the interaction between internal readiness and external opportunity.
    """)
    st.markdown(r"$$ S = f(V^R, H^R, \text{Synergy}) $$")
    st.markdown(r"where $S$ is the final Org-AI-R score, $V^R$ is Idiosyncratic Readiness, $H^R$ is Systematic Opportunity, and $\text{Synergy}$ is the interaction score.")
    st.markdown(f"""
    The tool will return not just the final score, but also its components and a confidence interval, giving AI agents a richer understanding of the assessment.

    I also need to expose other crucial tools: `get_company_evidence`, `project_ebitda_impact`, `analyze_whatif_scenario`, and `get_fund_portfolio`. These tools enable AI agents to gather supporting evidence, forecast financial impacts, simulate future scenarios, and aggregate portfolio-level insights. Each tool will have a clear `inputSchema` to guide AI agents on how to invoke them correctly.

    Below, you can interact with the defined MCP Tools. Select a tool, provide its required arguments, and execute it to see the structured output an AI agent would receive.
    """)

    if "tool_selected_name" not in st.session_state:
        st.session_state.tool_selected_name = "calculate_org_air_score"
    # st.session_state.all_tool_inputs is initialized globally

    available_tools_info = asyncio.run(list_tools())
    tool_names = [tool.name for tool in available_tools_info]
    tool_descriptions = {tool.name: tool.description for tool in available_tools_info}
    tool_schemas = {tool.name: tool.inputSchema for tool in available_tools_info}

    # Helper to find index safely
    try:
        tool_idx = tool_names.index(st.session_state.tool_selected_name)
    except ValueError:
        tool_idx = 0

    new_tool_selected_name = st.selectbox(
        "Select an MCP Tool to test:",
        tool_names,
        index=tool_idx,
        key="tool_selector"
    )

    # If the selected tool changes, reset the output and ensure input args are specific to the new tool
    if new_tool_selected_name != st.session_state.tool_selected_name:
        st.session_state.tool_selected_name = new_tool_selected_name
        st.session_state.tool_output = None # Clear previous tool's output
        # Ensure the current tool has an entry in all_tool_inputs
        if st.session_state.tool_selected_name not in st.session_state.all_tool_inputs:
            st.session_state.all_tool_inputs[st.session_state.tool_selected_name] = {}
    
    # Always point to the inputs for the currently selected tool
    current_tool_input_args = st.session_state.all_tool_inputs.setdefault(st.session_state.tool_selected_name, {})

    st.info(tool_descriptions[st.session_state.tool_selected_name])

    st.subheader(f"Input for `{st.session_state.tool_selected_name}`:")
    current_tool_schema = tool_schemas[st.session_state.tool_selected_name]
    required_fields = current_tool_schema.get("required", [])

    for prop_name, prop_details in current_tool_schema.get("properties", {}).items():
        label = f"{prop_name} ({'Required' if prop_name in required_fields else 'Optional'})"
        description = prop_details.get("description", "")
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{prop_name}**:")
            if description:
                st.caption(description)
        with col2:
            input_value = None
            # Get current value from the specific tool's input dict or schema default
            current_val = current_tool_input_args.get(prop_name, prop_details.get("default", None))
            
            # Unique key for each widget based on tool and property name
            widget_key = f"tool_input_{st.session_state.tool_selected_name}_{prop_name}"
            
            if prop_details["type"] == "string":
                if "enum" in prop_details:
                    default_enum_idx = 0
                    if current_val in prop_details["enum"]:
                        default_enum_idx = prop_details["enum"].index(current_val)
                    input_value = st.selectbox(f"Value for {prop_name}", prop_details["enum"], index=default_enum_idx, key=widget_key)
                else:
                    if current_val is None: current_val = ""
                    input_value = st.text_input(f"Value for {prop_name}", key=widget_key, value=str(current_val))
            
            elif prop_details["type"] == "number":
                if current_val is None: current_val = 0.0 # Default to 0.0 for numbers
                input_value = st.number_input(f"Value for {prop_name}", min_value=prop_details.get("minimum"), max_value=prop_details.get("maximum"), value=float(current_val), key=widget_key)
            
            elif prop_details["type"] == "integer":
                if current_val is None: current_val = 0 # Default to 0 for integers
                input_value = st.number_input(f"Value for {prop_name}", min_value=prop_details.get("minimum"), max_value=prop_details.get("maximum"), step=1, value=int(current_val), key=widget_key)
            
            elif prop_details["type"] == "boolean":
                if current_val is None: current_val = False
                input_value = st.checkbox(f"Value for {prop_name}", value=bool(current_val), key=widget_key)
            
            elif prop_details["type"] == "array" and prop_details.get("items", {}).get("type") == "number":
                default_val_str = ""
                if isinstance(current_val, list):
                    default_val_str = ",".join(map(str, current_val))
                input_str = st.text_input(f"Value for {prop_name} (comma-separated numbers)", key=widget_key, value=default_val_str)
                try:
                    if input_str.strip():
                        input_value = [float(x.strip()) for x in input_str.split(',') if x.strip()]
                    else:
                        input_value = []
                except ValueError:
                    st.error(f"Please enter valid comma-separated numbers for {prop_name}.")
                    input_value = None
            
            elif prop_details["type"] == "object" and prop_details.get("additionalProperties", {}).get("type") == "number":
                default_val_str = ""
                if isinstance(current_val, dict):
                    default_val_str = ", ".join([f"{k}:{v}" for k, v in current_val.items()])
                input_str = st.text_input(f"Value for {prop_name} (key1:value1, key2:value2)", key=widget_key, value=default_val_str)
                try:
                    input_value = {}
                    if input_str.strip():
                        for item in input_str.split(','):
                            if ':' in item:
                                key, val = item.split(':', 1)
                                input_value[key.strip()] = float(val.strip())
                            else:
                                raise ValueError("Invalid format")
                except ValueError:
                    st.error(f"Please enter valid comma-separated key:value pairs for {prop_name}.")
                    input_value = None

            # Update the specific tool's input dictionary
            if input_value is not None and (prop_details["type"] != "string" or input_value != ""):
                current_tool_input_args[prop_name] = input_value
            elif prop_name in current_tool_input_args: # Remove if input becomes empty (e.g. text cleared)
                del current_tool_input_args[prop_name]


    if st.button(f"Execute `{st.session_state.tool_selected_name}`"):
        try:
            # Validate required fields for the current tool
            missing_required = [field for field in required_fields if field not in current_tool_input_args or current_tool_input_args[field] is None or (isinstance(current_tool_input_args[field], str) and not current_tool_input_args[field])]
            if missing_required:
                st.error(f"Please provide values for all required fields: {', '.join(missing_required)}")
            else:
                # Filter args to only those in the schema to avoid passing extra state vars
                args_to_pass = {k: v for k, v in current_tool_input_args.items() if k in current_tool_schema.get("properties", {})}
                st.session_state.tool_output = asyncio.run(call_tool(st.session_state.tool_selected_name, args_to_pass))
                st.success("Tool executed successfully!")
        except Exception as e:
            st.error(f"Error executing tool: {e}")
            st.session_state.tool_output = None

    if st.session_state.tool_output:
        st.subheader("Tool Output:")
        # The call_tool returns a list of TextContent objects, each having a 'text' attribute with the JSON string
        try:
            output_json_str = st.session_state.tool_output[0].text if st.session_state.tool_output and len(st.session_state.tool_output) > 0 else "{}"
            st.json(json.loads(output_json_str))
        except (json.JSONDecodeError, AttributeError, IndexError) as e:
            st.error(f"Could not parse tool output as JSON or output format unexpected: {e}")
            st.code(st.session_state.tool_output)

    st.markdown(f"""
    In this section, we successfully interacted with MCP Tools. These tools provide comprehensive AI-readiness assessments, evidence retrieval, financial impact projections, what-if scenario analyses, and portfolio insights. The structured JSON outputs ensure that AI agents can easily parse and utilize the results.
    """)

elif st.session_state.current_page == "Standardize MCP Resources":
    # ----------------------------------------------------
    # 3. Standardize MCP Resources Page
    # ----------------------------------------------------
    st.subheader("3. Standardizing Data Access with MCP Resources")

    st.markdown(f"""
    Beyond executable tools, AI agents often need access to static reference data (like sector definitions or model parameters) and dynamic, contextual information (like a specific company's details or their current score). MCP Resources provide a standardized way to expose this data through URI-based access.

    For instance, an AI agent performing a sector-specific analysis might need to retrieve the `H^R` baselines for various sectors. Similarly, when a user asks about a specific company's AI-readiness profile, the AI agent should be able to fetch that information using a dynamic URI like `orgair://company/{{company_id}}/score`. This structured, URI-addressable data access is crucial for building robust AI applications that can autonomously gather necessary context.

    Below, explore the defined MCP Resources. You can list static resources, view dynamic resource templates, and then read a specific resource by providing its URI.
    """)

    # st.session_state.resource_selected_uri and st.session_state.resource_output are initialized globally

    st.subheader("Available Static Resources")
    static_resources_info = asyncio.run(list_resources_mcp())
    static_uris = [res.uri for res in static_resources_info]
    static_descriptions = {res.uri: res.description for res in static_resources_info}

    selected_static_uri = st.selectbox(
        "Select a static resource URI:",
        [""] + static_uris,
        index=0,
        key="static_uri_select"
    )
    if selected_static_uri:
        st.info(static_descriptions.get(selected_static_uri, "No description available."))
        # Update main URI input if user selects from here (helper behavior)
        if st.button("Use this Static URI", key="use_static_uri"):
             st.session_state.resource_selected_uri = selected_static_uri

    st.subheader("Dynamic Resource Templates")
    dynamic_templates_info = asyncio.run(list_resource_templates_mcp())
    dynamic_template_strings = [tmpl.uriTemplate for tmpl in dynamic_templates_info]
    dynamic_template_descriptions = {tmpl.uriTemplate: tmpl.description for tmpl in dynamic_templates_info}

    selected_template_string = st.selectbox(
        "Select a dynamic resource template:",
        [""] + dynamic_template_strings,
        index=0,
        key="dynamic_template_select"
    )
    if selected_template_string:
        st.info(dynamic_template_descriptions.get(selected_template_string, "No description available."))
        st.markdown(f"**Example for `{selected_template_string}`:**")
        
        preview_uri = selected_template_string
        if "company_id" in selected_template_string:
            example_company_id = st.text_input("Enter Company ID to preview URI:", "ACME-001", key="company_id_for_uri")
            preview_uri = selected_template_string.replace("{{company_id}}", example_company_id)
            st.code(preview_uri)
            if st.button("Use this URI", key="use_preview_uri_company"): # Unique key
                st.session_state.resource_selected_uri = preview_uri
        elif "fund_id" in selected_template_string:
            example_fund_id = st.text_input("Enter Fund ID to preview URI:", "PE-FUND-001", key="fund_id_for_uri")
            preview_uri = selected_template_string.replace("{{fund_id}}", example_fund_id)
            st.code(preview_uri)
            if st.button("Use this URI", key="use_preview_uri_fund"): # Unique key
                st.session_state.resource_selected_uri = preview_uri
        elif "metric_name" in selected_template_string:
            example_metric_name = st.text_input("Enter Metric Name to preview URI:", "ebitda_growth", key="metric_name_for_uri")
            preview_uri = selected_template_string.replace("{{metric_name}}", example_metric_name)
            st.code(preview_uri)
            if st.button("Use this URI", key="use_preview_uri_metric"): # Unique key
                st.session_state.resource_selected_uri = preview_uri


    st.subheader("Read a Resource by URI")
    st.session_state.resource_selected_uri = st.text_input(
        "Enter the full Resource URI (e.g., `orgair://sectors` or `orgair://company/ACME-001/score`):",
        value=st.session_state.resource_selected_uri,
        key="resource_uri_input"
    )

    if st.button("Read Resource"):
        if st.session_state.resource_selected_uri:
            try:
                st.session_state.resource_output = asyncio.run(read_resource_mcp(st.session_state.resource_selected_uri))
                st.success("Resource read successfully!")
            except Exception as e:
                st.error(f"Error reading resource: {e}")
                st.session_state.resource_output = None
        else:
            st.warning("Please enter a URI to read.")

    if st.session_state.resource_output:
        st.subheader("Resource Content:")
        try:
            st.json(json.loads(st.session_state.resource_output))
        except json.JSONDecodeError as e:
            st.error(f"Could not parse resource output as JSON: {e}")
            st.code(st.session_state.resource_output)

    st.markdown(f"""
    We've now fully configured and demonstrated the MCP Resource capabilities:
    *   **Static Resources:** `orgair://companies`, `orgair://sectors`, and `orgair://parameters/v2.0` are exposed, providing stable access to global configuration and reference data. AI agents can fetch sector-specific `H^R` baselines or the current EBITDA projection parameters, ensuring consistency across analyses.
    *   **Dynamic Resource Templates:** Templates like `orgair://company/{{company_id}}/score` allow AI agents to construct URIs dynamically to fetch specific, up-to-date information for individual entities (companies, funds). This is powerful for targeted inquiries.

    The `read_resource` function acts as the gateway, parsing the URI to determine which data to retrieve. This modular approach ensures that data access is standardized, discoverable, and easily extendable, fulfilling a critical requirement for flexible AI interoperability.
    """)

elif st.session_state.current_page == "Empower MCP Prompts":
    # ----------------------------------------------------
    # 4. Empower MCP Prompts Page
    # ----------------------------------------------------
    st.subheader("4. Empowering AI with Intelligent Prompts")

    st.markdown(f"""
    To further enhance the capabilities of AI agents, we need to provide them with structured guidance for complex analytical tasks. Instead of just exposing raw tools and data, MCP Prompts allow us to define reusable templates that guide an AI agent through a multi-step workflow.

    For example, an AI agent performing a `due_diligence_assessment` for a new investment target needs to:
    1.  Retrieve the Org-AI-R score.
    2.  Gather evidence for each dimension.
    3.  Analyze strengths and gaps.
    4.  Compare to benchmarks.
    5.  Identify risks and opportunities.
    6.  Formulate a recommendation.

    Defining this as a prompt template ensures that every AI agent performs due diligence consistently and comprehensively, delivering high-quality, structured output. Similarly, `value_creation_plan` and `competitive_analysis` prompts guide agents through other strategic tasks, reducing variability and improving efficiency.

    Below, you can explore the defined MCP Prompts. Select a prompt, provide its arguments, and generate the structured message that an AI agent would receive.
    """)

    if "prompt_selected_name" not in st.session_state:
        st.session_state.prompt_selected_name = "due_diligence_assessment"
    # st.session_state.prompt_all_inputs and st.session_state.prompt_output are initialized globally

    available_prompts_info = asyncio.run(list_prompts())
    prompt_names = [prompt.name for prompt in available_prompts_info]
    prompt_descriptions = {prompt.name: prompt.description for prompt in available_prompts_info}
    prompt_arguments_schema = {prompt.name: prompt.arguments for prompt in available_prompts_info}

    # Helper for index
    try:
        prompt_idx = prompt_names.index(st.session_state.prompt_selected_name)
    except ValueError:
        prompt_idx = 0

    new_prompt_selected_name = st.selectbox(
        "Select an MCP Prompt to generate:",
        prompt_names,
        index=prompt_idx,
        key="prompt_selector"
    )

    # If the selected prompt changes, clear the output and ensure input args are specific to the new prompt
    if new_prompt_selected_name != st.session_state.prompt_selected_name:
        st.session_state.prompt_selected_name = new_prompt_selected_name
        st.session_state.prompt_output = None # Clear previous prompt's output
        # Ensure the current prompt has an entry in prompt_all_inputs
        if st.session_state.prompt_selected_name not in st.session_state.prompt_all_inputs:
            st.session_state.prompt_all_inputs[st.session_state.prompt_selected_name] = {}

    # Always point to the inputs for the currently selected prompt
    current_prompt_input_args = st.session_state.prompt_all_inputs.setdefault(st.session_state.prompt_selected_name, {})

    st.info(prompt_descriptions[st.session_state.prompt_selected_name])

    st.subheader(f"Arguments for `{st.session_state.prompt_selected_name}`:")
    current_prompt_args_schema = prompt_arguments_schema[st.session_state.prompt_selected_name]

    for arg_details in current_prompt_args_schema:
        arg_name = arg_details["name"]
        is_required = arg_details.get("required", False)
        description = arg_details.get("description", "")

        label = f"{arg_name} ({'Required' if is_required else 'Optional'})"
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{arg_name}**:")
            if description:
                st.caption(description)
        with col2:
            # Use specific prompt's input args for value and create unique key
            input_value = st.text_input(
                f"Value for {arg_name}",
                key=f"prompt_input_{st.session_state.prompt_selected_name}_{arg_name}",
                value=current_prompt_input_args.get(arg_name, "")
            )
            if input_value:
                current_prompt_input_args[arg_name] = input_value
            else:
                # If input is cleared, remove from dictionary if it exists
                if arg_name in current_prompt_input_args:
                    del current_prompt_input_args[arg_name]

    if st.button(f"Generate `{st.session_state.prompt_selected_name}` Prompt"):
        try:
            # Basic validation for required fields
            missing_required = [
                arg["name"] for arg in current_prompt_args_schema
                if arg.get("required", False) and arg["name"] not in current_prompt_input_args
            ]
            if missing_required:
                st.error(f"Please provide values for all required arguments: {', '.join(missing_required)}")
            else:
                st.session_state.prompt_output = asyncio.run(get_prompt(st.session_state.prompt_selected_name, current_prompt_input_args))
                st.success("Prompt generated successfully!")
        except Exception as e:
            st.error(f"Error generating prompt: {e}")
            st.session_state.prompt_output = None

    if st.session_state.prompt_output:
        st.subheader("Generated Prompt Message (for AI Agent):")
        # get_prompt returns a list of PromptMessage objects
        if st.session_state.prompt_output and len(st.session_state.prompt_output) > 0:
            st.markdown(st.session_state.prompt_output[0].content.text)
        else:
            st.info("No prompt message generated.")

    st.markdown(f"""
    Here, we've implemented the `list_prompts` and `get_prompt` functionalities, enabling AI agents to request and receive structured task definitions:
    *   **`due_diligence_assessment`:** This prompt guides an AI agent through a comprehensive evaluation process, instructing it to use specific tools (`calculate_org_air_score`, `get_company_evidence`) and resources (`orgair://sectors`) in a defined sequence to produce a formal assessment.
    *   **`value_creation_plan`:** This prompt directs an AI agent to create a strategic plan for improving AI readiness and projecting its financial impact, leveraging tools like `analyze_whatif_scenario` and `project_ebitda_impact`.
    *   **`competitive_analysis`:** This prompt enables AI agents to perform a comparative study of AI readiness across multiple companies, providing insights into peer performance.

    By defining these prompts, we transform simple tool calls into complex, goal-oriented workflows that AI agents can execute autonomously. This greatly enhances the utility of our MCP server, allowing us to standardize high-level analytical tasks and ensure consistent, high-quality output from various AI clients.
    """)

elif st.session_state.current_page == "End-to-End Workflow Simulation":
    # ----------------------------------------------------
    # 5. End-to-End Workflow Simulation Page
    # ----------------------------------------------------
    st.subheader("5. Verifying Interoperability: Simulating an End-to-End Workflow")

    st.markdown(f"""
    Now that all MCP primitives (Tools, Resources, and Prompts) are defined and registered, it's time to demonstrate how an AI agent, like Claude Desktop, would orchestrate these capabilities to perform a complex real-world task. As a Software Developer, I want to simulate an agent performing a complete company assessment, from scoring to impact analysis, and then preparing a value creation plan. This confirms that our MCP server provides the necessary interoperability layer for AI agents to autonomously drive strategic insights.

    The workflow will involve:
    1.  **Initiation:** An AI agent receives a request to create a value creation plan for a company. It uses the `value_creation_plan` prompt template to understand the required steps.
    2.  **Current State Assessment:** The agent retrieves the current Org-AI-R score using the `calculate_org_air_score` tool and relevant company details from a resource.
    3.  **Gap Analysis & Evidence Gathering:** Based on the current score and target, the agent might infer areas for improvement and gather evidence using `get_company_evidence`.
    4.  **Scenario Modeling:** The agent uses `analyze_whatif_scenario` to model interventions for the identified improvement areas.
    5.  **Financial Impact Projection:** The agent projects the EBITDA impact of the improvements using the `project_ebitda_impact` tool.
    6.  **Plan Generation:** Finally, the agent synthesizes all this information into a structured value creation plan, guided by the prompt.

    This end-to-end simulation validates the true power of the MCP: enabling autonomous, intelligent, and standardized workflows for AI agents.
    """)

    # st.session_state.e2e_workflow_results is initialized globally

    async def run_e2e_workflow():
        st.session_state.e2e_workflow_results = []
        company_for_plan = "ACME-001"
        target_score_for_plan = "80" # Passed as string to prompt, then converted to float for tool call
        timeline_for_plan = "18"

        st.session_state.e2e_workflow_results.append(f"""
--- Simulating an AI Agent's End-to-End Value Creation Workflow ---
**Scenario:** An AI agent is tasked with creating an AI Value Creation Plan for `{company_for_plan}`.
""")

        st.session_state.e2e_workflow_results.append(f"**[AI Agent]:** Retrieving `value_creation_plan` prompt for {company_for_plan}...")
        value_plan_prompt_messages = await get_prompt(
            "value_creation_plan",
            {"company_id": company_for_plan, "target_score": target_score_for_plan, "timeline_months": timeline_for_plan}
        )
        if value_plan_prompt_messages:
            st.session_state.e2e_workflow_results.append(f"**Generated Prompt for AI Agent:**\n```markdown\n{value_plan_prompt_messages[0].content.text}\n```")
        else:
            st.session_state.e2e_workflow_results.append("**Generated Prompt for AI Agent:** _(Failed to retrieve prompt)_")


        st.session_state.e2e_workflow_results.append(f"\n**[AI Agent]:** Calling `calculate_org_air_score` for {company_for_plan}...")
        current_score_args = {
            "company_id": company_for_plan,
            "sector_id": "technology",
            "dimension_scores": [70, 65, 75, 68, 72, 60, 70],
            "talent_concentration": 0.2,
        }
        current_score_output = await call_tool("calculate_org_air_score", current_score_args)
        current_score_data = json.loads(current_score_output[0].text)
        current_org_air = current_score_data["final_score"]
        current_hr_score = current_score_data["components"]["h_r_score"]
        st.session_state.e2e_workflow_results.append(f"**Current Org-AI-R Score for {company_for_plan}:** `{current_org_air:.2f}`")
        st.session_state.e2e_workflow_results.append("**Tool Output (`calculate_org_air_score`):**")
        st.session_state.e2e_workflow_results.append(f"```json\n{json.dumps(current_score_data, indent=2, default=str)}\n```")


        st.session_state.e2e_workflow_results.append(f"\n**[AI Agent]:** Gathering evidence for 'data_infrastructure' in {company_for_plan}...")
        evidence_for_data_infra = await call_tool(
            "get_company_evidence",
            {"company_id": company_for_plan, "dimension": "data_infrastructure", "limit": 1}
        )
        evidence_data = json.loads(evidence_for_data_infra[0].text)
        sample_evidence_content = evidence_data["evidence_items"][0]["content"] if evidence_data["evidence_items"] else "No evidence found."
        st.session_state.e2e_workflow_results.append(f"**Sample Evidence (`get_company_evidence`):** `{sample_evidence_content}`")
        st.session_state.e2e_workflow_results.append("**Tool Output (`get_company_evidence`):**")
        st.session_state.e2e_workflow_results.append(f"```json\n{json.dumps(evidence_data, indent=2, default=str)}\n```")


        st.session_state.e2e_workflow_results.append(f"\n**[AI Agent]:** Analyzing what-if scenario for {company_for_plan}: 'Targeted_AI_Investment'...")
        whatif_scenario_args = {
            "company_id": company_for_plan,
            "scenario_name": "Targeted_AI_Investment",
            "dimension_changes": {"data_infrastructure": 10, "talent": 5},
            "investment_usd": 2000000,
        }
        whatif_result_output = await call_tool("analyze_whatif_scenario", whatif_scenario_args)
        whatif_data = json.loads(whatif_result_output[0].text)
        projected_org_air_change = whatif_data["org_air_change"]
        projected_financial_impact = whatif_data["projected_impact_usd"]
        st.session_state.e2e_workflow_results.append(f"**Projected Org-AI-R Change:** `{projected_org_air_change:.2f}`")
        st.session_state.e2e_workflow_results.append(f"**Projected Financial Impact (USD):** `${projected_financial_impact:,.2f}`")
        st.session_state.e2e_workflow_results.append("**Tool Output (`analyze_whatif_scenario`):**")
        st.session_state.e2e_workflow_results.append(f"```json\n{json.dumps(whatif_data, indent=2, default=str)}\n```")


        st.session_state.e2e_workflow_results.append(f"\n**[AI Agent]:** Projecting EBITDA impact for {company_for_plan} aiming for score {target_score_for_plan}...")
        ebitda_projection_args = {
            "company_id": company_for_plan,
            "entry_score": current_org_air,
            "target_score": float(target_score_for_plan), # Ensure target_score is float
            "h_r_score": current_hr_score,
            "holding_period_years": 3,
        }
        ebitda_impact_output = await call_tool("project_ebitda_impact", ebitda_projection_args)
        ebitda_impact_data = json.loads(ebitda_impact_output[0].text)
        base_ebitda_impact_pct = ebitda_impact_data["scenarios"]["base"]["ebitda_impact_pct"]
        st.session_state.e2e_workflow_results.append(f"**Projected Base EBITDA Impact:** `{base_ebitda_impact_pct * 100:.2f}%`")
        st.session_state.e2e_workflow_results.append("**Tool Output (`project_ebitda_impact`):**")
        st.session_state.e2e_workflow_results.append(f"```json\n{json.dumps(ebitda_impact_data, indent=2, default=str)}\n```")

        st.session_state.e2e_workflow_results.append(f"\n**[AI Agent]:** All data gathered. Now generating the full Value Creation Plan for {company_for_plan}...")
        final_plan_summary = f"""
--- AI Value Creation Plan Summary for {company_for_plan} ---
Target: Improve Org-AI-R score to {target_score_for_plan} within {timeline_for_plan} months.

1.  **Current Org-AI-R Score:** {current_org_air:.2f}
2.  **Key Improvement Areas:** Data Infrastructure, Talent (identified from gap analysis/evidence)
    *   *Example Evidence:* "{sample_evidence_content[:200]}..."
3.  **Modeled Scenario ('Targeted_AI_Investment'):**
    *   Expected Org-AI-R Change: +{projected_org_air_change:.2f}
    *   Estimated Financial Impact (USD): ${projected_financial_impact:,.2f}
    *   Confidence: Medium
4.  **Projected EBITDA Impact (Base Scenario):** +{base_ebitda_impact_pct * 100:.2f}% over 3 years.
5.  **Roadmap (Conceptual):**
    *   Phase 1 (Months 1-6): Data Governance Framework implementation, AI talent upskilling programs.
    *   Phase 2 (Months 7-12): Pilot AI-driven data analytics platform, develop internal AI champions.
    *   Phase 3 (Months 13-18): Scale successful AI initiatives, integrate AI into core business processes.
6.  **Estimated Investment:** $2,000,000 USD (for key initiatives)
7.  **Projected ROI:** High (based on EBITDA projections and efficiency gains)

This plan provides a strategic direction for {company_for_plan} to achieve its AI-readiness goals and unlock significant value.
"""
        st.session_state.e2e_workflow_results.append(f"```markdown\n{final_plan_summary}\n```")
        st.success("End-to-End Workflow Simulation Completed!")


    if st.button("Start AI Value Creation Workflow Simulation"):
        asyncio.run(run_e2e_workflow())
        st.rerun()

    if st.session_state.e2e_workflow_results:
        st.subheader("Simulation Steps & Results:")
        for result_item in st.session_state.e2e_workflow_results:
            # Check if the result item is a JSON string embedded in markdown-like format
            if result_item.strip().startswith("```json"):
                try:
                    # Extract the JSON string and parse it
                    json_str = result_item.replace("```json\n", "").replace("\n```", "").strip()
                    st.json(json.loads(json_str))
                except json.JSONDecodeError:
                    st.code(result_item) # Fallback to code if not valid JSON
            elif result_item.strip().startswith("```markdown"):
                # Display markdown content
                st.markdown(result_item.replace("```markdown\n", "").replace("\n```", ""))
            else:
                st.markdown(result_item)

    st.markdown(f"""
    This simulated end-to-end workflow demonstrates how an AI agent, powered by our MCP server, can execute a complex task like generating an "AI Value Creation Plan":
    1.  The agent starts by requesting a `value_creation_plan` prompt, which provides a structured set of instructions, essentially acting as a project brief.
    2.  It then autonomously invokes the `calculate_org_air_score` tool to fetch the current state of AI readiness.
    3.  It uses the `get_company_evidence` tool to gather supporting context for specific dimensions.
    4.  Next, it calls `analyze_whatif_scenario` to model the impact of proposed initiatives.
    5.  Finally, it leverages `project_ebitda_impact` to quantify the potential financial returns, specifically the `base_impact` percentage for EBITDA.
    6.  All these pieces of information, retrieved and analyzed through MCP primitives, are then synthesized by the AI agent into a coherent and actionable value creation plan summary.

    This demonstrates the core value proposition of our MCP server: enabling AI agents to interact intelligently and autonomously with our organization's capabilities, transforming raw data and models into strategic insights and actionable plans. For the Software Developer, this validates the successful integration and interoperability of all defined MCP components.
    """)
