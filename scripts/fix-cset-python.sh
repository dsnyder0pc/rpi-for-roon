#!/bin/bash
# Identify the active system Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
TARGET_DIR="/usr/lib/python${PYTHON_VERSION}/site-packages"
FOUND_MODULE=false

echo "Current System Python: $PYTHON_VERSION"

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
      echo "🚀 Migrating module to $TARGET_DIR..."
      sudo rsync -av "$OLD_DIR/cpuset"* "$TARGET_DIR/"
      FOUND_MODULE=true
      break
    fi
  done
fi

if [ "$FOUND_MODULE" = true ]; then
  # Ensure the cset script uses the correct system python
  echo "🛠️  Updating /usr/bin/cset shebang..."
  sudo sed -i "1s|.*|#!/usr/bin/python${PYTHON_VERSION}|" /usr/bin/cset
  echo "✅ cset is ready."
  cset --version
else
  echo "❌ Error: cpuset module not found on this system. Please ensure 'cpuset-git' is installed."
  exit 1
fi
