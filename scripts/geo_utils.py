import geopandas as gpd
from shapely.geometry import Point
import streamlit as st

@st.cache_data
def load_geodata():
    gdf_gouv = gpd.read_file("data/TN-gouvernorats.geojson")
    gdf_del = gpd.read_file("data/TN-delegations_raw.geojson")
    return gdf_gouv, gdf_del

def find_clicked_delegation(click_coords, gdf):
    if not click_coords or 'lat' not in click_coords or 'lng' not in click_coords:
        return None
    
    point = Point(click_coords['lng'], click_coords['lat'])
    for _, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return row
    return None
