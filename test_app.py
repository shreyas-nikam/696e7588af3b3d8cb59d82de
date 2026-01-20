
import pytest
from streamlit.testing.v1 import AppTest
import asyncio
import json
from unittest.mock import MagicMock, patch

# Mock the source.py functions since they are not provided in the snippet
# These mocks should reflect the expected return types and structures
mock_tools_info = [
    MagicMock(name="calculate_org_air_score", description="Calculate Org-AI-R Score",
               inputSchema={"type": "object", "properties": {
                   "company_id": {"type": "string", "description": "ID of the company", "default": "ACME-001"},
                   "sector_id": {"type": "string", "description": "Sector ID", "enum": ["technology", "finance"], "default": "technology"},
                   "dimension_scores": {"type": "array", "items": {"type": "number"}, "description": "Scores for various dimensions"},
                   "talent_concentration": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.2}},
                   "required": ["company_id", "sector_id", "dimension_scores"]}),
    MagicMock(name="get_company_evidence", description="Retrieve evidence for a company",
               inputSchema={"type": "object", "properties": {
                   "company_id": {"type": "string", "description": "ID of the company"},
                   "dimension": {"type": "string", "description": "Dimension to get evidence for"},
                   "limit": {"type": "integer", "default": 1}},
                   "required": ["company_id", "dimension"]}),
    MagicMock(name="project_ebitda_impact", description="Project EBITDA impact",
               inputSchema={"type": "object", "properties": {
                   "company_id": {"type": "string"},
                   "entry_score": {"type": "number"},
                   "target_score": {"type": "number"},
                   "h_r_score": {"type": "number"},
                   "holding_period_years": {"type": "integer"}},
                   "required": ["company_id", "entry_score", "target_score", "h_r_score"]}),
    MagicMock(name="analyze_whatif_scenario", description="Analyze what-if scenario",
               inputSchema={"type": "object", "properties": {
                   "company_id": {"type": "string"},
                   "scenario_name": {"type": "string"},
                   "dimension_changes": {"type": "object", "additionalProperties": {"type": "number"}},
                   "investment_usd": {"type": "number"}},
                   "required": ["company_id", "scenario_name"]}),
]

mock_resources_info = [
    MagicMock(uri="orgair://companies", description="List of all companies"),
    MagicMock(uri="orgair://sectors", description="Definitions of sectors"),
]

mock_resource_templates_info = [
    MagicMock(uriTemplate="orgair://company/{{company_id}}/score", description="Individual company score"),
    MagicMock(uriTemplate="orgair://fund/{{fund_id}}/performance", description="Fund performance data"),
]

mock_prompts_info = [
    MagicMock(name="due_diligence_assessment", description="Perform a due diligence assessment",
               arguments=[
                   {"name": "company_id", "type": "string", "required": True, "description": "ID of the company"},
                   {"name": "investment_target", "type": "string", "required": False, "description": "Target of investment"},
                   {"name": "sector", "type": "string", "required": True, "description": "Sector of the company"}
               ]),
    MagicMock(name="value_creation_plan", description="Generate a value creation plan",
               arguments=[
                   {"name": "company_id", "type": "string", "required": True, "description": "ID of the company"},
                   {"name": "target_score", "type": "string", "required": False, "description": "Target Org-AI-R score"},
                   {"name": "timeline_months", "type": "string", "required": False, "description": "Timeline in months"}
               ]),
]

# Mock return values for call_tool and read_resource_mcp based on expected JSON structures
mock_tool_output = {
    "calculate_org_air_score": json.dumps({
        "final_score": 70.5,
        "confidence_interval": [68.0, 73.0],
        "components": {"v_r_score": 70, "h_r_score": 71, "synergy_score": 0.5},
        "details": "Composite score based on dimensions and adjustments."
    }),
    "get_company_evidence": json.dumps({
        "company_id": "ACME-001",
        "dimension": "data_infrastructure",
        "evidence_items": [{"id": "doc1", "content": "Company has robust data warehousing."}],
        "summary": "Evidence points to strong data infrastructure."
    }),
    "project_ebitda_impact": json.dumps({
        "company_id": "ACME-001",
        "scenarios": {"base": {"ebitda_impact_pct": 0.15, "ebitda_impact_usd": 1500000}},
        "notes": "Projection based on achieving target AI-readiness score."
    }),
    "analyze_whatif_scenario": json.dumps({
        "company_id": "ACME-001",
        "scenario_name": "Targeted_AI_Investment",
        "org_air_change": 5.0,
        "projected_impact_usd": 1000000,
        "confidence": "Medium"
    }),
}

mock_resource_output = {
    "orgair://sectors": json.dumps({"sectors": [{"id": "technology", "name": "Technology"}, {"id": "finance", "name": "Finance"}]}),
    "orgair://company/ACME-001/score": json.dumps({"company_id": "ACME-001", "org_air_score": 75.2, "last_updated": "2023-10-26"})
}

mock_prompt_output = {
    "due_diligence_assessment": MagicMock(content=MagicMock(text="Perform a comprehensive due diligence for ACME-001 in the technology sector.")),
    "value_creation_plan": MagicMock(content=MagicMock(text="Develop a value creation plan for ACME-001 aiming for 80 score in 18 months."))
}

@patch('source.list_tools', new=lambda: asyncio.Future(set_result=lambda x: x(mock_tools_info)))
@patch('source.call_tool', new=lambda name, args: asyncio.Future(set_result=lambda x: x([MagicMock(text=mock_tool_output.get(name, "{}"))])))
@patch('source.list_resources_mcp', new=lambda: asyncio.Future(set_result=lambda x: x(mock_resources_info)))
@patch('source.list_resource_templates_mcp', new=lambda: asyncio.Future(set_result=lambda x: x(mock_resource_templates_info)))
@patch('source.read_resource_mcp', new=lambda uri: asyncio.Future(set_result=lambda x: x(mock_resource_output.get(uri, "{}")))))
@patch('source.list_prompts', new=lambda: asyncio.Future(set_result=lambda x: x(mock_prompts_info)))
@patch('source.get_prompt', new=lambda name, args: asyncio.Future(set_result=lambda x: x([mock_prompt_output.get(name, MagicMock(content=MagicMock(text="")))])))
def test_app_initialization_and_introduction_page():
    at = AppTest.from_file("app.py").run()
    assert at.title[0].value == "QuLab: Lab 9: MCP Server Implementation"
    assert "Introduction: Laying the Groundwork for AI Interoperability" in at.markdown[0].value
    assert "Welcome to the **PE Org-AI-R Model Context Protocol (MCP) Server Implementation Lab**!" in at.markdown[0].value
    assert "Remember: List MCP primitives (Tools, Resources, Prompts)" in at.markdown[1].value
    assert "mcp-sdk" in at.markdown[2].value
    assert "Model Context Protocol (MCP) specification" in at.markdown[3].value
    assert "Weeks 1-8 completed" in at.markdown[4].value
    assert at.info[0].value == "The MCP server and mock services have been initialized in `source.py`."

def test_navigation():
    at = AppTest.from_file("app.py").run()

    # Navigate to "Define MCP Tools"
    at.sidebar.selectbox[0].set_value("Define MCP Tools").run()
    assert at.subheader[0].value == "2. Building Core AI Assessment Tools"
    assert at.session_state["current_page"] == "Define MCP Tools"

    # Navigate to "Standardize MCP Resources"
    at.sidebar.selectbox[0].set_value("Standardize MCP Resources").run()
    assert at.subheader[0].value == "3. Standardizing Data Access with MCP Resources"
    assert at.session_state["current_page"] == "Standardize MCP Resources"

    # Navigate to "Empower MCP Prompts"
    at.sidebar.selectbox[0].set_value("Empower MCP Prompts").run()
    assert at.subheader[0].value == "4. Empowering AI with Intelligent Prompts"
    assert at.session_state["current_page"] == "Empower MCP Prompts"

    # Navigate to "End-to-End Workflow Simulation"
    at.sidebar.selectbox[0].set_value("End-to-End Workflow Simulation").run()
    assert at.subheader[0].value == "5. Verifying Interoperability: Simulating an End-to-End Workflow"
    assert at.session_state["current_page"] == "End-to-End Workflow Simulation"

@patch('source.list_tools', new=lambda: asyncio.Future(set_result=lambda x: x(mock_tools_info)))
@patch('source.call_tool', new=lambda name, args: asyncio.Future(set_result=lambda x: x([MagicMock(text=mock_tool_output.get(name, "{}"))])))
def test_define_mcp_tools_page():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("Define MCP Tools").run()

    # Test default tool selection and info
    assert at.selectbox[0].value == "calculate_org_air_score"
    assert at.info[0].value == "Calculate Org-AI-R Score"

    # Provide valid inputs for calculate_org_air_score
    at.text_input[0].set_value("ACME-001").run() # company_id
    at.selectbox[1].set_value("technology").run() # sector_id
    at.text_input[1].set_value("70,65,75,68,72,60,70").run() # dimension_scores
    at.number_input[0].set_value(0.25).run() # talent_concentration
    at.button[0].click().run()

    assert at.success[0].value == "Tool executed successfully!"
    assert at.json[0].value == json.loads(mock_tool_output["calculate_org_air_score"])

    # Test selecting another tool and inputs (get_company_evidence)
    at.selectbox[0].set_value("get_company_evidence").run()
    assert at.info[0].value == "Retrieve evidence for a company"
    at.text_input[0].set_value("ACME-001").run() # company_id
    at.text_input[1].set_value("data_infrastructure").run() # dimension
    at.number_input[0].set_value(2).run() # limit
    at.button[0].click().run()

    assert at.success[0].value == "Tool executed successfully!"
    assert at.json[0].value == json.loads(mock_tool_output["get_company_evidence"])

    # Test error for missing required field (company_id for calculate_org_air_score)
    at.selectbox[0].set_value("calculate_org_air_score").run()
    at.text_input[0].set_value("").run() # Clear company_id
    at.button[0].click().run()
    assert at.error[0].value == "Please provide values for all required fields: company_id"

@patch('source.list_resources_mcp', new=lambda: asyncio.Future(set_result=lambda x: x(mock_resources_info)))
@patch('source.list_resource_templates_mcp', new=lambda: asyncio.Future(set_result=lambda x: x(mock_resource_templates_info)))
@patch('source.read_resource_mcp', new=lambda uri: asyncio.Future(set_result=lambda x: x(mock_resource_output.get(uri, "{}")))))
def test_standardize_mcp_resources_page():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("Standardize MCP Resources").run()

    # Test selecting a static resource
    at.selectbox[0].set_value("orgair://sectors").run()
    assert at.info[0].value == "Definitions of sectors"
    at.button[0].click().run() # "Use this Static URI"
    assert at.text_input[0].value == "orgair://sectors"

    # Read the static resource
    at.button[1].click().run() # "Read Resource"
    assert at.success[0].value == "Resource read successfully!"
    assert at.json[0].value == json.loads(mock_resource_output["orgair://sectors"])

    # Test selecting a dynamic template and generating URI
    at.selectbox[1].set_value("orgair://company/{{company_id}}/score").run()
    assert at.info[1].value == "Individual company score"
    at.text_input[1].set_value("NEW-CO-007").run() # Enter Company ID to preview URI
    at.button[2].click().run() # "Use this URI"
    assert at.text_input[0].value == "orgair://company/NEW-CO-007/score"

    # Read the dynamic resource
    at.button[1].click().run() # "Read Resource"
    assert at.success[0].value == "Resource read successfully!"
    # The mock returns a specific company score, so we expect that for any company_id
    assert at.json[0].value == json.loads(mock_resource_output["orgair://company/ACME-001/score"])

    # Test empty URI
    at.text_input[0].set_value("").run()
    at.button[1].click().run()
    assert at.warning[0].value == "Please enter a URI to read."

@patch('source.list_prompts', new=lambda: asyncio.Future(set_result=lambda x: x(mock_prompts_info)))
@patch('source.get_prompt', new=lambda name, args: asyncio.Future(set_result=lambda x: x([mock_prompt_output.get(name, MagicMock(content=MagicMock(text="")))])))
def test_empower_mcp_prompts_page():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("Empower MCP Prompts").run()

    # Test default prompt selection and info
    assert at.selectbox[0].value == "due_diligence_assessment"
    assert at.info[0].value == "Perform a due diligence assessment"

    # Provide valid arguments for due_diligence_assessment
    at.text_input[0].set_value("ACME-001").run() # company_id
    at.text_input[1].set_value("Growth Fund").run() # investment_target (optional)
    at.text_input[2].set_value("technology").run() # sector
    at.button[0].click().run() # Generate Prompt

    assert at.success[0].value == "Prompt generated successfully!"
    assert at.markdown[2].value == mock_prompt_output["due_diligence_assessment"].content.text

    # Test selecting another prompt (value_creation_plan) and inputs
    at.selectbox[0].set_value("value_creation_plan").run()
    assert at.info[0].value == "Generate a value creation plan"
    at.text_input[0].set_value("ACME-001").run() # company_id
    at.text_input[1].set_value("80").run() # target_score
    at.text_input[2].set_value("18").run() # timeline_months
    at.button[0].click().run()

    assert at.success[0].value == "Prompt generated successfully!"
    assert at.markdown[2].value == mock_prompt_output["value_creation_plan"].content.text

    # Test error for missing required argument (company_id for value_creation_plan)
    at.selectbox[0].set_value("value_creation_plan").run()
    at.text_input[0].set_value("").run() # Clear company_id
    at.button[0].click().run()
    assert at.error[0].value == "Please provide values for all required arguments: company_id"

@patch('source.list_tools', new=lambda: asyncio.Future(set_result=lambda x: x(mock_tools_info)))
@patch('source.call_tool', new=lambda name, args: asyncio.Future(set_result=lambda x: x([MagicMock(text=mock_tool_output.get(name, "{}"))])))
@patch('source.list_prompts', new=lambda: asyncio.Future(set_result=lambda x: x(mock_prompts_info)))
@patch('source.get_prompt', new=lambda name, args: asyncio.Future(set_result=lambda x: x([mock_prompt_output.get(name, MagicMock(content=MagicMock(text="")))])))
@patch('source.read_resource_mcp', new=lambda uri: asyncio.Future(set_result=lambda x: x(mock_resource_output.get(uri, "{}")))))
def test_end_to_end_workflow_simulation_page():
    at = AppTest.from_file("app.py").run()
    at.sidebar.selectbox[0].set_value("End-to-End Workflow Simulation").run()

    at.button[0].click().run() # "Start AI Value Creation Workflow Simulation"

    assert at.success[0].value == "End-to-End Workflow Simulation Completed!"
    # Check for key content from the simulation results
    assert any("Simulating an AI Agent's End-to-End Value Creation Workflow" in item for item in at.session_state["e2e_workflow_results"])
    assert any("Current Org-AI-R Score for ACME-001:" in item for item in at.session_state["e2e_workflow_results"])
    assert any("Sample Evidence (`get_company_evidence`):" in item for item in at.session_state["e2e_workflow_results"])
    assert any("Projected Org-AI-R Change:" in item for item in at.session_state["e2e_workflow_results"])
    assert any("Projected Base EBITDA Impact:" in item for item in at.session_state["e2e_workflow_results"])
    assert any("AI Value Creation Plan Summary for ACME-001" in item for item in at.session_state["e2e_workflow_results"])
