#!/usr/bin/env python
#
# Purist Mode Web UI - A Flask application to control Purist Mode on a remote Diretta Target.
# To be run on the Diretta Host.
#
import os
import subprocess
import json
import logging
import sys
from flask import Flask, render_template_string, jsonify
from datetime import datetime, timedelta

# --- Configuration ---
REMOTE_USER = "purist-app"
REMOTE_HOST = "diretta-target"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/purist_app_key")
# The number of seconds of inactivity before we assume music is no longer playing.
PLAYBACK_THRESHOLD_SECONDS = 15

app = Flask(__name__)

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- HTML & CSS Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-900 text-gray-200">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnCaolas Link Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
        .btn-spinner {
            border-top-color: transparent;
            border-right-color: transparent;
            animation: spin 0.6s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .htmx-request .btn-spinner { display: inline-block; }
        .htmx-request .btn-text { opacity: 0; }
        .htmx-request button { cursor: not-allowed; }
    </style>
</head>
<body class="antialiased">
    <div class="max-w-2xl mx-auto p-4 sm:p-6 lg:p-8">
        <div class="text-center mb-8">
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white">AnCaolas Link</h1>
            <p class="text-lg text-gray-400">System Control</p>
        </div>

        <div id="control-panel" hx-get="/status" hx-trigger="load, every 30s, visibilitychange from:document" hx-swap="innerHTML">
            <div class="p-8 text-center text-gray-400">
                <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status"></div>
                <p class="mt-2">Connecting to Diretta Target...</p>
            </div>
        </div>

        <div class="text-center mt-8 text-sm text-gray-500">
            <p>&copy; 2025 AnCaolas Link</p>
        </div>
    </div>
</body>
</html>
"""

# This is the partial template that htmx will swap into the page.
STATUS_PANEL_TEMPLATE = """
<div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 space-y-6">
    <div class="flex items-center justify-between p-4 bg-gray-700/50 rounded-xl">
        <div>
            <h2 class="font-semibold text-lg text-white">Purist Mode</h2>
            {% if status.purist_mode_active %}
                <p class="text-sm text-green-400">ACTIVE - Optimized for critical listening.</p>
            {% else %}
                <p class="text-sm text-yellow-400">DISABLED - System in standard mode.</p>
            {% endif %}
        </div>
        <button hx-post="/toggle-mode" hx-target="#control-panel" hx-swap="innerHTML"
                class="relative inline-flex items-center justify-center w-28 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                       {% if status.purist_mode_active %} bg-green-600 hover:bg-green-500 text-white {% else %} bg-yellow-600 hover:bg-yellow-500 text-gray-900 {% endif %}">
            <span class="btn-text">{% if status.purist_mode_active %}Disable{% else %}Enable{% endif %}</span>
            <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
        </button>
    </div>

    <div class="flex items-center justify-between p-4 bg-gray-700/50 rounded-xl">
        <div>
            <h2 class="font-semibold text-lg text-white">Activate on Boot</h2>
            {% if status.auto_start_enabled %}
                <p class="text-sm text-green-400">ENABLED - Will activate 60s after boot.</p>
            {% else %}
                <p class="text-sm text-yellow-400">DISABLED - System will remain in standard mode.</p>
            {% endif %}
        </div>
        <button hx-post="/toggle-auto" hx-target="#control-panel" hx-swap="innerHTML"
                class="relative inline-flex items-center justify-center w-28 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                       {% if status.auto_start_enabled %} bg-green-600 hover:bg-green-500 text-white {% else %} bg-yellow-600 hover:bg-yellow-500 text-gray-900 {% endif %}">
            <span class="btn-text">{% if status.auto_start_enabled %}Disable{% else %}Enable{% endif %}</span>
            <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
        </button>
    </div>
</div>

{% if status.license_needs_activation %}
<div class="mt-8 bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8">
    <div class="flex items-center justify-between">
        <div>
            <h2 class="font-semibold text-lg text-white">License Activation</h2>
            <p class="text-sm text-yellow-400">Trial license detected. Restart after activation.</p>
        </div>
        <button hx-post="/restart-target" hx-target="#restart-message" hx-swap="innerHTML"
                class="relative inline-flex items-center justify-center w-40 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200 bg-blue-600 hover:bg-blue-500 text-white">
            <span class="btn-text">Restart Diretta</span>
            <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
        </button>
    </div>
    <div id="restart-message" class="mt-4 text-center text-green-400 h-5">
        </div>
</div>
{% endif %}
"""

# Template to display when music is playing. It polls to auto-restore the UI.
MUSIC_PLAYING_TEMPLATE = """
<div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 text-center">
    <div class="flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"></path>
          <path d="M13 12.434V8a1 1 0 0 0-2 0v5a1 1 0 0 0 .553.894l3 1.5a1 1 0 0 0 .447-1.939L13 12.434z"></path>
        </svg>
    </div>
    <h2 class="text-xl font-bold text-white mb-2">Shhhh... Music in Progress</h2>
    <p class="text-gray-400">The control panel is paused to ensure an uninterrupted performance.
    <br>It will automatically reappear after the music has finished.</p>
</div>
"""


# --- Backend Logic ---

def is_music_playing():
    """
    Checks if music is actively playing by inspecting the Diretta service log.
    Returns True if a recent 'info rcv' entry is found, False otherwise.
    """
    try:
        # Use journalctl to get the last log line containing "info rcv"
        cmd = [
            "journalctl",
            "-u", "diretta_alsa.service",
            "--no-pager",
            "-n", "20", # Check the last 20 lines for a recent entry
            "-g", "info rcv" # Grep for the relevant line
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0 or not result.stdout:
            # Command failed or returned no lines
            return False

        # Get the very last log line from the output
        last_line = result.stdout.strip().split('\n')[-1]

        # Extract timestamp (e.g., "Jul 26 08:49:32")
        log_time_str = ' '.join(last_line.split()[:3])

        # Parse the timestamp, which lacks a year.
        log_time = datetime.strptime(log_time_str, "%b %d %H:%M:%S")
        now = datetime.now()

        # Assume the log entry is from the current year.
        log_time = log_time.replace(year=now.year)

        # Handle year-end case: if log is Dec and now is Jan, log was last year.
        if log_time > now:
            log_time = log_time.replace(year=now.year - 1)

        # Check if the log entry is recent.
        delta = now - log_time
        if delta.total_seconds() < PLAYBACK_THRESHOLD_SECONDS:
            app.logger.info(f"Playback detected. Last log entry was {delta.total_seconds():.2f}s ago.")
            return True

    except (subprocess.TimeoutExpired, FileNotFoundError, IndexError, ValueError) as e:
        app.logger.error(f"Error checking playback status: {e}")
        return False

    app.logger.info("No recent playback detected.")
    return False


def run_remote_command(command):
    """Executes a command on the Diretta Target via SSH."""
    ssh_command = [
        "ssh",
        "-i", SSH_KEY_PATH,
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        command
    ]
    try:
        app.logger.info(f"Running remote command: {' '.join(ssh_command)}")
        result = subprocess.run(ssh_command, capture_output=True, text=True, check=True, timeout=15)
        app.logger.info(f"Remote command successful. Output: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Remote command failed with exit code {e.returncode}. Stderr: {e.stderr.strip()}")
        return None
    except subprocess.TimeoutExpired:
        app.logger.error("Remote command timed out.")
        return None
    except Exception as e:
        app.logger.error(f"An unexpected SSH error occurred: {e}")
        return None

def get_status():
    """Gets the current status from the Diretta Target."""
    raw_status = run_remote_command("/usr/local/bin/pm-get-status")
    if not raw_status:
        app.logger.error("Did not receive any status data from remote host.")
        return None
    try:
        return json.loads(raw_status)
    except json.JSONDecodeError:
        app.logger.error(f"Failed to decode JSON status from remote host. Received: {raw_status}")
        return None

@app.route("/")
def index():
    """Serves the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/status")
def status():
    """
    Serves the status panel, intended for HTMX updates.
    First checks for active playback before making remote calls.
    """
    if is_music_playing():
        # If music is playing, show the "shhhh" message and keep polling.
        return render_template_string(MUSIC_PLAYING_TEMPLATE)

    # If no music, proceed to get status from the Target.
    current_status = get_status()
    if current_status is None:
        return '<div class="p-8 text-center text-red-400">Error: Could not connect to Diretta Target. Please check the connection and try again.</div>'

    # Render the full control panel, which will re-enable polling.
    return render_template_string(STATUS_PANEL_TEMPLATE, status=current_status)


@app.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    """Toggles Purist Mode on/off."""
    run_remote_command("/usr/local/bin/pm-toggle-mode")
    return status()

@app.route("/toggle-auto", methods=["POST"])
def toggle_auto():
    """Toggles the auto-start service on/off."""
    run_remote_command("/usr/local/bin/pm-toggle-auto")
    return status()

@app.route("/restart-target", methods=["POST"])
def restart_target():
    """Restarts the Diretta service on the Target."""
    run_remote_command("/usr/local/bin/pm-restart-target")
    now = datetime.now().strftime("%H:%M:%S")
    # Return a confirmation message that will trigger a status refresh after a delay.
    return f"""
    <span>Restart command sent at {now}. Page will refresh shortly.</span>
    <div hx-trigger="load delay:3s" hx-get="/status" hx-target="#control-panel"></div>
    """

if __name__ == "__main__":
    is_interactive = sys.stdout.isatty()
    port = 8080 if is_interactive else 80
    debug_mode = is_interactive

    app.logger.info(f"Starting Flask server. Interactive: {is_interactive}, Port: {port}, Debug: {debug_mode}")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
