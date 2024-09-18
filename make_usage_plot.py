import os.path

from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, HourLocator, MinuteLocator
from matplotlib.ticker import FixedLocator, AutoMinorLocator
from matplotlib.cm import Dark2

import pandas as pd
import numpy as np
import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_prefix", type=str, default="job_stats")
    parser.add_argument("--output_file", type=str)
    parser.add_argument("--stats", choices=["cpu", "mem", "disk"], nargs="+", default=["cpu", "mem", "disk"])

    args = parser.parse_args()
    # If not provided, output file is the same name as input file.
    args.output_file = args.output_file or f"{args.input_prefix}.png"

    return args


def memory_str(n_bytes: int):
    if n_bytes < 0:
        raise ValueError("Negative bytes!")

    log_bytes = np.log10(n_bytes)

    bytes_log_thresh = np.array([3, 6, 9, 12])
    bytes_label = ["B", "KB", "MB", "GB"]

    bytes_idx = max(np.searchsorted(bytes_log_thresh, log_bytes, side="right"), 0)

    return f"{np.power(10, 3 + log_bytes - bytes_log_thresh[bytes_idx]):0.1f}{bytes_label[bytes_idx]}"


def read_stat_files(input_prefix: str):
    job_stats_fname = f"{input_prefix}.txt"
    job_markers_fname = f"{input_prefix}.markers"

    # Read the job stats file.
    job_stats = pd.read_csv(job_stats_fname, sep="\t")
    job_stats["datetime"] = pd.to_datetime(job_stats["time"], unit="s").dt.tz_localize("UTC").dt.tz_convert("America/Denver")

    # Read the job markers file if it exists.
    if os.path.exists(job_markers_fname):
        job_markers = pd.read_csv(job_markers_fname, header=None, names=["time", "marker"])
        job_markers["time"] = pd.to_datetime(job_markers["time"], unit="s").dt.tz_localize("UTC").dt.tz_convert("America/Denver")
        job_markers = {lbl: time for lbl, time in zip(job_markers["marker"], job_markers["time"])}
    else:
        job_markers = None

    return job_stats, job_markers


def plot_stat(ax: plt.Axes, job_stats: pd.DataFrame, stat: str):
    if stat == "cpu":
        n_phys_cpu = job_stats['n_phys_cpu'].iloc[0]
        n_log_cpu = job_stats['n_log_cpu'].iloc[0]
        n_avail_cpu = job_stats["n_avail_cpu"].iloc[0]

        label_str = f"CPU Usage %\n({n_phys_cpu} Physical CPUs, {n_log_cpu} Logical CPUs, {n_avail_cpu} Available CPUs)"
        ax.set_xlabel(label_str)
        ax.plot(job_stats["cpu_pct"], job_stats["datetime"], label=label_str, color=Dark2(0))
        ax.set_xlim(0, 100)
        ax.xaxis.set_major_locator(FixedLocator([0, 25, 50, 75, 100]))
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        if n_avail_cpu != n_log_cpu:
            ax.axvline(n_avail_cpu*100, label="Avail. CPU Usage Boundary")
            ax.legend(fancybox=False, color="black", loc="upper right")
    elif stat == "mem":
        label_str = f"Memory Usage %\n({memory_str(job_stats['total'].iloc[0])} Total RAM)"
        ax.set_xlabel(label_str)
        ax.plot(job_stats["percent"], job_stats["datetime"], label=label_str, color=Dark2(1))
        ax.set_xlim(0, 100)
        ax.xaxis.set_major_locator(FixedLocator([0, 25, 50, 75, 100]))
        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
    elif stat == "disk":
        ax.set_xlabel("Disk Usage (MB/s)")
        # Disk usage (estimate) is difference between successive byte counts divided by difference
        # between successive timestamps.
        d_t = job_stats["time"].diff()
        read_usage = job_stats["read_bytes"].diff()/(d_t*1e6)
        write_usage = job_stats["write_bytes"].diff()/(d_t*1e6)
        ax.plot(read_usage, job_stats["datetime"], label="Disk Read (MB/s)", color=Dark2(2))
        ax.plot(write_usage, job_stats["datetime"], label="Disk Write (MB/s)", color=Dark2(3))
        ax.set_xlim(-1, max(read_usage.max(), write_usage.max())+1)
        ax.legend(fancybox=False, edgecolor="black", loc="upper right")
    else:
        raise ValueError(f"Unsupported statistic '{stat}' !")


def make_plot(job_stats: pd.DataFrame, output_file: str, stats: list, job_markers: dict = None):

    # Calculate size of chart
    fig_width = 5*len(stats)
    job_duration = (job_stats["datetime"].max() - job_stats["datetime"].min()).total_seconds()/3600
    fig_height = max(10, job_duration)

    # Create figure
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), ncols=len(stats), sharey=True)

    # Plot all statistics
    for stat, ax_i in zip(stats, ax):

        # Plot job statistic
        ax_i.xaxis.tick_top()
        ax_i.xaxis.set_label_position('top')
        plot_stat(job_stats=job_stats, stat=stat, ax=ax_i)

        # Plot markers
        if job_markers is not None:
            for i, (lbl, lbl_time) in enumerate(job_markers.items()):
                ax_i.axhline(lbl_time, color="black", linestyle="--")
                ax_i.text(ax_i.get_xlim()[-1], lbl_time, lbl,  ha="right", va="bottom" if i % 2 == 1 else "top")

    # Y-axis is shared among all axes, so we set the defaults here.
    ax[0].yaxis.set_major_formatter(DateFormatter("%m/%d %H:%M:%S"))
    ax[0].yaxis.set_major_locator(HourLocator(interval=1) if job_duration > 1 else MinuteLocator(interval=1))
    ax[0].yaxis.set_minor_locator(AutoMinorLocator(4))
    # Invert so chart reads top -> bottom
    ax[0].set_ylim(job_stats["datetime"].min(), job_stats["datetime"].max())
    ax[0].invert_yaxis()

    fig.tight_layout()
    fig.savefig(output_file)


if __name__ == "__main__":
    # Parse arguments
    args = parse_args()

    print("Reading stats...")
    stat_df, marker_d = read_stat_files(args.input_prefix)

    print("Generating figure...")
    make_plot(job_stats=stat_df, output_file=args.output_file, job_markers=marker_d, stats=args.stats)

    print("Done!")
