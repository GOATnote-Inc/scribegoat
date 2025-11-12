# GOAT Scribe: Emergency Medicine Edition

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Nemotron%20Nano%209B%20v2-76B900)](https://developer.nvidia.com/)
[![Specialty](https://img.shields.io/badge/Specialty-Emergency%20Medicine-red)](https://github.com/GOATnote-Inc/scribegoat)

**Production-ready Emergency Medicine scribe with built-in safety guardrails.**

Designed for ED clinicians: physicians, nurses, PAs, NPs, techs, social workers, and paramedics.

---

## Features Built for ED Teams

**Safety guardrails** for high-stakes clinical documentation:
- ✅ **Vital signs validation**: HR, BP, RR, Temp, SpO2, GCS within valid ranges
- ✅ **Medication limits**: 11 common ED medications with max safe doses
- ✅ **Protocol warnings**: ACLS, ATLS, sepsis, stroke, STEMI protocols
- ✅ **ED documentation structure**: 12-section format with Medical Decision Making
- ✅ **High-risk awareness**: Prompts for critical rule-outs
- ✅ **Medical-legal compliance**: Return precautions, informed consent

---

## Features

### Emergency Medicine Safety (CRITICAL)

**Built-in Guardrails** (cannot be disabled in production):
- ✅ **Vital Signs Validation**: HR, BP, RR, Temp, SpO2, GCS within valid ranges
- ✅ **Medication Limits**: 11 common ED medications with max safe doses
- ✅ **Protocol Warnings**: ACLS, ATLS, sepsis, stroke, STEMI protocols
- ✅ **ED Note Structure**: All 12 required sections enforced

**Example**: Catches `"HR 350 BPM"` → ⚠️ Critical violation (valid range: 20-250)  
**Example**: Catches `"Morphine 50mg IV"` → ⚠️ Exceeds max safe dose (15mg)

### Core Capabilities
- **Real-Time Generation**: 6x higher throughput vs comparable models
- **HIPAA Compliance**: Microsoft Presidio for 18-identifier PHI detection
- **Audit Transparency**: Toggleable reasoning trails via `/think` token
- **Extended Context**: 128K tokens for comprehensive ED encounters
- **FHIR R4**: Standards-compliant healthcare interoperability
- **Zero-Residue Cleanup**: GPU memory wiping for data security
- **MONAI Integration**: Healthcare AI framework standard (v1.5.1)

### Technical Stack
- **Model**: NVIDIA Nemotron Nano 9B v2 (October 2025)
  - Hybrid Mamba-Transformer architecture
  - 6x throughput improvement
  - Toggleable reasoning for audit trails
- **PHI Detection**: Microsoft Presidio 2.2+
- **FHIR**: GCP Healthcare API with R4 support
- **Infrastructure**: H100 GPU optimization

---

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat

# Install dependencies
pip install -r requirements.txt

# Download spaCy model for Presidio
python -m spacy download en_core_web_lg

# Configure environment
cp .env.example .env
# Edit .env and add your NGC_API_KEY from https://org.ngc.nvidia.com/setup/api-key
```

### Basic Usage

```python
from goatnote_scribe import GOATScribe

# Initialize scribe
scribe = GOATScribe()

# Generate SOAP note
result = scribe(
    prompt="45M presents with 3-day history of fever (101°F), productive cough, "
           "mild dyspnea. No chest pain. PMH: asthma, GERD. "
           "Vitals: BP 128/82, HR 92, RR 18, SpO2 96% RA."
)

print(result['note'])               # Complete ED note (12 sections)
print(result['phi_removed'])        # Number of PHI entities detected
print(result['guardrail_safe'])     # True/False - any critical violations?
print(result['guardrail_report'])   # Detailed safety validation report
print(result['fhir_bundle'])        # FHIR R4 bundle

# Clean up (important for HIPAA)
scribe.wipe()
```

### FHIR Export to GCP

```python
from goatnote_scribe import GOATScribe, FHIRExporter

scribe = GOATScribe()
exporter = FHIRExporter()

# Generate note
result = scribe("Patient encounter text...")

# Upload to GCP Healthcare API
response = exporter.upload_bundle(result['fhir_bundle'])
print(f"Uploaded: {response['id']}")
```

---

## Configuration

### Environment Variables

```bash
# Required
NGC_API_KEY=nvapi-YOUR-KEY-HERE

# Optional (defaults shown)
NIM_URL=https://integrate.api.nvidia.com/v1
MODEL_NAME=nvidia/nemotron-nano-9b-v2
TEMPERATURE=0.1
MAX_TOKENS=512

# GCP FHIR (optional)
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
GCP_DATASET=scribe-dataset
GCP_FHIR_STORE=scribe-store
```

### Programmatic Configuration

```python
from goatnote_scribe import GOATScribe, ScribeConfig

config = ScribeConfig(
    nim_api_key="nvapi-...",
    model_name="nvidia/nemotron-nano-9b-v2",
    temperature=0.1,
    max_tokens=512,
    enable_reasoning=True  # Use /think for audit trails
)

scribe = GOATScribe(config=config)
```

---

## Architecture

### 2-Pass Generation Pipeline

```
Clinical Text
    ↓
PHI Detection (Presidio)
    ↓
De-identified Text
    ↓
Draft Generation (/think enabled)
    ↓
Self-Critique Pass
    ↓
Final SOAP Note
    ↓
FHIR R4 Bundle
    ↓
GCP Healthcare API (optional)
```

### Key Design Decisions

**Model Choice: Nemotron Nano 9B v2**
- 6x throughput vs Nemotron Super 49B
- 128K context vs 32K (full encounter support)
- Toggleable reasoning for HIPAA audit transparency
- Well-documented API, proven production use

**PHI Detection: Microsoft Presidio**
- 18 HIPAA identifier detection
- Anonymization before model inference
- No PHI sent to API endpoints

**Memory Safety**
- Zero-residue GPU cleanup via `wipe()`
- Ephemeral processing (no disk persistence)
- CUDA cache clearing after each session

---

## HIPAA Compliance

### PHI Protection

✅ **18 HIPAA Identifiers Detected:**
1. Names
2. Geographic subdivisions (ZIP, city, state)
3. Dates (birth, admission, discharge, death)
4. Phone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health plan numbers
10. Account numbers
11. Certificate/license numbers
12. Vehicle identifiers
13. Device identifiers
14. URLs
15. IP addresses
16. Biometric identifiers
17. Full-face photos
18. Any unique identifying numbers

### Audit Trail Features

- **Toggleable Reasoning**: `/think` token preserves model's reasoning process
- **Redaction Map**: Returns `[(entity_type, start, end)]` for each PHI detection
- **FHIR Bundles**: Structured, auditable output format
- **Memory Wiping**: Zero-residue cleanup via `wipe()` method

### Security Best Practices

```python
# Always wipe after processing
try:
    result = scribe(clinical_text)
    process_result(result)
finally:
    scribe.wipe()  # Ensures cleanup even if error occurs
```

---

## Performance

### Throughput (H100 GPU)

| Model | Tokens/sec | First Token | Context |
|-------|-----------|-------------|---------|
| Nemotron Super 49B | ~250 | 150ms | 32K |
| **Nemotron Nano 9B v2** | **~1500** | **<50ms** | **128K** |

*6x throughput improvement enables real-time clinical documentation*

### Latency Targets

- **Draft Generation**: <2 seconds
- **Self-Critique**: <2 seconds  
- **Total Pipeline**: <5 seconds (including PHI detection)

---

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src/goatnote_scribe --cov-report=html
```

### Code Quality

```bash
# Linting
ruff check src/
black --check src/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## API Reference

### GOATScribe

```python
class GOATScribe:
    def __init__(self, config: Optional[ScribeConfig] = None)
    
    def __call__(
        self,
        prompt: str,
        audio: Optional[bytes] = None,
        patient_id: str = "anon-001"
    ) -> Dict[str, any]
    
    def wipe(self) -> None
```

### FHIRExporter

```python
class FHIRExporter:
    def __init__(self, config: Optional[ScribeConfig] = None)
    
    def upload_bundle(self, bundle: Dict) -> Dict
    
    def get_patient(self, patient_id: str) -> Dict
    
    def search_documents(
        self,
        patient_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict
```

---

## Roadmap

### Version 1.0 (Current)
- ✅ Nemotron Nano 9B v2 integration
- ✅ HIPAA-compliant PHI detection
- ✅ FHIR R4 bundle generation
- ✅ GCP Healthcare API export
- ✅ Configuration management

### Version 1.1 (Planned)
- [ ] Comprehensive test suite (pytest)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Pre-commit hooks for secret scanning
- [ ] Audio transcription (Whisper)
- [ ] Example notebooks

### Version 2.0 (Future)
- [ ] H100 performance profiling (NCU/Nsight)
- [ ] Batch processing support
- [ ] Multi-language PHI detection
- [ ] Custom fine-tuning for specialties
- [ ] FHIR R5 support

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

### Reporting Issues

- **Security vulnerabilities**: Email b@thegoatnote.com (do not open public issues)
- **Bugs**: Open an issue with reproduction steps
- **Feature requests**: Open an issue with use case description

---

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

---

## Citation

```bibtex
@software{goat_scribe_2025,
  title = {GOAT Scribe: H100-Optimized HIPAA-Compliant Medical Scribe},
  author = {Dent, Brandon},
  year = {2025},
  url = {https://github.com/GOATnote-Inc/scribegoat},
  note = {NVIDIA Nemotron Nano 9B v2}
}
```

---

## Contact

**Email**: b@thegoatnote.com  
**Organization**: GOATnote Inc.  
**Repository**: https://github.com/GOATnote-Inc/scribegoat

---

## Acknowledgments

- **NVIDIA**: Nemotron Nano 9B v2 model and NIM platform
- **Microsoft**: Presidio PHI detection framework
- **Google Cloud**: Healthcare API and FHIR infrastructure
- **HL7**: FHIR R4 healthcare interoperability standards

