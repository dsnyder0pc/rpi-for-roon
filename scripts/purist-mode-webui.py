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
ROON_BRIDGE_VERSION_PATH = "/opt/RoonBridge/VERSION"
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

# A successful poll is cheap to repeat, so it is cached only long enough to
# collapse the burst of requests one page load makes. A failed poll is not: it
# costs a full round of SSH timeouts, and the panels poll on a timer, so an
# uncached failure has every poll and every page load paying that cost again,
# each one serialized behind STATUS_FETCH_LOCK. Requests then arrive faster
# than they drain and the queue grows without bound, which is indistinguishable
# from the UI having hung. Caching the failure too keeps the queue empty.
STATUS_CACHE_TTL = 3.0
STATUS_FAILURE_CACHE_TTL = 10.0

# Every elapsed-time measurement below uses time.monotonic(), never time.time().
# Neither machine has a battery-backed clock: both boot at the fake-hwclock time
# and chronyd steps them forward by weeks a minute or two later, which is inside
# the very window these timers police. Measured on the wall clock, a settling
# period that began before the step reads as weeks long and passes instantly,
# and a step backwards would stall a timer for just as long. Wall-clock time is
# still correct for anything displayed to a person.

# --- Link capacity model ---
# Diretta ALSA runs raw L2 on ethertype 0xcb4b: no IP, no UDP, and a 2-byte
# header of its own. Measured from two 3-minute captures and confirmed at five
# payload sizes (464, 920, 1840, 2000 and 2664 bytes), every audio frame is
# exactly payload + 16 on the wire, and payload + 20 as sysfs counts it.
#
# The same overhead therefore reads as three different numbers, and which one
# is correct depends entirely on where the byte count came from:
#   - 2 bytes against the MTU, which already excludes the Ethernet header.
#   - 16 bytes in a capture, where tshark's frame.len omits the FCS.
#   - 20 bytes in tx_bytes, which counts the Ethernet header and the FCS.
# Subtracting the wrong one is a quiet 18-byte error, so the two constants below
# are deliberately separate rather than one value used on both bases.
#
# The whole design rests on one L2 transmission per cycle, so the usable payload
# rate is whichever of two limits binds first:
#   1. Frame limit: a cycle's payload must fit in a single packet, (MTU - 2).
#   2. Wire limit: that packet plus its Ethernet framing must clear the link
#      inside one cycle, where 40 = 2 Diretta + 14 Ethernet header + 4 FCS
#      + 20 preamble, SFD and interframe gap.
# At every jumbo tier the frame limit binds. The wire limit only takes over on
# the 10 Mbps Super Purist link, which is why that mode caps at DSD64 and
# 32-bit/96 kHz no matter how large the MTU is.
FRAME_HEADER_BYTES = 2
WIRE_OVERHEAD_BYTES = 40
# What a packet costs in tx_bytes beyond its payload: the 2-byte Diretta header
# plus the 14-byte Ethernet header and 4-byte FCS that sysfs counts and the MTU
# does not.
TX_BYTES_OVERHEAD = 20

ALSA_STATUS_PATH = "/proc/asound/card0/pcm0p/sub0/status"

# Absorbs binary rounding where a format lands exactly on the ceiling, as
# DSD256 does at CycleTime 514 and again at MTU 2032. A stream sitting exactly
# on the budget fits, and must not be reported as exceeding it.
PAYLOAD_TOLERANCE = 1e-9

# The width to reckon PCM capacity in when nothing is playing: the widest
# container Diretta offers, so an idle panel quotes the conservative ceiling.
PCM_DEFAULT_SAMPLE_BYTES = 4

# Payload rates are for stereo: DSD is 1 bit per channel, PCM a 32-bit container.
DSD_TIERS = (
    ("DSD64", 0.7056),
    ("DSD128", 1.4112),
    ("DSD256", 2.8224),
    ("DSD512", 5.6448),
    ("DSD1024", 11.2896),
)
PCM_RATES_KHZ = (44.1, 48, 88.2, 96, 176.4, 192, 352.8, 384, 705.6, 768)

def _read_boot_id():
    """Returns the kernel's boot id, which changes on every reboot."""
    try:
        with open("/proc/sys/kernel/random/boot_id", "r", encoding="utf-8") as file_handle:
            return file_handle.read().strip()
    except OSError:
        return "unknown"


# Identifies this boot of this app process. A browser compares it against the
# value its page was served with; any change means the Host rebooted, or the
# service restarted under it. Comparing state this way is immune to a
# backgrounded tab missing the brief window when the Host was unreachable.
INSTANCE_TOKEN = f"{_read_boot_id()}:{int(time.time())}"

app = Flask(__name__)
# A secret key is required for flash messaging
app.secret_key = os.urandom(24)

# --- Global State ---
# Monotonic time starts near zero at boot, so a literal 0 here would read as
# "15 seconds ago" rather than "never" and could swallow the first enforcement.
ENFORCEMENT_STATE = {"last_time": float("-inf")}
ENFORCEMENT_LOCK = threading.Lock()
SETTLE_STATE = {"state": None, "since": 0.0}
SETTLE_LOCK = threading.Lock()
TRANSITION_STATE = {"active": False}
STATUS_CACHE = {"data": None, "timestamp": 0.0, "valid": False}
# MTU only changes across a reboot, so the last value the Target reported stays
# valid. Caching it lets the link panel refresh without any extra SSH traffic.
TARGET_LINK_CACHE = {"mtu": None}
# The activation URL carries the Target's hardware hash and is fixed for as
# long as that Target reports itself unlicensed, so it is fetched once rather
# than on every status poll. Cleared as soon as the Target reports activation.
ACTIVATION_URL_CACHE = {"url": ""}

# The elected cycle is measured inside the render that displays it, from two
# short transmit-counter brackets taken back to back. Nothing is sampled in the
# background: with no browser open the Host does no work at all for this.
ELECTED_CYCLE_CACHE = {"value": None, "t": float("-inf")}
TX_SAMPLE_WINDOW = 0.15     # bracket for one packet-rate reading, in seconds
TX_IDLE_PPS = 20.0          # below this the link is not carrying a stream
TX_RATE_STABLE = 0.10       # the two halves must agree this closely
# A stream holds one cycle for as long as it runs, so a reading this close to
# the last one is the same cycle measured again, not the link changing.
ELECTED_CYCLE_HYSTERESIS = 0.01
# Tab focus and visibility both trigger a refresh, so renders can arrive in a
# burst. One measurement serves the whole burst.
ELECTED_CYCLE_MEMO = 5.0
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

            <div id="power-control" class="absolute top-0 right-0">
                <button type="button" onclick="togglePowerMenu()" aria-haspopup="true"
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
        function togglePowerMenu() {
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

        // The power notice lives outside every auto-refreshing region, so nothing
        // would otherwise clear it: after the machines come back the page keeps
        // showing a stale "sequence started" line. Detection compares the server's
        // instance token rather than watching for the Host to disappear -- a
        // backgrounded tab has its timers throttled to about once a minute and
        // would miss a 30-second outage entirely, never noticing the restart it
        // was waiting for.
        //
        // A power off is watched too. It was once treated as never coming back,
        // but the notice itself tells the user to switch both machines on by
        // hand, so it is precisely the case that does come back -- just on a
        // human's schedule rather than a reboot's. It therefore gets a long
        // window and a slow tick instead of a short, fast one.
        var INSTANCE_TOKEN = "{{ instance_token }}";
        var POWER_WATCHES = {
            'reboot': {
                windowMs: 600000,
                intervalMs: 3000,
                offline: 'Host is restarting. This page will refresh when it returns.',
                expired: 'The Host has not come back yet. Reload this page once it does.'
            },
            'poweroff': {
                windowMs: 43200000,
                intervalMs: 30000,
                offline: 'Both machines are off. Switch them on by hand \u2014 ' +
                         'this page will refresh once the Host is back.',
                expired: 'Reload this page once the machines are switched back on.'
            }
        };
        var powerWatch = null;

        function probeForRestart(messageEl, offlineMessage) {
            return fetch('/alive', {cache: 'no-store'})
                .then(function (response) {
                    if (!response.ok) { throw new Error('not ready'); }
                    return response.text();
                })
                .then(function (token) {
                    if (token.trim() !== INSTANCE_TOKEN) {
                        window.location.reload();
                    }
                })
                .catch(function () {
                    messageEl.textContent = offlineMessage;
                });
        }

        function watchForReturn(messageEl, watch) {
            powerWatch = {deadline: Date.now() + watch.windowMs, watch: watch};
            var tick = function () {
                if (!powerWatch) { return; }
                if (Date.now() > powerWatch.deadline) {
                    messageEl.textContent = watch.expired;
                    powerWatch = null;
                    return;
                }
                probeForRestart(messageEl, watch.offline).then(function () {
                    setTimeout(tick, watch.intervalMs);
                });
            };
            setTimeout(tick, watch.intervalMs);
        }

        // Returning to a throttled background tab is the moment we are most likely
        // to be showing a stale notice, so probe immediately rather than waiting
        // for the next slow tick. That matters most after a power off, whose tick
        // is deliberately slow.
        document.addEventListener('visibilitychange', function () {
            if (document.hidden || !powerWatch) { return; }
            probeForRestart(document.getElementById('power-message'),
                            powerWatch.watch.offline);
        });

        document.body.addEventListener('htmx:afterRequest', function (event) {
            var config = event.detail.requestConfig;
            if (!config || !event.detail.successful) { return; }
            var path = config.path || '';
            var action = null;
            if (path.indexOf('/power/reboot') !== -1) { action = 'reboot'; }
            else if (path.indexOf('/power/poweroff') !== -1) { action = 'poweroff'; }
            if (!action) { return; }
            watchForReturn(document.getElementById('power-message'),
                           POWER_WATCHES[action]);
        });

        // Dismiss on an outside tap, click or Escape, the way a menu is expected to
        // behave. iOS Safari does not deliver click to document for taps on
        // non-interactive elements, so touchstart is needed for the menu to be
        // dismissable on iPhone and iPad at all.
        //
        // Both listeners test containment rather than relying on stopPropagation
        // inside the control: on a touch device a tap on the button fires
        // touchstart before click, so a blanket document handler would close the
        // menu and let the click immediately reopen it, leaving it stuck open.
        function handleOutsidePointer(event) {
            const control = document.getElementById('power-control');
            if (control && control.contains(event.target)) { return; }
            closePowerMenu();
        }

        document.addEventListener('click', handleOutsidePointer);
        document.addEventListener('touchstart', handleOutsidePointer, {passive: true});
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { closePowerMenu(); }
        });
    </script>
</body>
</html>
"""

# A phone freezes JS timers while its screen is off, so the 30s poll stops and
# the panel holds a stale reading until something wakes it. visibilitychange is
# the documented signal for that, but it is not reliably delivered across mobile
# browsers, so window focus is listened for as a second, independent recovery
# path. A refresh costs one 1.4 KB response built from three local file reads,
# far less than the page reload it replaces, so firing twice on wake is cheap.
#
# The card shell is stable and owns the refresh. The fragment endpoint returns
# only the body below, swapped as innerHTML: a fragment that carried its own
# hx-trigger="load" would re-fire the moment it was swapped in, looping forever.
LINK_PANEL_CARD = """
<div id="link-panel" hx-get="/link-status"
     hx-trigger="every 30s, visibilitychange from:document, focus from:window"
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
        <div class="bg-gray-900/40 p-4 cursor-help" title="The Ethernet speed the Host and Target negotiated on the point-to-point cable between them.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Link Speed</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.speed %}{{ link.speed }} Mb/s{% else %}&mdash;{% endif %}
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4 cursor-help" title="The largest Ethernet payload this link will carry.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">MTU</dt>
            <dd class="mt-1 text-lg font-semibold {{ 'text-red-400' if link.mtu_mismatch else 'text-white' }}">
                {{ link.mtu }} bytes
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4 cursor-help" title="How often the Host transmits audio to the Target. The configured value comes from setting.inf; the elected value is measured from the link while music plays. They differ whenever TargetProfileLimitTime is not 0, and by about 1% in the Flex cycle modes.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Cycle Time</dt>
            <dd class="mt-1 text-lg font-semibold {{ 'text-red-400' if link.cycle_mismatch else 'text-white' }}">
                {% if link.cycle_time %}{{ link.cycle_time }} &micro;s{% else %}&mdash;{% endif %}
            </dd>
            {% if link.elected_cycle %}
            <dd class="mt-0.5 text-xs {{ 'text-red-400' if link.cycle_mismatch else 'text-gray-400' }}">
                elected {{ link.elected_cycle }} &micro;s{% if link.frames_per_cycle > 1 %}<span class="text-red-400"> &middot; {{ link.frames_per_cycle }} frames/cycle</span>{% endif %}
            </dd>
            {% elif link.cycle_mismatch %}
            <dd class="mt-0.5 text-xs text-red-400">elected value differs</dd>
            {% endif %}
        </div>
        <div class="bg-gray-900/40 p-4 cursor-help" title="Diretta's information interval, set alongside CycleTime in setting.inf.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Info Cycle</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.info_cycle_ms %}{{ link.info_cycle_ms }} ms{% else %}&mdash;{% endif %}
            </dd>
        </div>
        <div class="bg-gray-900/40 p-4 cursor-help" title="The highest stereo PCM rate that still fits in one transmission per cycle at this MTU and link speed, for the container width in the heading. The link pays for the container rather than the word size, so a 16-bit stream reaches twice the rate a 32-bit one does. The width follows whatever is playing, and reverts to 32-bit when nothing is. A red playing line means the stream costs more than the link can carry: it will either fragment across several transmissions per cycle or fail to clear the wire in time.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Max PCM ({{ link.pcm_width }}-bit)</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.max_pcm %}{{ link.max_pcm }}{% else %}&mdash;{% endif %}
            </dd>
            {% if link.playing_pcm %}
            <dd class="mt-0.5 text-xs {{ 'text-red-400' if link.playing_over_budget else 'text-gray-400' }}">playing {{ link.playing_pcm }}</dd>
            {% endif %}
        </div>
        <div class="bg-gray-900/40 p-4 cursor-help" title="The highest DSD rate that still fits in one transmission per cycle at this MTU and link speed. Native because DoP carries DSD inside PCM frames, so a DoP stream is counted against Max PCM instead and never appears here.">
            <dt class="text-xs uppercase tracking-wide text-gray-500">Max DSD (Native)</dt>
            <dd class="mt-1 text-lg font-semibold text-white">
                {% if link.max_dsd %}{{ link.max_dsd }}{% else %}&mdash;{% endif %}
            </dd>
            {% if link.playing_dsd %}
            <dd class="mt-0.5 text-xs {{ 'text-red-400' if link.playing_over_budget else 'text-gray-400' }}">playing {{ link.playing_dsd }}</dd>
            {% endif %}
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
<div id="control-panel" hx-get="/status"
     hx-trigger="load, every 30s, visibilitychange from:document, focus from:window"
     hx-swap="innerHTML">
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
            <div class="grid {{ 'grid-cols-3' if app8_enabled else 'grid-cols-2' }} gap-2 p-1 bg-gray-900 rounded-xl border border-gray-700">
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
                {% if app8_enabled %}
                <button hx-post="/set-state/SuperPurist" hx-target="#control-panel" hx-swap="innerHTML" hx-disabled-elt="this"
                        class="relative inline-flex items-center justify-center py-3 text-sm font-semibold rounded-lg shadow-sm transition-colors duration-200
                        {{ 'bg-green-600 text-white border border-green-400/30' if current_state == 'SuperPurist' else 'text-gray-400 hover:text-white' }}">
                    <span class="btn-text">Super Purist</span>
                    <span class="absolute btn-spinner hidden h-5 w-5 rounded-full border-2 border-current"></span>
                </button>
                {% endif %}
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
    start_time = time.monotonic()
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

        if not blocking or (time.monotonic() - start_time >= block_timeout):
            break
        time.sleep(1)
    return False


def is_music_playing():
    """Checks if music is actively playing by inspecting /proc/asound/."""
    status_file_path = ALSA_STATUS_PATH
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


def _container_bits(format_name):
    """Width of an ALSA format's sample container, from its name.

    The first run of digits is the container width in every name that carries
    one: S32_LE and DSD_U32_LE are 32, S24_3LE is 24 (packed into 3 bytes, but
    still a 24-bit sample), S16_LE is 16. Names without digits, such as
    FLOAT_LE, return None rather than a guess.
    """
    digits = ""
    for char in format_name:
        if char.isdigit():
            digits += char
        elif digits:
            break
    return int(digits) if digits else None


def _container_bytes(format_name, bits):
    """Bytes each sample occupies on the wire, which is not always bits / 8.

    ALSA distinguishes a packed 24-bit sample (S24_3LE, three bytes) from one
    sitting in a four-byte slot (S24_LE), and the link pays for the slot. This
    device offers only the packed form, but the distinction is the whole reason
    a 24-bit stream can cost either three bytes or four.
    """
    if "_3" in format_name:
        return 3
    if bits <= 8:
        return 1
    return 2 if bits <= 16 else 4


def get_playing_format():
    """Names the format ALSA is currently handing the Diretta bridge.

    Read from hw_params, the sibling of the status file is_music_playing()
    uses. It only holds values while the device is open, so a return of None
    also means nothing is playing.

    This reports the container, which is what the link actually carries, and
    deliberately not the word size the player thinks it is sending. The two
    differ: Roon set to 24 bits opens an S32_LE container and pads each sample
    into it, and Diretta transmits that container verbatim rather than repacking
    it. Measured on this link at 96 kHz, Roon logged `pcm 96000/24/2` while the
    daemon sent `size=1384` -- 173 samples x 2 channels x 4 bytes. Three bytes
    per sample would have been 1038. The Target agrees, logging `set PCM 32`.

    So 24-bit and 32-bit at the same rate are the same stream to this panel,
    because they are the same stream on the wire. Reporting the player's word
    size here would describe what the Host received, not what it sent, on a
    panel whose subject is the point-to-point link. It would also tie a link
    reading to one player's log, when AudioLinux feeds this bridge from several.

    Returns:
        dict: {"label", "is_dsd", "bits", "sample_bytes"}, where label reads
            like "DSD64" or "44.1 kHz". The width is reported separately
            because it belongs to the ceiling rather than to the stream: it
            names which Max PCM figure applies. None when the device is closed
            or the format is not one we can name.
    """
    hw_params_path = "/proc/asound/card0/pcm0p/sub0/hw_params"
    try:
        with open(hw_params_path, "r", encoding="utf-8") as file_handle:
            # A closed device reports a single word rather than key: value
            # lines, which leaves nothing to unpack and reads as "not playing".
            params = {}
            for line in file_handle:
                key, separator, value = line.partition(":")
                if separator:
                    params[key.strip()] = value.strip()
    except OSError:
        return None

    format_name = params.get("format", "")
    bits = _container_bits(format_name)
    try:
        rate = int(params.get("rate", "").split()[0])
    except (ValueError, IndexError):
        return None
    if not bits or rate <= 0:
        return None

    if not format_name.startswith("DSD"):
        # Prefer the word size Roon reports over the container it was padded
        # into, but only where Roon's line agrees with the device about what is
        # playing. A stale or rotated-away line then costs nothing: the label
        # falls back to the container, which is what it said before.
        sample_bytes = _container_bytes(format_name, bits)
        return {"label": f"{rate / 1000:g} kHz", "is_dsd": False, "bits": bits,
                "sample_bytes": sample_bytes,
                "payload_rate": rate * sample_bytes * 2 / 1e6}

    # DSD arrives packed into PCM-shaped words, so its real bit rate is the
    # container rate times the container width: DSD_U32_LE at 88200 is
    # 2.8224 Mbit/s, which is DSD64. Naming the multiple means dividing by
    # whichever base family the rate belongs to.
    base = 44100 if rate % 44100 == 0 else 48000 if rate % 48000 == 0 else None
    if not base:
        return None
    sample_bytes = _container_bytes(format_name, bits)
    return {"label": f"DSD{round(rate * bits / base)}", "is_dsd": True,
            "bits": bits, "sample_bytes": sample_bytes,
            "payload_rate": rate * sample_bytes * 2 / 1e6}


def run_remote_command(command, attempts=SSH_RETRY_ATTEMPTS):
    """
    Executes a command on the Diretta Target via SSH.

    Transport-level failures (exit code 255) and timeouts are expected while the
    link renegotiates speed, so they are retried. A non-255 exit code means the
    remote command itself ran and failed, which is reported immediately.

    A Target that is switched off or unplugged is a different case: it leaves
    end0 without a carrier, so no attempt can reach it and retrying only spends
    ConnectTimeout three times over, inside a request the browser is waiting
    on. That is reported immediately instead.
    """
    if not get_host_link_up():
        app.logger.warning(
            "%s has no carrier; reporting the Target unreachable without "
            "attempting SSH: %s", LINK_INTERFACE, command
        )
        return None

    # Status polls and a user's transition run on separate threads, so their
    # log lines interleave. Tagging every line with the remote script's name
    # keeps a command and its output readable as a pair.
    label = command.rsplit("/", 1)[-1].split()[0] if command.strip() else command

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
            app.logger.info(
                "[%s] Running remote command: %s", label, " ".join(ssh_command)
            )
            result = subprocess.run(
                ssh_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=15
            )
            output = result.stdout.strip()
            app.logger.info("[%s] Remote command successful. Output: %s", label, output)
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


def _read_status_cache(now):
    """
    Returns (hit, data) for the status cache under its per-outcome lifetime.

    A cached failure is a hit like any other, so the "valid" flag rather than
    the data itself decides whether an entry exists.
    """
    with STATUS_CACHE_LOCK:
        if not STATUS_CACHE["valid"]:
            return False, None
        lifetime = (
            STATUS_CACHE_TTL if STATUS_CACHE["data"] is not None
            else STATUS_FAILURE_CACHE_TTL
        )
        if (now - STATUS_CACHE["timestamp"]) < lifetime:
            return True, STATUS_CACHE["data"]
    return False, None


def _write_status_cache(data, now):
    """Records a poll outcome, success or failure alike."""
    with STATUS_CACHE_LOCK:
        STATUS_CACHE["data"] = data
        STATUS_CACHE["timestamp"] = now
        STATUS_CACHE["valid"] = True


def _get_activation_url():
    """Returns the Target's license activation URL, fetching it at most once.

    The URL encodes the Target's own hardware hash, so it cannot change while
    that Target keeps reporting the same unlicensed state. Fetching it inside
    every status poll cost a second SSH round trip every 30 seconds for as
    long as a system sat unlicensed. A failed fetch is not cached, so the next
    poll retries.
    """
    if ACTIVATION_URL_CACHE["url"]:
        return ACTIVATION_URL_CACHE["url"]

    url = run_remote_command("/usr/local/bin/pm-get-license-url")
    if url:
        ACTIVATION_URL_CACHE["url"] = url
    return url or ""


def get_status_from_target(bypass_cache=False):
    """Gets the current status from the Diretta Target, using a brief cache."""
    if not bypass_cache:
        hit, cached = _read_status_cache(time.monotonic())
        if hit:
            app.logger.info("Returning cached Target status.")
            return cached

    # Use a lock to ensure only one thread performs the slow SSH fetch at a time
    with STATUS_FETCH_LOCK:
        now = time.monotonic()
        # Whoever held the lock has just refreshed the cache, and a failure
        # refreshes it too, so a queue that built up behind an unreachable
        # Target drains at once rather than each waiter starting its own poll.
        if not bypass_cache:
            hit, cached = _read_status_cache(now)
            if hit:
                app.logger.info("Returning cached Target status (after lock).")
                return cached

        raw_status = run_remote_command("/usr/local/bin/pm-get-status")
        if not raw_status:
            _write_status_cache(None, now)
            return None

        try:
            status_data = json.loads(raw_status)
            if status_data.get("license_needs_activation"):
                status_data["activation_url"] = _get_activation_url()
            else:
                # Activated, or a different Target: drop the memo so a later
                # unlicensed Target is asked for its own URL.
                ACTIVATION_URL_CACHE["url"] = ""
                status_data["activation_url"] = ""

            # Older Targets predate the mtu field; absent it, the link panel
            # simply omits the agreement check rather than guessing.
            if status_data.get("mtu"):
                TARGET_LINK_CACHE["mtu"] = status_data["mtu"]

            _write_status_cache(status_data, now)
            return status_data
        except json.JSONDecodeError:
            app.logger.error(
                "Failed to decode JSON status from remote host. Received: %s",
                raw_status
            )
            _write_status_cache(None, now)
            return None


def invalidate_status_cache():
    """Clears the target status cache to force a fresh SSH poll."""
    with STATUS_CACHE_LOCK:
        STATUS_CACHE["data"] = None
        STATUS_CACHE["timestamp"] = 0.0
        STATUS_CACHE["valid"] = False


def roon_bridge_is_installed():
    """Reports whether Roon Bridge is installed on this Host.

    The AudioLinux Three-Tier images ship without Roon Bridge, so a user who
    runs HQPlayer NAA, UPnP or another protocol has no roonbridge.service to
    act on. Roon Bridge self-updates in place, so its VERSION file is a
    cheaper and more current signal than querying the package database.
    """
    return os.path.exists(ROON_BRIDGE_VERSION_PATH)


def roon_is_available():
    """Reports whether the Roon IR Remote feature should be offered.

    The remote is only useful when this Host is a Roon endpoint, so both the
    IR remote's own config (Appendix 2) and Roon Bridge must be present. The
    remote stays installed either way, so the tab appears on its own if the
    user adds Roon Bridge later.
    """
    return os.path.exists(ROON_CONFIG_PATH) and roon_bridge_is_installed()


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


def _pcm_payload_rate(rate_khz, sample_bytes=PCM_DEFAULT_SAMPLE_BYTES):
    """Stereo PCM payload rate in bytes per microsecond.

    The link pays for the container, not the word size, so a 16-bit stream
    costs half what a 32-bit one does at the same rate and a packed 24-bit
    stream costs three quarters. That is a factor of two across the widths
    Diretta offers, which is why this is a parameter rather than a constant.
    """
    return rate_khz * 1000.0 * float(sample_bytes) * 2.0 / 1_000_000.0


def _read_tx_counters():
    """Reads end0's cumulative transmit counters, or None when unavailable."""
    try:
        base = "/sys/class/net/end0/statistics/"
        with open(base + "tx_packets", encoding="utf-8") as file_handle:
            packets = int(file_handle.read())
        with open(base + "tx_bytes", encoding="utf-8") as file_handle:
            octets = int(file_handle.read())
        return packets, octets
    except (OSError, ValueError):
        return None


def _counter_rate(before, after, span):
    """Packets per second between two counter reads, or None if unusable."""
    if before is None or after is None or span <= 0:
        return None
    packets = after[0] - before[0]
    return packets / span if packets > 0 else None


def _measure_packet_rate():
    """Brackets two contiguous windows and returns (packets/s, bytes/packet).

    Three counter reads make two halves and one whole. The halves are compared
    against each other to catch a stream starting or stopping mid-measurement,
    but the rate itself is taken across the full span: a packet rate is a count
    of whole packets, and the one that may fall either side of an edge carries
    half as much weight over twice the span. Measuring the halves separately
    and keeping one would throw that accuracy away.

    Each span is measured rather than assumed, so however the sleeps are
    scheduled the rate stays exact to within the time it takes to read two
    sysfs files. Returns None while the link is carrying no stream.
    """
    first = _read_tx_counters()
    start = time.monotonic()
    if first is None:
        return None

    # A quiet link is settled by the first half, so silence costs one window.
    time.sleep(TX_SAMPLE_WINDOW)
    middle = _read_tx_counters()
    split = time.monotonic()
    early = _counter_rate(first, middle, split - start)
    if early is None or early < TX_IDLE_PPS:
        return None

    # A half straddling the start or stop of a stream counts packets for only
    # part of its span, which reads as a far longer cycle than the truth and
    # would raise a false mismatch. Trust the pair only where they agree.
    time.sleep(TX_SAMPLE_WINDOW)
    last = _read_tx_counters()
    end = time.monotonic()
    late = _counter_rate(middle, last, end - split)
    if late is None or abs(late - early) > TX_RATE_STABLE * early:
        return None

    packets = last[0] - first[0]
    return packets / (end - start), (last[1] - first[1]) / packets


def _cycle_from_rate(pps, bytes_per_packet, cycle_time, mtu):
    """Turns a measured packet rate into the cycle it implies.

    Returns:
        dict: {"us", "frames", "diverges"} describing the cycle. "us" is None
            when the stream is fragmented and the frame count cannot be pinned
            down; "diverges" is still meaningful there, because a packet rate
            that is not a whole multiple of the configured cycle proves the two
            disagree. None when the shape of the stream says nothing at all.
    """
    # Diretta splits a cycle's payload across the fewest frames that fit the
    # MTU, so a frame no larger than half the usable payload cannot have been
    # split: one frame per cycle, and the cycle is just the packet interval.
    # bytes_per_packet comes from tx_bytes and usable from the MTU, so the two
    # need different overheads subtracted to be comparable at all.
    payload = bytes_per_packet - TX_BYTES_OVERHEAD
    usable = mtu - FRAME_HEADER_BYTES if mtu else 0
    if usable > 0 and payload * 2 <= usable:
        elected = 1e6 / pps
        return {"us": elected, "frames": 1,
                "diverges": _diverges(elected, cycle_time)}

    # A fragmented stream is ambiguous from counters alone, so fall back to the
    # frame count the configured cycle implies. A ratio that lands on a whole
    # number means the cycle is being honoured; one that does not is proof it
    # is not, even though the elected value stays unknown.
    if not cycle_time:
        return None

    frames = pps * cycle_time / 1e6
    nearest = round(frames)
    # Reporting no divergence here is not an assumption, it is the same 5%
    # threshold _diverges() applies, expressed in frames: at N frames per cycle
    # a ratio within 0.05 of N is a cycle within 5%/N of the configured one. So
    # a stream that lands inside this tolerance would pass _diverges() too. Real
    # 32-bit 768 kHz measures 2.998 against 3 and reports honestly.
    if nearest >= 1 and abs(frames - nearest) <= 0.05:
        return {"us": nearest * 1e6 / pps, "frames": nearest, "diverges": False}
    return {"us": None, "frames": None, "diverges": True}


def _measure_elected_cycle(cycle_time, mtu):
    """Derives the cycle Diretta actually transmits on, from the link counters.

    `CycleTime` in setting.inf is what the Host asks for, not necessarily what
    it gets. A non-zero TargetProfileLimitTime hands the choice to Diretta\'s
    automatic target profile, and even at 0 the Flex modes land a little above
    the request. The daemon states its choice at stream start, but Appendix 8
    leaves Debug disabled, so on a finished build the wire is the only source.

    One self-contained bracket, needing nothing from the render before it, so
    the figure is complete the first time the panel is drawn and cannot be lost
    by refreshing at the wrong moment.

    Returns:
        dict: the cycle as described by `_cycle_from_rate`, or None while
            nothing is playing or the bracket caught a stream starting.
    """
    measured = _measure_packet_rate()
    if measured is None:
        return None
    return _cycle_from_rate(measured[0], measured[1], cycle_time, mtu)


def _same_cycle(previous, current):
    """True when a reading is the last one measured again, not a new cycle.

    A stream holds one cycle for as long as it runs, so two readings a hair
    apart are one cycle measured twice, and the gap between them is this
    measurement\'s own noise rather than anything the link did. Redrawing that
    gap as a fresh number on every refresh would present noise as signal.
    """
    if not previous or not current:
        return False
    if previous.get("frames") != current.get("frames"):
        return False

    before, after = previous.get("us"), current.get("us")
    if before is None or after is None:
        return before is after
    return abs(after - before) <= ELECTED_CYCLE_HYSTERESIS * before


def get_elected_cycle(cycle_time, mtu):
    """Returns the measured cycle, reusing one taken moments ago.

    Only the memo and the settled figure span renders. A reading the memo has
    outlived is remeasured rather than shown, so a stopped stream drops the
    figure at the next refresh instead of leaving a stale one on the page.
    """
    cached = dict(ELECTED_CYCLE_CACHE)
    if time.monotonic() - cached["t"] <= ELECTED_CYCLE_MEMO:
        return cached["value"]

    value = _measure_elected_cycle(cycle_time, mtu)
    # Hold the figure still while it is the same cycle, so the panel reports a
    # cycle that changed only when one did.
    if _same_cycle(cached["value"], value):
        value = cached["value"]
    ELECTED_CYCLE_CACHE.update(value=value, t=time.monotonic())
    return value


def _diverges(elected_us, cycle_time):
    """True when the measured cycle is more than 5% off the configured one.

    The Flex modes overshoot by about 1%, which is expected and should not be
    reported as a fault.
    """
    if not elected_us or not cycle_time:
        return False
    return abs(elected_us - cycle_time) / cycle_time > 0.05


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


def get_max_formats(budget, sample_bytes=PCM_DEFAULT_SAMPLE_BYTES):
    """Returns the highest DSD tier and PCM sample rate that fit within a budget.

    `sample_bytes` is the width of the PCM container currently on the wire, so
    the PCM ceiling describes the stream actually playing rather than a 32-bit
    one that may not be.
    """
    if budget is None or budget <= 0:
        return None, None

    tolerance = PAYLOAD_TOLERANCE

    max_dsd = None
    for name, rate in DSD_TIERS:
        if rate <= budget + tolerance:
            max_dsd = name

    max_pcm = None
    for rate_khz in PCM_RATES_KHZ:
        if _pcm_payload_rate(rate_khz, sample_bytes) <= budget + tolerance:
            max_pcm = f"{rate_khz:g} kHz"

    return max_dsd, max_pcm


def _us_to_ms(microseconds):
    """
    Renders a microsecond period as milliseconds, trimming trailing zeros.

    InfoCycle is far longer than CycleTime, so setting.inf tends to hold
    six-figure microsecond values that read more easily as 180 ms than as
    180000 us. Trailing zeros are trimmed, leaving a decimal only when set.
    """
    if not microseconds or microseconds <= 0:
        return None

    return f"{microseconds / 1000.0:g}"


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
    info_cycle = _get_current_infocycle()
    target_mtu = TARGET_LINK_CACHE["mtu"]
    link_up = get_host_link_up()

    # The PCM ceiling is quoted for the container actually on the wire, since a
    # 16-bit stream costs half what a 32-bit one does and would otherwise be
    # measured against a limit that does not apply to it. With nothing playing
    # there is no container to speak of, so the widest one stands as the
    # conservative default.
    playing = get_playing_format()
    pcm_playing = playing if playing and not playing["is_dsd"] else None
    sample_bytes = pcm_playing["sample_bytes"] if pcm_playing else PCM_DEFAULT_SAMPLE_BYTES

    # Without a negotiated speed the wire limit cannot be applied, and the frame
    # limit alone would overstate the link: it would claim DSD256 on a 10 Mbps
    # Super Purist connection. Report nothing rather than something unfounded.
    budget = get_payload_budget(mtu, cycle_time, speed) if link_up and speed else None
    if budget:
        max_dsd, max_pcm = get_max_formats(budget, sample_bytes)
    else:
        max_dsd, max_pcm = None, None

    # Measured against the budget rather than the frames it needs, because the
    # two failure modes differ. Overrunning the frame limit fragments the cycle
    # and shows up as frames/cycle: the stream plays on, indefinitely and
    # invisibly, which is why it wants a warning at all. Overrunning the wire
    # limit still fits one frame but cannot clear it in time, and on a 10 Mbps
    # Super Purist link that has been seen to stop playback outright -- the Roon
    # zone drops and takes ~20s to reset before anything will play again.
    #
    # That last observation comes from 32-bit PCM and native DSD only. A stream
    # barely over the line, such as the packed 24-bit a UPnP source can send and
    # Roon cannot, may yet degrade instead of failing; treat "it stops dead" as
    # the tested case rather than the rule.
    #
    # Either way the panel seldom gets to colour a wire-limit overrun, since the
    # device closes before the next render. The warning that earns its keep
    # there is the ceiling shown while idle, read before anyone tries.
    over_budget = bool(
        budget and playing and playing["payload_rate"] > budget + PAYLOAD_TOLERANCE
    )

    elected = get_elected_cycle(cycle_time, mtu) or {}

    return {
        "up": link_up,
        "speed": speed,
        "mtu": mtu,
        "target_mtu": target_mtu,
        # A silent MTU mismatch is the failure this panel most needs to surface:
        # the link still comes up, but every full-size frame is discarded.
        "mtu_mismatch": target_mtu is not None and target_mtu != mtu,
        # Both cycle figures come straight from setting.inf, as periods rather
        # than as a packet rate: InfoCycle's transport is not the L2 stream, so
        # a frames-per-second reading would be speculation.
        "cycle_time": cycle_time,
        # What setting.inf asks for and what the link actually runs are not the
        # same number whenever the target profile is electing the cycle.
        "elected_cycle": round(elected["us"]) if elected.get("us") else None,
        "frames_per_cycle": elected.get("frames"),
        "cycle_mismatch": bool(elected.get("diverges")),
        "cycle_measured": bool(elected),
        "info_cycle_ms": _us_to_ms(info_cycle),
        "max_dsd": max_dsd,
        "max_pcm": max_pcm,
        # Filed under whichever ceiling it belongs beneath, so the reader sees
        # what is playing against the limit that applies to it. Both are None
        # while the bridge is closed, which is how the panel learns that
        # nothing is playing. The width names the ceiling rather than the
        # stream, so it sits in the heading instead of on this line.
        "playing_pcm": pcm_playing["label"] if pcm_playing else None,
        "playing_dsd": playing["label"] if playing and playing["is_dsd"] else None,
        "pcm_width": sample_bytes * 8 if not pcm_playing else pcm_playing["bits"],
        # True when what is playing costs more than the link can carry, whether
        # it fragments or merely fails to keep up.
        "playing_over_budget": over_budget,
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


def core_isolation_configured():
    """Reports whether Appendix 6 has reserved cores 2-3 for audio.

    Without it, a wide affinity is the expected state rather than a fault, and
    saying so at WARNING on every status poll buries the real regression: the
    isolation is configured but the running process is not on those cores.
    """
    try:
        with open("/opt/configuration/isolated.conf", "r", encoding="utf-8") as file_handle:
            return 'ISOLATED1="2,3"' in file_handle.read()
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

            if core_isolation_configured():
                app.logger.warning(
                    "Diretta running on non-isolated cores though Appendix 6 "
                    "reserves 2-3. Actual affinity: %s", affinity_list
                )
            else:
                app.logger.info(
                    "Core isolation not configured (Appendix 6 not applied); "
                    "using the baseline profile. Affinity: %s", affinity_list
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


def _apply_settings(lines, wanted):
    """Rewrites the wanted keys in setting.inf, adding any the file lacks.

    A key the installer never wrote has to be added rather than skipped: the
    old behaviour left it out silently, so Diretta kept running the previous
    profile behind a UI reporting the new one.
    """
    new_lines = []
    seen = set()
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else None
        if key in wanted:
            new_lines.append(f"{key}={wanted[key]}\n")
            seen.add(key)
        else:
            new_lines.append(line)

    missing = [key for key in wanted if key not in seen]
    if missing:
        app.logger.warning("setting.inf was missing %s; adding.", ", ".join(missing))
        # Keys belong under the section header, not after an unrelated section.
        insert_at = next(
            (i + 1 for i, ln in enumerate(new_lines) if ln.lstrip().startswith("[")),
            len(new_lines),
        )
        for key in missing:
            new_lines.insert(insert_at, f"{key}={wanted[key]}\n")

    return new_lines


def update_setting_inf(cycle_time, info_cycle):
    """Reads setting.inf, updates CycleTime and InfoCycle, and writes it back.

    Returns:
        bool: True once the file holds the requested values. Callers must not
            restart Diretta on a False return -- the running config is then
            unchanged, and a restart would present the previous profile as a
            completed mode switch, which is invisible from the UI.
    """
    if not os.path.exists(DIRETTA_SETTING_PATH):
        app.logger.error("Cannot update %s: file does not exist.", DIRETTA_SETTING_PATH)
        return False

    wanted = {"CycleTime": str(cycle_time), "InfoCycle": str(info_cycle)}
    try:
        with open(DIRETTA_SETTING_PATH, "r", encoding="utf-8") as file_handle:
            lines = file_handle.readlines()

        new_lines = _apply_settings(lines, wanted)

        app.logger.info("Writing new Diretta config: CycleTime=%s, InfoCycle=%s",
                        cycle_time, info_cycle)
        tmp_file = "/tmp/setting.inf.tmp"
        with open(tmp_file, "w", encoding="utf-8") as file_handle:
            file_handle.writelines(new_lines)

        mv_cmd = ["/usr/bin/sudo", "/usr/bin/mv", tmp_file, DIRETTA_SETTING_PATH]
        subprocess.run(mv_cmd, check=True)
        return True

    except OSError as err:
        app.logger.error("File operation error while updating setting.inf: %s", err)
    except subprocess.CalledProcessError as err:
        app.logger.error("Sudo mv failed when updating setting.inf: %s", err)
    return False


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
        if roon_bridge_is_installed():
            subprocess.run(
                [
                    "/usr/bin/sudo", "/usr/bin/systemctl",
                    "restart", "roonbridge.service"
                ],
                check=True
            )
        else:
            app.logger.info("Roon Bridge not installed; skipping its restart.")
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


def _get_setting_int(key):
    """Parses an integer setting from setting.inf, or 0 when it is unreadable."""
    try:
        with open(DIRETTA_SETTING_PATH, "r", encoding="utf-8") as file_handle:
            for line in file_handle:
                if line.startswith(f"{key}="):
                    return int(line.strip().split("=")[1])
    except (OSError, ValueError, IndexError):
        pass
    return 0


def _get_current_cycletime():
    """Parses the current CycleTime from setting.inf."""
    return _get_setting_int("CycleTime")


def _get_current_infocycle():
    """Parses the current InfoCycle from setting.inf."""
    return _get_setting_int("InfoCycle")


def _pending_boot_state(target_status):
    """
    Returns the state the system is booting into, or None if it has arrived.

    purist-mode-auto waits 60 seconds after boot so the Target can set its clock
    and fetch its license, so the Target honestly reports Purist Mode inactive
    for that window. The Host meanwhile clamped the link from the flag the
    moment it booted, which is deliberate: coming up at 100 Mbps and
    renegotiating down to 10 a minute later would halt any playback already in
    progress, whereas the Target enabling Purist Mode in the background is
    invisible. Reporting Standard through that window would therefore label the
    system with a mode whose link speed does not match the one on display.
    """
    # An explicit user action is judged on what is, not on what boot intended.
    if TRANSITION_STATE["active"]:
        return None

    if not target_status.get("auto_start_enabled", False):
        return None

    uptime = _get_host_uptime()
    if uptime is None or uptime >= BOOT_SETTLE_SECONDS:
        return None

    return "SuperPurist" if os.path.exists(SUPER_PURIST_FLAG) else "Purist"


def get_current_system_state(target_status):
    """Derives the friendly UI state name based on Target flags and Host flags."""
    if not target_status:
        return "Standard"
    if not target_status.get("purist_mode_active", False):
        return _pending_boot_state(target_status) or "Standard"
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

    # 3. Apply settings and restart. Restarting after a failed write would
    #    report a mode switch that did not happen; leaving the profile visibly
    #    wrong instead lets the next enforcement pass retry it.
    if update_setting_inf(cycle_time=expected_ct, info_cycle=expected_ic):
        restart_diretta_services()
    else:
        app.logger.error(
            "Skipping service restart: setting.inf still holds the previous "
            "profile (wanted CycleTime=%s, InfoCycle=%s).",
            expected_ct, expected_ic
        )

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

    # 3. Apply settings and restart. Restarting after a failed write would
    #    report a mode switch that did not happen; leaving the profile visibly
    #    wrong instead lets the next enforcement pass retry it.
    if update_setting_inf(cycle_time=expected_ct, info_cycle=expected_ic):
        restart_diretta_services()
    else:
        app.logger.error(
            "Skipping service restart: setting.inf still holds the previous "
            "profile (wanted CycleTime=%s, InfoCycle=%s).",
            expected_ct, expected_ic
        )

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
    now = time.monotonic()
    with SETTLE_LOCK:
        if SETTLE_STATE["state"] != current_state:
            SETTLE_STATE["state"] = current_state
            SETTLE_STATE["since"] = now
        return now - SETTLE_STATE["since"]


def _enforcement_settled(current_state, held_for, auto_start_pending):
    """
    Decides whether a detected mismatch is stable enough to act on.

    Guards against the boot race where the Target is reachable but has not yet
    applied Purist Mode, which would otherwise derive as Standard and drive a
    full profile flip that has to be undone moments later.

    That race only exists while purist-mode-auto is still going to fire. With
    activate-on-boot disabled the Target reverts on boot and then stays put, so
    its first stable reading is already final. Waiting out the full boot window
    anyway would leave a stale Super Purist flag clamping the link to 10 Mbps
    for two and a half minutes while the UI correctly reads Standard. The
    settling period below still covers the opposite race, where the Target
    briefly reports leftover Purist Mode before revert-on-boot completes.
    """
    uptime = _get_host_uptime()
    if auto_start_pending and uptime is not None and uptime < BOOT_SETTLE_SECONDS:
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

    profile_matches = (
        current_speed_val == expected_speed and current_ct == expected_ct
    )
    flag_stale = _super_purist_flag_is_stale(target_status)

    # A stale flag is worth acting on even when the live profile already looks
    # right: nothing else would ever clear it, and it would clamp the link at
    # the next boot.
    if profile_matches and not flag_stale:
        return

    if not _enforcement_settled(
        current_state, held_for, target_status.get("auto_start_enabled", False)
    ):
        return

    if flag_stale:
        reconcile_super_purist_flag(target_status)

    if not profile_matches:
        with ENFORCEMENT_LOCK:
            # Cooldown to prevent thread spamming during fast clicks or polling
            if time.monotonic() - ENFORCEMENT_STATE["last_time"] < 15:
                return
            ENFORCEMENT_STATE["last_time"] = time.monotonic()

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
    roon_configured = roon_is_available()

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
    roon_configured = roon_is_available()
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
    roon_configured = roon_is_available()
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

@app.context_processor
def inject_instance_token():
    """Makes the instance token available to every rendered template."""
    return {"instance_token": INSTANCE_TOKEN}


@app.route("/alive")
def alive():
    """Identifies the running instance so a browser can spot a completed reboot."""
    return INSTANCE_TOKEN


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
        current_state=current_state,
        app8_enabled=is_app8_enabled()
    )


def _clear_super_purist_flag():
    """Safely removes the super purist flag from disk if it exists."""
    if os.path.exists(SUPER_PURIST_FLAG):
        try:
            os.remove(SUPER_PURIST_FLAG)
            app.logger.info("Super Purist Mode flag cleanly removed from disk.")
        except OSError as err:
            app.logger.error("Failed to remove Super Purist flag file: %s", err)


def _super_purist_flag_is_stale(target_status):
    """
    Reports whether the flag on disk contradicts the Target.

    Super Purist is a layer on top of Purist Mode, so the flag is only
    meaningful while the Target actually has Purist Mode active.
    """
    if not target_status or target_status.get("purist_mode_active", False):
        return False
    return os.path.exists(SUPER_PURIST_FLAG)


def reconcile_super_purist_flag(target_status):
    """
    Drops a Super Purist flag that no longer reflects reality.

    The flag alone drives the Host's boot-time link clamp in set-link-speed.sh,
    so one left behind by a failed transition silently pins end0 to 10 Mbps at
    every boot while the UI still derives Standard.

    Callers on the background path must only invoke this once the derived state
    has settled: inside the boot window the Target reads as not-purist before
    purist-mode-auto has engaged, and acting then would delete a legitimate flag.
    """
    if not _super_purist_flag_is_stale(target_status):
        return

    app.logger.warning(
        "Stale Super Purist flag found while the Target is not in Purist "
        "Mode. Clearing it so the boot-time clamp cannot pin end0 to 10 Mbps."
    )
    _clear_super_purist_flag()


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


def _enforce_profile_after_transition(updated_status):
    """Aligns the link speed and Diretta profile with the state just selected."""
    current_speed_str = _get_current_speed()
    if not current_speed_str or "Unknown" in current_speed_str:
        return

    current_speed_val = current_speed_str.replace("Mb/s", "").strip()
    current_ct = _get_current_cycletime()

    current_state = get_current_system_state(updated_status)
    expected_speed = get_target_speed(current_state, updated_status)
    expected_ct, expected_ic = get_target_profile(current_state)

    if current_speed_val == expected_speed and current_ct == expected_ct:
        return

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


@app.route("/set-state/<state_name>", methods=["POST"])
def set_state(state_name):
    """HTMX endpoint to transition the system explicitly between operational states."""
    # Super Purist is the 10 Mbps layer, and only Appendix 8 installs the
    # boot-time clamp that keeps the link there. Without it the transition
    # would still drop both ends to 10 Mbps via ethtool, then lose that speed
    # at the next reboot while the flag survived -- a link and a Diretta
    # profile describing different modes. The button is hidden in that case,
    # so this catches a hand-made request.
    if state_name == "SuperPurist" and not is_app8_enabled():
        app.logger.warning(
            "Super Purist requested but limit-speed-100m.service is not "
            "enabled (Appendix 8 not installed). Refusing the transition."
        )
        return status()

    TRANSITION_STATE["active"] = True

    # The flag is what the Host's boot script reads to clamp the link, so it has
    # to record the user's intent, not merely a request that may abort below.
    # Every path out of Super Purist clears it immediately: the reachability and
    # status checks that follow can return early, and previously did so without
    # ever reaching _transition_to_standard, stranding the flag on disk.
    if state_name != "SuperPurist":
        _clear_super_purist_flag()

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
            # A Super Purist request that failed to engage Purist Mode on the
            # Target must not leave its flag behind to clamp the next boot.
            reconcile_super_purist_flag(updated_status)
            _enforce_profile_after_transition(updated_status)

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

    if roon_bridge_is_installed():
        app.logger.info("Restarting Roon Bridge service on Host...")
        try:
            subprocess.run(
                ["/usr/bin/sudo", "/usr/bin/systemctl", "restart", "roonbridge.service"],
                check=True
            )
        except subprocess.CalledProcessError as err:
            app.logger.error("Failed to restart Roon Bridge during activation: %s", err)
    else:
        app.logger.info("Roon Bridge not installed; skipping its restart.")

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
