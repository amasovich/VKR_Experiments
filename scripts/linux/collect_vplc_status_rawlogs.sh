#!/usr/bin/env bash
set -euo pipefail

# TECH collector for VPLC `vplc status`.
# It records the runtime-reported "Длительность цикла (ms)" as cycle_exec_ms.
# This is not validated as per-cycle Tper and rows are marked technical_check.

OUT=""
MODE_ID=""
SERIES_ID=""
RUN_ID=""
LOAD_LEVEL=""
LOAD_PASSES=""
T0_MS=""
DEADLINE_MS=""
SAMPLES="100"
INTERVAL_SEC="1"
OBJECT_NAME="vPLC_container"
NODE_ID="VPLC_HOST"

usage() {
    cat <<'EOF'
Usage:
  collect_vplc_status_rawlogs.sh --out PATH --mode-id MODE --series-id SERIES --run-id RUN \
    --load-level N --load-passes N --t0-ms N --deadline-ms N [--samples N] [--interval-sec N]

Notes:
  - cycle_exec_ms is parsed from `vplc status` field "Длительность цикла (ms)".
  - Tper/Jper/deadline_miss are intentionally left empty.
  - quality_flag is technical_check.
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --mode-id) MODE_ID="$2"; shift 2 ;;
        --series-id) SERIES_ID="$2"; shift 2 ;;
        --run-id) RUN_ID="$2"; shift 2 ;;
        --load-level) LOAD_LEVEL="$2"; shift 2 ;;
        --load-passes) LOAD_PASSES="$2"; shift 2 ;;
        --t0-ms) T0_MS="$2"; shift 2 ;;
        --deadline-ms) DEADLINE_MS="$2"; shift 2 ;;
        --samples) SAMPLES="$2"; shift 2 ;;
        --interval-sec) INTERVAL_SEC="$2"; shift 2 ;;
        --object) OBJECT_NAME="$2"; shift 2 ;;
        --node-id) NODE_ID="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
    esac
done

for required in OUT MODE_ID SERIES_ID RUN_ID LOAD_LEVEL LOAD_PASSES T0_MS DEADLINE_MS; do
    if [[ -z "${!required}" ]]; then
        echo "Missing required argument: $required" >&2
        usage >&2
        exit 2
    fi
done

mkdir -p "$(dirname "$OUT")"

echo "run_id,mode_id,series_id,object,node_id,sample_index,cycle_index,cycle_counter,ts_observe,ts_start,ts_end,timestamp_tick_ns,timestamp_source,t0_ms,deadline_threshold_ms,Tper,Jper,deadline_miss,heartbeat,workload_accumulator,load_level,load_passes,error_flag,quality_flag,notes,cycle_exec_ms,cycle_nominal_ms,program_status" > "$OUT"

for ((sample=0; sample<SAMPLES; sample++)); do
    ts_observe="$(LC_ALL=C date -u '+%Y-%m-%dT%H:%M:%S.%NZ')"
    status_text="$(vplc status 2>&1 || true)"

    cycle_line="$(printf '%s\n' "$status_text" | grep -F 'Длительность цикла (ms)' | tail -n 1 || true)"
    program_line="$(printf '%s\n' "$status_text" | grep -F 'Программа' | grep -F ':' | head -n 1 || true)"

    cycle_pair="$(printf '%s' "$cycle_line" | sed -n 's/.*: *\([0-9.][0-9.]*\/[0-9.][0-9.]*\).*/\1/p')"
    cycle_exec_ms=""
    cycle_nominal_ms=""
    if [[ "$cycle_pair" == */* ]]; then
        cycle_exec_ms="${cycle_pair%%/*}"
        cycle_nominal_ms="${cycle_pair##*/}"
    fi

    program_status="$(printf '%s' "$program_line" | sed -n 's/.*: *//p' | tr -d '\r' | sed 's/"/'\''/g')"
    notes="vplc_status_cycle_duration_not_validated_as_Tper"
    if [[ -z "$cycle_exec_ms" ]]; then
        notes="vplc_status_cycle_duration_parse_failed"
    fi

    fields=(
        "$RUN_ID" "$MODE_ID" "$SERIES_ID" "$OBJECT_NAME" "$NODE_ID" "$sample"
        "" "" "$ts_observe" "" "" "" "host_log"
        "$T0_MS" "$DEADLINE_MS" "" "" "" "" ""
        "$LOAD_LEVEL" "$LOAD_PASSES" "" "technical_check" "$notes"
        "$cycle_exec_ms" "$cycle_nominal_ms" "$program_status"
    )
    (IFS=,; echo "${fields[*]}") >> "$OUT"

    if (( sample + 1 < SAMPLES )); then
        sleep "$INTERVAL_SEC"
    fi
done

echo "Wrote TECH VPLC status RawLogs candidate: $OUT"
