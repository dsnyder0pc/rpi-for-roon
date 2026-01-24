#!/bin/bash

# Explicitly use the system Python via absolute path to bypass pyenv/shims
SYSTEM_PYTHON="/usr/bin/python3"

# Identify the active system Python version and actual executable path
PYTHON_VERSION=$($SYSTEM_PYTHON -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_BIN=$($SYSTEM_PYTHON -c 'import sys; print(sys.executable)')
TARGET_DIR="/usr/lib/python${PYTHON_VERSION}/site-packages"
FOUND_MODULE=false

echo "Current System Python: $PYTHON_VERSION"
echo "Python Executable: $PYTHON_BIN"

# Check if the module is already in the correct place
if [ -d "${TARGET_DIR}/cpuset" ]; then
  echo "✅ cpuset module is already in the correct path."
  FOUND_MODULE=true
else
  # Look for the module in older Python 3.x directories
  for old_path in /usr/lib/python3.*/site-packages/cpuset; do
    if [ -d "$old_path" ]; then
      OLD_DIR=$(dirname "$old_path")
      echo "📦 Found stranded cpuset module in $OLD_DIR"

      # Ensure the target directory exists before rsync
      if [ ! -d "$TARGET_DIR" ]; then
        echo "📂 Creating target directory: $TARGET_DIR"
        sudo mkdir -p "$TARGET_DIR"
      fi

      echo "🚀 Migrating module to $TARGET_DIR..."
      sudo rsync -av "$OLD_DIR/cpuset"* "$TARGET_DIR/"
      FOUND_MODULE=true
      break
    fi
  done
fi

if [ "$FOUND_MODULE" = true ]; then
  # Use the identified executable path for the shebang
  echo "🛠️  Updating /usr/bin/cset shebang..."
  sudo sed -i "1s|.*|#!${PYTHON_BIN}|" /usr/bin/cset
  echo "✅ cset is ready."
  cset --version
else
  echo "❌ Error: cpuset module not found on this system. Please ensure 'cpuset-git' is installed."
  exit 1
fi
