"""Data models for GitHub Stars Manager."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Repository(BaseModel):
    """Represents a GitHub repository."""

    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    stargazers_count: int = 0
    language: Optional[str] = None
    topics: list[str] = Field(default_factory=list)
    owner_login: str
    starred_at: Optional[datetime] = None
    archived: bool = False
    fork: bool = False

    @classmethod
    def from_api_response(cls, data: dict, starred_at: Optional[str] = None) -> "Repository":
        """Create a Repository from GitHub API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            full_name=data["full_name"],
            description=data.get("description"),
            html_url=data["html_url"],
            stargazers_count=data.get("stargazers_count", 0),
            language=data.get("language"),
            topics=data.get("topics", []),
            owner_login=data["owner"]["login"],
            starred_at=datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
            if starred_at
            else None,
            archived=data.get("archived", False),
            fork=data.get("fork", False),
        )


class StarList(BaseModel):
    """Represents a GitHub star list."""

    id: int
    name: str
    description: Optional[str] = None
    is_public: bool = True
    repo_count: int = 0

    @classmethod
    def from_api_response(cls, data: dict) -> "StarList":
        """Create a StarList from GitHub API response."""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            is_public=not data.get("is_private", False),
            repo_count=data.get("repositories_count", 0),
        )


class ListAssignment(BaseModel):
    """Represents a repository's assignment to lists."""

    repo_full_name: str
    list_names: list[str] = Field(default_factory=list)


class StarsSummary(BaseModel):
    """Summary statistics for starred repositories."""

    total_stars: int
    total_lists: int
    repos_in_lists: int
    repos_uncategorized: int
    languages: dict[str, int] = Field(default_factory=dict)
    topics: dict[str, int] = Field(default_factory=dict)
