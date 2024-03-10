#! /usr/bin/python3

import os
import argparse as ap

import asyncio

import pandas as pd
import rich.progress as rprog

VERBOSE = False
GEOLITE_COUNTRY_DB = "./data/geolite2/GeoLite2-Country_20240220/GeoLite2-Country.mmdb"
GEOLITE_CITY_DB = "./data/geolite2/GeoLite2-City_20240220/GeoLite2-City.mmdb"
GEOLITE_ASN_DB = "./data/geolite2/GeoLite2-ASN_20240220/GeoLite2-ASN.mmdb"

def geolite_geolocate_ip(ip, client):
    response = client.city(ip)
    return {
        "ip" : ip,
        "city_name" : response.city.name,
        "country_name" : response.country.name,
        "country_iso_code" : response.country.iso_code,
        "most_specific_name" : response.subdivisions.most_specific.name,
        "most_specific_iso_code" : response.subdivisions.most_specific.iso_code,
        "longitude" : response.location.latitude,
        "latitude" : response.location.longitude,
        "postal" : response.postal.code,
        "network" : str(response.traits.network)
    }

def geolite_geolocate(ips):
    import geoip2.database as geodb
    geo_data = []

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
                    row = geolite_geolocate_ip(ip, client)
                    progress.advance(success_task)
                    geo_data.append(row)
                except:
                    progress.advance(fail_task)

                progress.advance(query_task)

    geo_df = pd.DataFrame(geo_data)
    return geo_df

IPINFO_SEM = asyncio.Semaphore(128)
async def ipinfo_geolocate_ip(ip, handler, progress, query_task, success_task, fail_task):
    async with IPINFO_SEM:
        progress.advance(query_task)
        try:
            details = await handler.getDetails(ip)
            progress.advance(success_task)
        except:
            progress.advance(fail_task)
            return None
        df = pd.json_normalize(details.all, sep='_')
        return df.to_dict(orient="records")[0]

IPFINO_ACCESS_TOKEN = None

async def ipinfo_geolocate(ips):
    import ipinfo

    handler = ipinfo.getHandlerAsync(IPINFO_ACCESS_TOKEN)
    geo_data = []

    with rprog.Progress(
                rprog.TextColumn("[progress.description]{task.description}"),
                rprog.BarColumn(),
                rprog.TaskProgressColumn(),
                rprog.MofNCompleteColumn() 
            ) as progress:

        query_task = progress.add_task("[cyan]Running Queries...", total=len(ips))
        success_task = progress.add_task("[green]Responses ", total=len(ips))
        fail_task = progress.add_task("[red]Failures ", total=len(ips))

        coroutines = []

        for ip in ips:
            coroutines.append(ipinfo_geolocate_ip(ip, handler, progress, query_task, success_task, fail_task))

        geo_data = await asyncio.gather(*coroutines)
        geo_data = [x for x in geo_data if x is not None]

    geo_df = pd.DataFrame(geo_data)
    return geo_df

async def ipinfo_geolocation(df, ip_col):
    ips = df[ip_col]
    ips = ips.drop_duplicates()
    return await ipinfo_geolocate(ips)

async def geolite_geolocation(df, ip_col):
    ips = df[ip_col]
    ips = ips.drop_duplicates()
    return geolite_geolocate(ips)

