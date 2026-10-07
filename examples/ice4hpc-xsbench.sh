#!/usr/bin/env bash
# Builds XSBench (HIP) at the commit the ICE4HPC dataset used and records the
# dataset's event-based GPU configuration with the unionized grid on a Tuolumne
# login or compute node.
#
#   source examples/env-tuolumne.sh
#   examples/ice4hpc-xsbench.sh <work dir> [sizes...]
#
# Sizes default to "small"; ICE4HPC also uses large, XL and XXL.
set -euo pipefail

WORK=${1:?work directory}
shift
SIZES=${*:-small}
XSBENCH=$WORK/XSBench

if [ ! -d "$XSBENCH" ]; then
  git clone https://github.com/ANL-CESAR/XSBench "$XSBENCH"
  git -C "$XSBENCH" checkout ba08e52
fi

# Same flags add_mneme() applies in CMake builds; -grecord-command-line lets
# the export show device source with #ifs resolved.
make -C "$XSBENCH/hip" -j8 CC=hipcc \
  CFLAGS="-std=c++14 -O3 --offload-arch=gfx942 -g -grecord-command-line $(mneme config cflags)" \
  LDFLAGS="-lm --offload-arch=gfx942 $(mneme config ldflags)"

RUNS=()
for size in $SIZES; do
  out=$WORK/runs/xsbench-$size-unionized
  findingmnemo record -o "$out" --name XSBench --mneme-arg=-vass --mneme-arg=16 -- \
    "$XSBENCH/hip/XSBench" -m event -s "$size" -G unionized
  RUNS+=("$out")
done

findingmnemo export "${RUNS[@]}" -o "$WORK/xsbench-db"
