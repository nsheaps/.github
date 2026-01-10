# .github

Personal GitHub configuration repository with reusable actions and automation.

## Features

- **[Stars List Manager](docs/stars-manager.md)** - Manage GitHub star lists via YAML config with bidirectional sync

## Development

This repo uses a monorepo structure with:

- **mise** - Tool version management (node, gh)
- **yarn** - Package management with workspaces
- **nx** - Task orchestration and caching

### Setup

```bash
# Install mise (if not already installed)
curl https://mise.run | sh

# Install tools and dependencies
mise install
yarn install
```

### Commands

```bash
yarn build   # Build all projects
yarn test    # Run all tests
yarn check   # Run linting and type checking
yarn fix     # Auto-fix linting issues
```

### Project Structure

```
.github/
├── actions/
│   ├── sync-stars-push/    # Push YAML to GitHub lists
│   └── sync-stars-pull/    # Pull GitHub lists to YAML
├── workflows/
│   └── sync-stars.yaml     # Stars sync workflow
├── stars.yaml              # Stars configuration
docs/
├── stars-manager.md        # Stars manager documentation
```
