# NVIDIA Healthcare AI Showcase (November 2025)

> Curated by GOATnote for founders building regulated clinical AI on NVIDIA H100/H200 platforms.

This playbook consolidates the latest open-source NVIDIA healthcare AI tooling into a single reference environment. Pair it with the `deploy/` scripts to bootstrap a HIPAA-aware stack in under an hour.

---

## 1. Core Platform

| Component | Version | Install Command / Notes |
|-----------|---------|-------------------------|
| **CUDA Toolkit** | 13.0.2 (Update 2) | `sudo apt-get install cuda-toolkit-13-0` |
| **NVIDIA Driver** | 580.105.08 | `sudo apt-get install nvidia-driver-580` (reboot required) |
| **cuDNN** | 10.1 for CUDA 13 | `sudo apt-get install libcudnn10-cuda-13 libcudnn10-dev-cuda-13` |
| **TensorRT** | 11.0.1 | `sudo apt-get install tensorrt=11.0.1* tensorrt-dev=11.0.1*` |
| **CUTLASS** | 4.3.0 | `git clone --depth 1 --branch v4.3.0 https://github.com/NVIDIA/cutlass.git && cmake .. && sudo make install` |
| **FlashAttention** | 3.0.1 | `pip install flash-attn==3.0.1 --no-build-isolation` |
| **Triton Compiler** | 3.2.1 | `pip install triton==3.2.1` |

**Validation**
```bash
nvcc --version           # confirms CUDA 13.0
nvidia-smi               # driver ≥ 580
python - <<'PY'
import torch
print(torch.__version__)
print(torch.cuda.is_available(), torch.version.cuda)
PY
```

---

## 2. NVIDIA Healthcare SDKs

| Toolkit | Version | Purpose | Install |
|---------|---------|---------|---------|
| **MONAI** | 1.5.1.dev (weekly) | Imaging, segmentation, FHIR export glue | `pip install --pre monai-weekly --upgrade` |
| **Clara Holoscan** | 3.0.1 | Edge streaming, surgical guidance apps | `pip install --extra-index-url https://pypi.nvidia.com nvidia-clara-holoscan==3.0.1 nvidia-dali-cuda130 nvidia-nvimgcodec-cu13` |
| **NeMo Toolkit** | 25.09.1 | LLM/Speech/RAG fine-tuning | `pip install --extra-index-url https://pypi.nvidia.com "nemo_toolkit[all]==25.09.1" nvidia-modelopt==0.21.1 nvidia-pytriton` |
| **TensorRT-LLM** | 0.17.1 | Optimized generative inference | `pip install --extra-index-url https://pypi.nvidia.com tensorrt_llm==0.17.1` |
| **NIM Client SDKs** | OpenAI 1.56.0, LangChain NVIDIA 0.3.6 | Programmatic access to hosted Nemotron family | `pip install openai==1.56.0 langchain-nvidia-ai-endpoints==0.3.6 httpx==0.28.1` |
| **HIPAA Guardrails** | Presidio 2.2.360 | PHI detection & anonymization | `pip install presidio-analyzer==2.2.360 presidio-anonymizer==2.2.360 spacy==3.8.9 && python -m spacy download en_core_web_lg en_core_web_trf` |

> **Tip:** Keep these NVIDIA-only wheels in a dedicated requirements file. Use `pip install -r requirements-nvidia-healthcare.txt --extra-index-url https://pypi.nvidia.com --upgrade`.

---

## 3. Nemotron Model Portfolio

| Use Case | Model ID (Integrate API) | Notes |
|----------|-------------------------|-------|
| Clinical text generation (default) | `nvidia/llama-3.1-nemotron-nano-8b-v1` | 128K context, sub-second first token on H100 |
| Multimodal chart summarization | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | Accepts radiology images & vitals dashboards |
| High-accuracy audits | `nvidia/llama-3.3-nemotron-super-49b-v1.5` | Use in critique mode for QA or double-read |
| Safety guard | `nvidia/llama-3.1-nemotron-safety-guard-8b-v3` | Autonomous guardrail pass for ED notes |

Example request:
```bash
curl -s https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NGC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "model": "nvidia/llama-3.1-nemotron-nano-8b-v1",
        "messages": [
          {"role": "system", "content": "Emergency-medicine specialist scribe."},
          {"role": "user", "content": "Describe STEMI best-practice checklist."}
        ],
        "max_tokens": 256,
        "temperature": 0.1
      }'
```

---

## 4. Repository Layout Enhancements

- `deploy/h100_auto_deploy.sh` – bootstrap CUDA 13 + driver + spaCy models.
- `requirements-nvidia-healthcare.txt` – installable bundle for the table above.
- `src/goatnote_scribe/guardrails.py` – ED vitals/medication guardrails (hook into NeMo guardrails via REST).
- `docs/` – architecture diagrams, compliance checklist, profiling cheatsheets.

---

## 5. Post-Install Compliance Checklist

- [ ] Rotate & store `NGC_API_KEY` in your secrets manager (not shell history).
- [ ] Run `python -m goatnote_scribe.cli "Sample encounter"` and confirm `guardrail_safe=True`.
- [ ] Execute `python -m goatnote_scribe.scribe --self-test` (see CLI help) to log PHI detections into `logs/audit/`.
- [ ] `nvidia-smi` succeeds after reboot and reports driver `580.105.08`.
- [ ] Nsight Systems/Compute launch successfully (`nsys status`, `ncu --version`).
- [ ] Document GPU memory wiping policy (call `GOATScribe.wipe()` or `torch.cuda.empty_cache()`).

---

## 6. Useful References

- [CUDA Toolkit 13.0 Documentation](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)
- [NVIDIA Healthcare & Life Sciences SDK Catalog](https://www.nvidia.com/en-us/industries/healthcare-life-sciences/)
- [NVIDIA NIM Documentation](https://docs.nvidia.com/nim)
- [MONAI Tutorials](https://monai.io/)
- [Clara Holoscan Samples](https://developer.nvidia.com/holoscan-sdk)
- [NeMo User Guide](https://docs.nvidia.com/nemo)
- [CUTLASS Samples](https://github.com/NVIDIA/cutlass/tree/main/examples)

---

**Questions or contributions?** Open an issue or reach out to `engineering@goatnote.com` with compliance-focused improvements. We are especially interested in community PRs that pair MONAI imaging pipelines with GOAT Scribe’s FHIR exporter for holistic ED workflows.
