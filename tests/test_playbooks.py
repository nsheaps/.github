"""
Test suite for Ansible playbooks and roles.
"""

import os
import pytest
import yaml


class TestAnsibleStructure:
    """Test Ansible directory structure and files."""

    def test_playbooks_directory_exists(self):
        """Verify playbooks directory exists."""
        assert os.path.isdir("ansible/playbooks")

    def test_roles_directory_exists(self):
        """Verify roles directory exists."""
        assert os.path.isdir("ansible/roles")

    def test_inventory_directory_exists(self):
        """Verify inventory directory exists."""
        assert os.path.isdir("ansible/inventory")

    def test_templates_directory_exists(self):
        """Verify templates directory exists."""
        assert os.path.isdir("ansible/templates")


class TestPlaybooks:
    """Test Ansible playbooks."""

    def test_sync_workflows_playbook_exists(self):
        """Verify sync-workflows.yml exists."""
        assert os.path.isfile("ansible/playbooks/sync-workflows.yml")

    def test_sync_workflows_valid_yaml(self):
        """Verify sync-workflows.yml is valid YAML."""
        with open("ansible/playbooks/sync-workflows.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert isinstance(data, list)

    def test_requirements_file_exists(self):
        """Verify requirements.yml exists."""
        assert os.path.isfile("ansible/requirements.yml")

    def test_requirements_valid_yaml(self):
        """Verify requirements.yml is valid YAML."""
        with open("ansible/requirements.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert "collections" in data


class TestRoles:
    """Test Ansible roles."""

    def test_github_app_auth_role_exists(self):
        """Verify github_app_auth role exists."""
        assert os.path.isdir("ansible/roles/github_app_auth")
        assert os.path.isfile("ansible/roles/github_app_auth/tasks/main.yml")

    def test_workflow_sync_role_exists(self):
        """Verify workflow_sync role exists."""
        assert os.path.isdir("ansible/roles/workflow_sync")
        assert os.path.isfile("ansible/roles/workflow_sync/tasks/main.yml")

    def test_github_app_auth_tasks_valid_yaml(self):
        """Verify github_app_auth tasks are valid YAML."""
        with open("ansible/roles/github_app_auth/tasks/main.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert isinstance(data, list)

    def test_workflow_sync_tasks_valid_yaml(self):
        """Verify workflow_sync tasks are valid YAML."""
        with open("ansible/roles/workflow_sync/tasks/main.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert isinstance(data, list)


class TestInventory:
    """Test Ansible inventory files."""

    def test_production_inventory_exists(self):
        """Verify production inventory exists."""
        assert os.path.isfile("ansible/inventory/production.yml")

    def test_example_vault_exists(self):
        """Verify example vault file exists."""
        assert os.path.isfile("ansible/inventory/example.vault.yml")

    def test_production_inventory_valid_yaml(self):
        """Verify production inventory is valid YAML."""
        with open("ansible/inventory/production.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert "all" in data


class TestTemplates:
    """Test workflow templates."""

    def test_shared_ci_template_exists(self):
        """Verify shared-ci.yml template exists."""
        assert os.path.isfile("ansible/templates/workflows/shared-ci.yml")

    def test_shared_ci_valid_yaml(self):
        """Verify shared-ci.yml is valid YAML."""
        with open("ansible/templates/workflows/shared-ci.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert "name" in data
            assert "on" in data
            assert "jobs" in data


class TestWorkflows:
    """Test GitHub Actions workflows."""

    def test_ci_workflow_exists(self):
        """Verify CI workflow exists."""
        assert os.path.isfile(".github/workflows/ci.yml")

    def test_validate_workflows_exists(self):
        """Verify validate-workflows workflow exists."""
        assert os.path.isfile(".github/workflows/validate-workflows.yml")

    def test_ansible_test_workflow_exists(self):
        """Verify ansible-test workflow exists."""
        assert os.path.isfile(".github/workflows/ansible-test.yml")

    def test_workflow_run_metrics_exists(self):
        """Verify workflow-run-metrics workflow exists."""
        assert os.path.isfile(".github/workflows/workflow-run-metrics.yml")

    def test_ci_workflow_valid_yaml(self):
        """Verify CI workflow is valid YAML."""
        with open(".github/workflows/ci.yml", "r") as f:
            data = yaml.safe_load(f)
            assert data is not None
            assert "name" in data
            assert "jobs" in data


class TestScripts:
    """Test utility scripts."""

    def test_validate_workflows_script_exists(self):
        """Verify validate-workflows.sh exists."""
        assert os.path.isfile("scripts/validate-workflows.sh")

    def test_validate_workflows_script_executable(self):
        """Verify validate-workflows.sh is executable."""
        assert os.access("scripts/validate-workflows.sh", os.X_OK)


class TestDocumentation:
    """Test documentation files."""

    def test_readme_exists(self):
        """Verify README.md exists."""
        assert os.path.isfile("README.md")

    def test_license_exists(self):
        """Verify LICENSE file exists."""
        assert os.path.isfile("LICENSE")

    def test_requirements_txt_exists(self):
        """Verify requirements.txt exists."""
        assert os.path.isfile("requirements.txt")

    def test_renovate_config_exists(self):
        """Verify renovate.json exists."""
        assert os.path.isfile("renovate.json")

    def test_actrc_exists(self):
        """Verify .actrc exists."""
        assert os.path.isfile(".actrc")


class TestConfiguration:
    """Test configuration files."""

    def test_renovate_config_valid_json(self):
        """Verify renovate.json is valid JSON."""
        import json
        with open("renovate.json", "r") as f:
            data = json.load(f)
            assert data is not None
            assert "extends" in data
            assert "github>nsheaps/renovate-config" in data["extends"]

    def test_requirements_has_ansible(self):
        """Verify requirements.txt includes Ansible."""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "ansible" in content.lower()

    def test_requirements_has_pytest(self):
        """Verify requirements.txt includes pytest."""
        with open("requirements.txt", "r") as f:
            content = f.read()
            assert "pytest" in content.lower()
