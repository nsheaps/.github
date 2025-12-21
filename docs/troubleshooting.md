# Troubleshooting Guide

Common issues and solutions when working with this repository.

## Table of Contents

- [GitHub App Authentication Issues](#github-app-authentication-issues)
- [Ansible Playbook Errors](#ansible-playbook-errors)
- [Workflow Sync Problems](#workflow-sync-problems)
- [Local Testing with act](#local-testing-with-act)
- [CI/CD Pipeline Issues](#cicd-pipeline-issues)
- [Metrics Collection Problems](#metrics-collection-problems)

## GitHub App Authentication Issues

### Error: "Bad credentials"

**Symptom**: Ansible playbook fails with authentication error.

**Possible Causes**:
1. Incorrect App ID or Installation ID
2. Malformed private key
3. GitHub App not installed on organization

**Solutions**:

1. Verify App ID and Installation ID:
   ```bash
   ansible-vault edit ansible/inventory/vault.yml
   # Check vault_github_app_id and vault_github_installation_id
   ```

2. Ensure private key is correctly formatted:
   - Must start with `-----BEGIN RSA PRIVATE KEY-----`
   - Must end with `-----END RSA PRIVATE KEY-----`
   - Must preserve all line breaks from the original `.pem` file

3. Verify GitHub App installation:
   - Go to `https://github.com/organizations/YOUR_ORG/settings/installations`
   - Ensure your app is listed and active

### Error: "Resource not accessible by integration"

**Symptom**: API calls fail with permission error.

**Solution**:

Check GitHub App permissions:
1. Go to your GitHub App settings
2. Verify these permissions are granted:
   - Actions: Read & Write
   - Contents: Read & Write
   - Workflows: Read & Write
   - Metadata: Read

3. If you changed permissions, reinstall the app:
   - Go to organization settings → Installed GitHub Apps
   - Configure → Permissions → Review pending changes

### Error: "The token used in the request has expired"

**Symptom**: Long-running playbooks fail with token expiration.

**Solution**:

Installation tokens expire after 1 hour. For long operations:

1. Break into smaller playbooks
2. Re-run the playbook if it fails
3. The playbook will automatically generate a new token

### Error: "Could not generate JWT token"

**Symptom**: Python script fails to create JWT.

**Solutions**:

1. Install required Python packages:
   ```bash
   pip install PyJWT cryptography
   ```

2. Check Python version (requires 3.8+):
   ```bash
   python3 --version
   ```

3. Verify the private key format in vault file

## Ansible Playbook Errors

### Error: "ansible-playbook: command not found"

**Solution**:

Install Ansible:

```bash
pip install ansible
# or
brew install ansible  # macOS
```

### Error: "Could not find module ansible.builtin.uri"

**Solution**:

Install required Ansible collections:

```bash
ansible-galaxy install -r ansible/requirements.yml
```

### Error: "Vault password required"

**Symptom**: Playbook fails to read encrypted vault file.

**Solution**:

Provide vault password:

```bash
ansible-playbook playbooks/sync-workflows.yml \
  -i inventory/production.yml \
  --ask-vault-pass
```

Or use a password file:

```bash
echo "your-password" > .vault_pass
chmod 600 .vault_pass

ansible-playbook playbooks/sync-workflows.yml \
  -i inventory/production.yml \
  --vault-password-file .vault_pass
```

### Error: "No hosts matched"

**Symptom**: Playbook runs but doesn't process any hosts.

**Solution**:

1. Check inventory file syntax:
   ```bash
   ansible-inventory -i ansible/inventory/production.yml --list
   ```

2. Verify hosts are defined:
   ```yaml
   # ansible/inventory/production.yml
   all:
     children:
       target_repos:
         hosts:
           localhost:
             # ... configuration
   ```

### Error: "Template not found"

**Solution**:

Ensure workflow templates exist:

```bash
ls ansible/templates/workflows/
```

Create missing templates or update `workflows_to_sync` list in inventory.

## Workflow Sync Problems

### Workflows Not Syncing

**Symptom**: Playbook completes but workflows aren't updated in target repos.

**Troubleshooting**:

1. Enable verbose output:
   ```bash
   ansible-playbook playbooks/sync-workflows.yml \
     -i inventory/production.yml \
     --ask-vault-pass \
     -vvv
   ```

2. Check if workflows need update:
   ```yaml
   # Set force_sync in inventory
   all:
     vars:
       force_sync: true
   ```

3. Verify repository access:
   - Ensure GitHub App is installed on target repository
   - Check repository exists and name is correct

### Wrong Repository Updated

**Symptom**: Workflows sync to incorrect repository.

**Solution**:

Check inventory configuration:

```yaml
# ansible/inventory/production.yml
target_repos:
  hosts:
    my_repo:
      github_repo: "nsheaps/correct-repo-name"  # Full org/repo format
```

### Workflow Syntax Errors After Sync

**Solution**:

Validate workflows before syncing:

```bash
# Validate all template workflows
./scripts/validate-workflows.sh

# Or manually
actionlint ansible/templates/workflows/*.yml
```

## Local Testing with act

### Error: "Docker not found"

**Solution**:

Install and start Docker:

```bash
# macOS
brew install docker
open /Applications/Docker.app

# Linux
sudo systemctl start docker

# Windows
# Install Docker Desktop
```

### Error: "Permission denied connecting to Docker"

**Solution**:

Add user to docker group (Linux):

```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### act Hangs or Times Out

**Solutions**:

1. Use a smaller Docker image:
   ```bash
   act -P ubuntu-latest=node:16-alpine
   ```

2. Increase Docker memory (Docker Desktop → Settings → Resources)

3. Check Docker logs:
   ```bash
   docker logs $(docker ps -q)
   ```

### Workflows Fail in act but Work on GitHub

**Common Reasons**:

1. **Different runner images**: GitHub uses different images than act
2. **Secret availability**: Ensure `.secrets` file contains required secrets
3. **Network restrictions**: Some services may not be accessible locally

**Solutions**:

1. Test critical workflows on GitHub in a test branch
2. Mock external dependencies
3. Use conditional logic to handle local vs GitHub execution

## CI/CD Pipeline Issues

### Error: "workflow syntax error"

**Solution**:

Validate workflow syntax:

```bash
# Install actionlint
brew install actionlint  # macOS
# or
curl -s https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash | bash

# Validate workflows
actionlint .github/workflows/*.yml
```

### Tests Failing After Changes

**Troubleshooting**:

1. Run tests locally:
   ```bash
   pytest tests/ -v
   ```

2. Check specific test:
   ```bash
   pytest tests/test_playbooks.py::TestAnsibleStructure -v
   ```

3. Update tests if structure changed legitimately

### Linting Failures

**Solution**:

Run ansible-lint locally:

```bash
ansible-lint ansible/
```

Fix reported issues or add exclusions:

```yaml
# .ansible-lint
exclude_paths:
  - ansible/roles/external/
```

## Metrics Collection Problems

### Metrics Not Appearing in Datadog

**Troubleshooting**:

1. Verify API key is set:
   ```bash
   # Check repository secrets in GitHub settings
   ```

2. Check Datadog site configuration:
   - Ensure `DATADOG_SITE` is correct (e.g., `datadoghq.com` or `datadoghq.eu`)

3. Review workflow run logs:
   - Go to Actions → Select workflow run → Check "Send metrics to Datadog" step

4. Test API endpoint:
   ```bash
   curl -X GET "https://api.datadoghq.com/api/v1/validate" \
     -H "DD-API-KEY: ${YOUR_API_KEY}"
   ```

### Prometheus Metrics Not Updating

**Solutions**:

1. Verify Pushgateway is accessible:
   ```bash
   curl http://your-pushgateway:9091/metrics
   ```

2. Check if metrics were pushed:
   ```bash
   curl http://your-pushgateway:9091/metrics | grep github_workflow
   ```

3. Ensure Prometheus is scraping the Pushgateway:
   ```yaml
   # prometheus.yml
   scrape_configs:
     - job_name: 'pushgateway'
       static_configs:
         - targets: ['pushgateway:9091']
   ```

### New Relic Events Not Visible

**Troubleshooting**:

1. Verify credentials:
   - Check `NEW_RELIC_API_KEY` and `NEW_RELIC_ACCOUNT_ID` are set

2. Test API endpoint:
   ```bash
   curl -X POST \
     "https://insights-collector.newrelic.com/v1/accounts/${ACCOUNT_ID}/events" \
     -H "Content-Type: application/json" \
     -H "X-Insert-Key: ${API_KEY}" \
     -d '[{"eventType":"Test"}]'
   ```

3. Query for events in New Relic:
   ```sql
   SELECT * FROM GitHubWorkflowRun SINCE 1 hour ago
   ```

4. Check event limits (New Relic has rate limits on event ingestion)

## General Troubleshooting Tips

### Enable Verbose Logging

**Ansible**:
```bash
ansible-playbook playbooks/sync-workflows.yml -vvv
```

**GitHub Actions**:
```yaml
- name: Debug
  run: |
    set -x  # Enable bash debugging
    # your commands
```

### Check Environment

Verify your environment:

```bash
# Python version
python3 --version

# Ansible version
ansible --version

# Docker version (for act)
docker --version

# act version
act --version
```

### Reset to Clean State

If things are completely broken:

```bash
# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Reset Ansible collections
rm -rf ~/.ansible/collections
ansible-galaxy install -r ansible/requirements.yml
```

### Get More Help

If you're still stuck:

1. Check repository Issues for similar problems
2. Review GitHub Actions logs in detail
3. Enable debug logging in GitHub Actions:
   - Settings → Secrets → Add `ACTIONS_STEP_DEBUG` = `true`
4. Contact the repository maintainers with:
   - Error message
   - Steps to reproduce
   - Environment details (OS, versions)

## Additional Resources

- [Ansible Documentation](https://docs.ansible.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [act Documentation](https://github.com/nektos/act)
- [Datadog Documentation](https://docs.datadoghq.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [New Relic Documentation](https://docs.newrelic.com/)
