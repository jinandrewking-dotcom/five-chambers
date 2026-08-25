# Five Chambers — Personal Site

## Structure
```
index.html          ← single-page main site (self-contained CSS/JS)
sangha.html         ← Buddhist Youth chamber
pride.html          ← Pride & Practice chamber
tea.html            ← Tea & the Way chamber
data.html           ← Data & Drive chamber
travel.html         ← Solo Maps chamber
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
  sangha-photos.json
  pride-photos.json
  tea-photos.json
  data-photos.json
  travel-photos.json
photos/             ← image storage
  tasmania/          ← Tasmania trip photos
  china/             ← China trip photos
  new-zealand/       ← NZ trip photos
  sangha/            ← Sangha gallery photos
  pride/             ← Pride gallery photos
  tea/               ← Tea gallery photos
  data/              ← Data gallery photos
  travel/            ← Travel gallery photos
netlify.toml        ← Netlify build config
```

## Updating content via Decap CMS
1. Go to `yourdomain.netlify.app/admin` (or your custom domain `/admin`)
2. Log in with your Netlify Identity account
3. Edit Road Log, Trip Gallery, or any Chamber Gallery
4. Upload photos with any filename — no renaming needed
5. Click Save → Netlify auto-rebuilds in ~30s

## Updating content via code
- **Site config** (name/email/social): edit `const SITE` in `index.html`
- **Road Log**: edit `content/roadlog.json` (or inline `ROAD_LOG_FALLBACK` in index.html)
  - Add `"link": "tasmania.html"` (etc.) to an entry to make its Road Log row clickable, jumping to that trip page. Leave `link` out for entries that shouldn't navigate anywhere.
- **Trip Gallery**: edit `content/tripgallery.json` (or inline `TRIP_GALLERY_FALLBACK`)
  - Each gallery entry needs a stable `"slug"` (e.g. `"tasmania"`) — this is how `tasmania.html`/`china.html`/`new-zealand.html` find their own photos/title/description. Don't change an existing slug unless you also update the matching `SLUG` constant near the bottom of that trip page's `<script>`.
- **Chamber photos**: edit `content/{chamber}-photos.json`
- **Photo src accepts any filename/path** — e.g. `"photos/tasmania/my-sunset.jpg"`
- **Trip route maps**: each trip page (`tasmania.html`/`china.html`/`new-zealand.html`) has its own hand-drawn SVG route illustration inline in the HTML (search for `<div class="route-map">`) — it's decorative, not a real map, so edit the `<path>`/`<circle>`/`<text>` coordinates by hand if you add/rename waypoints. To add a 4th trip page, copy one of these three files as a template.

## Deploy
Push to GitHub → Netlify auto-deploys.
