"""CLI interface for GitHub Stars Manager."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .github_api import GitHubAPIError, GitHubClient

console = Console()


def get_client() -> GitHubClient:
    """Create and return a GitHub client."""
    try:
        return GitHubClient()
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def handle_api_error(e: GitHubAPIError) -> None:
    """Handle API errors with user-friendly messages."""
    if e.status_code == 401:
        console.print("[red]Error:[/red] Invalid or expired GitHub token.")
    elif e.status_code == 403:
        console.print("[red]Error:[/red] Rate limit exceeded or insufficient permissions.")
    elif e.status_code == 404:
        console.print("[red]Error:[/red] Resource not found.")
    else:
        console.print(f"[red]Error:[/red] {e.message}")
    sys.exit(1)


@click.group()
@click.version_option(package_name="github-stars-manager")
def main():
    """GitHub Stars List Manager - Organize your starred repositories."""
    pass


# === Stars Commands ===


@main.group()
def stars():
    """Manage starred repositories."""
    pass


@stars.command("list")
@click.option("--language", "-l", help="Filter by programming language")
@click.option("--limit", "-n", type=int, help="Limit number of results")
@click.option("--archived", is_flag=True, help="Include archived repositories")
def list_stars(language: Optional[str], limit: Optional[int], archived: bool):
    """List all starred repositories."""
    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Fetching starred repositories...", total=None)
                repos = client.get_starred_repos()

            # Apply filters
            if not archived:
                repos = [r for r in repos if not r.archived]
            if language:
                repos = [r for r in repos if r.language and r.language.lower() == language.lower()]
            if limit:
                repos = repos[:limit]

            if not repos:
                console.print("[yellow]No starred repositories found.[/yellow]")
                return

            table = Table(title=f"Starred Repositories ({len(repos)})")
            table.add_column("Repository", style="cyan")
            table.add_column("Description", max_width=50)
            table.add_column("Language", style="magenta")
            table.add_column("Stars", justify="right", style="yellow")

            for repo in repos:
                desc = repo.description[:47] + "..." if repo.description and len(repo.description) > 50 else (repo.description or "")
                table.add_row(
                    repo.full_name,
                    desc,
                    repo.language or "-",
                    str(repo.stargazers_count),
                )

            console.print(table)

        except GitHubAPIError as e:
            handle_api_error(e)


@stars.command("uncategorized")
@click.option("--limit", "-n", type=int, help="Limit number of results")
def uncategorized_stars(limit: Optional[int]):
    """List starred repositories not in any list."""
    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Finding uncategorized repositories...", total=None)
                repos = client.get_uncategorized_repos()

            if limit:
                repos = repos[:limit]

            if not repos:
                console.print("[green]All repositories are categorized![/green]")
                return

            table = Table(title=f"Uncategorized Repositories ({len(repos)})")
            table.add_column("Repository", style="cyan")
            table.add_column("Description", max_width=50)
            table.add_column("Language", style="magenta")
            table.add_column("Topics", style="blue")

            for repo in repos:
                desc = repo.description[:47] + "..." if repo.description and len(repo.description) > 50 else (repo.description or "")
                topics = ", ".join(repo.topics[:3])
                if len(repo.topics) > 3:
                    topics += f" (+{len(repo.topics) - 3})"
                table.add_row(
                    repo.full_name,
                    desc,
                    repo.language or "-",
                    topics or "-",
                )

            console.print(table)

        except GitHubAPIError as e:
            handle_api_error(e)


@stars.command("add")
@click.argument("repo")
def star_repo(repo: str):
    """Star a repository. REPO should be in 'owner/name' format."""
    if "/" not in repo:
        console.print("[red]Error:[/red] Repository must be in 'owner/name' format.")
        sys.exit(1)

    owner, name = repo.split("/", 1)

    with get_client() as client:
        try:
            client.star_repo(owner, name)
            console.print(f"[green]Starred[/green] {repo}")
        except GitHubAPIError as e:
            handle_api_error(e)


@stars.command("remove")
@click.argument("repo")
def unstar_repo(repo: str):
    """Unstar a repository. REPO should be in 'owner/name' format."""
    if "/" not in repo:
        console.print("[red]Error:[/red] Repository must be in 'owner/name' format.")
        sys.exit(1)

    owner, name = repo.split("/", 1)

    with get_client() as client:
        try:
            client.unstar_repo(owner, name)
            console.print(f"[yellow]Unstarred[/yellow] {repo}")
        except GitHubAPIError as e:
            handle_api_error(e)


@stars.command("summary")
def stars_summary():
    """Show summary statistics for starred repositories."""
    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Analyzing starred repositories...", total=None)
                summary = client.get_stars_summary()

            # Summary panel
            summary_text = f"""
[bold]Total Stars:[/bold] {summary.total_stars}
[bold]Total Lists:[/bold] {summary.total_lists}
[bold]In Lists:[/bold] {summary.repos_in_lists}
[bold]Uncategorized:[/bold] {summary.repos_uncategorized}
            """.strip()
            console.print(Panel(summary_text, title="Stars Summary", border_style="blue"))

            # Top languages table
            if summary.languages:
                lang_table = Table(title="Top Languages")
                lang_table.add_column("Language", style="magenta")
                lang_table.add_column("Count", justify="right", style="cyan")

                for lang, count in list(summary.languages.items())[:10]:
                    lang_table.add_row(lang, str(count))

                console.print(lang_table)

            # Top topics table
            if summary.topics:
                topic_table = Table(title="Top Topics")
                topic_table.add_column("Topic", style="blue")
                topic_table.add_column("Count", justify="right", style="cyan")

                for topic, count in list(summary.topics.items())[:10]:
                    topic_table.add_row(topic, str(count))

                console.print(topic_table)

        except GitHubAPIError as e:
            handle_api_error(e)


# === Lists Commands ===


@main.group()
def lists():
    """Manage star lists."""
    pass


@lists.command("list")
def list_lists():
    """List all star lists."""
    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Fetching star lists...", total=None)
                star_lists = client.get_star_lists()

            if not star_lists:
                console.print("[yellow]No star lists found.[/yellow]")
                return

            table = Table(title=f"Star Lists ({len(star_lists)})")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Description", max_width=40)
            table.add_column("Repos", justify="right", style="yellow")
            table.add_column("Public", justify="center")

            for star_list in star_lists:
                desc = star_list.description[:37] + "..." if star_list.description and len(star_list.description) > 40 else (star_list.description or "")
                table.add_row(
                    str(star_list.id),
                    star_list.name,
                    desc,
                    str(star_list.repo_count),
                    "[green]Yes[/green]" if star_list.is_public else "[red]No[/red]",
                )

            console.print(table)

        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("create")
@click.argument("name")
@click.option("--description", "-d", help="List description")
@click.option("--private", is_flag=True, help="Make the list private")
def create_list(name: str, description: Optional[str], private: bool):
    """Create a new star list."""
    with get_client() as client:
        try:
            star_list = client.create_star_list(name, description, is_private=private)
            console.print(f"[green]Created list:[/green] {star_list.name} (ID: {star_list.id})")
        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("delete")
@click.argument("list_id", type=int)
@click.option("--force", "-f", is_flag=True, help="Skip confirmation")
def delete_list(list_id: int, force: bool):
    """Delete a star list by ID."""
    with get_client() as client:
        try:
            # Get list info first
            star_lists = client.get_star_lists()
            target_list = next((sl for sl in star_lists if sl.id == list_id), None)

            if not target_list:
                console.print(f"[red]Error:[/red] List with ID {list_id} not found.")
                sys.exit(1)

            if not force:
                if not click.confirm(f"Delete list '{target_list.name}' ({target_list.repo_count} repos)?"):
                    console.print("Cancelled.")
                    return

            client.delete_star_list(list_id)
            console.print(f"[red]Deleted list:[/red] {target_list.name}")

        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("show")
@click.argument("list_id", type=int)
def show_list(list_id: int):
    """Show repositories in a star list."""
    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Fetching list repositories...", total=None)
                repos = client.get_list_repos(list_id)

            if not repos:
                console.print("[yellow]No repositories in this list.[/yellow]")
                return

            table = Table(title=f"Repositories in List (ID: {list_id})")
            table.add_column("Repository", style="cyan")
            table.add_column("Description", max_width=50)
            table.add_column("Language", style="magenta")
            table.add_column("Stars", justify="right", style="yellow")

            for repo in repos:
                desc = repo.description[:47] + "..." if repo.description and len(repo.description) > 50 else (repo.description or "")
                table.add_row(
                    repo.full_name,
                    desc,
                    repo.language or "-",
                    str(repo.stargazers_count),
                )

            console.print(table)

        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("add")
@click.argument("list_id", type=int)
@click.argument("repo")
def add_to_list(list_id: int, repo: str):
    """Add a repository to a star list."""
    if "/" not in repo:
        console.print("[red]Error:[/red] Repository must be in 'owner/name' format.")
        sys.exit(1)

    owner, name = repo.split("/", 1)

    with get_client() as client:
        try:
            client.add_repo_to_list(list_id, owner, name)
            console.print(f"[green]Added[/green] {repo} to list {list_id}")
        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("remove")
@click.argument("list_id", type=int)
@click.argument("repo")
def remove_from_list(list_id: int, repo: str):
    """Remove a repository from a star list."""
    if "/" not in repo:
        console.print("[red]Error:[/red] Repository must be in 'owner/name' format.")
        sys.exit(1)

    owner, name = repo.split("/", 1)

    with get_client() as client:
        try:
            client.remove_repo_from_list(list_id, owner, name)
            console.print(f"[yellow]Removed[/yellow] {repo} from list {list_id}")
        except GitHubAPIError as e:
            handle_api_error(e)


@lists.command("update")
@click.argument("list_id", type=int)
@click.option("--name", "-n", help="New name for the list")
@click.option("--description", "-d", help="New description")
@click.option("--public/--private", default=None, help="Set visibility")
def update_list(
    list_id: int,
    name: Optional[str],
    description: Optional[str],
    public: Optional[bool],
):
    """Update a star list's properties."""
    if name is None and description is None and public is None:
        console.print("[yellow]No updates specified.[/yellow]")
        return

    with get_client() as client:
        try:
            is_private = not public if public is not None else None
            updated = client.update_star_list(
                list_id,
                name=name,
                description=description,
                is_private=is_private,
            )
            console.print(f"[green]Updated list:[/green] {updated.name}")
        except GitHubAPIError as e:
            handle_api_error(e)


# === Bulk Operations ===


@main.group()
def bulk():
    """Bulk operations for managing stars."""
    pass


@bulk.command("categorize")
@click.argument("list_id", type=int)
@click.option("--language", "-l", help="Add repos matching this language")
@click.option("--topic", "-t", help="Add repos with this topic")
@click.option("--dry-run", is_flag=True, help="Show what would be done without making changes")
def bulk_categorize(
    list_id: int,
    language: Optional[str],
    topic: Optional[str],
    dry_run: bool,
):
    """Bulk add uncategorized repositories to a list based on criteria."""
    if not language and not topic:
        console.print("[red]Error:[/red] Specify at least --language or --topic.")
        sys.exit(1)

    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Finding matching repositories...", total=None)
                uncategorized = client.get_uncategorized_repos()

            matching = []
            for repo in uncategorized:
                if language and repo.language and repo.language.lower() == language.lower():
                    matching.append(repo)
                elif topic and topic.lower() in [t.lower() for t in repo.topics]:
                    matching.append(repo)

            if not matching:
                console.print("[yellow]No matching uncategorized repositories found.[/yellow]")
                return

            console.print(f"Found {len(matching)} matching repositories:")
            for repo in matching:
                console.print(f"  - {repo.full_name}")

            if dry_run:
                console.print("\n[yellow]Dry run - no changes made.[/yellow]")
                return

            if not click.confirm(f"\nAdd {len(matching)} repositories to list {list_id}?"):
                console.print("Cancelled.")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Adding repositories...", total=len(matching))

                for repo in matching:
                    owner, name = repo.full_name.split("/", 1)
                    client.add_repo_to_list(list_id, owner, name)
                    progress.advance(task)

            console.print(f"[green]Added {len(matching)} repositories to list {list_id}.[/green]")

        except GitHubAPIError as e:
            handle_api_error(e)


@bulk.command("export")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
@click.option("--format", "fmt", type=click.Choice(["json", "csv"]), default="json", help="Output format")
def export_stars(output: Optional[str], fmt: str):
    """Export all starred repositories and their list assignments."""
    import csv
    import json

    with get_client() as client:
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                progress.add_task("Exporting starred repositories...", total=None)

                repos = client.get_starred_repos()
                star_lists = client.get_star_lists()

                # Build repo to lists mapping
                repo_lists: dict[str, list[str]] = {r.full_name: [] for r in repos}
                for star_list in star_lists:
                    list_repos = client.get_list_repos(star_list.id)
                    for repo in list_repos:
                        if repo.full_name in repo_lists:
                            repo_lists[repo.full_name].append(star_list.name)

            if fmt == "json":
                data = {
                    "exported_at": str(__import__("datetime").datetime.now().isoformat()),
                    "total_stars": len(repos),
                    "lists": [
                        {"name": sl.name, "id": sl.id, "description": sl.description}
                        for sl in star_lists
                    ],
                    "repositories": [
                        {
                            "full_name": r.full_name,
                            "description": r.description,
                            "language": r.language,
                            "topics": r.topics,
                            "stars": r.stargazers_count,
                            "lists": repo_lists.get(r.full_name, []),
                            "archived": r.archived,
                            "url": r.html_url,
                        }
                        for r in repos
                    ],
                }
                content = json.dumps(data, indent=2)
            else:  # csv
                import io
                buffer = io.StringIO()
                writer = csv.writer(buffer)
                writer.writerow(["full_name", "description", "language", "topics", "stars", "lists", "archived", "url"])
                for r in repos:
                    writer.writerow([
                        r.full_name,
                        r.description or "",
                        r.language or "",
                        ";".join(r.topics),
                        r.stargazers_count,
                        ";".join(repo_lists.get(r.full_name, [])),
                        r.archived,
                        r.html_url,
                    ])
                content = buffer.getvalue()

            if output:
                with open(output, "w") as f:
                    f.write(content)
                console.print(f"[green]Exported to:[/green] {output}")
            else:
                console.print(content)

        except GitHubAPIError as e:
            handle_api_error(e)


if __name__ == "__main__":
    main()
