"""Regenerate a standalone Hamburg map using Qiusheng Wu's leafmap Folium backend.

Install: pip install leafmap folium
Run:     python build_map.py
Output:  leafmap-map.html (optional standalone alternative to the custom homepage)
The public homepage reads the same GeoJSON and uses Leaflet directly for responsive filtering.
"""
from pathlib import Path
import json
import html
import folium
import leafmap.foliumap as leafmap

ROOT = Path(__file__).resolve().parent
geo = json.loads((ROOT / "data/hamburg_places.geojson").read_text(encoding="utf-8"))
colors = {"Food": "#eaa45f", "Kneipen": "#e05d5a", "Cocktails": "#ac8ce3",
          "Sights": "#469a89", "Harbor": "#428ec3", "Shops": "#b99c50"}
m = leafmap.Map(center=[53.563, 9.987], zoom=12)
for category, color in colors.items():
    group = folium.FeatureGroup(name=category, show=True)
    for feature in geo["features"]:
        p = feature["properties"]
        if p["category"] != category:
            continue
        longitude, latitude = feature["geometry"]["coordinates"]
        dest = "https://www.google.com/maps/search/?api=1&query=" + __import__("urllib.parse", fromlist=["quote"]).quote(p["name"] + ", Hamburg Germany")
        popup = (f"<b>{html.escape(p['name'])}</b><p>{html.escape(p['description'])}</p>"
                 f'<a href="{dest}" target="_blank" rel="noopener noreferrer">Directions</a>')
        folium.CircleMarker(
            location=[latitude, longitude], radius=7, color="#ffffff",
            weight=1.5, fill=True, fill_color=color, fill_opacity=0.95,
            popup=folium.Popup(popup, max_width=320),
            tooltip=p["name"],
        ).add_to(group)
    group.add_to(m)
folium.LayerControl(collapsed=False).add_to(m)
m.to_html(str(ROOT / "leafmap-map.html"))
print(f"Exported {len(geo['features'])} places to leafmap-map.html")
