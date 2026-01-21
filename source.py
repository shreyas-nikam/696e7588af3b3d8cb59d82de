# import asyncio
# import json
# import uuid
# from datetime import datetime
# from decimal import Decimal
# from typing import Any, Dict, List, Optional

# import nest_asyncio
# from mcp.server import Server
# from mcp.types import (
#     LATEST_PROTOCOL_VERSION,
#     Prompt,
#     PromptMessage,
#     Resource,
#     ResourceTemplate,
#     TextContent,
#     Tool,
# )
# import structlog
# import asyncio
# import json
# import uuid
# from datetime import datetime, timezone
# from decimal import Decimal
# from typing import Any, Dict, List, Optional

# import nest_asyncio
# from mcp.server import Server
# from mcp.types import (
#     LATEST_PROTOCOL_VERSION,
#     Prompt,
#     PromptMessage,
#     Resource,
#     ResourceTemplate,
#     TextContent,
#     Tool,
# )
# import structlog

# nest_asyncio.apply()
# logger = structlog.get_logger()
# mcp_server = Server("pe-orgair-server")

# # Mock Services Definitions (as defined in previous cells and needed for tool handlers)

# class MockOrgAIRCalculator:
#     def calculate(
#         self,
#         company_id: str,
#         sector_id: str,
#         dimension_scores: List[float],
#         talent_concentration: float,
#         hr_baseline: float,
#         position_factor: float,
#         evidence_count: int,
#     ) -> Dict[str, Any]:

#         avg_dimension_score = sum(dimension_scores) / len(dimension_scores) if dimension_scores else 0.0
#         vr_score = avg_dimension_score * (1 - talent_concentration / 2)
#         hr_score = hr_baseline * (1 + position_factor)
#         synergy_score = (vr_score * hr_score) / 100 * 0.5
#         final_score = (vr_score + hr_score + synergy_score) / 2.5
#         final_score = min(100.0, max(0.0, final_score))
#         ci_lower = max(0.0, final_score - (5 + (1-talent_concentration)*5))
#         ci_upper = min(100.0, final_score + (5 + talent_concentration*5))
#         sem = (ci_upper - ci_lower) / 3.92

#         return {
#             "score_id": str(uuid.uuid4()),
#             "company_id": company_id,
#             "final_score": float(final_score),
#             "components": {
#                 "v_r_score": float(vr_score),
#                 "h_r_score": float(hr_score),
#                 "synergy_score": float(synergy_score),
#             },
#             "confidence_interval": {
#                 "lower": float(ci_lower),
#                 "upper": float(ci_upper),
#                 "sem": float(sem),
#             },
#             "audit_trail": {
#                 "weighted_mean": float(avg_dimension_score),
#                 "cv": float(talent_concentration * 10),
#                 "talent_risk_adj": float(talent_concentration * 15),
#             },
#             "timestamp": datetime.now(timezone.utc), # Use timezone.utc for consistency
#             "parameter_version": "v2.0",
#         }

# class MockHybridRetriever:
#     async def retrieve(self, query: str, k: int, filter_metadata: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
#         mock_evidence_pool = [
#             {"doc_id": "doc_1", "content": "Company X has invested heavily in cloud infrastructure, with specific mention of AWS Lambda and Azure Functions for scalable AI model deployment. Their data lake utilizes Snowflake.", "score": 0.95, "retrieval_method": "semantic", "metadata": {"company_id": "ACME-001", "dimension": "data_infrastructure", "source": "Q3 2023 Earnings Call Transcript"}},
#             {"doc_id": "doc_2", "content": "Recent job postings for 'AI Governance Lead' and 'Ethical AI Specialist' indicate a strong focus on responsible AI practices. They've also published an internal AI ethics guideline.", "score": 0.92, "retrieval_method": "keyword", "metadata": {"company_id": "ACME-001", "dimension": "ai_governance", "source": "Company Careers Page"}},
#             {"doc_id": "doc_3", "content": "Competitor Y recently launched an AI-powered customer service bot, reducing call center volume by 30%. Their technology stack appears to be largely open-source, including TensorFlow and PyTorch.", "score": 0.88, "retrieval_method": "semantic", "metadata": {"company_id": "GLOBAL-INC", "dimension": "tech_stack", "source": "Industry Report 2024"}},
#             {"doc_id": "doc_4", "content": "Internal HR data shows a 15% increase in AI/ML certifications among the engineering team over the last year. They run an internal AI academy.", "score": 0.91, "retrieval_method": "semantic", "metadata": {"company_id": "ACME-001", "dimension": "talent", "source": "Internal HR Report"}},
#             {"doc_id": "doc_5", "content": "The CEO's recent keynote emphasized 'AI-first' strategy and substantial investment in R&D, forming a dedicated AI steering committee.", "score": 0.93, "retrieval_method": "semantic", "metadata": {"company_id": "ACME-001", "dimension": "leadership", "source": "CEO Keynote Transcript"}},
#             {"doc_id": "doc_6", "content": "They are actively piloting AI solutions for predictive maintenance and supply chain optimization, with early success reported in cost reduction.", "score": 0.90, "retrieval_method": "keyword", "metadata": {"company_id": "ACME-001", "dimension": "use_case_portfolio", "source": "Pilot Project Update"}},
#             {"doc_id": "doc_7", "content": "An internal survey indicates high employee engagement with AI initiatives and a strong willingness to adapt to new AI tools.", "score": 0.89, "retrieval_method": "semantic", "metadata": {"company_id": "ACME-001", "dimension": "culture", "source": "Employee Engagement Survey"}},
#         ]

#         filtered_results = []
#         company_id_filter = filter_metadata.get("company_id") if filter_metadata else None

#         for item in mock_evidence_pool:
#             if company_id_filter and item["metadata"]["company_id"] != company_id_filter:
#                 continue
#             query_lower = query.lower()
#             dimension_lower = item["metadata"]["dimension"].lower()

#             # Simplified matching for testing: check if query is general, matches dimension exactly, or contains dimension
#             if "ai readiness" in query_lower or "evidence" in query_lower or query_lower == dimension_lower:
#                  filtered_results.append(item)
#             elif dimension_lower in query_lower:
#                 filtered_results.append(item)

#         return sorted(filtered_results, key=lambda x: x['score'], reverse=True)[:k]


# org_air_calculator = MockOrgAIRCalculator()
# hybrid_retriever = MockHybridRetriever()

# # --- Tool Definitions ---

# # Sector baselines for H^R, as per OCR input
# sector_baselines = {
#     "technology": 85,
#     "healthcare": 78,
#     "financial_services": 82,
#     "manufacturing": 72,
#     "retail": 75,
#     "energy": 68,
# }

# # _handle_ functions (implementing tool logic)

# async def _handle_calculate_score(args: Dict) -> Dict:
#     """Handle score calculation."""
#     company_id = args["company_id"]
#     sector_id = args["sector_id"]
#     dimension_scores = args["dimension_scores"]
#     talent_concentration = args.get("talent_concentration", 0.2)

#     # Get HR baseline from our hardcoded sector_baselines
#     hr_baseline = sector_baselines.get(sector_id, 75)  # Default to 75 if sector not found

#     # Mock parameters for the calculator
#     position_factor = 0.1
#     evidence_count = args.get("evidence_count", 10)

#     result = org_air_calculator.calculate(
#         company_id=company_id,
#         sector_id=sector_id,
#         dimension_scores=dimension_scores,
#         talent_concentration=talent_concentration,
#         hr_baseline=hr_baseline,
#         position_factor=position_factor,
#         evidence_count=evidence_count,
#     )

#     # Format the timestamp for JSON serialization
#     result["timestamp"] = result["timestamp"].isoformat()

#     return {
#         "score_id": result["score_id"],
#         "company_id": result["company_id"],
#         "final_score": float(result["final_score"]),
#         "components": {
#             "v_r_score": float(result["components"]["v_r_score"]),
#             "h_r_score": float(result["components"]["h_r_score"]),
#             "synergy_score": float(result["components"]["synergy_score"]),
#         },
#         "confidence_interval": {
#             "lower": float(result["confidence_interval"]["lower"]),
#             "upper": float(result["confidence_interval"]["upper"]),
#             "sem": float(result["confidence_interval"]["sem"]),
#         },
#         "audit_trail": {
#             "weighted_mean": float(result["audit_trail"]["weighted_mean"]),
#             "cv": float(result["audit_trail"]["cv"]),
#             "talent_risk_adj": float(result["audit_trail"]["talent_risk_adj"]),
#         },
#         "timestamp": result["timestamp"],
#         "parameter_version": result["parameter_version"],
#     }


# async def _handle_get_evidence(args: Dict) -> Dict:
#     """Handle evidence retrieval."""
#     company_id = args["company_id"]
#     dimension = args.get("dimension", "all")
#     query = args.get("query", f"AI readiness {dimension}")
#     limit = args.get("limit", 10)

#     results = await hybrid_retriever.retrieve(
#         query=query,
#         k=limit,
#         filter_metadata={"company_id": company_id} if company_id else None,
#     )

#     # Truncate content for brevity in output
#     for r in results:
#         r['content'] = r['content'][:500] + "..." if len(r['content']) > 500 else r['content']

#     return {
#         "company_id": company_id,
#         "dimension": dimension,
#         "evidence_count": len(results),
#         "evidence_items": results,
#     }


# async def _handle_ebitda_projection(args: Dict) -> Dict:
#     """Handle EBITDA projection with v2.0 parameters."""
#     from decimal import Decimal

#     company_id = args["company_id"]
#     entry_score = Decimal(str(args["entry_score"]))
#     target_score = Decimal(str(args["target_score"]))
#     h_r_score = Decimal(str(args["h_r_score"]))
#     holding_period_years = Decimal(str(args.get("holding_period_years", 5)))

#     delta_air = target_score - entry_score

#     # v2.0 conservative parameters (as per OCR)
#     gamma_0 = Decimal("0.0025")  # 0.25%
#     gamma_1 = Decimal("0.05")
#     gamma_2 = Decimal("0.025")
#     gamma_3 = Decimal("0.01")    # 1.0%
#     threshold = Decimal("25")    # Delta_AIR threshold for gamma_3 activation

#     # Base calculation formula
#     # This formula represents a simplified attribution model where EBITDA impact is a
#     # function of the change in Org-AI-R score (delta_air) and systematic opportunity (h_r_score).
#     # The gamma parameters are coefficients that weigh these factors.
#     # $ base_impact = \gamma_0 + \gamma_1 \cdot \Delta_{{AIR}} + \gamma_2 \cdot \Delta_{{AIR}} \cdot \frac{{H_R}}{{100}} + (\gamma_3 \text{{ if }} \Delta_{{AIR}} > \text{{threshold else }} 0) $
#     base_impact = (
#         gamma_0 +
#         gamma_1 * delta_air +
#         gamma_2 * delta_air * h_r_score / Decimal("100") +
#         (gamma_3 if delta_air > threshold else Decimal("0"))
#     )

#     return {
#         "company_id": company_id,
#         "entry_score": float(entry_score),
#         "target_score": float(target_score),
#         "delta_air": float(delta_air),
#         "holding_period_years": float(holding_period_years),
#         "scenarios": {
#             "conservative": {
#                 "ebitda_impact_pct": float(base_impact * Decimal("0.7")),  # 30% haircut
#                 "description": "30% haircut on base case, accounting for higher risk",
#             },
#             "base": {
#                 "ebitda_impact_pct": float(base_impact),
#                 "description": "Expected outcome based on v2.0 parameters",
#             },
#             "optimistic": {
#                 "ebitda_impact_pct": float(base_impact * Decimal("1.3")),  # 30% uplift
#                 "description": "30% uplift on base case, assuming optimal conditions",
#             },
#         },
#         "parameter_version": "v2.0",
#         "disclaimer": "Projections are estimates. Actual results may vary.",
#     }


# async def _handle_whatif(args: Dict) -> Dict:
#     """Handle what-if scenario analysis."""
#     company_id = args["company_id"]
#     scenario_name = args["scenario_name"]
#     dimension_changes = args["dimension_changes"]
#     investment_usd = args.get("investment_usd", 0)  # Optional investment amount

#     # Simplified logic for Org-AI-R change based on sum of dimension changes
#     org_air_change = sum(dimension_changes.values()) * 0.14  # As per OCR

#     # Simplified projected financial impact
#     # $ projected_impact = org_air_change \times \text{{investment_usd}} \times 0.05 $
#     projected_impact = org_air_change * investment_usd * 0.05

#     # A simple linear relationship for demo
#     return {
#         "company_id": company_id,
#         "scenario_name": scenario_name,
#         "dimension_changes": dimension_changes,
#         "org_air_change": float(org_air_change),
#         "projected_impact_usd": float(projected_impact),
#         "confidence": "medium",
#         "recommendation": "Further analysis recommended to validate projected impact and associated risks.",
#     }


# async def _handle_fund_portfolio(args: Dict) -> Dict:
#     """Handle fund portfolio request."""
#     fund_id = args["fund_id"]
#     # Mock data for fund portfolio, as per OCR
#     return {
#         "fund_id": fund_id,
#         "fund_air_score": 68.5,
#         "company_count": 12,
#         "metrics": {
#             "avg_org_air": 67.3,
#             "min_org_air": 45.2,
#             "max_org_air": 82.1,
#             "concentration_risk": "medium",
#         },
#         "as_of": datetime.now(timezone.utc).isoformat(),
#     }


# # Register all tools with the MCP server
# @mcp_server.list_tools()
# async def list_tools() -> List[Tool]:
#     """List all available tools."""
#     return [
#         Tool(
#             name="calculate_org_air_score",
#             description="""Calculate the Org-AI-R (Organizational AI-Readiness) score for a company.\nReturns a comprehensive assessment including:\n- Final Org-AI-R score (0-100)\n- V^R (Idiosyncratic Readiness) component\n- H^R (Systematic Opportunity) component\n- Synergy score\n- SEM-based confidence interval\n- Calculation audit trail""",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "company_id": {"type": "string", "description": "Unique company identifier"},
#                     "sector_id": {
#                         "type": "string",
#                         "description": "Industry sector (e.g., 'technology', 'healthcare')",
#                         "enum": ["technology", "healthcare", "financial_services", "manufacturing", "retail", "energy"],
#                     },
#                     "dimension_scores": {
#                         "type": "array",
#                         "items": {"type": "number", "minimum": 0, "maximum": 100},
#                         "minItems": 7,
#                         "maxItems": 7,
#                         "description": "Seven dimension scores: [data_infra, governance, tech_stack, talent, leadership, use_cases, culture]",
#                     },
#                     "talent_concentration": {
#                         "type": "number",
#                         "minimum": 0,
#                         "maximum": 1,
#                         "description": "Talent concentration ratio (0-1)",
#                     },
#                 },
#                 "required": ["company_id", "sector_id", "dimension_scores"],
#             },
#         ),
#         Tool(
#             name="get_company_evidence",
#             description="""Retrieve AI-readiness evidence for a company.\nSearches SEC filings, job postings, and other sources for evidence\nsupporting dimension assessments. Returns ranked evidence items with\nconfidence scores and source citations.""",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "company_id": {"type": "string", "description": "Company identifier"},
#                     "dimension": {
#                         "type": "string",
#                         "description": "Specific dimension to search (e.g., 'data_infrastructure')",
#                         "enum": ["data_infrastructure", "ai_governance", "technology_stack", "talent", "leadership", "use_case_portfolio", "culture", "all"],
#                     },
#                     "query": {"type": "string", "description": "Optional search query to refine results"},
#                     "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 10},
#                 },
#                 "required": ["company_id"],
#             },
#         ),
#         Tool(
#             name="project_ebitda_impact",
#             description="""Project EBITDA impact from AI-readiness improvements.\nUses the v2.0 conservative EBITDA attribution model to project\nfinancial impact across three scenarios (Conservative, Base, Optimistic).\nIncludes risk adjustments and confidence bounds.""",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "company_id": {"type": "string", "description": "Unique company identifier"},
#                     "entry_score": {"type": "number", "minimum": 0, "maximum": 100, "description": "Current Org-AI-R score"},
#                     "target_score": {"type": "number", "minimum": 0, "maximum": 100, "description": "Target Org-AI-R score after improvements"},
#                     "holding_period_years": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5, "description": "Number of years in the holding period for projection"},
#                     "h_r_score": {"type": "number", "minimum": 0, "maximum": 100, "description": "Systematic opportunity score (H^R component)"},
#                 },
#                 "required": ["company_id", "entry_score", "target_score", "h_r_score"],
#             },
#         ),
#         Tool(
#             name="analyze_whatif_scenario",
#             description="""Analyze what-if scenarios for AI investment decisions.\nModel the impact of specific AI initiatives on Org-AI-R score\nand downstream financial metrics.""",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "company_id": {"type": "string", "description": "Unique company identifier"},
#                     "scenario_name": {"type": "string", "description": "Name for the what-if scenario"},
#                     "dimension_changes": {
#                         "type": "object",
#                         "description": "Map of dimension name to expected score change (e.g., {'data_infra': 5, 'talent': 10})",
#                         "additionalProperties": {"type": "number"},
#                     },
#                     "investment_usd": {"type": "number", "minimum": 0, "description": "Planned investment amount in USD"},
#                 },
#                 "required": ["company_id", "scenario_name", "dimension_changes"],
#             },
#         ),
#         Tool(
#             name="get_fund_portfolio",
#             description="""Get portfolio summary for a fund.\nReturns Fund-AI-R score, company breakdown, concentration metrics,\nand portfolio-level insights.""",
#             inputSchema={
#                 "type": "object",
#                 "properties": {
#                     "fund_id": {"type": "string", "description": "Unique fund identifier"},
#                     "include_companies": {"type": "boolean", "default": True, "description": "Include detailed company list in the output"},
#                     "include_trends": {"type": "boolean", "default": False, "description": "Include historical trends in the output"},
#                 },
#                 "required": ["fund_id"],
#             },
#         ),
#     ]


# # The call_tool handler orchestrates execution of registered tools.
# @mcp_server.call_tool()
# async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
#     """Execute a tool and return results."""
#     logger.info("mcp_tool_called", tool=name, args=arguments)
#     try:
#         result = {}
#         if name == "calculate_org_air_score":
#             result = await _handle_calculate_score(arguments)
#         elif name == "get_company_evidence":
#             result = await _handle_get_evidence(arguments)
#         elif name == "project_ebitda_impact":
#             result = await _handle_ebitda_projection(arguments)
#         elif name == "analyze_whatif_scenario":
#             result = await _handle_whatif(arguments)
#         elif name == "get_fund_portfolio":
#             result = await _handle_fund_portfolio(arguments)
#         else:
#             result = {"error": f"Unknown tool: {name}"}

#         return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

#     except Exception as e:
#         logger.exception("mcp_tool_error", tool=name)
#         return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


# print("All tools defined and registered.")

# # --- Test Tool Invocations ---

# print("\n--- Testing calculate_org_air_score ---")
# calculate_score_args = {
#     "company_id": "ACME-001",
#     "sector_id": "technology",
#     "dimension_scores": [70, 65, 75, 68, 72, 60, 70],
#     "talent_concentration": 0.2,
# }
# score_result = await call_tool("calculate_org_air_score", calculate_score_args)
# print(score_result[0].text)

# print("\n--- Testing get_company_evidence ---")
# evidence_args = {
#     "company_id": "ACME-001",
#     "dimension": "data_infrastructure",
#     "limit": 2,
# }
# evidence_result = await call_tool("get_company_evidence", evidence_args)
# print(evidence_result[0].text)

# print("\n--- Testing project_ebitda_impact ---")
# ebitda_args = {
#     "company_id": "ACME-001",
#     "entry_score": 55,
#     "target_score": 75,
#     "h_r_score": 80,
#     "holding_period_years": 5,
# }
# ebitda_result = await call_tool("project_ebitda_impact", ebitda_args)
# print(ebitda_result[0].text)

# print("\n--- Testing analyze_whatif_scenario ---")
# whatif_args = {
#     "company_id": "ACME-001",
#     "scenario_name": "CloudMigration_AI_StackUpgrade",
#     "dimension_changes": {"data_infrastructure": 10, "tech_stack": 8},
#     "investment_usd": 1500000,
# }
# whatif_result = await call_tool("analyze_whatif_scenario", whatif_args)
# print(whatif_result[0].text)

# print("\n--- Testing get_fund_portfolio ---")
# fund_args = {
#     "fund_id": "PE-FUND-001",
#     "include_companies": False,  # Set to False for brevity in demo output
# }
# fund_result = await call_tool("get_fund_portfolio", fund_args)
# print(fund_result[0].text)

# # --- Resource Definitions ---


# @mcp_server.list_resources()
# async def list_resources() -> List[Resource]:
#     """List available static resources."""
#     return [
#         Resource(
#             uri="orgair://companies",
#             name="All Companies",
#             description="List of all companies in the platform",
#             mimeType="application/json",
#         ),
#         Resource(
#             uri="orgair://sectors",
#             name="Sector Calibrations",
#             description="H^R baselines and dimension weights by sector",
#             mimeType="application/json",
#         ),
#         Resource(
#             uri="orgair://parameters/v2.0",
#             name="Model Parameters v2.0",
#             description="Current scoring and projection model parameters",
#             mimeType="application/json",
#         ),
#     ]


# @mcp_server.list_resource_templates()
# async def list_resource_templates() -> List[ResourceTemplate]:
#     """List resource templates for dynamic URIs."""
#     return [
#         ResourceTemplate(
#             uriTemplate="orgair://company/{{company_id}}",
#             name="Company Details",
#             description="Get details for a specific company",
#             mimeType="application/json",
#         ),
#         ResourceTemplate(
#             uriTemplate="orgair://company/{{company_id}}/score",
#             name="Company Score",
#             description="Current Org-AI-R score for a company",
#             mimeType="application/json",
#         ),
#         ResourceTemplate(
#             uriTemplate="orgair://company/{{company_id}}/evidence",
#             name="Company Evidence",
#             description="Evidence items for a company's AI-readiness dimensions",
#             mimeType="application/json",
#         ),
#         ResourceTemplate(
#             uriTemplate="orgair://fund/{{fund_id}}",
#             name="Fund Details",
#             description="Fund portfolio and metrics summary",
#             mimeType="application/json",
#         ),
#     ]


# @mcp_server.read_resource()
# async def read_resource(uri: str) -> str:
#     """Read a resource by URI."""
#     logger.info("mcp_resource_read", uri=uri)

#     if uri == "orgair://companies":
#         # Mock company list
#         return json.dumps(
#             {
#                 "companies": [
#                     {"id": "ACME-001", "name": "ACME Corp", "sector": "technology"},
#                     {
#                         "id": "GLOBAL-INC",
#                         "name": "Global Innovations Inc.",
#                         "sector": "manufacturing",
#                     },
#                     {
#                         "id": "HEALTH-SYS",
#                         "name": "Health Systems LLC",
#                         "sector": "healthcare",
#                     },
#                 ]
#             },
#             indent=2,
#         )

#     elif uri == "orgair://sectors":
#         # Sector baselines (same as used in calculate_org_air_score)
#         return json.dumps(
#             {
#                 "sectors": [
#                     {"id": "technology", "name": "Technology", "h_r_baseline": 85},
#                     {"id": "healthcare", "name": "Healthcare", "h_r_baseline": 78},
#                     {
#                         "id": "financial_services",
#                         "name": "Financial Services",
#                         "h_r_baseline": 82,
#                     },
#                     {
#                         "id": "manufacturing",
#                         "name": "Manufacturing",
#                         "h_r_baseline": 72,
#                     },
#                     {
#                         "id": "retail",
#                         "name": "Retail/Consumer",
#                         "h_r_baseline": 75,
#                     },
#                     {
#                         "id": "energy",
#                         "name": "Energy/Utilities",
#                         "h_r_baseline": 68,
#                     },
#                 ]
#             },
#             indent=2,
#         )

#     elif uri == "orgair://parameters/v2.0":
#         # Model parameters for EBITDA (same as used in project_ebitda_impact)
#         return json.dumps(
#             {
#                 "version": "v2.0",
#                 "parameters": {
#                     "alpha": 0.60,
#                     "beta": 0.12,
#                     "lambda": 0.25,
#                     "delta": 0.15,
#                     "ebitda": {
#                         "gamma_0": 0.0025,
#                         "gamma_1": 0.05,
#                         "gamma_2": 0.025,
#                         "gamma_3": 0.01,
#                         "threshold": 25,
#                     },
#                 },
#             },
#             indent=2,
#         )

#     elif uri.startswith("orgair://company/"):
#         parts = uri.replace("orgair://company/", "").split("/")
#         company_id = parts[0]

#         if len(parts) == 1:
#             # orgair://company/{{company_id}}
#             return json.dumps(
#                 {
#                     "company_id": company_id,
#                     "name": f"Company {company_id} (Details Mock)",
#                     "sector": "technology",
#                 },
#                 indent=2,
#             )
#         elif parts[1] == "score":
#             # orgair://company/{{company_id}}/score
#             # Return a mock score, could be retrieved from a database in a real scenario
#             return json.dumps(
#                 {
#                     "company_id": company_id,
#                     "org_air_score": 72.5,
#                     "as_of": datetime.utcnow().isoformat(),
#                 },
#                 indent=2,
#             )
#         elif parts[1] == "evidence":
#             # orgair://company/{{company_id}}/evidence
#             # Return mock evidence count
#             return json.dumps(
#                 {
#                     "company_id": company_id,
#                     "evidence_count": 23,
#                     "sample_evidence": ["doc_1", "doc_4"],
#                 },
#                 indent=2,
#             )

#     elif uri.startswith("orgair://fund/"):
#         parts = uri.replace("orgair://fund/", "").split("/")
#         fund_id = parts[0]

#         if len(parts) == 1:
#             # orgair://fund/{{fund_id}}
#             # Return mock fund details
#             return json.dumps(
#                 {
#                     "fund_id": fund_id,
#                     "fund_name": f"Capital Partners {fund_id}",
#                     "fund_air_score": 68.5,
#                     "company_count": 12,
#                 },
#                 indent=2,
#             )

#     return json.dumps({"error": f"Unknown resource: {uri}"}, indent=2)


# print("All resources defined and registered.")

# # --- Test Resource Invocations ---

# print("\n--- Testing list_resources ---")
# static_resources = await list_resources()
# for res in static_resources:
#     print(f"- {res.uri}: {res.description}")

# print("\n--- Testing list_resource_templates ---")
# resource_templates = await list_resource_templates()
# for tmpl in resource_templates:
#     print(f"- {tmpl.uriTemplate}: {tmpl.description}")

# print("\n--- Testing read_resource (Static: sectors) ---")
# sectors_content = await read_resource("orgair://sectors")
# print(sectors_content)

# print("\n--- Testing read_resource (Static: model parameters) ---")
# params_content = await read_resource("orgair://parameters/v2.0")
# print(params_content)

# print("\n--- Testing read_resource (Dynamic: company details) ---")
# company_details_content = await read_resource("orgair://company/ACME-001")
# print(company_details_content)

# print("\n--- Testing read_resource (Dynamic: company score) ---")
# company_score_content = await read_resource("orgair://company/ACME-001/score")
# print(company_score_content)

# print("\n--- Testing read_resource (Dynamic: fund details) ---")
# fund_details_content = await read_resource("orgair://fund/PE-FUND-001")
# print(fund_details_content)
# # --- Prompt Definitions ---
# # Explicitly re-import Server to ensure we get the correct class
# from mcp.server import Server
# from mcp.types import (
#     Prompt,
#     PromptMessage,
#     TextContent, # Ensure TextContent is also imported as it's used in PromptMessage
# )
# import structlog

# # Re-initialize logger and mcp_server to ensure correct type and state
# logger = structlog.get_logger()
# mcp_server = Server("pe-orgair-server")


# @mcp_server.list_prompts()
# async def list_prompts() -> List[Prompt]:
#     """List available prompt templates."""
#     return [
#         Prompt(
#             name="due_diligence_assessment",
#             description="Comprehensive AI-readiness due diligence assessment for a company.",
#             arguments=[
#                 {
#                     "name": "company_id",
#                     "description": "Company to assess",
#                     "required": True,
#                 },
#                 {
#                     "name": "assessment_depth",
#                     "description": "screening, limited, or full",
#                     "required": False,
#                 },
#             ],
#         ),
#         Prompt(
#             name="value_creation_plan",
#             description="Generate an AI value creation plan for a portfolio company.",
#             arguments=[
#                 {
#                     "name": "company_id",
#                     "description": "Target company",
#                     "required": True,
#                 },
#                 {
#                     "name": "target_score",
#                     "description": "Target Org-AI-R score to achieve",
#                     "required": True,
#                 },
#                 {
#                     "name": "timeline_months",
#                     "description": "Implementation timeline in months",
#                     "required": False,
#                 },
#             ],
#         ),
#         Prompt(
#             name="competitive_analysis",
#             description="Compare AI-readiness across peer companies.",
#             arguments=[
#                 {
#                     "name": "company_ids",
#                     "description": "Comma-separated company IDs for comparison",
#                     "required": True,
#                 },
#                 {
#                     "name": "focus_dimensions",
#                     "description": "Specific dimensions to compare (comma-separated)",
#                     "required": False,
#                 },
#             ],
#         ),
#     ]


# @mcp_server.get_prompt()
# async def get_prompt(
#     name: str, arguments: Optional[Dict[str, str]] = None
# ) -> List[PromptMessage]:
#     """Get a prompt template with arguments."""
#     arguments = arguments or {}

#     if name == "due_diligence_assessment":
#         company_id = arguments.get("company_id", "UNKNOWN_COMPANY")
#         depth = arguments.get("assessment_depth", "limited")
#         return [
#             PromptMessage(
#                 role="user",
#                 content=TextContent(
#                     type="text",
#                     text=f"""Conduct a {depth} AI-readiness due diligence assessment for company {company_id}.

# Please:
# 1. First, retrieve the current Org-AI-R score using the `calculate_org_air_score` tool.
# 2. Gather evidence for each of the seven dimensions using the `get_company_evidence` tool.
# 3. Analyze strengths and gaps across dimensions based on the retrieved data and evidence.
# 4. Compare {company_id}'s Org-AI-R profile to sector benchmarks (e.g., from `orgair://sectors` resource).
# 5. Identify key risks and opportunities related to AI adoption and maturity.
# 6. Provide a strategic recommendation with a confidence level (e.g., 'high', 'medium', 'low').

# Structure your response as a formal due diligence memo, clearly stating the current Org-AI-R score, supporting evidence, comparative analysis, identified risks/opportunities, and a concise recommendation.""",
#                 ),
#             ),
#         ]

#     elif name == "value_creation_plan":
#         company_id = arguments.get("company_id", "UNKNOWN_COMPANY")
#         target_score = arguments.get("target_score", "75")
#         timeline_months = arguments.get("timeline_months", "24")
#         return [
#             PromptMessage(
#                 role="user",
#                 content=TextContent(
#                     type="text",
#                     text=f"""Create an AI value creation plan for company {company_id}.
# Target: Improve Org-AI-R score to {target_score} within {timeline_months} months.

# Please:
# 1. Get current Org-AI-R score using `calculate_org_air_score`.
# 2. Identify highest-impact improvement areas (e.g., based on low dimension scores or evidence gaps).
# 3. Use the `analyze_whatif_scenario` tool to model potential interventions and their impact on Org-AI-R score and financial metrics.
# 4. Project potential EBITDA impact using the `project_ebitda_impact` tool based on planned improvements.
# 5. Create a phased implementation roadmap, detailing key initiatives, estimated costs, and expected timelines.
# 6. Estimate investment requirements and projected ROI.

# Deliver as an executive-ready value creation plan, summarizing the current state, proposed initiatives, and projected financial benefits.""",
#                 ),
#             ),
#         ]

#     elif name == "competitive_analysis":
#         company_ids_str = arguments.get("company_ids", "").strip()
#         company_ids = [c.strip() for c in company_ids_str.split(",") if c.strip()]
#         dimensions = arguments.get("focus_dimensions", "all")

#         if not company_ids:
#             return [
#                 PromptMessage(
#                     role="user",
#                     content=TextContent(
#                         type="text",
#                         text="Error: 'company_ids' argument is required for competitive analysis.",
#                     ),
#                 )
#             ]

#         return [
#             PromptMessage(
#                 role="user",
#                 content=TextContent(
#                     type="text",
#                     text=f"""Conduct a competitive AI-readiness analysis for: {', '.join(company_ids)}.
# Focus dimensions: {dimensions}

# Please:
# 1. For each company, calculate its Org-AI-R score using the `calculate_org_air_score` tool.
# 2. Compare dimension-level performance across all specified companies.
# 3. Identify relative strengths and weaknesses for each company compared to its peers.
# 4. Highlight best practices observed from leading companies in the peer group.
# 5. Provide strategic recommendations for competitive positioning based on AI readiness.

# Present as a comparative analysis report with key findings and actionable insights.""",
#                 ),
#             ),
#         ]

#     return [
#         PromptMessage(
#             role="user",
#             content=TextContent(type="text", text=f"Unknown prompt: {name}"),
#         )
#     ]


# print("All prompt templates defined and registered.")

# # --- Test Prompt Generation ---

# print("\n--- Testing due_diligence_assessment prompt ---")
# due_diligence_prompt = await get_prompt(
#     "due_diligence_assessment",
#     {"company_id": "ACME-001", "assessment_depth": "full"},
# )
# print(due_diligence_prompt[0].content.text)

# print("\n--- Testing value_creation_plan prompt ---")
# value_plan_prompt = await get_prompt(
#     "value_creation_plan",
#     {"company_id": "GLOBAL-INC", "target_score": "85", "timeline_months": "36"},
# )
# print(value_plan_prompt[0].content.text)

# print("\n--- Testing competitive_analysis prompt ---")
# competitive_analysis_prompt = await get_prompt(
#     "competitive_analysis",
#     {
#         "company_ids": "ACME-001,GLOBAL-INC,HEALTH-SYS",
#         "focus_dimensions": "data_infrastructure,tech_stack,talent",
#     },
# )
# print(competitive_analysis_prompt[0].content.text)
# print("--- Simulating an AI Agent's End-to-End Value Creation Workflow ---")

# # Step 1: AI Agent receives a request to create a value creation plan.
# # It retrieves the appropriate prompt template to understand the task.
# print("\n[AI Agent]: Retrieving 'value_creation_plan' prompt for ACME-001...")
# company_for_plan = "ACME-001"
# target_score_for_plan = "80"
# timeline_for_plan = "18"
# value_plan_prompt_messages = await get_prompt(
#     "value_creation_plan",
#     {
#         "company_id": company_for_plan,
#         "target_score": target_score_for_plan,
#         "timeline_months": timeline_for_plan,
#     },
# )
# print(f"Generated Prompt for AI Agent:\n{value_plan_prompt_messages[0].content.text}")

# # Step 2: Agent needs current Org-AI-R score. It uses the 'calculate_org_air_score' tool.
# print(f"\n[AI Agent]: Calling 'calculate_org_air_score' for {company_for_plan}...")
# current_score_args = {
#     "company_id": company_for_plan,
#     "sector_id": "technology",
#     "dimension_scores": [70, 65, 75, 68, 72, 60, 70],
#     "talent_concentration": 0.2,
# }
# current_score_output = await call_tool("calculate_org_air_score", current_score_args)
# current_score_data = json.loads(current_score_output[0].text)
# current_org_air = current_score_data["final_score"]
# current_hr_score = current_score_data["components"]["h_r_score"]
# print(f"Current Org-AI-R Score for {company_for_plan}: {current_org_air:.2f}")

# # Step 3: Identify improvement areas and gather evidence (simplified for demo).
# # Let's assume the agent identifies 'data_infrastructure' and 'talent' as areas needing improvement.
# print(f"\n[AI Agent]: Gathering evidence for 'data_infrastructure' in {company_for_plan}...")
# evidence_for_data_infra = await call_tool(
#     "get_company_evidence",
#     {"company_id": company_for_plan, "dimension": "data_infrastructure", "limit": 1},
# )
# print(json.loads(evidence_for_data_infra[0].text)["evidence_items"][0]["content"])

# # Step 4: Model what-if scenarios for improvement (e.g., +10 in data_infra, +5 in talent).
# print(f"\n[AI Agent]: Analyzing what-if scenario for {company_for_plan}: 'Targeted_AI_Investment'...")
# whatif_scenario_args = {
#     "company_id": company_for_plan,
#     "scenario_name": "Targeted_AI_Investment",
#     "dimension_changes": {"data_infrastructure": 10, "talent": 5},
#     "investment_usd": 2000000,
# }
# whatif_result_output = await call_tool("analyze_whatif_scenario", whatif_scenario_args)
# whatif_data = json.loads(whatif_result_output[0].text)
# projected_org_air_change = whatif_data["org_air_change"]
# projected_financial_impact = whatif_data["projected_impact_usd"]
# print(f"Projected Org-AI-R Change: {projected_org_air_change:.2f}")
# print(f"Projected Financial Impact (USD): ${projected_financial_impact:,.2f}")

# # Step 5: Project EBITDA impact based on the target score.
# print(f"\n[AI Agent]: Projecting EBITDA impact for {company_for_plan} aiming for score {target_score_for_plan}...")
# ebitda_projection_args = {
#     "company_id": company_for_plan,
#     "entry_score": current_org_air,
#     "target_score": float(target_score_for_plan),
#     "h_r_score": current_hr_score,  # Use the H^R from the initial score calculation
#     "holding_period_years": 3,
# }
# ebitda_impact_output = await call_tool("project_ebitda_impact", ebitda_projection_args)
# ebitda_impact_data = json.loads(ebitda_impact_output[0].text)
# base_ebitda_impact_pct = ebitda_impact_data["scenarios"]["base"]["ebitda_impact_pct"]
# print(f"Projected Base EBITDA Impact: {base_ebitda_impact_pct * 100:.2f}%")

# # Step 6: AI Agent synthesizes all information into a value creation plan (conceptual).
# # The AI agent would then combine the prompt instructions with the retrieved data
# # to generate the final value creation plan document.
# print(f"\n[AI Agent]: All data gathered. Now generating the full Value Creation Plan for {company_for_plan}...")
# final_plan_summary = f"""
# --- AI Value Creation Plan Summary for {company_for_plan} ---

# Target: Improve Org-AI-R score to {target_score_for_plan} within {timeline_for_plan} months.

# 1. **Current Org-AI-R Score:** {current_org_air:.2f}

# 2. **Key Improvement Areas:** Data Infrastructure, Talent (identified from gap analysis/evidence)
#    * *Example Evidence:* "{json.loads(evidence_for_data_infra[0].text)['evidence_items'][0]['content']}"

# 3. **Modeled Scenario ('Targeted_AI_Investment'):**
#    * Expected Org-AI-R Change: +{projected_org_air_change:.2f}
#    * Estimated Financial Impact (USD): ${projected_financial_impact:,.2f}
#    * Confidence: Medium

# 4. **Projected EBITDA Impact (Base Scenario):** +{base_ebitda_impact_pct * 100:.2f}% over 3 years.

# 5. **Roadmap (Conceptual):**
#    * Phase 1 (Months 1-6): Data Governance Framework implementation, AI talent upskilling programs.
#    * Phase 2 (Months 7-12): Pilot AI-driven data analytics platform, develop internal AI champions.
#    * Phase 3 (Months 13-18): Scale successful AI initiatives, integrate AI into core business processes.

# 6. **Estimated Investment:** $2,000,000 USD (for key initiatives)

# 7. **Projected ROI:** High (based on EBITDA projections and efficiency gains)

# This plan provides a strategic direction for {company_for_plan} to achieve its AI-readiness goals and unlock significant value.
# """
# print(final_plan_summary)
