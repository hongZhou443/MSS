#! /usr/bin/python3

import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import argparse as ap
import csv

def main():
    parser = ap.ArgumentParser()
    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("-o", "--output-file", metavar="[OUT]", type=str, default="out.jpg", help="Output Image File")
    parser.add_argument("-lat", "--latitude-column", metavar="[COLUMN_NAME]", type=str, default="latitude", help="CSV Column Containing Latitudes")
    parser.add_argument("-lon", "--longitude-column", metavar="[COLUMN_NAME]", type=str, default="longitude", help="CSV Column Containing Longitudes")
    parser.add_argument("--static", action='store_true', default=True, help="Output static image")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    lat_col = args.latitude_column
    lon_col = args.longitude_column
    global VERBOSE
    VERBOSE = args.verbose

    df = pd.read_csv(input_file, delimiter=',', skiprows=0, low_memory=False)
    print(df[lat_col])
    print(df[lon_col])
    
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = GeoDataFrame(df, geometry=geometry)   
   
    if args.static:
        import matplotlib.pyplot as plt
        world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
        gdf.plot(ax=world.plot(figsize=(10, 6)), marker='o', color='red', markersize=15);
        plt.savefig(output_file)
    else:
        import folium as fl

        
if __name__ == "__main__":
    main()

