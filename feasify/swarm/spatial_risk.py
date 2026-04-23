"""Spatial Risk Agent - Deal-breaker detector."""
from typing import Dict, Any
import logging

from feasify.swarm.base import BaseAgent
from feasify.swarm.state import AgentResult, ProjectState, Severity
from feasify.swarm.prompts import SPATIAL_RISK_PROMPT

logger = logging.getLogger(__name__)


class SpatialRiskAgent(BaseAgent):
    """Spatial Risk identifies project-blocking spatial constraints."""
    
    name = "SPATIAL_RISK"
    system_prompt = SPATIAL_RISK_PROMPT
    
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Run all spatial risk checks."""
        
        lat = task.get("lat", 0)
        lon = task.get("lon", 0)
        zone = task.get("zone", "")
        ward = task.get("ward", "")
        cts = task.get("cts_number", "")
        proposed_height = task.get("proposed_height_m", 0)
        
        prompt = f"""Check all spatial constraints for this project:

PROJECT:
- CTS Number: {cts}
- Ward: {ward}
- Zone: {zone}
- Location: {lat}, {lon}
- Proposed building height: {proposed_height}m

Run ALL of the following checks:

1. CRZ CHECK
- What is the CRZ category for this location?
- What is the buffer requirement?
- Is development allowed?

2. AVIATION CHECK
- Distance to nearest airport (CSIA or secondary)?
- What is the permitted height?
- Is AAI NOC required?

3. HERITAGE CHECK
- Is this in a heritage precinct?
- What Grade (I, II, III)?
- Are there demolition restrictions?

4. DP RESERVATION CHECK
- Is there a Development Plan reservation on the plot?
- What purpose (road, amenity, etc)?
- What percentage of plot affected?

5. WARD RESTRICTIONS
- Any active stop-work orders?
- Any construction restrictions?
- Any ongoing litigation?

6. MANGROVE CHECK
- Distance to nearest mangrove area?
- Buffer requirements?

7. TDR RECEIVING ZONE
- Is this in a TDR receiving zone?
- What is the max TDR FSI?

8. DEFENCE/FOREST LAND
- Proximity to defence land?
- Any forest area nearby?

For each check, provide:
- Severity (BLOCKER/HIGH/MEDIUM/LOW)
- Description of issue
- Recommended action

OUTPUT FORMAT:
{{
  "risk_manifest": [
    {{
      "check": "CRZ|AVIATION|HERITAGE|DP_RESERVATION|WARD_RESTRICTIONS|MANGROVE|TDR_ZONE|DEFENCE_LAND",
      "severity": "BLOCKER|HIGH|MEDIUM|LOW",
      "description": str,
      "recommended_action": str,
      "confidence_score": float
    }}
  ],
  "overall_verdict": "CLEAR|CAUTION|BLOCKED",
  "proceed_to_cost": bool,
  "spatial_constraints_for_design": [str],
  "critical_requirements": [str]
}}"""
        
        try:
            response = self.generate_json(prompt)
            
            return AgentResult(
                output=response,
                confidence=self.get_confidence(response),
                assumptions=self.parse_assumptions(response),
            )
        except Exception as e:
            logger.error(f"Spatial Risk error: {e}")
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                errors=[str(e)]
            )