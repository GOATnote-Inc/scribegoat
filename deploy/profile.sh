#!/bin/bash
set -e

echo "🔬 NVIDIA H100 Profiling - GOAT Scribe"
echo "======================================"
echo ""

# Check for NCU
if ! command -v ncu &> /dev/null; then
    echo "❌ NVIDIA Nsight Compute (ncu) not found"
    echo ""
    echo "Install: sudo apt install nvidia-nsight-compute"
    echo "Or download: https://developer.nvidia.com/nsight-compute"
    exit 1
fi

echo "✅ NCU found: $(ncu --version | head -1)"
echo ""

# Check for GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ No NVIDIA GPU detected"
    exit 1
fi

GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
echo "🎮 GPU: $GPU_NAME"
echo ""

# Run NCU profile
echo "📊 Running NCU profile (this may take 2-3 minutes)..."
echo ""

TEST_PROMPT="35M with chest pain, 2h duration, radiating to left arm. BP 130/85, HR 95, RR 18, SpO2 98% RA."

ncu --target-processes all \
    --set full \
    --export ncu_goat_scribe \
    --force-overwrite \
    python -m goatnote_scribe.cli "$TEST_PROMPT" > /dev/null 2>&1

echo "✅ NCU profile complete"
echo ""

# Extract key metrics
echo "📈 Key Performance Metrics:"
echo ""

ncu -i ncu_goat_scribe.ncu-rep \
    --csv \
    --page raw \
    --metrics sm__throughput.avg.pct_of_peak_sustained_elapsed,dram__throughput.avg.pct_of_peak_sustained_elapsed,gpu__time_duration.avg \
    | tail -n +2 | head -1 | awk -F',' '{
        printf "  SM Efficiency:     %.1f%%\n", $1
        printf "  Memory Bandwidth:  %.1f%%\n", $2  
        printf "  Kernel Time:       %.2f ms\n", $3/1000000
    }'

echo ""
echo "======================================"
echo "✅ Profiling complete!"
echo "======================================"
echo ""
echo "📁 Full report: ncu_goat_scribe.ncu-rep"
echo ""
echo "🌐 View in GUI:"
echo "   ncu-ui ncu_goat_scribe.ncu-rep"
echo ""
echo "📄 Export to text:"
echo "   ncu -i ncu_goat_scribe.ncu-rep --page raw > report.txt"
echo ""

