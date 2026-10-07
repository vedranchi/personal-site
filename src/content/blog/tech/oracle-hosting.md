---
title: How to Host your Projects for Free with Oracle Cloud
description: Set up an Oracle Cloud Always Free VM and deploy your own websites, API's and services.
pubDate: 2026-10-03
tags:
  - tech
draft: true
---

So you've built something with a backend, an API, a web app with a database, a bot, and now you want it online. Static hosts like Vercel or Netlify are perfect for websites made of plain files, but the moment you need a server that runs your code and keeps a database, you need a machine of your own.

The good news: Oracle Cloud gives you an always free VM that runs as long as you are using it.

That's exactly how I am hosting _Glucoread_: a Django web app with a Postgres database, running on a free Oracle VM, on its own domain, with automatic HTTPS, automatic deploys and nightly backups. In this post I'll show you how to set up the same thing for your own project.

<!-- VEDRAN: one or two sentences on what GlucoRead is and why you didn't just use a paid host. -->

## Prerequisites

1. **An Oracle Cloud account** — free, but it asks for a credit card to verify you're a real person. Always Free resources don't charge it.

2. **A project that runs in Docker** — or the willingness to write a `Dockerfile` for it. Any language works; mine is Python.

3. **An SSH client** — built into the terminal on macOS and Linux, and into Windows 10 and newer.

4. **A domain name** — optional. You can start with a free subdomain from DuckDNS for example.

5. **Some Linux command line basics** — moving around folders, editing a file.

## What you get for free

Oracle's Always Free tier includes two kinds of virtual machines:

- **AMD micro instances** (`VM.Standard.E2.1.Micro`) — up to two of them, each with 1 GB of RAM. Small, but enough for a web app and its database if you're careful. Glucoread runs on one of these.
- **Ampere ARM instances** (`VM.Standard.A1.Flex`) — up to 4 CPU cores and 24 GB of RAM in total, which you can split across several VMs. Far more powerful, but often "out of capacity" in popular regions.

On top of that you get around 200 GB of disk and plenty of outgoing traffic each month. Oracle changes these limits from time to time, so check their Always Free page for the current numbers.

Two things worth knowing before you sign up:

- **Your home region is permanent.** Pick one close to your users — and, if you want an ARM machine, ideally one that isn't overcrowded.
- **Idle machines can be reclaimed.** Oracle may take back Always Free instances that sit almost completely unused for a week. A real app with real traffic is fine; a VM you created and forgot about may not be.

## The big picture

Here's everything that will run on the VM:

```text
Internet ──443──▶ Caddy ──▶ your app ──▶ database
                  (HTTPS)    (container)   (container)
```

- **Docker Compose** runs all three pieces as containers, described in one file. The whole setup lives in your Git repository, so you can rebuild it anywhere.
- **Caddy** is the only thing the internet can talk to. It's a web server that gets an HTTPS certificate for your domain automatically and passes requests on to your app.
- **Your app** listens only inside Docker's private network.
- **The database** isn't reachable from outside at all — only your app can talk to it.

## Step 1: Create the VM

In the Oracle Cloud console, go to **Compute → Instances → Create instance**:

1. **Image:** Ubuntu (the latest LTS).
2. **Shape:** pick an Always Free one — look for the "Always Free-eligible" label. I use `VM.Standard.E2.1.Micro`.
3. **SSH keys:** let Oracle generate a key pair and **download the private key** — you won't be able to get it again. Or upload the public key of one you already have.
4. Click **Create** and wait for the instance to turn green.

Then give it an address that doesn't change: by default, the public IP can change when the VM is stopped and started. Under **Networking → Reserved public IPs**, reserve one and attach it to the instance.

Now connect to it:

```bash
chmod 600 ~/Downloads/ssh-key.key
ssh -i ~/Downloads/ssh-key.key ubuntu@YOUR-VM-IP
```

You're in. Update the system before anything else:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Add swap (on a 1 GB machine)

With only 1 GB of RAM, a web app, a database and a web server leave very little headroom, and running out of memory kills processes without asking. _Swap_ is disk space the system can use as emergency memory — slow, but much better than a crash:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
sudo sysctl -w vm.swappiness=10
```

The last line tells Linux to use swap only when it really has to — a safety net, not a habit. If you got a big ARM machine, you can skip this step.

## Step 3: Open the ports — both firewalls

This is the step that trips up almost everyone on Oracle, so read it carefully. **There are two firewalls between the internet and your VM,** and you have to open both.

**Firewall 1 — Oracle's network.** In the console, open your instance's **Virtual Cloud Network → Security Lists → Default Security List** and add two ingress rules: source `0.0.0.0/0`, TCP, destination port **80**, and the same for port **443**. Port 22 (SSH) is already open.

**Firewall 2 — the VM itself.** Oracle's Ubuntu images come with `iptables` rules that reject everything except SSH, _even after_ you've opened the ports above. Add rules that allow web traffic, above the rule that rejects it:

```bash
sudo iptables -I INPUT 6 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

Check the order with `sudo iptables -L INPUT --line-numbers` — your two `ACCEPT` rules must appear above the `REJECT` one, because rules are checked from the top.

<!-- VEDRAN: how long you spent wondering why the site didn't load before finding the second firewall, if that happened. -->

## Step 4: Install Docker

Docker's official script installs everything, including Compose:

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker "$USER"
```

Log out and back in so the second line takes effect, then check that it works with `docker run hello-world`.

## Step 5: Point a domain at the VM

Your app needs a name, and Caddy needs one to get an HTTPS certificate. There are two options:

- **Free: DuckDNS.** Sign in at duckdns.org, create a subdomain like `myapp.duckdns.org`, and set it to your VM's IP. That's it — no purchase needed. This is how GlucoRead started.
- **Your own domain.** At your registrar, add an **A record** for your domain pointing at the VM's IP, and another one for `www` (or a CNAME from `www` to the domain).

Because you reserved the IP in Step 1, you only have to do this once. Check that the world can see it:

```bash
dig +short yourdomain.com
```

It should print your VM's IP. DNS changes can take a little while to spread, so be patient.

## Step 6: Describe your app with Docker Compose

Now the main part. Clone your project onto the VM:

```bash
sudo mkdir -p /opt/myapp && sudo chown "$USER" /opt/myapp
git clone https://github.com/YOUR-USERNAME/myapp.git /opt/myapp
cd /opt/myapp
```

Your repository needs three things. First, a `docker-compose.yml` that describes all three containers:

```yaml
services:
  db:
    image: postgres:17
    env_file: .env
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U $${POSTGRES_USER}']
      interval: 5s
      retries: 12
    restart: unless-stopped

  app:
    build: .
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
    expose:
      - '8000'
    restart: unless-stopped

  caddy:
    image: caddy:2
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - ./caddy:/etc/caddy:ro
      - caddy_data:/data
      - caddy_config:/config
    restart: unless-stopped

volumes:
  db_data:
  caddy_data:
  caddy_config:
```

A few details in there matter more than they look:

- **Only Caddy has `ports`.** The app uses `expose`, which makes it reachable by the other containers but not from the internet. The database has neither.
- **The healthcheck** makes the app wait until Postgres is actually ready to accept connections, not just started. Without it, a small VM booting up can start your app before the database is ready, and it will crash and restart in a loop.
- **Volumes** keep your data when containers are recreated. `db_data` is your database — never delete it.
- **`restart: unless-stopped`** brings everything back after a reboot.

Second, a `caddy/Caddyfile`. This is the entire web server config:

```text
yourdomain.com {
	encode gzip zstd
	reverse_proxy app:8000
}

www.yourdomain.com {
	redir https://yourdomain.com{uri} permanent
}
```

That's really it. Caddy sees the domain name, asks Let's Encrypt for a certificate, renews it forever, and sends every request to your app.

Third, a `.env` file with your secrets — database password, secret keys, and so on:

```bash
POSTGRES_DB=myapp
POSTGRES_USER=myapp
POSTGRES_PASSWORD=a-long-random-password
```

**Never commit `.env` to Git.** Add it to `.gitignore` and create it by hand on the VM. If your repository is public — like mine — everything in it is public forever.

Now start it all up:

```bash
docker compose up -d --build
docker compose logs -f caddy
```

Watch Caddy's logs as it gets your certificate. When it's done, open `https://yourdomain.com` — your app is live, with a padlock.

## Step 7: Deploy updates

The simplest way to deploy a change is to log in and rebuild:

```bash
cd /opt/myapp
git pull
docker compose up -d --build
```

Compose only recreates the containers that actually changed, so this is safe to run any time.

That's how I started too, but I ran into a problem: **building on a 1 GB VM is painfully slow.** A full build of GlucoRead took almost eight minutes, next to the live database, with long silent stretches that looked like it had frozen. A couple of times I gave up on one halfway — and an abandoned build leaves the _old_ version running, so a change I thought was deployed sat there unshipped for days.

The fix is to build somewhere else. GitHub Actions gives you free build machines with 4 cores: on every push it builds the image and publishes it to GitHub's container registry (GHCR). The VM only has to download the finished image. In `docker-compose.yml`, the app then points at that image instead of building:

```yaml
app:
  image: ghcr.io/YOUR-USERNAME/myapp:latest
```

And deploying becomes:

```bash
docker compose pull && docker compose up -d
```

You can even let the VM do this by itself: a small timer that runs those two commands every few minutes deploys your app on its own whenever a new image appears. I like this _pull-based_ approach because GitHub never needs a way into the VM — no SSH keys stored in GitHub, no extra ports open.

<!-- VEDRAN: decide how deep to go here. GlucoRead's version is a systemd timer + deploy/redeploy.sh (fast-forwards the config, reloads Caddy). Could be its own follow-up post. -->

## Step 8: Back up your database

If you take one thing from this post, take this one: **your data lives on one disk, on one machine.** If the VM is lost, or one wrong command deletes the volume, it's gone. Set up backups _before_ you have data worth losing.

The simplest backup is a daily database dump. Postgres can make one from inside its container:

```bash
mkdir -p /opt/myapp/backups
docker compose exec -T db pg_dump -U myapp myapp | gzip > backups/myapp-$(date +%F).sql.gz
```

Put that in a script and schedule it with `crontab -e`, for example every night at 03:30:

```text
30 3 * * * cd /opt/myapp && ./backup.sh >> /var/log/myapp-backup.log 2>&1
```

Three lessons I learned along the way:

1. **Check every backup before you trust it.** A dump that failed halfway still leaves a file. My script checks that the file is valid and complete before it deletes any older backups — otherwise one bad night could replace good backups with a broken one.
2. **Keep a copy somewhere else.** Backups on the same VM don't help if you lose the VM. GlucoRead's backups are also copied to a Backblaze B2 storage bucket, and pulled down to my laptop.
3. **Practise restoring.** A backup you've never restored is just a file you hope works. Restore one into a separate test database once in a while and check that the data is really there.

## Gotchas I ran into

- **The certificate won't issue.** Ports 80 and 443 aren't reachable. Check _both_ firewalls from Step 3, and that your domain points at the right IP.
- **A `$` in `.env` silently disappears.** Compose reads `$` as the start of a variable and swaps it for an empty string — so your app runs with a different password than the one in the file. Write a literal `$` as `$$`. Randomly generated secret keys are the usual victims.
- **Changing `.env` doesn't apply after a restart.** Environment files are read when a container is _created_, so `docker compose restart` keeps the old values. Use `docker compose up -d --force-recreate app` instead.
- **Logs slowly eat the disk.** Docker keeps container logs forever by default. Limit them per service with a `logging` block (`max-size: "10m"`, `max-file: "3"`).
- **Mount config folders, not single files.** I once mounted the `Caddyfile` itself into the container. Because `git pull` replaces files rather than editing them, the container kept reading the _old_ file after every update, and my changes never took effect. Mounting the folder that contains it fixes this.

## What it costs

| Piece                   | Cost                   |
| ----------------------- | ---------------------- |
| Oracle Always Free VM   | free                   |
| Docker, Caddy, Postgres | free                   |
| HTTPS certificate       | free, automatic        |
| GitHub Actions + GHCR   | free for public repos  |
| DuckDNS subdomain       | free                   |
| Your own domain         | optional, ~$10–15/year |

## Wrapping up

That's the whole setup: one free VM, two firewalls opened, Docker Compose running your app, its database and Caddy, and a few lines of config for HTTPS. Add automatic deploys and backups, and you have something that runs on its own — which is exactly what GlucoRead has been doing.

<!-- VEDRAN: closing line in your own voice — how long GlucoRead has been running like this, and a link to glucoread.com if you want readers to see it. -->
