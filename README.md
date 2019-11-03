# cost-experiments
Tools to experiment with cost of running BLAST searches
The goal is to easily replicate the experiments in from [this
publication](https://www.ncbi.nlm.nih.gov/pubmed/31040829) using NCBI BLAST cloud
products.

## How-to

The `Makefile` contains some targets to facilitate operations:

* Initialize test data: `make data/query.fa`
* Run tests: `make [small | medium | large]`
* Check script syntax: `make check`

# Desired output

Table with cost for each analysis (small, medium, large) for each product.
Make note of date and `nt` BLASTDB size.

