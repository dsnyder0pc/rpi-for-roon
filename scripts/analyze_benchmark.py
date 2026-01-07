#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse

def analyze_capture(csv_file):
    print(f"Loading {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
        df.columns = df.columns.str.strip().str.lower()
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # --- 1. Stream Identification ---
    src_col = 'eth.src'
    dst_col = 'eth.dst'
    time_col = 'frame.time_relative' if 'frame.time_relative' in df.columns else 'time'
    len_col = 'frame.len'

    if time_col not in df.columns:
        print("Error: Could not find a timestamp column (frame.time_relative or time).")
        return

    # Find Dominant Flow
    if src_col in df.columns:
        flow_counts = df.groupby([src_col, dst_col]).size().reset_index(name='count')
        if flow_counts.empty:
            print("Error: No traffic found.")
            return
        dominant_flow = flow_counts.loc[flow_counts['count'].idxmax()]
        host_mac = dominant_flow[src_col]
        target_mac = dominant_flow[dst_col]

        # Split Data: Stream vs Noise
        stream_df = df[(df[src_col] == host_mac) & (df[dst_col] == target_mac)].copy()
        noise_df = df[~((df[src_col] == host_mac) & (df[dst_col] == target_mac))].copy()

        print(f"\n--- Stream Summary ---")
        print(f"Flow:                  {host_mac} -> {target_mac}")
    else:
        stream_df = df.copy()
        noise_df = pd.DataFrame()
        print("Warning: MAC address columns not found. Assuming single stream.")

    # Calculate Deltas on the Stream only
    stream_df['delta_s'] = stream_df[time_col].diff()
    stream_df['delta_us'] = stream_df['delta_s'] * 1e6
    stream_df = stream_df.iloc[1:].copy() # Drop first NaN

    # --- PASS 1: Detect CycleTime (Steady State) ---
    steady_df = stream_df[stream_df[time_col] > 1.0].copy()

    if steady_df.empty:
        print("Warning: Recording too short to detect steady state (>1.0s). Using all data.")
        steady_df = stream_df

    detected_cycle = steady_df['delta_us'].median()

    # Dynamic Thresholds
    gap_threshold = detected_cycle * 1.5
    stability_margin = 0.20
    stability_lower = detected_cycle * (1.0 - stability_margin)
    stability_upper = detected_cycle * (1.0 + stability_margin)

    print(f"Mode:                  Auto-Detected Cycle")
    print(f"Detected CycleTime:    {detected_cycle:.2f} µs")
    print(f"Dynamic Gap Threshold: > {gap_threshold:.2f} µs (1.5x Cycle)")

    # --- PASS 2: Analysis ---

    # Duration and Throughput
    duration = stream_df[time_col].max() - stream_df[time_col].min()
    total_bytes = stream_df[len_col].sum()
    throughput_mbps = (total_bytes * 8) / (duration * 1e6)

    print(f"Duration (Total):      {duration:.2f} s")
    print(f"Packets (Total):       {len(stream_df):,}")
    print(f"Throughput:            {throughput_mbps:.2f} Mbps")

    # Timing Stats
    mean_interval = steady_df['delta_us'].mean()
    std_dev = steady_df['delta_us'].std()
    q75, q25 = np.percentile(steady_df['delta_us'], [75 ,25])
    iqr = q75 - q25

    print(f"\n--- Timing Precision (Steady State) ---")
    print(f"Mean Interval:         {mean_interval:.2f} µs")
    print(f"Median Interval:       {detected_cycle:.2f} µs")
    print(f"Standard Deviation:    {std_dev:.2f} µs")
    print(f"Jitter (IQR):          {iqr:.2f} µs          (Core Stability)")

    # Startup & Stability
    startup_df = stream_df[stream_df[time_col] <= 1.0]
    startup_gaps = startup_df[startup_df['delta_us'] > gap_threshold]
    startup_peak = startup_df['delta_us'].max() / 1000.0

    major_gaps = steady_df[steady_df['delta_us'] > gap_threshold]
    max_pause_steady = steady_df['delta_us'].max() / 1000.0
    stable_packets = steady_df[
        (steady_df['delta_us'] >= stability_lower) &
        (steady_df['delta_us'] <= stability_upper)
    ]
    stability_score = (len(stable_packets) / len(steady_df)) * 100.0

    print(f"\n--- Stability Events (Steady State) ---")
    print(f"Stability Score:       {stability_score:.5f} %")
    print(f"Max Pause:             {max_pause_steady:.2f} ms")
    print(f"Major Gaps:            {len(major_gaps):<8} (Packets > {gap_threshold:.0f}µs)")

    # Noise Analysis
    print(f"\n--- Isolation / Noise (Full Run) ---")
    print(f"Noise Packets:         {len(noise_df):<8} ({len(noise_df)/len(df)*100:.2f}%)")
    if not noise_df.empty and 'eth.type' in noise_df.columns:
        print("\nTop Noise Sources (EtherType):")
        print(noise_df['eth.type'].value_counts().head(3).to_string())

    # --- Plotting ---
    plt.figure(figsize=(12, 12))

    # Plot 1: Jitter Distribution (Histogram) - [Restored to Top]
    plt.subplot(3, 1, 1)
    core_data = steady_df[steady_df['delta_us'] < (detected_cycle * 1.2)]

    if not core_data.empty:
        plt.hist(core_data['delta_us'], bins=100, color='#2ecc71', alpha=0.7)
        plt.title(f"Jitter Distribution (Steady State) - Target: {detected_cycle:.0f} µs")
        plt.xlabel("Interval (µs)")
        plt.ylabel("Packet Count")
        plt.grid(True, alpha=0.3)
        plt.xlim(detected_cycle * 0.8, detected_cycle * 1.2)
    else:
        plt.text(0.5, 0.5, "No stable packets found", ha='center')

    # Plot 2: Stream Stability (Scatter) - [Restored to Middle]
    plt.subplot(3, 1, 2)

    plot_df = stream_df.iloc[::10] if len(stream_df) > 100000 else stream_df
    mask_startup = plot_df[time_col] <= 1.0

    plt.scatter(plot_df[mask_startup][time_col], plot_df[mask_startup]['delta_us'],
               color='gray', alpha=0.5, s=2, label='Startup')
    plt.scatter(plot_df[~mask_startup][time_col], plot_df[~mask_startup]['delta_us'],
               color='#3498db', alpha=0.5, s=2, label='Steady State')

    plt.axhline(y=gap_threshold, color='r', linestyle='--', alpha=0.5, label=f'Gap Threshold ({gap_threshold:.0f}µs)')
    plt.axhline(y=detected_cycle, color='g', linestyle='-', alpha=0.3, label=f'Cycle ({detected_cycle:.0f}µs)')

    limit_y = detected_cycle * 4
    if limit_y < 100: limit_y = 100

    plt.ylim(0, limit_y)
    plt.title(f"Stream Stability (Gray = Startup, Blue = Steady State)")
    plt.ylabel("Interval (µs)")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.xlabel("Time (seconds)")

    # Plot 3: Noise Forensics (Bottom) - [Unchanged]
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
        plt.ylim(0, 100)

    plt.xlabel("Time (seconds)")
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    output_img = csv_file.replace('.csv', '_report.png')
    plt.savefig(output_img)
    print(f"\n✅ Graph generated: {output_img}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze Diretta CSV (Auto-Detect + Original Plot Layout)')
    parser.add_argument('csv_file', help='Path to the Wireshark CSV export')
    args = parser.parse_args()

    analyze_capture(args.csv_file)
