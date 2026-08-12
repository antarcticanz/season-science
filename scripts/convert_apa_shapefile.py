"""Convert APA_shape_2024 shapefile to simplified WGS84 GeoJSON.

Reads assets/APA_shape_2024/APA_shape_2024.shp (EPSG:3031), reprojects to
EPSG:4326, simplifies at 0.0005 degrees (~55 m), splits by Tipo_apa, and
writes two GeoJSON files consumed by ol-map.js:
  assets/APA_ASPA.geojson
  assets/APA_ASMA.geojson

Re-run whenever the source shapefile changes. Requires geopandas + pyogrio.
"""
import json
import os

import geopandas as gpd

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))
SRC = os.path.join(ASSETS, "APA_shape_2024", "APA_shape_2024.shp")

KEEP_PROPS = ("Name", "Tipo_apa", "Marine", "Area_km", "Numero_apa")
SIMPLIFY_TOL_DEG = 0.0005


def _to_geojson(subset):
    features = []
    for _, row in subset.iterrows():
        props = {}
        for key in KEEP_PROPS:
            val = row.get(key)
            if hasattr(val, "item"):
                val = val.item()
            props[key] = val
        features.append({
            "type": "Feature",
            "properties": props,
            "geometry": row["geometry"].__geo_interface__,
        })
    return {"type": "FeatureCollection", "features": features}


def main():
    gdf = gpd.read_file(SRC, engine="pyogrio").to_crs(4326)
    gdf["geometry"] = gdf.geometry.simplify(SIMPLIFY_TOL_DEG, preserve_topology=True)

    for tipo, out_name in (("ASPA", "APA_ASPA.geojson"), ("ASMA", "APA_ASMA.geojson")):
        subset = gdf[gdf["Tipo_apa"] == tipo]
        out_path = os.path.join(ASSETS, out_name)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(_to_geojson(subset), f)
        print(f"wrote {out_path} ({len(subset)} features, {os.path.getsize(out_path):,} bytes)")


if __name__ == "__main__":
    main()
