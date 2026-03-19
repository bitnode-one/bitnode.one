#!/bin/bash
set -e
hugo new site . --force
# Hugo config for GitHub Pages + custom domain
cat > hugo.yaml << 'EOC'
baseURL: "https://bitnode.one/"
title: "Bitnode One ⚡"
languageCode: "en"
theme: "none"  # we use plain Tailwind
build:
  buildStats:
    enable: true
module:
  mounts:
    - source: assets
      target: assets
EOC
# Create folders & our exact one-pager
mkdir -p content layouts/partials assets/css
cat > content/_index.md << 'EOC'
---
title: "Bitnode One ⚡"
---
<!-- Full one-pager HTML from our preview (pasted as markdown for Hugo) -->
{{ partial "head.html" . }}
<!-- Paste the entire HTML body we created earlier here (shortened for script) -->
<!-- Hero + all sections exactly as in the Tailwind preview -->
EOC
# Tailwind setup
cat > assets/css/main.css << 'EOC'
@import "tailwindcss";
@plugin "@tailwindcss/typography";
EOC
npm init -y && npm install -D tailwindcss @tailwindcss/cli
cat > tailwind.config.js << 'EOC'
module.exports = { content: ["./content/**/*", "./layouts/**/*"], theme: { extend: {} } }
EOC
# Quick partials
cat > layouts/partials/head.html << 'EOC'
<!DOCTYPE html><html><head><script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
<style>body{font-family:system-ui}</style></head><body class="bg-black text-white">
EOC
cat > layouts/_default/baseof.html << 'EOC'
{{ partial "head.html" . }}{{ .Content }}</body></html>
EOC
echo "✅ Hugo + Tailwind initialized"
