"""GitHub API client for managing stars and lists."""

import os
from typing import Optional

import httpx

from .models import Repository, StarList, StarsSummary


class GitHubAPIError(Exception):
    """Exception raised for GitHub API errors."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"GitHub API error ({status_code}): {message}")


class GitHubClient:
    """Client for interacting with GitHub's REST API."""

    BASE_URL = "https://api.github.com"
    DEFAULT_PER_PAGE = 100

    def __init__(self, token: Optional[str] = None):
        """Initialize the GitHub client.

        Args:
            token: GitHub personal access token. If not provided, will look for
                   GITHUB_TOKEN or GH_TOKEN environment variables.
        """
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        if not self.token:
            raise ValueError(
                "GitHub token required. Set GITHUB_TOKEN or GH_TOKEN environment variable, "
                "or pass token directly."
            )

        self._client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make an authenticated request to the GitHub API."""
        response = self._client.request(method, endpoint, **kwargs)

        if response.status_code >= 400:
            try:
                error_data = response.json()
                message = error_data.get("message", response.text)
            except Exception:
                message = response.text
            raise GitHubAPIError(response.status_code, message)

        return response

    def _paginate(self, endpoint: str, params: Optional[dict] = None) -> list[dict]:
        """Fetch all pages of a paginated endpoint."""
        params = params or {}
        params.setdefault("per_page", self.DEFAULT_PER_PAGE)
        page = 1
        all_results = []

        while True:
            params["page"] = page
            response = self._request("GET", endpoint, params=params)
            data = response.json()

            if not data:
                break

            all_results.extend(data)

            # Check if there are more pages via Link header
            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break

            page += 1

        return all_results

    def get_authenticated_user(self) -> dict:
        """Get the authenticated user's information."""
        return self._request("GET", "/user").json()

    # === Starred Repositories ===

    def get_starred_repos(self, username: Optional[str] = None) -> list[Repository]:
        """Get all starred repositories for a user.

        Args:
            username: GitHub username. If not provided, uses authenticated user.

        Returns:
            List of Repository objects.
        """
        if username:
            endpoint = f"/users/{username}/starred"
        else:
            endpoint = "/user/starred"

        # Use special Accept header to get starred_at timestamp
        headers = {"Accept": "application/vnd.github.star+json"}
        params = {"per_page": self.DEFAULT_PER_PAGE}
        page = 1
        all_repos = []

        while True:
            params["page"] = page
            response = self._client.request(
                "GET",
                endpoint,
                params=params,
                headers={**self._client.headers, **headers},
            )

            if response.status_code >= 400:
                raise GitHubAPIError(response.status_code, response.text)

            data = response.json()
            if not data:
                break

            for item in data:
                repo_data = item.get("repo", item)
                starred_at = item.get("starred_at")
                all_repos.append(Repository.from_api_response(repo_data, starred_at))

            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break

            page += 1

        return all_repos

    def star_repo(self, owner: str, repo: str) -> None:
        """Star a repository."""
        self._request("PUT", f"/user/starred/{owner}/{repo}")

    def unstar_repo(self, owner: str, repo: str) -> None:
        """Unstar a repository."""
        self._request("DELETE", f"/user/starred/{owner}/{repo}")

    def is_repo_starred(self, owner: str, repo: str) -> bool:
        """Check if a repository is starred."""
        try:
            self._request("GET", f"/user/starred/{owner}/{repo}")
            return True
        except GitHubAPIError as e:
            if e.status_code == 404:
                return False
            raise

    # === Star Lists ===

    def get_star_lists(self) -> list[StarList]:
        """Get all star lists for the authenticated user."""
        data = self._paginate("/user/starred/lists")
        return [StarList.from_api_response(item) for item in data]

    def create_star_list(
        self, name: str, description: Optional[str] = None, is_private: bool = False
    ) -> StarList:
        """Create a new star list.

        Args:
            name: Name of the list.
            description: Optional description.
            is_private: Whether the list is private.

        Returns:
            The created StarList.
        """
        payload = {"name": name, "is_private": is_private}
        if description:
            payload["description"] = description

        response = self._request("POST", "/user/starred/lists", json=payload)
        return StarList.from_api_response(response.json())

    def delete_star_list(self, list_id: int) -> None:
        """Delete a star list."""
        self._request("DELETE", f"/user/starred/lists/{list_id}")

    def update_star_list(
        self,
        list_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_private: Optional[bool] = None,
    ) -> StarList:
        """Update a star list.

        Args:
            list_id: ID of the list to update.
            name: New name (optional).
            description: New description (optional).
            is_private: New privacy setting (optional).

        Returns:
            The updated StarList.
        """
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if is_private is not None:
            payload["is_private"] = is_private

        response = self._request("PATCH", f"/user/starred/lists/{list_id}", json=payload)
        return StarList.from_api_response(response.json())

    def get_list_repos(self, list_id: int) -> list[Repository]:
        """Get all repositories in a star list."""
        data = self._paginate(f"/user/starred/lists/{list_id}/repositories")
        return [Repository.from_api_response(item) for item in data]

    def add_repo_to_list(self, list_id: int, owner: str, repo: str) -> None:
        """Add a repository to a star list."""
        self._request("PUT", f"/user/starred/lists/{list_id}/repositories/{owner}/{repo}")

    def remove_repo_from_list(self, list_id: int, owner: str, repo: str) -> None:
        """Remove a repository from a star list."""
        self._request("DELETE", f"/user/starred/lists/{list_id}/repositories/{owner}/{repo}")

    def get_repo_lists(self, owner: str, repo: str) -> list[StarList]:
        """Get all lists that contain a repository."""
        data = self._paginate(f"/user/starred/lists/repositories/{owner}/{repo}")
        return [StarList.from_api_response(item) for item in data]

    # === Analysis & Summary ===

    def get_stars_summary(self) -> StarsSummary:
        """Get summary statistics for starred repositories."""
        repos = self.get_starred_repos()
        lists = self.get_star_lists()

        # Count repos in each list
        repos_in_lists = set()
        for star_list in lists:
            list_repos = self.get_list_repos(star_list.id)
            for repo in list_repos:
                repos_in_lists.add(repo.full_name)

        # Count languages
        languages: dict[str, int] = {}
        for repo in repos:
            if repo.language:
                languages[repo.language] = languages.get(repo.language, 0) + 1

        # Count topics
        topics: dict[str, int] = {}
        for repo in repos:
            for topic in repo.topics:
                topics[topic] = topics.get(topic, 0) + 1

        return StarsSummary(
            total_stars=len(repos),
            total_lists=len(lists),
            repos_in_lists=len(repos_in_lists),
            repos_uncategorized=len(repos) - len(repos_in_lists),
            languages=dict(sorted(languages.items(), key=lambda x: x[1], reverse=True)),
            topics=dict(sorted(topics.items(), key=lambda x: x[1], reverse=True)[:20]),
        )

    def get_uncategorized_repos(self) -> list[Repository]:
        """Get starred repositories that are not in any list."""
        repos = self.get_starred_repos()
        lists = self.get_star_lists()

        repos_in_lists = set()
        for star_list in lists:
            list_repos = self.get_list_repos(star_list.id)
            for repo in list_repos:
                repos_in_lists.add(repo.full_name)

        return [repo for repo in repos if repo.full_name not in repos_in_lists]
