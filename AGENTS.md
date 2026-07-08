# Project rules — personal-site

Vedran Chichov's personal site: programming projects, cycling, and a blog. Astro static
site with a cozy _Stardew Valley_ pixel theme ("tasteful pixel accents": pixel headings,
readable body). See the plan/memory for full context.

## Git & review (hard rules)

- Work on feature branches named `feat/<milestone>` — one per milestone.
- Commit locally as you go. **Never `git push` or merge to `main` without asking for a
  review first.** `main` is the deploy trigger.
- When in doubt about anything, ask before proceeding — resolve it together.
- Remote: `git@github.com:vedranchi/personal-site.git`.

## Deploy safety (hard rule)

- The target Ubuntu VM also hosts Vedran's **café POS** project. Any deploy or VM change
  must be strictly **additive and non-destructive** — inspect the existing nginx config
  first and verify the POS still works before/after. Never assume; confirm.

## Conventions

- **No external CDNs.** Self-host everything (fonts via `@fontsource/*`, images bundled)
  so the built site has no runtime third-party dependencies.
- **Content lives in fixed places:** blog posts = Markdown in `src/content/blog/` (an
  Obsidian vault); projects in `src/content/projects/`; cycling data is generated to
  `src/data/cycling.json` by `scripts/scrape_pcs.py` (never hand-edit that file).
- **Design:** readable body text always, support light ("day farm") and dark ("night
  farm") modes, keep everything responsive/mobile-friendly.
- Astro is pinned to `^7.0.6` — `create-astro` wrongly scaffolds a nonexistent `^7.0.7`.

## Workflow

- Dev server: `astro dev --background`; manage with `astro dev stop | status | logs`.
- Before committing, run `npm run format` and `npm run check` (both must be clean).
