"""DCPR Expert Agent - Regulatory compliance specialist."""
from typing import Dict, Any
import logging

from feasify.swarm.base import BaseAgent
from feasify.swarm.state import AgentResult, ProjectState
from feasify.swarm.prompts import DCPR_EXPERT_PROMPT

logger = logging.getLogger(__name__)


class DCPRExpertAgent(BaseAgent):
    """DCPR Expert calculates FSI and regulatory compliance."""
    
    name = "DCPR_EXPERT"
    system_prompt = DCPR_EXPERT_PROMPT
    
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Run DCPR analysis for the project."""
        
        prompt = f"""Perform DCPR-2034 feasibility analysis for this project:

PROJECT DATA:
{self.format_task(task)}

Analyze:
1. What is the applicable regulation section (30A, 33-5, 33-7, 33-7B, etc)?
2. What is the base FSI for this zone and plot size?
3. What premium FSI is applicable?
4. What TDR options exist?
5. What fungible area can be claimed?
6. What is the maximum buildable area?
7. What is the premium payable to BMC?
8. What FSI exclusions apply (parking, lift, etc)?
9. What is the height limit based on road width?
10. What are the setback requirements?

Use DCPR-2034 regulations and cite specific sections.

Respond with detailed JSON:
{{
  "regulation_section": str,
  "regulation_basis": "DCPR_2034_BASE|GR_AMENDMENT",
  "gr_reference": str|null,
  "zone_analysis": {{ "zone": str, "sub_zone": str, "island_city": bool }},
  "fsi_breakdown": {{
    "base": float,
    "premium": float,
    "tdr": float,
    "fungible": float,
    "total": float
  }},
  "max_buildable_sqm": float,
  "saleable_sqm_estimate": float,
  "premium_payable_inr": float,
  "asr_rate_used": float,
  "asr_ward": str,
  "fsi_exclusions": [str],
  "height_limit_m": float,
  "setback_requirements": {{ "front": float, "side": float, "rear": float, "rear_open": float }},
  "parking_calculation": {{ "spaces_required": int, "area_sqm": float }},
  "tenement_analysis": {{ "max_tenements": int, "min_carpet_sqm": float }},
  "assumptions": [{{ "field": str, "assumption": str, "confidence": float }}],
  "confidence_score": float,
  "warnings": [str]
}}"""
        
        try:
            response = self.generate_json(prompt)
            
            return AgentResult(
                output=response,
                confidence=self.get_confidence(response),
                assumptions=self.parse_assumptions(response),
            )
        except Exception as e:
            logger.error(f"DCPR Expert error: {e}")
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                errors=[str(e)]
            )