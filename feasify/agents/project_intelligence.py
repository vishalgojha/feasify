"""Project Intelligence Agent - Claude-powered feasibility analysis."""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from feasify.agents.spatial import get_spatial_context
from feasify.agents.clearance_engine import resolve_clearances, calculate_critical_path
from feasify.agents.cost_engine import (
    calculate_government_premiums,
    calculate_professional_fees,
    calculate_financing_cost,
    build_cost_stack,
)
from feasify.agents.report import generate_report, print_cli_report, generate_pdf_report, ProjectReport
from feasify.agents.constants import (
    MUMBAI_ASR_LAND_RATE_PER_SQM,
    PWD_BASE_RATES,
)
from feasify.core.estimator import estimate_cost
from feasify.knowledge.dcpr import FeasibilityInput, calculate_feasibility
from feasify.core.fetcher import MCGMScraper, iGRScraper
from feasify.config import settings

logger = logging.getLogger(__name__)

# System prompt for the agent
SYSTEM_PROMPT = """You are a Mumbai real estate project feasibility expert with deep knowledge of DCPR-2034, MCGM processes, Maharashtra government clearances, and construction economics.

You have access to tools that fetch real data and run calculations. Use them in sequence to build a complete picture of a project.

Your job:
1. Resolve the CTS number to get plot details
2. Get spatial context — airport proximity, coastal proximity, heritage/railway flags
3. Derive the maximum viable design using DCPR-2034 rules
4. Identify every clearance this project triggers — do not miss any
5. Calculate the full cost stack — every line item with its basis
6. Reason over all of this to produce a recommendation.

Your recommendation must address:
- Is this project viable at the proposed use type?
- What is the total project cost range (min/max)?
- What is the single biggest risk to this project?
- What design or use-type changes would improve viability?
- What is the critical path — which clearance drives the project timeline?

Be specific. Use numbers. Flag contradictions. If a clearance makes the project unviable, say so directly.
If data is missing (e.g. road width not on record), state your assumption and its impact.
"""

# Tool definitions for Claude
TOOLS = [
    {
        "name": "resolve_cts",
        "description": "Fetch plot details from MCGM for a CTS number. Returns plot area, ward, address, zone designation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cts_number": {"type": "string"}
            },
            "required": ["cts_number"]
        }
    },
    {
        "name": "get_spatial_context",
        "description": "Given an address or lat/long, compute distance to CSIA airport, JNPA airport, nearest coastline, and flag heritage ward or railway buffer ward.",
        "input_schema": {
            "type": "object",
            "properties": {
                "address": {"type": "string"},
                "lat": {"type": "number"},
                "lng": {"type": "number"}
            }
        }
    },
    {
        "name": "calculate_feasibility",
        "description": "Run DCPR-2034 feasibility analysis. Returns permissible BUA, FSI, height, setbacks, parking, tenements.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plot_area_sqm": {"type": "number"},
                "zone": {"type": "string", "enum": ["island_city", "suburbs", "extended_suburbs", "barc_area", "crz_affected"]},
                "use": {"type": "string", "enum": ["residential", "commercial", "industrial"]},
                "road_width_m": {"type": "number"},
                "floors": {"type": "integer"},
                "include_fungible": {"type": "boolean"}
            },
            "required": ["plot_area_sqm", "zone", "use", "road_width_m", "floors"]
        }
    },
    {
        "name": "estimate_construction_cost",
        "description": "Estimate construction cost using PWD rates. Returns base cost, contingency, overhead, total.",
        "input_schema": {
            "type": "object",
            "properties": {
                "area_sqft": {"type": "number"},
                "zone_type": {"type": "string"},
                "num_floors": {"type": "integer"},
                "finish_grade": {"type": "string", "enum": ["basic", "standard", "premium"]}
            },
            "required": ["area_sqft", "zone_type", "num_floors"]
        }
    },
    {
        "name": "resolve_clearances",
        "description": "Given plot spatial context and derived design parameters, return all triggered clearances with fees, timelines, and risk levels.",
        "input_schema": {
            "type": "object",
            "properties": {
                "height_m": {"type": "number"},
                "bua_sqm": {"type": "number"},
                "plot_area_sqm": {"type": "number"},
                "distance_to_csia_km": {"type": "number"},
                "distance_to_coast_km": {"type": "number"},
                "ward": {"type": "string"},
                "use": {"type": "string"}
            },
            "required": ["height_m", "bua_sqm", "plot_area_sqm", "use"]
        }
    },
    {
        "name": "calculate_government_premiums",
        "description": "Calculate all government levies — premium FSI charge, fungible premium, development cess, infrastructure charges, IOD/CC/OC fees, labour cess.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plot_area_sqm": {"type": "number"},
                "bua_sqm": {"type": "number"},
                "fsi_used": {"type": "number"},
                "zonal_basic_fsi": {"type": "number"},
                "fungible_sqm": {"type": "number"},
                "use": {"type": "string"},
                "asr_rate_per_sqm": {"type": "number"}
            },
            "required": ["plot_area_sqm", "bua_sqm", "fsi_used", "zonal_basic_fsi", "use"]
        }
    },
    {
        "name": "calculate_professional_fees",
        "description": "Calculate architect, PMC, legal, liaison fees based on construction cost and project complexity.",
        "input_schema": {
            "type": "object",
            "properties": {
                "base_construction_cost": {"type": "number"},
                "ec_triggered": {"type": "boolean"},
                "heritage_triggered": {"type": "boolean"}
            },
            "required": ["base_construction_cost"]
        }
    },
    {
        "name": "calculate_financing_cost",
        "description": "Calculate financing drag from clearance timelines on land cost.",
        "input_schema": {
            "type": "object",
            "properties": {
                "land_cost": {"type": "number"},
                "max_clearance_days": {"type": "integer"},
                "interest_rate_pct": {"type": "number"}
            },
            "required": ["land_cost", "max_clearance_days"]
        }
    },
    {
        "name": "generate_report",
        "description": "Compile all analysis into a structured ProjectReport and save JSON. Returns report summary.",
        "input_schema": {
            "type": "object",
            "properties": {
                "cts_number": {"type": "string"},
                "spatial_context": {"type": "object"},
                "design": {"type": "object"},
                "clearances": {"type": "array"},
                "cost_stack": {"type": "object"},
                "recommendation": {"type": "string"},
                "risks": {"type": "array"},
                "output_dir": {"type": "string"}
            },
            "required": ["cts_number", "design", "clearances", "cost_stack", "recommendation"]
        }
    }
]


def dispatch_tool(name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route tool calls to actual Feasify implementations.
    
    Args:
        name: Tool name
        inputs: Tool input parameters
    
    Returns:
        Tool execution result
    """
    try:
        if name == "resolve_cts":
            scraper = MCGMScraper()
            return scraper.fetch_plot_details(inputs["cts_number"])
        
        elif name == "get_spatial_context":
            return get_spatial_context(
                address=inputs.get("address", ""),
                lat=inputs.get("lat"),
                lng=inputs.get("lng"),
                ward=inputs.get("ward", "")
            )
        
        elif name == "calculate_feasibility":
            from feasify.knowledge.dcpr import MumbaiZone, BuildingUse
            
            # Convert zone string to enum
            zone_map = {
                "island_city": MumbaiZone.ISLAND_CITY,
                "suburbs": MumbaiZone.SUBURBS,
                "extended_suburbs": MumbaiZone.EXTENDED_SUBURBS,
                "barc_area": MumbaiZone.BARC_AREA,
                "crz_affected": MumbaiZone.CRZ_AFFECTED,
            }
            use_map = {
                "residential": BuildingUse.RESIDENTIAL,
                "commercial": BuildingUse.COMMERCIAL,
                "industrial": BuildingUse.INDUSTRIAL,
            }
            
            inp = FeasibilityInput(
                plot_area_sqm=inputs["plot_area_sqm"],
                zone=zone_map.get(inputs["zone"], MumbaiZone.SUBURBS),
                use=use_map.get(inputs["use"], BuildingUse.RESIDENTIAL),
                road_width_m=inputs["road_width_m"],
                floors=inputs["floors"],
                include_fungible=inputs.get("include_fungible", False)
            )
            result = calculate_feasibility(inp)
            return result.__dict__
        
        elif name == "estimate_construction_cost":
            result = estimate_cost(
                area=inputs["area_sqft"],
                zone_type=inputs["zone_type"],
                num_floors=inputs["num_floors"]
            )
            return result
        
        elif name == "resolve_clearances":
            clearances = resolve_clearances(
                height_m=inputs["height_m"],
                bua_sqm=inputs["bua_sqm"],
                plot_area_sqm=inputs["plot_area_sqm"],
                distance_to_csia_km=inputs.get("distance_to_csia_km", 999.0),
                distance_to_coast_km=inputs.get("distance_to_coast_km", 999.0),
                ward=inputs.get("ward", ""),
                use=inputs["use"]
            )
            return clearances
        
        elif name == "calculate_government_premiums":
            return calculate_government_premiums(
                plot_area_sqm=inputs["plot_area_sqm"],
                bua_sqm=inputs["bua_sqm"],
                fsi_used=inputs["fsi_used"],
                zonal_basic_fsi=inputs["zonal_basic_fsi"],
                fungible_sqm=inputs.get("fungible_sqm", 0.0),
                use=inputs["use"],
                asr_rate_per_sqm=inputs.get("asr_rate_per_sqm", MUMBAI_ASR_LAND_RATE_PER_SQM)
            )
        
        elif name == "calculate_professional_fees":
            return calculate_professional_fees(
                base_construction_cost=inputs["base_construction_cost"],
                ec_triggered=inputs.get("ec_triggered", False),
                heritage_triggered=inputs.get("heritage_triggered", False)
            )
        
        elif name == "calculate_financing_cost":
            return calculate_financing_cost(
                land_cost=inputs["land_cost"],
                max_clearance_days=inputs["max_clearance_days"],
                interest_rate_pct=inputs.get("interest_rate_pct", 12.0)
            )
        
        elif name == "generate_report":
            # Generate report
            report_result = generate_report(
                cts_number=inputs["cts_number"],
                spatial_context=inputs.get("spatial_context", {}),
                design=inputs.get("design", {}),
                clearances=inputs.get("clearances", []),
                cost_stack=inputs.get("cost_stack", {}),
                recommendation=inputs.get("recommendation", ""),
                risks=inputs.get("risks", []),
                output_dir=inputs.get("output_dir", "data/reports")
            )
            return report_result
        
        else:
            return {"error": f"Unknown tool: {name}"}
    
    except Exception as e:
        logger.error(f"Tool {name} failed: {e}")
        return {"error": str(e), "tool": name}


def run_agent(
    cts_number: str,
    use_type: str,
    land_cost: float = None,
    finish_grade: str = "standard",
    output_dir: str = "data/reports",
    generate_pdf: bool = False
) -> ProjectReport:
    """
    Run the Project Intelligence Agent with Claude as reasoning engine.
    
    Args:
        cts_number: CTS number to analyze
        use_type: Proposed use type (residential/commercial/industrial)
        land_cost: Land cost in ₹ (optional)
        finish_grade: Construction grade (basic/standard/premium)
        output_dir: Directory to save reports
        generate_pdf: Whether to generate PDF report
    
    Returns:
        ProjectReport object
    """
    if not ANTHROPIC_AVAILABLE:
        raise RuntimeError("anthropic package not installed. Install with: pip install anthropic")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    
    # Build initial message
    land_cost_str = f"₹{land_cost:,.0f}" if land_cost else "Not provided"
    
    messages = [
        {
            "role": "user",
            "content": f"""Analyze this project:
CTS Number: {cts_number}
Proposed Use: {use_type}
Finish Grade: {finish_grade}
Land Cost: {land_cost_str}

Run a complete feasibility analysis. Derive the optimal design, identify all required clearances, calculate the full cost stack, and give me your recommendation."""
        }
    ]
    
    # Agent loop
    while True:
        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOLS,
                messages=messages
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
        
        # Append assistant response to history
        messages.append({"role": "assistant", "content": response.content})
        
        # If no tool calls, agent is done
        if response.stop_reason == "end_turn":
            break
        
        # Process tool calls
        tool_results = []
        for block in response.content:
            if hasattr(block, 'type') and block.type == "tool_use":
                logger.info(f"Calling tool: {block.name}")
                result = dispatch_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })
        
        if not tool_results:
            break
        
        messages.append({"role": "user", "content": tool_results})
    
    # Extract report from messages
    return extract_report(messages, output_dir, generate_pdf)


def extract_report(
    messages: List[Dict],
    output_dir: str = "data/reports",
    generate_pdf: bool = False
) -> ProjectReport:
    """
    Extract the final ProjectReport from agent messages.
    
    Args:
        messages: Conversation history
        output_dir: Output directory
        generate_pdf: Whether to generate PDF
    
    Returns:
        ProjectReport object
    """
    # Extract data from tool results in messages
    plot_details = {}
    spatial_context = {}
    design = {}
    clearances = []
    cost_stack = {}
    recommendation = ""
    risks = []
    
    for msg in messages:
        if msg.get("role") == "user" and isinstance(msg.get("content"), list):
            for item in msg["content"]:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    try:
                        result = json.loads(item["content"])
                        
                        if "plot_id" in result or "cts_number" in result:
                            plot_details = result
                        elif "distance_to_csia_km" in result:
                            spatial_context = result
                        elif "max_permissible_fsi" in result or "zonal_basic_fsi" in result:
                            design = result
                        elif isinstance(result, list) and len(result) > 0:
                            if "name" in result[0] and "timeline_days" in result[0]:
                                clearances = result
                        elif "grand_total" in result or "total_government_premiums" in result:
                            cost_stack = result
                        elif "recommendation" not in str(result).lower() and isinstance(result, dict):
                            # Might be recommendation text
                            pass
                    except:
                        pass
        
        # Extract recommendation from assistant messages
        if msg.get("role") == "assistant" and isinstance(msg.get("content"), list):
            for block in msg["content"]:
                if hasattr(block, 'type') and block.type == "text":
                    recommendation = block.text
                    break
    
    # Determine risks from warnings
    if spatial_context and "warnings" in spatial_context:
        risks.extend(spatial_context["warnings"])
    if design and "warnings" in design:
        risks.extend(design["warnings"])
    
    # Build report
    report = ProjectReport(
        cts_number=plot_details.get("cts_number") or plot_details.get("plot_id", "Unknown"),
        plot_details=plot_details,
        spatial_context=spatial_context,
        design=design,
        clearances=clearances,
        cost_stack=cost_stack,
        recommendation=recommendation,
        risks=risks
    )
    
    # Save JSON report
    try:
        generate_report(
            cts_number=report.cts_number,
            spatial_context=spatial_context,
            design=design,
            clearances=clearances,
            cost_stack=cost_stack,
            recommendation=recommendation,
            risks=risks,
            output_dir=output_dir
        )
    except Exception as e:
        logger.warning(f"Failed to save report: {e}")
    
    # Generate PDF if requested
    if generate_pdf and REPORTLAB_AVAILABLE:
        try:
            generate_pdf_report(report, output_dir)
        except Exception as e:
            logger.warning(f"Failed to generate PDF: {e}")
    
    # Print CLI report
    if RICH_AVAILABLE:
        print_cli_report(report)
    else:
        print(f"\nRecommendation:\n{recommendation}")
    
    return report


class ProjectIntelligenceAgent:
    """High-level agent class for running project analysis."""
    
    def __init__(self, api_key: str = None):
        if api_key:
            self.client = anthropic.Anthropic(api_key=api_key)
        elif os.getenv("ANTHROPIC_API_KEY"):
            self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        else:
            raise ValueError("ANTHROPIC_API_KEY required")
    
    def analyze(
        self,
        cts_number: str,
        use_type: str,
        land_cost: float = None,
        finish_grade: str = "standard",
        output_dir: str = "data/reports",
        generate_pdf: bool = False
    ) -> ProjectReport:
        """Run complete project feasibility analysis."""
        return run_agent(
            cts_number=cts_number,
            use_type=use_type,
            land_cost=land_cost,
            finish_grade=finish_grade,
            output_dir=output_dir,
            generate_pdf=generate_pdf
        )
