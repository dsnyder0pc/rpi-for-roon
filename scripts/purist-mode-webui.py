#!/usr/bin/env python
#
# AnCaolas Link System Control - A multi-page Flask application to control
# Diretta Purist Mode and Roon IR Remote settings.
# To be run on the Diretta Host.
#
import os
import subprocess
import json
import logging
import sys
from flask import Flask, render_template_string, jsonify, request, redirect, url_for, flash
from datetime import datetime, timedelta

# --- Configuration ---
REMOTE_USER = "purist-app"
REMOTE_HOST = "diretta-target"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/purist_app_key")
PLAYBACK_THRESHOLD_SECONDS = 15
ROON_CONFIG_PATH = os.path.expanduser('~/roon-ir-remote/app_info.json')


app = Flask(__name__)
# A secret key is required for flash messaging
app.secret_key = os.urandom(24)


# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- HTML & CSS TEMPLATES ---

# --- BASE TEMPLATE (Used by all pages) ---
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="bg-gray-900 text-gray-200">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AnCaolas Link Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <style type="text/tailwindcss">
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
        .nav-link {
            @apply px-4 py-2 text-gray-300 rounded-md border border-gray-600 hover:bg-green-600 hover:border-green-500 hover:text-white transition-colors;
        }
        .nav-link.active {
            @apply bg-blue-600 text-white border-blue-500;
        }
        .flash-message {
            @apply p-4 mb-4 text-sm text-green-400 bg-green-800/50 rounded-lg;
        }
    </style>
</head>
<body class="antialiased">
    <div class="max-w-2xl mx-auto p-4 sm:p-6 lg:p-8">
        <div class="text-center mb-6">
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white">AnCaolas Link</h1>
            <p class="text-lg text-gray-400">System Control</p>
        </div>

        <nav class="flex justify-center items-center mb-8 p-2 space-x-4">
            <a href="{{ url_for('landing_page') }}" class="nav-link {{ 'active' if active_page == 'home' else '' }}">Home</a>
            <a href="{{ url_for('purist_app') }}" class="nav-link {{ 'active' if active_page == 'purist' else '' }}">Purist Mode</a>
            {% if roon_is_configured %}
            <a href="{{ url_for('remote_app') }}" class="nav-link {{ 'active' if active_page == 'remote' else '' }}">IR Remote</a>
            {% endif %}
        </nav>

        {% with messages = get_flashed_messages() %}
            {% if messages %}
                <div class="flash-message" role="alert">
                    {{ messages[0] }}
                </div>
            {% endif %}
        {% endwith %}

        {{ content | safe }}

        <div class="text-center mt-8 text-sm text-gray-500">
            <p>&copy; 2025 AnCaolas Link</p>
        </div>
    </div>
</body>
</html>
"""

# --- LANDING PAGE ---
LANDING_PAGE_CONTENT = """
<div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 text-center space-y-6">
    <h2 class="text-2xl font-bold text-white">Welcome</h2>
    <p class="text-gray-400">Please choose a control panel to continue.</p>
    <div class="flex justify-center gap-4">
        <a href="{{ url_for('purist_app') }}" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            Purist Mode Control
        </a>
        {% if roon_is_configured %}
        <a href="{{ url_for('remote_app') }}" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
            IR Remote Control
        </a>
        {% endif %}
    </div>
</div>
"""

# --- PURIST MODE APP ---
PURIST_APP_TEMPLATE = """
<div id="control-panel" hx-get="/status" hx-trigger="load, every 30s, visibilitychange from:document" hx-swap="innerHTML">
    <div class="p-8 text-center text-gray-400">
        <div class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" role="status"></div>
        <p class="mt-2">Connecting to Diretta Target...</p>
    </div>
</div>
"""

STATUS_PANEL_TEMPLATE = """
<div class="space-y-6">
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
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8">
        <div class="flex items-center justify-between">
            <div>
                <h2 class="font-semibold text-lg text-white">License Activation</h2>
                <p class="text-sm text-yellow-400">Trial license detected. Restart after activation.</p>
            </div>
            <button hx-post="/restart-target" hx-target="#restart-message" hx-swap="innerHTML"
                    class="relative inline-flex items-center justify-center w-40 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200 bg-blue-600 hover:bg-blue-500 text-white">
                <span class="btn-text">Restart Services</span>
                <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
            </button>
        </div>
        <div id="restart-message" class="mt-4 text-center text-green-400 h-5"></div>
    </div>
    {% endif %}
</div>
"""

# --- IR REMOTE APP ---
REMOTE_APP_TEMPLATE = """
<div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8">
    <h2 class="text-xl font-bold text-white mb-4">Roon IR Remote Zone</h2>
    <p class="text-gray-400 mb-6">Enter the exact name of the Roon Zone you want the IR remote to control.</p>
    <form method="POST">
        <div class="flex items-center space-x-4">
            <input type="text" name="zone_name" value="{{ current_zone }}"
                   class="flex-grow bg-gray-900 border border-gray-600 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
            <button type="submit"
                    class="inline-flex items-center justify-center w-28 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200 bg-green-600 hover:bg-green-500 text-white">
                Save
            </button>
        </div>
    </form>
</div>
"""

# --- MUSIC PLAYING TEMPLATE ---
MUSIC_PLAYING_TEMPLATE = """
<div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 text-center" hx-get="/status" hx-trigger="every 5s" hx-swap="outerHTML">
    <div class="flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2C6.486 2 2 6.486 2 12s4.486 10 10 10 10-4.486 10-10S17.514 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8z"></path>
          <path d="M13 12.434V8a1 1 0 0 0-2 0v5a1 1 0 0 0 .553.894l3 1.5a1 1 0 0 0 .447-1.939L13 12.434z"></path>
        </svg>
    </div>
    <h2 class="text-xl font-bold text-white mb-2">Shhhh... Music in Progress</h2>
    <p class="text-gray-400">The control panel is paused to ensure an uninterrupted performance.
    <br>It will automatically reappear up to a minute after the music has finished.</p>
</div>
"""

# --- BACKEND LOGIC (Helper Functions) ---

def is_music_playing():
    """Checks if music is actively playing by inspecting the local Diretta Host log."""
    try:
        # Check the local diretta_alsa.service log on the Host
        cmd = ["journalctl", "-u", "diretta_alsa.service", "--no-pager", "-n", "20", "-g", "info rcv"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0 or not result.stdout:
            return False

        last_line = result.stdout.strip().split('\n')[-1]
        log_time_str = ' '.join(last_line.split()[:3])
        log_time = datetime.strptime(log_time_str, "%b %d %H:%M:%S").replace(year=datetime.now().year)

        now = datetime.now()
        # Handle year-end case: if log is Dec and now is Jan, log was last year.
        if log_time > now and log_time.month == 12 and now.month == 1:
            log_time = log_time.replace(year=now.year - 1)

        delta = now - log_time
        if 0 <= delta.total_seconds() < PLAYBACK_THRESHOLD_SECONDS:
            app.logger.info(f"Playback detected on Host. Last log entry was {delta.total_seconds():.2f}s ago.")
            return True

    except Exception as e:
        app.logger.error(f"Error checking playback status on Host: {e}")
        return False

    app.logger.info("No recent playback detected on Host.")
    return False

def run_remote_command(command):
    """Executes a command on the Diretta Target via SSH."""
    ssh_command = ["ssh", "-i", SSH_KEY_PATH, "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", f"{REMOTE_USER}@{REMOTE_HOST}", command]
    try:
        app.logger.info(f"Running remote command: {' '.join(ssh_command)}")
        result = subprocess.run(ssh_command, capture_output=True, text=True, check=True, timeout=15)
        app.logger.info(f"Remote command successful. Output: {result.stdout.strip()}")
        return result.stdout.strip()
    except Exception as e:
        app.logger.error(f"Remote command failed: {e}")
        return None

def get_status_from_target():
    """Gets the current status from the Diretta Target."""
    raw_status = run_remote_command("/usr/local/bin/pm-get-status")
    if not raw_status: return None
    try:
        return json.loads(raw_status)
    except json.JSONDecodeError:
        app.logger.error(f"Failed to decode JSON status from remote host. Received: {raw_status}")
        return None

def get_roon_zone_from_host():
    """Gets the current Roon zone name from the local config file."""
    if not os.path.exists(ROON_CONFIG_PATH): return "Not Configured"
    try:
        with open(ROON_CONFIG_PATH, 'r') as f: config = json.load(f)
        return config.get('roon', {}).get('zone', {}).get('name', 'Not Set')
    except Exception: return "Error Reading Config"

# --- FLASK ROUTES ---

@app.route("/")
def landing_page():
    """Serves the main landing page."""
    content = render_template_string(LANDING_PAGE_CONTENT, roon_is_configured=os.path.exists(ROON_CONFIG_PATH))
    return render_template_string(BASE_TEMPLATE, content=content, active_page='home', roon_is_configured=os.path.exists(ROON_CONFIG_PATH))

@app.route("/purist")
def purist_app():
    """Serves the Purist Mode control application."""
    content = render_template_string(PURIST_APP_TEMPLATE)
    return render_template_string(BASE_TEMPLATE, content=content, active_page='purist', roon_is_configured=os.path.exists(ROON_CONFIG_PATH))

@app.route("/remote", methods=['GET', 'POST'])
def remote_app():
    """Serves the IR Remote control application."""
    if not os.path.exists(ROON_CONFIG_PATH):
        return redirect(url_for('landing_page'))

    if request.method == 'POST':
        new_zone_name = request.form.get('zone_name')
        if not new_zone_name:
            flash("Error: No zone name provided.")
        else:
            try:
                with open(ROON_CONFIG_PATH, 'r') as f: config = json.load(f)
                config['roon']['zone']['name'] = new_zone_name
                with open(ROON_CONFIG_PATH, 'w') as f: json.dump(config, f, indent=2)
                subprocess.run(['sudo', 'systemctl', 'restart', 'roon-ir-remote.service'], check=True)
                app.logger.info(f"Roon zone updated to '{new_zone_name}' and service restarted.")
                flash(f"Successfully updated Roon Zone to: {new_zone_name}")
            except Exception as e:
                app.logger.error(f"Failed to update Roon zone: {e}")
                flash(f"An error occurred: {e}")
        return redirect(url_for('remote_app'))

    # For GET request
    current_zone = get_roon_zone_from_host()
    content = render_template_string(REMOTE_APP_TEMPLATE, current_zone=current_zone)
    return render_template_string(BASE_TEMPLATE, content=content, active_page='remote', roon_is_configured=os.path.exists(ROON_CONFIG_PATH))

# --- HTMX API Endpoints (for Purist App) ---

@app.route("/status")
def status():
    """Serves the status panel for HTMX updates."""
    if is_music_playing():
        return render_template_string(MUSIC_PLAYING_TEMPLATE)
    target_status = get_status_from_target()
    if target_status is None:
        return '<div class="p-8 text-center text-red-400">Error: Could not connect to Diretta Target.</div>'
    return render_template_string(STATUS_PANEL_TEMPLATE, status=target_status)

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
    """Restarts Diretta on Target and Roon Bridge on Host."""
    run_remote_command("/usr/local/bin/pm-restart-target")
    subprocess.run(['sudo', 'systemctl', 'restart', 'roonbridge.service'], check=True)
    app.logger.info("Roon Bridge service on Host restarted.")
    now = datetime.now().strftime("%H:%M:%S")
    return f"""
    <span>Restart commands sent at {now}. Page will refresh shortly.</span>
    <div hx-trigger="load delay:3s" hx-get="/status" hx-target="#control-panel"></div>
    """

if __name__ == "__main__":
    is_interactive = sys.stdout.isatty()
    port = 8080 if is_interactive else 80
    debug_mode = is_interactive
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
