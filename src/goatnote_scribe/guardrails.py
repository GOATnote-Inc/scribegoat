"""
Emergency Medicine Guardrails for GOAT Scribe

CRITICAL SAFETY LAYER: Prevents medical errors in high-stakes ED environment.
For ED teams.

Author: Brandon Dent
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GuardrailViolation:
    """Represents a safety guardrail violation"""
    rule: str
    severity: str  # "critical", "warning", "info"
    message: str
    location: str  # Where in the note


class EDGuardrails:
    """
    Emergency Medicine safety guardrails.
    
    Validates clinical documentation for:
    - Vital signs within physiologic ranges
    - Medication dosages within safe limits
    - Protocol documentation completeness
    - Required ED note sections
    """
    
    # Valid ranges for vitals (adult ED patients)
    VITAL_RANGES = {
        "heart_rate": (20, 250),  # BPM
        "blood_pressure_systolic": (40, 250),  # mmHg
        "blood_pressure_diastolic": (20, 180),  # mmHg
        "respiratory_rate": (4, 60),  # breaths/min
        "temperature": (90.0, 108.0),  # Fahrenheit
        "spo2": (40, 100),  # Oxygen saturation %
        "gcs": (3, 15),  # Glasgow Coma Scale
    }
    
    # Common ED medications with max doses (mg unless specified)
    MEDICATION_LIMITS = {
        "morphine": 15,  # mg IV push
        "fentanyl": 200,  # mcg IV push
        "midazolam": 10,  # mg IV
        "lorazepam": 4,  # mg IV
        "epinephrine": 1,  # mg IV push (cardiac arrest)
        "atropine": 3,  # mg IV total
        "adenosine": 12,  # mg IV push
        "amiodarone": 300,  # mg IV push
        "naloxone": 10,  # mg IV/IM
        "aspirin": 325,  # mg PO
        "nitroglycerin": 0.4,  # mg SL
    }
    
    # ACLS/Trauma protocols that must be accurate
    CRITICAL_PROTOCOLS = [
        "ACLS",
        "ATLS", 
        "Trauma",
        "Sepsis",
        "Stroke",
        "STEMI",
        "DKA",
        "Status Epilepticus"
    ]
    
    def __init__(self, enable_vitals: bool = True, enable_meds: bool = True, enable_protocols: bool = True):
        self.enable_vitals = enable_vitals
        self.enable_meds = enable_meds
        self.enable_protocols = enable_protocols
    
    def validate_note(self, note: str) -> Tuple[bool, List[GuardrailViolation]]:
        """
        Validate ED note for safety violations.
        
        Returns:
            (is_safe, violations) - is_safe=False if critical violations found
        """
        violations = []
        
        if self.enable_vitals:
            violations.extend(self._check_vitals(note))
        
        if self.enable_meds:
            violations.extend(self._check_medications(note))
        
        if self.enable_protocols:
            violations.extend(self._check_protocols(note))
        
        # Check for critical violations
        critical_violations = [v for v in violations if v.severity == "critical"]
        is_safe = len(critical_violations) == 0
        
        return is_safe, violations
    
    def _check_vitals(self, note: str) -> List[GuardrailViolation]:
        """Check for invalid vital signs"""
        violations = []
        
        # Heart rate patterns
        hr_patterns = [
            r"HR[:\s]+(\d+)",
            r"heart rate[:\s]+(\d+)",
            r"pulse[:\s]+(\d+)",
        ]
        
        for pattern in hr_patterns:
            matches = re.finditer(pattern, note, re.IGNORECASE)
            for match in matches:
                hr = int(match.group(1))
                min_hr, max_hr = self.VITAL_RANGES["heart_rate"]
                if not (min_hr <= hr <= max_hr):
                    violations.append(GuardrailViolation(
                        rule="vital_signs_heart_rate",
                        severity="critical",
                        message=f"Heart rate {hr} is outside valid range ({min_hr}-{max_hr} BPM)",
                        location=match.group(0)
                    ))
        
        # Blood pressure patterns
        bp_pattern = r"BP[:\s]+(\d+)/(\d+)"
        matches = re.finditer(bp_pattern, note, re.IGNORECASE)
        for match in matches:
            sys = int(match.group(1))
            dia = int(match.group(2))
            
            min_sys, max_sys = self.VITAL_RANGES["blood_pressure_systolic"]
            min_dia, max_dia = self.VITAL_RANGES["blood_pressure_diastolic"]
            
            if not (min_sys <= sys <= max_sys):
                violations.append(GuardrailViolation(
                    rule="vital_signs_bp_systolic",
                    severity="critical",
                    message=f"Systolic BP {sys} is outside valid range ({min_sys}-{max_sys} mmHg)",
                    location=match.group(0)
                ))
            
            if not (min_dia <= dia <= max_dia):
                violations.append(GuardrailViolation(
                    rule="vital_signs_bp_diastolic",
                    severity="critical",
                    message=f"Diastolic BP {dia} is outside valid range ({min_dia}-{max_dia} mmHg)",
                    location=match.group(0)
                ))
        
        # Temperature patterns (Fahrenheit)
        temp_patterns = [
            r"Temp[:\s]+(\d+\.?\d*)",
            r"Temperature[:\s]+(\d+\.?\d*)",
        ]
        
        for pattern in temp_patterns:
            matches = re.finditer(pattern, note, re.IGNORECASE)
            for match in matches:
                temp = float(match.group(1))
                min_temp, max_temp = self.VITAL_RANGES["temperature"]
                if not (min_temp <= temp <= max_temp):
                    violations.append(GuardrailViolation(
                        rule="vital_signs_temperature",
                        severity="critical",
                        message=f"Temperature {temp}°F is outside valid range ({min_temp}-{max_temp}°F)",
                        location=match.group(0)
                    ))
        
        return violations
    
    def _check_medications(self, note: str) -> List[GuardrailViolation]:
        """Check for medication dosage errors"""
        violations = []
        
        for med_name, max_dose in self.MEDICATION_LIMITS.items():
            # Pattern: medication name followed by dose
            pattern = rf"{med_name}\s+(\d+\.?\d*)\s*(mg|mcg)?"
            matches = re.finditer(pattern, note, re.IGNORECASE)
            
            for match in matches:
                dose = float(match.group(1))
                unit = match.group(2) if match.group(2) else "mg"
                
                # Convert mcg to mg for comparison
                if unit.lower() == "mcg":
                    dose = dose / 1000
                
                if dose > max_dose:
                    violations.append(GuardrailViolation(
                        rule=f"medication_{med_name}_dose",
                        severity="critical",
                        message=f"{med_name.title()} dose {match.group(1)}{unit} exceeds max safe dose ({max_dose} mg)",
                        location=match.group(0)
                    ))
        
        return violations
    
    def _check_protocols(self, note: str) -> List[GuardrailViolation]:
        """Check for protocol mentions - warn if critical protocols mentioned"""
        violations = []
        
        for protocol in self.CRITICAL_PROTOCOLS:
            if re.search(rf"\b{protocol}\b", note, re.IGNORECASE):
                violations.append(GuardrailViolation(
                    rule=f"protocol_{protocol.lower()}",
                    severity="warning",
                    message=f"{protocol} protocol mentioned - ensure all steps documented and verified",
                    location=protocol
                ))
        
        return violations
    
    def format_violations(self, violations: List[GuardrailViolation]) -> str:
        """Format violations for display"""
        if not violations:
            return "✅ No guardrail violations detected"
        
        output = []
        output.append(f"\n⚠️  GUARDRAIL VIOLATIONS DETECTED: {len(violations)}\n")
        
        critical = [v for v in violations if v.severity == "critical"]
        warnings = [v for v in violations if v.severity == "warning"]
        
        if critical:
            output.append(f"🔴 CRITICAL ({len(critical)}):")
            for v in critical:
                output.append(f"  - {v.message}")
                output.append(f"    Location: '{v.location}'")
        
        if warnings:
            output.append(f"\n🟡 WARNINGS ({len(warnings)}):")
            for v in warnings:
                output.append(f"  - {v.message}")
        
        return "\n".join(output)

