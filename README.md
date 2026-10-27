# Hamburg 2026 — interactive public city guide

A map-first website of 36 curated public locations collected for a November 2026 Hamburg visit.

**Public website:** https://karstenkelm.github.io/

## Files

- `index.html` — deployed mobile-friendly site: Leaflet/OpenStreetMap, place search, category filters and popups.
- `data/hamburg_places.geojson` — editable curated locations and descriptions.
- `build_map.py` — alternative reproducible HTML map generator using **Professor Qiusheng Wu's leafmap Folium backend**.

## Build with leafmap

```sh
python -m pip install leafmap folium
python build_map.py
```

This writes `leafmap-map.html`, a separate standalone map with category layers. The homepage itself uses Leaflet directly so its custom search, list, and mobile experience work on GitHub Pages without a Python runtime. Both use the same GeoJSON.

## Editing the website

Edit `data/hamburg_places.geojson` to add places, then commit to `main`. GitHub Pages should serve the update from its configured publishing branch. Coordinates are **approximate orientation markers**, not verified front-door coordinates. The Directions link searches for the venue name.

Only public attractions and businesses are included; private trip plans and accommodation are intentionally excluded.

## Image and map credits

Header photo: **Florian Schäffer**, [Astra rotlicht.jpg](https://commons.wikimedia.org/wiki/File:Astra_rotlicht.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The original Commons file is displayed without editing.

Map tiles and data: © OpenStreetMap contributors, [copyright notice](https://www.openstreetmap.org/copyright).

## Previous website

The former GeoAI Lab homepage remains available through Git history (before commit `af2eebf`). Other prior pages were not deleted.

## QA

Check the published site on mobile and desktop. External dependencies require Internet (OpenStreetMap tiles, Leaflet CDN, Commons photo). Validate exact business locations and opening times before visiting.
