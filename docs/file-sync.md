# Ansible File Sync

Synchronize files across organization repositories using Ansible. Maintains consistency for configuration files, workflows, and other assets.

## Overview

The file sync system:
- **Syncs** files from `.github` repo to target repositories
- **Central repo trumps** - your `.github` config is always authoritative
- **Preserves changes** - if a target repo has modifications, opens a PR in `.github` to preserve them

## Configuration

### File Mapping

Define files to sync in `ansible/config/sync-files.yml`:

```yaml
defaults:
  preserve_target_changes: true
  commit_message_prefix: "[sync]"

files:
  # Key = source file path (relative to ansible/templates/)
  # Value = { dest (optional), repos: [list] }

  # Simple: dest path matches source path
  ".github/workflows/ci.yml":
    repos:
      - nsheaps/repo-a
      - nsheaps/repo-b

  # Extended: different dest path
  "configs/renovate-org.json":
    dest: "renovate.json"
    repos:
      - nsheaps/repo-c
```

### Source Files

Place source files in `ansible/templates/`:

```
ansible/templates/
├── .github/
│   └── workflows/
│       └── ci.yml
├── configs/
│   └── renovate-org.json
└── CODEOWNERS
```

## Usage

### Local Development

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_xxx

# Preview changes (dry run)
mise run sync-files -- --dry-run

# Apply changes
mise run sync-files

# Force sync (ignore unchanged)
mise run sync-files -- --force
```

### CI/CD

The sync runs automatically when:
- Files in `ansible/config/sync-files.yml` change
- Files in `ansible/templates/` change

Manual trigger via workflow_dispatch is also available.

## Conflict Handling

When syncing, if a target repository has modifications:

1. **PR is created** in `.github` repo to preserve the target's changes
2. **Target is updated** with central config (central always wins)
3. **Review the PR** to decide if changes should be merged into central config

This ensures:
- Central config is authoritative
- No changes are lost
- Modifications can be reviewed and potentially adopted

## Authentication

### Personal Access Token (Local)

1. Create token at https://github.com/settings/tokens
2. Required scopes: `repo`, `read:org`
3. Export as `GITHUB_TOKEN`

### GitHub App (CI)

1. Create a GitHub App with `contents: write` permission
2. Install on target repositories AND the `.github` repo
3. Add secrets:
   - `SYNC_APP_ID`
   - `SYNC_INSTALLATION_ID`
   - `SYNC_PRIVATE_KEY`
4. Set `SYNC_APP_CONFIGURED=true` repository variable

## Validation

```bash
# Validate config syntax
mise run validate-sync-config

# Lint Ansible code
mise run ansible-lint
```

## Troubleshooting

### Common Issues

**"GITHUB_TOKEN not set"**
- Set `export GITHUB_TOKEN=ghp_xxx` for local dev
- For CI, ensure secrets are configured

**"404 Not Found"**
- Verify repository exists and token has access
- Check `owner/repo` format is correct

**"422 Unprocessable Entity"**
- Usually invalid file path
- Check for special characters

### Debug Mode

```bash
mise run sync-files -- -v
```
