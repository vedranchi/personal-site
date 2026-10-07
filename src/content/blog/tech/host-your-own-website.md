---
title: Put Your Own Website Online, on Your Own Domain
description: How a website gets from your laptop to yourname.com — static sites, Git, automatic deploys and DNS, explained with the setup behind this very blog.
pubDate: 2026-10-03
tags:
  - tech
  - web
draft: true
---

Ever wondered what it actually takes to have your own website at your own address? Not a profile on someone else's platform, but _yourname.com_ — something you built, that loads for anyone in the world.

It's a lot less than you'd think. The site you're reading right now costs me the price of a domain name each year, and nothing else. Every time I save a change and push it, it's live a minute later — no servers to babysit, no FTP, no manual uploads.

<!-- VEDRAN: one or two sentences on why you wanted your own site in the first place. -->

In this post I'll walk you through the whole path, from a folder on your laptop to a live site on your own domain — and then a second site on a subdomain, the way this blog lives at `blog.vchichov.com` next to my portfolio at `vchichov.com`. I'll explain each idea in general terms first, and then show how I did it. I use **Astro**, **GitHub**, **Vercel** and **Namecheap**, but every one of them has alternatives, and the ideas carry over.

## Prerequisites

1. **A GitHub account** — free. This is where your site's code will live.

2. **Node.js 22 or newer** — the tool that builds the site on your computer. Install the LTS version from nodejs.org.

3. **A code editor** — VS Code is a good default.

4. **About $10–15 a year for a domain** — optional until the last steps; everything before that works on a free address.

5. **Basic comfort with a terminal** — you'll type a handful of commands, and I'll show every one of them.

## The big picture

Before touching anything, it helps to know which pieces exist and what each one is responsible for. There are four:

1. **The site itself.** A _static site_ is just a folder of HTML, CSS, JavaScript and images, built ahead of time. There's no database and no code running on a server when someone visits — the server only hands out files. That's why it can be fast, secure and free to host.

2. **A Git host** (GitHub). It keeps your code and its full history, and it's the thing the hosting platform watches for changes.

3. **A hosting platform** (Vercel). It notices every push to GitHub, builds your site, and puts the result on servers all around the world. This is called _continuous deployment_.

4. **A domain and DNS** (Namecheap). The domain is the name you rent; DNS is the internet's phone book that tells browsers which servers answer for that name.

Put together, the flow looks like this:

```text
your laptop ──git push──▶ GitHub ──notifies──▶ Vercel ──builds & serves──▶ visitors
                                                  ▲
                         yourname.com ──DNS───────┘
```

Once it's set up, your whole job is the left side: write, commit, push.

## Step 1: Build a static site

You can write the HTML by hand, but a _static site generator_ makes life much easier: you write pages and Markdown posts, and it turns them into plain HTML for you. I use [Astro](https://astro.build); Hugo, Eleventy and Jekyll do the same job.

Create a new project:

```bash
npm create astro@latest my-site
cd my-site
npm run dev
```

Open `http://localhost:4321` and you'll see your site, reloading every time you save a file. When you're happy, build it for real:

```bash
npm run build
```

This creates a `dist/` folder. **That folder is your entire website** — those are the files that will be served to visitors. Everything else in the project is just the recipe for making them.

<!-- VEDRAN: optional — a line about what your first version looked like. -->

## Step 2: Put it on GitHub

Create an empty repository on GitHub (the **New repository** button — don't add a README, since you already have files). Then connect your project to it and push:

```bash
git init
git add .
git commit -m "First version of my site"
git branch -M main
git remote add origin git@github.com:YOUR-USERNAME/my-site.git
git push -u origin main
```

Astro already includes a `.gitignore` that keeps `node_modules/` and `dist/` out of Git. That's on purpose: the hosting platform builds `dist/` itself, so you only ever commit the recipe, never the output.

> If your repository is public, remember that _everything_ you commit is public — forever, even if you delete it later. Never commit passwords, API keys or private information.

## Step 3: Deploy with Vercel

Sign in to [Vercel](https://vercel.com) with your GitHub account, click **Add New → Project**, and import your repository. Vercel recognises Astro and fills in the settings for you:

- **Build command:** `npm run build`
- **Output directory:** `dist`

Click **Deploy**, wait a minute, and you get a live address like `my-site.vercel.app`. Your site is on the internet.

From now on, two things happen automatically:

- **Every push to `main` deploys to production.** Change a file, push, and it's live.
- **Every pull request gets its own preview URL.** You can look at a change on a real deployment before it goes live — and share the link with a friend for feedback.

> Don't panic if a preview link sends you to a Vercel login page. Previews are protected by default so only you can see them — it's a gate, not a broken build.

Vercel's free _Hobby_ plan covers personal, non-commercial sites like this one. Netlify, Cloudflare Pages and GitHub Pages all work the same way, with small differences.

## Step 4: Get a domain

`my-site.vercel.app` works, but a domain of your own is what makes the site yours. You buy one from a _registrar_ — I use Namecheap; Cloudflare and Porkbun are also popular.

A few things worth knowing before you pay:

- **Check the renewal price, not just the first year.** Many domains are cheap for year one and cost more afterwards.
- **Make sure WHOIS privacy is included,** so your name and address don't end up in a public database. Most good registrars include it for free.
- **Skip the upsells.** You don't need their hosting, email or website builder — Vercel is your host.

<!-- VEDRAN: what you paid for vchichov.com, roughly, and why you picked the name. -->

## Step 5: Point your domain at your site

This is the step that feels like magic the first time, so let's go slowly.

### How DNS works, briefly

When someone types `yourname.com`, their browser asks DNS: _which server answers for this name?_ You answer that question by adding **records** at your registrar. Two kinds matter here:

- An **A record** points a name at an IP address — a server's numeric address.
- A **CNAME record** points a name at _another name_, and lets that name's owner decide the address. If Vercel moves its servers, your site keeps working without you changing anything.

There's one catch: the bare domain (`yourname.com`, called the _apex_ or _root_) can't be a CNAME — that's a rule of DNS itself. So the apex usually gets an A record, and subdomains like `www` get CNAMEs. (Some DNS providers work around this with record types called ALIAS or ANAME.)

### Doing it

1. In Vercel, open your project → **Settings → Domains** and add `yourname.com`. Vercel will offer to add `www.yourname.com` too and redirect one to the other — say yes.

2. Vercel now shows you the exact records to create. **Copy the values from there**, not from a blog post (including this one) — they can differ between projects and change over time.

3. At your registrar, open the DNS settings. On Namecheap, that's **Domain List → Manage → Advanced DNS**. Add the records Vercel asked for — typically an A record with host `@` (which means the apex) and a CNAME with host `www`. Delete any default "parking page" records the registrar added, or they'll fight with yours.

4. Wait. DNS changes usually show up within minutes, but can take up to a couple of days to reach everyone. Vercel's Domains page turns green once it can see your records.

You can check from your own terminal what the world currently sees:

```bash
dig +short yourname.com
dig +short www.yourname.com
```

<!-- VEDRAN: how long it actually took for yours, and anything that confused you. -->

### Pick one address

`yourname.com` and `www.yourname.com` are technically two different addresses. Pick one as the real one and redirect the other to it, so search engines don't see two copies of your site. I went with the apex — `vchichov.com` — and `www.vchichov.com` redirects there.

And HTTPS? You don't have to do anything. Vercel requests a certificate for your domain automatically once DNS is in place, and keeps renewing it. The padlock just appears.

## Step 6: Tell your site its own address

Your site needs to know its own URL — for the sitemap that search engines read, for the RSS feed, and for the _canonical_ link that tells Google which address is the real one. In Astro, that's one line in `astro.config.mjs`:

```js
export default defineConfig({
  site: 'https://yourname.com',
});
```

The lesson I learned the hard way: **write your address in exactly one place,** and make everything else read it from there. I once had the old address written by hand into a `robots.txt` file. When the site moved, that file kept sending search engines to a dead address for weeks before anyone noticed. Now `robots.txt` is generated from the same `site` setting as everything else, so it can't go stale.

## Step 7: Add a second site on a subdomain

Once one site works, a second one is mostly repetition. This blog is a separate site from my portfolio, with its own look, living at `blog.vchichov.com`. Here's how a subdomain like that works:

1. **Create a second Vercel project.** It can come from a different repository — or, as in my case, from the same one with different settings. Mine builds both sites from one repo; the blog project just uses a different build command and output folder.

2. **Add the subdomain to the new project** in **Settings → Domains**: `blog.yourname.com`.

3. **Add a CNAME record at your registrar,** with host `blog`, pointing to the target Vercel shows you. Your main site's records don't change at all — each name is answered separately.

That's the beauty of DNS: `yourname.com`, `www.yourname.com` and `blog.yourname.com` are independent entries, so each one can point somewhere completely different.

One gotcha from my own setup: when you override the build command in Vercel, it runs exactly what you type. My blog's first deploy failed because I'd entered `astro build:blog` instead of `npm run build:blog` — Astro didn't recognise the command, printed its help text, and the build produced nothing. If a deploy "succeeds" but the site is empty or 404s, check the build command and output directory first.

## When something doesn't work

- **Vercel says "Invalid Configuration" on your domain.** Your DNS records don't match what it asked for yet. Double-check them, delete leftover parking records, and give it time.
- **The domain works but `www` doesn't (or the other way round).** You've only added a record for one of them.
- **The site loads but shows a 404.** The output directory is probably wrong — it has to match the folder your build creates.
- **A preview link asks you to log in.** That's deployment protection doing its job.

## What it costs

| Piece             | Cost             |
| ----------------- | ---------------- |
| Astro             | free             |
| GitHub            | free             |
| Vercel (Hobby)    | free             |
| HTTPS certificate | free, automatic  |
| Domain            | ~$10–15 per year |

## Wrapping up

That's the whole journey: a folder of files, a Git repository, a platform that builds and serves it on every push, and a few DNS records that give it a name. Once it's set up, publishing is just writing and pushing — which is exactly how this post got here.

<!-- VEDRAN: a closing line in your own voice — what you'd tell someone about to try this, and maybe a link to your home-server post once it's published. -->
