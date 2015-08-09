# Transcriptional signatures of perturbation from LINCS L1000

[![DOI](https://zenodo.org/badge/doi/10.5281/zenodo.27229.svg)](http://dx.doi.org/10.5281/zenodo.27229)

Python analysis of the [LINCS L1000](http://www.lincscloud.org/) data.

The repository consists of python notebooks which are executed in the following order:

1. [`api.ipynb`](api.ipynb) retreives metadata from the [L1000 API](http://api.lincscloud.org/). Retreived data is converted into a dataframe and saved as a tsv. Files are created for [perturbations](data/pertinfo/pertinfo.tsv.gz), [signatures](data/siginfo/siginfo.tsv.gz), [cells](data/cellinfo/cellinfo.tsv.gz), and [probes](data/geneinfo/geneinfo.tsv.gz).
2. [`database.ipynb`](database.ipynb) creates a SQLite database containing the metadata retrieved from the API. Data cleaning occurs here.
3. [`unichem.ipynb`](unichem.ipynb) maps compounds to external databases and adds the mapping to the database.
4. [`chemical-similarity.ipynb`](chemical-similarity.ipynb) computes chemical similarities between compounds and adds these similarities to the database.
5. [`consensi.ipynb`](consensi.ipynb) computes concensus signatures for each perturbagen. The following concensus files are created:
  + [`consensi-pert_id.tsv.gz`](consensi/consensi-pert_id.tsv.gz) with consensus signatures for each L1000 pert_id
  + [`consensi-drugbank.tsv.gz`](consensi/consensi-drugbank.tsv.gz) with consensus signatures for each mapped drugbank compound 
  + [`consensi-knockdown.tsv.gz`](consensi/consensi-knockdown.tsv.gz) with consensus signatures for each gene knockdown
  + [`consensi-overexpression.tsv.gz`](consensi/consensi-overexpression.tsv.gz) with consensus signatures for each gene over-expression
