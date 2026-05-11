(* VKR VPLC workload v0.2.
   Intended for a cyclic ST task in VPLC Studio.
   This code mirrors the deterministic workload semantics used in Siemens S7.

   Timing fields Tper/Jper/deadline_miss are not produced here yet.
   They must come from a confirmed VPLC capture method.
*)

IF NOT init_done THEN
    load_level := 0;
    T0_ms := 10.0;
    deadline_threshold_ms := 20.0;
    load_passes_level1 := 32;
    load_passes_level2 := 128;
    load_passes_level3 := 512;
    max_load_passes := 512;
    heartbeat_divisor_cycles := 100;
    accumulator_modulus := 2147483647;
    init_done := TRUE;
END_IF;

divisor_two := 2;

cycle_counter := cycle_counter + 1;

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
