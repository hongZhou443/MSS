#! /usr/bin/python3

import asyncio
import dns
import dns.resolver
import dns.asyncresolver

import pandas as pd

import rich.progress as rprog

def mx_handler(rr):
    return {
            "exchange" : rr.exchange,
            "preference" : rr.preference,
            "class" : dns.rdataclass.to_text(rr.rdclass),
            "type" : dns.rdatatype.to_text(rr.rdtype)
            }

def txt_handler(rr):
    return { "strings" : str(rr.strings) }

def a_handler(rr):
    return {"a_record" : rr.to_text()}

NUM_QUERIES_AT_ONCE = 16
QUERY_SEM = asyncio.Semaphore(NUM_QUERIES_AT_ONCE)

async def run_query(domain, record_type, progress, sent_task, success_task, fail_task):
    async with QUERY_SEM:
        MAX_ATTEMPTS = 1
        attempts = 0
        progress.advance(sent_task)
        while attempts < MAX_ATTEMPTS:
             try:
                 result = await dns.asyncresolver.resolve(domain, record_type, raise_on_no_answer=False)
                 progress.advance(success_task)
                 return result
             except (dns.resolver.NoNameservers,
                     dns.resolver.NoAnswer,
                     dns.resolver.LifetimeTimeout):
                 progress.advance(fail_task)
                 return None
             except:
                 attempts += 1
                 continue
        progress.advance(fail_task)
        return None

async def run_queries(df, record_type, handler):
    results = []
    failures = []

    percent_displayed = 0
    num_queried = 0

    df = df[~df.index.duplicated(keep='first')]

    with rprog.Progress(
                rprog.TextColumn("[progress.description]{task.description}"),
                rprog.BarColumn(),
                rprog.TaskProgressColumn(),
                rprog.MofNCompleteColumn()
            ) as progress:
        query_task = progress.add_task("[cyan]Running Queries...", total=len(df.index))
        success_task = progress.add_task("[green]Responses ", total=len(df.index))
        fail_task = progress.add_task("[red]Failures ", total=len(df.index))

        domains = []
        coroutines = []

        for index, row in df.iterrows():
            domain = index
            coroutines.append(run_query(domain, record_type, progress, query_task, success_task, fail_task))
            domains.append(domain)

        query_results_list = await asyncio.gather(*coroutines)

        rdicts = []
        for query_result, domain in zip(query_results_list, domains):
            if query_result == None:
                continue
            for rr in query_result:
                rdict = handler(rr)
                rdict['queried'] = domain
                rdicts.append(rdict)

    rdf = pd.DataFrame.from_dict(rdicts)
    return rdf.set_index('queried')

handlers = {
    "MX" : mx_handler,
    "TXT" : txt_handler,
    "A" : a_handler
    }

async def run_record_lookup(df, record_type):

    if not record_type in handlers.keys():
        print(f"Could not find handler for Record Type: {record_type}!")
        return
    handler = handlers[record_type]

    print(f"Querying {record_type} Records...")

    rdf = await run_queries(df,record_type,handler)

    return rdf
