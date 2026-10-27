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
    m = leafmap.Map(center=[53.563, 9.987], zoom=12)
    # Minimal monochrome appearance for the raster basemap, preserving colored markers.
    m.get_root().header.add_child(folium.Element("""
    <style>
    .leaflet-tile-pane img.leaflet-tile {
      filter: grayscale(100%) saturate(0%) contrast(82%) brightness(110%);
    }
    </style>
    """))
    for category, color in colors.items():
        label = names_de[category] if lang == "de" else category
        group = folium.FeatureGroup(name=label, show=True)
        for feature in geo["features"]:
            p = feature["properties"]
            if p["category"] != category:
                continue
            longitude, latitude = feature["geometry"]["coordinates"]
            dest = "https://www.google.com/maps/search/?api=1&query=" + quote(p["name"] + ", Hamburg Germany")
            desc = p.get("description_de", p["description"]) if lang == "de" else p["description"]
            link_text = "Route anzeigen" if lang == "de" else "Directions"
            popup = (f"<b>{html.escape(p['name'])}</b><p>{html.escape(desc)}</p>"
                     f'<a href="{dest}" target="_blank" rel="noopener noreferrer">{link_text}</a>')
            folium.CircleMarker(
                location=[latitude, longitude], radius=7, color="#ffffff",
                weight=1.5, fill=True, fill_color=color, fill_opacity=0.95,
                popup=folium.Popup(popup, max_width=320), tooltip=p["name"],
            ).add_to(group)
        group.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    m.to_html(str(ROOT / output))
    print(f"Exported {len(geo['features'])} places to {output}")
