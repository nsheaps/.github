# .github Repository

Central repository for managing GitHub workflows and configurations across the nsheaps organization using Ansible automation.

## Overview

This repository provides a centralized management system for synchronizing GitHub Actions workflows and repository configurations across multiple repositories in the organization. It uses Ansible for automation and GitHub App authentication for secure, scalable access.

## Features

- 🔄 **Automated Workflow Synchronization**: Deploy and update workflows across multiple repositories
- 🔐 **GitHub App Authentication**: Secure authentication using GitHub Apps instead of personal access tokens
- 📊 **Metrics Collection**: Example workflow_run triggers for collecting traces and metrics (Datadog, Prometheus, NewRelic)
- ✅ **Local Testing**: Validate workflows locally using `act` before deployment
- 🧪 **Comprehensive Testing**: Full test suite for Ansible playbooks and workflows
- 🔧 **Dependency Management**: Automated dependency updates via Renovate

## Quick Start

### Prerequisites

- Python 3.8+
- Ansible 2.10+
- [act](https://github.com/nektos/act) (for local workflow testing)
- GitHub App with appropriate permissions

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/nsheaps/.github.git
   cd .github
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ansible-galaxy install -r ansible/requirements.yml
   ```

3. Configure your GitHub App credentials:
   ```bash
   cp ansible/inventory/example.vault.yml ansible/inventory/vault.yml
   ansible-vault edit ansible/inventory/vault.yml
   ```

## GitHub App Setup

This repository requires a GitHub App for authentication. Follow the official GitHub documentation to create and configure your app:

### Creating a GitHub App

1. **[Creating a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)** - Official guide for registering a new GitHub App
2. **[Authenticating with GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app)** - Understanding GitHub App authentication
3. **[Setting Permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)** - Configure required permissions

### Required Permissions

Your GitHub App needs the following permissions:

- **Repository permissions:**
  - Actions: Read & Write
  - Contents: Read & Write
  - Workflows: Read & Write
  - Metadata: Read

- **Organization permissions:**
  - Administration: Read

### Installation

After creating your GitHub App:

1. Generate a private key for your app
2. Install the app on your organization
3. Store the App ID, Installation ID, and private key securely using Ansible Vault

For detailed instructions, see [docs/github-app-setup.md](docs/github-app-setup.md)

## Usage

### Syncing Workflows

To sync workflows to target repositories:

```bash
cd ansible
ansible-playbook playbooks/sync-workflows.yml -i inventory/production.yml --ask-vault-pass
```

### Syncing to Specific Repositories

```bash
ansible-playbook playbooks/sync-workflows.yml -i inventory/production.yml \
  --ask-vault-pass \
  --extra-vars "target_repos=repo1,repo2,repo3"
```

### Testing Locally with act

Test workflows locally before deploying:

```bash
# Test a specific workflow
act -W .github/workflows/ci.yml

# Test with secrets
act -W .github/workflows/ci.yml --secret-file .secrets

# List available jobs
act -l
```

See [docs/local-testing.md](docs/local-testing.md) for more details.

## Workflows

### CI Workflows

- **ci.yml**: Main CI pipeline for testing this repository
- **validate-workflows.yml**: Validates all workflow files syntax
- **ansible-test.yml**: Tests Ansible playbooks

### Shared Workflows

Workflows in `ansible/templates/workflows/` are synced to target repositories:

- **shared-ci.yml**: Standard CI workflow for organization repositories
- **dependency-updates.yml**: Automated dependency update workflow
- **security-scan.yml**: Security scanning workflow

### Metrics Collection Example

The `workflow-run-metrics.yml` demonstrates how to collect workflow traces and metrics:

- Triggered on `workflow_run` completion
- Collects run metadata, timing, and status
- Sends to observability platforms (Datadog, Prometheus, NewRelic)

See [docs/metrics-collection.md](docs/metrics-collection.md) for implementation details.

## Project Structure

```
.github/
├── ansible/
│   ├── playbooks/          # Ansible playbooks
│   │   ├── sync-workflows.yml
│   │   └── setup-repos.yml
│   ├── roles/              # Ansible roles
│   │   ├── github-app-auth/
│   │   └── workflow-sync/
│   ├── inventory/          # Inventory files
│   │   ├── production.yml
│   │   └── vault.yml
│   ├── templates/          # Workflow templates
│   │   └── workflows/
│   └── requirements.yml    # Ansible Galaxy requirements
├── .github/
│   └── workflows/          # CI workflows for this repo
│       ├── ci.yml
│       ├── validate-workflows.yml
│       ├── ansible-test.yml
│       └── workflow-run-metrics.yml
├── docs/                   # Documentation
│   ├── github-app-setup.md
│   ├── local-testing.md
│   ├── metrics-collection.md
│   └── troubleshooting.md
├── tests/                  # Test suite
│   ├── test_playbooks.py
│   └── test_workflows.sh
├── scripts/                # Utility scripts
│   └── validate-workflows.sh
├── .actrc                  # act configuration
├── requirements.txt        # Python dependencies
├── renovate.json          # Renovate configuration
└── README.md
```

## Testing

### Run All Tests

```bash
# Run Python tests
pytest tests/

# Run workflow validation
./scripts/validate-workflows.sh

# Run Ansible playbook syntax checks
ansible-playbook ansible/playbooks/sync-workflows.yml --syntax-check
```

### Continuous Integration

All commits are automatically tested via GitHub Actions. See `.github/workflows/ci.yml` for details.

## Dependency Management

This repository uses [Renovate](https://github.com/renovatebot/renovate) for automated dependency updates, configured to extend [nsheaps/renovate-config](https://github.com/nsheaps/renovate-config).

Renovate will automatically:
- Check for dependency updates
- Create pull requests for updates
- Run tests on update PRs

Configuration: `renovate.json`

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally using `act`
4. Run the test suite
5. Submit a pull request

## Security

- GitHub App credentials are stored using Ansible Vault
- Never commit secrets to the repository
- Use environment variables or vault for sensitive data
- Regularly rotate GitHub App private keys

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues and solutions.

## License

This project is proprietary and confidential. See [LICENSE](LICENSE) for details.

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Ansible Documentation](https://docs.ansible.com/)
- [act - Local GitHub Actions Testing](https://github.com/nektos/act)
- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Renovate Documentation](https://docs.renovatebot.com/)