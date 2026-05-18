#!/usr/bin/env python
"""
AnCaolas Link System Control - A multi-page Flask application to control
Diretta Purist Mode states and Roon IR Remote settings.

To be run on the Diretta Host.
"""

import os
import time
import subprocess
import json
import logging
import sys
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, redirect, url_for, flash

# --- Configuration ---
REMOTE_USER = "purist-app"
REMOTE_HOST = "diretta-target"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/purist_app_key")
ROON_CONFIG_PATH = os.path.expanduser("~/roon-ir-remote/app_info.json")
DIRETTA_SETTING_PATH = "/opt/diretta-alsa/setting.inf"
SUPER_PURIST_FLAG = os.path.expanduser("~/purist-mode-webui/super_purist.flag")

app = Flask(__name__)
# A secret key is required for flash messaging
app.secret_key = os.urandom(24)

# --- Global State ---
ENFORCEMENT_STATE = {"last_time": 0}
ENFORCEMENT_LOCK = threading.Lock()

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# pylint: disable=line-too-long
# --- HTML & CSS TEMPLATES ---

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

        /* STRICT TARGETING: Only spin if the button itself fired the request */
        button.htmx-request .btn-spinner { display: inline-block; }
        button.htmx-request .btn-text { opacity: 0; }
        button.htmx-request { cursor: not-allowed; }

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
            <p>&copy; {{ current_year }} AnCaolas Link</p>
            <p class="text-xs mt-1">Powered by AudioLinux</p>
        </div>
    </div>
</body>
</html>
"""

LANDING_PAGE_CONTENT = """
<div class="space-y-6">
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 text-center space-y-6">
        <h2 class="text-2xl font-bold text-white">Welcome</h2>
        <p class="text-gray-400">Please choose a control panel to continue.</p>
        <div class="flex flex-wrap justify-center gap-4">
            <a href="{{ url_for('purist_app') }}" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                Purist Mode Control
            </a>
            <a href="#" onclick="window.open('//' + window.location.hostname + ':5001', '_blank')" class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                Host AudioLinux UI
            </a>

            {% if current_state != 'Standard' or music_playing %}
                {% set reason = "Unavailable while background services are disabled" if current_state != 'Standard' else "Unavailable while music is playing" %}
                <a href="#" class="bg-gray-800 text-gray-500 cursor-not-allowed font-bold py-3 px-6 rounded-lg" title="{{ reason }}">
                    Target AudioLinux UI
                </a>
            {% else %}
                <a href="#" onclick="window.open('//' + window.location.hostname + ':5101', '_blank')" class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                    Target AudioLinux UI
                </a>
            {% endif %}

            {% if roon_is_configured %}
            <a href="{{ url_for('remote_app') }}" class="bg-blue-600 hover:bg-blue-500 text-white font-bold py-3 px-6 rounded-lg transition-colors">
                IR Remote Control
            </a>
            {% endif %}
        </div>
    </div>

    {% if status.license_needs_activation %}
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 space-y-4">
        <div class="text-left">
            <h2 class="font-semibold text-lg text-white">License Activation Required</h2>
            <p class="text-sm text-yellow-400 mt-1">Evaluation mode detected. High-resolution playback is locked to Super Purist boundaries (10 Mbps limit).</p>
        </div>
        <div class="flex flex-col sm:flex-row items-start justify-between gap-6 text-left">
            <div class="text-sm text-gray-300 flex-1">
                <p class="mb-2"><strong>Step 1:</strong> Purchase license with this unique link.</p>
                <a href="{{ status.activation_url }}" target="_blank" rel="noopener noreferrer"
                   class="inline-block text-blue-400 hover:text-blue-300 underline break-all font-mono text-xs">
                    {{ status.activation_url }}
                </a>
            </div>
            <div class="flex-shrink-0">
                <p class="text-sm text-gray-300 mb-2"><strong>Step 2:</strong> After activating, restart.</p>
                <button hx-post="/restart-target" hx-target="#restart-message" hx-swap="innerHTML"
                        class="relative inline-flex items-center justify-center w-40 h-12 px-4 py-2 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200 bg-blue-600 hover:bg-blue-500 text-white">
                    <span class="btn-text">Restart Services</span>
                    <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-white"></span>
                </button>
            </div>
        </div>
        <div id="restart-message" class="mt-4 text-center text-green-400 h-5"></div>
    </div>
    {% endif %}
</div>
"""

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
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8">
        <div>
            <h2 class="font-semibold text-xl text-white mb-4">System Optimization Level</h2>
            <div class="grid grid-cols-3 gap-2 p-1 bg-gray-900 rounded-xl border border-gray-700">
                <button hx-post="/set-state/Standard" hx-target="#control-panel" hx-swap="innerHTML" hx-disabled-elt="this"
                        class="relative inline-flex items-center justify-center py-3 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {{ 'bg-yellow-600 text-gray-900' if current_state == 'Standard' else 'text-gray-400 hover:text-white' }}">
                    <span class="btn-text">Standard</span>
                    <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-current"></span>
                </button>
                <button hx-post="/set-state/Purist" hx-target="#control-panel" hx-swap="innerHTML" hx-disabled-elt="this"
                        class="relative inline-flex items-center justify-center py-3 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {{ 'bg-green-600 text-white' if current_state == 'Purist' else 'text-gray-400 hover:text-white' }}">
                    <span class="btn-text">Purist</span>
                    <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-current"></span>
                </button>
                <button hx-post="/set-state/SuperPurist" hx-target="#control-panel" hx-swap="innerHTML" hx-disabled-elt="this"
                        class="relative inline-flex items-center justify-center py-3 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {{ 'bg-green-600 text-white border border-green-400/30' if current_state == 'SuperPurist' else 'text-gray-400 hover:text-white' }}">
                    <span class="btn-text">Super Purist</span>
                    <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-current"></span>
                </button>
            </div>
        </div>

        <div class="border-t border-gray-700/50 py-4 mt-6">
            {% if current_state == 'Standard' %}
                <div class="text-sm text-yellow-400">
                    <span class="font-bold block mb-1">Standard Operation:</span>
                    <ul class="list-disc list-outside space-y-1 text-gray-400 text-xs ml-5">
                        <li>Background tasks and communications enabled on the Target.</li>
                        <li>Required state for routine system maintenance and updates.</li>
                        <li>Sets and maintains the local system time on the Target.</li>
                        <li>Point-to-point link operates at its standard baseline frequency.</li>
                    </ul>
                </div>
            {% elif current_state == 'Purist' %}
                <div class="text-sm text-green-400">
                    <span class="font-bold block mb-1">Purist Mode:</span>
                    <ul class="list-disc list-outside space-y-1 text-gray-400 text-xs ml-5">
                        <li>Non-essential background tasks and communications disabled on the Target.</li>
                        <li>Local noise floor minimized and computational headroom maximized.</li>
                        <li>50% reduction in physical network frequency compared to standard Gigabit.</li>
                        <li>Preserves bandwidth required for native, bit-perfect DSD and high-res PCM.</li>
                    </ul>
                </div>
            {% elif current_state == 'SuperPurist' %}
                <div class="text-sm text-green-400">
                    <span class="font-bold block mb-1">Super Purist Mode:</span>
                    <ul class="list-disc list-outside space-y-1 text-gray-400 text-xs ml-5">
                        <li>Maximum physical and electrical isolation engaged.</li>
                        <li>Point-to-point link throttled to its absolute lowest operating frequency.</li>
                        <li>68% lower physical network frequency than Purist Mode.</li>
                        <li>Optimized for maximum micro-dynamic expression and the quietest background at the cost of restricted format support.</li>
                    </ul>
                    <div class="p-3 mt-3 text-xs text-yellow-400 bg-yellow-900/20 rounded-lg border border-yellow-700/30">
                        <strong>⚠️ Required Roon Setting:</strong> You must set the Max sample rate (PCM) to 96 kHz. See advanced Audio settings for this zone in Roon. Native DSD is unsupported.
                    </div>
                </div>
            {% endif %}
        </div>

        <div class="flex items-center justify-between p-4 bg-gray-700/30 border border-gray-700 rounded-xl mt-2">
            <div>
                <h3 class="font-semibold text-base text-white">Activate on Boot</h3>
                {% if status.auto_start_enabled %}
                    <p class="text-xs text-green-400">Will automatically engage current optimization level 60s after boot.</p>
                {% else %}
                    <p class="text-xs text-gray-400">System will always initialize in Standard Mode after a reboot.</p>
                {% endif %}
            </div>
            <button hx-post="/toggle-auto" hx-target="#control-panel" hx-swap="innerHTML"
                    class="relative inline-flex items-center justify-center w-24 h-10 px-3 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {% if status.auto_start_enabled %} bg-green-600 hover:bg-green-500 text-white {% else %} bg-yellow-600 hover:bg-yellow-500 text-gray-900 {% endif %}">
                <span class="btn-text">{% if status.auto_start_enabled %}Disable{% else %}Enable{% endif %}</span>
                <span class="absolute btn-spinner hidden h-4 w-4 rounded-full border-2 border-white"></span>
            </button>
        </div>
    </div>
</div>
"""

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
# pylint: enable=line-too-long


# --- BACKEND LOGIC (Helper Functions) ---

def is_music_playing():
    """Checks if music is actively playing by inspecting /proc/asound/."""
    status_file_path = "/proc/asound/card0/pcm0p/sub0/status"
    try:
        with open(status_file_path, "r", encoding="utf-8") as file_handle:
            status_content = file_handle.read()

        if "state: RUNNING" in status_content:
            app.logger.info("Playback detected on Host via /proc.")
            return True

        app.logger.info("No playback detected on Host via /proc (state is not RUNNING).")
        return False
    except FileNotFoundError:
        app.logger.info("ALSA status file not found at %s. Assuming no playback.", status_file_path)
        return False
    except OSError as err:
        app.logger.error("OS Error checking playback status via /proc: %s", err)
        return False


def run_remote_command(command):
    """Executes a command on the Diretta Target via SSH."""
    ssh_command = [
        "/usr/bin/ssh",
        "-i", SSH_KEY_PATH,
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        command
    ]
    try:
        app.logger.info("Running remote command: %s", " ".join(ssh_command))
        result = subprocess.run(
            ssh_command, capture_output=True, text=True, check=True, timeout=15
        )
        output = result.stdout.strip()
        app.logger.info("Remote command successful. Output: %s", output)
        return output
    except subprocess.CalledProcessError as err:
        app.logger.error(
            "Remote command failed with return code %s: %s", err.returncode, err.stderr
        )
        return None
    except subprocess.TimeoutExpired:
        app.logger.error("Remote command timed out after 15 seconds.")
        return None
    except OSError as err:
        app.logger.error("OS Error executing remote command: %s", err)
        return None


def get_status_from_target():
    """Gets the current status from the Diretta Target."""
    raw_status = run_remote_command("/usr/local/bin/pm-get-status")
    if not raw_status:
        return None

    try:
        status_data = json.loads(raw_status)
        if status_data.get("license_needs_activation"):
            license_url = run_remote_command("/usr/local/bin/pm-get-license-url")
            status_data["activation_url"] = license_url if license_url else ""
        else:
            status_data["activation_url"] = ""
        return status_data
    except json.JSONDecodeError:
        app.logger.error("Failed to decode JSON status from remote host. Received: %s", raw_status)
        return None


def get_roon_zone_from_host():
    """Gets the current Roon zone name from the local config file."""
    if not os.path.exists(ROON_CONFIG_PATH):
        return "Not Configured"
    try:
        with open(ROON_CONFIG_PATH, "r", encoding="utf-8") as file_handle:
            config = json.load(file_handle)
        return config.get("roon", {}).get("zone", {}).get("name", "Not Set")
    except (json.JSONDecodeError, OSError) as err:
        app.logger.error("Error Reading Config: %s", err)
        return "Error Reading Config"


def get_host_mtu(interface="end0"):
    """Reads the MTU of the specified network interface."""
    try:
        with open(f"/sys/class/net/{interface}/mtu", "r", encoding="utf-8") as file_handle:
            return int(file_handle.read().strip())
    except OSError as err:
        app.logger.error("Could not read MTU for %s: %s", interface, err)
        return 1500
    except ValueError as err:
        app.logger.error("Invalid MTU value read for %s: %s", interface, err)
        return 1500


def is_app8_enabled():
    """Checks if the Optional Purist Network Speed (App 8) service is enabled."""
    try:
        result = subprocess.run(
            ["systemctl", "is-enabled", "limit-speed-100m.service"],
            capture_output=True, text=True, check=False
        )
        return "enabled" in result.stdout.strip()
    except OSError:
        return False


def is_diretta_isolated():
    """
    Checks if the running diretta_alsa service is bound to isolated audio cores (2 or 3)
    by querying the active process affinity directly from the kernel scheduler.
    """
    try:
        pid_cmd = ["systemctl", "show", "--property", "MainPID", "--value", "diretta_alsa.service"]
        pid_result = subprocess.run(pid_cmd, capture_output=True, text=True, check=False)
        pid = pid_result.stdout.strip()

        if not pid or pid == "0":
            app.logger.warning("Diretta service is either not running or PID is invalid (0).")
            return False

        taskset_cmd = ["/usr/bin/taskset", "-cp", pid]
        taskset_result = subprocess.run(taskset_cmd, capture_output=True, text=True, check=False)
        taskset_out = taskset_result.stdout.strip()

        if ":" in taskset_out:
            affinity_list = taskset_out.split(":")[-1].strip()

            # Exact string matching prevents matching wide default masks like "0,1,2,3"
            valid_masks = ["2", "3", "2-3", "2,3", "3,2"]
            if affinity_list in valid_masks:
                app.logger.info("Live core isolation verified. Affinity list: %s", affinity_list)
                return True

            app.logger.warning(
                "Diretta running on non-isolated cores. Actual affinity: %s",
                affinity_list
            )

    except OSError as err:
        app.logger.error("OS Error checking real-time taskset isolation: %s", err)

    return False


def _set_link_speed(speed, autoneg):
    """Internal helper to set the link speed via ethtool."""
    cmd = [
        "/usr/bin/sudo", "/usr/bin/ethtool", "-s", "end0",
        "speed", str(speed), "duplex", "full", "autoneg", autoneg
    ]
    try:
        subprocess.run(cmd, check=False, capture_output=True)
    except OSError as err:
        app.logger.error("Failed to execute ethtool: %s", err)


def update_setting_inf(cycle_time, info_cycle):
    """Reads setting.inf, updates CycleTime and InfoCycle, and writes it back."""
    if not os.path.exists(DIRETTA_SETTING_PATH):
        return

    try:
        with open(DIRETTA_SETTING_PATH, "r", encoding="utf-8") as file_handle:
            lines = file_handle.readlines()

        changed = False
        new_lines = []
        for line in lines:
            if line.startswith("CycleTime="):
                new_lines.append(f"CycleTime={cycle_time}\n")
                changed = True
            elif line.startswith("InfoCycle="):
                new_lines.append(f"InfoCycle={info_cycle}\n")
                changed = True
            else:
                new_lines.append(line)

        if changed:
            app.logger.info("Writing new Diretta config: CycleTime=%s, InfoCycle=%s",
                            cycle_time, info_cycle)
            tmp_file = "/tmp/setting.inf.tmp"
            with open(tmp_file, "w", encoding="utf-8") as file_handle:
                file_handle.writelines(new_lines)

            mv_cmd = ["/usr/bin/sudo", "/usr/bin/mv", tmp_file, DIRETTA_SETTING_PATH]
            subprocess.run(mv_cmd, check=True)

    except OSError as err:
        app.logger.error("File operation error while updating setting.inf: %s", err)
    except subprocess.CalledProcessError as err:
        app.logger.error("Sudo mv failed when updating setting.inf: %s", err)


def restart_diretta_services():
    """Restarts the Diretta and Roon Bridge services."""
    app.logger.info("Restarting Diretta and Roon Bridge services...")
    try:
        subprocess.run(
            ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "diretta_alsa.service"],
            check=True
        )
        subprocess.run(
            ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "roonbridge.service"],
            check=True
        )
    except subprocess.CalledProcessError as err:
        app.logger.error("Failed to restart services: %s", err)
    except OSError as err:
        app.logger.error("OS Error restarting services: %s", err)


def _get_current_speed():
    """Parses ethtool output to return the current speed string."""
    try:
        ethtool_out = subprocess.run(
            ["/usr/bin/ethtool", "end0"], capture_output=True, text=True, check=False
        ).stdout
        for line in ethtool_out.split("\n"):
            if "Speed:" in line:
                return line.split(":")[1].strip()
    except OSError as err:
        app.logger.error("Could not run ethtool to determine speed: %s", err)
    return None


def _get_current_cycletime():
    """Parses the current CycleTime from setting.inf."""
    try:
        with open(DIRETTA_SETTING_PATH, "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                if line.startswith("CycleTime="):
                    return int(line.strip().split("=")[1])
    except (OSError, ValueError, IndexError):
        pass
    return 0


def get_current_system_state(target_status):
    """Derives the friendly UI state name based on Target flags and Host flags."""
    if not target_status:
        return "Standard"
    if not target_status.get("purist_mode_active", False):
        return "Standard"
    if os.path.exists(SUPER_PURIST_FLAG):
        return "SuperPurist"
    return "Purist"


def get_baseline_link_speed(target_status):
    """Calculates the baseline network speed based on Appendix 8 and license status."""
    if is_app8_enabled():
        if target_status and target_status.get("license_needs_activation", False):
            return "10"
        return "100"
    return "1000"


def get_target_speed(current_state, target_status):
    """Determines the exact physical speed target required for the current state."""
    if current_state == "SuperPurist":
        return "10"
    return get_baseline_link_speed(target_status)


def get_target_profile(current_state):
    """Determines the exact CycleTime and InfoCycle parameters for the current state."""
    if current_state == "SuperPurist":
        return 2000, 200000

    if not is_diretta_isolated():
        return 800, 80000

    mtu = get_host_mtu()
    if mtu == 1500:
        return 514, 51400
    if mtu == 2032:
        return 700, 70000
    if mtu >= 9000:
        return 1000, 100000

    return 514, 51400  # Default isolated fallback


def _async_hardware_transition(expected_speed, expected_ct, expected_ic, current_state):
    """Executes the link and profile adjustments on a non-blocking thread."""
    app.logger.info("Asynchronously transitioning link and Diretta profile...")

    # 1. Coordinate link speed
    run_remote_command(f"/usr/local/bin/pm-set-link {expected_speed}")
    _set_link_speed(expected_speed, "on")

    # 2. Wait for physical layer to settle
    time.sleep(4)

    # 3. Apply settings and restart
    update_setting_inf(cycle_time=expected_ct, info_cycle=expected_ic)
    restart_diretta_services()

    # 4. Enforce Target state
    if current_state in ["Purist", "SuperPurist"]:
        run_remote_command("/usr/local/bin/pm-toggle-mode --enforce")


def check_and_enforce_host_profile(target_status):
    """
    Intelligently compares current runtime variables against the target logic matrix.
    If mismatched, orchestrates the entire hardware and profile transition pipeline.
    """

    if not target_status:
        return

    current_speed_str = _get_current_speed()

    # SAFETY GATE: If the link state is unstable or negotiating, do not enforce rules
    if not current_speed_str or "Unknown" in current_speed_str:
        app.logger.info("Physical link is currently negotiating or down. Skipping enforcement.")
        return

    current_speed_val = current_speed_str.replace("Mb/s", "").strip()
    current_ct = _get_current_cycletime()

    current_state = get_current_system_state(target_status)
    expected_speed = get_target_speed(current_state, target_status)
    expected_ct, expected_ic = get_target_profile(current_state)

    if current_speed_val != expected_speed or current_ct != expected_ct:
        with ENFORCEMENT_LOCK:
            # Cooldown to prevent thread spamming during fast clicks or polling
            if time.time() - ENFORCEMENT_STATE["last_time"] < 15:
                return
            ENFORCEMENT_STATE["last_time"] = time.time()

        app.logger.info(
            "Enforcement triggered. Speed: %s -> %s | CycleTime: %s -> %s",
            current_speed_val, expected_speed, current_ct, expected_ct
        )

        threading.Thread(
            target=_async_hardware_transition,
            args=(expected_speed, expected_ct, expected_ic, current_state),
            daemon=True
        ).start()


# --- FLASK ROUTES ---

@app.route("/")
def landing_page():
    """Serves the main landing page with activation details if required."""
    roon_configured = os.path.exists(ROON_CONFIG_PATH)

    target_status = get_status_from_target()
    if not target_status:
        target_status = {
            "purist_mode_active": False,
            "license_needs_activation": False,
            "activation_url": ""
        }

    music_playing = is_music_playing()
    current_state = get_current_system_state(target_status)

    content = render_template_string(
        LANDING_PAGE_CONTENT,
        roon_is_configured=roon_configured,
        status=target_status,
        music_playing=music_playing,
        current_state=current_state
    )
    return render_template_string(
        BASE_TEMPLATE,
        content=content,
        active_page="home",
        roon_is_configured=roon_configured,
        current_year=datetime.now().year
    )


@app.route("/purist")
def purist_app():
    """Serves the Purist Mode control application."""
    roon_configured = os.path.exists(ROON_CONFIG_PATH)
    content = render_template_string(PURIST_APP_TEMPLATE)
    return render_template_string(
        BASE_TEMPLATE,
        content=content,
        active_page="purist",
        roon_is_configured=roon_configured,
        current_year=datetime.now().year
    )


@app.route("/remote", methods=["GET", "POST"])
def remote_app():
    """Serves the IR Remote control application."""
    roon_configured = os.path.exists(ROON_CONFIG_PATH)
    if not roon_configured:
        return redirect(url_for("landing_page"))

    if request.method == "POST":
        new_zone_name = request.form.get("zone_name")
        if not new_zone_name:
            flash("Error: No zone name provided.")
        else:
            try:
                with open(ROON_CONFIG_PATH, "r", encoding="utf-8") as file_handle:
                    config = json.load(file_handle)

                config["roon"]["zone"]["name"] = new_zone_name

                with open(ROON_CONFIG_PATH, "w", encoding="utf-8") as file_handle:
                    json.dump(config, file_handle, indent=2)

                subprocess.run(
                    ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "roon-ir-remote.service"],
                    check=True
                )
                app.logger.info("Roon zone updated to '%s' and service restarted.", new_zone_name)
                flash(f"Successfully updated Roon Zone to: {new_zone_name}")
            except OSError as err:
                app.logger.error("Failed to update Roon zone config file: %s", err)
                flash(f"An error occurred: {err}")
            except subprocess.CalledProcessError as err:
                app.logger.error("Failed to restart Roon IR service: %s", err)
                flash(f"An error occurred restarting the service: {err}")

        return redirect(url_for("remote_app"))

    current_zone = get_roon_zone_from_host()
    content = render_template_string(REMOTE_APP_TEMPLATE, current_zone=current_zone)
    return render_template_string(
        BASE_TEMPLATE,
        content=content,
        active_page="remote",
        roon_is_configured=roon_configured,
        current_year=datetime.now().year
    )


# --- HTMX API Endpoints ---

@app.route("/status")
def status():
    """Serves the status panel for HTMX updates."""
    if is_music_playing():
        return render_template_string(MUSIC_PLAYING_TEMPLATE)

    target_status = get_status_from_target()
    if target_status is None:
        return '<div class="p-8 text-center text-red-400">Error: Could not connect to Target.</div>'

    # Enforce Host profile (speed and CycleTime) dynamically based on Target status
    check_and_enforce_host_profile(target_status)
    current_state = get_current_system_state(target_status)

    return render_template_string(
        STATUS_PANEL_TEMPLATE,
        status=target_status,
        current_state=current_state
    )


def _clear_super_purist_flag():
    """Safely removes the super purist flag from disk if it exists."""
    if os.path.exists(SUPER_PURIST_FLAG):
        try:
            os.remove(SUPER_PURIST_FLAG)
            app.logger.info("Super Purist Mode flag cleanly removed from disk.")
        except OSError as err:
            app.logger.error("Failed to remove Super Purist flag file: %s", err)


def _transition_to_standard(is_currently_purist):
    """Handles down-transition back to Standard operational mode."""
    _clear_super_purist_flag()
    if is_currently_purist:
        run_remote_command("/usr/local/bin/pm-toggle-mode")


def _transition_to_purist(is_currently_purist):
    """Handles transition to high-resolution Purist mode layers."""
    _clear_super_purist_flag()
    if not is_currently_purist:
        run_remote_command("/usr/local/bin/pm-toggle-mode")


def _transition_to_super_purist(is_currently_purist):
    """Handles extreme isolation transition down to 10 Mbps layers."""
    if not os.path.exists(SUPER_PURIST_FLAG):
        try:
            os.makedirs(os.path.dirname(SUPER_PURIST_FLAG), exist_ok=True)
            with open(SUPER_PURIST_FLAG, "w", encoding="utf-8") as file_handle:
                file_handle.write("1")
            app.logger.info("Super Purist Mode flag created via UI selection.")
        except OSError as err:
            app.logger.error("Failed to set Super Purist flag: %s", err)
    if not is_currently_purist:
        run_remote_command("/usr/local/bin/pm-toggle-mode")


@app.route("/set-state/<state_name>", methods=["POST"])
def set_state(state_name):
    """HTMX endpoint to transition the system explicitly between operational states."""
    target_status = get_status_from_target()
    if not target_status:
        return status()

    is_currently_purist = target_status.get("purist_mode_active", False)

    if state_name == "Standard":
        _transition_to_standard(is_currently_purist)
    elif state_name == "Purist":
        _transition_to_purist(is_currently_purist)
    elif state_name == "SuperPurist":
        _transition_to_super_purist(is_currently_purist)

    return status()


@app.route("/toggle-auto", methods=["POST"])
def toggle_auto():
    """Toggles the auto-start service on/off."""
    run_remote_command("/usr/local/bin/pm-toggle-auto")
    return status()


@app.route("/restart-target", methods=["POST"])
def restart_target():
    """
    Disables Purist Mode on the Target to ensure internet access,
    then restarts the Diretta service for license activation. Also
    restarts the Roon Bridge service on the Host.
    """
    app.logger.info("Starting license activation sequence...")
    t_status = get_status_from_target()

    if t_status and t_status.get("purist_mode_active"):
        app.logger.info("Purist Mode is active. Disabling it before restart.")
        run_remote_command("/usr/local/bin/pm-toggle-mode")
    else:
        app.logger.info("Purist Mode is not active. Proceeding with restart.")

    app.logger.info("Restarting Diretta ALSA Target service...")
    run_remote_command("/usr/local/bin/pm-restart-target")

    app.logger.info("Restarting Roon Bridge service on Host...")
    try:
        subprocess.run(
            ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "roonbridge.service"],
            check=True
        )
    except subprocess.CalledProcessError as err:
        app.logger.error("Failed to restart Roon Bridge during activation: %s", err)

    now = datetime.now().strftime("%H:%M:%S")
    return f"""
    <span>Restart commands sent at {now}. Allow 10-15 seconds for backend initialization.</span>
    """


if __name__ == "__main__":
    is_interactive = sys.stdout.isatty()
    APP_PORT = 8080 if is_interactive else 80
    APP_DEBUG_MODE = is_interactive
    app.run(host="0.0.0.0", port=APP_PORT, debug=APP_DEBUG_MODE)
