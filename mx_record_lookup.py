import dns
import dns.resolver

import subprocess
import csv
import re

def main():
    input_file = 'urls.txt'
    output_file = 'nslookup_results.csv'

    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['domain', 'exchange'])

        for url in urls:
            query_results = dns.resolver.resolve(url, "MX")
            for rr in query_results:
                writer.writerow([url,str(rr.exchange).rstrip(".")])

    print(f'NSLookup results written to {output_file}')

if __name__ == "__main__":
    main()
