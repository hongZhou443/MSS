
PYTHON:=python3
PDFLATEX:=pdflatex

SCRIPTS_DIR:=./scripts
DATA_DIR=./data

GOV_CSV=$(DATA_DIR)/registry-gov.csv
UK_CSV=$(DATA_DIR)/List_of_gov.uk_domains_as_of_30_March_2023.csv

gov_mx:
	@$(PYTHON) ./record_lookup.py $(GOV_CSV) -r MX -d "Domain name" -o $(DATA_DIR)/gov_mx_results.csv.tmp
	@mv $(DATA_DIR)/gov_mx_results.csv.tmp $(DATA_DIR)/gov_mx_results.csv

gov_mailserver_a:
	@$(PYTHON) ./record_lookup.py $(DATA_DIR)/gov_mx_results.csv -r A -d "exchange" -o $(DATA_DIR)/gov_mailserver_a_results.csv.tmp
	@mv $(DATA_DIR)/gov_mailserver_a_results.csv.tmp $(DATA_DIR)/gov_mailserver_a_results.csv

gov_txt:
	@$(PYTHON) ./record_lookup.py $(GOV_CSV) -r TXT -d "Domain name" -o $(DATA_DIR)/gov_txt_results.csv.tmp
	@mv $(DATA_DIR)/gov_txt_results.csv.tmp $(DATA_DIR)/gov_txt_results.csv

uk_mx:
	@$(PYTHON) ./record_lookup.py $(UK_CSV) -r MX -d "Domain: Domain Name" -o $(DATA_DIR)/gov_uk_mx_results.csv.tmp
	@mv $(DATA_DIR)/gov_uk_mx_results.csv.tmp $(DATA_DIR)/gov_uk_mx_results.csv

uk_mailserver_a:
	@$(PYTHON) ./record_lookup.py $(DATA_DIR)/gov_uk_mx_results.csv -r A -d "exchange" -o $(DATA_DIR)/gov_uk_mailserver_a_results.csv.tmp
	@mv $(DATA_DIR)/gov_uk_mailserver_a_results.csv.tmp $(DATA_DIR)/gov_uk_mailserver_a_results.csv
	
paper:
	@$(PDFLATEX) ./paper.tex

