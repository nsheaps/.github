# nsheaps/.github - Organization Configuration Repository
#
# Prerequisites:
#   - mise: https://mise.run
#   - just: https://github.com/casey/just
#
# Usage:
#   just          # Show available commands
#   just setup    # Install dependencies
#   just check    # Run all checks (CI equivalent)

set unstable

root_dir := justfile_directory()

# Default: show help
default:
    @just --list

# Install development dependencies
setup:
    @echo "Installing tools via mise..."
    mise install -y
    @echo "Enabling corepack..."
    corepack enable
    corepack install
    @echo "Installing yarn dependencies..."
    yarn install
    @echo "Setup complete!"

# Run linting (eslint)
lint:
    yarn check

# Auto-fix lint issues
lint-fix:
    yarn fix

# Run TypeScript type checking
typecheck:
    yarn check

# Build all projects
build:
    yarn build

# Run all tests
test:
    yarn test

# Run all checks (equivalent to CI)
check: lint build test
    @echo "All checks passed!"

# Validate workflow syntax with actionlint (if installed)
validate-workflows:
    #!/usr/bin/env bash
    if command -v actionlint &> /dev/null; then
        actionlint .github/workflows/*.yaml
    else
        echo "actionlint not installed, skipping workflow validation"
        echo "Install with: brew install actionlint"
    fi

# Clean build artifacts
clean:
    rm -rf .github/actions/*/dist
    rm -rf .nx
    rm -rf node_modules
