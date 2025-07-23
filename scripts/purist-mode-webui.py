#!/usr/bin/env python
#
# Purist Mode Web UI - A Flask application to control Purist Mode on a remote Diretta Target.
# To be run on the Diretta Host.
#
import os
import subprocess
import json
from flask import Flask, render_template_string, jsonify, request

# --- Configuration ---
# The user that the web app will use to SSH into the Target.
REMOTE_USER = "purist-app"
# The hostname of the Diretta Target (should be in /etc/hosts).
REMOTE_HOST = "diretta-target"
# The path to the private SSH key for the purist-app user.
SSH_KEY_PATH = os.path.expanduser("~/.ssh/purist_app_key")

app = Flask(__name__)

# --- HTML & CSS Template ---
# A single, self-contained template using Tailwind CSS for styling.
# It uses htmx to handle interactions without full page reloads for a smoother experience.
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
        /* HTMX indicator styles */
        .htmx-request .btn-spinner { display: inline-block; }
        .htmx-request .btn-text { opacity: 0; }
        .htmx-request button { cursor: not-allowed; }
    </style>
</head>
<body class="antialiased">
    <div class="max-w-2xl mx-auto p-4 sm:p-6 lg:p-8">
        <!-- Header -->
        <div class="text-center mb-8">
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white">AnCaolas Link</h1>
            <p class="text-lg text-gray-400">Purist Mode Control</p>
        </div>

        <!-- Status & Control Panel -->
        <div id="status-panel" 
             class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10"
             hx-get="/status" 
             hx-trigger="load, every 5s">
            <!-- This content will be replaced by the /status endpoint -->
            <div class="p-8 text-center text-gray-400">
                <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status"></div>
                <p class="mt-2">Connecting to Diretta Target...</p>
            </div>
        </div>

        <!-- Footer -->
        <div class="text-center mt-8 text-sm text-gray-500">
            <p>&copy; 2025 AnCaolas Link</p>
        </div>
    </div>
</body>
</html>
"""

# --- Status Panel Template ---
# This is a partial template that htmx will use to update the status panel.
STATUS_PANEL_TEMPLATE = """
<div class="p-6 sm:p-8 space-y-6">
    <!-- Purist Mode Status & Toggle -->
    <div class="flex items-center justify-between p-4 bg-gray-700/50 rounded-xl">
        <div>
            <h2 class="font-semibold text-lg text-white">Purist Mode</h2>
            {% if status.purist_mode_active %}
                <p class="text-sm text-green-400">ACTIVE - Optimized for critical listening.</p>
            {% else %}
                <p class="text-sm text-yellow-400">DISABLED - System in standard mode.</p>
            {% endif %}
        </div>
        <button hx-post="/toggle-mode" hx-target="#status-panel" hx-swap="outerHTML"
                class="relative inline-flex items-center justify-center w-28 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                       {% if status.purist_mode_active %} bg-red-600 hover:bg-red-500 text-white {% else %} bg-green-600 hover:bg-green-500 text-white {% endif %}">
            <span class="btn-text">{% if status.purist_mode_active %}Disable{% else %}Enable{% endif %}</span>
            <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
        </button>
    </div>

    <!-- Auto-Start on Boot Status & Toggle -->
    <div class="flex items-center justify-between p-4 bg-gray-700/50 rounded-xl">
        <div>
            <h2 class="font-semibold text-lg text-white">Activate on Boot</h2>
            {% if status.auto_start_enabled %}
                <p class="text-sm text-green-400">ENABLED - Will activate 60s after boot.</p>
            {% else %}
                <p class="text-sm text-yellow-400">DISABLED - System will remain in standard mode.</p>
            {% endif %}
        </div>
        <button hx-post="/toggle-auto" hx-target="#status-panel" hx-swap="outerHTML"
                class="relative inline-flex items-center justify-center w-28 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                       {% if status.auto_start_enabled %} bg-red-600 hover:bg-red-500 text-white {% else %} bg-green-600 hover:bg-green-500 text-white {% endif %}">
            <span class="btn-text">{% if status.auto_start_enabled %}Disable{% else %}Enable{% endif %}</span>
            <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
        </button>
    </div>
</div>
"""

# --- Backend Logic ---

def run_remote_command(command):
    """Executes a command on the Diretta Target via SSH."""
    ssh_command = [
        "ssh",
        "-i", SSH_KEY_PATH,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        command
    ]
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, check=True, timeout=15)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Remote command failed: {e.stderr}")
        return None
    except subprocess.TimeoutExpired:
        app.logger.error("Remote command timed out.")
        return None
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")
        return None

def get_status():
    """Gets the current status from the Diretta Target."""
    raw_status = run_remote_command("get-status")
    if raw_status:
        try:
            return json.loads(raw_status)
        except json.JSONDecodeError:
            app.logger.error("Failed to decode JSON status from remote host.")
            return None
    return None

@app.route("/")
def index():
    """Serves the main page."""
    return render_template_string(HTML_TEMPLATE)

@app.route("/status")
def status():
    """Serves the status panel, intended for HTMX updates."""
    current_status = get_status()
    if current_status is None:
        # Return an error message if we can't get the status
        return '<div class="p-8 text-center text-red-400">Error: Could not connect to Diretta Target. Please check the connection and try again.</div>'
    return render_template_string(STATUS_PANEL_TEMPLATE, status=current_status)

@app.route("/toggle-mode", methods=["POST"])
def toggle_mode():
    """Toggles Purist Mode on/off."""
    run_remote_command("toggle-mode")
    return status() # Return the updated status panel

@app.route("/toggle-auto", methods=["POST"])
def toggle_auto():
    """Toggles the auto-start service on/off."""
    run_remote_command("toggle-auto")
    return status() # Return the updated status panel

if __name__ == "__main__":
    # Note: For production, use a proper WSGI server like Gunicorn or Waitress.
    # For this simple, private network use case, the Flask dev server is sufficient.
    # We bind to 0.0.0.0 to make it accessible from other devices on the LAN.
    app.run(host="0.0.0.0", port=80)

