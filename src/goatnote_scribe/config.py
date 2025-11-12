"""Configuration management for GOAT Scribe - Emergency Medicine Edition"""

import os
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ScribeConfig:
    """Configuration for GOAT Scribe medical note generation"""
    
    # API Configuration
    nim_url: str = "https://integrate.api.nvidia.com/v1"
    nim_api_key: Optional[str] = None
    
    # Model Configuration (November 2025)
    model_name: str = "nvidia/llama-3.1-nemotron-nano-8b-v1"  # Publicly accessible Nemotron model
    temperature: float = 0.1
    max_tokens: int = 512  # Increased for detailed SOAP notes
    enable_reasoning: bool = True  # Use /think for transparent reasoning in audit trails
    
    # PHI Detection
    phi_language: str = "en"
    
    # Emergency Medicine Configuration
    specialty: str = "emergency_medicine"  # Primary specialty
    enable_guardrails: bool = True  # NeMo Guardrails for safety (CRITICAL)
    
    # ED-Specific Guardrails
    validate_vitals: bool = True  # Check vital signs are in valid ranges
    validate_medications: bool = True  # Check drug names/doses
    validate_acls_protocols: bool = True  # Verify ACLS/trauma protocols
    
    # Output Structure
    ed_note_structure: List[str] = None  # Will be set in __post_init__
    
    def __post_init__(self):
        """Set ED-specific defaults"""
        if self.ed_note_structure is None:
            self.ed_note_structure = [
                "Chief Complaint",
                "History of Present Illness",
                "Review of Systems",
                "Past Medical/Surgical History",
                "Medications",
                "Allergies",
                "Social History",
                "Physical Examination",
                "ED Course & Procedures",
                "Labs & Imaging",
                "Medical Decision Making",
                "Disposition"
            ]
        
        # Load API key
        if self.nim_api_key is None:
            self.nim_api_key = os.getenv("NGC_API_KEY")
            if self.nim_api_key is None:
                raise ValueError(
                    "NGC_API_KEY must be set via environment variable or config. "
                    "Get your key from: https://org.ngc.nvidia.com/setup/api-key"
                )
    
    # FHIR Configuration
    gcp_project_id: str = "scribe-fhir"
    gcp_location: str = "us-central1"
    gcp_dataset: str = "scribe-dataset"
    gcp_fhir_store: str = "scribe-store"
    
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

