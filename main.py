import argparse
import logging
import os
import sys
import time

import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_argparse():
    """Sets up the argument parser for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Samples a process through /proc on Linux and reports measured values and deltas over the sampling window."
    )
    parser.add_argument(
        "-p", "--pid", type=int, required=False,
        help="Process ID to analyze. If not provided, samples the current process.",
    )
    parser.add_argument(
        "-o", "--output", type=str, default="process_analysis.csv",
        help="Output CSV file to store the analysis results (default: process_analysis.csv).",
    )
    parser.add_argument(
        "-t", "--trace_duration", type=int, default=10,
        help="Duration in seconds to sample the process (default: 10 seconds).",
    )
    parser.add_argument(
        "-l", "--log_level", type=str, default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO).",
    )
    return parser.parse_args()


def _read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def sample_process(pid):
    """Read one real sample of the named process from /proc.

    Raises FileNotFoundError if the process is gone and PermissionError
    if a file cannot be read by this user.
    """
    base = f"/proc/{pid}"
    if not os.path.isdir(base):
        raise FileNotFoundError(f"Process with PID {pid} does not exist.")

    sample = {}

    status = _read_text(os.path.join(base, "status"))
    for line in status.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if key == "State":
            sample["state"] = value
        elif key == "Threads":
            sample["threads"] = int(value)
        elif key == "voluntary_ctxt_switches":
            sample["voluntary_ctxt_switches"] = int(value)
        elif key == "nonvoluntary_ctxt_switches":
            sample["nonvoluntary_ctxt_switches"] = int(value)

    stat_text = _read_text(os.path.join(base, "stat"))
    # Field 2 (comm) is in parentheses and may contain spaces, so parse
    # the fields after the last closing parenthesis.
    rest = stat_text[stat_text.rfind(")") + 2:].split()
    # rest[0] is field 3 (state); utime is field 14, stime field 15,
    # num_threads field 20.
    sample["utime_ticks"] = int(rest[11])
    sample["stime_ticks"] = int(rest[12])
    sample["num_threads_stat"] = int(rest[17])

    try:
        io_text = _read_text(os.path.join(base, "io"))
        for line in io_text.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            if key in ("syscr", "syscw", "read_bytes", "write_bytes"):
                sample[key] = int(value.strip())
    except (FileNotFoundError, PermissionError, OSError):
        # /proc/<pid>/io is not readable for every process and user.
        # Those counters are simply omitted from the report.
        pass

    try:
        sample["open_fds"] = len(os.listdir(os.path.join(base, "fd")))
    except OSError:
        pass

    children = set()
    try:
        for task in os.listdir(os.path.join(base, "task")):
            children_file = os.path.join(base, "task", task, "children")
            try:
                for token in _read_text(children_file).split():
                    children.add(int(token))
            except (FileNotFoundError, PermissionError, OSError, ValueError):
                continue
    except OSError:
        pass
    sample["child_pids"] = sorted(children)
    sample["child_count"] = len(children)
    return sample


NUMERIC_METRICS = [
    "utime_ticks",
    "stime_ticks",
    "threads",
    "voluntary_ctxt_switches",
    "nonvoluntary_ctxt_switches",
    "syscr",
    "syscw",
    "read_bytes",
    "write_bytes",
    "open_fds",
    "child_count",
]


def trace_process(pid, duration):
    """Sample the named PID at the start and end of the window.

    Returns (start_sample, end_sample, elapsed_seconds). Every value
    comes from /proc for that PID; nothing is simulated.
    """
    start = sample_process(pid)
    start_time = time.time()
    remaining = duration
    while remaining > 0:
        step = min(0.5, remaining)
        time.sleep(step)
        remaining -= step
        # Fail promptly if the process exits during the window.
        if not os.path.isdir(f"/proc/{pid}"):
            raise FileNotFoundError(
                f"Process with PID {pid} exited during sampling."
            )
    end = sample_process(pid)
    elapsed = time.time() - start_time
    return start, end, elapsed


def build_report(pid, duration, start, end, elapsed):
    """Build one row per real measured quantity."""
    rows = []
    rows.append({
        "pid": pid, "duration_seconds": round(elapsed, 3),
        "metric": "state",
        "start_value": start.get("state", ""), "end_value": end.get("state", ""),
        "delta": "", "per_second": "", "note": "Process state from /proc status at start and end.",
    })
    rows.append({
        "pid": pid, "duration_seconds": round(elapsed, 3),
        "metric": "child_pids",
        "start_value": " ".join(str(c) for c in start.get("child_pids", [])),
        "end_value": " ".join(str(c) for c in end.get("child_pids", [])),
        "delta": "", "per_second": "", "note": "Child PIDs listed under /proc task children at end of window.",
    })
    for metric in NUMERIC_METRICS:
        if metric not in start or metric not in end:
            continue
        delta = end[metric] - start[metric]
        per_second = round(delta / elapsed, 3) if elapsed > 0 else ""
        note = ""
        if metric in ("voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"):
            note = "Measured count only. No anomaly verdict is computed."
        rows.append({
            "pid": pid, "duration_seconds": round(elapsed, 3),
            "metric": metric,
            "start_value": start[metric], "end_value": end[metric],
            "delta": delta, "per_second": per_second, "note": note,
        })
    total_switches = 0
    counted = False
    for metric in ("voluntary_ctxt_switches", "nonvoluntary_ctxt_switches"):
        if metric in start and metric in end:
            total_switches += end[metric] - start[metric]
            counted = True
    if counted and elapsed > 0:
        rate = round(total_switches / elapsed, 3)
        rows.append({
            "pid": pid, "duration_seconds": round(elapsed, 3),
            "metric": "context_switches_per_second",
            "start_value": "", "end_value": "",
            "delta": total_switches, "per_second": rate,
            "note": "Total context switches divided by the sampling duration. This is a measured rate, not a verdict on the process.",
        })
    return pd.DataFrame(rows)


def main():
    args = setup_argparse()
    logging.getLogger().setLevel(args.log_level.upper())
    try:
        pid = args.pid
        if pid is None:
            pid = os.getpid()
            logging.info(f"No PID specified, sampling the current process with PID {pid}")
        if not isinstance(pid, int) or pid <= 0:
            raise ValueError("Invalid PID. PID must be a positive integer.")
        try:
            os.kill(pid, 0)
        except OSError:
            raise ValueError(f"Process with PID {pid} does not exist or cannot be accessed.")
        trace_duration = args.trace_duration
        if not isinstance(trace_duration, int) or trace_duration <= 0:
            raise ValueError("Invalid trace duration. Duration must be a positive integer.")
        output_file = args.output
        if not isinstance(output_file, str):
            raise ValueError("Invalid output file name. Must be a string.")
        if not output_file.endswith(".csv"):
            output_file += ".csv"

        logging.info(f"Sampling process {pid} through /proc for {trace_duration} seconds.")
        start, end, elapsed = trace_process(pid, trace_duration)
        report = build_report(pid, trace_duration, start, end, elapsed)
        if report.empty:
            logging.error("No measured data was collected.")
            sys.exit(1)
        try:
            report.to_csv(output_file, index=False)
        except Exception as e:
            logging.error(f"Could not write output CSV {output_file}: {e}")
            sys.exit(1)
        logging.info(f"Analysis results saved to {output_file}")
        print(report.to_string(index=False))
    except FileNotFoundError as e:
        logging.error(str(e))
        sys.exit(1)
    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
