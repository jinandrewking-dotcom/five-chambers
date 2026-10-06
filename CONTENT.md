# Five Chambers — content guide

Paths below are inside `site/` (the folder Netlify publishes) unless they start with `tools/` or `.github/`.
This guide lives at the repo root so it isn't published with the site.

## Structure
```
index.html          ← single-page main site (self-contained CSS/JS)
sangha.html         ← Buddhist Youth chamber
pride.html          ← Pride & Practice chamber
tea.html            ← Tea & the Way chamber
data.html           ← Data & Drive chamber
travel.html         ← Solo Maps chamber
notes.html          ← Notes · 研究笔记 — the reading log
tasmania.html       ← Trip page: Launceston → Hobart (route map + gallery)
china.html          ← Trip page: Jingdezhen → Changsha (route map + gallery)
new-zealand.html    ← Trip page: Queenstown → ... → Auckland (route map + gallery)
chamber.css         ← shared styles for chamber pages AND trip pages
admin/              ← Decap CMS admin panel
  index.html        ← CMS entry point
  config.yml         ← CMS collection configuration
content/            ← CMS-managed JSON data
  roadlog.json       ← Road Log entries
  tripgallery.json   ← Trip Gallery entries + photos
  notes.json         ← Notes entries (the reading log)
  ev-share.json      ← EV figures behind the data.html charts
  fi-insights.json   ← F&I / value-add section of data.html (public info only)
  sangha-photos.json
  pride-photos.json
  tea-photos.json
  travel-photos.json
photos/             ← image storage
  tasmania/          ← Tasmania trip photos
  china/             ← China trip photos
  new-zealand/       ← NZ trip photos
  sangha/            ← Sangha gallery photos
  pride/             ← Pride gallery photos
  tea/               ← Tea gallery photos
  travel/            ← Travel gallery photos
netlify.toml        ← Netlify build config

(repo root, not published)
tools/add_note.py          ← append a note to site/content/notes.json from the terminal
tools/optimize_photos.py   ← strip GPS/EXIF and resize photos to 1600 px
.github/workflows/optimize-photos.yml ← runs optimize_photos.py on every photo push
```

## Updating content via Decap CMS
1. Go to `yourdomain.netlify.app/admin` (or your custom domain `/admin`)
2. Log in with your Netlify Identity account
3. Edit Road Log, Trip Gallery, Notes, EV Data, F&I Insights, or any Chamber Gallery
4. Upload photos with any filename — no renaming needed. A GitHub Action then strips the
   phone's GPS location from the photo and shrinks it, and commits that back (see *Photos* below)
5. Click Save → Netlify auto-rebuilds in ~30s

## Updating content via code
- **Site config** (name/email/social): edit `const SITE` in `index.html`
- **Road Log**: edit `content/roadlog.json` (or inline `ROAD_LOG_FALLBACK` in index.html)
  - Add `"link": "tasmania.html"` (etc.) to an entry to make its Road Log row clickable, jumping to that trip page. Leave `link` out for entries that shouldn't navigate anywhere.
- **Trip Gallery**: edit `content/tripgallery.json` (or inline `TRIP_GALLERY_FALLBACK`)
  - Each gallery entry needs a stable `"slug"` (e.g. `"tasmania"`) — this is how `tasmania.html`/`china.html`/`new-zealand.html` find their own photos/title/description. Don't change an existing slug unless you also update the matching `SLUG` constant near the bottom of that trip page's `<script>`.
- **Chamber photos**: edit `content/{chamber}-photos.json`
- **Notes (reading log)**: edit `content/notes.json`, or run the helper from the repo root:
  ```
  python tools/add_note.py --title "..." --summary "..." --tags neuroscience,methods \
      --source https://example.org/paper --source-label "Journal, 1 Oct 2026"
  python tools/add_note.py --title "..." --summary "..." --dry-run   # preview only
  ```
  It refuses duplicates (same source URL, or same title on the same date; `--force` overrides) and only accepts http(s) source links.
  Newest entries sort to the top automatically. Tag buttons on the page build themselves from the tags you use.
- **EV charts (data.html)**: edit `content/ev-share.json` — `stats` feed the big-number cards, `monthly.points` feeds the line chart, `states.points` feeds the bar chart. Both charts also render as tables (open the "View as table" toggle), so the numbers stay readable without JavaScript.
  - `monthly.context` (same month in earlier years) prints under the line chart; `brands.points` fills an optional third chart that stays hidden while empty.
  - **Source discipline**: every chart reads its attribution from the `sources` array in the JSON. Keep public, citable figures here (FCAI VFACTS, EVC, AAA EV Index) — never internal dealership data. Link the primary publication where possible, not a news article about it. Only `https://` links are rendered as links.
- **F&I section (data.html)**: edit `content/fi-insights.json` (metrics, lender-channel comparison, hypotheses, regulation timeline). Same rule, stricter: public regulation/legislation and frameworks only — never employer, dealership, lender or customer figures, even rounded or anonymised.
- **Photo src accepts any filename/path** — e.g. `"photos/tasmania/my-sunset.jpg"`
- **Trip route maps**: each trip page (`tasmania.html`/`china.html`/`new-zealand.html`) has its own hand-drawn SVG route illustration inline in the HTML (search for `<div class="route-map">`) — it's decorative, not a real map, so edit the `<path>`/`<circle>`/`<text>` coordinates by hand if you add/rename waypoints. To add a 4th trip page, copy one of these three files as a template.

## Photos
Phones embed the GPS location of every shot in the file. `tools/optimize_photos.py` removes all metadata
(GPS, camera, timestamps), bakes in the rotation, and resizes to 1600 px — typically 3–6 MB down to 0.2–0.4 MB.
The GitHub Action runs it automatically on every push to `main` that touches `site/photos/`, so CMS uploads
are cleaned within a minute or two. To run it by hand: `python tools/optimize_photos.py` (or `--check` to only report).

On iPhone you can also stop location being attached when sharing: Share sheet → **Options** → turn **Location** off.

## Deploy
Push to GitHub → Netlify auto-deploys.
