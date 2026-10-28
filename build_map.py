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
          "Sights": "#469a89", "Harbor": "#428ec3", "Shops": "#b99c50", "Kodak Moments": "#527c9c"}
names_de = {"Food": "Essen", "Kneipen": "Kneipen", "Cocktails": "Cocktails",
            "Sights": "Sehenswertes", "Harbor": "Hafen", "Shops": "Läden", "Kodak Moments": "Kodak Moments"}

# Compact Lucide-style SVG pictograms inside understated, category-colored badges.
icon_paths = {
    "Food": '<path d="M4 3v7a3 3 0 0 0 6 0V3M7 3v18M19 3c-3 3-4 6-4 10h4v8"/>',
    "Kneipen": '<path d="M5 8h12v10a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3V8ZM17 9h2a3 3 0 0 1 0 6h-2M7 3v3M11 3v3M15 3v3"/>',
    "Cocktails": '<path d="m3 4 9 10 9-10H3ZM12 14v7M7 21h10M16 7l4-4"/>',
    "Sights": '<path d="m3 10 9-7 9 7M5 10v10h14V10M9 20v-7h6v7M3 20h18"/>',
    "Harbor": '<circle cx="12" cy="4" r="2"/><path d="M12 6v15M5 11H2l3 4M19 11h3l-3 4M3 15c1 4 4 6 9 6s8-2 9-6"/>',
    "Shops": '<path d="M4 9h16l-1-5H5L4 9ZM5 9v11h14V9M9 20v-7h6v7"/>',
    "Kodak Moments": '<path d="M3 7h4l2-3h6l2 3h4v13H3V7Z"/><circle cx="12" cy="13" r="4"/>',
}
def category_icon(category, color):
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           'width="19" height="19" fill="none" stroke="currentColor" '
           'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
           + icon_paths[category] + "</svg>")
    markup = (f'<div class="poi-symbol" style="background:{color}">'
              + svg + "</div>")
    return folium.DivIcon(html=markup, icon_size=(32, 32), icon_anchor=(16, 16),
                          popup_anchor=(0, -16), class_name="poi-div-icon")


for lang, output in (("en", "leafmap-map.html"), ("de", "leafmap-map-de.html")):
    m = leafmap.Map(center=[53.563, 9.987], zoom=12, fullscreen_control=False)
    # Fit every pin, including outlying locations, on desktop and mobile.
    coordinates = [feature["geometry"]["coordinates"] for feature in geo["features"]]
    m.fit_bounds(
        [[min(p[1] for p in coordinates), min(p[0] for p in coordinates)],
         [max(p[1] for p in coordinates), max(p[0] for p in coordinates)]],
        padding_top_left=(36, 36),
        padding_bottom_right=(36, 36),
    )
    # Minimal monochrome appearance for the raster basemap, preserving colored markers.
    m.get_root().header.add_child(folium.Element("""
    <style>
    .poi-div-icon { background: transparent; border: none; }\n    .poi-symbol { width: 30px; height: 30px; border: 2px solid #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; box-shadow: 0 1px 5px #34342f44; box-sizing: border-box; }\n    .leaflet-tile-pane img.leaflet-tile {
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
            fields = [f"<strong style='font-size:15px'>{html.escape(p['name'])}</strong>"]
            photo_url = p.get("photo_url", "")
            if p["category"] == "Kodak Moments" and photo_url.startswith("https://"):
                image_alt = html.escape(p.get("photo_alt_de" if lang == "de" else "photo_alt", p["name"]), quote=True)
                image_source = html.escape(photo_url, quote=True)
                fields.append(f'<img src="{image_source}" alt="{image_alt}" loading="lazy" style="display:block;width:100%;height:auto;max-height:195px;object-fit:cover;border-radius:4px;margin:10px 0" />')
                credit = p.get("photo_credit", "")
                credit_url = p.get("photo_credit_url", "")
                if credit:
                    if credit_url.startswith("https://"):
                        fields.append(f'<small style="display:block;margin-bottom:8px;color:#666"><a href="{html.escape(credit_url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(credit)}</a></small>')
                    else:
                        fields.append(f'<small style="display:block;margin-bottom:8px;color:#666">{html.escape(credit)}</small>')
            fields.append(f"<p>{html.escape(desc)}</p>")
            if p["category"] == "Kodak Moments":
                viewpoint = p["viewpoint_de"] if lang == "de" else p["viewpoint"]
                shot = p["photo_tip_de"] if lang == "de" else p["photo_tip"]
                light = p["best_light_de"] if lang == "de" else p["best_light"]
                fields.append(f"<div><b>{'Fotostandort' if lang == 'de' else 'Viewpoint'}:</b> {html.escape(viewpoint)}</div>")
                fields.append(f"<div><b>{'Motiv' if lang == 'de' else 'Photo idea'}:</b> {html.escape(shot)}</div>")
                fields.append(f"<div><b>{'Beste Zeit' if lang == 'de' else 'Best light'}:</b> {html.escape(light)}</div>")
            for key, title in (("address", "Adresse" if lang == "de" else "Address"),
                               ("phone", "Telefon" if lang == "de" else "Phone"),
                               ("hours_de" if lang == "de" else "hours", "Öffnungszeiten" if lang == "de" else "Hours")):
                if p.get(key):
                    fields.append(f"<div><b>{title}:</b> {html.escape(p[key])}</div>")
            if p.get("website", "").startswith(("https://", "http://")):
                fields.append(f'<p><a href="{html.escape(p["website"], quote=True)}" target="_blank" rel="noopener noreferrer">{"Webseite" if lang == "de" else "Website"} ↗</a></p>')
            fields.append(f'<a href="{dest}" target="_blank" rel="noopener noreferrer">{link_text} ↗</a>')
            popup = "".join(fields)
            marker = folium.Marker(
                location=[latitude, longitude], icon=category_icon(category, color),
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
