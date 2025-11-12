"""GOAT Scribe: H100-optimized HIPAA-compliant medical scribe"""

__version__ = "1.0.0"
__author__ = "B Dent"
__email__ = "b@thegoatnote.com"

from .scribe import GOATScribe
from .fhir import FHIRExporter

__all__ = ["GOATScribe", "FHIRExporter"]

