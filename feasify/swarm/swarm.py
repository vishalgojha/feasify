"""Feasify Swarm - Multi-agent orchestrator."""
from typing import Dict, Any, Optional
import logging

from feasify.swarm.state import (
    ProjectState, SwarmConfig, AgentResult, Verdict, Severity, SpatialVerdict
)
from feasify.swarm.llm import LLMClient
from feasify.swarm.base import BaseAgent
from feasify.swarm.planner import PlannerAgent
from feasify.swarm.dcpr_expert import DCPRExpertAgent
from feasify.swarm.spatial_risk import SpatialRiskAgent
from feasify.swarm.cost_engineer_agent import CostEngineerAgent
from feasify.swarm.reviewer import ReviewerAgent

logger = logging.getLogger(__name__)


class FeasifySwarm:
    """Orchestrates the multi-agent feasibility analysis."""
    
    def __init__(self, config: Optional[SwarmConfig] = None):
        self.config = config or SwarmConfig()
        self.llm = LLMClient(self.config)
        
        self.agents: Dict[str, BaseAgent] = {
            "planner": PlannerAgent(self.llm, self.config),
            "dcpr_expert": DCPRExpertAgent(self.llm, self.config),
            "spatial_risk": SpatialRiskAgent(self.llm, self.config),
            "cost_engineer": CostEngineerAgent(self.llm, self.config),
            "reviewer": ReviewerAgent(self.llm, self.config),
        }
    
    def analyze(
        self,
        cts_number: str,
        zone: str,
        road_width_m: float,
        use: str = "residential",
        plot_area_sqm: float = 0,
        land_cost: float = 0,
        lat: float = 0,
        lon: float = 0,
        ward: str = "",
        proposed_height_m: float = 0,
        finish_grade: str = "standard",
    ) -> Dict[str, Any]:
        """
        Run complete feasibility analysis using multi-agent swarm.
        
        Args:
            cts_number: CTS number for the plot
            zone: Zone designation (island_city, suburbs, etc.)
            road_width_m: Road width in meters
            use: Building use type (residential/commercial/industrial)
            plot_area_sqm: Plot area in square meters
            land_cost: User-provided land cost in INR
            lat: Latitude for spatial checks
            lon: Longitude for spatial checks
            ward: Ward designation
            proposed_height_m: Proposed building height
            finish_grade: Construction finish grade
        
        Returns:
            Complete feasibility report
        """
        state = ProjectState(cts_number=cts_number)
        
        base_task = {
            "cts_number": cts_number,
            "zone": zone,
            "road_width_m": road_width_m,
            "use": use,
            "plot_area_sqm": plot_area_sqm,
            "land_cost": land_cost,
            "lat": lat,
            "lon": lon,
            "ward": ward,
            "proposed_height_m": proposed_height_m,
            "finish_grade": finish_grade,
        }
        
        logger.info(f"Starting Feasify Swarm analysis for {cts_number}")
        
        state.spatial_result = self._run_spatial_risk(state, base_task)
        
        if self._has_blocker(state.spatial_result):
            logger.warning(f"BLOCKER found in spatial risk for {cts_number}")
            return self._build_blocked_report(state, base_task)
        
        state.dcpr_result = self._run_dcpr_expert(state, base_task)
        state.cost_result = self._run_cost_engineer(state, base_task)
        state.reviewer_result = self._run_reviewer(state)
        
        if not self._is_approved(state.reviewer_result):
            if self._needs_rerun(state.reviewer_result):
                state.increment_correction()
                state.dcpr_result = self._run_dcpr_expert(state, base_task)
                state.reviewer_result = self._run_reviewer(state)
            
            if not self._is_approved(state.reviewer_result) and state.can_correct():
                state.increment_correction()
                state.cost_result = self._run_cost_engineer(state, base_task)
                state.reviewer_result = self._run_reviewer(state)
        
        report = self._build_final_report(state)
        logger.info(f"Feasify Swarm analysis complete for {cts_number}")
        
        return report
    
    def _run_spatial_risk(self, state: ProjectState, task: Dict) -> AgentResult:
        """Run Spatial Risk agent."""
        logger.info(f"Running SPATIAL_RISK for {state.cts_number}")
        return self.agents["spatial_risk"].run(state, task)
    
    def _run_dcpr_expert(self, state: ProjectState, task: Dict) -> AgentResult:
        """Run DCPR Expert agent."""
        logger.info(f"Running DCPR_EXPERT for {state.cts_number}")
        return self.agents["dcpr_expert"].run(state, task)
    
    def _run_cost_engineer(self, state: ProjectState, task: Dict) -> AgentResult:
        """Run Cost Engineer agent."""
        logger.info(f"Running COST_ENGINEER for {state.cts_number}")
        return self.agents["cost_engineer"].run(state, task)
    
    def _run_reviewer(self, state: ProjectState) -> AgentResult:
        """Run Reviewer agent."""
        logger.info(f"Running REVIEWER for {state.cts_number}")
        return self.agents["reviewer"].run(state, {})
    
    def _has_blocker(self, result: AgentResult) -> bool:
        """Check if spatial result has any BLOCKER severity."""
        if not result or not result.output:
            return False
        
        risk_manifest = result.output.get("risk_manifest", [])
        for risk in risk_manifest:
            if risk.get("severity") == "BLOCKER":
                return True
        return False
    
    def _is_approved(self, result: AgentResult) -> bool:
        """Check if reviewer approved the outputs."""
        if not result or not result.output:
            return False
        return result.output.get("verdict") == "APPROVED"
    
    def _needs_rerun(self, result: AgentResult) -> bool:
        """Check if reviewer requires a full rerun."""
        if not result or not result.output:
            return False
        return result.output.get("verdict") == "NEEDS_RERUN"
    
    def _build_blocked_report(self, state: ProjectState, task: Dict) -> Dict[str, Any]:
        """Build report when project is blocked by spatial constraints."""
        risk_manifest = state.spatial_result.output.get("risk_manifest", [])
        blockers = [
            {
                "type": r.get("check", ""),
                "description": r.get("description", ""),
                "severity": r.get("severity", ""),
                "recommended_action": r.get("recommended_action", ""),
            }
            for r in risk_manifest
            if r.get("severity") == "BLOCKER"
        ]
        
        return {
            "project_id": state.project_id,
            "cts_number": state.cts_number,
            "status": "BLOCKED",
            "verdict": "BLOCKED",
            "blockers": blockers,
            "all_risks": risk_manifest,
            "plot_summary": {
                "cts": state.cts_number,
                "zone": task.get("zone", ""),
                "road_width_m": task.get("road_width_m", 0),
                "plot_area_sqm": task.get("plot_area_sqm", 0),
            },
            "message": "Project is BLOCKED due to spatial constraints. See blockers for details.",
            "can_proceed": False,
            "iteration": state.iteration,
        }
    
    def _build_final_report(self, state: ProjectState) -> Dict[str, Any]:
        """Build the final feasibility report."""
        dcpr = state.dcpr_result.output if state.dcpr_result else {}
        cost = state.cost_result.output if state.cost_result else {}
        spatial = state.spatial_result.output if state.spatial_result else {}
        reviewer = state.reviewer_result.output if state.reviewer_result else {}
        
        fsi = dcpr.get("fsi_breakdown", {})
        cost_stack = cost.get("cost_stack_inr", {})
        ratios = cost.get("feasibility_ratios", {})
        revenue = cost.get("revenue_model", {})
        
        fsi_total = fsi.get("total", 0)
        
        if fsi_total >= 3.0:
            verdict = "VIABLE"
        elif fsi_total >= 2.0:
            verdict = "MARGINAL"
        else:
            verdict = "BLOCKED"
        
        if reviewer.get("flags"):
            verdict = "NEEDS_REVISION"
        
        return {
            "project_id": state.project_id,
            "cts_number": state.cts_number,
            "status": "COMPLETE",
            "verdict": verdict,
            "plot_summary": {
                "cts": state.cts_number,
                "zone": dcpr.get("zone_analysis", {}).get("zone", ""),
                "road_width_m": 0,
                "plot_area_sqm": 0,
            },
            "fsi_summary": {
                "base": fsi.get("base", 0),
                "premium": fsi.get("premium", 0),
                "tdr": fsi.get("tdr", 0),
                "fungible": fsi.get("fungible", 0),
                "total": fsi.get("total", 0),
                "max_buildable_sqm": dcpr.get("max_buildable_sqm", 0),
                "saleable_sqm": dcpr.get("saleable_sqm_estimate", 0),
            },
            "regulation": {
                "section": dcpr.get("regulation_section", ""),
                "basis": dcpr.get("regulation_basis", ""),
                "gr_reference": dcpr.get("gr_reference"),
            },
            "cost_summary": {
                "total": cost_stack.get("total", 0),
                "construction": cost_stack.get("construction", 0),
                "premium": cost_stack.get("bmc_premium", 0),
                "cost_per_sqft": ratios.get("cost_per_sqft_inr", 0),
                "cost_per_sqm": ratios.get("cost_per_sqm_inr", 0),
            },
            "revenue": {
                "saleable_sqft": revenue.get("saleable_sqft", 0),
                "market_rate_sqft": revenue.get("market_rate_sqft", 0),
                "gross_revenue": revenue.get("gross_revenue_inr", 0),
            },
            "feasibility_ratios": ratios,
            "risk_manifest": spatial.get("risk_manifest", []),
            "reviewer_flags": reviewer.get("flags", []),
            "reviewer_verdict": reviewer.get("verdict", "UNKNOWN"),
            "overall_confidence": reviewer.get("overall_confidence", 1.0),
            "can_proceed": verdict in ["VIABLE", "MARGINAL"] and reviewer.get("verdict") == "APPROVED",
            "iteration": state.iteration,
            "assumptions": [
                {"field": a.field, "assumption": a.assumption, "confidence": a.confidence}
                for a in state.all_assumptions
            ],
        }


def run_swarm_analysis(
    cts_number: str,
    zone: str,
    road_width_m: float,
    use: str = "residential",
    **kwargs
) -> Dict[str, Any]:
    """Convenience function to run swarm analysis."""
    swarm = FeasifySwarm()
    return swarm.analyze(
        cts_number=cts_number,
        zone=zone,
        road_width_m=road_width_m,
        use=use,
        **kwargs
    )