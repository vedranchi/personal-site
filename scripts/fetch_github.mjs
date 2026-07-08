#!/usr/bin/env node
// Fetch public repos for a GitHub user and write them to src/data/projects.json.
// Runs locally (`npm run sync:projects`) and in CI. Honors GITHUB_TOKEN if set
// (higher rate limit); works unauthenticated for public data too.

import { writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const USER = process.env.GITHUB_USER ?? 'vedranchi';
const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT = join(__dirname, '..', 'src', 'data', 'projects.json');

const headers = {
  Accept: 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'User-Agent': `${USER}-portfolio-site`,
};
if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;

const res = await fetch(
  `https://api.github.com/users/${USER}/repos?per_page=100&sort=updated&type=owner`,
  { headers },
);
if (!res.ok) {
  throw new Error(`GitHub API ${res.status} ${res.statusText}: ${await res.text()}`);
}
const repos = await res.json();

const projects = repos
  // Showcase = the user's own, visible work.
  .filter((r) => !r.fork && !r.archived && !r.private)
  .map((r) => ({
    name: r.name,
    description: r.description ?? '',
    url: r.html_url,
    homepage: r.homepage || null,
    language: r.language ?? null,
    topics: r.topics ?? [],
    stars: r.stargazers_count ?? 0,
    updatedAt: r.pushed_at,
  }))
  // Most recently worked-on first.
  .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));

const payload = {
  generatedAt: new Date().toISOString(),
  user: USER,
  projects,
};

await mkdir(dirname(OUT), { recursive: true });
await writeFile(OUT, JSON.stringify(payload, null, 2) + '\n');
console.log(`Wrote ${projects.length} project(s) for @${USER} to ${OUT}`);
