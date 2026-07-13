// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

import remarkWikilinks from './src/lib/remark-wikilinks.mjs';
import { site } from './src/data/site.ts';

// https://astro.build/config
export default defineConfig({
  site: site.url,
  integrations: [sitemap()],
  markdown: {
    // Obsidian [[wiki links]] -> /blog/<slug>. See src/lib/remark-wikilinks.mjs.
    remarkPlugins: [remarkWikilinks],
  },
});
