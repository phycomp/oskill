---
name: viz-dboard
description: >
  Use when visualizing skill hierarchies or generating a mindmap of local
  skills. Triggers on "mindmap", "skill map", "viz-dboard", or "visualize
  skills".
---

# Viz Dboard

Visualize a set of skills as a mindmap in SVG format.

## 1. Inventory the skills

List the skills under review and their parent-child relationships.

## 2. Build the hierarchy

Define nodes and edges:

- Root: the collection (e.g., "self-developed skills")
- Parents: orchestrator skills
- Children: atomic capabilities hooked by parents

## 3. Render the mindmap

Create an SVG file (e.g., `skill-map.svg`) with:

- A root node
- Branches for each parent
- Child nodes connected by edges
- A legend for node types

The included example mindmap is at `skill-map.svg`.

## 4. Validate

```bash
python3 -c "import xml.etree.ElementTree as ET; ET.parse('skill-map.svg'); print('SVG valid')"
```

## Notes

- Keep node labels short (skill names).
- Use dashed lines for conditional hooks.
- Update the SVG whenever the skill hierarchy changes.
EOF
echo "written"