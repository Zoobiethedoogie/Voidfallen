# GitHub Pages Deployment Guide

## Quick Deploy (1-2 minutes)

1. **Push to main branch:**
   ```bash
   git add -A
   git commit -m "Deploy Voidfallen web version"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: **main** branch, **/ (root)** directory
   - Save

3. **Access your game:**
   - Visit: `https://<your-username>.github.io/Voidfallen/`
   - Game loads instantly in browser

## How It Works

The game uses **static files only**:
- HTML structure
- JavaScript game logic
- CSS styling
- PNG assets

No build process, no backend server needed. GitHub serves everything as-is.

## Updating Your Game

After making changes:

```bash
# Commit and push
git add .
git commit -m "Update: [description of changes]"
git push origin main
```

Changes deploy automatically within a few seconds.

## Troubleshooting

**Game doesn't load:**
- Check browser console (F12 → Console tab)
- Verify `index.html` path is `/Voidfallen/index.html`
- Clear browser cache (Ctrl+Shift+Delete)

**Images not showing:**
- Asset paths should be relative: `../game_assets/...`
- Check file names match exactly (case-sensitive)

**Local testing before deploy:**
- Open `index.html` directly in browser, or
- Use `python3 -m http.server` and visit `localhost:8000`

## Custom Domain (Optional)

To use your own domain instead of `github.io`:

1. Buy a domain
2. Settings → Pages → Custom domain
3. Add DNS records (CNAME or A records)
4. Create `CNAME` file in repo with your domain

See [GitHub's guide](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) for details.
