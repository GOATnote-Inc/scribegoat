#!/bin/bash
set -e

echo "🔍 GOAT Scribe Verification"
echo "==========================="
echo ""

# Test 1: Import check
echo "✓ Test 1: Python imports..."
python -c "
from goatnote_scribe import GOATScribe, FHIRExporter, EDGuardrails
print('  ✅ All imports successful')
"

# Test 2: Basic generation
echo "✓ Test 2: Basic note generation..."
python -c "
from goatnote_scribe import GOATScribe

scribe = GOATScribe()
result = scribe('Test patient with fever')

assert 'note' in result, 'Missing note'
assert 'guardrail_safe' in result, 'Missing guardrail_safe'
assert 'fhir_bundle' in result, 'Missing FHIR bundle'
print(f'  ✅ Generated {len(result[\"note\"])} character note')
"

# Test 3: Guardrails trigger
echo "✓ Test 3: Guardrails detection..."
python -c "
from goatnote_scribe import GOATScribe

scribe = GOATScribe()
result = scribe('Patient with HR 350 BPM, morphine 50mg IV')

assert not result['guardrail_safe'], 'Guardrails should have triggered'
assert result['guardrail_violations'] > 0, 'Should have violations'
print(f'  ✅ Detected {result[\"guardrail_violations\"]} violations correctly')
"

# Test 4: CLI works
echo "✓ Test 4: CLI functionality..."
output=$(python -m goatnote_scribe.cli "Test patient" 2>&1)
if echo "$output" | grep -q "Generated"; then
    echo "  ✅ CLI working"
else
    echo "  ❌ CLI failed"
    exit 1
fi

# Test 5: GPU detection (if available)
echo "✓ Test 5: GPU detection..."
if command -v nvidia-smi &> /dev/null; then
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    echo "  ✅ GPU: $GPU_NAME"
else
    echo "  ⚠️  No GPU detected (will use CPU)"
fi

echo ""
echo "==========================="
echo "✅ All verification tests passed"
echo "==========================="
echo ""
echo "Next steps:"
echo "  - Launch UI: python app.py"
echo "  - Profile H100: ./deploy/profile.sh"
echo "  - View docs: cat deploy/DEPLOY.md"
echo ""

