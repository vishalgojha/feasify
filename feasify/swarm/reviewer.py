"""Reviewer Agent - Verification and quality control."""
from typing import Dict, Any, List
import logging

from feasify.swarm.base import BaseAgent
from feasify.swarm.state import AgentResult, ProjectState, ReviewerFlag, Severity
from feasify.swarm.prompts import REVIEWER_PROMPT

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """Reviewer verifies and validates agent outputs."""
    
    name = "REVIEWER"
    system_prompt = REVIEWER_PROMPT
    
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Run verification checks on agent outputs."""
        
        prompt = f"""Verify the following agent outputs for internal consistency:

STATE:
- CTS: {state.cts_number}
- Iteration: {state.iteration}

DCPR OUTPUT:
{self._format_dict(state.dcpr_result.output if state.dcpr_result else {})}

COST OUTPUT:
{self._format_dict(state.cost_result.output if state.cost_result else {})}

SPATIAL OUTPUT:
{self._format_dict(state.spatial_result.output if state.spatial_result else {})}

Run ALL of the following checks:

1. FSI ARITHMETIC
- Verify: base + premium + tdr + fungible == total
- Tolerance: ±0.01

2. PREMIUM COST CALCULATION
- Verify: premium_fsi_sqm × ASR × premium_pct == bmc_premium
- Premium pct: 60% residential, 100% commercial

3. DEVELOPMENT CESS
- Verify against current MCGM schedule for zone

4. SALEABLE AREA
- Must be ≤ 80% of max_buildable (residential)
- Typical is 75%

5. REVENUE CHECK
- Verify: saleable_sqm × 10.764 × market_rate_sqft == gross_revenue

6. FINANCE COST
- Verify: 0.12 × 0.60 × (total - land) × years == finance_cost

7. CONTINGENCY
- Must be 5% of (construction + premium + tdr + cess + infra + approval + professional + finance)

8. WARD CONSISTENCY
- DCPR ward must match Cost ward

9. ASR RATE CONSISTENCY
- ASR rate used by DCPR agent must match Cost engineer

10. SPATIAL BLOCKER CHECK
- If any SPATIAL risk is BLOCKER, verify no revenue projection in cost stack

OUTPUT:
{{
  "checks_run": int,
  "checks_passed": int,
  "flags": [
    {{
      "severity": "HIGH|MEDIUM|LOW",
      "field": str,
      "description": str,
      "expected_value": str,
      "actual_value": str,
      "delta": float,
      "recommended_fix": str
    }}
  ],
  "verdict": "APPROVED|NEEDS_REVISION|NEEDS_RERUN",
  "overall_confidence": float,
  "checks_summary": {{
    "fsi_arithmetic": "PASS|FAIL",
    "premium_cost": "PASS|FAIL",
    "dev_cess": "PASS|FAIL",
    "saleable_area": "PASS|FAIL",
    "revenue_model": "PASS|FAIL",
    "finance_cost": "PASS|FAIL",
    "contingency": "PASS|FAIL",
    "ward_consistency": "PASS|FAIL",
    "asr_consistency": "PASS|FAIL",
    "spatial_revenue": "PASS|FAIL"
  }},
  "notes_for_planner": str
}}"""
        
        try:
            response = self.generate_json(prompt)
            
            flags = []
            for f in response.get("flags", []):
                flags.append(ReviewerFlag(
                    severity=Severity(f.get("severity", "MEDIUM")),
                    field=f.get("field", ""),
                    description=f.get("description", ""),
                    recommended_fix=f.get("recommended_fix", "")
                ))
            
            return AgentResult(
                output=response,
                confidence=response.get("overall_confidence", 1.0),
                assumptions=[],
            )
        except Exception as e:
            logger.error(f"Reviewer error: {e}")
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                errors=[str(e)]
            )
    
    def _format_dict(self, d: Dict) -> str:
        """Format dictionary for prompt."""
        if not d:
            return "No data"
        lines = []
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(f"{k}:")
                for k2, v2 in v.items():
                    lines.append(f"  {k2}: {v2}")
            else:
                lines.append(f"{k}: {v}")
        return "\n".join(lines)