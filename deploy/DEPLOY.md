# Deploy GOAT Scribe to H100 (< 15 minutes)

**Goal**: Functional deployment showcasing NVIDIA's latest stack for startup evaluation.

---

## Prerequisites (< 5 min)

1. **Brev Account**: https://brev.dev (sign in with NVIDIA NGC)
2. **NGC API Key**: https://org.ngc.nvidia.com/setup/api-key
3. **GCP Project** (optional): For FHIR integration

---

## Option 1: One-Command Deploy (RECOMMENDED)

```bash
# Clone and deploy
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat
./deploy/quick_start.sh
```

**What this does:**
1. Checks for NGC API key
2. Installs dependencies
3. Launches Gradio UI on port 7860
4. Prints public URL via Brev tunnel
5. Runs basic health check

**Time**: 5 minutes

---

## Option 2: Manual Deploy (for customization)

### Step 1: Launch H100 Instance

```bash
# Brev H100 (80GB)
brev create h100 --name goat-scribe --region us-central1

# SSH into instance
brev shell goat-scribe
```

### Step 2: Install Stack

```bash
# Clone repo
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat

# Install dependencies
pip install -e .

# Download spaCy model for Presidio
python -m spacy download en_core_web_lg

# Set NGC API key
export NGC_API_KEY="nvapi-YOUR-KEY-HERE"
```

### Step 3: Run Scribe

```bash
# Launch Gradio UI
python app.py

# Or use CLI
python -m goatnote_scribe.cli "Patient presents with chest pain..."
```

### Step 4: Get Public URL

```bash
# Brev automatically creates public URL
brev urls

# Or manual port forward
ssh -L 7860:localhost:7860 user@brev-instance
# Visit: http://localhost:7860
```

**Time**: 10 minutes

---

## Option 3: Docker Deploy (production)

```bash
# Build container
docker build -t goat-scribe:latest .

# Run with GPU
docker run --gpus all \
  -e NGC_API_KEY=$NGC_API_KEY \
  -p 7860:7860 \
  goat-scribe:latest
```

**Time**: 8 minutes (including build)

---

## Verification

### Test 1: Basic Generation

```bash
curl -X POST http://localhost:7860/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "35M with chest pain, 2h duration, radiating to left arm. BP 130/85, HR 95, RR 18, SpO2 98% RA."
  }'
```

**Expected**: JSON with `note`, `phi_removed`, `guardrail_safe`, `fhir_bundle`

### Test 2: Guardrails Trigger

```bash
curl -X POST http://localhost:7860/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Patient with HR 350 BPM, gave morphine 50mg IV"
  }'
```

**Expected**: `guardrail_safe: false` with violation warnings

### Test 3: FHIR Export (optional)

```bash
# Set GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Test export
python -c "
from goatnote_scribe import GOATScribe, FHIRExporter
scribe = GOATScribe()
exporter = FHIRExporter()
result = scribe('Test patient...')
response = exporter.upload_bundle(result['fhir_bundle'])
print(f'Uploaded: {response}')
"
```

---

## Troubleshooting

### Issue: "NGC_API_KEY not set"
```bash
export NGC_API_KEY="nvapi-YOUR-KEY-HERE"
echo "export NGC_API_KEY=$NGC_API_KEY" >> ~/.bashrc
```

### Issue: "spaCy model not found"
```bash
python -m spacy download en_core_web_lg
```

### Issue: "CUDA out of memory"
```bash
# Check GPU memory
nvidia-smi

# Restart Python process to clear cache
```

### Issue: "Port 7860 already in use"
```bash
# Find process
lsof -i :7860

# Kill it
kill -9 <PID>

# Or use different port
python app.py --port 7861
```

---

## Next Steps

Once deployed:
1. **Profile with NCU**: See `deploy/PROFILE.md`
2. **CI/CD Setup**: See `deploy/CICD.md`
3. **FHIR Integration**: See `docs/FHIR.md`

---

**Support**: b@thegoatnote.com  
**Issues**: https://github.com/GOATnote-Inc/scribegoat/issues

