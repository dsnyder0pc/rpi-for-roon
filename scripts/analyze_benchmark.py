#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys

def analyze_capture(csv_file):
    print(f"Loading {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # --- 1. Stream Identification ---
    flow_counts = df.groupby(['eth.src', 'eth.dst']).size().reset_index(name='count')
    dominant_flow = flow_counts.loc[flow_counts['count'].idxmax()]
    host_mac = dominant_flow['eth.src']
    target_mac = dominant_flow['eth.dst']

    # Split Audio vs Noise
    audio_df = df[(df['eth.src'] == host_mac) & (df['eth.dst'] == target_mac)].copy()
    noise_df = df[~((df['eth.src'] == host_mac) & (df['eth.dst'] == target_mac))].copy()

    # --- 2. Metric Calculations ---
    audio_df['delta'] = audio_df['frame.time_relative'].diff()
    deltas_us = audio_df['delta'] * 1e6

    # Statistics
    duration = audio_df['frame.time_relative'].iloc[-1] - audio_df['frame.time_relative'].iloc[0]
    throughput_mbps = (audio_df['frame.len'].sum() * 8) / duration / 1e6

    mean_gap = deltas_us.mean()
    median_gap = deltas_us.median()
    std_dev = deltas_us.std()

    # Packet Sizes
    avg_frame = audio_df['frame.len'].mean()
    min_frame = audio_df['frame.len'].min()
    max_frame = audio_df['frame.len'].max()

    # Robust Jitter (1% - 99% percentile to ignore OS spikes)
    p01 = deltas_us.quantile(0.01)
    p99 = deltas_us.quantile(0.99)
    core_deltas = deltas_us[(deltas_us >= p01) & (deltas_us <= p99)]
    robust_std = core_deltas.std()

    # Stability Score (Packets < 1000us)
    total_packets = len(deltas_us)
    stable_packets = len(deltas_us[deltas_us <= 1000])
    stability_score = (stable_packets / total_packets) * 100

    # Mode Detection
    burst_count = len(deltas_us[deltas_us < 100])
    is_burst_mode = burst_count > (len(audio_df) * 0.1)

    # --- 3. Console Output (Strict Columns) ---
    # Columns: Label(20) | Value(12) | Unit(4) | Desc

    def p_row(label, val, unit, desc):
        print(f"{label:<20} {val:>12} {unit:<4} {desc}")

    print(f"\n{'--- Stream Summary ---':<40}")
    print(f"{'Flow:':<20} {host_mac} -> {target_mac}")
    print(f"{'Mode:':<20} {'BURST (High-Res)' if is_burst_mode else 'SINGLE FRAME (Standard)'}")
    p_row("Duration:", f"{duration:.2f}", "s", "")
    p_row("Packets:", f"{len(audio_df):,}", "", "")
    p_row("Throughput:", f"{throughput_mbps:.2f}", "Mbps", "")

    print(f"\n{'--- Timing Precision ---':<40}")
    p_row("Mean Interval:", f"{mean_gap:.2f}", "µs", "(Clock Sync)")
    p_row("Median Interval:", f"{median_gap:.2f}", "µs", "(Typical Gap)")
    p_row("Core Jitter:", f"{robust_std:.2f}", "µs", "(Excl. Outliers)")
    p_row("Total Jitter:", f"{std_dev:.2f}", "µs", "(Incl. Outliers)")

    print(f"\n{'--- Packet Sizes (Payload) ---':<40}")
    p_row("Avg Size:", f"{avg_frame:.0f}", "B", "(Wire Size)")
    p_row("Min / Max:", f"{min_frame:.0f} / {max_frame:.0f}", "B", "")

    print(f"\n{'--- Stability Events ---':<40}")
    p_row("Stability Score:", f"{stability_score:.5f}", "%", "(Packets < 1ms)")
    p_row("Max Pause:", f"{deltas_us.max()/1000:.2f}", "ms", "")
    long_gaps = len(deltas_us[deltas_us > 1000])
    p_row("Major Gaps:", f"{long_gaps}", "", "(Packets > 1000µs)")

    print(f"\n{'--- Isolation / Noise ---':<40}")
    noise_pct = (len(noise_df)/len(df))*100
    p_row("Noise Packets:", f"{len(noise_df):,}", "", f"({noise_pct:.2f}%)")

    if not noise_df.empty:
        print("\nTop Noise Sources:")
        print(noise_df['eth.type'].value_counts().head(3).to_string())

    # --- 4. Plotting ---
    plt.figure(figsize=(14, 12))

    # Plot 1: Precision Histogram
    plt.subplot(3, 1, 1)
    if is_burst_mode:
        plt.hist(core_deltas, bins=200, range=(0, 600), color='#2ecc71', edgecolor='none', alpha=0.8)
        plt.title(f"Burst Mode Timing Distribution (Core Jitter: {robust_std:.2f}µs)")
    else:
        plt.hist(core_deltas, bins=100, range=(450, 580), color='#2ecc71', edgecolor='black', alpha=0.7)
        plt.title(f"Single-Frame Timing Distribution (Core Jitter: {robust_std:.2f}µs)")
        plt.axvline(x=514, color='red', linestyle='--', label='Target 514µs')
        plt.legend()
    plt.ylabel("Count")
    plt.grid(True, alpha=0.3)

    # Plot 2: Stability Timeline
    plt.subplot(3, 1, 2)
    subset = audio_df.iloc[::50]
    plt.plot(subset['frame.time_relative'], subset['delta'] * 1e6,
             color='#2980b9', alpha=0.6, linewidth=0.5, label='Audio Interval')

    outliers = audio_df[audio_df['delta'] * 1e6 > 1000]
    if not outliers.empty:
        plt.scatter(outliers['frame.time_relative'], outliers['delta'] * 1e6,
                    color='red', s=20, zorder=5, label='>1ms Pause')

    plt.ylim(0, 1500)
    plt.title(f"Stream Stability (Max Pause: {deltas_us.max()/1000:.2f} ms)")
    plt.ylabel("Interval (µs)")
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)

    # Plot 3: Noise Forensics (Scatter)
    plt.subplot(3, 1, 3)
    if not noise_df.empty:
        plt.scatter(noise_df['frame.time_relative'], noise_df['frame.len'],
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
