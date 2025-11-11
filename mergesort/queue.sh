#!/bin/bash
set -euo pipefail

echo "Running mergesort benchmark locally on this machine..."
bash ./bench_mergesort.sh
echo "----------------------"
echo
echo "Local run finished. Now plot with \`make plot\`"
