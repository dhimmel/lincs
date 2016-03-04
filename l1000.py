import pandas
import numpy

def url_to_df(path):
    """Takes url for gzipped tsv files and returns a dataframe."""
    import StringIO
    import urllib
    import gzip
    url = urllib.urlopen(path)
    url_f = StringIO.StringIO(url.read())
    g = gzip.GzipFile(fileobj=url_f)
    return pandas.read_table(g)

def extract_from_gctx(path, probes, signatures):
    """Returns a DataFrame with probes as rows and signatures as columns."""
    import cmap.io.gct
    gct_object = cmap.io.gct.GCT(path)
    gct_object.read_gctx_matrix(cid = signatures, rid = probes)
    return pandas.DataFrame(gct_object.matrix, index=probes, columns=signatures)

def probes_to_genes(df, probe_to_gene):
    """Converts probe level dataframe to gene level dataframe."""
    get_gene = lambda probe: probe_to_gene.get(probe)
    grouped = df.groupby(by=get_gene, axis=0)
    gene_df = grouped.mean()
    return gene_df

def get_consensus_signatures(df, pert_to_sigs, weighting_subset=False):
    """
    Compute consensus signatures for pertubagens specified in `pert_to_sigs`,
    which is a dictionary of context_id to sig_id list. `df` is a probe (rows)
    by signature (columns) dataframe. `weighting_subset` is a subset of probes
    to use for weighting, for example all landmark probes.
    """
    consensuses = dict()
    for pert, sigs in pert_to_sigs.items():
        consensuses[pert] = get_consensus_signature(df.loc[:, sigs], weighting_subset=weighting_subset)
    return pandas.DataFrame(consensuses)

def get_consensus_signature(df, weighting_subset=False):
    """
    Compute a concensus signature for all signatures (columns in `df`).
    """
    weighting_df = df if weighting_subset is False else df.loc[weighting_subset, :]
    weights = weight_signature(weighting_df)
    consensus = df.apply(stouffer, axis='columns', weights=weights)
    return consensus

def stouffer(z_scores, weights):
    """
    Meta-analyze z_scores using Stouffer's method.
    See https://doi.org/10.15363/thinklab.d43#5
    """
    assert len(z_scores) == len(weights)
    z_scores = numpy.array(z_scores)
    weights = numpy.array(weights)
    return numpy.sum(z_scores * weights) / numpy.sqrt(numpy.sum(weights ** 2))

def weight_signature(df, min_cor = 0.05):
    """
    Calculate a weight for each signature that equals a signature's average
    correlation to other signatures. `min_cor` sets a minimum correlation to
    prevent signatures from having zero or negative weights. `df` is probe
    (rows) by signature (columns) dataframe. Returns a numpy.array of weights.
    """
    if len(df.columns) == 1:
        return numpy.array([1])

    if len(df.columns) == 2:
        return numpy.array([0.5, 0.5])

    corr_df = df.corr(method='spearman')
    mean_cor = (corr_df.sum(axis='rows') - 1) / (len(corr_df) - 1)
    weights = numpy.maximum(mean_cor, min_cor)
    weights /= weights.sum()
    return numpy.array(weights)
