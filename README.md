# Five Chambers

A personal site — a hive of five obsessions: Buddhist youth (Sangha), LGBTQ+ advocacy (Pride), tea-zen (Tea), automotive data (Data), and solo road trips (Travel).

**Live:** https://fivechambers.netlify.app

## Repo map

```
site/                  ← THE SITE. Netlify publishes this folder.
  index.html           ← one-page main site (self-contained CSS/JS)
  sangha.html  pride.html  tea.html  data.html  travel.html   ← chamber pages
  tasmania.html  china.html  new-zealand.html                 ← trip pages (route map + gallery)
  chamber.css          ← shared styles for chamber + trip pages
  content/*.json       ← content data (Road Log, Trip Gallery, chamber photos)
  admin/               ← Decap CMS panel — reachable at /admin
  photos/              ← image storage
  netlify.toml         ← build config (publish = ".")
README.md              ← this file
```

> **History note.** An earlier hardcoded copy of the site lived at the repo root (`index.html`, `chamber.css`, the five chamber pages, and a stray `photos` file). Those were removed so there is exactly one source of truth — editing them never changed the live site anyway. They remain in git history if ever needed: `git show <commit>:index.html`.

## Deploy

Netlify's **base directory is `site/`** (set in the Netlify UI). Every push to `main` auto-publishes in ~30 s. Nothing outside `site/` is published.

## Editing content

Two ways — full guide in [`site/README.md`](site/README.md):

1. **Via CMS** — open `/admin`, log in with your Netlify Identity account, edit Road Log / Trip Gallery / any chamber gallery, upload photos, Save → auto-rebuild.
2. **Via code** — edit `site/content/*.json` directly. Road Log is one object per entry; add `"link": "tasmania.html"` to make a row clickable.

Site identity (name, email, social links) lives in the `const SITE = { … }` block near the bottom of `site/index.html`.

## Local preview

There is no build step, but the pages `fetch()` their JSON, so serve over HTTP rather than opening the file directly:

```bash
cd site
python -m http.server 8000
# → http://localhost:8000
```

## Stack

Static HTML / CSS / JS — no build step. Fonts: Fraunces, Instrument Sans, Noto Serif SC (Google Fonts). CMS: Decap CMS + Netlify Identity.
