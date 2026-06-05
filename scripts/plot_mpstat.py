#!/usr/bin/env python3
"""
Plot the output of the 'mpstat -P ALL 1 125' command.

This script parses mpstat log files, typically generated on a Raspberry Pi,
and plots the CPU usage telemetry including total CPU, user, sys, and soft IRQ
processing for each core.

Example: mpstat -P ALL 1 125 | tee mpstat.out
         ./plot_mpstat mpstat.out
"""

import sys
import re
import argparse
import pandas as pd
import matplotlib.pyplot as plt

# Establish distinct, vibrant colors for the individual cores.
# Core 'all' is explicitly set to solid black.
CORE_COLORS = {
    'all': '#000000',
    '0': '#e74c3c',    # Red
    '1': '#3498db',    # Blue
    '2': '#2ecc71',    # Green
    '3': '#f39c12'     # Amber/Orange
}


def parse_mpstat(file_path):
    """Parse raw mpstat output file and return a pandas DataFrame.

    Args:
        file_path (str): Path to the log file.

    Returns:
        pd.DataFrame: Parsed telemetry data.

    Raises:
        ValueError: If no valid mpstat metric rows could be parsed.
    """
    data = []
    # Match lines that begin with a time stamp like "07:10:07 AM" or "07:10:07"
    # Followed by a core identifier (all, 0, 1, 2, 3) and numeric columns.
    # Note: Using shorter regex pattern to avoid very long line limit.
    pattern = (
        r'^(\d{2}:\d{2}:\d{2}(?:\s+[A-Z]{2})?)\s+'
        r'([a-z0-9]+)\s+'
        r'([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)'
    )
    row_re = re.compile(pattern)

    with open(file_path, 'r', encoding='utf-8') as file_obj:
        for line in file_obj:
            line = line.strip()
            match = row_re.match(line)
            if not match:
                continue

            groups = match.groups()
            time_str = groups[0]
            cpu = groups[1]
            # Safely find %idle which is the last column in standard mpstat layout
            parts = line.split()
            try:
                idle = float(parts[-1])
                total_cpu = 100.0 - idle

                data.append({
                    'time': time_str,
                    'cpu': cpu,
                    'total_cpu': total_cpu,
                    'usr': float(groups[2]),
                    'sys': float(groups[4]),
                    'soft': float(groups[7])
                })
            except ValueError:
                continue

    df = pd.DataFrame(data)
    if df.empty:
        raise ValueError("No valid mpstat metric rows could be parsed.")
    return df


def plot_metric(ax, df, metric, title):
    """Plot a single telemetry metric on the given axis.

    Args:
        ax (matplotlib.axes.Axes): The axis to plot on.
        df (pd.DataFrame): The parsed telemetry DataFrame.
        metric (str): The column name of the metric to plot.
        title (str): The title of the plot panel.
    """
    unique_times = df['time'].unique()
    time_map = {t: i for i, t in enumerate(unique_times)}

    for cpu_core in ['all', '0', '1', '2', '3']:
        core_df = df[df['cpu'] == cpu_core].copy()
        if core_df.empty:
            continue

        # Map timestamps to chronological sequence positions to avoid layout issues
        core_df['x'] = core_df['time'].map(time_map)
        core_df = core_df.sort_values('x')

        # Ensure the 'all' metric stands out visually with a slightly thicker line
        lw = 2.5 if cpu_core == 'all' else 1.5
        zorder = 5 if cpu_core == 'all' else 2

        ax.plot(
            core_df['x'], core_df[metric],
            label=f"Core {cpu_core}" if cpu_core != 'all' else "Total (all)",
            color=CORE_COLORS.get(cpu_core, '#7f8c8d'),
            linewidth=lw,
            zorder=zorder
        )

    ax.set_title(title, fontsize=12, fontweight='bold', loc='left')
    ax.set_ylabel('Percentage (%)')
    ax.grid(True, linestyle='--', alpha=0.5)

    # Set y-axis limits with padding
    max_val = df[metric].max()
    ylim_upper = 102 if metric == 'total_cpu' else max(max_val + 5, 15)
    ax.set_ylim(-2, ylim_upper)

    if metric == 'total_cpu':
        ax.legend(loc='upper right', ncol=5, frameon=True)


def generate_report(df, output_img):
    """Generate a 4-panel telemetry visualization plot.

    Args:
        df (pd.DataFrame): Parsed telemetry DataFrame.
        output_img (str): Path where the PNG image will be saved.
    """
    metrics = [
        ('total_cpu', 'Total CPU Usage (100% - %idle)'),
        ('usr', '%user Processing'),
        ('sys', '%sys Processing'),
        ('soft', '%soft (Software Interrupts)')
    ]

    _, axes = plt.subplots(4, 1, figsize=(14, 16), sharex=True)

    for ax, (metric, title) in zip(axes, metrics):
        plot_metric(ax, df, metric, title)

    # Clean up X-axis ticks using downsampled timestamps
    unique_times = df['time'].unique()
    x_indices = range(len(unique_times))
    step = max(1, len(unique_times) // 10)
    plt.xticks(
        list(x_indices)[::step],
        list(unique_times)[::step],
        rotation=45,
        ha='right'
    )
    plt.xlabel('Timestamp Sequence')

    plt.tight_layout()
    plt.savefig(output_img, dpi=150)
    print(f"✅ Telemetry plots successfully exported to: {output_img}")


def main():
    """Main program entry point to parse CLI arguments and run report generation."""
    desc = (
        'Parse mpstat performance logs and generate a 4-panel '
        'core-isolation analysis layout.'
    )
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('log_file', help='Path to target-mpstat raw output file')
    parser.add_argument(
        '--output', '-o',
        help='Output PNG path',
        default='mpstat_analysis.png'
    )
    args = parser.parse_args()

    try:
        telemetry_df = parse_mpstat(args.log_file)
        generate_report(telemetry_df, args.output)
    except Exception as error:  # pylint: disable=broad-exception-caught
        print(f"Error processing telemetry: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
