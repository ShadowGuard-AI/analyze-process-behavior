import argparse
import logging
import os
import sys
import time
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Analyzes process behavior to detect anomalies and potential malicious activity."
    )

    parser.add_argument(
        "-p",
        "--pid",
        type=int,
        help="Process ID to analyze.  If not provided, attempts to trace the current process.",
        required=False
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="process_analysis.csv",
        help="Output CSV file to store the analysis results (default: process_analysis.csv)."
    )

    parser.add_argument(
        "-t",
        "--trace_duration",
        type=int,
        default=10,
        help="Duration in seconds to trace the process (default: 10 seconds)."
    )

    parser.add_argument(
        "-l",
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)."
    )


    return parser.parse_args()

def trace_process(pid, duration):
    """
    Traces a process and collects system call information.
    This is a placeholder implementation.  A real implementation would
    use ptrace, systemtap, or ETW to collect system call data.
    """

    # Security best practice:  Avoid direct shell commands.  A real implementation
    # would interact with the OS directly via system calls (e.g., using ctypes).

    logging.info(f"Tracing process {pid} for {duration} seconds. This is a placeholder implementation.")

    # Placeholder data (replace with real syscall data collection)
    syscall_data = []
    import random  #Imported here as it is only used in the placeholder
    start_time = time.time()
    while time.time() - start_time < duration:
      # Simulate some system calls
      syscalls = ["read", "write", "open", "close", "connect", "accept"]
      syscall = random.choice(syscalls)
      count = random.randint(1,5)
      syscall_data.append({"timestamp": time.time(), "syscall": syscall, "count": count})
      time.sleep(0.1) # Simulate some activity


    return syscall_data

def analyze_syscalls(syscall_data):
    """
    Analyzes the collected system call data.

    This is a very basic anomaly detection example. A real implementation
    would use more sophisticated techniques.
    """

    df = pd.DataFrame(syscall_data)
    if df.empty:
        logging.warning("No syscall data to analyze.")
        return pd.DataFrame()

    logging.info("Analyzing syscall data...")

    syscall_counts = df['syscall'].value_counts().reset_index()
    syscall_counts.columns = ['syscall', 'count']

    # Simple anomaly detection: Flag syscalls with unusually high frequency
    mean_count = syscall_counts['count'].mean()
    std_count = syscall_counts['count'].std()

    # Check for zero standard deviation
    if std_count == 0:
      threshold = mean_count * 2
    else:
      threshold = mean_count + 2 * std_count


    syscall_counts['is_anomalous'] = syscall_counts['count'] > threshold

    return syscall_counts


def main():
    """
    Main function to orchestrate the process analysis.
    """
    args = setup_argparse()

    # Set the logging level
    logging.getLogger().setLevel(args.log_level.upper())

    try:
        pid = args.pid
        if pid is None:
            pid = os.getpid() # Analyze the current process if no PID is specified
            logging.info(f"No PID specified, analyzing the current process with PID {pid}")

        # Input validation: Check if the PID is valid.  This is a basic check.
        if not isinstance(pid, int) or pid <= 0:
            raise ValueError("Invalid PID. PID must be a positive integer.")

        # Check if the process exists (more robust validation)
        try:
            os.kill(pid, 0)  # Signals the process, but doesn't kill it (signal 0)
        except OSError:
            raise ValueError(f"Process with PID {pid} does not exist or cannot be accessed.")

        trace_duration = args.trace_duration
        if not isinstance(trace_duration, int) or trace_duration <= 0:
            raise ValueError("Invalid trace duration. Duration must be a positive integer.")

        output_file = args.output

        # Sanitize the output file path
        if not isinstance(output_file, str):
            raise ValueError("Invalid output file name.  Must be a string.")

        # Basic path sanitization to prevent path traversal
        output_file = os.path.basename(output_file)

        if not output_file.endswith(".csv"):
            output_file += ".csv"


        # Perform the analysis
        syscall_data = trace_process(pid, trace_duration)
        analysis_results = analyze_syscalls(syscall_data)


        # Output the results
        if not analysis_results.empty:
            analysis_results.to_csv(output_file, index=False)
            logging.info(f"Analysis results saved to {output_file}")
        else:
            logging.warning("No analysis results to save.")


    except ValueError as e:
        logging.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Example usage:
    # python main.py -p <PID> -t 15 -o my_analysis.csv --log_level DEBUG
    # python main.py -t 5  # Analyze the current process for 5 seconds
    # python main.py  # Analyze the current process for 10 seconds, default output
    main()