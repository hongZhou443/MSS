#! /usr/bin/python3

import os
import geoip2.database as geodb
import argparse as ap
import csv
import rich.progress as rprog

VERBOSE = False
MAXMIND_USER_ID = ""
MAXMIND_KEY = ""
GEOLITE_COUNTRY_DB = "./data/geolite2/GeoLite2-Country_20240220/GeoLite2-Country.mmdb"
GEOLITE_CITY_DB = "./data/geolite2/GeoLite2-City_20240220/GeoLite2-City.mmdb"
GEOLITE_ASN_DB = "./data/geolite2/GeoLite2-ASN_20240220/GeoLite2-ASN.mmdb"

def geolocate_ip(ip, client):
    response = client.city(ip)
    row = {}
    row["ip"] = ip
    row["city_name"] = response.city.name
    row["country_name"] = response.country.name
    row["country_iso_code"] = response.country.iso_code
    row["most_specific_name"] = response.subdivisions.most_specific.name
    row["most_specific_iso_code"] = response.subdivisions.most_specific.iso_code
    row["latitude"] = response.location.latitude
    row["longitude"] = response.location.longitude
    row["postal"] = response.postal.code
    row["network"] = str(response.traits.network)
    return row

def geolocate(ips):
    geo_data = []

    MAXMIND_USER_ID = os.environ['MAXMIND_USER_ID']
    MAXMIND_KEY = os.environ['MAXMIND_KEY']

    with rprog.Progress(
                rprog.TextColumn("[progress.description]{task.description}"),
                rprog.BarColumn(),
                rprog.TaskProgressColumn(),
                rprog.MofNCompleteColumn() 
            ) as progress:

        query_task = progress.add_task("[cyan]Running Queries...", total=len(ips))
        success_task = progress.add_task("[green]Responses ", total=len(ips))
        fail_task = progress.add_task("[red]Failures ", total=len(ips))

        with geodb.Reader(GEOLITE_CITY_DB) as client:
            for ip in ips:
                try:
                    row = geolocate_ip(ip, client)
                    progress.advance(success_task)
                    geo_data.append(row)
                except:
                    progress.advance(fail_task)

                progress.advance(query_task)

    return geo_data

def main():
    parser = ap.ArgumentParser()
    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("-o", "--output-file", metavar="[OUT]", type=str, default="out.csv", help="Output CSV File")
    parser.add_argument("-i", "--ip-column", metavar="[COLUMN_NAME]", type=str, default="Domain", help="CSV Column Containing IP Addresses")
    parser.add_argument("-v", "--verbose", help="Verbose Output")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    ip_col = args.ip_column
    VERBOSE = args.verbose

    print(f"Reading Input from File: {input_file}")
    print(f"Writing Output to File: {output_file}")

    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        input_data = [row for row in reader]

    ips = [row[ip_col] for row in input_data]

    geo_data = geolocate(ips)

    with open(output_file, 'w') as output_csvfile:
        if len(geo_data) == 0:
            return
        csv_writer = csv.DictWriter(output_csvfile, fieldnames=list(geo_data[0].keys()))
        csv_writer.writeheader()
        for row in geo_data:
            csv_writer.writerow(row)

if __name__ == "__main__":
    main()

