#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def analyze_capture(csv_file):
    print(f"Loading {csv_file}...")
    try:
        # Load CSV with stripped column names to handle whitespace
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # --- 1. Stream Identification ---
    # We look for the dominant flow to automatically filter out unrelated traffic
    # Common Wireshark/TShark column names
    src_col = 'eth.src'
    dst_col = 'eth.dst'
    time_col = 'frame.time_relative' if 'frame.time_relative' in df.columns else 'time'
    len_col = 'frame.len'

    if time_col not in df.columns:
        print("Error: Could not find a timestamp column (frame.time_relative or time).")
        return

    # Find the pair of MAC addresses with the most packets
    if src_col in df.columns:
        flow_counts = df.groupby([src_col, dst_col]).size().reset_index(name='count')
        if flow_counts.empty:
            print("Error: No traffic found.")
            return
        dominant_flow = flow_counts.loc[flow_counts['count'].idxmax()]
        host_mac = dominant_flow[src_col]
        target_mac = dominant_flow[dst_col]

        # Filter: Audio Stream vs Noise
        audio_full_df = df[(df[src_col] == host_mac) & (df[dst_col] == target_mac)].copy()
        noise_df = df[~((df[src_col] == host_mac) & (df[dst_col] == target_mac))].copy()
    else:
        print("Warning: No MAC address columns found. Analyzing all packets as audio.")
        audio_full_df = df.copy()
        noise_df = pd.DataFrame() # Empty
        host_mac = "Unknown"
        target_mac = "Unknown"

    # --- 2. Phase Separation (Startup vs Steady State) ---
    STARTUP_TIME = 1.0 # Ignore the first 1.0 seconds for Core Jitter stats

    # Ensure time is sorted
    audio_full_df = audio_full_df.sort_values(by=time_col)

    # Startup Phase Data
    startup_df = audio_full_df[audio_full_df[time_col] <= STARTUP_TIME].copy()
    startup_df['delta'] = startup_df[time_col].diff()
    startup_deltas = startup_df['delta'] * 1e6 # microseconds

    # Steady State Data (The "Real" Benchmark)
    steady_df = audio_full_df[audio_full_df[time_col] > STARTUP_TIME].copy()
    steady_df['delta'] = steady_df[time_col].diff()

    # Fallback if capture is too short
    if steady_df.empty:
        print(f"Warning: Capture is shorter than {STARTUP_TIME}s. Using full data for stats.")
        steady_df = audio_full_df.copy()
        steady_df['delta'] = steady_df[time_col].diff()

    deltas_us = steady_df['delta'] * 1e6 # microseconds (Steady State)

    # --- 3. Metric Calculations ---

    # Throughput & Duration
    if len(steady_df) > 1:
        duration = steady_df[time_col].iloc[-1] - steady_df[time_col].iloc[0]
        throughput_mbps = (steady_df[len_col].sum() * 8) / duration / 1e6 if duration > 0 else 0
    else:
        duration = 0
        throughput_mbps = 0

    # Timing Stats
    mean_gap = deltas_us.mean()
    median_gap = deltas_us.median()
    std_dev = deltas_us.std() # Total Jitter (Steady State)

    # Packet Sizes
    avg_frame = steady_df[len_col].mean()
    min_frame = steady_df[len_col].min()
    max_frame = steady_df[len_col].max()

    # Robust Core Jitter (1% - 99% percentile of Steady State)
    # This filters out the random OS noise to find the engine's true precision
    p01 = deltas_us.quantile(0.01)
    p99 = deltas_us.quantile(0.99)
    core_deltas = deltas_us[(deltas_us >= p01) & (deltas_us <= p99)]
    robust_std = core_deltas.std()

    # Stability Score (Steady State)
    total_packets = len(deltas_us)
    stable_packets = len(deltas_us[deltas_us <= 1000])
    stability_score = (stable_packets / total_packets) * 100 if total_packets > 0 else 0

    # Mode Detection (Burst vs Single Frame)
    # If >10% of packets arrive instantly (<100us), it's Burst Mode
    burst_count = len(deltas_us[deltas_us < 100])
    is_burst_mode = burst_count > (len(steady_df) * 0.1)

    # --- 4. Console Output ---
    def p_row(label, val, unit, desc):
        print(f"{label:<22} {val:>12} {unit:<4} {desc}")

    print(f"\n{'--- Stream Summary ---':<45}")
    print(f"{'Flow:':<22} {host_mac} -> {target_mac}")
    print(f"{'Mode:':<22} {'BURST (High-Res)' if is_burst_mode else 'SINGLE FRAME (Standard)'}")
    p_row("Duration (Steady):", f"{duration:.2f}", "s", f"(Excludes first {STARTUP_TIME}s)")
    p_row("Packets (Steady):", f"{len(steady_df):,}", "", "")
    p_row("Throughput:", f"{throughput_mbps:.2f}", "Mbps", "")

    print(f"\n{'--- Timing Precision (Steady State) ---':<45}")
    p_row("Mean Interval:", f"{mean_gap:.2f}", "µs", "(Clock Sync)")
    p_row("Median Interval:", f"{median_gap:.2f}", "µs", "(Typical Gap)")
    p_row("Core Jitter:", f"{robust_std:.2f}", "µs", "(Excl. Outliers)")
    p_row("Total Jitter:", f"{std_dev:.2f}", "µs", "(Incl. Outliers)")

    print(f"\n{'--- Startup Phase (First 1s) ---':<45}")
    if not startup_df.empty:
        max_startup_pause = startup_deltas.max() / 1000
        # Count gaps > 1ms (1000us)
        startup_gaps = len(startup_deltas[startup_deltas > 1000])
        p_row("Startup Peak Pause:", f"{max_startup_pause:.2f}", "ms", "")
        p_row("Startup Gaps:", f"{startup_gaps}", "", "(Packets > 1000µs)")
    else:
        print("No startup data found.")

    print(f"\n{'--- Stability Events (Steady State) ---':<45}")
    p_row("Stability Score:", f"{stability_score:.5f}", "%", "(Packets < 1ms)")
    p_row("Max Pause:", f"{deltas_us.max()/1000:.2f}", "ms", "")
    long_gaps = len(deltas_us[deltas_us > 1000])
    p_row("Major Gaps:", f"{long_gaps}", "", "(Packets > 1000µs)")

    print(f"\n{'--- Isolation / Noise (Full Run) ---':<45}")
    noise_pct = (len(noise_df)/len(df))*100
    p_row("Noise Packets:", f"{len(noise_df):,}", "", f"({noise_pct:.2f}%)")

    if not noise_df.empty:
        print("\nTop Noise Sources:")
        # Try to use eth.type if available
        if 'eth.type' in noise_df.columns:
             print(noise_df['eth.type'].value_counts().head(3).to_string())
        else:
             print("(eth.type column missing, cannot identify protocols)")

    # --- 5. Plotting ---
    plt.figure(figsize=(14, 12))

    # Plot 1: Precision Histogram (Steady State ONLY)
    plt.subplot(3, 1, 1)
    if is_burst_mode:
        plt.hist(core_deltas, bins=200, range=(0, 600), color='#2ecc71', edgecolor='none', alpha=0.8)
        plt.title(f"Burst Mode Timing Distribution (Steady State Jitter: {robust_std:.2f}µs)")
    else:
        # Zoom in on the target interval
        plt.hist(core_deltas, bins=100, range=(450, 580), color='#2ecc71', edgecolor='black', alpha=0.7)
        plt.title(f"Single-Frame Timing Distribution (Steady State Jitter: {robust_std:.2f}µs)")
        plt.axvline(x=514, color='red', linestyle='--', label='Target 514µs')
        plt.legend()
    plt.ylabel("Count")
    plt.grid(True, alpha=0.3)

    # Plot 2: Stability Timeline (Full Run)
    plt.subplot(3, 1, 2)

    # Plot Startup Phase in Gray (Subsampled for speed)
    if not startup_df.empty:
        startup_sub = startup_df.iloc[::50]
        plt.plot(startup_sub[time_col], startup_sub['delta'] * 1e6,
                 color='gray', alpha=0.4, linewidth=0.5, label='Startup Phase')

        # Highlight startup gaps
        startup_outliers = startup_df[startup_df['delta'] * 1e6 > 1000]
        if not startup_outliers.empty:
             plt.scatter(startup_outliers[time_col], startup_outliers['delta'] * 1e6,
                        color='orange', s=15, zorder=5, label='Startup Gap')

    # Plot Steady State in Blue (Subsampled)
    steady_sub = steady_df.iloc[::50]
    plt.plot(steady_sub[time_col], steady_sub['delta'] * 1e6,
             color='#2980b9', alpha=0.6, linewidth=0.5, label='Steady State Audio')

    # Highlight Steady State Gaps in Red
    steady_outliers = steady_df[steady_df['delta'] * 1e6 > 1000]
    if not steady_outliers.empty:
        plt.scatter(steady_outliers[time_col], steady_outliers['delta'] * 1e6,
                    color='red', s=30, zorder=10, label='Steady State Gap')

    plt.axvline(x=STARTUP_TIME, color='black', linestyle=':', label='1s Threshold')

    plt.ylim(0, 1500)
    plt.title(f"Stream Stability (Gray = Startup, Blue = Steady State)")
    plt.ylabel("Interval (µs)")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)

    # Plot 3: Noise Forensics (Full Run)
    plt.subplot(3, 1, 3)
    if not noise_df.empty:
        plt.scatter(noise_df[time_col], noise_df[len_col],
                   color='#e74c3c', alpha=0.4, s=10, label='Noise Packet')
        plt.title(f"Noise Forensics: Packet Size vs Time (Total: {len(noise_df)})")
        plt.ylabel("Packet Size (Bytes)")
        plt.ylim(0, 1600)
    else:
        plt.text(0.5, 0.5, "Perfect Isolation (0 Noise)", ha='center', fontsize=12)
        plt.title("Noise Floor")

    plt.xlabel("Time (seconds)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    output_img = csv_file.replace('.csv', '_report.png')
    plt.savefig(output_img)
    print(f"\n✅ Graph generated: {output_img}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./analyze_benchmark.py <file.csv>")
        sys.exit(1)
    analyze_capture(sys.argv[1])
