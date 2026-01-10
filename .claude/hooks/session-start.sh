#!/bin/bash
set -euo pipefail

# Only run in remote environment (Claude Code on the web)
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

echo "Setting up development environment..."

# Install mise if not present
if ! command -v mise &> /dev/null; then
  echo "Installing mise..."
  curl -fsSL https://mise.run | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# Add mise to environment file for session
echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"

cd "$CLAUDE_PROJECT_DIR"

# Trust and install mise tools
echo "Installing mise tools (node, gh)..."
mise trust --yes
mise install --yes

# Activate mise for this session
eval "$(mise activate bash)"

# Enable corepack for yarn
echo "Corepack setup..."
corepack enable && corepack install

# Install dependencies
echo "Installing yarn dependencies..."
yarn install

echo "Environment setup complete!"
