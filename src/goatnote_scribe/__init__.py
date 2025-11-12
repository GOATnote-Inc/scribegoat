"""
GOAT Scribe: H100-optimized HIPAA-compliant Emergency Medicine scribe

For ED clinicians: physicians, nurses, PAs, NPs, techs, social workers, paramedics.
Safety-first design for high-stakes ED documentation.
"""

__version__ = "1.0.0"
__author__ = "Brandon Dent"
__email__ = "b@thegoatnote.com"
__specialty__ = "Emergency Medicine"

from .scribe import GOATScribe
from .fhir import FHIRExporter
from .guardrails import EDGuardrails, GuardrailViolation

__all__ = ["GOATScribe", "FHIRExporter", "EDGuardrails", "GuardrailViolation"]

