# Environment for the examples on Tuolumne. Source it after setting
# MNEME_PREFIX to a Mneme install that has bin/mneme and python/mneme, built
# with MNEME_ENABLE_PYTHON=On from a branch that records kernel source
# (record-source-file or later).
#
#   export MNEME_PREFIX=/path/to/mneme/install
#   source examples/env-tuolumne.sh

: "${MNEME_PREFIX:?set MNEME_PREFIX to a Mneme install prefix}"
: "${MNEME_PYTHON:=/usr/workspace/fink12/miniconda3_tioga/envs/proteus_experimentation/bin}"

module load cmake/3.29.2 rocm/6.4.0

FINDINGMNEMO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export FINDINGMNEMO_ROOT
export PATH="$FINDINGMNEMO_ROOT/bin:$MNEME_PREFIX/bin:$MNEME_PYTHON:$PATH"
export PYTHONPATH="$MNEME_PREFIX/python${PYTHONPATH:+:$PYTHONPATH}"
