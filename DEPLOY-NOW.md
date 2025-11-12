# Deploy to Your H100 Instance NOW

**Your H100 is running. Let's get results.**

---

## Current Status

✅ **Instance**: scribe (NCA-d3fa-18703)  
✅ **GPU**: NVIDIA H100 (80GB)  
✅ **Status**: Running  
✅ **Code**: https://github.com/GOATnote-Inc/scribegoat  

---

## Option 1: Brev CLI (Recommended)

### Step 1: Authenticate
```bash
brev login --token YOUR_BREV_TOKEN_HERE
```

### Step 2: Open in Cursor
```bash
brev open scribe cursor
```

### Step 3: Deploy in Terminal
```bash
cd ~
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat
export NGC_API_KEY="nvapi-YOUR-NGC-KEY"
./deploy/quick_start.sh
```

---

## Option 2: Direct SSH

### Step 1: Shell into instance
```bash
brev shell scribe
```

### Step 2: Clone and deploy
```bash
cd ~
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat

# Set NGC API key
export NGC_API_KEY="nvapi-YOUR-NGC-KEY"

# Deploy (takes ~3 minutes)
./deploy/quick_start.sh
```

### Step 3: Verify
```bash
./deploy/verify.sh
```

---

## Option 3: Jupyter Notebook (Port 8888)

**Your Brev instance has Jupyter running**: https://ju9yhn0-x34a0tOc.brev.dev

### In Jupyter Terminal:
```bash
cd ~
git clone https://github.com/GOATnote-Inc/scribegoat.git
cd scribegoat
export NGC_API_KEY="nvapi-YOUR-NGC-KEY"
pip install -e .
python -m spacy download en_core_web_lg
```

### Test in Notebook:
```python
from goatnote_scribe import GOATScribe

scribe = GOATScribe()
result = scribe("""
35M with chest pain, 2h duration, radiating to left arm, diaphoretic.
Denies SOB, N/V. 
PMH: HTN, hyperlipidemia.
Vitals: BP 145/90, HR 98, RR 16, SpO2 99% RA.
""")

print(result['note'])
print(f"\n✅ PHI removed: {result['phi_removed']}")
print(f"✅ Guardrail safe: {result['guardrail_safe']}")
```

---

## After Deployment: Profile H100

### Run NCU profiling
```bash
cd ~/scribegoat
./deploy/profile.sh
```

**This generates**: `ncu_goat_scribe.ncu-rep` with:
- SM Efficiency (target: >80%)
- Memory Bandwidth (target: >2 TB/s)
- Tensor Core Utilization (target: >70%)

### Add results to repo
```bash
git add ncu_goat_scribe.ncu-rep
git commit -m "perf: H100 NCU profile - actual performance data"
git push
```

---

## Launch Public UI

### Start Gradio
```bash
cd ~/scribegoat
python app.py
```

### Get Public URL
From Brev dashboard, add port 7860:
- Go to "Share a Service"
- Port: 7860
- Get public URL like: https://xxx.brev.dev

---

## Expected Results (H100 80GB)

After deployment, you should see:

```
✅ NGC API key found
✅ Python version OK
✅ Dependencies installed
✅ Health check passed

🎮 GPU: NVIDIA H100 (80GB)

✅ GOAT Scribe is ready!
```

**Performance targets**:
- Draft generation: <2s
- Critique pass: <2s  
- Total pipeline: <5s
- Throughput: 1500+ tok/s

---

## Troubleshooting

### "NGC_API_KEY not set"
```bash
export NGC_API_KEY="nvapi-YOUR-KEY"
echo "export NGC_API_KEY=$NGC_API_KEY" >> ~/.bashrc
```

### "spaCy model not found"
```bash
python -m spacy download en_core_web_lg
```

### Check GPU
```bash
nvidia-smi
```

Should show: NVIDIA H100 80GB with driver 535+

---

## Next Steps After Deployment

1. ✅ **Verify**: `./deploy/verify.sh`
2. 📊 **Profile**: `./deploy/profile.sh`
3. 🌐 **Launch UI**: `python app.py`
4. 📈 **Add NCU results**: Commit and push performance data
5. 🚀 **Share**: Get public URL from Brev dashboard

---

**Time to results**: 5 minutes  
**Repository**: https://github.com/GOATnote-Inc/scribegoat  
**Contact**: b@thegoatnote.com

