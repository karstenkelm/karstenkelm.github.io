"""Build English and German static Hamburg maps with Qiusheng Wu's leafmap."""
from pathlib import Path
import json
import html
from urllib.parse import quote
import folium
import leafmap.foliumap as leafmap

ROOT = Path(__file__).resolve().parent
geo = json.loads((ROOT / "data/hamburg_places.geojson").read_text(encoding="utf-8"))
colors = {"Food": "#eaa45f", "Kneipen": "#e05d5a", "Cocktails": "#ac8ce3",
          "Sights": "#469a89", "Harbor": "#428ec3", "Shops": "#b99c50"}
names_de = {"Food": "Essen", "Kneipen": "Kneipen", "Cocktails": "Cocktails",
            "Sights": "Sehenswertes", "Harbor": "Hafen", "Shops": "Läden"}

for lang, output in (("en", "leafmap-map.html"), ("de", "leafmap-map-de.html")):
    m = leafmap.Map(center=[53.563, 9.987], zoom=12, fullscreen_control=False)
    # Minimal monochrome appearance for the raster basemap, preserving colored markers.
    m.get_root().header.add_child(folium.Element("""
    <style>
    .leaflet-tile-pane img.leaflet-tile {
      filter: grayscale(100%) saturate(0%) contrast(82%) brightness(110%);
    }
    </style>
    """))
    map_groups = []
    for category, color in colors.items():
        label = names_de[category] if lang == "de" else category
        group = folium.FeatureGroup(name=label, show=True)
        map_markers = []
        for feature in geo["features"]:
            p = feature["properties"]
            if p["category"] != category:
                continue
            longitude, latitude = feature["geometry"]["coordinates"]
            dest = "https://www.google.com/maps/search/?api=1&query=" + quote(p["name"] + ", Hamburg Germany")
            desc = p.get("description_de", p["description"]) if lang == "de" else p["description"]
            link_text = "Route anzeigen" if lang == "de" else "Directions"
            fields = [f"<strong style='font-size:15px'>{html.escape(p['name'])}</strong>", f"<p>{html.escape(desc)}</p>"]
            for key, title in (("address", "Adresse" if lang == "de" else "Address"),
                               ("phone", "Telefon" if lang == "de" else "Phone"),
                               ("hours_de" if lang == "de" else "hours", "Öffnungszeiten" if lang == "de" else "Hours")):
                if p.get(key):
                    fields.append(f"<div><b>{title}:</b> {html.escape(p[key])}</div>")
            if p.get("website", "").startswith(("https://", "http://")):
                fields.append(f'<p><a href="{html.escape(p["website"], quote=True)}" target="_blank" rel="noopener noreferrer">{"Webseite" if lang == "de" else "Website"} ↗</a></p>')
            fields.append(f'<a href="{dest}" target="_blank" rel="noopener noreferrer">{link_text} ↗</a>')
            popup = "".join(fields)
            marker = folium.CircleMarker(
                location=[latitude, longitude], radius=7, color="#ffffff",
                weight=1.5, fill=True, fill_color=color, fill_opacity=0.95,
                popup=folium.Popup(popup, max_width=320), tooltip=p["name"],
            ).add_to(group)
            query = " ".join([p["name"], p["description"], p.get("description_de", ""), category]).lower()
            map_markers.append((p["id"], marker.get_name(), query))
        group.add_to(m)
        map_groups.append((category, group.get_name(), map_markers))
    registry = [{"category": cat, "group": grp, "markers": [
        {"id": pid, "layer": name, "search": query} for pid, name, query in markers
    ]} for cat, grp, markers in map_groups]
    script = """
    (function () {
      const map = MAP_OBJECT;
      const groups = REGISTRY;
      function findMarker(id) {
        for (const group of groups) for (const entry of group.markers) {
          if (String(entry.id) === String(id)) return {group, entry};
        }
        return null;
      }
      function applyFilter(category, term) {
        const needle = String(term || "").toLowerCase().trim();
        map.closePopup();
        groups.forEach(row => {
          const layerGroup = window[row.group];
          if (!layerGroup) return;
          const categoryMatches = category === "All" || row.category === category;
          row.markers.forEach(entry => {
            const marker = window[entry.layer];
            if (!marker) return;
            if (categoryMatches && (!needle || entry.search.includes(needle))) layerGroup.addLayer(marker);
            else layerGroup.removeLayer(marker);
          });
          if (categoryMatches) map.addLayer(layerGroup);
          else map.removeLayer(layerGroup);
        });
      }
      window.addEventListener("message", event => {
        if (event.origin !== window.location.origin || event.source !== window.parent) return;
        const data = event.data;
        if (!data) return;
        if (data.type === "hamburg-map-filter") applyFilter(data.category, data.term);
        if (data.type === "hamburg-map-focus") {
          const hit = findMarker(data.id);
          if (!hit) return;
          const group = window[hit.group.group], marker = window[hit.entry.layer];
          if (!marker || !group) return;
          if (!map.hasLayer(group)) map.addLayer(group);
          if (!group.hasLayer(marker)) group.addLayer(marker);
          map.flyTo(marker.getLatLng(), Math.max(map.getZoom(), 16), {duration: 0.6});
          marker.openPopup();
        }
      });
      window.parent.postMessage({type:"hamburg-map-ready"}, window.location.origin);
    })();
    """.replace("MAP_OBJECT", m.get_name()).replace("REGISTRY", json.dumps(registry, ensure_ascii=False))
    output_file = ROOT / output
    m.to_html(str(output_file))
    # Append the bridge AFTER Folium creates map, groups, and markers.
    rendered = output_file.read_text(encoding="utf-8")
    rendered = rendered.replace("</script>\n</html>", script + "\n</script>\n</html>")
    if "hamburg-map-ready" not in rendered:
        raise RuntimeError("Could not inject sidebar/map bridge after Leaflet initialization")
    output_file.write_text(rendered, encoding="utf-8")
    print(f"Exported {len(geo['features'])} places to {output}")
