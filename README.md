# .github

Organization-wide GitHub configuration and automation for nsheaps.

## Features

### Available Now

- **[Stars List Manager](docs/stars-manager.md)** - Manage GitHub star lists via YAML with bidirectional sync
- **[Ansible File Sync](docs/file-sync.md)** - Sync files across organization repositories
- **Unified CI** - Consistent validation pipeline using mise tasks for local/CI parity

### Planned

- **Reusable Workflows** - Shared CI/CD workflows for organization repositories
- **Organization Templates** - Issue and PR templates
- **Workflow Observability** - Metrics collection for workflow runs

## Development

### Prerequisites

- [mise](https://mise.run) - Tool version management and task runner

### Quick Start

```bash
# Install tools and dependencies
mise install
mise run setup

# Run all checks (same as CI)
mise run check
```

### Available Tasks

```bash
mise run              # Show all tasks
mise run setup        # Full setup (tools + dependencies)
mise run check        # Run all checks (lint, build, test)
mise run build        # Build all projects
mise run test         # Run tests
mise run lint         # Run linting
mise run lint-fix     # Auto-fix lint issues
mise run clean        # Remove build artifacts
mise run validate-workflows  # Validate workflow YAML (requires actionlint)

# Ansible File Sync
mise run ansible-setup       # Install Ansible dependencies
mise run ansible-lint        # Lint Ansible files
mise run validate-sync-config  # Validate sync configuration
mise run sync-files          # Sync files to repositories
mise run sync-files -- --dry-run  # Preview changes
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
│       ├── sync-files.yaml   # Ansible file sync
│       └── sync-stars.yaml   # Stars sync automation
├── ansible/               # Ansible file synchronization
│   ├── config/            # Sync task definitions
│   ├── inventory/         # Ansible inventory
│   ├── playbooks/         # Ansible playbooks
│   ├── roles/             # Ansible roles
│   └── templates/         # Source files to sync
├── docs/                  # Documentation
├── mise.toml              # Tool versions and tasks
├── package.json           # Node.js configuration
├── nx.json                # Nx build orchestration
└── tsconfig.base.json     # TypeScript configuration
```

## CI/CD

The CI workflow runs the same commands locally available via mise tasks:

1. **Lint** - ESLint with TypeScript support
2. **Build** - Compile TypeScript actions
3. **Test** - Run test suites
4. **Validate Ansible** - Lint and validate Ansible configuration

### Local Validation

Before pushing, run the full CI suite locally:

```bash
mise run check
mise run validate-sync-config
mise run ansible-lint
```

This ensures parity between local development and CI.

## Ansible File Sync

Sync files across organization repositories using Ansible. Define sync tasks in `ansible/config/sync-tasks.yml`:

```yaml
sync_tasks:
  - name: "Sync CI workflow"
    source: "workflows/shared-ci.yml"
    dest: ".github/workflows/ci.yml"
    state: present
    repos:
      - nsheaps/repo-a
      - nsheaps/repo-b

  - name: "Remove deprecated file"
    dest: ".github/workflows/old.yml"
    state: absent
    repos:
      - nsheaps/repo-c
```

For local development, set `GITHUB_TOKEN`:
```bash
export GITHUB_TOKEN=ghp_xxx
mise run sync-files --dry-run
```

See [File Sync documentation](docs/file-sync.md) for details.

## Claude Code Integration

This repository is configured for use with [Claude Code](https://claude.ai/claude-code):

- Session hooks automatically set up the development environment
- Permissions pre-configured for common operations
- Plugins from [nsheaps/ai](https://github.com/nsheaps/ai) marketplace available

## License

Proprietary - See [LICENSE](LICENSE)
