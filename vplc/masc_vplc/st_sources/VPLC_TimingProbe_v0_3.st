(* VKR VPLC timing probe v0.3.
   Purpose: check whether the documented system variable
   _milliseconds_from_start_ can be used inside VPLC ST code.

   Source basis:
   documentation/v0.5_Функции_MASC_ВПЛК.pdf:
   _milliseconds_from_start_ : LREAL
   "Количество миллисекунд от запуска ВПЛК"

   This is a TECH probe, not the final workload.
*)

IF NOT timing_probe_init_done THEN
    T0_ms := 10.0;
    deadline_threshold_ms := 20.0;
    max_valid_tper_ms := 1000.0;
    timing_first_cycle := TRUE;
    timing_probe_init_done := TRUE;
END_IF;

cycle_counter := cycle_counter + 1;

now_ms := _milliseconds_from_start_;

IF timing_first_cycle THEN
    Tper_ms := 0.0;
    Jper_ms := 0.0;
    timing_valid := FALSE;
    deadline_miss := FALSE;
    timing_quality_flag := 1;
    timing_first_cycle := FALSE;
ELSE
    Tper_ms := now_ms - prev_ms;
    Jper_ms := Tper_ms - REAL_TO_LREAL(T0_ms);

    IF (Tper_ms <= 0.0) OR (Tper_ms > REAL_TO_LREAL(max_valid_tper_ms)) THEN
        timing_valid := FALSE;
        deadline_miss := FALSE;
        timing_quality_flag := 2;
    ELSE
        timing_valid := TRUE;
        deadline_miss := Tper_ms > REAL_TO_LREAL(deadline_threshold_ms);
        timing_quality_flag := 0;
    END_IF;
END_IF;

prev_ms := now_ms;
