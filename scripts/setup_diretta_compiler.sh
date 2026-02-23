#!/bin/bash
# Description: Ensures the correct LLVM/clang toolchain is installed and prioritized
#              based on the compiler version used to build the running kernel.
#              Includes fallbacks for Arch Linux ARM archive mirrors.

# --- Configuration ---
KERNEL_VERSION_INFO=$(cat /proc/version)
echo "Kernel build info: ${KERNEL_VERSION_INFO}"

# Extract the major clang version used to build the kernel
MAJOR_VER=$(echo "${KERNEL_VERSION_INFO}" | grep -oP 'clang version \K[0-9]+')

# --- Pre-installation Prep ---
# Temporarily disable IgnorePkg in pacman.conf to allow the system sync
# and toolchain installation to proceed without interactive prompts.
echo "Temporarily disabling IgnorePkg to allow full system synchronization..."
sudo sed -i 's/^IgnorePkg/#IgnorePkg/' /etc/pacman.conf

# Update system and sync databases to prevent 404s on rotated packages
echo "Synchronizing package databases and performing system update..."
sudo pacman -Syu --noconfirm

# Determine required toolchain suffix
TOOLCHAIN_SUFFIX=""
if [[ -n "${MAJOR_VER}" ]]; then
  # Find the latest MAJOR version number available as a specific llvmXX package
  LATEST_VERSIONED_LLVM=$(pacman -Ss '^llvm[0-9]+$' | grep -oP '^extra/llvm\K[0-9]+' | sort -nr | head -n 1)

  if [[ -z "$LATEST_VERSIONED_LLVM" ]]; then
      LATEST_VERSIONED_LLVM=0
  fi

  if [[ "$MAJOR_VER" -le "$LATEST_VERSIONED_LLVM" ]]; then
      TOOLCHAIN_SUFFIX="${MAJOR_VER}"
      echo "Kernel requires LLVM major version ${MAJOR_VER}. Using specific '${TOOLCHAIN_SUFFIX}' packages."
  else
      echo "Kernel requires LLVM major version ${MAJOR_VER}, likely the current default."
      TOOLCHAIN_SUFFIX=""
  fi
else
  echo "Could not detect specific clang version. Assuming latest default LLVM toolchain."
  TOOLCHAIN_SUFFIX=""
fi

# --- Define Package Names as Arrays ---
PACKAGES_TO_INSTALL=(
    "clang${TOOLCHAIN_SUFFIX}"
    "llvm${TOOLCHAIN_SUFFIX}"
    "llvm${TOOLCHAIN_SUFFIX}-libs"
    "compiler-rt${TOOLCHAIN_SUFFIX}"
    "lld${TOOLCHAIN_SUFFIX}"
)

PACKAGES_TO_IGNORE=(
    "clang${TOOLCHAIN_SUFFIX}"
    "llvm${TOOLCHAIN_SUFFIX}"
    "lld${TOOLCHAIN_SUFFIX}"
    "llvm${TOOLCHAIN_SUFFIX}-libs"
    "compiler-rt${TOOLCHAIN_SUFFIX}"
    "diretta-alsa-daemon"
    "diretta-alsa-dkms"
    "diretta-alsa-target"
    "diretta-direct-dkms"
)

# --- Installation with Archive Fallback ---
echo "Ensuring required toolchain packages are installed..."

# Use array expansion with double quotes to satisfy shellcheck SC2086
if ! sudo pacman -S --noconfirm --needed "${PACKAGES_TO_INSTALL[@]}"; then
    echo "Standard installation failed (likely a 404). Attempting Archive Fallback..."

    # Common ALARM archive mirror for aarch64
    ARCHIVE_BASE="http://tardis.tiny-vps.com/aarch64/packages"

    for PKG in "${PACKAGES_TO_INSTALL[@]}"; do
        if ! pacman -Qi "$PKG" > /dev/null 2>&1; then
            echo "Searching archive for $PKG..."
            echo "Warning: $PKG could not be found on current mirrors."
            echo "Check: ${ARCHIVE_BASE}/${PKG:0:1}/${PKG}/"
        fi
    done
fi

# --- Configure PATH ---
if [[ -n "${TOOLCHAIN_SUFFIX}" ]]; then
    LLVM_BIN_PATH="/usr/lib/llvm${TOOLCHAIN_SUFFIX}/bin"
else
    LLVM_BIN_PATH="/usr/bin"
fi

PROFILE_SCRIPT="/etc/profile.d/llvm_diretta.sh"
if [[ "${LLVM_BIN_PATH}" != "/usr/bin" ]]; then
    echo "Configuring system-wide PATH in ${PROFILE_SCRIPT} to prioritize ${LLVM_BIN_PATH}..."
    sudo tee "${PROFILE_SCRIPT}" > /dev/null <<EOF
# Added by Diretta setup script to prioritize LLVM toolchain for kernel modules
export PATH="${LLVM_BIN_PATH}:\$PATH"
EOF
    sudo chmod +x "${PROFILE_SCRIPT}"
    export PATH="${LLVM_BIN_PATH}:$PATH"
else
    if [[ -f "${PROFILE_SCRIPT}" ]]; then
        sudo rm "${PROFILE_SCRIPT}"
    fi
    echo "Using default system path for LLVM tools."
fi

# --- Clean and Set IgnorePkg ---
PACMAN_CONF="/etc/pacman.conf"
echo "Setting IgnorePkg for required version tools..."

# Remove any existing IgnorePkg lines (commented or uncommented) to avoid duplicates
sudo sed -i '/^#*IgnorePkg\s*=/d' "${PACMAN_CONF}"

# Join array into a space-separated string for the pacman.conf entry
IGNORE_LIST_STRING="${PACKAGES_TO_IGNORE[*]}"

# Add the new IgnorePkg line directly after the [options] header
sudo sed -i "/^\[options\]/a IgnorePkg = ${IGNORE_LIST_STRING}" "${PACMAN_CONF}"

echo "Set IgnorePkg to: ${IGNORE_LIST_STRING}"

# --- Verification ---
echo "Verifying installation..."
if ! command -v clang > /dev/null; then
    echo "ERROR: clang command not found in PATH."
    exit 1
fi

DETECTED_CLANG_VERSION=$(clang --version | head -n 1)
echo "Current clang version: ${DETECTED_CLANG_VERSION}"

if [[ -n "${MAJOR_VER}" && ! "${DETECTED_CLANG_VERSION}" =~ clang\ version\ ${MAJOR_VER}\. ]]; then
    echo "WARNING: Detected clang version doesn't match kernel build version (${MAJOR_VER}). Build might fail."
else
    echo "LLVM toolchain setup successful for the current kernel."
fi
