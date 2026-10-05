#!/usr/bin/env bash
# Builds Mneme's examples/hip_vec_add, records it, and exports the database.
#
#   source examples/env-tuolumne.sh
#   examples/mneme-hip-vec-add.sh <mneme source dir> <work dir>
set -euo pipefail

MNEME_SRC=${1:?Mneme source directory}
WORK=${2:?work directory}
PROTEUS_PREFIX=${PROTEUS_PREFIX:-/p/vast1/fink12/proteus/install-tuolumne-rocm-6.4.0}
LLVM_BIN="$(mneme config llvmdir)/bin"

cmake -S "$MNEME_SRC/examples/hip_vec_add" -B "$WORK/vecadd-build" \
  -DCMAKE_HIP_ARCHITECTURES=gfx942 \
  -DCMAKE_PREFIX_PATH="$(mneme config cmakedir);$PROTEUS_PREFIX" \
  -DCMAKE_C_COMPILER="$LLVM_BIN/amdclang" -DCMAKE_CXX_COMPILER="$LLVM_BIN/amdclang++" \
  -DCMAKE_HIP_COMPILER="$LLVM_BIN/clang++"
make -C "$WORK/vecadd-build"

findingmnemo record -o "$WORK/vecadd" -- "$WORK/vecadd-build/vecAdd" 100
findingmnemo export "$WORK/vecadd"
