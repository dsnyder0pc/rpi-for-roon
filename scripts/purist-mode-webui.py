#!/usr/bin/env python
"""
AnCaolas Link System Control - A multi-page Flask application to control
Diretta Purist Mode states and Roon IR Remote settings.

To be run on the Diretta Host.
"""

# pylint: disable=too-many-lines

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

# SSH to the Target fails transiently while the point-to-point link renegotiates
# between 10 and 100 Mbps, in either direction. Those are transport-level
# failures (exit 255) or timeouts, and they clear within a second or two, so
# retry them rather than reporting the Target as unreachable.
SSH_RETRY_ATTEMPTS = 3
SSH_RETRY_DELAY = 2.0

# The Target answers SSH well before purist-mode-auto.service has applied Purist
# Mode, so an early poll reports purist off and derives as Standard. Acting on
# that flips the Host to 100 Mbps/1300us, only to flip back once the Target
# finishes booting. Background enforcement therefore waits out the Host's own
# boot window and requires the derived state to hold before it acts.
BOOT_SETTLE_SECONDS = 150
STATE_SETTLE_SECONDS = 30

# The point-to-point interface on both the Host and the Target.
LINK_INTERFACE = "end0"

# The Host waits this long before shutting itself down, so the Target reaches
# its own shutdown first and the browser still receives the confirmation.
HOST_POWER_DELAY_SECONDS = 10

# --- Link capacity model ---
# The whole design rests on one L2 transmission per cycle, so the usable payload
# rate is whichever of two limits binds first:
#   1. Frame limit: a cycle's payload must fit in a single packet, (MTU - 48)
#      bytes, where 48 = 20 IP + 8 UDP + 20 Diretta.
#   2. Wire limit: that packet plus its Ethernet framing must clear the link
#      inside one cycle, where 86 = those 48 header bytes + 14 Ethernet header
#      + 4 FCS + 20 preamble, SFD and interframe gap.
# At every jumbo tier the frame limit binds. The wire limit only takes over on
# the 10 Mbps Super Purist link, which is why that mode caps at DSD64 and
# 32-bit/96 kHz no matter how large the MTU is.
FRAME_HEADER_BYTES = 48
WIRE_OVERHEAD_BYTES = 86

# Payload rates are for stereo: DSD is 1 bit per channel, PCM a 32-bit container.
DSD_TIERS = (
    ("DSD64", 0.7056),
    ("DSD128", 1.4112),
    ("DSD256", 2.8224),
    ("DSD512", 5.6448),
    ("DSD1024", 11.2896),
)
PCM_RATES_KHZ = (44.1, 48, 88.2, 96, 176.4, 192, 352.8, 384, 705.6, 768)

app = Flask(__name__)
# A secret key is required for flash messaging
app.secret_key = os.urandom(24)

# --- Global State ---
ENFORCEMENT_STATE = {"last_time": 0}
ENFORCEMENT_LOCK = threading.Lock()
SETTLE_STATE = {"state": None, "since": 0.0}
SETTLE_LOCK = threading.Lock()
TRANSITION_STATE = {"active": False}
STATUS_CACHE = {"data": None, "timestamp": 0.0}
# MTU only changes across a reboot, so the last value the Target reported stays
# valid. Caching it lets the link panel refresh without any extra SSH traffic.
TARGET_LINK_CACHE = {"mtu": None}
STATUS_CACHE_LOCK = threading.Lock()
STATUS_FETCH_LOCK = threading.Lock()

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
        <div class="relative text-center mb-6 px-12">
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-white">AnCaolas Link</h1>
            <p class="text-lg text-gray-400">System Control</p>

            <div class="absolute top-0 right-0">
                <button type="button" onclick="togglePowerMenu(event)" aria-haspopup="true"
                        aria-expanded="false" aria-label="Power options" id="power-button"
                        class="flex items-center justify-center h-10 w-10 rounded-full bg-gray-800 text-red-500 ring-1 ring-white/10 hover:bg-red-600 hover:text-white transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
                        <path d="M12 3v9"></path>
                        <path d="M6.6 6.6a8 8 0 1 0 10.8 0"></path>
                    </svg>
                </button>

                <div id="power-menu" hidden
                     class="absolute right-0 mt-2 w-56 origin-top-right rounded-xl bg-gray-800 p-1 shadow-lg ring-1 ring-white/10 z-20 text-left">
                    <button hx-post="/power/reboot" hx-target="#power-message" hx-swap="innerHTML"
                            hx-confirm="Reboot the Diretta Target and then this Host? Playback will stop and the link will be down for about a minute."
                            onclick="closePowerMenu()"
                            class="w-full flex items-center gap-3 px-3 py-2 text-sm text-gray-200 rounded-lg hover:bg-gray-700">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                            <path d="M21 12a9 9 0 1 1-2.64-6.36"></path>
                            <path d="M21 3v6h-6"></path>
                        </svg>
                        Reboot System
                    </button>
                    <button hx-post="/power/poweroff" hx-target="#power-message" hx-swap="innerHTML"
                            hx-confirm="Power off the Diretta Target and then this Host? Both must be switched on by hand afterwards."
                            onclick="closePowerMenu()"
                            class="w-full flex items-center gap-3 px-3 py-2 text-sm text-red-400 rounded-lg hover:bg-red-600 hover:text-white">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 flex-shrink-0" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                            <path d="M12 3v9"></path>
                            <path d="M6.6 6.6a8 8 0 1 0 10.8 0"></path>
                        </svg>
                        Power Off System
                    </button>
                </div>
            </div>
        </div>

        <div id="power-message" class="text-center text-sm text-yellow-400 empty:hidden mb-4"></div>

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
    <script>
        function togglePowerMenu(event) {
            event.stopPropagation();
            const menu = document.getElementById('power-menu');
            menu.hidden = !menu.hidden;
            document.getElementById('power-button')
                    .setAttribute('aria-expanded', String(!menu.hidden));
        }

        function closePowerMenu() {
            const menu = document.getElementById('power-menu');
            menu.hidden = true;
            document.getElementById('power-button').setAttribute('aria-expanded', 'false');
        }

        // Dismiss on an outside click or Escape, the way a menu is expected to behave.
        document.addEventListener('click', closePowerMenu);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { closePowerMenu(); }
        });
        document.getElementById('power-menu')
                .addEventListener('click', function (event) { event.stopPropagation(); });
    </script>
</body>
</html>
"""

# The card shell is stable and owns the refresh. The fragment endpoint returns
# only the body below, swapped as innerHTML: a fragment that carried its own
# hx-trigger="load" would re-fire the moment it was swapped in, looping forever.
LINK_PANEL_CARD = """
<div id="link-panel" hx-get="/link-status" hx-trigger="every 30s, visibilitychange from:document"
     hx-swap="innerHTML" class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8">
{{ link_body | safe }}
</div>
"""

LINK_PANEL_TEMPLATE = """
    <div class="flex items-center justify-between mb-4">
        <h2 class="font-semibold text-xl text-white">Point-to-Point Link</h2>
        {% if link.up %}
            <span class="inline-flex items-center gap-2 text-xs font-semibold text-green-400">
                <span class="h-2 w-2 rounded-full bg-green-400"></span>Up
            </span>
        {% else %}
            <span class="inline-flex items-center gap-2 text-xs font-semibold text-red-400">
                <span class="h-2 w-2 rounded-full bg-red-400"></span>Down
            </span>
        {% endif %}
    </div>

    <dl class="grid grid-cols-2 gap-px bg-gray-700/50 rounded-xl overflow-hidden border border-gray-700">
        <div class="bg-gray-900/40 p-4">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Link Speed</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.speed %}{{ link.speed }} Mb/s{% else %}&mdash;{% endif %}
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4">
            <dt class="text-xs uppercase tracking-wide text-gray-500">MTU</dt>
            <dd class="mt-1 text-lg font-semibold {{ 'text-red-400' if link.mtu_mismatch else 'text-white' }}">
                {{ link.mtu }}
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Max PCM</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.max_pcm %}{{ link.max_pcm }}{% else %}&mdash;{% endif %}
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Max DSD</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.max_dsd %}{{ link.max_dsd }}{% else %}&mdash;{% endif %}
            </dd>
        </div>
    </dl>

    {% if link.mtu_mismatch %}
    <div class="p-3 mt-4 text-xs text-red-400 bg-red-900/20 rounded-lg border border-red-700/30">
        <strong>&#9888;&#65039; MTU mismatch:</strong> the Host is set to {{ link.mtu }} but the Target reports
        {{ link.target_mtu }}. Re-run Appendix 9 on both machines.
    </div>
    {% endif %}
"""

LANDING_PAGE_CONTENT = """
<div class="space-y-6">
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 text-center space-y-6">
        <h2 class="text-2xl font-bold text-white">Welcome</h2>
        <p class="text-gray-400">Use the navigation above for system controls, or open an AudioLinux interface below.</p>
        <div class="flex flex-wrap justify-center gap-4">
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
        </div>
    </div>

    {{ link_panel | safe }}

    {% if status.license_needs_activation %}
    <div class="bg-gray-800/50 rounded-2xl shadow-lg ring-1 ring-white/10 p-6 sm:p-8 space-y-4">
        <div class="text-left">
            <h2 class="font-semibold text-lg text-white">License Activation Required</h2>
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
        <p class="text-xs text-gray-500 mt-4 max-w-md mx-auto">
            <strong>Troubleshooting Tip:</strong> If this connection screen persists or the UI keeps spinning, the physical network link may be renegotiating. You may need to power cycle your Target computer to restore service.
        </p>
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
                        <strong>⚠️ Required Roon Setting:</strong> You must set the Max sample rate (PCM) to 96 kHz. See advanced Audio settings for this zone in Roon. Native DSD64 may work but DoP will not.
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
            <button hx-post="/toggle-auto" hx-target="#control-panel" hx-swap="innerHTML" hx-disabled-elt="this"
                    class="relative inline-flex items-center justify-center w-24 h-10 px-3 py-1.5 text-xs font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {% if status.auto_start_enabled %} bg-green-600 hover:bg-green-500 text-white {% else %} bg-yellow-600 hover:bg-yellow-500 text-gray-900 {% endif %}">
                <span class="btn-text">{% if status.auto_start_enabled %}Disable{% else %}Enable{% endif %}</span>
                <span class="absolute btn-spinner hidden h-4 w-4 rounded-full border-2 border-white"></span>
            </button>
        </div>

        <div class="text-center mt-6 p-3 bg-gray-900/30 border border-gray-800 rounded-xl">
            <p class="text-xs text-gray-500">
                <strong>💡 Troubleshooting:</strong> If the interface remains unresponsive or keeps spinning during optimization transitions, please power cycle your Target computer to restore the network link.
            </p>
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

def ping_target(timeout=1, blocking=False, block_timeout=15):
    """Pings the Diretta Target to check reachability, optionally blocking."""
    cmd = ["ping", "-c", "1", "-W", str(timeout), REMOTE_HOST]
    start_time = time.time()
    while True:
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            if result.returncode == 0:
                return True
        except (subprocess.CalledProcessError, OSError):
            pass

        if not blocking or (time.time() - start_time >= block_timeout):
            break
        time.sleep(1)
    return False


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
        app.logger.info(
            "ALSA status file not found at %s. Assuming no playback.",
            status_file_path
        )
        return False
    except OSError as err:
        app.logger.error("OS Error checking playback status via /proc: %s", err)
        return False


def run_remote_command(command, attempts=SSH_RETRY_ATTEMPTS):
    """
    Executes a command on the Diretta Target via SSH.

    Transport-level failures (exit code 255) and timeouts are expected while the
    link renegotiates speed, so they are retried. A non-255 exit code means the
    remote command itself ran and failed, which is reported immediately.
    """
    ssh_command = [
        "/usr/bin/ssh",
        "-i", SSH_KEY_PATH,
        "-o", "ConnectTimeout=5",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{REMOTE_USER}@{REMOTE_HOST}",
        command
    ]

    for attempt in range(1, attempts + 1):
        try:
            app.logger.info("Running remote command: %s", " ".join(ssh_command))
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=15
            )
            output = result.stdout.strip()
            app.logger.info("Remote command successful. Output: %s", output)
            return output
        except subprocess.CalledProcessError as err:
            if err.returncode != 255:
                app.logger.error(
                    "Remote command failed with return code %s: %s",
                    err.returncode, err.stderr
                )
                return None
            reason = f"SSH transport error: {(err.stderr or '').strip()}"
        except subprocess.TimeoutExpired:
            reason = "Remote command timed out after 15 seconds"
        except OSError as err:
            app.logger.error("OS Error executing remote command: %s", err)
            return None

        if attempt < attempts:
            app.logger.warning(
                "%s (attempt %s of %s). Link may be renegotiating; "
                "retrying in %ss.",
                reason, attempt, attempts, SSH_RETRY_DELAY
            )
            time.sleep(SSH_RETRY_DELAY)
        else:
            app.logger.error(
                "%s (attempt %s of %s). Giving up.", reason, attempt, attempts
            )

    return None


def get_status_from_target(bypass_cache=False):
    """Gets the current status from the Diretta Target, using a brief cache."""
    now = time.time()

    if not bypass_cache:
        with STATUS_CACHE_LOCK:
            if (
                STATUS_CACHE["data"] is not None
                and (now - STATUS_CACHE["timestamp"]) < 3.0
            ):
                app.logger.info("Returning cached Target status.")
                return STATUS_CACHE["data"]

    # Use a lock to ensure only one thread performs the slow SSH fetch at a time
    with STATUS_FETCH_LOCK:
        now = time.time()
        if not bypass_cache:
            with STATUS_CACHE_LOCK:
                if (
                    STATUS_CACHE["data"] is not None
                    and (now - STATUS_CACHE["timestamp"]) < 3.0
                ):
                    app.logger.info("Returning cached Target status (after lock).")
                    return STATUS_CACHE["data"]

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

            # Older Targets predate the mtu field; absent it, the link panel
            # simply omits the agreement check rather than guessing.
            if status_data.get("mtu"):
                TARGET_LINK_CACHE["mtu"] = status_data["mtu"]

            with STATUS_CACHE_LOCK:
                STATUS_CACHE["data"] = status_data
                STATUS_CACHE["timestamp"] = now
            return status_data
        except json.JSONDecodeError:
            app.logger.error(
                "Failed to decode JSON status from remote host. Received: %s",
                raw_status
            )
            return None


def invalidate_status_cache():
    """Clears the target status cache to force a fresh SSH poll."""
    with STATUS_CACHE_LOCK:
        STATUS_CACHE["data"] = None
        STATUS_CACHE["timestamp"] = 0.0


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


def get_host_mtu(interface=LINK_INTERFACE):
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


def get_host_link_speed(interface=LINK_INTERFACE):
    """
    Reads the negotiated link speed in Mbps from sysfs.

    Returns None while the link is down, when sysfs reports -1 and reading the
    attribute can fail outright with EINVAL.
    """
    try:
        with open(f"/sys/class/net/{interface}/speed", "r", encoding="utf-8") as file_handle:
            speed = int(file_handle.read().strip())
        return speed if speed > 0 else None
    except (OSError, ValueError):
        return None


def get_host_link_up(interface=LINK_INTERFACE):
    """Reports whether the point-to-point interface is currently carrying a link."""
    try:
        with open(f"/sys/class/net/{interface}/operstate", "r", encoding="utf-8") as file_handle:
            return file_handle.read().strip() == "up"
    except OSError:
        return False


def _pcm_payload_rate(rate_khz):
    """Stereo 32-bit PCM payload rate in bytes per microsecond."""
    return rate_khz * 1000.0 * 4.0 * 2.0 / 1_000_000.0


def get_payload_budget(mtu, cycle_time, speed_mbps):
    """
    Returns the largest payload rate in bytes/us that still fits one L2
    transmission per cycle, or None if the inputs are not yet known.
    """
    if not mtu or not cycle_time or cycle_time <= 0:
        return None

    budget = (mtu - FRAME_HEADER_BYTES) / cycle_time
    if speed_mbps and speed_mbps > 0:
        wire_limit = speed_mbps / 8.0 - WIRE_OVERHEAD_BYTES / cycle_time
        budget = min(budget, wire_limit)
    return budget


def get_max_formats(budget):
    """Returns the highest DSD tier and PCM sample rate that fit within a budget."""
    if budget is None or budget <= 0:
        return None, None

    # A tolerance absorbs binary rounding where a tier lands exactly on the
    # ceiling, as DSD256 does at CycleTime 514 and again at MTU 2032.
    tolerance = 1e-9

    max_dsd = None
    for name, rate in DSD_TIERS:
        if rate <= budget + tolerance:
            max_dsd = name

    max_pcm = None
    for rate_khz in PCM_RATES_KHZ:
        if _pcm_payload_rate(rate_khz) <= budget + tolerance:
            max_pcm = f"{rate_khz:g} kHz"

    return max_dsd, max_pcm


def render_link_panel_body():
    """Renders the link panel's inner content from the current link state."""
    return render_template_string(LINK_PANEL_TEMPLATE, link=get_link_info())


def get_link_info():
    """
    Assembles the point-to-point link panel data from Host-local sources only.

    The Target's MTU comes from whatever the last status poll cached, so this
    never adds SSH traffic of its own and stays quiet during playback.
    """
    mtu = get_host_mtu()
    speed = get_host_link_speed()
    cycle_time = _get_current_cycletime()
    target_mtu = TARGET_LINK_CACHE["mtu"]
    link_up = get_host_link_up()

    # Without a negotiated speed the wire limit cannot be applied, and the frame
    # limit alone would overstate the link: it would claim DSD256 on a 10 Mbps
    # Super Purist connection. Report nothing rather than something unfounded.
    if link_up and speed:
        max_dsd, max_pcm = get_max_formats(get_payload_budget(mtu, cycle_time, speed))
    else:
        max_dsd, max_pcm = None, None

    return {
        "up": link_up,
        "speed": speed,
        "mtu": mtu,
        "target_mtu": target_mtu,
        # A silent MTU mismatch is the failure this panel most needs to surface:
        # the link still comes up, but every full-size frame is discarded.
        "mtu_mismatch": target_mtu is not None and target_mtu != mtu,
        "cycle_time": cycle_time,
        "max_dsd": max_dsd,
        "max_pcm": max_pcm,
    }


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
        pid_cmd = [
            "systemctl", "show", "--property", "MainPID",
            "--value", "diretta_alsa.service"
        ]
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
                app.logger.info(
                    "Live core isolation verified. Affinity list: %s",
                    affinity_list
                )
                return True

            app.logger.warning(
                "Diretta running on non-isolated cores. Actual affinity: %s",
                affinity_list
            )

    except OSError as err:
        app.logger.error("OS Error checking real-time taskset isolation: %s", err)

    return False


def _set_link_speed(speed, _autoneg):
    """Internal helper to set the link speed via ethtool using safe advertisement masks."""
    mask = "0x03f"  # Default to 1 Gbps
    if speed == "10":
        mask = "0x002"
    elif speed == "100":
        mask = "0x00a"

    cmd = [
        "/usr/bin/sudo", "/usr/bin/ethtool", "-s", "end0", "advertise", mask
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
            ["/usr/bin/sudo", "/usr/bin/systemctl", "daemon-reload"],
            check=True
        )
        subprocess.run(
            [
                "/usr/bin/sudo", "/usr/bin/systemctl",
                "restart", "diretta_alsa.service"
            ],
            check=True
        )
        subprocess.run(
            [
                "/usr/bin/sudo", "/usr/bin/systemctl",
                "restart", "roonbridge.service"
            ],
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
            ["/usr/bin/ethtool", "end0"],
            capture_output=True,
            text=True,
            check=False
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


def get_baseline_link_speed(_target_status):
    """Calculates the baseline network speed based on Appendix 8 and license status."""
    if is_app8_enabled():
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
        # 10 Mbps link, highest supported formats are DSD64 and 32-bit/96 kHz.
        # 32-bit/96 kHz binds at 0.768 B/us; 1800us keeps one packet per cycle
        # even at the un-upgraded MTU of 1500 (Appendix 9 not run).
        return 1800, 180000

    # Read the physical hardware environment first
    mtu = get_host_mtu()
    if mtu == 2032:
        return 700, 70000  # Baby Jumbo optimization layer
    if mtu == 3824:
        return 1300, 130000  # Medium Jumbo optimization layer
    if mtu >= 9000:
        return 1500, 150000  # Full Jumbo optimization layer

    # If we are on standard MTU, check if we have the green light for isolation timings
    if is_diretta_isolated() or _get_current_cycletime() == 514:
        return 514, 51400  # Tight core-isolated timing

    return 800, 80000  # Un-isolated fallback baseline


def _async_hardware_transition(expected_speed, expected_ct, expected_ic, current_state):
    """Executes the link and profile adjustments on a non-blocking thread."""
    app.logger.info("Asynchronously transitioning link and Diretta profile...")

    # 1. Coordinate link speed
    run_remote_command(f"/usr/local/bin/pm-set-link {expected_speed}")
    _set_link_speed(expected_speed, "on")

    # 2. Wait for physical layer to settle using block pinging
    app.logger.info("Waiting for physical layer to settle...")
    ping_target(blocking=True, block_timeout=15)

    # 3. Apply settings and restart
    update_setting_inf(cycle_time=expected_ct, info_cycle=expected_ic)
    restart_diretta_services()

    # 4. Give the Target up to 10 seconds to recover its SSH/Systemd stack
    app.logger.info("Waiting for Target to recover after service restarts...")
    ping_target(blocking=True, block_timeout=10)

    # 5. Enforce Target state
    if current_state in ["Purist", "SuperPurist"]:
        run_remote_command("/usr/local/bin/pm-toggle-mode --enforce")


def _sync_hardware_transition(expected_speed, expected_ct, expected_ic, current_state):
    """Executes the link and profile adjustments synchronously."""
    app.logger.info("Synchronously transitioning link and Diretta profile...")

    # 1. Coordinate link speed
    run_remote_command(f"/usr/local/bin/pm-set-link {expected_speed}")
    _set_link_speed(expected_speed, "on")

    # 2. Wait for physical layer to settle using block pinging
    app.logger.info("Waiting for physical layer to settle...")
    ping_target(blocking=True, block_timeout=15)

    # 3. Apply settings and restart
    update_setting_inf(cycle_time=expected_ct, info_cycle=expected_ic)
    restart_diretta_services()

    # 4. Give the Target up to 10 seconds to recover its SSH/Systemd stack
    app.logger.info("Waiting for Target to recover after service restarts...")
    ping_target(blocking=True, block_timeout=10)

    # 5. Enforce Target state
    if current_state in ["Purist", "SuperPurist"]:
        run_remote_command("/usr/local/bin/pm-toggle-mode --enforce")


def _get_host_uptime():
    """Returns the Host's uptime in seconds, or None if it cannot be read."""
    try:
        with open("/proc/uptime", "r", encoding="utf-8") as file_handle:
            return float(file_handle.read().split()[0])
    except (OSError, ValueError, IndexError) as err:
        app.logger.error("Could not read Host uptime: %s", err)
        return None


def _record_state_hold(current_state):
    """Tracks how long the derived state has read the same way, in seconds."""
    now = time.time()
    with SETTLE_LOCK:
        if SETTLE_STATE["state"] != current_state:
            SETTLE_STATE["state"] = current_state
            SETTLE_STATE["since"] = now
        return now - SETTLE_STATE["since"]


def _enforcement_settled(current_state, held_for):
    """
    Decides whether a detected mismatch is stable enough to act on.

    Guards against the boot race where the Target is reachable but has not yet
    applied Purist Mode, which would otherwise derive as Standard and drive a
    full profile flip that has to be undone moments later.
    """
    uptime = _get_host_uptime()
    if uptime is not None and uptime < BOOT_SETTLE_SECONDS:
        app.logger.info(
            "Host uptime is %.0fs, inside the %ss boot window. Deferring "
            "enforcement until the Target has finished starting up.",
            uptime, BOOT_SETTLE_SECONDS
        )
        return False

    if held_for < STATE_SETTLE_SECONDS:
        app.logger.info(
            "State has read as %s for only %.0fs of the %ss settling period. "
            "Deferring enforcement.",
            current_state, held_for, STATE_SETTLE_SECONDS
        )
        return False

    return True


def check_and_enforce_host_profile(target_status):
    """
    Intelligently compares current runtime variables against the target logic matrix.
    If mismatched, orchestrates the entire hardware and profile transition pipeline.
    """

    if not target_status:
        return

    # Skip background enforcement if we are already in an active UI transition
    if TRANSITION_STATE["active"]:
        return

    current_speed_str = _get_current_speed()

    # SAFETY GATE: If the link state is unstable or negotiating, do not enforce rules
    if not current_speed_str or "Unknown" in current_speed_str:
        app.logger.info(
            "Physical link is currently negotiating or down. Skipping enforcement."
        )
        return

    current_speed_val = current_speed_str.replace("Mb/s", "").strip()
    current_ct = _get_current_cycletime()

    current_state = get_current_system_state(target_status)

    # Track the hold time on every poll so the settling window reflects the
    # Target's real history, not just the polls that happened to find a mismatch.
    held_for = _record_state_hold(current_state)

    expected_speed = get_target_speed(current_state, target_status)
    expected_ct, expected_ic = get_target_profile(current_state)

    if current_speed_val == expected_speed and current_ct == expected_ct:
        return

    if not _enforcement_settled(current_state, held_for):
        return

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
        current_state=current_state,
        link_panel=render_template_string(
            LINK_PANEL_CARD, link_body=render_link_panel_body()
        )
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
                    [
                        "/usr/bin/sudo", "/usr/bin/systemctl",
                        "restart", "roon-ir-remote.service"
                    ],
                    check=True
                )
                app.logger.info(
                    "Roon zone updated to '%s' and service restarted.",
                    new_zone_name
                )
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

@app.route("/link-status")
def link_status():
    """Serves the link panel body for HTMX updates, swapped into the card shell."""
    return render_link_panel_body()


@app.route("/status")
def status():
    """Serves the status panel for HTMX updates."""
    if TRANSITION_STATE["active"]:
        # Pause/ignore refresh during active UI transition to prevent
        # race conditions or spinner interrupts
        return "", 204

    if is_music_playing():
        return render_template_string(MUSIC_PLAYING_TEMPLATE)

    target_status = get_status_from_target()
    if target_status is None:
        return (
            '<div class="p-8 text-center text-red-400">'
            'Error: Could not connect to Target.</div>'
        )

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
    TRANSITION_STATE["active"] = True
    try:
        # Condition 1: Verify Target is reachable initially
        app.logger.info(
            "State transition to %s requested. Verifying Target reachability...",
            state_name
        )
        if not ping_target(blocking=True, block_timeout=15):
            app.logger.error("Target not reachable before transition. Aborting.")
            flash(
                "Error: Diretta Target is not reachable. "
                "Cannot transition state."
            )
            return status()

        # Retrieve current target status before doing the transition
        target_status = get_status_from_target(bypass_cache=True)
        if not target_status:
            flash("Error: Could not retrieve current Target status via SSH.")
            return status()

        is_currently_purist = target_status.get("purist_mode_active", False)

        # Condition 2: Run SSH command(s) and wait for them to return
        app.logger.info("Executing state transition command via SSH...")
        if state_name == "Standard":
            _transition_to_standard(is_currently_purist)
        elif state_name == "Purist":
            _transition_to_purist(is_currently_purist)
        elif state_name == "SuperPurist":
            _transition_to_super_purist(is_currently_purist)

        invalidate_status_cache()

        # Check if a hardware link profile adjustment is necessary based on the new target state
        updated_status = get_status_from_target(bypass_cache=True)
        if updated_status:
            current_speed_str = _get_current_speed()
            if current_speed_str and "Unknown" not in current_speed_str:
                current_speed_val = current_speed_str.replace("Mb/s", "").strip()
                current_ct = _get_current_cycletime()

                current_state = get_current_system_state(updated_status)
                expected_speed = get_target_speed(current_state, updated_status)
                expected_ct, expected_ic = get_target_profile(current_state)

                if current_speed_val != expected_speed or current_ct != expected_ct:
                    app.logger.info(
                        "Synchronous hardware enforcement needed: "
                        "Speed %s -> %s | CycleTime %s -> %s",
                        current_speed_val, expected_speed,
                        current_ct, expected_ct
                    )
                    _sync_hardware_transition(
                        expected_speed, expected_ct,
                        expected_ic, current_state
                    )

        # Condition 3: Wait for Target to return to being reachable (network may drop)
        app.logger.info("Waiting for Target to return to being reachable...")
        if not ping_target(blocking=True, block_timeout=30):
            app.logger.warning("Target failed to respond to pings within 30 seconds.")
            flash(
                "Warning: Transition completed, but the Target did not "
                "recover ping response within 30s."
            )
        else:
            app.logger.info("Target successfully returned to being reachable.")

    finally:
        TRANSITION_STATE["active"] = False

    return status()


@app.route("/toggle-auto", methods=["POST"])
def toggle_auto():
    """Toggles the auto-start service on/off."""
    TRANSITION_STATE["active"] = True
    try:
        # Condition 1: Verify Target is reachable initially
        app.logger.info("Toggle auto-start requested. Checking Target reachability...")
        if not ping_target(blocking=True, block_timeout=15):
            app.logger.error("Target not reachable before toggle-auto. Aborting.")
            flash(
                "Error: Diretta Target is not reachable. "
                "Cannot toggle auto-start."
            )
            return status()

        # Condition 2: Run SSH command and wait for it to return
        app.logger.info("Executing auto-start toggle command via SSH...")
        run_remote_command("/usr/local/bin/pm-toggle-auto")
        invalidate_status_cache()

        # Condition 3: Verify reachability is stable
        app.logger.info("Verifying Target reachability is stable...")
        if not ping_target(blocking=True, block_timeout=15):
            app.logger.error("Target became unreachable after toggle-auto command.")
            flash(
                "Warning: Toggle-auto command executed, "
                "but Target became unreachable."
            )
        else:
            app.logger.info("Target reachability verified.")

    finally:
        TRANSITION_STATE["active"] = False

    return status()


@app.route("/restart-target", methods=["POST"])
def restart_target():
    """
    Disables Purist Mode on the Target to ensure internet access,
    then restarts the Diretta service for license activation. Also
    restarts the Roon Bridge service on the Host.
    """
    app.logger.info("Starting license activation sequence...")
    t_status = get_status_from_target(bypass_cache=True)

    if t_status and t_status.get("purist_mode_active"):
        app.logger.info("Purist Mode is active. Disabling it before restart.")
        run_remote_command("/usr/local/bin/pm-toggle-mode")
    else:
        app.logger.info("Purist Mode is not active. Proceeding with restart.")

    app.logger.info("Restarting Diretta ALSA Target service...")
    run_remote_command("/usr/local/bin/pm-restart-target")
    invalidate_status_cache()

    app.logger.info("Restarting Roon Bridge service on Host...")
    try:
        subprocess.run(
            ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "roonbridge.service"],
            check=True
        )
    except subprocess.CalledProcessError as err:
        app.logger.error("Failed to restart Roon Bridge during activation: %s", err)

    now = datetime.now().strftime("%H:%M:%S")
    return (
        f"<span>Restart commands sent at {now}. "
        "Allow 10-15 seconds for backend initialization.</span>"
    )


@app.route("/power/<action>", methods=["POST"])
def power(action):
    """
    Reboots or powers off the pair, Target first.

    The Target is only reachable through the Host, so shutting the Host down
    first would strand it. The Host's own command is deferred to a background
    thread so this response reaches the browser before the machine goes down.
    """
    if action not in ("reboot", "poweroff"):
        return '<span class="text-red-400">Unknown power action.</span>', 400

    verb = "Reboot" if action == "reboot" else "Power off"
    app.logger.info("%s requested for the Target and Host.", verb)

    target_ok = run_remote_command(f"/usr/local/bin/pm-power {action}") is not None
    if not target_ok:
        app.logger.error("Target did not accept the %s command.", action)
    invalidate_status_cache()

    def _shutdown_host():
        # Long enough for the Target to reach its own shutdown, and for this
        # response to have been delivered.
        time.sleep(HOST_POWER_DELAY_SECONDS)
        app.logger.info("Issuing %s on the Host.", action)
        try:
            subprocess.run(
                ["/usr/bin/sudo", "/usr/local/bin/pm-power", action],
                check=False
            )
        except OSError as err:
            app.logger.error("Failed to %s the Host: %s", action, err)

    threading.Thread(target=_shutdown_host, daemon=True).start()

    target_note = (
        "Target is shutting down"
        if target_ok
        else "Target did not respond, continuing anyway"
    )
    tail = (
        "Both machines will restart shortly."
        if action == "reboot"
        else "Both machines must be switched on by hand."
    )
    return (
        f'<span>{verb} sequence started &mdash; {target_note}. '
        f'The Host follows in {HOST_POWER_DELAY_SECONDS} seconds. {tail}</span>'
    )


if __name__ == "__main__":
    is_interactive = sys.stdout.isatty()
    APP_PORT = 8080 if is_interactive else 80
    APP_DEBUG_MODE = is_interactive
    app.run(host="0.0.0.0", port=APP_PORT, debug=APP_DEBUG_MODE)
