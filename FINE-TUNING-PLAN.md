# Emergency Medicine Fine-Tuning Plan

**Owner**: Brandon Dent, MD (Emergency Medicine)  
**Goal**: Specialty fine-tuning for ED-specific medical scribe  
**Status**: Phase 1 (Foundation) - Ready for Phase 2 (Data Collection)

---

## Why Emergency Medicine Needs Specialty Fine-Tuning

### Generic Medical Scribe ❌
- Writes generic SOAP notes for any specialty
- No understanding of ED-specific workflows
- Misses critical ED rule-outs (MI, PE, stroke, sepsis)
- Doesn't understand triage urgency
- No grasp of ED medical-legal requirements

### ED-Specialized Scribe ✅
- **Time-critical**: Understands 3-minute vs 30-minute patients
- **High-risk rule-outs**: Always documents MI, PE, stroke, sepsis considerations
- **Triage-aware**: ESI 1 (resuscitation) vs ESI 5 (non-urgent) documentation
- **Medical-legal**: Discharge instructions, return precautions, shared decision-making
- **Protocol-aware**: ACLS, ATLS, sepsis, stroke protocols with correct steps
- **ED terminology**: "ED course", "disposition", "medical decision making"

---

## Phase 1: Foundation (COMPLETE ✅)

### 1.1 Base Architecture
- ✅ Nemotron Nano 9B v2 (October 2025) - 6x throughput, 128K context
- ✅ NVIDIA NIM API integration
- ✅ HIPAA-compliant PHI detection (Presidio)
- ✅ FHIR R4 export to GCP Healthcare API
- ✅ MONAI Core integration for medical AI standards

### 1.2 ED Guardrails (CRITICAL)
- ✅ Vital signs validation (HR, BP, RR, Temp, SpO2, GCS)
- ✅ Medication dosage limits (morphine, fentanyl, etc.)
- ✅ ACLS/Trauma protocol warnings
- ✅ 12-section ED note structure

### 1.3 ED-Specific Prompts
- ✅ ED system prompt with all required sections
- ✅ Medical Decision Making emphasis
- ✅ High-risk rule-outs reminder
- ✅ Disposition documentation (discharge vs admit)

---

## Phase 2: Data Collection (IN PROGRESS 🚧)

### 2.1 Training Data Requirements

**Target**: 10,000 ED cases minimum for effective fine-tuning

#### Data Sources
1. **De-identified ED notes** (from your clinical experience)
   - Chief complaints: chest pain, abdominal pain, headache, trauma, etc.
   - Full ED course with vitals, medications, procedures
   - Medical decision making with differential diagnosis
   - Disposition with rationale

2. **Synthetic ED cases** (generated with validation)
   - Create using Nemotron Nano 9B v2 base model
   - Validate with ED guardrails
   - Review by ED physician (you)

3. **Public ED datasets**
   - MIMIC-IV-ED (emergency department data)
   - PhysioNet clinical databases
   - Must be properly de-identified and HIPAA-compliant

#### Data Format

```json
{
  "prompt": "35yo M with chest pain...",
  "completion": "CHIEF COMPLAINT\nChest pain...\n\nHISTORY OF PRESENT ILLNESS\n...\n\nMEDICAL DECISION MAKING\nDifferential: ACS vs PE vs aortic dissection...",
  "metadata": {
    "chief_complaint": "chest pain",
    "esi_level": 2,
    "disposition": "admit",
    "protocols": ["STEMI", "ACLS"]
  }
}
```

### 2.2 Data Quality Control

**Quality Gates** (automated with guardrails):
- ✅ All 12 ED sections present
- ✅ No guardrail violations (vitals, meds, protocols)
- ✅ Medical Decision Making section robust
- ✅ Disposition documented with rationale
- ✅ PHI completely removed

### 2.3 Data Labeling & Review

**Physician Review** (Brandon Dent, MD):
- Sample 10% of cases (1000 notes)
- Check for medical accuracy
- Verify ED-specific documentation standards
- Flag any medical errors or omissions

---

## Phase 3: Fine-Tuning Strategy (PLANNED 📋)

### 3.1 NVIDIA NeMo Framework

**Why NeMo?**
- Native NVIDIA integration (built for H100)
- Support for Nemotron models
- Efficient parameter-efficient fine-tuning (PEFT)
- Multi-GPU distributed training

#### Fine-Tuning Method: LoRA (Low-Rank Adaptation)

**LoRA Benefits**:
- **Efficient**: Only train 0.1% of parameters (9M params instead of 9B)
- **Fast**: 10x faster training, 3x less memory
- **Modular**: Can swap LoRA adapters for different specialties
- **Preserves base model**: Nemotron Nano 9B v2 reasoning intact

**LoRA Configuration**:
```python
# NeMo LoRA config for ED fine-tuning
lora_config = {
    "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],  # Attention layers
    "r": 32,  # LoRA rank (higher = more capacity, slower)
    "lora_alpha": 64,  # Scaling factor
    "lora_dropout": 0.05,  # Regularization
}
```

### 3.2 Training Configuration

**Hardware**: 1x H100 (80GB) - Sufficient for LoRA fine-tuning

**Training Hyperparameters**:
```yaml
model: nvidia/nemotron-nano-9b-v2
method: lora
rank: 32
alpha: 64

# Training
batch_size: 4
gradient_accumulation: 8  # Effective batch size = 32
learning_rate: 2e-4
warmup_steps: 100
max_steps: 5000
weight_decay: 0.01

# Optimization (H100-specific)
precision: bf16  # H100 native precision
flash_attention: true  # FlashAttention-3
gradient_checkpointing: true
optimizer: adamw_torch_fused  # H100-optimized AdamW

# Evaluation
eval_steps: 500
save_steps: 500
logging_steps: 10
```

**Expected Training Time**: 
- 10,000 cases × 5 epochs = 50,000 examples
- ~8-12 hours on H100 with LoRA

### 3.3 Evaluation Metrics

#### Automated Metrics
1. **Medical Accuracy** (via guardrails)
   - 0 critical violations (vitals, meds, protocols)
   - Target: 100% guardrail compliance

2. **Completeness** (12 ED sections)
   - All required sections present
   - Target: 100% completeness

3. **ROUGE-L** (text similarity to reference notes)
   - Target: >0.60 (clinical note generation benchmark)

4. **BERTScore** (semantic similarity)
   - Target: >0.85

#### Clinical Evaluation (Brandon Dent, MD)
1. **Medical Decision Making Quality**
   - Differential diagnosis comprehensive?
   - Risk stratification appropriate?
   - Disposition reasoning sound?

2. **ED-Specific Standards**
   - High-risk rule-outs documented?
   - Return precautions appropriate?
   - Medical-legal requirements met?

3. **Usability**
   - Would you trust this note in your ED?
   - Does it save time vs manual documentation?
   - Would you show this to NVIDIA for director role?

---

## Phase 4: Deployment & Iteration (FUTURE 🔮)

### 4.1 H100 Deployment
- Deploy fine-tuned model to Brev H100 instance
- Serve via NVIDIA Triton Inference Server
- Public API endpoint for beta testing

### 4.2 Beta Testing
- 5-10 ED physicians (early adopters)
- Real clinical cases (de-identified)
- Feedback loop for continuous improvement

### 4.3 Continuous Fine-Tuning
- Collect feedback from beta users
- Retrain monthly with new cases
- Track metrics over time (accuracy, safety, usability)

---

## Current Status & Next Steps

### ✅ COMPLETE (Phase 1)
- Base architecture with Nemotron Nano 9B v2
- ED guardrails with safety validations
- HIPAA-compliant PHI detection
- FHIR R4 integration
- ED-specific prompts and structure

### 🚧 IN PROGRESS (Phase 2)
- **Data collection**: Need 10,000 ED cases
- **Options**:
  1. De-identify your clinical notes (HIPAA-compliant process)
  2. Use MIMIC-IV-ED public dataset (requires PhysioNet access)
  3. Generate synthetic cases with validation

### 📋 NEXT IMMEDIATE STEPS

1. **Set up MIMIC-IV-ED access** (1 week)
   - Request access: https://physionet.org/content/mimic-iv-ed/
   - Download ED notes subset
   - Verify de-identification

2. **Prepare training data** (2 weeks)
   - Parse MIMIC-IV-ED to required format
   - Run through guardrails for quality control
   - Split: 80% train, 10% validation, 10% test

3. **Set up NeMo training environment** (1 week)
   - Install NeMo 25.09 on H100
   - Configure LoRA fine-tuning
   - Test training loop with 100 examples

4. **Full fine-tuning run** (1-2 days)
   - Train on 10,000 cases
   - Monitor metrics
   - Evaluate on test set

5. **Clinical validation** (1 week)
   - You review 100 generated notes
   - Check medical accuracy
   - Assess usability for real ED work

---

## Why This Matters for NVIDIA Director Role

### Technical Excellence
- ✅ **H100 Optimization**: LoRA fine-tuning with FlashAttention-3, BF16 precision
- ✅ **NVIDIA Stack**: NeMo, NIM, Triton, MONAI
- ✅ **Production-Ready**: Guardrails, monitoring, HIPAA compliance

### Healthcare AI Expertise
- ✅ **Clinical Validation**: Built by ED physician, for ED physicians
- ✅ **Safety-First**: Medical-legal guardrails, not just accuracy
- ✅ **Real-World Impact**: Solves actual ED documentation burden

### Leadership & Vision
- ✅ **Specialty-Specific**: Not generic, but tailored to high-stakes specialty
- ✅ **Scalable**: LoRA adapters → multi-specialty (EM, cards, neuro, etc.)
- ✅ **Open Source**: Democratizes healthcare AI for all specialties

---

## Questions for Brandon Dent, MD

1. **Data Source**: Which path for training data?
   - Option A: Your de-identified clinical notes (faster, higher quality)
   - Option B: MIMIC-IV-ED (public, takes longer to access)
   - Option C: Synthetic + validation (can start immediately)

2. **Chief Complaints Priority**: Which CC should we prioritize?
   - High-volume: Chest pain, abdominal pain, headache
   - High-stakes: Trauma, stroke, STEMI, sepsis
   - Both?

3. **Evaluation Standards**: What's your bar for "good enough to use in ED"?
   - 90% accuracy?
   - 95% accuracy?
   - 100% safety (no guardrail violations)?

4. **Timeline**: When do you need this for NVIDIA director application?
   - 1 month? (rush, may sacrifice quality)
   - 3 months? (optimal, full fine-tuning + validation)
   - 6 months? (research-grade, publish paper)

---

**Author**: Brandon Dent, MD - Emergency Medicine  
**Contact**: b@thegoatnote.com  
**Repository**: https://github.com/GOATnote/scribegoat

