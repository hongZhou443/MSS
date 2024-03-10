
import argparse as ap
import csv

VERBOSE = False

def split_csv(input_file, output_dir, column, verbose):

    open_files = []
    column_files = {}

    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            col_data = row[column]
            if not col_data in column_files:
                new_file_name = output_dir + "/" + str(col_data).lower() + ".csv"
                new_file = open(new_file_name, 'w', newline='')
                open_files.append(new_file)
                column_files[col_data] = csv.DictWriter(new_file, fieldnames=list(dict(row).keys()))
                column_files[col_data].writeheader()
            column_files[col_data].writerow(row)
    
    for file in open_files:
        file.close()

def main():
    parser = ap.ArgumentParser(description="Split CSV into multiple CSV's based on a column")
    parser.add_argument("input_file", metavar="[IN]", type=str, help="Input CSV File")
    parser.add_argument("-o", "--output-dir", metavar="[OUT-DIR]", type=str, default="./split", help="Output Directory")
    parser.add_argument("-c", "--column", metavar="[COLUMN]", type=str, default="", help="Column to split on")
    parser.add_argument("-v", "--verbose", action='store_true', help="Verbose Output")

    args = parser.parse_args()

    split_csv(args.input_file, args.output_dir, args.column, args.verbose)

if __name__ == "__main__":
    main()

