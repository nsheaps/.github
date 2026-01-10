"""Utility functions for GitHub Stars Manager."""

from collections import Counter
from typing import Optional

from .models import Repository


def suggest_lists_for_repo(repo: Repository) -> list[str]:
    """Suggest potential list names for a repository based on its properties.

    Args:
        repo: The repository to analyze.

    Returns:
        List of suggested list names.
    """
    suggestions = []

    # Language-based suggestions
    language_lists = {
        "Python": ["python", "python-tools"],
        "JavaScript": ["javascript", "web"],
        "TypeScript": ["typescript", "web"],
        "Go": ["golang", "go-tools"],
        "Rust": ["rust", "systems"],
        "Ruby": ["ruby"],
        "Java": ["java", "jvm"],
        "Kotlin": ["kotlin", "jvm"],
        "C": ["c-cpp", "systems"],
        "C++": ["c-cpp", "systems"],
        "Shell": ["devops", "scripts"],
        "Dockerfile": ["devops", "docker"],
    }

    if repo.language and repo.language in language_lists:
        suggestions.extend(language_lists[repo.language])

    # Topic-based suggestions
    topic_mappings = {
        "machine-learning": ["ai", "ml"],
        "deep-learning": ["ai", "ml"],
        "artificial-intelligence": ["ai"],
        "llm": ["ai", "llm"],
        "kubernetes": ["devops", "k8s"],
        "docker": ["devops", "docker"],
        "terraform": ["devops", "infra"],
        "ansible": ["devops", "automation"],
        "homelab": ["homelab", "self-hosted"],
        "self-hosted": ["homelab", "self-hosted"],
        "cli": ["tools", "cli"],
        "terminal": ["tools", "cli"],
        "neovim": ["dotfiles", "editor"],
        "vim": ["dotfiles", "editor"],
        "react": ["web", "frontend"],
        "vue": ["web", "frontend"],
        "nextjs": ["web", "fullstack"],
        "api": ["backend", "api"],
        "database": ["backend", "database"],
        "security": ["security"],
        "privacy": ["security", "privacy"],
        "awesome": ["awesome-lists"],
    }

    for topic in repo.topics:
        topic_lower = topic.lower()
        if topic_lower in topic_mappings:
            suggestions.extend(topic_mappings[topic_lower])

    # Description-based suggestions
    if repo.description:
        desc_lower = repo.description.lower()
        keyword_mappings = {
            "home lab": ["homelab"],
            "home-lab": ["homelab"],
            "self-host": ["homelab", "self-hosted"],
            "ai ": ["ai"],
            "machine learning": ["ai", "ml"],
            "neural network": ["ai", "ml"],
            "llm": ["ai", "llm"],
            "language model": ["ai", "llm"],
            "cli tool": ["tools", "cli"],
            "command line": ["tools", "cli"],
            "kubernetes": ["devops", "k8s"],
            "docker": ["devops", "docker"],
        }

        for keyword, lists in keyword_mappings.items():
            if keyword in desc_lower:
                suggestions.extend(lists)

    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique_suggestions.append(s)

    return unique_suggestions


def analyze_repos_for_categorization(
    repos: list[Repository],
) -> dict[str, list[Repository]]:
    """Analyze repositories and suggest categorizations.

    Args:
        repos: List of repositories to analyze.

    Returns:
        Dictionary mapping suggested list names to repositories.
    """
    categorizations: dict[str, list[Repository]] = {}

    for repo in repos:
        suggestions = suggest_lists_for_repo(repo)
        for suggestion in suggestions:
            if suggestion not in categorizations:
                categorizations[suggestion] = []
            categorizations[suggestion].append(repo)

    # Sort by number of repos in each category
    return dict(sorted(categorizations.items(), key=lambda x: len(x[1]), reverse=True))


def find_similar_repos(
    target: Repository,
    repos: list[Repository],
    limit: int = 10,
) -> list[tuple[Repository, float]]:
    """Find repositories similar to the target based on language and topics.

    Args:
        target: The target repository.
        repos: List of repositories to compare against.
        limit: Maximum number of similar repos to return.

    Returns:
        List of (repository, similarity_score) tuples, sorted by score.
    """
    scores: list[tuple[Repository, float]] = []

    target_topics = set(t.lower() for t in target.topics)

    for repo in repos:
        if repo.full_name == target.full_name:
            continue

        score = 0.0

        # Language match
        if target.language and repo.language:
            if target.language.lower() == repo.language.lower():
                score += 3.0

        # Topic overlap
        repo_topics = set(t.lower() for t in repo.topics)
        if target_topics and repo_topics:
            overlap = len(target_topics & repo_topics)
            union = len(target_topics | repo_topics)
            if union > 0:
                score += (overlap / union) * 5.0

        # Same owner
        if target.owner_login == repo.owner_login:
            score += 1.0

        if score > 0:
            scores.append((repo, score))

    # Sort by score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:limit]


def get_language_distribution(repos: list[Repository]) -> dict[str, int]:
    """Get the distribution of programming languages in repositories.

    Args:
        repos: List of repositories.

    Returns:
        Dictionary mapping language names to counts.
    """
    languages = [r.language for r in repos if r.language]
    return dict(Counter(languages).most_common())


def get_topic_distribution(repos: list[Repository], limit: Optional[int] = None) -> dict[str, int]:
    """Get the distribution of topics in repositories.

    Args:
        repos: List of repositories.
        limit: Maximum number of topics to return.

    Returns:
        Dictionary mapping topic names to counts.
    """
    all_topics = []
    for repo in repos:
        all_topics.extend(repo.topics)

    counter = Counter(all_topics)
    if limit:
        return dict(counter.most_common(limit))
    return dict(counter.most_common())


def format_repo_url(full_name: str) -> str:
    """Format a repository full name into a GitHub URL.

    Args:
        full_name: Repository in 'owner/name' format.

    Returns:
        Full GitHub URL.
    """
    return f"https://github.com/{full_name}"


def parse_repo_identifier(identifier: str) -> tuple[str, str]:
    """Parse a repository identifier into owner and name.

    Args:
        identifier: Repository identifier (URL or 'owner/name' format).

    Returns:
        Tuple of (owner, name).

    Raises:
        ValueError: If the identifier format is invalid.
    """
    # Handle GitHub URLs
    if identifier.startswith("https://github.com/"):
        identifier = identifier.replace("https://github.com/", "")
    elif identifier.startswith("http://github.com/"):
        identifier = identifier.replace("http://github.com/", "")
    elif identifier.startswith("github.com/"):
        identifier = identifier.replace("github.com/", "")

    # Remove trailing slashes and .git suffix
    identifier = identifier.rstrip("/")
    if identifier.endswith(".git"):
        identifier = identifier[:-4]

    # Split into owner and name
    parts = identifier.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid repository identifier: {identifier}")

    return parts[0], parts[1]
