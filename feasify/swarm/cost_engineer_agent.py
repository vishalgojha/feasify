"""Cost Engineer Agent - Financial analysis specialist."""
from typing import Dict, Any
import logging

from feasify.swarm.base import BaseAgent
from feasify.swarm.state import AgentResult, ProjectState
from feasify.swarm.prompts import COST_ENGINEER_PROMPT

logger = logging.getLogger(__name__)


class CostEngineerAgent(BaseAgent):
    """Cost Engineer builds complete project cost stacks."""
    
    name = "COST_ENGINEER"
    system_prompt = COST_ENGINEER_PROMPT
    
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Build complete cost stack for the project."""
        
        prompt = f"""Build a complete project cost stack for this Mumbai real estate project:

PROJECT PARAMETERS:
{self.format_task(task)}

Include ALL of the following line items:

1. LAND COST
- User-provided or market estimate
- Stamp duty and registration (7% of land value in Mumbai)

2. CONSTRUCTION COST
- Use PWD rates as base
- Mumbai city loading: 1.35x
- Suburbs loading: 1.25x
- Include for structure + finishes

3. GOVERNMENT PREMIUMS
- Premium FSI payment to BMC
- Residential: 60% of ASR
- Commercial: 100% of ASR
- Industrial: 80% of ASR

4. STATUTORY CHARGES
- Development cess (MCGM)
- Infrastructure levy
- IOD/CC/OC fees

5. PROFESSIONAL FEES
- Architect fees (3-5% of construction)
- PMC fees (2-3% of construction)
- Legal fees
- Liaison fees

6. FINANCING COST
- Interest rate: 12% p.a.
- Utilization: 60% average
- Construction period estimate

7. STATUTORY COMPLIANCE
- Labour cess (1% of construction)
- GST (18% on construction services)

8. CONTINGENCY
- 5% of items 2-7 (excluding land and finance)

REVENUE MODEL:
- Saleable area (sqft/sqmt)
- Market rate for this location and typology
- Gross revenue
- Net revenue after GST

FEASIBILITY RATIOS:
- Gross margin %
- Cost per sqft
- Breakeven rate
- ROI estimate

OUTPUT:
{{
  "cost_stack_inr": {{
    "land": float,
    "construction": float,
    "bmc_premium": float,
    "tdr_purchase": float,
    "dev_cess": float,
    "infra_charges": float,
    "approval_fees": float,
    "professional_fees": float,
    "finance_cost": float,
    "contingency": float,
    "total": float
  }},
  "revenue_model": {{
    "saleable_sqm": float,
    "saleable_sqft": float,
    "market_rate_sqft": float,
    "gross_revenue_inr": float,
    "net_revenue_inr": float
  }},
  "feasibility_ratios": {{
    "gross_margin_pct": float,
    "net_margin_pct": float,
    "roi_pct": float,
    "cost_per_sqft_inr": float,
    "cost_per_sqm_inr": float,
    "breakeven_rate_sqft": float
  }},
  "rate_sources": [
    {{ "item": str, "source": str, "date": str, "rate": float }}
  ],
  "construction_details": {{
    "total_bua_sqft": float,
    "num_floors": int,
    "construction_period_months": int,
    "finish_spec": str
  }},
  "assumptions": [
    {{ "field": str, "assumption": str, "confidence": float }}
  ],
  "confidence_score": float,
  "notes": [str]
}}"""
        
        try:
            response = self.generate_json(prompt)
            
            return AgentResult(
                output=response,
                confidence=self.get_confidence(response),
                assumptions=self.parse_assumptions(response),
            )
        except Exception as e:
            logger.error(f"Cost Engineer error: {e}")
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                errors=[str(e)]
            )