#! /usr/bin/python3

import asyncio

import os
from record_lookup import run_record_lookup
from map_ip_to_asn import add_asns
import geolocation
import analysis

import pandas as pd
import argparse as ap

MX_RECORD_CSV = "mx_records.csv"
A_RECORD_CSV = "mx_ip.csv"
GEOLITE_GEO_CSV = "geolite_mx_geo.csv"
IPINFO_GEO_CSV = "ipinfo_mx_geo.csv"

async def main():

    parser = ap.ArgumentParser(description="Run all analyses on a set of domains and output to a directory")
    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("-o", "--output-dir", metavar="[OUT-DIR]", type=str, default="./driver_results", help="Output Directory")
    parser.add_argument("-d", "--domain-column", metavar="[COLUMN_NAME]", type=str, default="Domain", help="CSV Column Containing Domains")
    parser.add_argument("-f", "--force", action='store_true', default=False, help="Force Re-Gather Data")
    parser.add_argument("-i", "--ipinfo", action='store_true', default=False, help="Use IP-Info")
    parser.add_argument("-a", "--ipinfo_access_token", type=str, help="IP-Info Access Token")

    args = parser.parse_args()
    input_file = args.input_file
    output_dir = args.output_dir + "/"
    domain_col = args.domain_column
    force = args.force

    ipinfo = args.ipinfo

    geo_csv = GEOLITE_GEO_CSV
    run_geolocation = geolocation.geolite_geolocation

    if ipinfo:
        geolocation.IPINFO_ACCESS_TOKEN = args.ipinfo_access_token
        geo_csv = IPINFO_GEO_CSV
        run_geolocation = geolocation.ipinfo_geolocation

    df = pd.read_csv(input_file)
    df = df.rename(columns={domain_col : "domain"})

    redid_data = False

    if not force and os.path.isfile(output_dir + MX_RECORD_CSV):
        mx_record_df = pd.read_csv(output_dir + MX_RECORD_CSV)
    else:
        mx_record_df = await run_record_lookup(df.set_index("domain"), "MX")
        mx_record_df.to_csv(output_dir + MX_RECORD_CSV)
        redid_data = True

    if not force and os.path.isfile(output_dir + A_RECORD_CSV):
        a_record_df = pd.read_csv(output_dir + A_RECORD_CSV)
    else:
        a_record_df = await run_record_lookup(mx_record_df.set_index("exchange"), "A")
        a_record_df = await add_asns(a_record_df, "a_record")
        a_record_df.to_csv(output_dir + A_RECORD_CSV)
        redid_data = True

    if not force and os.path.isfile(output_dir + geo_csv):
        geo_df = pd.read_csv(output_dir + geo_csv)
    else:
        geo_df = await run_geolocation(a_record_df, "a_record")
        geo_df.to_csv(output_dir + geo_csv)
        redid_data = True

    df = df.add_prefix("gov_")
    mx_record_df = mx_record_df.add_prefix("mx_")
    a_record_df = a_record_df.add_prefix("a_")
    geo_df = geo_df.add_prefix("geo_")

    analysis.run_analysis(df, mx_record_df, a_record_df, geo_df, output_dir, redid_data)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

