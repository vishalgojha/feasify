"""Project state management for Feasify Swarm."""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


class Verdict(str, Enum):
    APPROVED = "APPROVED"
    NEEDS_REVISION = "NEEDS_REVISION"
    NEEDS_RERUN = "NEEDS_RERUN"
    BLOCKED = "BLOCKED"
    MARGINAL = "MARGINAL"
    VIABLE = "VIABLE"


class Severity(str, Enum):
    BLOCKER = "BLOCKER"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SpatialVerdict(str, Enum):
    CLEAR = "CLEAR"
    CAUTION = "CAUTION"
    BLOCKED = "BLOCKED"


@dataclass
class Assumption:
    field: str
    assumption: str
    confidence: float


@dataclass
class AgentResult:
    output: Dict[str, Any]
    confidence: float = 1.0
    assumptions: List[Assumption] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PlotSummary:
    cts_number: str
    zone: str
    road_width_m: float
    plot_area_sqm: float = 0.0
    ward: str = ""
    address: str = ""


@dataclass
class FSISummary:
    base: float
    premium: float
    tdr: float
    fungible: float
    total: float
    max_buildable_sqm: float
    saleable_sqm: float


@dataclass
class DealBreaker:
    type: str
    description: str
    severity: Severity
    recommended_action: str = ""


@dataclass
class CostStack:
    land: float = 0.0
    construction: float = 0.0
    bmc_premium: float = 0.0
    tdr_purchase: float = 0.0
    dev_cess: float = 0.0
    infra_charges: float = 0.0
    approval_fees: float = 0.0
    professional_fees: float = 0.0
    finance_cost: float = 0.0
    contingency: float = 0.0
    total: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "land": self.land,
            "construction": self.construction,
            "bmc_premium": self.bmc_premium,
            "tdr_purchase": self.tdr_purchase,
            "dev_cess": self.dev_cess,
            "infra_charges": self.infra_charges,
            "approval_fees": self.approval_fees,
            "professional_fees": self.professional_fees,
            "finance_cost": self.finance_cost,
            "contingency": self.contingency,
            "total": self.total,
        }


@dataclass
class RiskCheck:
    check: str
    severity: Severity
    description: str
    recommended_action: str
    confidence_score: float


@dataclass
class ReviewerFlag:
    severity: Severity
    field: str
    description: str
    recommended_fix: str


@dataclass
class FeasibilityReport:
    plot_summary: PlotSummary
    fsi_summary: FSISummary
    deal_breakers: List[DealBreaker]
    cost_stack: CostStack
    feasibility_verdict: Verdict
    assumptions: List[Assumption]
    recommended_scenario: str
    risk_manifest: List[RiskCheck] = field(default_factory=list)
    reviewer_flags: List[ReviewerFlag] = field(default_factory=list)
    overall_confidence: float = 1.0
    raw_agent_outputs: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "plot_summary": {
                "cts": self.plot_summary.cts_number,
                "zone": self.plot_summary.zone,
                "road_width_m": self.plot_summary.road_width_m,
                "plot_area_sqm": self.plot_summary.plot_area_sqm,
                "ward": self.plot_summary.ward,
            },
            "fsi_summary": {
                "base": self.fsi_summary.base,
                "premium": self.fsi_summary.premium,
                "tdr": self.fsi_summary.tdr,
                "fungible": self.fsi_summary.fungible,
                "total": self.fsi_summary.total,
                "max_buildable_sqm": self.fsi_summary.max_buildable_sqm,
                "saleable_sqm": self.fsi_summary.saleable_sqm,
            },
            "deal_breakers": [
                {"type": db.type, "description": db.description, "severity": db.severity.value}
                for db in self.deal_breakers
            ],
            "cost_stack": self.cost_stack.to_dict(),
            "feasibility_verdict": self.feasibility_verdict.value,
            "assumptions": [{"field": a.field, "assumption": a.assumption, "confidence": a.confidence} for a in self.assumptions],
            "recommended_scenario": self.recommended_scenario,
            "overall_confidence": self.overall_confidence,
        }


@dataclass
class ProjectState:
    project_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    cts_number: str = ""
    iteration: int = 1
    status: str = "DRAFT"
    
    plot_summary: Optional[PlotSummary] = None
    spatial_result: Optional[AgentResult] = None
    dcpr_result: Optional[AgentResult] = None
    cost_result: Optional[AgentResult] = None
    reviewer_result: Optional[AgentResult] = None
    
    final_report: Optional[FeasibilityReport] = None
    all_assumptions: List[Assumption] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    corrections_cycle: int = 0
    max_corrections: int = 2
    
    def mark_updated(self):
        self.updated_at = datetime.now()
    
    def add_assumption(self, assumption: Assumption):
        self.all_assumptions.append(assumption)
    
    def can_correct(self) -> bool:
        return self.corrections_cycle < self.max_corrections
    
    def increment_correction(self):
        self.corrections_cycle += 1
        self.iteration += 1


@dataclass
class SwarmConfig:
    max_corrections: int = 2
    confidence_threshold: float = 0.7
    use_groq: bool = True
    groq_model: str = "llama3-70b-8192"
    anthropic_model: str = "claude-sonnet-4-20250514"
    
    planner_llm: str = "groq"
    sub_agent_llm: str = "groq"
    
    save_state: bool = True
    state_table: str = "project_state"
    
    def get_llm_for_role(self, role: str) -> str:
        if role in ["planner", "reviewer"]:
            return self.planner_llm
        return self.sub_agent_llm