#!/usr/bin/env bash
# Builds XSBench (HIP) at the commit the ICE4HPC dataset used and records the
# dataset's GPU configurations on a Tuolumne login or compute node.
#
#   source examples/env-tuolumne.sh
#   examples/ice4hpc-xsbench.sh <work dir> [sizes...]
#
# Sizes default to "small large"; ICE4HPC also uses XL and XXL. History mode
# is skipped because XSBench does not implement it on GPUs.
#
# Only the unionized grid is recorded with Mneme: hash and nuclide allocate a
# zero-byte buffer, which Mneme's recorder currently aborts on. Those runs
# capture launch stacks only.
set -euo pipefail

WORK=${1:?work directory}
shift
SIZES=${*:-small large}
XSBENCH=$WORK/XSBench

if [ ! -d "$XSBENCH" ]; then
  git clone https://github.com/ANL-CESAR/XSBench "$XSBENCH"
  git -C "$XSBENCH" checkout ba08e52
fi

# Same flags add_mneme() applies in CMake builds.
make -C "$XSBENCH/hip" -j8 CC=hipcc \
  CFLAGS="-std=c++14 -O3 --offload-arch=gfx942 -gline-tables-only $(mneme config cflags)" \
  LDFLAGS="-lm --offload-arch=gfx942 $(mneme config ldflags)"

RUNS=()
for size in $SIZES; do
  out=$WORK/runs/xsbench-$size-unionized
  findingmnemo record -o "$out" --name XSBench --mneme-arg=-vass --mneme-arg=16 -- \
    "$XSBENCH/hip/XSBench" -m event -s "$size" -G unionized
  RUNS+=("$out")
  for grid in hash nuclide; do
    out=$WORK/runs/xsbench-$size-$grid
    findingmnemo record -o "$out" --name XSBench --no-mneme -- \
      "$XSBENCH/hip/XSBench" -m event -s "$size" -G "$grid"
    RUNS+=("$out")
  done
done

findingmnemo export "${RUNS[@]}" --db "$WORK/xsbench.sqlite"
