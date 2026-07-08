// @ts-check
import { defineConfig } from 'astro/config';

import remarkWikilinks from './src/lib/remark-wikilinks.mjs';
import { site } from './src/data/site.ts';

// https://astro.build/config
export default defineConfig({
  site: site.url,
  markdown: {
    // Obsidian [[wiki links]] -> /blog/<slug>. See src/lib/remark-wikilinks.mjs.
    remarkPlugins: [remarkWikilinks],
  },
});
