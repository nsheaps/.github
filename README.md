# GitHub Stars List Manager

A CLI tool to manage your GitHub starred repositories and organize them into lists.

## Features

- **View Stars**: List all your starred repositories with filtering options
- **Manage Lists**: Create, update, and delete star lists
- **Organize Repos**: Add/remove repositories from lists
- **Find Uncategorized**: Identify starred repos not in any list
- **Bulk Operations**: Categorize multiple repos at once based on language or topics
- **Export**: Export your stars and list assignments to JSON or CSV
- **Smart Suggestions**: Get list suggestions based on repo language, topics, and description

## Installation

```bash
# Clone the repository
git clone https://github.com/nsheaps/.github.git
cd .github

# Install with pip
pip install -e .

# Or with uv
uv pip install -e .
```

## Authentication

Set your GitHub token as an environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
# or
export GH_TOKEN="ghp_your_token_here"
```

Required token scopes:
- `repo` (for accessing starred repos)
- `user` (for managing star lists)

## Usage

### Stars Commands

```bash
# List all starred repositories
stars stars list

# Filter by language
stars stars list --language Python

# Limit results
stars stars list --limit 20

# Include archived repos
stars stars list --archived

# Find uncategorized repos (not in any list)
stars stars uncategorized

# Star a repository
stars stars add owner/repo

# Unstar a repository
stars stars remove owner/repo

# Get summary statistics
stars stars summary
```

### Lists Commands

```bash
# List all star lists
stars lists list

# Show repos in a specific list
stars lists show <list_id>

# Create a new list
stars lists create "my-list"
stars lists create "private-list" --description "My private collection" --private

# Update a list
stars lists update <list_id> --name "new-name" --description "new description"
stars lists update <list_id> --private  # Make private
stars lists update <list_id> --public   # Make public

# Delete a list
stars lists delete <list_id>
stars lists delete <list_id> --force  # Skip confirmation

# Add a repo to a list
stars lists add <list_id> owner/repo

# Remove a repo from a list
stars lists remove <list_id> owner/repo
```

### Bulk Operations

```bash
# Bulk categorize repos by language
stars bulk categorize <list_id> --language Python
stars bulk categorize <list_id> --language Python --dry-run  # Preview changes

# Bulk categorize repos by topic
stars bulk categorize <list_id> --topic machine-learning

# Export all stars to JSON
stars bulk export --output stars.json

# Export to CSV
stars bulk export --format csv --output stars.csv
```

## Example Workflow

For a user with 149 starred repos and lists "ai" (11 repos) and "homelab" (1 repo):

```bash
# Check current status
stars stars summary

# Find uncategorized repos
stars stars uncategorized

# Bulk add Python repos to a "python" list
stars lists create "python"
stars bulk categorize <python_list_id> --language Python --dry-run
stars bulk categorize <python_list_id> --language Python

# Add ML repos to the existing "ai" list
stars bulk categorize <ai_list_id> --topic machine-learning

# Export for backup
stars bulk export --output my-stars-backup.json
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Type check
mypy stars_manager
```

## Project Structure

```
.github/
├── stars_manager/
│   ├── __init__.py      # Package init
│   ├── cli.py           # CLI commands (Click)
│   ├── github_api.py    # GitHub API client
│   ├── models.py        # Pydantic models
│   └── utils.py         # Utility functions
├── tests/
│   ├── test_models.py   # Model tests
│   └── test_utils.py    # Utility tests
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## API Reference

### GitHubClient

```python
from stars_manager.github_api import GitHubClient

with GitHubClient() as client:
    # Get all starred repos
    repos = client.get_starred_repos()

    # Get all lists
    lists = client.get_star_lists()

    # Create a list
    new_list = client.create_star_list("my-list", description="My repos")

    # Add repo to list
    client.add_repo_to_list(list_id, "owner", "repo")

    # Get uncategorized repos
    uncategorized = client.get_uncategorized_repos()
```

### Utility Functions

```python
from stars_manager.utils import suggest_lists_for_repo, parse_repo_identifier

# Get list suggestions for a repo
suggestions = suggest_lists_for_repo(repo)

# Parse various repo formats
owner, name = parse_repo_identifier("https://github.com/owner/repo")
owner, name = parse_repo_identifier("owner/repo")
```

## License

MIT
