---
name: seo-check
description: "Audit SEO, Open Graph, responsive design. Checks meta tags, OG image, robots.txt, sitemap, structured data, and mobile rendering."
disable-model-invocation: false
argument-hint: "[url]"
---

# SEO & Responsive Audit

Audit a web project's SEO metadata and responsive rendering from source code. Fix issues found.

## Input

- Work from the current project directory (cwd)
- An optional URL argument for the responsive check (screenshots). If not provided, infer the production URL from CLAUDE.md, config files, or env vars.

## Step 0: Locate Files

Find the HTML entry point and static assets:
1. Search for `index.html` — common locations: `./index.html`, `public/index.html`, `frontend/index.html`, `src/index.html`
2. Find the static/public assets directory (where `robots.txt`, `sitemap.xml`, OG images live): `public/`, `frontend/public/`, `static/`
3. Identify the production domain from CLAUDE.md, package.json homepage, env files, or nginx config

## 1. Meta Tags Audit

Read the HTML `<head>` from the source `index.html` and check:

| Check | Optimal |
|-------|---------|
| `<title>` | 50–60 characters, includes brand + value prop |
| `<meta name="description">` | 120–160 characters, actionable |
| `<link rel="canonical">` | Present, absolute URL |
| `<html lang="...">` | Present |
| `<meta name="viewport">` | Present |

Report: present/missing/too short/too long for each.

## 2. Open Graph Audit

Check these `<meta property="og:...">` tags in `index.html`:

| Tag | Required |
|-----|----------|
| `og:title` | Yes — 50–60 chars |
| `og:description` | Yes — under 200 chars |
| `og:image` | Yes — URL to image |
| `og:image:width` | Yes — 1200 |
| `og:image:height` | Yes — 630 |
| `og:url` | Yes — canonical URL |
| `og:type` | Yes — `website` or `article` |
| `og:site_name` | Recommended |

### OG Image Validation

If `og:image` references an image file:
1. Find the local file in the public/static assets directory
2. Read the image to check dimensions (should be 1200×630) and inspect visually
3. Check file size < 300KB
4. Visual check: has a clear headline? Has a CTA or brand? Not just a generic illustration?

## 3. Twitter Card Audit

Check in `index.html`:
- `twitter:card` — should be `summary_large_image`
- `twitter:title` — present
- `twitter:description` — present
- `twitter:image` — present

## 4. Structured Data (JSON-LD)

Check for `<script type="application/ld+json">` in `index.html`:
- Present? Parse and validate JSON
- Has `@type` — `SoftwareApplication`, `WebSite`, `Organization`, etc.
- Has `name`, `url`, `description`
- Schema matches the actual product/site

## 5. Crawler Files

Look for these files in the static/public assets directory:

### robots.txt
- Exists?
- Has `Sitemap:` directive?
- Blocks auth/api/admin routes?
- Allows public pages?

### sitemap.xml
- Exists?
- Valid XML?
- Lists all public pages?
- No authenticated/private pages included?

## 6. Responsive Design Check

Use `o-browser` (BrowserClient) to take screenshots of the production URL at multiple viewports:

```python
from o_browser import BrowserClient

viewports = [
    ("mobile", 375, 812),     # iPhone 13
    ("tablet", 768, 1024),    # iPad
    ("desktop", 1440, 900),   # Standard desktop
]

async with BrowserClient(headless=True) as browser:
    for name, w, h in viewports:
        await browser.page.set_viewport_size({"width": w, "height": h})
        await browser.goto(url)
        await browser.page.wait_for_load_state("networkidle")
        await browser.screenshot(f"/tmp/responsive-{name}.png")
```

Then read each screenshot and check:
- **Mobile**: no horizontal overflow, text readable, touch targets ≥ 44px, navigation usable
- **Tablet**: layout adapts, no wasted space, images scale
- **Desktop**: full layout, no broken sections

## 7. Output

### Report Format

```
## SEO Audit: <project>

### Meta Tags
- ✅ title: "..." (XX chars)
- ❌ description: missing
- ...

### Open Graph
- ✅ og:title: "..."
- ⚠️ og:image: exists but no headline text
- ...

### Twitter Card
- ✅ All tags present

### Structured Data
- ✅ JSON-LD SoftwareApplication

### Crawler Files
- ✅ robots.txt
- ❌ sitemap.xml: missing

### Responsive
- ✅ Mobile: [screenshot]
- ⚠️ Tablet: horizontal overflow on hero section
- ✅ Desktop: OK

### Issues to Fix
1. [priority] description
2. ...
```

### After Reporting

- Ask the user which issues to fix
- Fix them directly in source code (edit HTML, generate images, create files)
- For OG image generation, use Python PIL to create/modify images with text overlay
- For responsive issues, edit CSS/components in the project
- Re-run affected checks after fixes
