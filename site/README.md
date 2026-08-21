# Five Chambers — Personal Site

## Structure
```
index.html          ← single-page main site (self-contained CSS/JS)
sangha.html         ← Buddhist Youth chamber
pride.html          ← Pride & Practice chamber
tea.html            ← Tea & the Way chamber
data.html           ← Data & Drive chamber
travel.html         ← Solo Maps chamber
chamber.css         ← shared styles for chamber pages
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
- **Trip Gallery**: edit `content/tripgallery.json` (or inline `TRIP_GALLERY_FALLBACK`)
- **Chamber photos**: edit `content/{chamber}-photos.json`
- **Photo src accepts any filename/path** — e.g. `"photos/tasmania/my-sunset.jpg"`

## Deploy
Push to GitHub → Netlify auto-deploys.
