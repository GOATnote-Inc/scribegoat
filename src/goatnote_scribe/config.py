"""Configuration management for GOAT Scribe"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScribeConfig:
    """Configuration for GOAT Scribe medical note generation"""
    
    # API Configuration
    nim_url: str = "https://integrate.api.nvidia.com/v1"
    nim_api_key: Optional[str] = None
    
    # Model Configuration (November 2025)
    model_name: str = "nvidia/nemotron-nano-3-moe"  # October 2025: Hybrid MoE, faster reasoning
    temperature: float = 0.1
    max_tokens: int = 512  # Increased for detailed SOAP notes
    
    # PHI Detection
    phi_language: str = "en"
    
    # FHIR Configuration
    gcp_project_id: str = "scribe-fhir"
    gcp_location: str = "us-central1"
    gcp_dataset: str = "scribe-dataset"
    gcp_fhir_store: str = "scribe-store"
    
    def __post_init__(self):
        """Load API key from environment if not provided"""
        if self.nim_api_key is None:
            self.nim_api_key = os.getenv("NGC_API_KEY")
            if self.nim_api_key is None:
                raise ValueError(
                    "NGC_API_KEY must be set via environment variable or config. "
                    "Get your key from: https://org.ngc.nvidia.com/setup/api-key"
                )
    
    @classmethod
    def from_env(cls) -> "ScribeConfig":
        """Create config from environment variables"""
        return cls(
            nim_url=os.getenv("NIM_URL", cls.nim_url),
            nim_api_key=os.getenv("NGC_API_KEY"),
            model_name=os.getenv("MODEL_NAME", cls.model_name),
            temperature=float(os.getenv("TEMPERATURE", cls.temperature)),
            max_tokens=int(os.getenv("MAX_TOKENS", cls.max_tokens)),
            gcp_project_id=os.getenv("GCP_PROJECT_ID", cls.gcp_project_id),
        )

