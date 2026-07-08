# portfolio-site

Vladimir's personal site — programming projects, cycling, and a blog. Cozy
_Stardew Valley_-style pixel theme, built with [Astro](https://astro.build).

## Tech at a glance

- **Astro** static site (no runtime backend).
- **Content**: blog posts are Markdown files written in **Obsidian** (the vault
  lives in `src/content/blog/`); projects live in `src/content/projects/`.
- **Cycling**: a Python scraper (`scripts/scrape_pcs.py`) pulls results from
  [procyclingstats.com](https://www.procyclingstats.com) into
  `src/data/cycling.json`, which the site reads at build time.
- **Hosting**: self-hosted on an Ubuntu VM behind nginx; auto-deployed from
  `main` via GitHub Actions.

## Commands

| Command           | Action                                   |
| :---------------- | :--------------------------------------- |
| `npm install`     | Install dependencies                     |
| `npm run dev`     | Start the dev server at `localhost:4321` |
| `npm run build`   | Build the production site to `./dist/`   |
| `npm run preview` | Preview the production build locally     |
| `npm run check`   | Type-check the project (`astro check`)   |
| `npm run format`  | Format all files with Prettier           |

## Project structure

```text
src/
├─ layouts/      # shared page shells
├─ components/   # reusable pixel-theme UI pieces
├─ pages/        # routes (index, projects, cycling, blog)
├─ content/      # blog/ (Obsidian vault) and projects/
├─ data/         # cycling.json (generated) + site config
├─ styles/       # design tokens + global styles
└─ assets/       # fonts, pixel art
scripts/         # scrape_pcs.py and helpers
```

## Git workflow

Work happens on feature branches (`feat/...`); finished, reviewed work merges to
`main`. Pushing `main` triggers a deploy. **Nothing is pushed without a review.**

## Writing a blog post (Obsidian)

_Documented in Milestone 3 once the Obsidian loader is wired up._
