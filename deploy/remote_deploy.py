#!/usr/bin/env python3
"""
Execute deployment on remote H100 via Jupyter kernel
"""
import subprocess
import sys

commands = [
    "cd ~/scribegoat",
    "git pull",
    "export NGC_API_KEY='nvapi-4d70_U8yEIN4Rx3b4W9rSAD307D_eTf36v0hTSmKw1pfYw'",
    "pip install -q -e .",
    "python -m spacy download en_core_web_lg",
    "python -c \"from goatnote_scribe import GOATScribe; s = GOATScribe(); r = s('Test'); print(f'✅ {len(r[\\\"note\\\"])} chars')\""
]

for cmd in commands:
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"❌ Command failed with code {result.returncode}")
        sys.exit(1)

print("✅ Deployment complete")
