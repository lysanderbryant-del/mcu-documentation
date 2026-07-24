# Deploy MCU Documentation to GitHub Pages

## Option 1: GitHub Repository (Recommended)

### Step 1: Push to GitHub

```bash
cd c:/Users/bryantl4/Documents/process-factory

# Initialize git (if not already)
git init
git add .
git commit -m "MCU documentation complete"

# Create GitHub repo (via GitHub UI)
# Then:
git remote add origin https://github.com/YOUR_USERNAME/process-factory.git
git push -u origin main
```

### Step 2: Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main**
4. Folder: **/ (root)** or **/docs**
5. Save

### Step 3: Configure Path

**Option A: Root deployment**
- Move `projects/mcu/docs/index.html` → `docs/index.html`
- URL: `https://YOUR_USERNAME.github.io/process-factory/`

**Option B: Project subfolder**
- Keep `projects/mcu/docs/index.html` as-is
- URL: `https://YOUR_USERNAME.github.io/process-factory/projects/mcu/docs/`

### Step 4: Verify

Wait 2-3 minutes, then visit:
```
https://YOUR_USERNAME.github.io/process-factory/projects/mcu/docs/
```

---

## Option 2: Netlify Drop (No GitHub)

### Step 1: Create Deployment Package

```bash
cd c:/Users/bryantl4/Documents/process-factory/projects/mcu/docs
zip -r mcu-docs.zip index.html
```

### Step 2: Deploy

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag `mcu-docs.zip` onto the page
3. Wait 10 seconds
4. Get URL: `https://random-name-12345.netlify.app/`

### Step 3: Custom Domain (Optional)

1. Click **Site settings**
2. **Domain management** → **Add custom domain**
3. Follow DNS instructions

---

## Option 3: Azure Static Web Apps

### Step 1: Create Azure Static Web App

```bash
# Install Azure CLI
az login

# Create resource group
az group create --name mcu-docs-rg --location uksouth

# Create static web app
az staticwebapp create \
  --name mcu-documentation \
  --resource-group mcu-docs-rg \
  --source c:/Users/bryantl4/Documents/process-factory/projects/mcu/docs \
  --location uksouth \
  --branch main
```

### Step 2: Get URL

```bash
az staticwebapp show \
  --name mcu-documentation \
  --resource-group mcu-docs-rg \
  --query "defaultHostname" \
  --output tsv
```

URL: `https://mcu-documentation.azurestaticapps.net/`

---

## Option 4: Local Network Share (Intranet Only)

### Step 1: Copy to Network Share

```bash
# Copy documentation
xcopy c:\Users\bryantl4\Documents\process-factory\projects\mcu\docs\index.html \\centrica-share\mcu-docs\ /Y

# Or use mapped drive
copy c:\Users\bryantl4\Documents\process-factory\projects\mcu\docs\index.html Z:\mcu-docs\
```

### Step 2: Share Link

Internal URL:
```
file://centrica-share/mcu-docs/index.html
```

Or:
```
file://Z:/mcu-docs/index.html
```

**Note**: Only accessible within Centrica network.

---

## Export Flowcharts as Images (Visio-Quality)

Flowcharts are rendered by Mermaid.js in the browser. To save as PNG/SVG:

### Browser Method (Manual)

1. Open `index.html` in Chrome/Edge
2. Right-click flowchart → **Inspect**
3. Find `<svg>` element
4. Right-click → **Copy outerHTML**
5. Paste into [SVG to PNG Converter](https://svgtopng.com/)
6. Download PNG

### Automated Export (Node.js)

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Extract mermaid diagrams from HTML
grep -A 100 'class="mermaid"' index.html > diagrams.mmd

# Convert to PNG (high-res)
mmdc -i diagrams.mmd -o architecture.png -w 1920 -H 1080

# Convert to SVG (vector)
mmdc -i diagrams.mmd -o architecture.svg
```

### Python Script (Automated)

```python
# Save as: export-flowcharts.py
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()
driver.get('file:///c:/Users/bryantl4/Documents/process-factory/projects/mcu/docs/index.html')
time.sleep(3)  # Wait for Mermaid render

# Find all SVG elements
svgs = driver.find_elements(By.CSS_SELECTOR, '.mermaid svg')

for i, svg in enumerate(svgs):
    svg_html = svg.get_attribute('outerHTML')
    with open(f'flowchart-{i+1}.svg', 'w', encoding='utf-8') as f:
        f.write(svg_html)

print(f"Exported {len(svgs)} flowcharts")
driver.quit()
```

Run:
```bash
pip install selenium
python export-flowcharts.py
```

Outputs: `flowchart-1.svg`, `flowchart-2.svg`, etc.

---

## Recommended: GitHub Pages + Mermaid

**Why**:
- ✓ Free hosting
- ✓ Version control (track changes)
- ✓ Collaborative editing (PRs)
- ✓ Mermaid renders client-side (no build step)
- ✓ Export to Word via browser print

**Setup time**: 5 minutes

**URL example**: `https://centricaplc.github.io/process-factory/projects/mcu/docs/`

---

## Next Steps

1. **Choose deployment method** (recommend GitHub Pages)
2. **Deploy documentation**
3. **Share URL** with stakeholders
4. **Optional**: Export flowcharts as PNG for presentations
5. **Optional**: Print to PDF for offline use

---

*GitHub Pages deployment is the modern, maintainable solution for technical documentation.*
