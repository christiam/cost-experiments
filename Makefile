# Makefile for cost-experiments
# Author: Christiam Camacho (christiam.camacho@gmail.com)
# Created: Sun Nov  3 06:51:01 2019

SHELL=/bin/bash
.PHONY: all clean distclean check small medium large
VENV=.env

all: small

small: data/query.fa ${VENV}
	[ -d results ] || mkdir results
	source ${VENV}/bin/activate && /usr/bin/time -p src/web-blast.py data/query1.fa > results/web-blast-small.tsv
	source ${VENV}/bin/activate && /usr/bin/time -p src/blast-gcp.py data/query1.fa > results/blast-gcp-small.tsv

medium: data/query.fa ${VENV}
	[ -d results ] || mkdir results
	source ${VENV}/bin/activate && /usr/bin/time -p src/web-blast.py data/query5.fa > results/web-blast-medium.tsv
	source ${VENV}/bin/activate && /usr/bin/time -p src/blast-gcp.py data/query5.fa > results/blast-gcp-medium.tsv

large: data/query.fa ${VENV}
	[ -d results ] || mkdir results
	source ${VENV}/bin/activate && /usr/bin/time -p src/web-blast.py data/query.fa > results/web-blast-large.tsv
	source ${VENV}/bin/activate && /usr/bin/time -p src/blast-gcp.py data/query.fa > results/blast-gcp-large.tsv

data/query.fa:
	[ -d data ] || mkdir data
	[ -f data/fa.zip ] || wget -q -O data/fa.zip https://ndownloader.figshare.com/articles/6865397?private_link=729b346eda670e9daba4
	unzip -d data data/fa.zip
	cat data/*.fa > data/query.fa
	cat data/'Sample_1 (paired) trimmed (paired) assembly.fa' > data/query1.fa
	cat data/'Sample_1 (paired) trimmed (paired) assembly.fa' data/'Sample_2 (paired) trimmed (paired) assembly.fa' data/'Sample_3 (paired) trimmed (paired) assembly.fa' data/'Sample_4 (paired) trimmed (paired) assembly.fa' data/'Sample_5 (paired) trimmed (paired) assembly.fa' > data/query5.fa

#########################################################################
# Python support

check: ${VENV}
	source ${VENV}/bin/activate && \
	for f in $(wildcard src/*.py); do python -m py_compile $$f ; done
	#python3 -m unittest $(subst .py,,$(filter-out setup.py, $(wildcard src/*.py))) && python3 -m unittest discover -s tests
	#time -p python3 -m doctest map.py
	#time -p py.test *.py
	#time -p py.test tests

${VENV}: requirements.txt
	[ -d ${VENV} ] || virtualenv -p python3 $@
	source ${VENV}/bin/activate && pip install -r $^

clean:
	find . -name __pycache__ | xargs ${RM} -fr
	find . -name '*.pyc' | xargs ${RM} -fr

distclean: clean
	${RM} -r ${VENV}
	${RM} -fr results data
