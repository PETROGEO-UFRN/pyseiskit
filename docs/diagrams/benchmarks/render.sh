#!/usr/bin/env bash
# Compile the C4 diagrams in this folder (*.mmd, Mermaid) to SVG.
#
# Uses the Mermaid CLI when it can run (needs a headless Chrome); otherwise the Kroki
# rendering service (https://kroki.io), which receives the diagram text. Every SVG then
# gets an opaque white background, so it stays readable on dark themes.
set -euo pipefail
cd "$(dirname "$0")"

for source in *.mmd; do
    target="${source%.mmd}.svg"
    if command -v mmdc >/dev/null && mmdc -i "$source" -o "$target" -b white 2>/dev/null; then
        echo "$source -> $target (mmdc)"
    else
        curl -sSf --max-time 60 -H 'Content-Type: text/plain' --data-binary @"$source" \
            https://kroki.io/mermaid/svg -o "$target"
        echo "$source -> $target (kroki.io)"
    fi
    python3 - "$target" <<'EOF'
import re, sys
path = sys.argv[1]
svg = open(path).read()
if 'id="c4-background"' not in svg:
    x, y, w, h = re.search(r'viewBox="([-\d.]+) ([-\d.]+) ([\d.]+) ([\d.]+)"', svg).groups()
    rect = f'<rect id="c4-background" x="{x}" y="{y}" width="{w}" height="{h}" fill="#ffffff"/>'
    svg = re.sub(r'(<svg[^>]*>)', r'\1' + rect, svg, count=1)
    open(path, "w").write(svg)
EOF
done
