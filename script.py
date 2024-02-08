import subprocess
import csv
import re

def nslookup(url):
    try:
        pattern = r'mail exchanger = (\S+)'
        result = subprocess.check_output(['nslookup', '-type=mx', url]).decode('utf-8')
        result = re.findall(pattern, result)
        return result
    except subprocess.CalledProcessError:
        return 'Error: Unable to resolve'

def main():
    input_file = 'urls.txt'
    output_file = 'nslookup_results.csv'

    with open(input_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['domain', '-type=mx records'])

        for url in urls:
            results = nslookup(url)
            for result in results:
                writer.writerow([url, result])

    print(f'NSLookup results written to {output_file}')

if __name__ == "__main__":
    main()
