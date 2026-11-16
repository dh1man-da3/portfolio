# Physics Portfolio — GitHub Pages Edition

A five-page, dark-themed academic portfolio rebuilt from an earlier Flask project. The **original HTML layout, CSS rules, JavaScript interactions, copy, and images are preserved**. The deployed site consists of ordinary static HTML, CSS, JavaScript, and image files; it does **not** run Flask or Python when visitors open it.

The small Python/Jinja2 script is used **only to generate** the static files before publication. It retains the original Jinja template inheritance and data-driven projects/skills without introducing a large JavaScript framework or copying headers/footers across five separate pages.

## Pages

| Page | Public URL path | Editable template |
| --- | --- | --- |
| Home | `/` | `src/templates/pages/index.html` |
| About | `/about/` | `src/templates/pages/about.html` |
| Projects | `/projects/` | `src/templates/pages/projects.html` |
| Skills | `/skills/` | `src/templates/pages/skills.html` |
| Contact | `/contact/` | `src/templates/pages/contact.html` |

An additional `404.html` page handles missing pages.

## Repository layout

```text
.
├── .github/workflows/deploy.yml       # Test, build and publish using GitHub Actions
├── .gitignore
├── README.md
├── requirements-build.txt             # Jinja2 (build-time only)
├── scripts/
│   └── build.py                       # Static HTML generator; path-prefix-aware
├── src/
│   ├── assets/
│   │   ├── css/style.css              # Original stylesheet plus minimal fixes
│   │   ├── js/script.js               # Animations and static contact form
│   │   └── images/                    # All five original images
│   ├── data/
│   │   ├── site.json                  # Name, contact info, social links
│   │   ├── pages.json                 # Navigation and page metadata
│   │   ├── projects.json              # Four project descriptions and images
│   │   └── skills.json                # Six skill percentages
│   └── templates/
│       ├── layouts/base.html          # Shared header, navigation, footer
│       └── pages/                     # Five original page templates + 404
├── tests/test_site.py                 # Builds and verifies both Pages URL styles
└── dist/                              # Generated output; NOT committed
```

## 1. Publish on GitHub Pages

**No web hosting provider, database, Flask server, access token, or manual `gh-pages` branch is necessary.** The included GitHub Actions workflow builds and deploys the website on each push to `main`.

1. Create an empty GitHub repository, for example `physics-portfolio`. For a homepage at `https://YOUR-USERNAME.github.io/` instead, create a repository named exactly `YOUR-USERNAME.github.io`.
2. Extract this ZIP. Upload **the contents of the extracted project folder** to the repository root, including the hidden `.github` directory. Keep `src/`, `scripts/`, and `requirements-build.txt` at the root.
3. In the GitHub repository, go to **Settings → Pages → Build and deployment → Source → GitHub Actions**. Save/confirm that choice if requested.
4. Push to the `main` branch (or commit the uploaded files to `main`). The **Actions** tab will run *Build and deploy portfolio to GitHub Pages* automatically.
5. After the workflow succeeds, GitHub Pages will be available at either:
   - `https://YOUR-USERNAME.github.io/physics-portfolio/` (project repository)
   - `https://YOUR-USERNAME.github.io/` (special user-site repository)

**Important:** Don't select “Deploy from a branch” with the unbuilt source folder. This project has Jinja templates; `dist/` must be generated first. The workflow handles this automatically.

The workflow retrieves GitHub Pages' **actual base path** through `actions/configure-pages`. Therefore it also works if you later rename the repository, switch between a project site and user site, or add a custom domain. You do not need to edit hard-coded navigation or image URLs. For a custom domain, configure it under GitHub **Settings → Pages** as well as configuring your DNS, following GitHub's instructions.

### Option: push using Terminal on macOS

After creating an empty repository on GitHub, run these commands *inside the extracted project folder*, replacing the placeholders:

```bash
git init
git add .
git commit -m "Create static physics portfolio"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

If GitHub tells you the remote repository already contains a README or a commit, clone that repository first and copy the project files into the cloned folder rather than forcing a push.

## 2. Preview it locally

Python 3.10+ is suitable. On macOS, use `python3` in place of `python` if needed. No Node.js, npm or Flask is involved.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-build.txt
python scripts/build.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000/` in your browser. Stop the preview with `Ctrl+C`.

The output folder is regenerated after each build; repeat `python scripts/build.py` after changes and refresh the browser. **Do not edit files inside `dist/`**, because they are automatically replaced.

To test a GitHub Pages project-site path locally at build time:

```bash
python scripts/build.py --base-path /physics-portfolio/
```

That command confirms URLs are generated with the prefix. For simple local browsing use the normal `/` build.

## 3. Make changes

| What you want to change | Edit this file |
| --- | --- |
| Portfolio name, academic details, real email, social links | `src/data/site.json` |
| Project names, descriptions and image filenames | `src/data/projects.json` |
| Skill names and percentages (0–100) | `src/data/skills.json` |
| Introduction, education, interests, written content | `src/templates/pages/*.html` |
| Main navigation, descriptions, pages | `src/data/pages.json` |
| Shared header, footer and metadata | `src/templates/layouts/base.html` |
| Colors, spacing, cards, mobile design | `src/assets/css/style.css` |
| Animations, contact-form behavior | `src/assets/js/script.js` |
| Project/profile pictures | `src/assets/images/` |

Images referenced from `projects.json` must exist in `src/assets/images/` with a matching filename. Use the image's original name or edit the JSON to match the new filename. Template output escapes user-supplied text to protect HTML rendering.

### Contact details: important before you publish

The original `dhiman.physics@example.com` address was a placeholder; **it has not been guessed or published as a real address**. To configure your real contact address:

1. Open `src/data/site.json`.
2. Replace `"email": ""` with a real address, e.g. `"email": "you@yourdomain.example"` (replace that sample; don't publish it).
3. Add your other verified social URLs. The GitHub link is filled in; the other labels stay visible but non-clickable until you add their URLs.
4. Commit and push the changes.

The message form preserves the original visual design. **When an email is configured**, submitting the form opens the visitor's email app with a pre-filled draft. They must send that draft themselves; GitHub Pages cannot email messages directly. A visitor without a configured mail app may not be able to use the form. If you later prefer a hosted form provider, integrate it into the existing form without rebuilding the rest of the site.

If no email is configured, form submissions show an explicit “not configured” message instead of falsely claiming to deliver a message.

### Add another page

1. Duplicate one of the templates in `src/templates/pages/` and edit its HTML. Keep `{% extends "layouts/base.html" %}` and `{% block content %}`.
2. Add one object to `src/data/pages.json`, e.g. with `"key": "research"`, `"label": "Research"`, `"template": "pages/research.html"`, `"output": "research/index.html"`, `"url": "/research/"` and a description.
3. Link using `{{ route('research') }}` so GitHub Pages base paths are handled correctly.
4. Build, test and push. The navbar is generated from this data automatically.

**Note:** For HTML asset links use `{{ asset('images/example.png') }}` and for navigation use `{{ route('projects') }}`. Don't hard-code site-root links such as `/projects/` or `/assets/...` because a project Pages site may live under `/repository-name/`.

## 4. Tests and deployment checks

```bash
python -m unittest discover -s tests -v
python scripts/build.py
```

Tests check that all pages are generated, required images and local links resolve, projects and skills render, contact inputs exist, and internal links work with both `/` and `/repository-name/` bases. The GitHub Actions workflow runs these checks **before** deploying on every push. A failed test prevents a broken deployment.

## Notes and limitations

- The website **does not** need Python or JavaScript on the server; only the build workflow uses Python/Jinja2.
- No Flask dependency, API, user login, database, tracking script or third-party form submission has been added.
- The original Google Fonts Inter stylesheet is still fetched from Google; if offline or blocked, the site falls back to the system sans-serif font.
- The original visual design and wording are deliberately not rewritten. The main exceptions are: safe contact/social placeholders, improved mobile navbar wrapping, keyboard focus visibility, and reduced-motion handling.
- The original project illustrations and profile photograph are included. Review your permission to publish those images publicly before making the repository public.
- GitHub Pages sites are **publicly accessible**, even if the backing repository is private under an eligible plan.

### Upstream reference documentation

- [GitHub Pages: publishing with GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [GitHub Pages: custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Jinja2 documentation](https://jinja.palletsprojects.com/)
