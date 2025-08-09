"""
AI Configuration - Manages AI client settings and API keys
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class AIConfig:
    """Configuration for AI clients."""
    provider: str = "auto"  # "openai", "anthropic", "auto", "mock"
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    max_tokens: int = 1000
    temperature: float = 0.3
    timeout: int = 30

class AIConfigManager:
    """Manages AI configuration and API key detection."""
    
    def __init__(self):
        self.config = AIConfig()
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # Override defaults with environment variables if present
        self.config.provider = os.getenv('AI_PROVIDER', self.config.provider)
        self.config.openai_model = os.getenv('OPENAI_MODEL', self.config.openai_model)
        self.config.anthropic_model = os.getenv('ANTHROPIC_MODEL', self.config.anthropic_model)
        
        # Numeric settings
        try:
            self.config.max_tokens = int(os.getenv('AI_MAX_TOKENS', str(self.config.max_tokens)))
            self.config.temperature = float(os.getenv('AI_TEMPERATURE', str(self.config.temperature)))
            self.config.timeout = int(os.getenv('AI_TIMEOUT', str(self.config.timeout)))
        except ValueError:
            pass  # Keep defaults if invalid values
    
    def get_available_providers(self) -> Dict[str, bool]:
        """Check which AI providers are available based on API keys."""
        return {
            'openai': bool(os.getenv('OPENAI_API_KEY')),
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY'))
        }
    
    def get_preferred_provider(self) -> str:
        """Get the preferred AI provider based on configuration and availability."""
        available = self.get_available_providers()
        
        if self.config.provider == "auto":
            # Auto-select based on availability (prefer OpenAI)
            if available['openai']:
                return 'openai'
            elif available['anthropic']:
                return 'anthropic'
            else:
                return 'mock'
        elif self.config.provider in available and available[self.config.provider]:
            return self.config.provider
        else:
            return 'mock'
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        if provider == 'openai':
            return os.getenv('OPENAI_API_KEY')
        elif provider == 'anthropic':
            return os.getenv('ANTHROPIC_API_KEY')
        return None
    
    def validate_setup(self) -> Dict[str, Any]:
        """Validate AI setup and return status information."""
        available = self.get_available_providers()
        preferred = self.get_preferred_provider()
        
        return {
            'available_providers': available,
            'preferred_provider': preferred,
            'has_ai_capability': preferred != 'mock',
            'config': self.config,
            'recommendations': self._get_setup_recommendations(available)
        }
    
    def _get_setup_recommendations(self, available: Dict[str, bool]) -> List[str]:
        """Get setup recommendations based on current configuration."""
        recommendations = []
        
        if not any(available.values()):
            recommendations.extend([
                "Set OPENAI_API_KEY environment variable to use OpenAI GPT-4 for test enhancement",
                "Or set ANTHROPIC_API_KEY environment variable to use Claude for test enhancement",
                "Example: export OPENAI_API_KEY='your-api-key-here'"
            ])
        
        if available['openai'] and available['anthropic']:
            recommendations.append(
                "Both OpenAI and Anthropic API keys detected. Set AI_PROVIDER=openai or AI_PROVIDER=anthropic to choose explicitly"
            )
        
        return recommendations