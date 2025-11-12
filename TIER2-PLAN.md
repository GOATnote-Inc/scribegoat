# Tier 2 Implementation Plan

**Status**: 📋 **PLANNED** (Not Yet Executed)  
**Estimated Time**: 2-3 hours  
**Prerequisites**: Tier 1 complete ✅

---

## Overview

Tier 2 adds production-grade testing and CI/CD infrastructure to the clean Tier 1 codebase.

**Goal**: Transform from "working code" to "director-level engineering"

---

## Tier 2 Components

### 1. Comprehensive Test Suite (60-90 min)

**Files to Create:**
```
tests/
├── __init__.py
├── conftest.py (pytest fixtures)
├── test_scribe.py (core scribe tests)
├── test_fhir.py (FHIR export tests)
├── test_config.py (configuration tests)
└── test_phi_detection.py (HIPAA critical)
```

#### test_scribe.py
**What it tests:**
- ✅ Scribe initialization with valid config
- ✅ PHI detection accuracy (18 HIPAA identifiers)
- ✅ SOAP note generation (mocked API calls)
- ✅ 2-pass generation (draft + critique)
- ✅ `/think` token injection when `enable_reasoning=True`
- ✅ Memory cleanup via `wipe()`
- ✅ Error handling (empty prompt, API failures)

**Example tests:**
```python
def test_phi_detection(scribe):
    """Test HIPAA-critical PHI detection"""
    text = "Patient John Doe, DOB 1/1/1980, SSN 123-45-6789"
    result = scribe(text)
    assert result['phi_removed'] >= 3  # Name, DOB, SSN
    
def test_reasoning_toggle(config):
    """Test /think token injection"""
    config.enable_reasoning = True
    scribe = GOATScribe(config)
    # Mock API call, verify /think in request
```

#### test_fhir.py
**What it tests:**
- ✅ FHIR R4 bundle creation
- ✅ Bundle validation (resourceType, entries)
- ✅ GCP Healthcare API upload (mocked)
- ✅ Patient retrieval (mocked)
- ✅ Document search (mocked)
- ✅ Error handling (auth failures, invalid bundles)

#### test_config.py
**What it tests:**
- ✅ Config loading from environment
- ✅ Config validation (missing API key raises error)
- ✅ Default values
- ✅ Custom config overrides

#### test_phi_detection.py (HIPAA Critical)
**What it tests:**
- ✅ All 18 HIPAA identifiers detected
- ✅ Names (first, last, full)
- ✅ Dates (DOB, admission, discharge)
- ✅ SSN, MRN, account numbers
- ✅ Phone, fax, email
- ✅ Addresses, ZIP codes
- ✅ Biometric identifiers

**This is the most important test file** - HIPAA compliance depends on it.

---

### 2. CI/CD Pipeline (30-45 min)

**Files to Create:**
```
.github/
└── workflows/
    ├── ci.yml (main CI pipeline)
    └── security.yml (secret scanning)
```

#### ci.yml
**What it does:**
```yaml
on: [push, pull_request]

jobs:
  lint:
    - black --check src/
    - ruff check src/
    - mypy src/
    
  test:
    - pytest tests/ --cov=src/goatnote_scribe
    - Upload coverage to Codecov
    
  security:
    - bandit -r src/
    - safety check (dependency vulnerabilities)
```

**Benefits:**
- Every commit is linted
- Every PR must pass tests
- Security issues caught automatically
- Shows engineering maturity

---

### 3. Pre-commit Hooks (15-30 min)

**Files to Create:**
```
.pre-commit-config.yaml
```

**What it does:**
- Detect secrets before commit
- Run black formatter
- Run ruff linter
- Check for large files
- Check YAML/JSON syntax

**Benefit:** Prevents accidental secret commits to public repos.

---

### 4. Example Notebook (30 min)

**Files to Create:**
```
examples/
└── getting_started.ipynb
```

**What it shows:**
- Installation
- Basic usage
- PHI detection demo
- FHIR export example
- Error handling
- Memory cleanup

**Benefit:** Shows it actually works, helps users get started.

---

### 5. Updated Jupyter Demo (15 min)

**Files to Update:**
```
examples/GOAT_Scribe_Demo.ipynb (from old repo)
```

**Changes needed:**
- Update imports: `from goatnote_scribe import GOATScribe`
- Remove references to non-existent `start_nim.sh`
- Update to Nemotron Nano 9B v2
- Add `/think` reasoning example
- Fix FHIR export to use new `FHIRExporter` class

---

## Implementation Order

### Phase 1: Testing (Execute First)
1. Create `tests/conftest.py` with pytest fixtures
2. Create `tests/test_config.py` (simplest, validates structure)
3. Create `tests/test_phi_detection.py` (HIPAA critical)
4. Create `tests/test_scribe.py` (core functionality)
5. Create `tests/test_fhir.py` (integration)

**Verify:** `pytest tests/` passes (will use mocked API calls)

### Phase 2: CI/CD (Execute Second)
1. Create `.github/workflows/ci.yml`
2. Create `.github/workflows/security.yml`
3. Create `.pre-commit-config.yaml`

**Verify:** Push to GitHub, watch Actions run

### Phase 3: Examples (Execute Third)
1. Create `examples/getting_started.ipynb`
2. Update `examples/GOAT_Scribe_Demo.ipynb` from old repo

**Verify:** Notebooks run end-to-end

---

## Success Criteria

After Tier 2 completion:

✅ **Tests**
- [ ] 80%+ code coverage
- [ ] All 18 HIPAA identifiers tested
- [ ] Mock API calls (no real API keys needed for tests)
- [ ] pytest runs in <30 seconds

✅ **CI/CD**
- [ ] GitHub Actions passing on all commits
- [ ] Linting enforced (black, ruff, mypy)
- [ ] Security scanning (bandit, safety)
- [ ] Pre-commit hooks installed and working

✅ **Documentation**
- [ ] Example notebooks run successfully
- [ ] README has quick start example
- [ ] CHANGELOG documents all decisions

✅ **Git History**
- [ ] Clean commits: "test:", "ci:", "docs:" prefixes
- [ ] No "fix fix fix" commits
- [ ] Professional progression

---

## What This Achieves

**Before Tier 2 (Current State):**
- Working code ✅
- Clean architecture ✅
- Good documentation ✅
- Professional git history ✅
- **But**: No tests, no CI/CD, no automation

**After Tier 2:**
- Working code ✅
- Clean architecture ✅
- Good documentation ✅
- Professional git history ✅
- **Comprehensive tests** ✅
- **CI/CD pipeline** ✅
- **Secret detection** ✅
- **Example notebooks** ✅

**Result**: Director-level portfolio piece that demonstrates:
1. Technical skill (code quality)
2. Engineering maturity (tests, CI/CD)
3. Security awareness (pre-commit hooks, secret scanning)
4. Documentation (README, examples, CHANGELOG)
5. HIPAA understanding (18 identifier testing)

---

## Estimated Timeline

| Phase | Task | Time | Cumulative |
|-------|------|------|------------|
| 1 | Test fixtures | 15 min | 0:15 |
| 1 | Config tests | 15 min | 0:30 |
| 1 | PHI detection tests | 30 min | 1:00 |
| 1 | Scribe tests | 30 min | 1:30 |
| 1 | FHIR tests | 15 min | 1:45 |
| 2 | CI/CD workflows | 30 min | 2:15 |
| 2 | Pre-commit hooks | 15 min | 2:30 |
| 3 | Example notebooks | 45 min | 3:15 |

**Total**: ~3 hours for complete Tier 2

---

## Risk Mitigation

**What could go wrong:**
1. **Tests fail**: Mock API calls properly, don't rely on real NGC key
2. **CI/CD fails**: Test locally first with `act` (GitHub Actions simulator)
3. **Pre-commit breaks workflow**: Make hooks optional, document override
4. **Notebooks don't run**: Test in clean venv, pin all dependencies

**Mitigation Strategy:**
- Commit after each phase (tests, CI/CD, examples)
- Verify locally before pushing to GitHub
- Use pytest-mock for all API calls
- Keep it simple (no complex fixtures or mocking)

---

## Files to Transfer from Old Repo

**YES:**
- `examples/GOAT_Scribe_Demo.ipynb` (update imports)
- `CONTRIBUTING.md` (as-is)
- `SECURITY.md` (as-is)

**NO:**
- All status/deployment markdown files
- Ad-hoc test scripts
- Deployment scripts

---

## Approval Checklist

Before proceeding with Tier 2 execution, confirm:

- [ ] Tier 1 code is correct and working
- [ ] Model choice (Nemotron Nano 9B v2) is final
- [ ] Documentation (README, CHANGELOG) is accurate
- [ ] Implementation plan is clear and achievable
- [ ] Success criteria are well-defined
- [ ] Timeline is realistic

**Once approved, Tier 2 will be executed in order: Tests → CI/CD → Examples**

---

**Status**: 📋 Awaiting approval to proceed with Tier 2 implementation.

