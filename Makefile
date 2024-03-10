
-include personal_config.mk

PYTHON:=python3
PDFLATEX:=pdflatex

ROOT_DIR:=$(shell pwd)
SCRIPTS_DIR:=./scripts
DATA_DIR:=./data
OUTPUT_DIR=./results

US_CSV=$(DATA_DIR)/registry-gov.csv
US_CITY_CSV=$(DATA_DIR)/US/city.csv
UK_CSV=$(DATA_DIR)/List_of_gov.uk_domains_as_of_30_March_2023.csv

default: paper

paper: FORCE
	@make -C $(PAPER_DIR) paper

us_geolite:
	@mkdir -p $(OUTPUT_DIR)/US
	@$(PYTHON) $(SCRIPTS_DIR)/driver.py $(US_CSV) -d "Domain name" -o $(OUTPUT_DIR)/US

us:
	@mkdir -p $(OUTPUT_DIR)/US
	@$(PYTHON) $(SCRIPTS_DIR)/driver.py $(US_CSV) -d "Domain name" -o $(OUTPUT_DIR)/US -i -a "$(IPINFO_ACCESS_TOKEN)"


us-city:
	@mkdir -p $(OUTPUT_DIR)/US
	@mkdir -p $(OUTPUT_DIR)/US/city
	@$(PYTHON) $(SCRIPTS_DIR)/driver.py $(US_CITY_CSV) -d "Domain name" -o $(OUTPUT_DIR)/US/city

uk:
	@mkdir -p $(OUTPUT_DIR)/UK
	@$(PYTHON) $(SCRIPTS_DIR)/driver.py $(UK_CSV) -d "Domain: Domain Name" -o $(OUTPUT_DIR)/UK
	
FORCE:
