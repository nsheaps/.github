#!/bin/bash
# Validate GitHub Actions workflow files

set -e

echo "Validating GitHub Actions workflows..."

# Check if actionlint is installed
if ! command -v actionlint &> /dev/null; then
    echo "Installing actionlint..."
    bash <(curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash)
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
