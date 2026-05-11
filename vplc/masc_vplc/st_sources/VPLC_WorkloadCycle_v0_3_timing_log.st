(* VKR VPLC workload v0.3 with internal timing and ring log.
   Intended for a cyclic ST task in VPLC Studio.

   Timing source:
   _milliseconds_from_start_ : LREAL
   documented in v0.5_Функции_MASC_ВПЛК.pdf as milliseconds since VPLC start.

   This version mirrors the Siemens S7 workload/logging shape:
   - Tper_ms = start-to-start period between adjacent ST task calls
   - Jper_ms = Tper_ms - T0_ms
   - deadline_miss = Tper_ms > deadline_threshold_ms
   - ring buffer arrays hold 1000 recent rows for dump-based RawLogs extraction
*)

IF reset_log_request THEN
    cycle_counter := 0;
    heartbeat := FALSE;
    heartbeat_divider := 0;
    workload_accumulator := 0;
    error_flag := FALSE;
    load_level_effective := 0;
    load_passes_effective := 0;

    timing_first_cycle := TRUE;
    timing_valid := FALSE;
    deadline_miss := FALSE;
    timing_quality_flag := 1;
    quality_flag := 1;
    now_ms := 0.0;
    prev_ms := 0.0;
    Tper_ms := 0.0;
    Jper_ms := 0.0;

    sample_index := 0;
    write_index := 0;
    buffer_wrapped := FALSE;
    freeze_logging := FALSE;
    reset_log_request := FALSE;
END_IF;

IF NOT init_done THEN
    load_level := 0;
    T0_ms := 10.0;
    deadline_threshold_ms := 20.0;
    max_valid_tper_ms := 1000.0;
    load_passes_level1 := 32;
    load_passes_level2 := 128;
    load_passes_level3 := 512;
    max_load_passes := 512;
    heartbeat_divisor_cycles := 100;
    accumulator_modulus := 2147483647;
    log_capacity := 1000;
    divisor_two := 2;
    timing_first_cycle := TRUE;
    init_done := TRUE;
END_IF;

cycle_counter := cycle_counter + 1;

now_ms := _milliseconds_from_start_;

IF timing_first_cycle THEN
    Tper_ms := 0.0;
    Jper_ms := 0.0;
    timing_valid := FALSE;
    deadline_miss := FALSE;
    timing_quality_flag := 1;
    quality_flag := 1;
    timing_first_cycle := FALSE;
ELSE
    Tper_ms := now_ms - prev_ms;
    Jper_ms := Tper_ms - REAL_TO_LREAL(T0_ms);

    IF (Tper_ms <= 0.0) OR (Tper_ms > REAL_TO_LREAL(max_valid_tper_ms)) THEN
        timing_valid := FALSE;
        deadline_miss := FALSE;
        timing_quality_flag := 2;
        quality_flag := 2;
    ELSE
        timing_valid := TRUE;
        deadline_miss := Tper_ms > REAL_TO_LREAL(deadline_threshold_ms);
        timing_quality_flag := 0;
        quality_flag := 0;
    END_IF;
END_IF;

prev_ms := now_ms;

heartbeat_divider := heartbeat_divider + 1;
IF heartbeat_divider >= heartbeat_divisor_cycles THEN
    heartbeat := NOT heartbeat;
    heartbeat_divider := 0;
END_IF;

load_passes := 0;

IF load_level = 0 THEN
    error_flag := FALSE;
    effective_load_level := 0;
ELSIF load_level = 1 THEN
    error_flag := FALSE;
    effective_load_level := 1;
    load_passes := load_passes_level1;
ELSIF load_level = 2 THEN
    error_flag := FALSE;
    effective_load_level := 2;
    load_passes := load_passes_level2;
ELSIF load_level = 3 THEN
    error_flag := FALSE;
    effective_load_level := 3;
    load_passes := load_passes_level3;
ELSE
    error_flag := TRUE;
    effective_load_level := 0;
    load_passes := 0;
    quality_flag := 3;
END_IF;

IF load_passes > max_load_passes THEN
    load_passes := max_load_passes;
END_IF;

load_level_effective := effective_load_level;
load_passes_effective := load_passes;

workload_accumulator := workload_accumulator + cycle_counter + effective_load_level;
DIVMOD(workload_accumulator, accumulator_modulus, tmp_quotient, tmp_modulo);
workload_accumulator := tmp_modulo;

IF load_passes > 0 THEN
    FOR p := 1 TO load_passes DO
        FOR i := 0 TO 15 DO
            int_state[i] := int_state[i] + cycle_counter + i + p + effective_load_level;
            DIVMOD(int_state[i], accumulator_modulus, tmp_quotient, tmp_modulo);
            int_state[i] := tmp_modulo;

            DIVMOD(int_state[i], divisor_two, tmp_quotient, tmp_modulo);
            bool_state[i] := tmp_modulo = 0;

            IF bool_state[i] THEN
                workload_accumulator := workload_accumulator + int_state[i];
                DIVMOD(workload_accumulator, accumulator_modulus, tmp_quotient, tmp_modulo);
                workload_accumulator := tmp_modulo;
            ELSE
                workload_accumulator := workload_accumulator + i + p;
                DIVMOD(workload_accumulator, accumulator_modulus, tmp_quotient, tmp_modulo);
                workload_accumulator := tmp_modulo;
            END_IF;
        END_FOR;
    END_FOR;
END_IF;

IF NOT freeze_logging THEN
    log_idx := UDINT_TO_INT(write_index);

    log_sample_index[log_idx] := sample_index;
    log_cycle_counter[log_idx] := cycle_counter;
    log_now_ms[log_idx] := now_ms;
    log_Tper_ms[log_idx] := Tper_ms;
    log_Jper_ms[log_idx] := Jper_ms;
    log_deadline_miss[log_idx] := deadline_miss;
    log_timing_valid[log_idx] := timing_valid;
    log_heartbeat[log_idx] := heartbeat;
    log_workload_accumulator[log_idx] := workload_accumulator;
    log_load_level[log_idx] := load_level;
    log_load_passes[log_idx] := load_passes_effective;
    log_error_flag[log_idx] := error_flag;
    log_quality_flag[log_idx] := quality_flag;

    sample_index := sample_index + 1;
    write_index := write_index + 1;

    IF write_index >= log_capacity THEN
        write_index := 0;
        buffer_wrapped := TRUE;
    END_IF;
END_IF;
