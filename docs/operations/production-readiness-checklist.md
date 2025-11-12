# GOAT Scribe Production Readiness Checklist (HIPAA + NVIDIA Healthcare Stack)

## 1. Secrets Hygiene
- Rotate all `nvapi-` keys via https://build.nvidia.com/settings/api-keys; update `~/.config/scribegoat/.env` and downstream secret managers.
- `chmod 600` secret files; verify no secrets committed (`git status --ignored`).
- Run `history -d` or clear shells after sourcing keys; confirm CI/CD injects keys from vault.

## 2. GPU Telemetry Capture
- `nvidia-smi --query-gpu=name,driver_version,memory.total,memory.used --format=csv -l 1 > logs/nvidia-smi-$(date +%Y%m%d).log &` for baseline.
- Archive Nsight profiling artifacts (`docs/benchmarks/ncu/latest/*.ncu-rep`, CSV, plots) per release.

## 3. PHI Redaction + Guardrails
- Execute `python -m goatnote_scribe.audit.phi_redaction --input samples/ --report logs/phi_audit.json`.
- Run `./deploy/verify.sh` and confirm guardrail violations trigger on unsafe doses (`morphine 50 mg`).
- Validate `GOATScribe.wipe()` is called in teardown (CI, Lambda, or cron) to purge cached transcripts.

## 4. Deployment Verification
- Smoke tests: `python -m goatnote_scribe.cli "Sample encounter"` and `python app.py` (Gradio UI).
- Container / serverless: rebuild NIM/Triton images with `requirements-nvidia-healthcare.txt`; document image digests.
- Ensure MONAI/TensorRT benchmark regression passes (`python scripts/monai_h100_benchmark.py --mode optimized`).

## 5. Compliance Logging
- Record reboot + driver updates in change log (`docs/operations/change-log.md`).
- Store Nsight Compute dataset metadata (`docs/benchmarks/ncu/**`) with release tags.
- Capture HIPAA access logs (Cloud provider / on-prem SIEM) for the period of deployment.

## 6. Sign-off
- Clinical safety review of generated notes.
- Security officer sign-off on key storage, PHI audit, and log retention.
- Final reminder: purge temporary profiling data containing patient-like prompts.
