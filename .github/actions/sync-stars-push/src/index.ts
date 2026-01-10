import * as fs from "fs";
import * as yaml from "js-yaml";

interface StarEntry {
  [repo: string]: { tags: string[] };
}

interface StarsConfig {
  stars: (string | StarEntry)[];
}

interface StarList {
  id: number;
  name: string;
}

interface Repository {
  full_name: string;
  owner: { login: string };
  name: string;
}

async function main() {
  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    throw new Error("GITHUB_TOKEN environment variable is required");
  }

  const configPath = process.env.STARS_CONFIG_PATH || ".github/stars.yaml";

  // Parse stars.yaml
  console.log(`Reading config from ${configPath}...`);
  const configContent = fs.readFileSync(configPath, "utf8");
  const config = yaml.load(configContent) as StarsConfig;
  const stars = config.stars || [];

  // Get existing lists
  console.log("Fetching existing star lists...");
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
    throw new Error(
      `Failed to fetch lists: ${listsResponse.status} ${await listsResponse.text()}`
    );
  }

  const lists = (await listsResponse.json()) as StarList[];
  const listsByName = new Map(lists.map((l) => [l.name, l]));

  // Build desired state: { listName: [repos] }
  const desired = new Map<string, string[]>();

  for (const entry of stars) {
    let repo: string;
    let tags: string[];

    if (typeof entry === "string") {
      repo = entry;
      tags = [];
    } else {
      repo = Object.keys(entry)[0];
      tags = entry[repo]?.tags || [];
    }

    for (const tag of tags) {
      if (!desired.has(tag)) {
        desired.set(tag, []);
      }
      desired.get(tag)!.push(repo);
    }
  }

  // Sync each list
  for (const [listName, repos] of desired.entries()) {
    console.log(`\nProcessing list: ${listName}`);

    // Create list if it doesn't exist
    let list = listsByName.get(listName);
    if (!list) {
      console.log(`  Creating list: ${listName}`);
      const createResponse = await fetch(
        "https://api.github.com/user/starred/lists",
        {
          method: "POST",
          headers: {
            Accept: "application/vnd.github+json",
            Authorization: `Bearer ${token}`,
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name: listName }),
        }
      );

      if (!createResponse.ok) {
        throw new Error(
          `Failed to create list: ${createResponse.status} ${await createResponse.text()}`
        );
      }

      list = (await createResponse.json()) as StarList;
    }

    // Get current repos in list
    const listReposResponse = await fetch(
      `https://api.github.com/user/starred/lists/${list.id}/repositories`,
      {
        headers: {
          Accept: "application/vnd.github+json",
          Authorization: `Bearer ${token}`,
          "X-GitHub-Api-Version": "2022-11-28",
        },
      }
    );

    if (!listReposResponse.ok) {
      throw new Error(
        `Failed to fetch list repos: ${listReposResponse.status}`
      );
    }

    const currentRepos = (await listReposResponse.json()) as Repository[];
    const currentSet = new Set(currentRepos.map((r) => r.full_name));
    const desiredSet = new Set(repos);

    // Add missing repos
    for (const repo of repos) {
      if (!currentSet.has(repo)) {
        const [owner, name] = repo.split("/");
        console.log(`  Adding: ${repo}`);
        try {
          const addResponse = await fetch(
            `https://api.github.com/user/starred/lists/${list.id}/repositories/${owner}/${name}`,
            {
              method: "PUT",
              headers: {
                Accept: "application/vnd.github+json",
                Authorization: `Bearer ${token}`,
                "X-GitHub-Api-Version": "2022-11-28",
              },
            }
          );

          if (!addResponse.ok) {
            console.log(
              `  Warning: Could not add ${repo} - ${addResponse.status}`
            );
          }
        } catch (e) {
          console.log(`  Warning: Could not add ${repo} - ${e}`);
        }
      }
    }

    // Remove repos no longer in list
    for (const repo of currentRepos) {
      if (!desiredSet.has(repo.full_name)) {
        console.log(`  Removing: ${repo.full_name}`);
        await fetch(
          `https://api.github.com/user/starred/lists/${list.id}/repositories/${repo.owner.login}/${repo.name}`,
          {
            method: "DELETE",
            headers: {
              Accept: "application/vnd.github+json",
              Authorization: `Bearer ${token}`,
              "X-GitHub-Api-Version": "2022-11-28",
            },
          }
        );
      }
    }
  }

  console.log("\nSync complete!");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
