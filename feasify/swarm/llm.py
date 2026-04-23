"""LLM client wrapper for Feasify Swarm - Gemini default, Groq fallback."""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, config):
        self.config = config
        self.groq_client = None
        self.gemini_client = None
        
        self._init_clients()
    
    def _init_clients(self):
        # Gemini (primary - best value)
        try:
            from google import genai
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if api_key:
                client = genai.Client(api_key=api_key)
                self.gemini_client = client
                logger.info("Gemini client initialized")
        except ImportError:
            logger.warning("google-genai not installed - install: pip install google-genai")
        except Exception as e:
            logger.warning(f"Gemini init failed: {e}")
        
        # Groq (fallback - fast)
        try:
            from groq import Groq
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                self.groq_client = Groq(api_key=api_key)
                logger.info("Groq client initialized")
        except ImportError:
            logger.warning("groq not installed")
        except Exception as e:
            logger.warning(f"Groq init failed: {e}")
    
    def generate(
        self,
        prompt: str,
        system: str = "",
        model: Optional[str] = None,
        max_tokens: int = 8192,
        temperature: float = 0.0,
    ) -> str:
        """Generate response, trying providers in priority order."""
        
        errors = []
        
        # 1. Gemini (primary - best value)
        if self.gemini_client:
            try:
                result = self._gemini_generate(prompt, system, max_tokens, temperature)
                if result:
                    logger.info("LLM: Gemini response")
                    return result
            except Exception as e:
                errors.append(f"Gemini: {e}")
                logger.debug(f"Gemini failed: {e}")
        
        # 2. Groq (fallback - fast)
        if self.groq_client:
            try:
                result = self._groq_generate(prompt, system, model or "llama3-70b-8192", max_tokens, temperature)
                if result:
                    logger.info("LLM: Groq response")
                    return result
            except Exception as e:
                errors.append(f"Groq: {e}")
                logger.debug(f"Groq failed: {e}")
        
        raise RuntimeError(f"All LLM providers failed: {errors}")
    
    def _gemini_generate(
        self,
        prompt: str,
        system: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[str]:
        if not self.gemini_client:
            return None
        
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        response = self.gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
            config={
                "max_output_tokens": max_tokens,
                "temperature": temperature,
            }
        )
        
        return response.text
    
    def _groq_generate(
        self,
        prompt: str,
        system: str,
        model: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[str]:
        if not self.groq_client:
            return None
        
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
    
    def generate_json(
        self,
        prompt: str,
        system: str = "",
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate JSON response with automatic fallback."""
        
        full_prompt = f"{prompt}\n\nRespond with valid JSON only. No markdown code blocks, no explanation."
        if system:
            full_prompt = f"{system}\n\n{full_prompt}"
        
        response = self.generate(
            prompt=full_prompt,
            system="",
            max_tokens=8192,
        )
        
        return self._parse_json(response)
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON from text, handling common issues."""
        # Remove markdown code blocks
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        # Try direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Find JSON object
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        # Clean common issues
        cleaned = text
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        cleaned = cleaned.replace('\\ ', '\\')
        
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(cleaned[start:end])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"Could not parse JSON from response: {text[:200]}")
    
    @property
    def available_providers(self) -> list:
        """List available LLM providers."""
        providers = []
        if self.gemini_client:
            providers.append("gemini")
        if self.groq_client:
            providers.append("groq")
        return providers


def get_llm_client(config=None) -> LLMClient:
    """Get configured LLM client."""
    if config is None:
        from feasify.swarm.state import SwarmConfig
        config = SwarmConfig()
    return LLMClient(config)