"""LLM client wrapper for Feasify Swarm."""
import os
import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, config):
        self.config = config
        self.groq_client = None
        self.anthropic_client = None
        
        self._init_clients()
    
    def _init_clients(self):
        if self.config.use_groq:
            try:
                from groq import Groq
                api_key = os.getenv("GROQ_API_KEY")
                if api_key:
                    self.groq_client = Groq(api_key=api_key)
                    logger.info("Groq client initialized")
            except ImportError:
                logger.warning("groq not installed")
        
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
                logger.info("Anthropic client initialized")
        except ImportError:
            logger.warning("anthropic not installed")
    
    def generate(
        self,
        prompt: str,
        system: str = "",
        model: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.0,
    ) -> str:
        model = model or self.config.groq_model
        
        if model.startswith("claude"):
            return self._anthropic_generate(prompt, system, model, max_tokens, temperature)
        else:
            return self._groq_generate(prompt, system, model, max_tokens, temperature)
    
    def _groq_generate(
        self,
        prompt: str,
        system: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        if not self.groq_client:
            raise RuntimeError("Groq client not available")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = self.groq_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content
    
    def _anthropic_generate(
        self,
        prompt: str,
        system: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        if not self.anthropic_client:
            raise RuntimeError("Anthropic client not available")
        
        response = self.anthropic_client.messages.create(
            model=model.replace("claude-", ""),
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        
        return response.content[0].text
    
    def generate_json(
        self,
        prompt: str,
        system: str = "",
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        full_prompt = prompt + "\n\nRespond with valid JSON only."
        
        response = self.generate(
            prompt=full_prompt,
            system=system,
            max_tokens=4096,
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(response[start:end])
            raise ValueError(f"Could not parse JSON from response: {response[:200]}")