
PYTHON:=python3
PDFLATEX:=pdflatex

DATA_DIR=./data
GOV_CSV=$(DATA_DIR)/registry-gov.csv

gov_mx:
	@$(PYTHON) ./record_lookup.py $(GOV_CSV) -r MX -d "Domain name" -o $(DATA_DIR)/gov_mx_results.csv.tmp
	@mv $(DATA_DIR)/gov_mx_results.csv.tmp $(DATA_DIR)/gov_mx_results.csv

gov_txt:
	@$(PYTHON) ./record_lookup.py $(GOV_CSV) -r TXT -d "Domain name" -o $(DATA_DIR)/gov_txt_results.csv.tmp
	@mv $(DATA_DIR)/gov_txt_results.csv.tmp $(DATA_DIR)/gov_txt_results.csv

	
paper:
	@$(PDFLATEX) ./paper.tex

