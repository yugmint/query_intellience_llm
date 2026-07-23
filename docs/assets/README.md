# Assets

- `workflow.svg` — hand-authored diagram of the LangGraph node graph
  (referenced from `../01-architecture.md`). Real, checked-in asset.
- `architecture.png` — **not generated.** I can't produce raster images.
  Two options instead of a placeholder file with nothing in it:
  1. Export `workflow.svg` to PNG yourself if a raster copy is specifically
     needed somewhere (`rsvg-convert workflow.svg architecture.png`, or any
     browser "export SVG as PNG").
  2. Use the Mermaid diagrams already embedded in `../01-architecture.md`
     directly — they render natively on GitHub, no export step needed.
- `screenshots/` — placeholder. This is a CLI + FastAPI backend with no UI,
  so there isn't a natural screenshot the way there would be for a
  frontend. See `screenshots/README.md` for closer equivalents.
