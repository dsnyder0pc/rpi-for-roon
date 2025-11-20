#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# --- Configuration ---
# Adjust these filenames if necessary or pass them as command line arguments
# Usage: ./plot_traffic.py [raat_csv_file] [diretta_csv_file]
DEFAULT_RAAT_CSV = "raat_input_20251118_193906.csv"
DEFAULT_DIRETTA_CSV = "diretta_output_20251118_193906.csv"

def load_data(filename):
    """Loads CSV data into a Pandas DataFrame."""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)
    return pd.read_csv(filename)

def calculate_throughput(df, window_size='100ms'):
    """
    Calculates throughput in Mbps by resampling the packet sizes over time.
    Assumes 'frame.time_relative' is in seconds.
    """
    # Convert relative time to a proper Timedelta index for resampling
    df['time_delta'] = pd.to_timedelta(df['frame.time_relative'], unit='s')
    df = df.set_index('time_delta')

    # Resample and sum packet lengths (in bytes)
    resampled = df['frame.len'].resample(window_size).sum().fillna(0)

    # Convert Bytes -> Bits -> Megabits
    # Window size needs to be normalized to seconds to get Mbps rate
    window_seconds = pd.to_timedelta(window_size).total_seconds()
    throughput_mbps = (resampled * 8) / (1_000_000 * window_seconds)

    # Convert index back to seconds (float) for plotting
    time_seconds = resampled.index.total_seconds()

    return time_seconds, throughput_mbps

def find_busiest_window_centered(df, window_span=0.004):
    """
    Finds the window with the most packets and centers it.
    This ensures the micro-view isn't empty and looks nice.
    """
    # Create a simple histogram/density check
    # Bin data into 0.1ms chunks for finer resolution
    bins = np.arange(df['frame.time_relative'].min(), df['frame.time_relative'].max(), 0.0001)
    counts, edges = np.histogram(df['frame.time_relative'], bins=bins)

    # Find the index of the bin with the max packets
    max_idx = np.argmax(counts)

    # The peak time is the center of that bin
    peak_time = (edges[max_idx] + edges[max_idx+1]) / 2

    # Calculate start time so peak is in the middle of the window
    start_time = peak_time - (window_span / 2)

    return start_time

def plot_graphs(raat_df, diretta_df):
    """Generates the 2x2 comparison plot."""

    # --- 1. Macro View Data Preparation (Throughput) ---
    t_raat, bw_raat = calculate_throughput(raat_df, window_size='10ms')
    t_diretta, bw_diretta = calculate_throughput(diretta_df, window_size='10ms')

    # Define a 30s window for the Macro View
    macro_start = 15.0
    macro_end = 45.0

    # --- 2. Micro View Data Preparation (Packet Zoom) ---
    # Automatically find a busy spot in the RAAT stream
    raat_segment = raat_df[(raat_df['frame.time_relative'] >= macro_start) &
                           (raat_df['frame.time_relative'] <= macro_end)]

    if not raat_segment.empty:
        # Find the busiest packet burst and center the window around it
        micro_start = find_busiest_window_centered(raat_segment)
    else:
        micro_start = macro_start + 10

    micro_span = 0.004 # 4ms
    micro_end = micro_start + micro_span

    print(f"Auto-selected Micro Zoom Window (Centered): {micro_start:.4f}s to {micro_end:.4f}s")

    # Filter DataFrames for the Micro View
    raat_micro = raat_df[(raat_df['frame.time_relative'] >= micro_start) &
                         (raat_df['frame.time_relative'] <= micro_end)]

    diretta_micro = diretta_df[(diretta_df['frame.time_relative'] >= micro_start) &
                               (diretta_df['frame.time_relative'] <= micro_end)]

    # --- 3. Plotting ---
    fig, axs = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('Network Traffic Analysis: RAAT vs. Diretta (Logarithmic Scale)', fontsize=16)

    # --- Top Left: RAAT Macro (Throughput) ---
    axs[0, 0].plot(t_raat, bw_raat, color='#E24A33', linewidth=1)
    axs[0, 0].set_title('RAAT Input (30s Window): The Sawtooth', fontsize=14)
    axs[0, 0].set_ylabel('Throughput (Mbps) - Log Scale')
    axs[0, 0].set_yscale('log')
    axs[0, 0].set_xlim(macro_start, macro_end)
    axs[0, 0].set_ylim(0.1, 150)
    axs[0, 0].grid(True, which="both", ls="-", alpha=0.3)

    # --- Top Right: Diretta Macro (Throughput) ---
    axs[0, 1].plot(t_diretta, bw_diretta, color='#348ABD', linewidth=1)
    axs[0, 1].set_title('Diretta Output (30s Window): The Flatline', fontsize=14)
    axs[0, 1].set_ylabel('Throughput (Mbps) - Log Scale')
    axs[0, 1].set_yscale('log')
    axs[0, 1].set_xlim(macro_start, macro_end)
    axs[0, 1].set_ylim(0.1, 150)
    axs[0, 1].grid(True, which="both", ls="-", alpha=0.3)

    # --- Bottom Left: RAAT Micro (Packet Size) ---
    if not raat_micro.empty:
        axs[1, 0].stem(raat_micro['frame.time_relative'], raat_micro['frame.len'],
                       linefmt='#E24A33', markerfmt='o', basefmt=" ")
    axs[1, 0].set_title('RAAT Micro-View (4ms Zoom): Packet Clumping', fontsize=14)
    axs[1, 0].set_ylabel('Packet Size (Bytes) - Log Scale')
    axs[1, 0].set_xlabel('Time (seconds)')
    axs[1, 0].set_yscale('log')
    axs[1, 0].set_xlim(micro_start, micro_end)
    axs[1, 0].set_ylim(40, 2000)
    axs[1, 0].grid(True, which="both", ls="-", alpha=0.3)

    # --- Bottom Right: Diretta Micro (Packet Size) ---
    if not diretta_micro.empty:
        axs[1, 1].stem(diretta_micro['frame.time_relative'], diretta_micro['frame.len'],
                       linefmt='#348ABD', markerfmt='o', basefmt=" ")

    axs[1, 1].set_title('Diretta Micro-View (4ms Zoom): Even Spacing', fontsize=14)
    axs[1, 1].set_ylabel('Packet Size (Bytes) - Log Scale')
    axs[1, 1].set_xlabel('Time (seconds)')
    axs[1, 1].set_yscale('log')
    axs[1, 1].set_xlim(micro_start, micro_end)
    axs[1, 1].set_ylim(40, 2000)
    axs[1, 1].grid(True, which="both", ls="-", alpha=0.3)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    # Handle command line args
    raat_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RAAT_CSV
    diretta_file = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DIRETTA_CSV

    print(f"Loading RAAT data from: {raat_file}")
    raat_df = load_data(raat_file)

    print(f"Loading Diretta data from: {diretta_file}")
    diretta_df = load_data(diretta_file)

    print("Generating plots...")
    plot_graphs(raat_df, diretta_df)
