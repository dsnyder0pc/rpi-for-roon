#!/bin/bash
# Description: Ensures the correct LLVM/clang toolchain is installed and prioritized
#              based on the compiler version used to build the running kernel.

# --- Configuration ---
# Get kernel compiler info
KERNEL_VERSION_INFO=$(cat /proc/version)
echo "Kernel build info: ${KERNEL_VERSION_INFO}"

# Extract the major clang version used to build the kernel
MAJOR_VER=$(echo "${KERNEL_VERSION_INFO}" | grep -oP 'clang version \K[0-9]+')

# Determine required toolchain suffix (e.g., "20", "21", or empty for latest)
TOOLCHAIN_SUFFIX=""
if [[ -n "${MAJOR_VER}" ]]; then
  # Find the latest MAJOR version number available as a specific llvmXX package
  LATEST_VERSIONED_LLVM=$(pacman -Ss '^llvm[0-9]+$' | grep -oP '^extra/llvm\K[0-9]+' | sort -nr | head -n 1)

  if [[ -z "$LATEST_VERSIONED_LLVM" ]]; then
      LATEST_VERSIONED_LLVM=0 # Handle case where no versioned packages exist yet
  fi

  if [[ "$MAJOR_VER" -le "$LATEST_VERSIONED_LLVM" ]]; then
      TOOLCHAIN_SUFFIX="${MAJOR_VER}"
      echo "Kernel requires LLVM major version ${MAJOR_VER}. Using specific '${TOOLCHAIN_SUFFIX}' packages."
  else
      echo "Kernel requires LLVM major version ${MAJOR_VER}, likely the current default. Using default packages."
      TOOLCHAIN_SUFFIX=""
  fi
else
  echo "Could not detect specific clang version for kernel build (maybe GCC?). Assuming latest default LLVM toolchain needed."
  TOOLCHAIN_SUFFIX=""
fi

# --- Define Package Names and Paths ---
CLANG_PKG="clang${TOOLCHAIN_SUFFIX}"
LLVM_PKG="llvm${TOOLCHAIN_SUFFIX}"
LLVM_LIBS_PKG="llvm${TOOLCHAIN_SUFFIX}-libs"
COMPILER_RT_PKG="compiler-rt${TOOLCHAIN_SUFFIX}"
LLD_PKG="lld${TOOLCHAIN_SUFFIX}"

if [[ -n "${TOOLCHAIN_SUFFIX}" ]]; then LLVM_BIN_PATH="/usr/lib/llvm${TOOLCHAIN_SUFFIX}/bin"; else LLVM_BIN_PATH="/usr/bin"; fi

PACKAGES_TO_INSTALL="${CLANG_PKG} ${LLVM_PKG} ${LLVM_LIBS_PKG} ${COMPILER_RT_PKG} ${LLD_PKG}"
PACKAGES_TO_IGNORE="${CLANG_PKG} ${LLVM_PKG} ${LLD_PKG} ${LLVM_LIBS_PKG} ${COMPILER_RT_PKG}"

# --- Installation ---
echo "Ensuring required toolchain packages (${PACKAGES_TO_INSTALL}) are installed..."
# shellcheck disable=SC2086 # We need word splitting for pacman here
if ! sudo pacman -S --noconfirm --needed ${PACKAGES_TO_INSTALL}; then
  echo "Error installing required LLVM packages. Aborting."
  exit 1
fi
echo "Required packages are installed."

# --- Configure PATH ---
PROFILE_SCRIPT="/etc/profile.d/llvm_diretta.sh"
echo "Configuring system-wide PATH in ${PROFILE_SCRIPT} to prioritize ${LLVM_BIN_PATH}..."
sudo tee ${PROFILE_SCRIPT} > /dev/null <<EOF
# Added by Diretta setup script to prioritize LLVM toolchain for kernel modules
export PATH="${LLVM_BIN_PATH}:\$PATH"
EOF
sudo chmod +x ${PROFILE_SCRIPT}
export PATH="${LLVM_BIN_PATH}:$PATH"
echo "PATH configured. Log out and back in for changes to apply universally."

# --- Clean and Set IgnorePkg ---
PACMAN_CONF="/etc/pacman.conf"
echo "Cleaning old LLVM IgnorePkg entries and setting for required version (${PACKAGES_TO_IGNORE})..."

# Remove any existing IgnorePkg lines (commented or uncommented) to avoid duplicates
sudo sed -i '/^#*IgnorePkg\s*=/d' ${PACMAN_CONF}

# Add the new, correct IgnorePkg line directly after the [options] header
sudo sed -i "/^\[options\]/a IgnorePkg = ${PACKAGES_TO_IGNORE}" ${PACMAN_CONF}

echo "Set IgnorePkg to: ${PACKAGES_TO_IGNORE}"


# --- Verification ---
echo "Verifying installation..."
if ! command -v clang > /dev/null; then echo "ERROR: clang command not found in PATH (${PATH})."; exit 1; fi
DETECTED_CLANG_PATH=$(which clang)
DETECTED_CLANG_VERSION=$(clang --version | head -n 1)
echo "Current clang in PATH: ${DETECTED_CLANG_PATH}"
echo "Current clang version: ${DETECTED_CLANG_VERSION}"
if [[ "${DETECTED_CLANG_PATH}" != "${LLVM_BIN_PATH}/clang" ]]; then
    echo "WARNING: The clang found in PATH is not the expected one (${LLVM_BIN_PATH}/clang). Log out and log back in."
elif [[ -n "${MAJOR_VER}" && ! "${DETECTED_CLANG_VERSION}" =~ clang\ version\ ${MAJOR_VER}\. ]]; then
    echo "WARNING: Detected clang version (${DETECTED_CLANG_VERSION}) doesn't match kernel build version (${MAJOR_VER}). Build might fail."
else
    echo "LLVM toolchain setup appears successful for the current kernel."
fi

echo "Compiler check complete. Proceeding with Diretta installation..."

# --- Add subsequent Diretta installation/build commands here ---
