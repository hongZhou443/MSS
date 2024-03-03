#! /usr/bin/python3

import dns
import dns.resolver
import csv
import argparse as ap
import rich.progress as rprog

VERBOSE = False

def mx_handler(url, rr, prog):
    data = {}
    data["url"] = url
    data["exchange"] = rr.exchange
    data["preference"] = rr.preference
    data["class"] = dns.rdataclass.to_text(rr.rdclass)
    data["type"] = dns.rdatatype.to_text(rr.rdtype)
    return data

def txt_handler(url, rr, prg):
    data = {}
    data["url"] = url
    data["strings"] = str(rr.strings)
    return data

def a_handler(url, rr, prg):
    data = {}
    data["url"] = url
    data["ipv4"] = rr.to_text()
    return data

def run_queries(input_data, dom_col, record_type, handler):
    results = []
    failures = []

    percent_displayed = 0
    num_queried = 0

    with rprog.Progress(
                rprog.TextColumn("[progress.description]{task.description}"),
                rprog.BarColumn(),
                rprog.TaskProgressColumn(),
                rprog.MofNCompleteColumn()
            ) as progress:
        query_task = progress.add_task("[cyan]Running Queries...", total=len(input_data))
        success_task = progress.add_task("[green]Responses ", total=len(input_data))
        fail_task = progress.add_task("[red]Failures ", total=len(input_data))

        for row in input_data:
            url = row[dom_col]
            try:
                if VERBOSE:
                    progress.console.print(f"Querying \"{url}\"...")
                query_results = dns.resolver.resolve(url, record_type)
                if VERBOSE:
                    progress.console.print(f"[green][SUCCESS] \"{url}\"...")
                progress.advance(success_task)
                for rr in query_results:
                    results.append(handler(url, rr, progress))
            except:
                if VERBOSE:
                    progress.console.print(f"[red][FAILED] \"{url}\"")
                progress.advance(fail_task)
                failures.append(row)

            progress.advance(query_task)

    return (results,failures)

handlers = {
    "MX" : mx_handler,
    "TXT" : txt_handler,
    "A" : a_handler
    }

def main():
    parser = ap.ArgumentParser(description="run DNS record lookups on a set of input domains")

    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("-o", "--output-file", metavar="[OUT]", type=str, default="out.csv", help="Output CSV File")
    parser.add_argument("-r", "--record-type", metavar="[RECORD_TYPE]", type=str, default="MX", help="DNS Record Type to Query")
    parser.add_argument("-d", "--domain-column", metavar="[COLUMN_NAME]", type=str, default="Domain", help="CSV Column Containing Domains")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    record_type = args.record_type
    domain_col = args.domain_column
    global VERBOSE
    VERBOSE = args.verbose

    if not record_type in handlers.keys():
        print(f"Could not find handler for Record Type: {record_type}!")
        return

    handler = handlers[record_type]

    print(f"Reading Input from File: {input_file}")
    print(f"Writing Output to File: {output_file}")

    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        input_data = [row for row in reader]

    print(f"Querying {record_type} Records of Domains in {input_file}...")
    results, failures = run_queries(input_data,domain_col,record_type,handler)

    with open(output_file, 'w', newline='') as csvfile:
        if len(results) == 0:
            return

        csv_writer = csv.DictWriter(csvfile, fieldnames=list(results[0].keys()))
        csv_writer.writeheader()
        for result in results:
            csv_writer.writerow(result)

if __name__ == "__main__":
    main()
