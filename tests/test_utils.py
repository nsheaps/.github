"""Tests for utility functions."""

import pytest
from stars_manager.models import Repository
from stars_manager.utils import (
    format_repo_url,
    get_language_distribution,
    get_topic_distribution,
    parse_repo_identifier,
    suggest_lists_for_repo,
)


def make_repo(
    full_name: str = "owner/repo",
    language: str | None = None,
    topics: list[str] | None = None,
    description: str | None = None,
) -> Repository:
    """Helper to create test repositories."""
    return Repository(
        id=1,
        name=full_name.split("/")[1],
        full_name=full_name,
        html_url=f"https://github.com/{full_name}",
        owner_login=full_name.split("/")[0],
        language=language,
        topics=topics or [],
        description=description,
    )


class TestSuggestListsForRepo:
    """Tests for suggest_lists_for_repo function."""

    def test_python_language(self):
        """Test suggestions for Python repos."""
        repo = make_repo(language="Python")
        suggestions = suggest_lists_for_repo(repo)
        assert "python" in suggestions

    def test_ai_topic(self):
        """Test suggestions for AI-related topics."""
        repo = make_repo(topics=["machine-learning", "deep-learning"])
        suggestions = suggest_lists_for_repo(repo)
        assert "ai" in suggestions or "ml" in suggestions

    def test_homelab_topic(self):
        """Test suggestions for homelab topics."""
        repo = make_repo(topics=["homelab", "self-hosted"])
        suggestions = suggest_lists_for_repo(repo)
        assert "homelab" in suggestions

    def test_combined_suggestions(self):
        """Test combined language and topic suggestions."""
        repo = make_repo(
            language="Go",
            topics=["kubernetes", "docker"],
        )
        suggestions = suggest_lists_for_repo(repo)
        assert "golang" in suggestions or "go-tools" in suggestions
        assert "devops" in suggestions

    def test_no_duplicates(self):
        """Test that suggestions don't contain duplicates."""
        repo = make_repo(
            language="Python",
            topics=["cli", "terminal"],
            description="A CLI tool for Python",
        )
        suggestions = suggest_lists_for_repo(repo)
        assert len(suggestions) == len(set(suggestions))


class TestParseRepoIdentifier:
    """Tests for parse_repo_identifier function."""

    def test_simple_format(self):
        """Test owner/name format."""
        owner, name = parse_repo_identifier("owner/repo")
        assert owner == "owner"
        assert name == "repo"

    def test_https_url(self):
        """Test HTTPS GitHub URL."""
        owner, name = parse_repo_identifier("https://github.com/owner/repo")
        assert owner == "owner"
        assert name == "repo"

    def test_url_with_trailing_slash(self):
        """Test URL with trailing slash."""
        owner, name = parse_repo_identifier("https://github.com/owner/repo/")
        assert owner == "owner"
        assert name == "repo"

    def test_url_with_git_suffix(self):
        """Test URL with .git suffix."""
        owner, name = parse_repo_identifier("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert name == "repo"

    def test_invalid_format(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError):
            parse_repo_identifier("invalid")


class TestFormatRepoUrl:
    """Tests for format_repo_url function."""

    def test_basic(self):
        """Test basic URL formatting."""
        url = format_repo_url("owner/repo")
        assert url == "https://github.com/owner/repo"


class TestGetLanguageDistribution:
    """Tests for get_language_distribution function."""

    def test_distribution(self):
        """Test language distribution calculation."""
        repos = [
            make_repo("a/1", language="Python"),
            make_repo("a/2", language="Python"),
            make_repo("a/3", language="Go"),
            make_repo("a/4", language=None),
        ]
        dist = get_language_distribution(repos)

        assert dist["Python"] == 2
        assert dist["Go"] == 1
        assert None not in dist


class TestGetTopicDistribution:
    """Tests for get_topic_distribution function."""

    def test_distribution(self):
        """Test topic distribution calculation."""
        repos = [
            make_repo("a/1", topics=["cli", "python"]),
            make_repo("a/2", topics=["cli", "docker"]),
            make_repo("a/3", topics=["kubernetes"]),
        ]
        dist = get_topic_distribution(repos)

        assert dist["cli"] == 2
        assert dist["python"] == 1
        assert dist["docker"] == 1
        assert dist["kubernetes"] == 1

    def test_with_limit(self):
        """Test topic distribution with limit."""
        repos = [
            make_repo("a/1", topics=["a", "b", "c"]),
            make_repo("a/2", topics=["a", "b"]),
            make_repo("a/3", topics=["a"]),
        ]
        dist = get_topic_distribution(repos, limit=2)

        assert len(dist) == 2
        assert "a" in dist
