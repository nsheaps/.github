# GitHub Stars List Manager

Manage your GitHub star lists via a YAML config file with bidirectional sync.

## Setup

1. Create a Personal Access Token with `repo` and `user` scopes
2. Add it as a repository secret named `STARS_TOKEN`
3. Edit `.github/stars.yaml` to define your starred repos and lists

## Configuration

Edit `.github/stars.yaml`:

```yaml
stars:
  # Just starred (no list assignment)
  - "owner/repo"

  # Assign to lists
  - "anthropics/claude-code":
      tags: [ai, tools]

  - "awesome-selfhosted/awesome-selfhosted":
      tags: [homelab]
```

## Sync Directions

The workflow supports two directions, selectable via workflow_dispatch:

### Push: Repository → GitHub (YAML to Lists)

- **Trigger**: Automatically on push to `.github/stars.yaml`, or manually select "repo-to-github"
- **Action**: Updates your GitHub star lists to match the YAML config
- **Creates lists** if they don't exist
- **Adds/removes repos** from lists to match your config

### Pull: GitHub → Repository (Lists to YAML)

- **Trigger**: Manually select "github-to-repo"
- **Action**: Fetches your current stars and list assignments from GitHub API
- **Overwrites** `.github/stars.yaml` with current state from GitHub
- **Commits and pushes** the updated YAML file

## Usage

### Automatic Sync (Push)

Just edit `.github/stars.yaml` and push - the workflow will sync your changes to GitHub.

### Manual Sync

1. Go to Actions tab
2. Select "Sync Stars Lists"
3. Click "Run workflow"
4. Choose direction:
   - `repo-to-github` - Push YAML config to GitHub lists
   - `github-to-repo` - Pull current state from GitHub to YAML
