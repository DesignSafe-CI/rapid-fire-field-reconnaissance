# Data files

## buildings.json and buildings.js

Building footprints near the fire perimeters. The page loads `buildings.js`, which assigns the same JSON to `window.BUILDINGS_DATA`, through a script tag so it works when opened from disk and on GitHub Pages alike. `buildings.json` is the same data for other tools.

- Source: Overture Maps release 2026-08-19.0, buildings theme. Overture merges Microsoft ML Buildings (version 2025-02-25), OpenStreetMap, and Esri Community Maps. License ODbL.
- Extent: footprints whose representative point lies within 300 m of any fire perimeter on the page. The download bounding box is -117.625, 47.683 to -117.300, 47.832.
- Count: 4,726 footprints, 2,390 inside a perimeter.
- Heights are as published by Overture. Where OpenStreetMap has no height tag, the value is Microsoft's machine-learning estimate. Footprints without a height are drawn at 3 m in the page and marked.

Each record: `id` (Overture GERS id), `g` (outer ring as lon, lat pairs), `h` (height, m), `fl` (floors), `c` (class), `st` (subtype), `n` (primary name), `s` (source bitmask: 1 Microsoft, 2 OpenStreetMap, 4 Esri), `a` (footprint area, m²), `fire` (containing perimeter name or null), `d` (distance to the nearest fire line, m), `hsi` (containing hyperspectral tile or null), `v` (Overture record version), `rs` (roof shape).

Regenerate with:

```
uv run --with "shapely>=2.0" --with pyproj --with overturemaps python scripts/build_buildings.py
```

The raw Overture download (about 70 MB) is written to `data/overture_buildings_raw.geojson` and is ignored by git.
