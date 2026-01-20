
# Streamlit Application Specification: PE Org-AI-R MCP Server Implementation

## 1. Application Overview

### Purpose of the Application

The "PE Org-AI-R MCP Server Implementation" Streamlit application serves as an interactive blueprint for Software Developers at PE Org-AI-R. Its primary purpose is to demonstrate the step-by-step process of building and integrating a Model Context Protocol (MCP) server that exposes our core AI-Readiness assessment capabilities to AI agents like Claude Desktop. It illustrates how to define Tools, Resources, and Prompts, enabling standardized, autonomous AI interactions.

### High-Level Story Flow

As a Software Developer, I'm tasked with creating the foundational AI interoperability layer for PE Org-AI-R. This application guides me through this crucial project by simulating a multi-page experience:

1.  **Introduction**: I begin by understanding the concept of MCP, its importance for AI interoperability, and the initial setup of the MCP server and mock services. This sets the context for transforming our siloed AI-readiness assessments into a standardized, discoverable ecosystem.
2.  **Defining MCP Tools**: I then move to expose core Org-AI-R functionalities, such as calculating AI readiness scores or projecting financial impact, as MCP Tools. I interact with widgets to simulate tool invocation and observe the structured outputs, ensuring AI agents can programmatically access our services.
3.  **Standardizing MCP Resources**: Next, I learn how to standardize data access by defining MCP Resources. This involves exposing static reference data (e.g., sector baselines) and dynamic, contextual information (e.g., specific company scores) through URI-based access. I'll construct URIs and fetch data, simulating how AI agents gather context.
4.  **Empowering MCP Prompts**: I proceed to define sophisticated, multi-step workflows as MCP Prompts. This demonstrates how to guide AI agents through complex tasks like a "due diligence assessment" or a "value creation plan," ensuring consistent, high-quality analytical output. I'll generate prompt messages based on user inputs.
5.  **End-to-End Workflow Simulation**: Finally, the application culminates in an end-to-end simulation. I trigger a complete "AI Value Creation Plan" workflow for a hypothetical company. This demonstrates how an AI agent orchestrates tools, resources, and prompts autonomously to deliver strategic insights, validating the successful integration of our MCP server.

This application transitions me from theoretical understanding to practical application, showcasing how our MCP server enables AI agents to autonomously contribute to strategic decision-making.

## 2. Code Requirements

### Import Statement

```python
import streamlit as st
import asyncio
import json
from source import mcp_server, list_tools, call_tool, list_resources_mcp, list_resource_templates_mcp, read_resource_mcp, list_prompts, get_prompt
```

### `st.session_state` Design

*   `st.session_state.current_page`:
    *   **Initialized**: `st.session_state.current_page = "Introduction"`
    *   **Updated**: When the user selects an option from the sidebar `st.selectbox`.
    *   **Read**: To conditionally render content in the main area.
*   `st.session_state.tool_selected_name`:
    *   **Initialized**: `st.session_state.tool_selected_name = "calculate_org_air_score"` or `None`.
    *   **Updated**: When the user selects a tool from a `st.selectbox` on the "Define MCP Tools" page.
    *   **Read**: To determine which tool's input fields to display and which function to call.
*   `st.session_state.tool_input_args`:
    *   **Initialized**: `st.session_state.tool_input_args = {}`
    *   **Updated**: Dynamically as the user inputs values into `st.text_input`, `st.number_input`, `st.multiselect`, etc., for the selected tool. This will be a dictionary.
    *   **Read**: Passed as `arguments` to `call_tool`.
*   `st.session_state.tool_output`:
    *   **Initialized**: `st.session_state.tool_output = None`
    *   **Updated**: With the JSON string result from `asyncio.run(call_tool(...))`.
    *   **Read**: Displayed using `st.json` on the "Define MCP Tools" page.
*   `st.session_state.resource_selected_uri`:
    *   **Initialized**: `st.session_state.resource_selected_uri = ""`
    *   **Updated**: When the user selects a static resource from a `st.selectbox` or types a dynamic URI into `st.text_input` on the "Standardize MCP Resources" page.
    *   **Read**: Passed as `uri` to `read_resource_mcp`.
*   `st.session_state.resource_output`:
    *   **Initialized**: `st.session_state.resource_output = None`
    *   **Updated**: With the JSON string result from `asyncio.run(read_resource_mcp(...))`.
    *   **Read**: Displayed using `st.json` on the "Standardize MCP Resources" page.
*   `st.session_state.prompt_selected_name`:
    *   **Initialized**: `st.session_state.prompt_selected_name = "due_diligence_assessment"` or `None`.
    *   **Updated**: When the user selects a prompt from a `st.selectbox` on the "Empower MCP Prompts" page.
    *   **Read**: To determine which prompt's input fields to display and which function to call.
*   `st.session_state.prompt_input_args`:
    *   **Initialized**: `st.session_state.prompt_input_args = {}`
    *   **Updated**: Dynamically as the user inputs values into `st.text_input` for the selected prompt. This will be a dictionary of string arguments.
    *   **Read**: Passed as `arguments` to `get_prompt`.
*   `st.session_state.prompt_output`:
    *   **Initialized**: `st.session_state.prompt_output = None`
    *   **Updated**: With the `PromptMessage` list result from `asyncio.run(get_prompt(...))`.
    *   **Read**: Displayed as markdown on the "Empower MCP Prompts" page.
*   `st.session_state.e2e_workflow_results`:
    *   **Initialized**: `st.session_state.e2e_workflow_results = []`
    *   **Updated**: Appended with markdown strings and JSON results during the execution of the "End-to-End Workflow Simulation".
    *   **Read**: Displayed sequentially on the "End-to-End Workflow Simulation" page.

### Application Structure and Flow

The application will use a sidebar for navigation and conditional rendering for the main content.

```python
# --- App Initialization ---
st.set_page_config(layout="wide", page_title="PE Org-AI-R MCP Server Lab")

# Initialize session state for page navigation if not already present
if "current_page" not in st.session_state:
    st.session_state.current_page = "Introduction"

# --- Sidebar Navigation ---
st.sidebar.title("MCP Server Lab Navigation")
page_options = [
    "Introduction",
    "Define MCP Tools",
    "Standardize MCP Resources",
    "Empower MCP Prompts",
    "End-to-End Workflow Simulation",
]
st.session_state.current_page = st.sidebar.selectbox(
    "Go to section:",
    page_options,
    index=page_options.index(st.session_state.current_page)
)

# --- Main Content Area (Conditional Rendering) ---

if st.session_state.current_page == "Introduction":
    # ----------------------------------------------------
    # 1. Introduction Page
    # ----------------------------------------------------
    st.title("1. Introduction: Laying the Groundwork for AI Interoperability")

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

    st.info("The MCP server and mock services have been initialized in `source.py`.")


elif st.session_state.current_page == "Define MCP Tools":
    # ----------------------------------------------------
    # 2. Define MCP Tools Page
    # ----------------------------------------------------
    st.title("2. Building Core AI Assessment Tools")

    st.markdown(f"""
    My first task is to expose the core `calculate_org_air_score` functionality. This is the cornerstone of our platform, providing a holistic view of a company's AI readiness. Financial analysts, for example, will use AI agents to quickly assess the AI readiness of potential investment targets.

    The Org-AI-R score is a composite metric derived from several dimensions and adjusted by factors like talent concentration and sector-specific benchmarks. Conceptually, it combines:
    *   **Idiosyncratic Readiness ($V^R$):** Reflects internal capabilities, often a weighted average of dimension scores adjusted for specific company factors.
    *   **Systematic Opportunity ($H^R$):** Represents external market opportunities and sector-specific AI adoption baselines.
    *   **Synergy Score:** Captures the interaction between internal readiness and external opportunity.
    """)
    st.markdown(r"$$ S = f(V^R, H^R, \text{{Synergy}}) $$")
    st.markdown(r"where $S$ is the final Org-AI-R score, $V^R$ is Idiosyncratic Readiness, $H^R$ is Systematic Opportunity, and $\text{Synergy}$ is the interaction score.")
    st.markdown(f"""
    The tool will return not just the final score, but also its components and a confidence interval, giving AI agents a richer understanding of the assessment.

    I also need to expose other crucial tools: `get_company_evidence`, `project_ebitda_impact`, `analyze_whatif_scenario`, and `get_fund_portfolio`. These tools enable AI agents to gather supporting evidence, forecast financial impacts, simulate future scenarios, and aggregate portfolio-level insights. Each tool will have a clear `inputSchema` to guide AI agents on how to invoke them correctly.

    Below, you can interact with the defined MCP Tools. Select a tool, provide its required arguments, and execute it to see the structured output an AI agent would receive.
    """)

    # Tool selection
    if "tool_selected_name" not in st.session_state:
        st.session_state.tool_selected_name = "calculate_org_air_score"
    if "tool_input_args" not in st.session_state:
        st.session_state.tool_input_args = {}
    if "tool_output" not in st.session_state:
        st.session_state.tool_output = None

    available_tools_info = asyncio.run(list_tools())
    tool_names = [tool.name for tool in available_tools_info]
    tool_descriptions = {tool.name: tool.description for tool in available_tools_info}
    tool_schemas = {tool.name: tool.inputSchema for tool in available_tools_info}

    st.session_state.tool_selected_name = st.selectbox(
        "Select an MCP Tool to test:",
        tool_names,
        index=tool_names.index(st.session_state.tool_selected_name) if st.session_state.tool_selected_name in tool_names else 0
    )

    st.info(tool_descriptions[st.session_state.tool_selected_name])

    st.subheader(f"Input for `{st.session_state.tool_selected_name}`:")
    current_tool_schema = tool_schemas[st.session_state.tool_selected_name]
    required_fields = current_tool_schema.get("required", [])

    # Dynamically generate input widgets based on the schema
    st.session_state.tool_input_args = {}
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
            if prop_details["type"] == "string":
                if "enum" in prop_details:
                    input_value = st.selectbox(f"Value for {prop_name}", prop_details["enum"], key=f"tool_input_{prop_name}")
                else:
                    input_value = st.text_input(f"Value for {prop_name}", key=f"tool_input_{prop_name}", value=st.session_state.tool_input_args.get(prop_name, ""))
            elif prop_details["type"] == "number":
                input_value = st.number_input(f"Value for {prop_name}", min_value=prop_details.get("minimum"), max_value=prop_details.get("maximum"), value=float(st.session_state.tool_input_args.get(prop_name, prop_details.get("default", 0.0))), key=f"tool_input_{prop_name}")
            elif prop_details["type"] == "integer":
                input_value = st.number_input(f"Value for {prop_name}", min_value=prop_details.get("minimum"), max_value=prop_details.get("maximum"), step=1, value=int(st.session_state.tool_input_args.get(prop_name, prop_details.get("default", 0))), key=f"tool_input_{prop_name}")
            elif prop_details["type"] == "boolean":
                input_value = st.checkbox(f"Value for {prop_name}", value=st.session_state.tool_input_args.get(prop_name, prop_details.get("default", False)), key=f"tool_input_{prop_name}")
            elif prop_details["type"] == "array" and prop_details.get("items", {}).get("type") == "number":
                # For dimension_scores, allow comma-separated numbers
                default_val = st.session_state.tool_input_args.get(prop_name, "")
                if isinstance(default_val, list):
                    default_val = ",".join(map(str, default_val))
                input_str = st.text_input(f"Value for {prop_name} (comma-separated numbers)", key=f"tool_input_{prop_name}", value=default_val)
                try:
                    input_value = [float(x.strip()) for x in input_str.split(',') if x.strip()]
                except ValueError:
                    st.error(f"Please enter valid comma-separated numbers for {prop_name}.")
                    input_value = None
            elif prop_details["type"] == "object" and prop_details.get("additionalProperties", {}).get("type") == "number":
                # For dimension_changes, allow comma-separated key:value pairs
                default_val = st.session_state.tool_input_args.get(prop_name, "")
                if isinstance(default_val, dict):
                    default_val = ", ".join([f"{k}:{v}" for k, v in default_val.items()])
                input_str = st.text_input(f"Value for {prop_name} (key1:value1, key2:value2)", key=f"tool_input_{prop_name}", value=default_val)
                try:
                    input_value = {}
                    for item in input_str.split(','):
                        if ':' in item:
                            key, val = item.split(':', 1)
                            input_value[key.strip()] = float(val.strip())
                except ValueError:
                    st.error(f"Please enter valid comma-separated key:value pairs for {prop_name}.")
                    input_value = None

            if input_value is not None:
                st.session_state.tool_input_args[prop_name] = input_value

    if st.button(f"Execute `{st.session_state.tool_selected_name}`"):
        try:
            # Validate required fields
            missing_required = [field for field in required_fields if field not in st.session_state.tool_input_args or st.session_state.tool_input_args[field] is None or (isinstance(st.session_state.tool_input_args[field], str) and not st.session_state.tool_input_args[field])]
            if missing_required:
                st.error(f"Please provide values for all required fields: {', '.join(missing_required)}")
            else:
                st.session_state.tool_output = asyncio.run(call_tool(st.session_state.tool_selected_name, st.session_state.tool_input_args))
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
        except (json.JSONDecodeError, AttributeError) as e:
            st.error(f"Could not parse tool output as JSON: {e}")
            st.code(st.session_state.tool_output)

    st.markdown(f"""
    In this section, we successfully interacted with MCP Tools. These tools provide comprehensive AI-readiness assessments, evidence retrieval, financial impact projections, what-if scenario analyses, and portfolio insights. The structured JSON outputs ensure that AI agents can easily parse and utilize the results.
    """)

elif st.session_state.current_page == "Standardize MCP Resources":
    # ----------------------------------------------------
    # 3. Standardize MCP Resources Page
    # ----------------------------------------------------
    st.title("3. Standardizing Data Access with MCP Resources")

    st.markdown(f"""
    Beyond executable tools, AI agents often need access to static reference data (like sector definitions or model parameters) and dynamic, contextual information (like a specific company's details or their current score). MCP Resources provide a standardized way to expose this data through URI-based access.

    For instance, an AI agent performing a sector-specific analysis might need to retrieve the `H^R` baselines for various sectors. Similarly, when a user asks about a specific company's AI-readiness profile, the AI agent should be able to fetch that information using a dynamic URI like `orgair://company/{{company_id}}/score`. This structured, URI-addressable data access is crucial for building robust AI applications that can autonomously gather necessary context.

    Below, explore the defined MCP Resources. You can list static resources, view dynamic resource templates, and then read a specific resource by providing its URI.
    """)

    if "resource_selected_uri" not in st.session_state:
        st.session_state.resource_selected_uri = ""
    if "resource_output" not in st.session_state:
        st.session_state.resource_output = None

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
        if "company_id" in selected_template_string:
            example_company_id = st.text_input("Enter Company ID to preview URI:", "ACME-001", key="company_id_for_uri")
            preview_uri = selected_template_string.replace("{{company_id}}", example_company_id)
            st.code(preview_uri)
            if st.button("Use this URI", key="use_preview_uri"):
                st.session_state.resource_selected_uri = preview_uri
        elif "fund_id" in selected_template_string:
            example_fund_id = st.text_input("Enter Fund ID to preview URI:", "PE-FUND-001", key="fund_id_for_uri")
            preview_uri = selected_template_string.replace("{{fund_id}}", example_fund_id)
            st.code(preview_uri)
            if st.button("Use this URI", key="use_preview_uri_fund"):
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
    st.title("4. Empowering AI with Intelligent Prompts")

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
    if "prompt_input_args" not in st.session_state:
        st.session_state.prompt_input_args = {}
    if "prompt_output" not in st.session_state:
        st.session_state.prompt_output = None

    available_prompts_info = asyncio.run(list_prompts())
    prompt_names = [prompt.name for prompt in available_prompts_info]
    prompt_descriptions = {prompt.name: prompt.description for prompt in available_prompts_info}
    prompt_arguments_schema = {prompt.name: prompt.arguments for prompt in available_prompts_info}

    st.session_state.prompt_selected_name = st.selectbox(
        "Select an MCP Prompt to generate:",
        prompt_names,
        index=prompt_names.index(st.session_state.prompt_selected_name) if st.session_state.prompt_selected_name in prompt_names else 0
    )

    st.info(prompt_descriptions[st.session_state.prompt_selected_name])

    st.subheader(f"Arguments for `{st.session_state.prompt_selected_name}`:")
    current_prompt_args_schema = prompt_arguments_schema[st.session_state.prompt_selected_name]

    st.session_state.prompt_input_args = {}
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
            input_value = st.text_input(
                f"Value for {arg_name}",
                key=f"prompt_input_{arg_name}",
                value=st.session_state.prompt_input_args.get(arg_name, "")
            )
            if input_value: # Only add if not empty to allow optional fields to be truly optional
                st.session_state.prompt_input_args[arg_name] = input_value

    if st.button(f"Generate `{st.session_state.prompt_selected_name}` Prompt"):
        try:
            # Basic validation for required fields
            missing_required = [
                arg["name"] for arg in current_prompt_args_schema
                if arg.get("required", False) and arg["name"] not in st.session_state.prompt_input_args
            ]
            if missing_required:
                st.error(f"Please provide values for all required arguments: {', '.join(missing_required)}")
            else:
                st.session_state.prompt_output = asyncio.run(get_prompt(st.session_state.prompt_selected_name, st.session_state.prompt_input_args))
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
    st.title("5. Verifying Interoperability: Simulating an End-to-End Workflow")

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

    if "e2e_workflow_results" not in st.session_state:
        st.session_state.e2e_workflow_results = []

    async def run_e2e_workflow():
        st.session_state.e2e_workflow_results = []
        company_for_plan = "ACME-001"
        target_score_for_plan = "80"
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
            "target_score": float(target_score_for_plan),
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
        # Force re-render to show results incrementally if run_e2e_workflow were truly yielding
        # For a full blocking run, once it completes, the results are ready in session_state
        st.rerun()

    if st.session_state.e2e_workflow_results:
        st.subheader("Simulation Steps & Results:")
        for result_item in st.session_state.e2e_workflow_results:
            if result_item.startswith("```json"):
                st.json(json.loads(result_item.replace("```json\n", "").replace("\n```", "")))
            elif result_item.startswith("```markdown"):
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
```
