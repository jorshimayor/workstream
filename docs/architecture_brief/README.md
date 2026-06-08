# Workstream Architecture Brief

This folder contains the shareable Workstream architecture brief.

- Source: [workstream_architecture_brief.md](workstream_architecture_brief.md)
- PDF: [workstream_architecture_brief.pdf](workstream_architecture_brief.pdf)
- Render script: [render_pdf.sh](render_pdf.sh)

The brief uses the C4-PlantUML diagrams from `docs/diagrams/` and packages them into a single PDF for team review.

## Render

```bash
docs/architecture_brief/render_pdf.sh
```

The script regenerates image assets from the current diagram SVGs, renders the lifecycle sequence asset when PlantUML is available, then produces `workstream_architecture_brief.pdf`.
