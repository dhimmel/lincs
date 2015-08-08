import urllib
import StringIO
import gzip

import pandas
import scipy.stats
import numpy

import cmap.io.gct

def url_to_df(path):
    """Takes url for gzipped tsv files and returns a dataframe."""
    url = urllib.urlopen(path)
    url_f = StringIO.StringIO(url.read())
    g = gzip.GzipFile(fileobj=url_f)
    return pandas.read_table(g)

def extract_from_gctx(path, probes, signatures):
    """Returns a DataFrame with probes as rows and signatures as columns."""
    gct_object = cmap.io.gct.GCT(path)
    gct_object.read_gctx_matrix(cid = signatures, rid = probes)
    return pandas.DataFrame(gct_object.matrix, index=probes, columns=signatures)

def probes_to_genes(df, probe_to_gene):
    """Converts probe level dataframe to gene level dataframe"""
    get_gene = lambda probe: probe_to_gene.get(probe)
    grouped = df.groupby(by=get_gene, axis=0)
    gene_df = grouped.mean()
    return gene_df

def get_consensus_signatures(df, pert_to_sigs):
    """pert_to_sigs is a dictionary of context_id to a list of signatures."""
    consensuses = dict()
    for pert, sigs in pert_to_sigs.items():
        consensuses[pert] = get_consensus_signature(df.loc[:, sigs])
    return pandas.DataFrame(consensuses)

def get_consensus_signature(df):
    """TODO"""
    weights = weight_signature(df)
    consensus = df.apply(stouffer, axis=1, weights=weights)
    return consensus

def stouffer(z_scores, weights):
    assert len(z_scores) == len(weights)
    z_scores = numpy.array(z_scores)
    weights = numpy.array(weights)
    return numpy.sum(z_scores * weights) / numpy.sqrt(numpy.sum(weights ** 2))

def weight_signature(df, min_cor = 0.05):
    """
    """
    if len(df.columns) == 1:
        return numpy.array([1])

    if len(df.columns) == 2:
        return numpy.array([0.5, 0.5])

    rho, p = scipy.stats.spearmanr(df, axis=0)
    mean_cor = (numpy.sum(rho, axis=0) - 1) / (len(rho) - 1)
    weights = numpy.maximum(mean_cor, min_cor)
    weights /= numpy.sum(weights)
    return weights

