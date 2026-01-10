"""Tests for data models."""

import pytest
from stars_manager.models import Repository, StarList, StarsSummary


class TestRepository:
    """Tests for Repository model."""

    def test_from_api_response_minimal(self):
        """Test creating Repository from minimal API response."""
        data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "html_url": "https://github.com/owner/test-repo",
            "owner": {"login": "owner"},
        }
        repo = Repository.from_api_response(data)

        assert repo.id == 123
        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
        assert repo.owner_login == "owner"
        assert repo.description is None
        assert repo.language is None
        assert repo.topics == []

    def test_from_api_response_full(self):
        """Test creating Repository from full API response."""
        data = {
            "id": 456,
            "name": "full-repo",
            "full_name": "owner/full-repo",
            "description": "A test repository",
            "html_url": "https://github.com/owner/full-repo",
            "stargazers_count": 100,
            "language": "Python",
            "topics": ["testing", "python"],
            "owner": {"login": "owner"},
            "archived": False,
            "fork": True,
        }
        repo = Repository.from_api_response(data, starred_at="2024-01-15T10:30:00Z")

        assert repo.id == 456
        assert repo.description == "A test repository"
        assert repo.stargazers_count == 100
        assert repo.language == "Python"
        assert repo.topics == ["testing", "python"]
        assert repo.archived is False
        assert repo.fork is True
        assert repo.starred_at is not None


class TestStarList:
    """Tests for StarList model."""

    def test_from_api_response(self):
        """Test creating StarList from API response."""
        data = {
            "id": 789,
            "name": "ai",
            "description": "AI and ML projects",
            "is_private": False,
            "repositories_count": 11,
        }
        star_list = StarList.from_api_response(data)

        assert star_list.id == 789
        assert star_list.name == "ai"
        assert star_list.description == "AI and ML projects"
        assert star_list.is_public is True
        assert star_list.repo_count == 11

    def test_from_api_response_private(self):
        """Test creating private StarList from API response."""
        data = {
            "id": 101,
            "name": "private-list",
            "is_private": True,
            "repositories_count": 5,
        }
        star_list = StarList.from_api_response(data)

        assert star_list.is_public is False


class TestStarsSummary:
    """Tests for StarsSummary model."""

    def test_default_values(self):
        """Test StarsSummary with default values."""
        summary = StarsSummary(
            total_stars=149,
            total_lists=2,
            repos_in_lists=12,
            repos_uncategorized=137,
        )

        assert summary.total_stars == 149
        assert summary.total_lists == 2
        assert summary.repos_in_lists == 12
        assert summary.repos_uncategorized == 137
        assert summary.languages == {}
        assert summary.topics == {}

    def test_with_languages_and_topics(self):
        """Test StarsSummary with languages and topics."""
        summary = StarsSummary(
            total_stars=50,
            total_lists=3,
            repos_in_lists=20,
            repos_uncategorized=30,
            languages={"Python": 25, "JavaScript": 15, "Go": 10},
            topics={"cli": 8, "docker": 5, "kubernetes": 3},
        )

        assert summary.languages["Python"] == 25
        assert summary.topics["cli"] == 8
