import argparse
import psutil
import csv
import time
import os


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--output_file", required=False, type=str, default="job_stats.txt", help="Name of the output file to write to.")
    parser.add_argument("--interval", required=False, type=int, default=60, help="Interval to fetch statistics")

    return parser.parse_args()


def get_header_columns():
    """ Because psutil returns different numbers of values for each metric depending on OS,
    we call each metric function once so we know which values we are getting.
    :return: A list of header column names.
    """
    # Time and CPU % Usage are static.
    columns = ["time", "cpu_pct"]
    # Virtual memory columns can vary on OS.
    columns += list(psutil.virtual_memory()._asdict().keys())
    # Load Avg columns are static.
    columns += ["load_1", "load_5", "load_15"]
    # Disk IO columns can vary on OS.
    columns += list(psutil.disk_io_counters(perdisk=False, nowrap=True)._asdict().keys())
    # N_CPU is static.
    columns += ["n_phys_cpu", "n_log_cpu", "n_avail_cpu"]

    return columns


def get_cpu_counts():
    n_phys_cpu = psutil.cpu_count(logical=False)
    n_log_cpu = psutil.cpu_count(logical=True)

    try:
        n_avail_cpu = len(psutil.Process().cpu_affinity())
    except:
        print("CPU affinity stats not available, falling back to # of logical cores.")
        n_avail_cpu = psutil.cpu_count(logical=True)

    return n_phys_cpu, n_log_cpu, n_avail_cpu


def main():
    args = parse_args()

    output_file = args.output_file
    interval = args.interval

    with open(output_file, "w", newline="") as f:
        csv_writer = csv.writer(f, delimiter="\t")
        csv_writer.writerow(get_header_columns())

        cpu_counts = get_cpu_counts()

        while True:
            now = time.time()
            cpu_stat = psutil.cpu_percent()
            mem_stat = psutil.virtual_memory()
            load_avg = psutil.getloadavg()
            disk_stat = psutil.disk_io_counters(perdisk=False, nowrap=True)
            csv_writer.writerow((now, cpu_stat) + mem_stat + load_avg + disk_stat + cpu_counts)
            f.flush()
            time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Received SIGINT, exiting.")
    finally:
        print("Script complete.")
