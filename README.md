# .github

Organization-wide GitHub configuration and automation for nsheaps.

## Features

### Available Now

- **[Stars List Manager](docs/stars-manager.md)** - Manage GitHub star lists via YAML with bidirectional sync
- **Unified CI** - Consistent validation pipeline using justfile for local/CI parity

### Planned

- **Reusable Workflows** - Shared CI/CD workflows for organization repositories
- **Organization Templates** - Issue and PR templates
- **Workflow Observability** - Metrics collection for workflow runs

## Development

### Prerequisites

- [mise](https://mise.run) - Tool version management
- [just](https://github.com/casey/just) - Command runner (installed via mise)

### Quick Start

```bash
# Install tools (mise installs just, node, gh)
mise install

# Install dependencies
just setup

# Run all checks (same as CI)
just check
```

### Available Commands

```bash
just              # Show all commands
just setup        # Full setup (tools + dependencies)
just check        # Run all checks (lint, build, test)
just build        # Build all projects
just test         # Run tests
just lint         # Run linting
just lint-fix     # Auto-fix lint issues
just clean        # Remove build artifacts
just validate-workflows  # Validate workflow YAML (requires actionlint)
```

## Project Structure

```
.
├── .claude/               # Claude Code configuration
│   ├── hooks/             # Session hooks
│   └── settings.json      # Permissions and plugins
├── .github/
│   ├── actions/           # Reusable composite actions
│   │   ├── setup/         # Shared environment setup
│   │   ├── sync-stars-pull/  # Pull stars from GitHub
│   │   └── sync-stars-push/  # Push stars to GitHub
│   ├── stars.yaml         # Stars list configuration
│   └── workflows/         # CI/CD workflows
│       ├── ci.yaml        # Main validation pipeline
│       └── sync-stars.yaml  # Stars sync automation
├── docs/                  # Documentation
├── justfile               # Local development commands
├── .mise.toml             # Tool versions (node, just, gh)
├── package.json           # Node.js configuration
├── nx.json                # Nx build orchestration
└── tsconfig.base.json     # TypeScript configuration
```

## CI/CD

The CI workflow runs the same commands locally available via justfile:

1. **Lint** - ESLint with TypeScript support
2. **Build** - Compile TypeScript actions
3. **Test** - Run test suites

### Local Validation

Before pushing, run the full CI suite locally:

```bash
just check
```

This ensures parity between local development and CI.

## Claude Code Integration

This repository is configured for use with [Claude Code](https://claude.ai/claude-code):

- Session hooks automatically set up the development environment
- Permissions pre-configured for common operations
- Plugins from [nsheaps/ai](https://github.com/nsheaps/ai) marketplace available

## License

Proprietary - See [LICENSE](LICENSE)
