
PYTHON:=python3
PDFLATEX:=pdflatex

dns:
	@$(PYTHON) ./mx_record_lookup.py

paper:
	@$(PDFLATEX) ./paper.tex

