#!/bin/bash
# Validate GitHub Actions workflow files

set -e

echo "Validating GitHub Actions workflows..."

# actionlint version to download
ACTIONLINT_VERSION="1.6.27"

# Check if actionlint is installed
if ! command -v actionlint &> /dev/null; then
    echo "Installing actionlint version ${ACTIONLINT_VERSION}..."

    # Determine OS and architecture
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    if [ "$ARCH" = "x86_64" ]; then
        ARCH="amd64"
    elif [ "$ARCH" = "aarch64" ]; then
        ARCH="arm64"
    fi

    # Download URL
    DOWNLOAD_URL="https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_${OS}_${ARCH}.tar.gz"

    # Download and extract
    echo "Downloading from ${DOWNLOAD_URL}"
    curl -sL "${DOWNLOAD_URL}" | tar xz -C "${PWD}"
    chmod +x "${PWD}/actionlint"
    export PATH="${PWD}:${PATH}"
fi

# Validate workflows in .github/workflows
echo ""
echo "Validating workflows in .github/workflows..."
for workflow in .github/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo "  - $(basename "$workflow")"
        actionlint "$workflow"
    fi
done

# Validate template workflows
echo ""
echo "Validating template workflows in ansible/templates/workflows..."
for workflow in ansible/templates/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo "  - $(basename "$workflow")"
        actionlint "$workflow"
    fi
done

echo ""
echo "✓ All workflows validated successfully!"
