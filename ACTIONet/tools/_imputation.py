from typing import Literal, Optional

import numpy as np
import pandas as pd
from anndata import AnnData
from scipy import sparse

import _ACTIONet as _an

def impute_genes_using_archetypes(
    adata: AnnData,
    genes: list,
    archetypes_key: Optional[str] = 'H_unified',
    profile_key: Optional[str] = 'unified_feature_profile'
) -> AnnData:
    """
    Impute expression of genes by interpolating over archetype profile

    Parameters
    ----------
    adata
        AnnData object storing the ACTIONet results
    genes
        List of genes to impute
    archetypes_key
        Key in `adata.obsm` that holds the archetype footprints
    profile_key
        Key in `adata.varm` that holds the archetype feature profile

    Returns
    -------
    AnnData
        cells x genes
    """
    if archetypes_key not in adata.obsm.keys():
        raise ValueError(f'Did not find adata.obsm[\'{archetypes_key}\'].')
    if profile_key not in adata.varm.keys():
        raise ValueError(
            f'Did not find adata.varm[\'{profile_key}\']. '
            'Please run pp.compute_archetype_feature_specificity() first.'
        )
    genes = adata.obs.index.intersection(genes)
    Z = adata[:, genes].varm[f'{archetypes_key}_profile']
    H = adata.obsm[archetypes_key].T
    return AnnData(
        X=(Z @ H).T, obs=pd.DataFrame(index=adata.obs.index), var=pd.DataFrame(index=genes)
    )


def impute_specific_genes_using_archetypes(
    adata: AnnData,
    genes: list,
    archetypes_key: Optional[str] = 'H_unified',
    significance_key: Optional[str] = 'unified_feature_specificity'
) -> AnnData:
    """
    Impute expression of genes by interpolating over archetype profile

    Parameters
    ----------
    adata
        AnnData object storing the ACTIONet results
    genes
        List of genes to impute
    archetypes_key
        Key in `adata.obsm` that contains archetype footprints
    significance_key
        Key in `adata.varm` that contains feature specificity

    Returns
    -------
    AnnData
        cells x genes
    """
    if archetypes_key not in adata.obsm.keys():
        raise ValueError(f'Did not find adata.obsm[\'{archetypes_key}\'].')
    if significance_key not in adata.varm.keys():
        raise ValueError(
            f'Did not find adata.varm[\'{significance_key}\']. '
            'Please run pp.compute_archetype_feature_specificity() first.'
        )
    genes = adata.obs.index.intersection(genes)
    Z = np.log1p(adata[:, genes].varm[significance_key])
    H = adata.obsm[archetypes_key].T
    return AnnData(
        X=(Z @ H).T, obs=pd.DataFrame(index=adata.obs.index), var=pd.DataFrame(index=genes)
    )

def impute_genes_using_ACTIONet(
    adata: AnnData,
    genes: list,
    alpha: Optional[float] = 0.85,
    n_threads: Optional[int] = 0,
    n_iters: Optional[int] = 5
) -> AnnData:
    """Gene expression imputation using network diffusion.

    Parameters
    ----------
    adata
        Annotated data matrix
    genes
        List of genes to impute
    alpha
        Depth of diffusion between (0, 1)
    n_threads
        Number of threads. Defaults to number of threads available
    n_iters
        Number of diffusion iterations

    Returns
    -------
    AnnData
    """
    if 'ACTIONet' not in adata.obsp.keys():
        raise ValueError(
            f'Did not find adata.obsp[\'ACTIONet\']. '
            'Please run nt.build_ACTIONet() first.'
        )

    genes = adata.var.index.intersection(genes)
    mask = adata.var.index.isin(genes)
    if (np.sum(mask)) > 0:
        U = adata.X[:, mask].copy()
        U[U < 0] = 0
        cs = np.array(np.sum(U, axis=0)).flatten()
        U = U / cs
        U = U[:, cs > 0]
        gg = genes[cs > 0]
    else:
        U = adata.X[:, mask].copy()
        U = U / np.sum(U)
        gg = genes

    # Network diffusion
    G = adata.obsp['ACTIONet']
    imputed = _an.compute_network_diffusion(G, sparse.csc_matrix(U), n_threads, alpha, n_iters)
    np.nan_to_num(imputed, copy=False, nan=0.0)

    # Rescale the baseline expression of each gene
    rescaled = np.zeros(imputed.shape)
    for i in range(imputed.shape[1]):
        x = U[:, i]
        y = imputed[:, i]

        # In the R implementation, quantile(x, 1) is used, which just
        # finds the maximum.
        x_Q = np.max(x)
        y_Q = np.max(y)

        if y_Q == 0:
            # Leave this column as zeros
            continue

        y = y * x_Q / y_Q
        y[y > x_Q] = x_Q
        rescaled[:, i] = y

    return AnnData(
        X=rescaled, obs=pd.DataFrame(index=adata.obs.index), var=pd.DataFrame(index=genes)
    )
