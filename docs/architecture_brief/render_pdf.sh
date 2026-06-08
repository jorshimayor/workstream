#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

mkdir -p images

convert_diagram() {
  local source="$1"
  local target="$2"
  convert -background white -density 180 "$source" -resize '2400x2400>' "$target"
}

convert_diagram ../diagrams/rendered/workstream_context.svg images/workstream_context.png
convert_diagram ../diagrams/rendered/workstream_v01_container.svg images/workstream_v01_container.png
convert_diagram ../diagrams/rendered/backend_v01_components.svg images/backend_v01_components.png
convert_diagram ../diagrams/rendered/future_identity_payment_reputation.svg images/future_identity_payment_reputation.png

if command -v plantuml >/dev/null 2>&1; then
  plantuml -tpng task_lifecycle_sequence.puml
elif [[ -n "${PLANTUML_JAR:-}" ]]; then
  java -jar "$PLANTUML_JAR" -tpng task_lifecycle_sequence.puml
else
  echo "PlantUML is required to regenerate task_lifecycle_sequence.png" >&2
  echo "Set PLANTUML_JAR=/path/to/plantuml.jar or install plantuml." >&2
  exit 1
fi
mv task_lifecycle_sequence.png images/task_lifecycle_sequence.png

pandoc workstream_architecture_brief.md \
  --standalone \
  --from markdown+raw_html \
  --pdf-engine=weasyprint \
  --css brief.css \
  --metadata title="Workstream Architecture Brief" \
  --resource-path=".:images" \
  --output workstream_architecture_brief.pdf

echo "Rendered docs/architecture_brief/workstream_architecture_brief.pdf"
