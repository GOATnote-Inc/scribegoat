#!/bin/bash
set -e

echo "🚀 GOAT Scribe Quick Start - NVIDIA H100 Deployment"
echo "=================================================="
echo ""

# Check for NGC API key
if [ -z "$NGC_API_KEY" ]; then
    echo "❌ NGC_API_KEY not set"
    echo ""
    echo "Get your key: https://org.ngc.nvidia.com/setup/api-key"
    echo "Then run: export NGC_API_KEY='nvapi-YOUR-KEY-HERE'"
    exit 1
fi

echo "✅ NGC API key found"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "🐍 Python version: $PYTHON_VERSION"

if (( $(echo "$PYTHON_VERSION < 3.10" | bc -l) )); then
    echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version OK"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -e .
python -m spacy download en_core_web_lg > /dev/null 2>&1

echo "✅ Dependencies installed"
echo ""

# Check GPU
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    echo "🎮 GPU: $GPU_NAME"
    echo ""
else
    echo "⚠️  No GPU detected (will use CPU - slower)"
    echo ""
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    echo "NGC_API_KEY=$NGC_API_KEY" > .env
    chmod 600 .env
    echo "✅ .env created"
    echo ""
fi

# Run health check
echo "🏥 Running health check..."
python -c "
from goatnote_scribe import GOATScribe

try:
    scribe = GOATScribe()
    result = scribe('Test patient with fever')
    assert 'note' in result
    assert 'guardrail_safe' in result
    print('✅ Health check passed')
except Exception as e:
    print(f'❌ Health check failed: {e}')
    exit(1)
"

echo ""
echo "=================================================="
echo "✅ GOAT Scribe is ready!"
echo "=================================================="
echo ""
echo "🌐 Launch Gradio UI:"
echo "   python app.py"
echo ""
echo "💻 CLI usage:"
echo "   python -m goatnote_scribe.cli 'Patient presents with...'"
echo ""
echo "📊 Profile with NCU:"
echo "   ./deploy/profile.sh"
echo ""
echo "📖 Full docs: ./deploy/DEPLOY.md"
echo ""

