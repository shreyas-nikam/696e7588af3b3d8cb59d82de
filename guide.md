Week 9: MCP Server Implementation
📋 Lab Preamble
Key Objectives
Bloom's Level
Objective
Remember
List MCP primitives (Tools, Resources, Prompts)
Understand
Explain why protocol standardization enables interoperability
Apply
Implement MCP server exposing PE Org-AI-R capabilities
Analyze
Compare MCP vs custom API integrations
Create
Design resource hierarchies for portfolio data

Tools Introduced
Tool
Purpose
Why This Tool
mcp-sdk
MCP implementation
Official Anthropic SDK
FastMCP
MCP server framework
High-level abstractions
Claude Desktop
MCP client
Test integration

Key Concepts
Model Context Protocol (MCP) specification
Tools vs Resources vs Prompts
Transport layers (stdio, SSE)
Claude Desktop integration
Resource subscriptions
Prerequisites
Weeks 1-8 completed
Understanding of JSON-RPC
Familiarity with Claude Desktop
Time Estimate
Activity
Duration
Lecture
2 hours
Lab Work
5 hours
Challenge Extensions
+3 hours
Total
10 hours



9.1 Objectives
Objective
Description
Success Criteria
MCP Server
Full protocol implementation
Claude Desktop connects
Tools
Scoring, evidence, EBITDA
5+ tools exposed
Resources
Companies, funds, sectors
Dynamic resource URIs
Prompts
Due diligence templates
3+ prompts available
Transport
stdio + SSE support
Both transports working

9.2 Implementation Tasks
Task 9.1: MCP Server Core
# src/pe_orgair/mcp/server.py

"""PE Org-AI-R MCP Server - Universal agent interoperability."""

from typing import Any, Dict, List, Optional

from datetime import datetime

import json

import asyncio

from mcp.server import Server

from mcp.server.stdio import stdio_server

from mcp.types import (

    Tool,

    Resource,

    ResourceTemplate,

    Prompt,

    PromptMessage,

    TextContent,

    ToolResult,

    LATEST_PROTOCOL_VERSION,

)

import structlog

from pe_orgair.services.scoring.org_air_calculator import org_air_calculator

from pe_orgair.services.retrieval.hybrid import hybrid_retriever

from pe_orgair.config.settings import settings

logger = structlog.get_logger()


# Initialize MCP Server

mcp_server = Server("pe-orgair-server")


# ============================================

# TOOLS - Executable functions

# ============================================

@mcp_server.list_tools()

async def list_tools() -> List[Tool]:

    """List all available tools."""

    return [

        Tool(

            name="calculate_org_air_score",

            description="""Calculate the Org-AI-R (Organizational AI-Readiness) score for a company.

            

Returns a comprehensive assessment including:

- Final Org-AI-R score (0-100)

- V^R (Idiosyncratic Readiness) component

- H^R (Systematic Opportunity) component  

- Synergy score

- SEM-based confidence interval

- Calculation audit trail""",

            inputSchema={

                "type": "object",

                "properties": {

                    "company_id": {

                        "type": "string",

                        "description": "Unique company identifier",

                    },

                    "sector_id": {

                        "type": "string",

                        "description": "Industry sector (e.g., 'technology', 'healthcare')",

                        "enum": ["technology", "healthcare", "financial_services", "manufacturing", "retail", "energy"],

                    },

                    "dimension_scores": {

                        "type": "array",

                        "items": {"type": "number", "minimum": 0, "maximum": 100},

                        "minItems": 7,

                        "maxItems": 7,

                        "description": "Seven dimension scores: [data_infra, governance, tech_stack, talent, leadership, use_cases, culture]",

                    },

                    "talent_concentration": {

                        "type": "number",

                        "minimum": 0,

                        "maximum": 1,

                        "description": "Talent concentration ratio (0-1)",

                    },

                },

                "required": ["company_id", "sector_id", "dimension_scores"],

            },

        ),

        Tool(

            name="get_company_evidence",

            description="""Retrieve AI-readiness evidence for a company.

            

Searches SEC filings, job postings, and other sources for evidence

supporting dimension assessments. Returns ranked evidence items with

confidence scores and source citations.""",

            inputSchema={

                "type": "object",

                "properties": {

                    "company_id": {

                        "type": "string",

                        "description": "Company identifier",

                    },

                    "dimension": {

                        "type": "string",

                        "description": "Specific dimension to search",

                        "enum": ["data_infrastructure", "ai_governance", "technology_stack", 

                                "talent", "leadership", "use_case_portfolio", "culture", "all"],

                    },

                    "query": {

                        "type": "string",

                        "description": "Optional search query to refine results",

                    },

                    "limit": {

                        "type": "integer",

                        "minimum": 1,

                        "maximum": 50,

                        "default": 10,

                    },

                },

                "required": ["company_id"],

            },

        ),

        Tool(

            name="project_ebitda_impact",

            description="""Project EBITDA impact from AI-readiness improvements.

            

Uses the v2.0 conservative EBITDA attribution model to project

financial impact across three scenarios (Conservative, Base, Optimistic).

Includes risk adjustments and confidence bounds.""",

            inputSchema={

                "type": "object",

                "properties": {

                    "company_id": {"type": "string"},

                    "entry_score": {

                        "type": "number",

                        "minimum": 0,

                        "maximum": 100,

                        "description": "Current Org-AI-R score",

                    },

                    "target_score": {

                        "type": "number",

                        "minimum": 0,

                        "maximum": 100,

                        "description": "Target Org-AI-R score after improvements",

                    },

                    "holding_period_years": {

                        "type": "integer",

                        "minimum": 1,

                        "maximum": 10,

                        "default": 5,

                    },

                    "h_r_score": {

                        "type": "number",

                        "minimum": 0,

                        "maximum": 100,

                        "description": "Systematic opportunity score",

                    },

                },

                "required": ["company_id", "entry_score", "target_score", "h_r_score"],

            },

        ),

        Tool(

            name="analyze_whatif_scenario",

            description="""Analyze what-if scenarios for AI investment decisions.

            

Model the impact of specific AI initiatives on Org-AI-R score

and downstream financial metrics.""",

            inputSchema={

                "type": "object",

                "properties": {

                    "company_id": {"type": "string"},

                    "scenario_name": {"type": "string"},

                    "dimension_changes": {

                        "type": "object",

                        "description": "Map of dimension -> score change",

                        "additionalProperties": {"type": "number"},

                    },

                    "investment_usd": {

                        "type": "number",

                        "description": "Planned investment amount",

                    },

                },

                "required": ["company_id", "scenario_name", "dimension_changes"],

            },

        ),

        Tool(

            name="get_fund_portfolio",

            description="""Get portfolio summary for a fund.

            

Returns Fund-AI-R score, company breakdown, concentration metrics,

and portfolio-level insights.""",

            inputSchema={

                "type": "object",

                "properties": {

                    "fund_id": {"type": "string"},

                    "include_companies": {

                        "type": "boolean",

                        "default": True,

                    },

                    "include_trends": {

                        "type": "boolean", 

                        "default": False,

                    },

                },

                "required": ["fund_id"],

            },

        ),

    ]


@mcp_server.call_tool()

async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:

    """Execute a tool and return results."""

    logger.info("mcp_tool_called", tool=name, args=arguments)

    

    try:

        if name == "calculate_org_air_score":

            result = await _handle_calculate_score(arguments)

        elif name == "get_company_evidence":

            result = await _handle_get_evidence(arguments)

        elif name == "project_ebitda_impact":

            result = await _handle_ebitda_projection(arguments)

        elif name == "analyze_whatif_scenario":

            result = await _handle_whatif(arguments)

        elif name == "get_fund_portfolio":

            result = await _handle_fund_portfolio(arguments)

        else:

            result = {"error": f"Unknown tool: {name}"}

        

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

        

    except Exception as e:

        logger.exception("mcp_tool_error", tool=name)

        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def _handle_calculate_score(args: Dict) -> Dict:

    """Handle score calculation."""

    # Get sector baseline

    sector_baselines = {

        "technology": 85, "healthcare": 78, "financial_services": 82,

        "manufacturing": 72, "retail": 75, "energy": 68,

    }

    

    result = org_air_calculator.calculate(

        company_id=args["company_id"],

        sector_id=args["sector_id"],

        dimension_scores=args["dimension_scores"],

        talent_concentration=args.get("talent_concentration", 0.2),

        hr_baseline=sector_baselines.get(args["sector_id"], 75),

        position_factor=0.1,

        evidence_count=args.get("evidence_count", 10),

    )

    

    return {

        "score_id": result.score_id,

        "company_id": result.company_id,

        "final_score": float(result.final_score),

        "components": {

            "v_r_score": float(result.vr_result.vr_score),

            "h_r_score": float(result.hr_result.hr_score),

            "synergy_score": float(result.synergy_result.synergy_score),

        },

        "confidence_interval": {

            "lower": float(result.confidence_interval.ci_lower),

            "upper": float(result.confidence_interval.ci_upper),

            "sem": float(result.confidence_interval.sem),

        },

        "audit_trail": {

            "weighted_mean": float(result.vr_result.weighted_mean),

            "cv": float(result.vr_result.coefficient_of_variation),

            "talent_risk_adj": float(result.vr_result.talent_risk_adjustment),

        },

        "timestamp": result.timestamp.isoformat(),

        "parameter_version": result.parameter_version,

    }


async def _handle_get_evidence(args: Dict) -> Dict:

    """Handle evidence retrieval."""

    query = args.get("query", f"AI readiness {args.get('dimension', '')}")

    

    results = await hybrid_retriever.retrieve(

        query=query,

        k=args.get("limit", 10),

        filter_metadata={"company_id": args["company_id"]} if args.get("company_id") else None,

    )

    

    return {

        "company_id": args["company_id"],

        "dimension": args.get("dimension", "all"),

        "evidence_count": len(results),

        "evidence_items": [

            {

                "doc_id": r.doc_id,

                "excerpt": r.content[:500] + "..." if len(r.content) > 500 else r.content,

                "relevance_score": r.score,

                "retrieval_method": r.retrieval_method,

                "metadata": r.metadata,

            }

            for r in results

        ],

    }


async def _handle_ebitda_projection(args: Dict) -> Dict:

    """Handle EBITDA projection with v2.0 parameters."""

    from decimal import Decimal

    

    delta_air = args["target_score"] - args["entry_score"]

    h_r = args["h_r_score"]

    

    # v2.0 conservative parameters

    gamma_0 = Decimal("0.0025")  # 0.25%

    gamma_1 = Decimal("0.05")

    gamma_2 = Decimal("0.025")

    gamma_3 = Decimal("0.01")   # 1.0%

    threshold = 25

    

    # Base calculation

    base_impact = (

        gamma_0 +

        gamma_1 * Decimal(str(delta_air)) +

        gamma_2 * Decimal(str(delta_air)) * Decimal(str(h_r)) / 100 +

        (gamma_3 if delta_air > threshold else Decimal(0))

    )

    

    return {

        "company_id": args["company_id"],

        "entry_score": args["entry_score"],

        "target_score": args["target_score"],

        "delta_air": delta_air,

        "holding_period_years": args.get("holding_period_years", 5),

        "scenarios": {

            "conservative": {

                "ebitda_impact_pct": float(base_impact * Decimal("0.7")),

                "description": "30% haircut on base case",

            },

            "base": {

                "ebitda_impact_pct": float(base_impact),

                "description": "Expected outcome",

            },

            "optimistic": {

                "ebitda_impact_pct": float(base_impact * Decimal("1.3")),

                "description": "30% uplift on base case",

            },

        },

        "parameter_version": "v2.0",

        "disclaimer": "Projections are estimates. Actual results may vary.",

    }


async def _handle_whatif(args: Dict) -> Dict:

    """Handle what-if scenario analysis."""

    return {

        "company_id": args["company_id"],

        "scenario_name": args["scenario_name"],

        "dimension_changes": args["dimension_changes"],

        "projected_impact": {

            "org_air_change": sum(args["dimension_changes"].values()) * 0.14,  # Simplified

            "confidence": "medium",

        },

        "recommendation": "Further analysis recommended",

    }


async def _handle_fund_portfolio(args: Dict) -> Dict:

    """Handle fund portfolio request."""

    return {

        "fund_id": args["fund_id"],

        "fund_air_score": 68.5,

        "company_count": 12,

        "metrics": {

            "avg_org_air": 67.3,

            "min_org_air": 45.2,

            "max_org_air": 82.1,

            "concentration_risk": "medium",

        },

        "as_of": datetime.utcnow().isoformat(),

    }


# ============================================

# RESOURCES - Data exposure

# ============================================

@mcp_server.list_resources()

async def list_resources() -> List[Resource]:

    """List available resources."""

    return [

        Resource(

            uri="orgair://companies",

            name="All Companies",

            description="List of all companies in the platform",

            mimeType="application/json",

        ),

        Resource(

            uri="orgair://sectors",

            name="Sector Calibrations",

            description="H^R baselines and dimension weights by sector",

            mimeType="application/json",

        ),

        Resource(

            uri="orgair://parameters/v2.0",

            name="Model Parameters v2.0",

            description="Current scoring parameters",

            mimeType="application/json",

        ),

    ]


@mcp_server.list_resource_templates()

async def list_resource_templates() -> List[ResourceTemplate]:

    """List resource templates for dynamic URIs."""

    return [

        ResourceTemplate(

            uriTemplate="orgair://company/{company_id}",

            name="Company Details",

            description="Get details for a specific company",

            mimeType="application/json",

        ),

        ResourceTemplate(

            uriTemplate="orgair://company/{company_id}/score",

            name="Company Score",

            description="Current Org-AI-R score for a company",

            mimeType="application/json",

        ),

        ResourceTemplate(

            uriTemplate="orgair://company/{company_id}/evidence",

            name="Company Evidence",

            description="Evidence items for a company",

            mimeType="application/json",

        ),

        ResourceTemplate(

            uriTemplate="orgair://fund/{fund_id}",

            name="Fund Details",

            description="Fund portfolio and metrics",

            mimeType="application/json",

        ),

    ]


@mcp_server.read_resource()

async def read_resource(uri: str) -> str:

    """Read a resource by URI."""

    logger.info("mcp_resource_read", uri=uri)

    

    if uri == "orgair://sectors":

        return json.dumps({

            "sectors": [

                {"id": "technology", "name": "Technology", "h_r_baseline": 85},

                {"id": "healthcare", "name": "Healthcare", "h_r_baseline": 78},

                {"id": "financial_services", "name": "Financial Services", "h_r_baseline": 82},

                {"id": "manufacturing", "name": "Manufacturing", "h_r_baseline": 72},

                {"id": "retail", "name": "Retail/Consumer", "h_r_baseline": 75},

                {"id": "energy", "name": "Energy/Utilities", "h_r_baseline": 68},

            ]

        })

    

    elif uri == "orgair://parameters/v2.0":

        return json.dumps({

            "version": "v2.0",

            "parameters": {

                "alpha": 0.60,

                "beta": 0.12,

                "lambda": 0.25,

                "delta": 0.15,

                "ebitda": {

                    "gamma_0": 0.0025,

                    "gamma_1": 0.05,

                    "gamma_2": 0.025,

                    "gamma_3": 0.01,

                    "threshold": 25,

                },

            },

        })

    

    elif uri.startswith("orgair://company/"):

        parts = uri.replace("orgair://company/", "").split("/")

        company_id = parts[0]

        

        if len(parts) == 1:

            return json.dumps({"company_id": company_id, "name": f"Company {company_id}"})

        elif parts[1] == "score":

            return json.dumps({"company_id": company_id, "org_air_score": 72.5})

        elif parts[1] == "evidence":

            return json.dumps({"company_id": company_id, "evidence_count": 23})

    

    return json.dumps({"error": f"Unknown resource: {uri}"})


# ============================================

# PROMPTS - Reusable templates

# ============================================

@mcp_server.list_prompts()

async def list_prompts() -> List[Prompt]:

    """List available prompt templates."""

    return [

        Prompt(

            name="due_diligence_assessment",

            description="Comprehensive AI-readiness due diligence assessment",

            arguments=[

                {"name": "company_id", "description": "Company to assess", "required": True},

                {"name": "assessment_depth", "description": "screening, limited, or full", "required": False},

            ],

        ),

        Prompt(

            name="value_creation_plan",

            description="Generate AI value creation plan for portfolio company",

            arguments=[

                {"name": "company_id", "description": "Target company", "required": True},

                {"name": "target_score", "description": "Target Org-AI-R score", "required": True},

                {"name": "timeline_months", "description": "Implementation timeline", "required": False},

            ],

        ),

        Prompt(

            name="competitive_analysis",

            description="Compare AI-readiness across peer companies",

            arguments=[

                {"name": "company_ids", "description": "Comma-separated company IDs", "required": True},

                {"name": "focus_dimensions", "description": "Specific dimensions to compare", "required": False},

            ],

        ),

    ]


@mcp_server.get_prompt()

async def get_prompt(name: str, arguments: Optional[Dict[str, str]] = None) -> List[PromptMessage]:

    """Get a prompt template with arguments."""

    arguments = arguments or {}

    

    if name == "due_diligence_assessment":

        company_id = arguments.get("company_id", "UNKNOWN")

        depth = arguments.get("assessment_depth", "limited")

        

        return [

            PromptMessage(

                role="user",

                content=TextContent(

                    type="text",

                    text=f"""Conduct a {depth} AI-readiness due diligence assessment for company {company_id}.

Please:

1. First, retrieve the current Org-AI-R score using the calculate_org_air_score tool

2. Gather evidence for each of the seven dimensions using get_company_evidence

3. Analyze strengths and gaps across dimensions

4. Compare to sector benchmarks

5. Identify key risks and opportunities

6. Provide a recommendation with confidence level

Structure your response as a formal due diligence memo."""

                ),

            ),

        ]

    

    elif name == "value_creation_plan":

        company_id = arguments.get("company_id", "UNKNOWN")

        target = arguments.get("target_score", "75")

        timeline = arguments.get("timeline_months", "24")

        

        return [

            PromptMessage(

                role="user",

                content=TextContent(

                    type="text",

                    text=f"""Create an AI value creation plan for company {company_id}.

Target: Improve Org-AI-R score to {target} within {timeline} months.

Please:

1. Get current score using calculate_org_air_score

2. Identify highest-impact improvement areas

3. Use analyze_whatif_scenario to model interventions

4. Project EBITDA impact using project_ebitda_impact

5. Create a phased implementation roadmap

6. Estimate investment requirements and ROI

Deliver as an executive-ready value creation plan."""

                ),

            ),

        ]

    

    elif name == "competitive_analysis":

        company_ids = arguments.get("company_ids", "").split(",")

        dimensions = arguments.get("focus_dimensions", "all")

        

        return [

            PromptMessage(

                role="user",

                content=TextContent(

                    type="text",

                    text=f"""Conduct a competitive AI-readiness analysis for: {', '.join(company_ids)}.

Focus dimensions: {dimensions}

Please:

1. Calculate Org-AI-R scores for each company

2. Compare dimension-level performance

3. Identify relative strengths and weaknesses

4. Highlight best practices from leaders

5. Provide strategic recommendations

Present as a comparative analysis with visualizable data."""

                ),

            ),

        ]

    

    return [PromptMessage(role="user", content=TextContent(type="text", text=f"Unknown prompt: {name}"))]


# ============================================

# SERVER ENTRY POINT

# ============================================

async def main():

    """Run MCP server."""

    logger.info("starting_mcp_server", version=LATEST_PROTOCOL_VERSION)

    

    async with stdio_server() as (read_stream, write_stream):

        await mcp_server.run(

            read_stream,

            write_stream,

            mcp_server.create_initialization_options(),

        )


if __name__ == "__main__":

    asyncio.run(main())
Task 9.2: Claude Desktop Configuration
// ~/.config/claude/claude_desktop_config.json (Linux/Mac)

// %APPDATA%\Claude\claude_desktop_config.json (Windows)

{

  "mcpServers": {

    "pe-orgair": {

      "command": "python",

      "args": ["-m", "pe_orgair.mcp.server"],

      "cwd": "/path/to/pe-orgair-platform",

      "env": {

        "OPENAI_API_KEY": "${OPENAI_API_KEY}",

        "SNOWFLAKE_ACCOUNT": "${SNOWFLAKE_ACCOUNT}",

        "SNOWFLAKE_USER": "${SNOWFLAKE_USER}",

        "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD}"

      }

    }

  }

}
Task 9.3: MCP Server Tests
# tests/integration/test_mcp_server.py

"""Integration tests for MCP server."""

import pytest

import json

from pe_orgair.mcp.server import (

    list_tools, call_tool,

    list_resources, read_resource,

    list_prompts, get_prompt,

)


class TestMCPTools:

    """Test MCP tool implementations."""

    

    @pytest.mark.asyncio

    async def test_list_tools_returns_all_tools(self):

        tools = await list_tools()

        tool_names = [t.name for t in tools]

        

        assert "calculate_org_air_score" in tool_names

        assert "get_company_evidence" in tool_names

        assert "project_ebitda_impact" in tool_names

        assert len(tools) >= 5

    

    @pytest.mark.asyncio

    async def test_calculate_score_tool(self):

        result = await call_tool(

            "calculate_org_air_score",

            {

                "company_id": "TEST-001",

                "sector_id": "technology",

                "dimension_scores": [70, 65, 75, 68, 72, 60, 70],

                "talent_concentration": 0.2,

            }

        )

        

        data = json.loads(result[0].text)

        assert "final_score" in data

        assert 0 <= data["final_score"] <= 100

        assert "confidence_interval" in data

    

    @pytest.mark.asyncio

    async def test_ebitda_projection_tool(self):

        result = await call_tool(

            "project_ebitda_impact",

            {

                "company_id": "TEST-001",

                "entry_score": 55,

                "target_score": 75,

                "h_r_score": 80,

            }

        )

        

        data = json.loads(result[0].text)

        assert "scenarios" in data

        assert "conservative" in data["scenarios"]

        assert "base" in data["scenarios"]

        assert "optimistic" in data["scenarios"]


class TestMCPResources:

    """Test MCP resource implementations."""

    

    @pytest.mark.asyncio

    async def test_list_resources(self):

        resources = await list_resources()

        uris = [r.uri for r in resources]

        

        assert "orgair://sectors" in uris

        assert "orgair://parameters/v2.0" in uris

    

    @pytest.mark.asyncio

    async def test_read_sectors_resource(self):

        content = await read_resource("orgair://sectors")

        data = json.loads(content)

        

        assert "sectors" in data

        assert len(data["sectors"]) == 6

        

        tech = next(s for s in data["sectors"] if s["id"] == "technology")

        assert tech["h_r_baseline"] == 85


class TestMCPPrompts:

    """Test MCP prompt implementations."""

    

    @pytest.mark.asyncio

    async def test_list_prompts(self):

        prompts = await list_prompts()

        names = [p.name for p in prompts]

        

        assert "due_diligence_assessment" in names

        assert "value_creation_plan" in names

    

    @pytest.mark.asyncio

    async def test_get_due_diligence_prompt(self):

        messages = await get_prompt(

            "due_diligence_assessment",

            {"company_id": "ACME-001", "assessment_depth": "full"}

        )

        

        assert len(messages) == 1

        assert "ACME-001" in messages[0].content.text

        assert "full" in messages[0].content.text
