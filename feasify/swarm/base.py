"""Base agent class for Feasify Swarm."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import asdict
import logging

from feasify.swarm.state import AgentResult, ProjectState, Assumption
from feasify.swarm.llm import LLMClient
from feasify.swarm.prompts import (
    PLANNER_PROMPT, DCPR_EXPERT_PROMPT, SPATIAL_RISK_PROMPT,
    COST_ENGINEER_PROMPT, REVIEWER_PROMPT
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all Swarm agents."""
    
    name: str = "BaseAgent"
    system_prompt: str = ""
    
    def __init__(self, llm_client: LLMClient, config):
        self.llm = llm_client
        self.config = config
    
    @abstractmethod
    def run(self, state: ProjectState, task: Dict[str, Any]) -> AgentResult:
        """Run the agent with given task and return result."""
        pass
    
    def generate_response(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        """Generate response from LLM."""
        system = system or self.system_prompt
        return self.llm.generate(prompt, system=system)
    
    def generate_json(
        self,
        prompt: str,
        system: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate JSON response from LLM."""
        system = system or self.system_prompt
        return self.llm.generate_json(prompt, system=system)
    
    def format_task(self, task: Dict[str, Any]) -> str:
        """Format task dictionary as prompt text."""
        lines = ["Task parameters:"]
        for key, value in task.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    def parse_assumptions(self, data: Dict[str, Any]) -> list:
        """Parse assumptions from agent output."""
        assumptions = []
        for a in data.get("assumptions", []):
            if isinstance(a, dict):
                assumptions.append(Assumption(
                    field=a.get("field", ""),
                    assumption=a.get("assumption", ""),
                    confidence=a.get("confidence", 1.0)
                ))
        return assumptions
    
    def get_confidence(self, data: Dict[str, Any]) -> float:
        """Get confidence score from agent output."""
        return data.get("confidence_score", data.get("confidence", 1.0))