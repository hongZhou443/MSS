#! /usr/bin/python3

import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

GLOBE_MAP_PATH = gpd.datasets.get_path('naturalearth_lowres')

def run_analysis(gov_df, mx_df, a_df, geo_df, output_dir):
    print("Summary Info:") 
    report_statistics(gov_df, mx_df, a_df, geo_df, "All ", output_dir)

    grouped_by_types = gov_df.groupby('gov_Domain type')
    for val, df in grouped_by_types:
        print("Type: ", val)
        report_statistics(df, mx_df, a_df, geo_df, val, output_dir)

def report_statistics(gov_df, mx_df, a_df, geo_df, output_prefix, output_dir):

    unique_gov = len(gov_df.reset_index()['gov_domain'].drop_duplicates())
    print("\t# Domains: ", unique_gov)
    gov_mx_df = gov_df.set_index("gov_domain").join(mx_df.set_index("mx_queried"), how='left')
    gov_with_mx_df = gov_mx_df.reset_index().dropna(subset='mx_exchange')
    unique_gov_with_mx_df = gov_with_mx_df['gov_domain'].drop_duplicates()
    print("\t# Domains with at least 1 mailserver: ", len(unique_gov_with_mx_df))

    gov_mx_a_df = gov_with_mx_df.set_index('mx_exchange').join(a_df.set_index('a_queried'), how='left')
    full_df = gov_mx_a_df.reset_index().set_index('a_a_record').join(geo_df.reset_index().set_index('geo_ip'), how='left')

    all_exchanges = full_df['mx_exchange'].drop_duplicates()
    print("\t# Unqiue Exchange Domains: ", len(all_exchanges))

    with_a_record_df = full_df.reset_index().dropna(subset='a_a_record')
    exchanges = with_a_record_df['mx_exchange'].drop_duplicates()
    print('\t# Exchanges whose A record lookup failed: ', len(all_exchanges) - len(exchanges))

    location_df = with_a_record_df.drop_duplicates(subset=['geo_latitude','geo_longitude'])
    location_df = location_df.dropna(subset='geo_country')
    print("\t# Unique Locations (which had at least a country code): ", len(location_df))

    us_locations_df = location_df.loc[location_df['geo_country'] == 'US']
    foreign_locations_df = location_df.loc[location_df['geo_country'] != 'US']

    print("\t# US Locations: ", len(us_locations_df))
    print("\t# Foreign Locations: ", len(foreign_locations_df))
    print(foreign_locations_df)

    anycast_df = with_a_record_df.loc[with_a_record_df['geo_anycast'] == True]
    print("\t# Domains Using Exchange with Anycast IP: ", len(anycast_df))
   
    df = full_df.reset_index()

    geometry = [Point(xy) for xy in zip(df['geo_longitude'], df['geo_latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)   
   
    world = gpd.read_file(GLOBE_MAP_PATH)
    gdf.plot(column=gdf['gov_Domain type'], ax=world.plot(figsize=(10, 6)), marker='o', markersize=15, cmap='RdYlGn', legend=True);
    
    plt.savefig(output_dir + "/" + output_prefix + " Locations.jpg")

