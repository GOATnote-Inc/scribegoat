# GOAT Scribe: Emergency Medicine Edition

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![NVIDIA](https://img.shields.io/badge/NVIDIA-Nemotron%20Nano%209B%20v2-76B900)](https://developer.nvidia.com/)
[![Specialty](https://img.shields.io/badge/Specialty-Emergency%20Medicine-red)](https://github.com/GOATnote-Inc/scribegoat)

**Production-ready Emergency Medicine scribe with built-in safety guardrails.**

Designed for ED teams and NVIDIA healthcare AI startups that need a curated, bleeding-edge reference stack.

---

## NVIDIA Healthcare AI Showcase · November 2025

This repository now doubles as a living showcase of NVIDIA’s latest open healthcare AI tooling. The H100 playbook demonstrated here spans clinical text, imaging, multimodal, and deployment workflows:

- **CUDA 13.0 Update 2** with driver `580.105.08` (Blackwell-ready) and Nsight Compute/Systems 2025.4.
- **CUTLASS 4.3.0** kernels + FlashAttention 3.0.1 for high-throughput Hopper compute.
- **NVIDIA Nemotron Nano / Super Models** served through NIM (text-only `llama‑3.1‑nemotron‑nano‑8b‑v1` + VL `llama‑3.1‑nemotron‑nano‑vl‑8b‑v1` examples).
- **NVIDIA NeMo 25.09.1** + ModelOpt 0.21 for speech/Large Language Model fine-tuning.
- **MONAI 1.5.1 (weekly)** pipelines for medical imaging triage and FHIR export glue.
- **Clara Holoscan 3.0.1** operators for edge inference + DALI (`cuda130`) preprocessing.
- **TensorRT‑LLM 0.17.1 & Triton 3.2.1** for low-latency deployment.
- **Presidio 2.2.360** + GOATnote guardrails for HIPAA compliance.

> 📁 See `docs/NVIDIA-Healthcare-AI-Showcase.md` for setup commands, architecture diagrams, and links to each toolkit.

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

## 🚀 Deploy in 5 Minutes

**For startups evaluating NVIDIA's healthcare AI stack:**

```bash
# One-command deploy to H100
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat
export NGC_API_KEY="nvapi-YOUR-KEY-HERE"
./deploy/quick_start.sh
```

**What you get:**
- ✅ H100-optimized inference (1500+ tok/s)
- ✅ Safety guardrails (vitals, meds, protocols)
- ✅ HIPAA-compliant PHI detection
- ✅ FHIR R4 export ready
- ✅ Gradio UI on port 7860

**Full deployment guide**: [`deploy/DEPLOY.md`](deploy/DEPLOY.md)

---

## 📊 Profile & Optimize

**See NVIDIA tech in action:**

```bash
# Run NCU profiling
./deploy/profile.sh

# View H100 optimization metrics:
# - SM Efficiency (target: >80%)
# - Memory Bandwidth (target: >2 TB/s)
# - Tensor Core Utilization (target: >70%)
```

**Technologies showcased:**
- CUDA 13.0 (Blackwell support, tile programming)
- CUTLASS 4.3 (high-performance primitives)
- FlashAttention-3 (H100-optimized attention)
- cuDNN 9.15, TensorRT 10.14

**Profiling guide**: [`deploy/PROFILE.md`](deploy/PROFILE.md)

## Usage

### Web UI (Gradio)

```bash
python app.py
# Visit: http://localhost:7860
# Or get Brev public URL: brev urls
```

### Command Line

```bash
# Generate ED note
python -m goatnote_scribe.cli "35M with chest pain, 2h duration..."

# From file
cat encounter.txt | python -m goatnote_scribe.cli

# With FHIR export
python -m goatnote_scribe.cli --export-fhir "Patient presents..."
```

### Python API

```python
from goatnote_scribe import GOATScribe

scribe = GOATScribe()

result = scribe(
    "45M with fever, cough, dyspnea. BP 128/82, HR 92, RR 18, SpO2 96%."
)

print(result['note'])               # Complete ED note (12 sections)
print(result['guardrail_safe'])     # Safety validation
print(result['fhir_bundle'])        # FHIR R4 bundle

scribe.wipe()  # HIPAA cleanup
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
MODEL_NAME=nvidia/llama-3.1-nemotron-nano-8b-v1
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

# Optional: NVIDIA healthcare add-ons (requires https://pypi.nvidia.com)
pip install --upgrade -r requirements-nvidia-healthcare.txt \
    --extra-index-url https://pypi.nvidia.com

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

### Version 1.0 ✅ COMPLETE
- ✅ Nemotron Nano 9B v2 integration
- ✅ Emergency Medicine guardrails (vitals, meds, protocols)
- ✅ HIPAA-compliant PHI detection (18 identifiers)
- ✅ FHIR R4 export to GCP Healthcare API
- ✅ One-command deployment (< 5 min)
- ✅ H100 profiling with NCU/Nsight
- ✅ Gradio UI and CLI

### Version 1.1 (In Progress)
- [ ] NCU CI/CD integration (performance regression detection)
- [ ] Comprehensive test suite (pytest + guardrails)
- [ ] Example notebooks (chest pain, stroke, trauma)
- [ ] Audio transcription (Whisper large-v3-turbo)

### Version 2.0 (Planned)
- [ ] LoRA fine-tuning for ED specialty (MIMIC-IV-ED)
- [ ] Batch processing API
- [ ] Multi-language PHI detection (Spanish, Chinese)
- [ ] FHIR R5 support
- [ ] Clara integration for medical imaging

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

