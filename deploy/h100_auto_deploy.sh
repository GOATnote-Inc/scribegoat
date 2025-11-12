#!/bin/bash
set -e

echo "🚀 Auto-Deploying GOAT Scribe on H100"
echo "====================================="
echo ""

# Check if NGC_API_KEY is set
if [ -z "$NGC_API_KEY" ]; then
    echo "⚠️  NGC_API_KEY not set. Set it with:"
    echo "   export NGC_API_KEY='nvapi-YOUR-KEY'"
    echo ""
    read -p "Enter NGC API key now (or Ctrl+C to cancel): " NGC_API_KEY
    export NGC_API_KEY
fi

echo "✅ NGC API key set"
echo ""

# Update repo
echo "📥 Pulling latest code..."
git pull origin main 2>/dev/null || git pull

echo "✅ Code updated"
echo ""

# Install dependencies
echo "📦 Installing dependencies (this takes ~2 min)..."
pip install -q -e .
python -m spacy download en_core_web_lg > /dev/null 2>&1

echo "✅ Dependencies installed"
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    echo "🎮 GPU Info:"
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    echo ""
fi

# Run health check
echo "🏥 Running health check..."
python -c "
from goatnote_scribe import GOATScribe

try:
    scribe = GOATScribe()
    result = scribe('Test patient with fever, cough. BP 120/80, HR 85.')
    
    print(f'  ✅ Generated {len(result[\"note\"])} character note')
    print(f'  ✅ PHI removed: {result[\"phi_removed\"]}')
    print(f'  ✅ Guardrail safe: {result[\"guardrail_safe\"]}')
    print(f'  ✅ FHIR bundle: {\"resourceType\" in result[\"fhir_bundle\"]}')
    
except Exception as e:
    print(f'  ❌ Health check failed: {e}')
    exit(1)
"

echo ""
echo "====================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "====================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Launch Gradio UI:"
echo "   python app.py"
echo "   (Then add port 7860 in Brev dashboard)"
echo ""
echo "2. Profile H100 (requires NCU):"
echo "   ./deploy/profile.sh"
echo ""
echo "3. Run verification tests:"
echo "   ./deploy/verify.sh"
echo ""
echo "4. Test CLI:"
echo "   python -m goatnote_scribe.cli 'Patient with chest pain...'"
echo ""

