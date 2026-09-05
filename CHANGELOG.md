# Changelog

## Unreleased

- Replace the page with the RAPID Facility's revised version of September 5, 2026. Sample points carry only the scan id, date, creator, and position; the notes, categories, and the coordinate readout in the popup are gone. The points list filters by date. The point markers are 40 m circles at 55% opacity.
- Embed every imagery layer in the page, including the orthomosaic. The 10 cm tile layer, its tile probe, and the `ortho_10cm_tiles/` folder are no longer used.
- Add the SIPI2 pigment stress index layer and a pre-fire regional Esri Wayback layer dated 2026-06-30. The map has no pan limit; the home button returns to the survey area.
- Start with the building footprints hidden. The Show footprints toggle or choosing a building from the list draws them.
- Open a hyperspectral tile from its number label or from a click on ground inside it; buildings inside a tile still take the click.
- Move the Overture attribution from the map attribution bar to the Buildings tab, which lists the release, source datasets, and license.
- Add a Show on map switch in the header for the sample points. The 3D view follows it.
- Carry the theme toggle, RAPID logo, DesignSafe attribution, home button, compare clip fix, building footprints, and 3D view over from the previous page. The control card now spans the map height and sits above the Leaflet panes and controls.
- Fix building selection inside the fire perimeter and hyperspectral tiles: their fills no longer capture clicks, and buildings draw beneath the sample points so both stay clickable.
- Add a Buildings section to the control card and a Buildings tab to the side panel: Overture footprints near the fire perimeters, colored by source dataset, fire perimeter, or height, with filters by scope, source, type, height, and distance to a fire line, a selected-building card, and the equivalent DuckDB query for the current filters.
- Add a 3D view switch that extrudes the filtered footprints by published height over the current imagery layer, with the fire perimeters, hyperspectral tiles, and sample points drawn in the same scene. deck.gl loads on first use.
- Add `data/buildings.json` and `data/buildings.js` with `scripts/build_buildings.py` to produce them from Overture release 2026-08-19.0. The page loads the `.js` file through a script tag so it runs from disk and from GitHub Pages.
