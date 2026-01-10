# GitHub Stars List Manager

Manage your GitHub star lists via a YAML config file.

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

## Usage

The workflow runs automatically when you push changes to `.github/stars.yaml`, or trigger it manually from the Actions tab.

Lists are created automatically if they don't exist. Repos are added/removed to match your config.
