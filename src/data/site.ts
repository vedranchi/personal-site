// Central site configuration. Edit this to change nav, name, and links everywhere.

export const site = {
  name: 'Vedran Chichov',
  shortName: 'Vedran',
  tagline: 'code · cycling · words',
  description:
    'Personal site of Vedran Chichov — programming projects, cycling, and a blog. ' +
    'A fresh high-school grad from Macedonia building things and riding bikes.',
  // TODO: set to the real URL once the DuckDNS subdomain is chosen (used for SEO/RSS).
  url: 'https://vedran.example.duckdns.org',
  nav: [
    { href: '/', label: 'Home' },
    { href: '/projects', label: 'Projects' },
    { href: '/cycling', label: 'Cycling' },
    { href: '/blog', label: 'Blog' },
  ],
  socials: [
    { href: 'https://github.com/vedranchi', label: 'GitHub' },
    { href: 'https://www.procyclingstats.com/rider/vedran-cicov/', label: 'ProCyclingStats' },
  ],
} as const;

export type NavItem = (typeof site.nav)[number];
