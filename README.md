# Transcriptional signatures of perturbation from LINCS L1000

[![DOI](https://zenodo.org/badge/14475/dhimmel/lincs.svg)](https://zenodo.org/badge/latestdoi/14475/dhimmel/lincs)

Python analysis of the [LINCS L1000](http://www.lincscloud.org/) data.

The repository consists of python notebooks which are executed in the following order:

1. [`api.ipynb`](api.ipynb) retreives metadata from the [L1000 API](http://api.lincscloud.org/). Retrieved data is converted into a dataframe and saved as a tsv. Files are created for [perturbations](data/pertinfo/pertinfo.tsv.gz), [signatures](data/siginfo/siginfo.tsv.gz), [cells](data/cellinfo/cellinfo.tsv.gz), and [probes](data/geneinfo/geneinfo.tsv.gz).
2. [`database.ipynb`](database.ipynb) creates a SQLite database containing the metadata retrieved from the API. Data cleaning occurs here. The database resides at `data/l1000.db` but is ignored due to file size. However, the populated database is available [on figshare](https://doi.org/10.6084/m9.figshare.3085837).
3. [`unichem.ipynb`](unichem.ipynb) maps compounds to external databases and adds the mapping to the database. See [this comment](https://doi.org/10.15363/thinklab.d51#8 "Thinklab · Method for mapping L1000 compounds to external vocabularies") for more information.
4. [`chemical-similarity.ipynb`](chemical-similarity.ipynb) computes chemical similarities between compounds and adds these similarities to the database.
5. [`consensi.ipynb`](consensi.ipynb) computes consensus signatures for each perturbagen. The following consensus files are created:
  + [`consensi-drugbank.tsv.bz2`](data/consensi/consensi-drugbank.tsv.bz2) with consensus signatures for each mapped drugbank compound
  + [`consensi-knockdown.tsv.bz2`](data/consensi/consensi-knockdown.tsv.bz2) with consensus signatures for each gene knockdown
  + [`consensi-overexpression.tsv.bz2`](data/consensi/consensi-overexpression.tsv.bz2) with consensus signatures for each gene over-expression
  + `consensi-pert_id.tsv.bz2` with consensus signatures for each L1000 pert_id. This file is too large for GitHub (500 MB), but is available [on figshare](https://doi.org/10.6084/m9.figshare.3085426).
6. [`significance.ipynb`](significance.ipynb) converts consensus z-scores into significant up/down-regulation values. The following files are created:
  + DrugBank dysregulated genes ([`dysreg-drugbank.tsv`](data/consensi/signif/dysreg-drugbank.tsv)) and counts ([`dysreg-drugbank-summary.tsv`](data/consensi/signif/dysreg-drugbank-summary.tsv))
  + Knockdown dysregulated genes ([`dysreg-knockdown.tsv`](data/consensi/signif/dysreg-knockdown.tsv)) and counts ([`dysreg-knockdown-summary.tsv`](data/consensi/signif/dysreg-knockdown-summary.tsv))
  + Overexpression dysregulated genes ([`dysreg-overexpression.tsv`](data/consensi/signif/dysreg-overexpression.tsv)) and counts ([`dysreg-overexpression-summary.tsv`](data/consensi/signif/dysreg-overexpression-summary.tsv))
  + All perturbagens dysregulated genes ([`dysreg-pert_id.tsv.gz`](data/consensi/signif/dysreg-pert_id.tsv.gz)) and counts ([`dysreg-pert_id-summary.tsv`](data/consensi/signif/dysreg-pert_id-summary.tsv))

See [this comment](https://doi.org/10.15363/thinklab.d43#7 "Thinklab · Concensus signatures version 2.0") for more information on steps 5 & 6.

**Note:** This is not an official LINCS L1000 repository. Users are warned that our modifications may have introduced errors or removed signal that was present the original data.

## Inputs

This repository depends on `modzs.gctx` — a legacy probe × signature matrix of differential expression z-scores. Due to large file size (42.5 GB) this file is not uploaded to GitHub. To recreate this analysis rather than just use the results, users should retrieve [`modzs.gctx` from figshare](https://doi.org/10.6084/m9.figshare.3759129 "modzs.gctx: a legacy LINCS L1000 dataset of differential expression signatures · figshare") and place it in the [`download`](download) directory.

## Citation

See the [Transcriptional signatures of perturbation from LINCS L1000](https://git.dhimmel.com/rephetio-manuscript/#transcriptional-signatures-of-perturbation-from-lincs-l1000) section of the Rephetio manuscript for the final description of this work.
Citations related to this repository are below:

1. **Systematic integration of biomedical knowledge prioritizes drugs for repurposing**
Daniel Scott Himmelstein, Antoine Lizee, Christine Hessler, Leo Brueggeman, Sabrina L Chen, Dexter Hadley, Ari Green, Pouya Khankhanian, Sergio E Baranzini
*eLife* (2017-09-22) <https://doi.org/cdfk>
DOI: [10.7554/elife.26726](https://doi.org/10.7554/elife.26726) · PMID: [28936969](https://www.ncbi.nlm.nih.gov/pubmed/28936969) · PMCID: [PMC5640425](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5640425)

2. **Consensus signatures for LINCS L1000 perturbations**
Daniel Himmelstein, Leo Brueggeman, Sergio Baranzini
*Figshare* (2016-03-08) <https://doi.org/f3mqvs>
DOI: [10.6084/m9.figshare.3085426.v1](https://doi.org/10.6084/m9.figshare.3085426.v1)

3. **dhimmel/lincs v2.0: Refined Consensus Signatures From Lincs L1000**
Daniel Himmelstein, Leo Brueggeman, Sergio Baranzini
*Zenodo* (2016-03-08) <https://doi.org/f3mqvr>
DOI: [10.5281/zenodo.47223](https://doi.org/10.5281/zenodo.47223)

4. **Computing consensus transcriptional profiles for LINCS L1000 perturbations**
Daniel Himmelstein, Caty Chung
*ThinkLab* (2015-03-26) <https://doi.org/f3mqwc>
DOI: [10.15363/thinklab.d43](https://doi.org/10.15363/thinklab.d43)

## Environment

Create the conda environment for this repository using:

```sh
conda env create --file environment.yml
```

## License

All original content in this repository is released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/ "Creative Commons · Public Domain Dedication"). LINCS data and derivatives are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — please refer to the [LINCS data policy](http://www.lincsproject.org/data/data-release-policy/) and attribute [this repository](https://github.com/dhimmel/lincs) and [LINCS L1000](http://www.lincscloud.org/l1000/).
