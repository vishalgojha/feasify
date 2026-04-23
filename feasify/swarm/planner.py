"""Planner Agent - Lead orchestrator for Feasify Swarm."""
from typing import Dict, Any
import logging

from feasify.swarm.base import BaseAgent
from feasify.swarm.state import AgentResult, ProjectState, PlotSummary, Assumption
from feasify.swarm.prompts import PLANNER_PROMPT

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Planner orchestrates the multi-agent analysis flow."""
    
    name = "PLANNER"
    system_prompt = PLANNER_PROMPT
    
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Determine next action based on current state."""
        
        plot_data = task.get("plot_data", {})
        user_request = task.get("request", "")
        
        prompt = f"""Analyze this real estate feasibility request:

{user_request}

PROJECT DATA:
{self.format_task(plot_data)}

Current state:
- Iteration: {state.iteration}
- Corrections cycle: {state.corrections_cycle}
- Has spatial result: {state.spatial_result is not None}
- Has DCPR result: {state.dcpr_result is not None}
- Has cost result: {state.cost_result is not None}
- Has reviewer result: {state.reviewer_result is not None}

What is the next action? Choose from:
1. SPATIAL_RISK - Check spatial constraints first
2. DCPR_EXPERT - Calculate FSI and regulations
3. COST_ENGINEER - Build cost stack
4. REVIEWER - Verify outputs
5. SYNTHESISE - Create final report
6. HALT - Stop due to blocking issues

Reasoning:
Thought: [your analysis]
Action: [your decision]
Input: [what to pass to next agent]

Respond with JSON:
{{
  "next_action": "SPATIAL_RISK|DCPR_EXPERT|COST_ENGINEER|REVIEWER|SYNTHESISE|HALT",
  "reasoning": "why you chose this",
  "input_for_next_agent": {{...}},
  "halt_reason": "if HALT, explain the blocker"
}}"""
        
        try:
            response = self.generate_json(prompt)
            
            return AgentResult(
                output=response,
                confidence=self.get_confidence(response),
                assumptions=self.parse_assumptions(response),
            )
        except Exception as e:
            logger.error(f"Planner error: {e}")
            return AgentResult(
                output={"error": str(e)},
                confidence=0.0,
                errors=[str(e)]
            )
    
    def synthesise_report(self, state: ProjectState) -> Dict[str, Any]:
        """Create final feasibility report from agent outputs."""
        
        prompt = f"""Synthesise the final feasibility report from agent outputs.

STATE:
- CTS Number: {state.cts_number}
- Iteration: {state.iteration}

SPATIAL RESULTS:
{state.spatial_result.output if state.spatial_result else "None"}

DCPR RESULTS:
{state.dcpr_result.output if state.dcpr_result else "None"}

COST RESULTS:
{state.cost_result.output if state.cost_result else "None"}

REVIEWER RESULTS:
{state.reviewer_result.output if state.reviewer_result else "None"}

ALL ASSUMPTIONS:
{[(a.field, a.assumption, a.confidence) for a in state.all_assumptions]}

Create the final feasibility report with:
1. Executive summary
2. Key metrics (FSI, BUA, cost, timeline)
3. Deal breakers identified
4. Feasibility verdict (VIABLE/MARGINAL/BLOCKED)
5. Assumptions made
6. Recommended next steps

Respond with JSON:
{{
  "plot_summary": {{ "cts": str, "zone": str, "road_width_m": float, "plot_area_sqm": float }},
  "fsi_summary": {{ "base": float, "premium": float, "tdr": float, "fungible": float, "total": float, "max_buildable_sqm": float, "saleable_sqm": float }},
  "deal_breakers": [{{ "type": str, "description": str, "severity": str }}],
  "cost_summary": {{ "total": float, "cost_per_sqft": float, "cost_per_sqm": float }},
  "feasibility_verdict": "VIABLE|MARGINAL|BLOCKED",
  "feasibility_ratios": {{ "gross_margin_pct": float, "roi_pct": float, "cost_per_sqft_inr": float, "breakeven_rate_sqft": float }},
  "risk_summary": {{ "critical_path_days": int, "key_risks": [str] }},
  "assumptions": [{{ "field": str, "assumption": str, "confidence": float }}],
  "recommended_scenario": str,
  "next_steps": [str]
}}"""
        
        try:
            return self.generate_json(prompt)
        except Exception as e:
            logger.error(f"Synthesise error: {e}")
            return {"error": str(e)}