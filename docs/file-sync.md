# Ansible File Sync

Synchronize files across organization repositories using Ansible. This allows you to maintain consistency for configuration files, workflows, and other assets across multiple repositories.

## Overview

The file sync system uses Ansible to:
- **Create** files that don't exist in target repositories
- **Update** files that differ from the source
- **Delete** files that should be removed (`state: absent`)

All operations are idempotent and use the GitHub Contents API.

## Configuration

### Sync Tasks

Define sync tasks in `ansible/config/sync-tasks.yml`:

```yaml
---
defaults:
  state: present
  force_sync: false
  commit_message_prefix: "[sync]"

sync_tasks:
  # Sync a workflow to multiple repos
  - name: "Sync shared CI workflow"
    source: "workflows/shared-ci.yml"
    dest: ".github/workflows/ci.yml"
    state: present
    repos:
      - nsheaps/repo-a
      - nsheaps/repo-b
      - nsheaps/repo-c

  # Different file to different repos
  - name: "Sync renovate config"
    source: "config/renovate.json"
    dest: "renovate.json"
    state: present
    repos:
      - nsheaps/repo-a
      - nsheaps/repo-d  # Different repo set

  # Remove a deprecated file
  - name: "Remove old security workflow"
    dest: ".github/workflows/deprecated-security.yml"
    state: absent  # No source needed for deletion
    repos:
      - nsheaps/repo-b
```

### Task Properties

| Property | Required | Description |
|----------|----------|-------------|
| `name` | Yes | Human-readable task name |
| `source` | Yes* | Path to source file (relative to `ansible/templates/`) |
| `dest` | Yes | Destination path in target repositories |
| `repos` | Yes | List of target repositories (`owner/repo` format) |
| `state` | No | `present` (default) or `absent` |
| `commit_message` | No | Custom commit message |

\* `source` is required when `state: present`, not needed for `state: absent`

### Source Templates

Place source files in `ansible/templates/`:

```
ansible/templates/
├── workflows/
│   └── shared-ci.yml
├── config/
│   └── renovate.json
└── CODEOWNERS
```

## Usage

### Local Development

Set your GitHub token:

```bash
export GITHUB_TOKEN=ghp_xxx  # Personal access token with repo scope
```

Preview changes (dry run):

```bash
mise run sync-files -- --dry-run
```

Apply changes:

```bash
mise run sync-files
```

Force sync (ignore unchanged files):

```bash
mise run sync-files -- --force
```

### CI/CD

The sync can be triggered automatically when templates change, or manually via workflow_dispatch.

For CI, configure GitHub App authentication:

1. Create a GitHub App with `contents: write` permission
2. Install it on target repositories
3. Add secrets to the `.github` repository:
   - `SYNC_APP_ID`
   - `SYNC_INSTALLATION_ID`
   - `SYNC_PRIVATE_KEY`
4. Set repository variable `SYNC_APP_CONFIGURED=true`

## Authentication

### Personal Access Token (Local)

For local development, use a personal access token:

1. Create token at https://github.com/settings/tokens
2. Required scopes: `repo`, `read:org`
3. Export as `GITHUB_TOKEN`

### GitHub App (CI)

For CI, use a GitHub App for better security:

1. Create a GitHub App in your organization
2. Set permissions: `Contents: Read and write`
3. Install on target repositories
4. Store credentials in repository secrets

## Architecture

### Roles

**`github_auth`** - Handles authentication
- Supports both personal tokens and GitHub App
- Auto-detects method based on available credentials

**`file_sync`** - Performs file operations
- Routes to `sync_file.yml` or `delete_file.yml` based on state
- Checks current file state before making changes
- Commits directly to default branch

### Playbook Flow

1. Authenticate with GitHub
2. Load sync tasks from config
3. For each task:
   - For each repository:
     - Check current file state
     - Create/update/delete as needed
     - Report result

## Troubleshooting

### Common Issues

**"GITHUB_TOKEN environment variable not set"**
- Set `export GITHUB_TOKEN=ghp_xxx` for local development
- For CI, ensure secrets are configured

**"404 Not Found" for repository**
- Verify the repository exists
- Check token has access to the repository
- Ensure repository name is correct (`owner/repo` format)

**"422 Unprocessable Entity"**
- Usually means the file path is invalid
- Check for special characters in path

### Debug Mode

Run with verbose output:

```bash
mise run sync-files -- -v
```

### Validation

Validate configuration before running:

```bash
mise run validate-sync-config
mise run ansible-lint
```
