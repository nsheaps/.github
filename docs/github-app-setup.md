# GitHub App Setup Guide

This guide walks through the process of creating and configuring a GitHub App for authenticating with the GitHub API to sync workflows across repositories.

## Why GitHub Apps?

GitHub Apps provide several advantages over personal access tokens:

- **Fine-grained permissions**: Only grant the specific permissions needed
- **Higher rate limits**: 5,000 requests per hour per installation
- **Organization-wide installation**: Can be installed across all repositories
- **Audit trail**: All actions are attributed to the app, not a personal account
- **Automatic token expiration**: Installation tokens expire after 1 hour

## Creating a GitHub App

### 1. Navigate to GitHub App Settings

For organization-owned apps:
- Go to your organization's settings: `https://github.com/organizations/YOUR_ORG/settings/apps`
- Click **New GitHub App**

For personal apps:
- Go to your personal settings: `https://github.com/settings/apps`
- Click **New GitHub App**

### 2. Configure Basic Information

Fill in the following fields:

- **GitHub App name**: Choose a unique name (e.g., "Workflow Sync Bot")
- **Homepage URL**: Your organization's website or this repository URL
- **Webhook URL**: Leave blank if not using webhooks
- **Webhook secret**: Leave blank if not using webhooks
- Uncheck **Active** under "Webhook" if not using webhooks

### 3. Set Permissions

Configure the following repository permissions:

| Permission | Access Level | Reason |
|------------|--------------|--------|
| Actions | Read & Write | Deploy and manage workflow files |
| Contents | Read & Write | Read/write repository files |
| Workflows | Read & Write | Modify workflow files |
| Metadata | Read | Access repository metadata |

Configure organization permissions:

| Permission | Access Level | Reason |
|------------|--------------|--------|
| Administration | Read | List organization repositories |

### 4. Choose Installation Location

Under "Where can this GitHub App be installed?":
- Select **Only on this account** for organization-specific apps

### 5. Create the App

Click **Create GitHub App** to create your app.

## Generating Credentials

### 1. Generate a Private Key

After creating the app:

1. Scroll to the **Private keys** section
2. Click **Generate a private key**
3. A `.pem` file will be downloaded to your computer
4. **Store this file securely** - you'll need it for authentication

### 2. Note Your App ID

At the top of the app settings page, note the **App ID** number. You'll need this for configuration.

### 3. Install the App

1. Click **Install App** in the left sidebar
2. Select the organization or account to install on
3. Choose **All repositories** or select specific repositories
4. Click **Install**
5. Note the **Installation ID** from the URL (e.g., `https://github.com/organizations/YOUR_ORG/settings/installations/INSTALLATION_ID`)

## Configuring Ansible Vault

Now that you have your GitHub App credentials, store them securely using Ansible Vault:

### 1. Create Vault File

```bash
cd ansible/inventory
cp example.vault.yml vault.yml
```

### 2. Edit Vault File

```bash
ansible-vault edit vault.yml
```

You'll be prompted to create a vault password. Enter a strong password and remember it.

### 3. Add Your Credentials

In the vault file, replace the example values:

```yaml
---
vault_github_app_id: "YOUR_APP_ID"
vault_github_installation_id: "YOUR_INSTALLATION_ID"
vault_github_private_key: |
  -----BEGIN RSA PRIVATE KEY-----
  [Paste the contents of your .pem file here]
  -----END RSA PRIVATE KEY-----
```

Save and exit the editor.

### 4. Verify Encryption

Check that the file is encrypted:

```bash
cat vault.yml
```

You should see encrypted content, not plaintext.

## Using the Credentials

When running Ansible playbooks, provide the vault password:

```bash
ansible-playbook playbooks/sync-workflows.yml \
  -i inventory/production.yml \
  --ask-vault-pass
```

Or use a password file:

```bash
echo "your-vault-password" > .vault_pass
chmod 600 .vault_pass
ansible-playbook playbooks/sync-workflows.yml \
  -i inventory/production.yml \
  --vault-password-file .vault_pass
```

**Important**: Add `.vault_pass` to `.gitignore` to prevent committing the password!

## Testing Authentication

Test your GitHub App authentication:

```bash
cd ansible
ansible-playbook playbooks/sync-workflows.yml \
  -i inventory/production.yml \
  --ask-vault-pass \
  --check
```

If authentication is successful, you'll see tasks execute without errors.

## Rotating Credentials

### Rotating Private Keys

It's good practice to rotate your private key periodically:

1. Go to your GitHub App settings
2. Under **Private keys**, click **Generate a private key**
3. Download the new key
4. Update your vault file with the new key:
   ```bash
   ansible-vault edit ansible/inventory/vault.yml
   ```
5. Test with the new credentials
6. Revoke the old private key in GitHub App settings

### Changing Vault Password

To change your Ansible Vault password:

```bash
ansible-vault rekey ansible/inventory/vault.yml
```

## Troubleshooting

### "Bad credentials" Error

- Verify your App ID and Installation ID are correct
- Ensure the private key is properly formatted with line breaks
- Check that the GitHub App is installed on your organization

### "Resource not accessible by integration"

- Review the permissions granted to your GitHub App
- Ensure the app has "Contents: Read & Write" and "Workflows: Read & Write"
- Verify the app is installed on the target repositories

### "The token used in the request has expired"

- Installation tokens expire after 1 hour
- The playbook automatically generates new tokens
- If running long operations, tokens may need to be refreshed

## Additional Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Creating a GitHub App](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/registering-a-github-app)
- [Authenticating with GitHub Apps](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/about-authentication-with-a-github-app)
- [GitHub App Permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)
- [Ansible Vault Documentation](https://docs.ansible.com/ansible/latest/vault_guide/index.html)
