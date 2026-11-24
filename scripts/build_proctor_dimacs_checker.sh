#!/usr/bin/env bash
# Produce a standalone static Lean source bundle. No proof data enters source.
set -euo pipefail
if [[ $# -ne 1 ]]; then
  echo "usage: $0 OUTPUT.lean" >&2
  exit 2
fi
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
out="$1"
# Preserve all kernel printouts in the research bundle; no gate stripping.
cat "$root/formal/ProctorHallDeficiency.lean" \
    "$root/formal/ProctorCapacityDeficiency.lean" \
    "$root/formal/ProctorMixedInference.lean" \
    "$root/formal/ProctorPairedReplay.lean" \
    "$root/formal/ProctorExecutableReplay.lean" \
    "$root/formal/ProctorCapacityReplay.lean" \
    "$root/formal/ProctorXorReplay.lean" \
    "$root/formal/ProctorUnifiedReplay.lean" \
    "$root/formal/ProctorDataParser.lean" \
    "$root/formal/ProctorDimacsInput.lean" \
    "$root/formal/ProctorDimacsMain.lean" > "$out"
