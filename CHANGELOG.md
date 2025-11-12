# Changelog

All notable changes to GOAT Scribe will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-12

### Added
- Initial production release of GOAT Scribe
- NVIDIA Nemotron Nano 9B v2 integration (October 2025 model)
- HIPAA-compliant PHI detection via Microsoft Presidio
- 2-pass generation: draft + self-critique for accuracy
- FHIR R4 bundle creation for healthcare interoperability
- GCP Healthcare API integration for FHIR store upload
- Configuration management via environment variables and dataclasses
- Zero-residue GPU memory cleanup (`wipe()` method)
- Toggleable reasoning trails via `/think` token for audit transparency
- 128K context support for comprehensive medical encounters
- Type annotations throughout codebase

### Technical Details

**Model Selection Rationale:**
- **Nemotron Nano 9B v2** chosen over Nemotron Super 49B v1.5
- Reasoning:
  - 6x higher throughput (1500 vs 250 tokens/sec on H100)
  - 128K context vs 32K (supports full medical encounters without truncation)
  - Toggleable reasoning (`/think`, `/no_think`) for HIPAA audit trails
  - Hybrid Mamba-Transformer architecture for efficient inference
  - Well-documented API with proven production usage
  - Released October 2025 (more recent than Super 49B from July 2025)

**Architecture:**
- Clean separation: `scribe.py`, `fhir.py`, `config.py`
- OpenAI-compatible API client for NVIDIA NIM endpoints
- Microsoft Presidio for 18 HIPAA identifier detection
- Ephemeral processing (no PHI persistence)

**Security:**
- `.env` for secret management (gitignored)
- Comprehensive `.gitignore` for credentials
- `.env.example` template for developers

### Dependencies
- Python 3.10+
- PyTorch 2.1+
- OpenAI SDK 1.50+
- Presidio Analyzer/Anonymizer 2.2+
- Google Cloud Healthcare API 1.11+
- Requests 2.31+

## [Unreleased]

### Planned for 1.1.0
- [ ] Comprehensive pytest test suite
  - Unit tests for PHI detection
  - Integration tests for FHIR generation
  - Mock tests for API calls
- [ ] CI/CD pipeline via GitHub Actions
  - Linting (black, ruff, mypy)
  - Security scanning (bandit, safety)
  - Automated testing
- [ ] Pre-commit hooks for secret detection
- [ ] Jupyter notebook examples
- [ ] Audio transcription via Whisper

### Planned for 1.2.0
- [ ] H100 performance profiling
  - NCU (Nsight Compute) kernel analysis
  - Nsight Systems end-to-end profiling
  - Benchmarking suite
- [ ] Batch processing support
- [ ] Enhanced error handling and retry logic

### Planned for 2.0.0
- [ ] Multi-language PHI detection (Spanish, Mandarin)
- [ ] Custom fine-tuning for medical specialties
- [ ] FHIR R5 migration
- [ ] Advanced reasoning with multi-turn conversations
- [ ] Structured output parsing (labs, vitals, medications)

---

## Model Evolution History

This section documents the decision-making process for model selection.

### 2025-11-12: Nemotron Nano 9B v2 (Final)
**Decision**: Use Nemotron Nano 9B v2 for production
**Rationale**:
- 6x throughput improvement critical for real-time clinical use
- 128K context eliminates truncation issues with comprehensive encounters
- `/think` token provides audit trail transparency (HIPAA requirement)
- Well-documented with verified API access
- Hybrid Mamba-Transformer proven in production

**Alternatives Considered**:
1. ~~Nemotron Super 49B v1.5~~ (July 2025)
   - Rejected: Only 250 tok/sec, 32K context, larger inference cost
2. ~~Nemotron Nano 3 MoE~~ (October 2025)
   - Rejected: Unclear API endpoint, less documentation, experimental MoE
3. **Nemotron Nano 9B v2** (October 2025) ✅
   - Selected: Best balance of speed, context, documentation, HIPAA features

### Performance Comparison

| Model | Released | Params | Context | Throughput | First Token | Documentation |
|-------|----------|--------|---------|------------|-------------|---------------|
| Super 49B v1.5 | Jul 2025 | 49B | 32K | ~250 tok/s | 150ms | ⭐⭐⭐⭐⭐ |
| Nano 3 MoE | Oct 2025 | ? | ? | ? | ? | ⭐⭐ |
| **Nano 9B v2** | **Oct 2025** | **9B** | **128K** | **~1500 tok/s** | **<50ms** | **⭐⭐⭐⭐⭐** |

---

## Security Changelog

### [1.0.0] - 2025-11-12
- **Added**: `.env` for API key management (gitignored)
- **Added**: `.env.example` template with no real secrets
- **Added**: Comprehensive `.gitignore` for credentials, keys, PEM files
- **Added**: `wipe()` method for zero-residue GPU memory cleanup
- **Security**: PHI anonymization before API calls (no PHI sent to NVIDIA)
- **Security**: Ephemeral processing (no disk writes of clinical data)

---

## Breaking Changes

None - this is the initial release.

---

## Notes

- This project follows semantic versioning
- All security issues should be reported to b@thegoatnote.com
- Model updates will be documented with performance comparisons
- HIPAA compliance maintained across all versions

