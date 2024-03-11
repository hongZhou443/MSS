#! /usr/bin/python3

import re
import os
import contextily as ctx
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

GLOBE_MAP_PATH = gpd.datasets.get_path('naturalearth_lowres')
CALIFORNIA_MAP_PATH = "./data/California/CA_State_TIGER2016.shp"
US_MAP_PATH = "./data/tl_2023_us_state/tl_2023_us_state.shp"

WORLD_MAP = gpd.read_file(GLOBE_MAP_PATH).to_crs("EPSG:4326")
US_MAP = gpd.read_file(US_MAP_PATH).to_crs("EPSG:4326")
US_NON_CONT = ['HI','VI','MP','GU','AK','AS','PR']
US_CONT_MAP = US_MAP
for n in US_NON_CONT:
    US_CONT_MAP = US_CONT_MAP[US_CONT_MAP.STUSPS != n]

CA_MAP = gpd.read_file(CALIFORNIA_MAP_PATH).to_crs("EPSG:4326")

RUN_DOMAIN_TYPES = True

third_party_patterns = [
      re.compile("google", re.IGNORECASE),
      re.compile("outlook", re.IGNORECASE),
      re.compile("mimecast", re.IGNORECASE),
      re.compile("barracuda", re.IGNORECASE),
      re.compile("ppe-hosted", re.IGNORECASE),
      re.compile("pphosted", re.IGNORECASE),
      re.compile("sophos", re.IGNORECASE),
      re.compile("zoho", re.IGNORECASE),
      re.compile("spamexperts", re.IGNORECASE),
      re.compile("everycloudtech", re.IGNORECASE),
      ]

def is_domain_third_party(domain_name):
    for pattern in third_party_patterns:
        if re.search(pattern, domain_name) != None:
           return True
    return False

def run_analysis(gov_df, mx_df, a_df, geo_df, output_dir, force_plot):
    print("Summary Info:") 
    prefix = "Summary/"
    directory = output_dir+prefix
    if not os.path.exists(directory):
        os.makedirs(directory)

    report_statistics(gov_df, mx_df, a_df, geo_df, prefix, output_dir, force_plot)

    if RUN_DOMAIN_TYPES:
        grouped_by_types = gov_df.groupby('gov_Domain type')
        for val, df in grouped_by_types:
            print("Type: ", val)
            prefix = val + "/"
            directory = output_dir+prefix
            if not os.path.exists(directory):
                os.makedirs(directory)
            report_statistics(df, mx_df, a_df, geo_df, prefix, output_dir, force_plot)

def report_statistics(gov_df, mx_df, a_df, geo_df, output_prefix, output_dir, force_plot):

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

    anycast_df = with_a_record_df.loc[with_a_record_df['geo_anycast'] == True]
    print("\t# Domains Using Exchange with Anycast IP: ", len(anycast_df))
 
    print("\t# Unique Exchange ASN's: ", len(full_df['a_asn'].drop_duplicates()))

    # Preference Analysis
    full_df['mx_preference_rank'] = full_df.groupby('gov_domain')['mx_preference'].rank(method='dense', ascending=False)

    # Trying to determine third parties
    full_df['third party'] = full_df['mx_exchange'].map(is_domain_third_party)

    third_party_df = full_df.loc[full_df['third party'] == True]
    print("\t# Detected Third Party Mail Servers: ", len(third_party_df))
    print("\t% Detected Third Party Mail Servers: ", float(len(third_party_df) / len(full_df)) * 100.0, "%")
 
    fig = plt.figure()
    gb_domain = full_df.groupby('gov_domain')
    gb_domain['mx_exchange'].nunique().plot(kind='hist',
        title="Number of Domains with N Unqiue Mail Domains",
        xlabel="Number of Government Domains",
        ylabel="Number of Unique Mail Domains",
        range=(1,10), legend=False, color='green')
    plt.savefig(output_dir + '/' + output_prefix + ' Exchanges Per Domain Counts.png')
    plt.close(fig)

    fig = plt.figure()
    gb_domain = full_df.groupby('gov_domain')
    gb_domain[['geo_latitude','geo_longitude']].nunique().plot(kind='hist',
        title='CDF of Number of Unique Locations for a Government Domain',
        xlabel='Number of Locations',
        ylabel='Number of Government Domains',
        xticks=range(0,9),
        cumulative=True, density=True, bins=20, legend=False, color='orange')
    plt.savefig(output_dir + '/' + output_prefix + ' Location Count CDF.png')
    plt.close(fig)

    fig = plt.figure()
    gb_domain = full_df.groupby('gov_domain')
    gb_domain['a_asn'].nunique().plot(kind='hist',
        title='CDF of Number of AS serving a Government Domain',
        xlabel='Number of AS',
        ylabel='Number of Government Domains',
        xticks=range(0,5),
        cumulative=True, density=True, bins=20, legend=False, color='purple')
    plt.savefig(output_dir + '/' + output_prefix + ' ASN Count CDF.png')
    plt.close(fig)

    fig = plt.figure()
    gb_exchange = gov_mx_df.reset_index().groupby('mx_exchange')
    gb_exchange['gov_domain'].nunique().plot(kind='hist',
        title="Number of Mail Domains Serving N Unique Government Domains",
        xlabel="Number of Mail Domains",
        ylabel="Number of Unique Government Domains",
        legend=False, color='blue', bins=100, range=(0,500))
    plt.savefig(output_dir + '/' + output_prefix + ' Domains Per Exchange Counts.png')
    plt.close(fig)

    # Don't Count anycast IP's in this graph
    fig = plt.figure()
    gb_exchange_ip = full_df.loc[full_df['geo_anycast'] != True].reset_index().groupby('a_a_record')
    gb_exchange_ip['gov_domain'].nunique().plot(kind='hist',
        title="Number of Mail Server IP's Serving N Unqiue Government Domains",
        xlabel="Number of Mail Server IP's",
        ylabel="Number of Unique Government Servers",
        legend=False, color='red', bins=100, range=(0,500))
    plt.savefig(output_dir + '/' + output_prefix + ' Domains Per Exchange IP.png')
    plt.close(fig)

    # Maps
    geoplot(full_df.reset_index(), output_prefix, output_dir, force_plot)

def geoplot(df, output_prefix, output_dir, force):

    figsize = (20,12)
    markersize = 80

    globe_file = output_dir + "/" + output_prefix + " Globe.png"
    globe_preference_file = output_dir + "/" + output_prefix + " Globe Preference.png"
    us_file = output_dir + "/" + output_prefix + " US.png"
    us_preference_file = output_dir + "/" + output_prefix + " US Preference.png"
    ca_file = output_dir + "/" + output_prefix + " California.png"
    globe_heat_file = output_dir + "/" + output_prefix + " Heat Globe.png"

    s_loc_count = df.value_counts(subset=['geo_latitude','geo_longitude'], normalize=True).rename("loc_count")
    df = df.set_index(['geo_latitude','geo_longitude']).merge(s_loc_count, left_index=True, right_index=True).reset_index()

    geometry = [Point(xy) for xy in zip(df['geo_longitude'], df['geo_latitude'])]
    gdf = GeoDataFrame(df, geometry=geometry)   

    continental_us = df.loc[df['geo_latitude'] > 25]
    continental_us = continental_us.loc[continental_us['geo_latitude'] < 50]
    continental_us = continental_us.loc[continental_us['geo_longitude'] < -65]
    continental_us = continental_us.loc[continental_us['geo_longitude'] > -125]

    geometry = [Point(xy) for xy in zip(continental_us['geo_longitude'], continental_us['geo_latitude'])]
    continental_us_gdf = GeoDataFrame(continental_us, geometry=geometry)   

    if force or not os.path.isfile(globe_file):
        ax = WORLD_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        gdf.plot(column='gov_Domain type', ax=ax, marker='o', markersize=markersize, cmap='RdYlGn', legend=True); 
        plt.savefig(globe_file)

    if force or not os.path.isfile(globe_preference_file):
        ax = WORLD_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        gdf.plot(column='mx_preference_rank', ax=ax, marker='o', markersize=markersize, cmap='RdYlGn', legend=True); 
        plt.savefig(globe_preference_file)

    if force or not os.path.isfile(us_file):
        ax = US_CONT_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        continental_us_gdf.plot(column='gov_Domain type', ax=ax, marker='o', markersize=markersize, cmap='RdYlGn', legend=True);
        plt.savefig(output_dir + "/" + output_prefix + " US.png")

    if force or not os.path.isfile(us_preference_file):
        ax = US_CONT_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        continental_us_gdf.plot(column='mx_preference_rank', ax=ax, marker='o', markersize=markersize, cmap='RdYlGn', legend=True);
        plt.savefig(output_dir + "/" + output_prefix + " US Preference.png")

    if force or not os.path.isfile(ca_file):
        ax = CA_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        gdf.loc[gdf['geo_region'] == 'California'].plot(column='gov_Domain type', ax=ax, marker='o', markersize=markersize, cmap='RdYlGn', legend=True);
        plt.savefig(ca_file)

    if force or not os.path.isfile(globe_heat_file):
        ax = WORLD_MAP.plot(figsize=figsize,edgecolor='k',alpha=0.4) 
        gdf.plot(ax=ax, alpha = 0.3, markersize=gdf["loc_count"]*700, color='r'); 
        plt.savefig(globe_heat_file)

