# Local Testing with act

This guide explains how to use [act](https://github.com/nektos/act) to test GitHub Actions workflows locally before pushing to GitHub.

## What is act?

`act` is a tool that allows you to run GitHub Actions workflows locally using Docker. This enables you to:

- Test workflows without pushing commits
- Debug workflow issues quickly
- Validate workflow syntax and behavior
- Save GitHub Actions minutes

## Installation

### macOS

```bash
brew install act
```

### Linux

```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Windows

```bash
choco install act-cli
```

Or download from [GitHub Releases](https://github.com/nektos/act/releases).

## Configuration

This repository includes a `.actrc` file with default configuration:

```ini
# Use medium-sized runner image
-P ubuntu-latest=catthehacker/ubuntu:act-latest

# Bind the repository to /workspace
--bind

# Use built-in secrets file if exists
--secret-file .secrets

# Verbose output for debugging
--verbose
```

## Setting Up Secrets

Create a `.secrets` file in the repository root for local testing:

```bash
# .secrets file format
GITHUB_TOKEN=ghp_your_token_here
DATADOG_API_KEY=your_datadog_key
DATADOG_SITE=datadoghq.com
PROMETHEUS_PUSHGATEWAY_URL=http://localhost:9091
NEW_RELIC_API_KEY=your_newrelic_key
NEW_RELIC_ACCOUNT_ID=your_account_id
```

**Important**: Add `.secrets` to `.gitignore` to prevent committing secrets!

```bash
echo ".secrets" >> .gitignore
```

## Basic Usage

### List Available Workflows

```bash
act -l
```

This shows all jobs in all workflows.

### Run a Specific Workflow

```bash
# Run the CI workflow
act -W .github/workflows/ci.yml

# Run a specific job
act -W .github/workflows/ci.yml -j lint

# Run a specific event
act push
act pull_request
```

### Dry Run

See what would run without actually running it:

```bash
act -n
```

### Verbose Output

Get detailed information about what act is doing:

```bash
act -v
```

## Testing Different Events

### Push Event

```bash
act push
```

### Pull Request Event

```bash
act pull_request
```

### Workflow Dispatch

```bash
act workflow_dispatch
```

### Custom Event Payload

```bash
# Create event payload file
cat > event.json <<EOF
{
  "repository": {
    "name": "test-repo",
    "owner": {
      "login": "nsheaps"
    }
  }
}
EOF

# Run with custom payload
act -e event.json
```

## Testing Specific Workflows

### Test CI Workflow

```bash
act -W .github/workflows/ci.yml
```

### Test Workflow Validation

```bash
act -W .github/workflows/validate-workflows.yml
```

### Test Ansible Playbooks

```bash
act -W .github/workflows/ansible-test.yml
```

### Test Metrics Collection

Note: The workflow_run event is complex to test locally. Instead, test the scripts directly:

```bash
# Extract the script logic and test it
docker run --rm -v $PWD:/workspace -w /workspace ubuntu:latest bash -c '
  # Simulate workflow_run environment variables
  export GITHUB_EVENT_WORKFLOW_RUN_NAME="CI"
  export GITHUB_EVENT_WORKFLOW_RUN_CONCLUSION="success"
  
  # Run your metric collection logic
  echo "Testing metrics collection..."
'
```

## Advanced Usage

### Using Different Docker Images

```bash
# Use a specific runner image
act -P ubuntu-latest=nektos/act-environments-ubuntu:18.04
```

### Running with Environment Variables

```bash
act -W .github/workflows/ci.yml --env MY_VAR=value
```

### Mounting Volumes

```bash
act --bind
```

This is already configured in `.actrc`.

### Limiting Jobs

```bash
# Only run jobs matching a pattern
act -W .github/workflows/ci.yml -j 'test-*'
```

## Debugging Workflows

### Interactive Debugging

If a workflow fails, act stops and you can inspect the state:

```bash
# Run with verbose output
act -v

# Check the Docker containers
docker ps -a

# Inspect a container
docker logs <container_id>
```

### Using act with VS Code

Install the [GitHub Actions extension](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-github-actions) which includes act integration.

## Common Issues

### Docker Not Running

**Error**: Cannot connect to the Docker daemon

**Solution**: Ensure Docker is running:

```bash
# macOS/Linux
docker info

# Windows
docker version
```

### Insufficient Permissions

**Error**: Permission denied

**Solution**: Add your user to the docker group (Linux):

```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Workflow Requires GitHub API

Some workflows interact with the GitHub API and may not work perfectly locally. In these cases:

1. Mock the API calls
2. Use GitHub's test endpoints
3. Run the workflow on GitHub instead

### Secret Not Found

**Error**: Secret not found

**Solution**: Ensure your `.secrets` file exists and contains the required secrets:

```bash
cat .secrets
```

## Best Practices

### 1. Always Test Locally First

Before pushing workflow changes:

```bash
# Validate syntax
act -n

# Run the workflow
act -W .github/workflows/ci.yml
```

### 2. Use Minimal Docker Images

For faster iteration, use smaller images:

```bash
act -P ubuntu-latest=node:16-alpine
```

### 3. Cache Dependencies

Act respects workflow caching, but the cache is local to your machine.

### 4. Test All Paths

Test both success and failure scenarios:

```bash
# Test with different inputs
act -W .github/workflows/ci.yml --input test_type=unit
act -W .github/workflows/ci.yml --input test_type=integration
```

### 5. Clean Up

Remove old act containers periodically:

```bash
docker container prune
```

## Example Workflow

Here's a typical workflow for testing changes:

```bash
# 1. Make changes to workflow file
vim .github/workflows/ci.yml

# 2. Validate syntax
act -n

# 3. Test locally
act -W .github/workflows/ci.yml

# 4. Fix any issues
vim .github/workflows/ci.yml

# 5. Test again
act -W .github/workflows/ci.yml

# 6. Commit and push
git add .github/workflows/ci.yml
git commit -m "Update CI workflow"
git push
```

## Integration with CI/CD

You can run act in your CI pipeline to validate workflows:

```yaml
# .github/workflows/validate-with-act.yml
name: Validate with act

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install act
        run: |
          curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
      
      - name: Validate workflows
        run: |
          act -n
```

## Additional Resources

- [act Documentation](https://github.com/nektos/act)
- [act Runner Images](https://github.com/catthehacker/docker_images)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
