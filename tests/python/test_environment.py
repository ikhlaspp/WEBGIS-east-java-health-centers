import json
from pathlib import Path

import folium
import geopandas as gpd
from shapely.geometry import Point, shape


FIXTURE_DIRECTORY = Path(__file__).parents[1] / "data" / "wf-055"


def load_geometry(fixture_name: str):
    feature = json.loads((FIXTURE_DIRECTORY / fixture_name).read_text(encoding="utf-8"))
    assert feature["properties"]["synthetic"] is True
    return shape(feature["geometry"])


def test_python_gis_and_notebook_dependencies_import():
    assert gpd.__version__
    assert folium.__version__


def test_synthetic_point_is_inside_multipolygon():
    point = load_geometry("facility-point.geojson")
    boundary = load_geometry("district-multipolygon.geojson")

    assert isinstance(point, Point)
    assert boundary.geom_type == "MultiPolygon"
    assert boundary.is_valid

    facilities = gpd.GeoDataFrame(
        [{"fixture_id": "SYNTH-FAC-001"}],
        geometry=[point],
        crs="EPSG:4326",
    )

    assert facilities.geometry.within(boundary).tolist() == [True]
    assert boundary.covers(Point(113.95, -7.01)) is False
