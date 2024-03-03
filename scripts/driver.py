#! /usr/bin/python3

import record_lookup
import geolocation
import geoplot

import argparse as ap

def main():

    parser = ap.ArgumentParser(description="Run all analyses on a set of domains and output to a directory")
    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("output_dir", metavar="[OUT-DIRECTORY]", type=str, help="Output Directory")

    parser.add_argument("-d", "--domain-column", metavar="[COLUMN_NAME]", type=str, default="Domain", help="CSV Column Containing Domains")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()
    input_file = args.input_file
    output_dir = args.output_dir
    domain_col = args.domain_col
    verbose = args.verbose

    mx_record_output_file = output_dir + "/mx_records.csv"
    mx_ip_output_file = output_dir + "/mx_ip.csv"
    mx_geo_output_file = output_dir + "/mx_geo.csv"
    mx_static_plot_output_file = output_dir + "/mx_static_plot.jpg"

    record_lookup.run(input_file, mx_record_output_file, "MX", domain_col, verbose)
    record_lookup.run(mx_record_output_file, mx_ip_output_file, "A", record_lookup.MX_EXCHANGE_COL, verbose)

    geolocation.run(mx_ip_output_file, mx_geo_output_file, record_lookup.A_IP_COL, verbose)

    geoplot.run(mx_ip_output_file,mx_static_plot_output_file, geolocation.LAT_COL, geolocation.LON_COL, True, verbose)

if __name__ == "__main__":
    main()

