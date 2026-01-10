import * as fs from "fs";

interface StarList {
  id: number;
  name: string;
}

interface Repository {
  full_name: string;
  repo?: { full_name: string };
}

interface StarEntry {
  [repo: string]: { tags: string[] };
}

async function fetchAllPages<T>(
  url: string,
  token: string,
  headers: Record<string, string> = {}
): Promise<T[]> {
  const results: T[] = [];
  let nextUrl: string | null = url;

  while (nextUrl) {
    const response = await fetch(nextUrl, {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28",
        ...headers,
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch: ${response.status}`);
    }

    const data = (await response.json()) as T[];
    results.push(...data);

    // Parse Link header for next page
    const linkHeader = response.headers.get("Link");
    nextUrl = null;
    if (linkHeader) {
      const match = linkHeader.match(/<([^>]+)>;\s*rel="next"/);
      if (match) {
        nextUrl = match[1];
      }
    }
  }

  return results;
}

async function main() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is required");
  }

  const configPath = process.env.STARS_CONFIG_PATH || ".github/stars.yaml";

  // Fetch all starred repos
  console.log("Fetching starred repos...");
  const starred = await fetchAllPages<Repository>(
    "https://api.github.com/user/starred?per_page=100",
    token,
    { Accept: "application/vnd.github.star+json" }
  );
  console.log(`Found ${starred.length} starred repos`);

  // Fetch all lists
  console.log("Fetching star lists...");
  const listsResponse = await fetch(
    "https://api.github.com/user/starred/lists",
    {
      headers: {
        Accept: "application/vnd.github+json",
        Authorization: `Bearer ${token}`,
        "X-GitHub-Api-Version": "2022-11-28",
      },
    }
  );

  if (!listsResponse.ok) {
    throw new Error(`Failed to fetch lists: ${listsResponse.status}`);
  }

  const lists = (await listsResponse.json()) as StarList[];
  console.log(`Found ${lists.length} lists`);

  // Build repo -> tags mapping
  const repoTags = new Map<string, string[]>();
  for (const item of starred) {
    const repoName = item.repo?.full_name || (item as { full_name: string }).full_name;
    repoTags.set(repoName, []);
  }

  // Fetch repos in each list
  for (const list of lists) {
    console.log(`Fetching repos in list: ${list.name}`);
    const listRepos = await fetchAllPages<Repository>(
      `https://api.github.com/user/starred/lists/${list.id}/repositories?per_page=100`,
      token
    );

    for (const repo of listRepos) {
      const fullName = repo.full_name;
      if (repoTags.has(fullName)) {
        repoTags.get(fullName)!.push(list.name);
      }
    }
  }

  // Build YAML structure
  const stars: (string | StarEntry)[] = [];

  // Group by tags for cleaner output
  const byTags = new Map<string, string[]>();
  const untagged: string[] = [];

  for (const [repo, tags] of repoTags.entries()) {
    if (tags.length === 0) {
      untagged.push(repo);
    } else {
      const key = tags.sort().join(",");
      if (!byTags.has(key)) {
        byTags.set(key, []);
      }
      byTags.get(key)!.push(repo);
    }
  }

  // Add tagged repos first, grouped by tag combination
  const sortedTagKeys = Array.from(byTags.keys()).sort();
  for (const tagKey of sortedTagKeys) {
    const tags = tagKey.split(",");
    const repos = byTags.get(tagKey)!.sort();
    for (const repo of repos) {
      stars.push({ [repo]: { tags } });
    }
  }

  // Add untagged repos at the end
  for (const repo of untagged.sort()) {
    stars.push(repo);
  }

  // Write YAML
  const lines = [
    "# GitHub Stars List Configuration",
    "# Auto-generated from GitHub API",
    "# Format:",
    '#   - "owner/repo"                    # Just starred, no lists',
    '#   - "owner/repo":',
    "#       tags: [list1, list2]          # Assign to these lists",
    "",
    "stars:",
  ];

  for (const entry of stars) {
    if (typeof entry === "string") {
      lines.push(`  - "${entry}"`);
    } else {
      const repo = Object.keys(entry)[0];
      const tags = entry[repo].tags;
      lines.push(`  - "${repo}":`);
      lines.push(`      tags: [${tags.join(", ")}]`);
    }
  }

  const content = lines.join("\n") + "\n";
  fs.writeFileSync(configPath, content);
  console.log(`\nWrote ${stars.length} repos to ${configPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
