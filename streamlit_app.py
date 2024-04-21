# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import inspect
import textwrap
from urllib.error import URLError

import pandas as pd
import geopandas as gpd
import pydeck as pdk
import streamlit as st


def show_code(demo):
    """Show the code of the demo."""
    show_code = st.sidebar.checkbox("Show code", True)
    if show_code:
        # Showing the code of the demo.
        st.markdown("## Code")
        sourcelines, _ = inspect.getsourcelines(demo)
        st.code(textwrap.dedent("".join(sourcelines[1:])))


def mapping_demo():
    try:
        ALL_LAYERS = {
            "state": polygon,

        }
        st.sidebar.markdown("### Map Layers")
        selected_layers = [
            layer
            for layer_name, layer in ALL_LAYERS.items()
            if st.sidebar.checkbox(layer_name, True)
        ]
        if selected_layers:
            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v9",
                    initial_view_state=view_state,
                    layers=selected_layers,
                )
            )
        else:
            st.error("Please choose at least one layer above.")
    except URLError as e:
        st.error(
            """
            **This demo requires internet access.**
            Connection error: %s
        """
            % e.reason
        )


# Load data from a JSON file into a pandas DataFrame
# The parameters are set to ensure that the data is loaded as strings without any conversion
df = pd.read_json("sample.json", orient="index", convert_dates=False,
                  keep_default_dates=False, convert_axes=False, dtype=int, precise_float=False, date_unit=None, )
# Reset the index of the DataFrame
df.reset_index(inplace=True)
# Rename the columns of the DataFrame
df.columns = ["GEOID", "population"]

# Load a GeoJSON file into a GeoDataFrame
gdf = gpd.read_file('mi1.json', geometry='geometry')
# Merge the DataFrame and GeoDataFrame on the 'GEOID' column
gdf = gdf.merge(df, on='GEOID')
gdf["color"] = gdf['population'] / gdf['population'].max()

# Create a new GeoDataFrame for the centroids of the geometries in the original GeoDataFrame
# Also, copy the 'population' column from the original GeoDataFrame
centroids = gpd.GeoDataFrame(geometry=gdf.centroid, crs=gdf.crs)
centroids["population"] = gdf['population']

# Define the initial view state for the pydeck visualization
# The latitude and longitude are set to the mean of the y and x coordinates of the centroids, respectively
view_state = pdk.ViewState(latitude=centroids.centroid.y.mean(), longitude=centroids.centroid.x.mean(), zoom=6,
                           max_zoom=12)

# Define a GeoJsonLayer for the geometries in the original GeoDataFrame
polygon = pdk.Layer("GeoJsonLayer", gdf, stroked=True, filled=True, opacity=0.7, get_line_color=[255, 0, 0],
                    get_fill_color="[255, 140, 0, 254 * color]",
                    line_width_min_pixels=2)

st.set_page_config(page_title="Mapping Demo", page_icon="🌍")
st.markdown("# Mapping Demo")
st.write(
    """This demo shows how to use
[`st.pydeck_chart`](https://docs.streamlit.io/library/api-reference/charts/st.pydeck_chart)
to display geospatial data."""
)

mapping_demo()

show_code(mapping_demo)
